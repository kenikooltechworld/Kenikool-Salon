"""
Security service - Password management, 2FA, sessions, and security monitoring
"""
import logging
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple
from bson import ObjectId
import pyotp
import qrcode
from io import BytesIO
import base64

from app.database import Database
from app.utils.security import hash_password, verify_password
from app.services.email_service import email_service
from app.utils.redis_cache import RedisCache

logger = logging.getLogger(__name__)


class SecurityException(Exception):
    """Base exception for security operations"""
    pass


class UnauthorizedException(SecurityException):
    """Raised when authentication fails"""
    pass


class BadRequestException(SecurityException):
    """Raised when request is invalid"""
    pass


class NotFoundException(SecurityException):
    """Raised when resource is not found"""
    pass


class SecurityService:
    """Service for security operations including password, 2FA, and session management"""

    # ==================== PASSWORD MANAGEMENT ====================

    @staticmethod
    async def change_password(
        user_id: str,
        tenant_id: str,
        current_password: str,
        new_password: str,
        request_info: Dict
    ) -> bool:
        """
        Change user password with validation and session invalidation
        
        Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            current_password: Current password for verification
            new_password: New password
            request_info: Request metadata (IP, device, etc.)
            
        Returns:
            True if password changed successfully
            
        Raises:
            UnauthorizedException: If current password is incorrect
            BadRequestException: If new password is invalid
        """
        db = Database.get_db()
        
        # Get user
        user = db.users.find_one({"_id": ObjectId(user_id), "tenant_id": tenant_id})
        if not user:
            raise NotFoundException("User not found")
        
        # Verify current password (Requirement 1.1, 1.2)
        if not verify_password(current_password, user.get("password_hash")):
            # Log failed attempt
            try:
                from app.services.audit_log_service import audit_log_service
                await audit_log_service.log_event(
                    user_id=user_id,
                    tenant_id=tenant_id,
                    event_type="password_change_failed",
                    request_info=request_info,
                    success=False,
                    details={"reason": "incorrect_current_password"}
                )
            except Exception as e:
                logger.error(f"Failed to log audit event: {str(e)}")
            
            raise UnauthorizedException("Current password is incorrect")
        
        # Validate new password strength (Requirement 1.3)
        if len(new_password) < 8:
            raise BadRequestException("New password must be at least 8 characters long")
        
        # Check if new password is same as current (Requirement 1.4)
        if verify_password(new_password, user.get("password_hash")):
            raise BadRequestException("New password must be different from current password")
        
        # Hash new password
        new_password_hash = hash_password(new_password)
        
        # Update password and timestamp
        db.users.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "password_hash": new_password_hash,
                    "password_changed_at": datetime.utcnow()
                }
            }
        )
        
        # Invalidate all other sessions (Requirement 1.6)
        current_session_id = request_info.get("session_id")
        if current_session_id:
            db.sessions.delete_many({
                "user_id": user_id,
                "tenant_id": tenant_id,
                "_id": {"$ne": ObjectId(current_session_id)}
            })
        else:
            # If no current session, invalidate all
            db.sessions.delete_many({
                "user_id": user_id,
                "tenant_id": tenant_id
            })
        
        # Send confirmation email (Requirement 1.5)
        try:
            await email_service.send_password_change_confirmation(
                to=user.get("email"),
                user_name=user.get("full_name", "User")
            )
        except Exception as e:
            logger.error(f"Failed to send password change confirmation email: {str(e)}")
        
        # Log security event (Requirement 1.6)
        try:
            from app.services.audit_log_service import audit_log_service
            await audit_log_service.log_event(
                user_id=user_id,
                tenant_id=tenant_id,
                event_type="password_changed",
                request_info=request_info,
                success=True,
                details={"sessions_invalidated": True}
            )
        except Exception as e:
            logger.error(f"Failed to log audit event: {str(e)}")
        
        logger.info(f"Password changed for user {user_id}")
        return True

    # ==================== 2FA SETUP AND VERIFICATION ====================

    @staticmethod
    async def setup_2fa(user_id: str, tenant_id: str) -> Dict:
        """
        Initialize 2FA setup with TOTP secret and backup codes
        
        Requirements: 2.1, 2.2, 2.3
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            
        Returns:
            Dict with secret, QR code URL, and backup codes
        """
        db = Database.get_db()
        
        # Get user
        user = db.users.find_one({"_id": ObjectId(user_id), "tenant_id": tenant_id})
        if not user:
            raise NotFoundException("User not found")
        
        # Generate TOTP secret (Requirement 2.1)
        secret = pyotp.random_base32()
        
        # Create QR code URL (Requirement 2.2)
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user.get("email"),
            issuer_name="Salon Management"
        )
        
        # Generate QR code image
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
        qr_code_url = f"data:image/png;base64,{qr_code_base64}"
        
        # Generate 10 backup codes (Requirement 2.3)
        backup_codes = [secrets.token_hex(4) for _ in range(10)]
        backup_codes_hashed = [hash_password(code) for code in backup_codes]
        
        # Store temporary setup data in cache (not enabled yet)
        setup_key = f"2fa_setup:{user_id}"
        RedisCache.set(
            setup_key,
            {
                "secret": secret,
                "backup_codes_hashed": backup_codes_hashed,
                "created_at": datetime.utcnow().isoformat()
            },
            timedelta(minutes=10)  # 10 minutes expiration
        )
        
        logger.info(f"2FA setup initiated for user {user_id}")
        
        return {
            "secret": secret,
            "qr_code_url": qr_code_url,
            "backup_codes": backup_codes
        }

    @staticmethod
    async def verify_and_enable_2fa(
        user_id: str,
        tenant_id: str,
        code: str,
        request_info: Dict
    ) -> bool:
        """
        Verify 2FA code and enable 2FA for user
        
        Requirements: 2.1, 2.3, 2.5, 2.6
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            code: 6-digit TOTP code
            request_info: Request metadata
            
        Returns:
            True if 2FA enabled successfully
            
        Raises:
            BadRequestException: If code is invalid or setup expired
        """
        db = Database.get_db()
        
        # Get setup data from cache
        setup_key = f"2fa_setup:{user_id}"
        setup_data = RedisCache.get(setup_key)
        
        if not setup_data:
            raise BadRequestException("2FA setup expired. Please start setup again.")
        
        secret = setup_data.get("secret")
        backup_codes_hashed = setup_data.get("backup_codes_hashed")
        
        # Verify TOTP code
        totp = pyotp.TOTP(secret)
        if not totp.verify(code, valid_window=1):
            raise BadRequestException("Invalid verification code")
        
        # Enable 2FA in user document
        db.users.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "totp_secret": secret,
                    "totp_enabled": True,
                    "backup_codes": backup_codes_hashed
                }
            }
        )
        
        # Clear setup cache
        RedisCache.delete(setup_key)
        
        # Log security event
        await audit_log_service.log_event(
            user_id=user_id,
            tenant_id=tenant_id,
            event_type="2fa_enabled",
            request_info=request_info,
            success=True
        )
        
        logger.info(f"2FA enabled for user {user_id}")
        return True

    @staticmethod
    async def disable_2fa(
        user_id: str,
        tenant_id: str,
        password: str,
        code: str,
        request_info: Dict
    ) -> bool:
        """
        Disable 2FA with password and 2FA code verification
        
        Requirements: 2.5, 2.6
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            password: Current password
            code: Current 2FA code
            request_info: Request metadata
            
        Returns:
            True if 2FA disabled successfully
            
        Raises:
            UnauthorizedException: If password or code is invalid
        """
        db = Database.get_db()
        
        # Get user
        user = db.users.find_one({"_id": ObjectId(user_id), "tenant_id": tenant_id})
        if not user:
            raise NotFoundException("User not found")
        
        # Verify password
        if not verify_password(password, user.get("password_hash")):
            raise UnauthorizedException("Password is incorrect")
        
        # Verify 2FA code
        if not user.get("totp_enabled"):
            raise BadRequestException("2FA is not enabled")
        
        totp = pyotp.TOTP(user.get("totp_secret"))
        if not totp.verify(code, valid_window=1):
            raise UnauthorizedException("Invalid 2FA code")
        
        # Disable 2FA
        db.users.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "totp_enabled": False,
                    "totp_secret": None,
                    "backup_codes": []
                }
            }
        )
        
        # Log security event
        await audit_log_service.log_event(
            user_id=user_id,
            tenant_id=tenant_id,
            event_type="2fa_disabled",
            request_info=request_info,
            success=True
        )
        
        logger.info(f"2FA disabled for user {user_id}")
        return True

    # ==================== SESSION MANAGEMENT ====================

    @staticmethod
    async def create_session(
        user_id: str,
        tenant_id: str,
        token: str,
        request_info: Dict
    ) -> str:
        """
        Create new session with device and location metadata
        
        Requirements: 3.1, 3.2
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            token: Session token
            request_info: Request metadata (IP, device, browser, user_agent)
            
        Returns:
            Session ID
        """
        db = Database.get_db()
        
        # Hash token for storage
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # Get geolocation from IP (simplified - in production use GeoIP service)
        ip_address = request_info.get("ip_address", "unknown")
        location = request_info.get("location", "Unknown")
        
        # Create session document
        session_doc = {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "token_hash": token_hash,
            "device": request_info.get("device", "Unknown"),
            "browser": request_info.get("browser", "Unknown"),
            "ip_address": ip_address,
            "location": location,
            "user_agent": request_info.get("user_agent", ""),
            "last_active": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(days=30),
            "created_at": datetime.utcnow()
        }
        
        result = db.sessions.insert_one(session_doc)
        session_id = str(result.inserted_id)
        
        logger.info(f"Session created for user {user_id}: {session_id}")
        return session_id

    @staticmethod
    async def get_active_sessions(user_id: str, tenant_id: str) -> List[Dict]:
        """
        Get all active sessions for user
        
        Requirements: 3.2
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            
        Returns:
            List of active sessions
        """
        db = Database.get_db()
        
        sessions = list(db.sessions.find({
            "user_id": user_id,
            "tenant_id": tenant_id,
            "expires_at": {"$gt": datetime.utcnow()}
        }).sort("last_active", -1))
        
        # Convert ObjectId to string
        for session in sessions:
            session["id"] = str(session.pop("_id"))
        
        return sessions

    @staticmethod
    async def revoke_session(user_id: str, tenant_id: str, session_id: str) -> bool:
        """
        Revoke specific session
        
        Requirements: 3.3, 3.6
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            session_id: Session ID to revoke
            
        Returns:
            True if session revoked
        """
        db = Database.get_db()
        
        result = db.sessions.delete_one({
            "_id": ObjectId(session_id),
            "user_id": user_id,
            "tenant_id": tenant_id
        })
        
        if result.deleted_count == 0:
            raise NotFoundException("Session not found")
        
        logger.info(f"Session revoked: {session_id}")
        return True

    @staticmethod
    async def revoke_all_other_sessions(
        user_id: str,
        tenant_id: str,
        current_session_id: str
    ) -> int:
        """
        Revoke all sessions except current
        
        Requirements: 3.4, 3.6
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            current_session_id: Current session to keep
            
        Returns:
            Number of sessions revoked
        """
        db = Database.get_db()
        
        result = db.sessions.delete_many({
            "user_id": user_id,
            "tenant_id": tenant_id,
            "_id": {"$ne": ObjectId(current_session_id)}
        })
        
        logger.info(f"Revoked {result.deleted_count} sessions for user {user_id}")
        return result.deleted_count

    @staticmethod
    async def cleanup_expired_sessions() -> int:
        """
        Delete expired sessions (background job)
        
        Requirements: 3.5
        
        Returns:
            Number of sessions deleted
        """
        db = Database.get_db()
        
        result = db.sessions.delete_many({
            "expires_at": {"$lt": datetime.utcnow()}
        })
        
        logger.info(f"Cleaned up {result.deleted_count} expired sessions")
        return result.deleted_count

    # ==================== SECURITY SCORE ====================

    @staticmethod
    async def calculate_security_score(user_id: str, tenant_id: str) -> int:
        """
        Calculate security score (0-100) based on security factors
        
        Requirements: 11.1, 11.2, 11.3, 11.4, 11.6
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            
        Returns:
            Security score (0-100)
        """
        db = Database.get_db()
        
        # Check cache first
        cache_key = f"security_score:{user_id}"
        cached_score = RedisCache.get(cache_key)
        if cached_score is not None:
            return cached_score
        
        user = db.users.find_one({"_id": ObjectId(user_id), "tenant_id": tenant_id})
        if not user:
            raise NotFoundException("User not found")
        
        score = 0
        
        # Password strength: 25 points
        password_hash = user.get("password_hash", "")
        if len(password_hash) > 60:  # bcrypt hash is ~60 chars
            score += 25
        
        # 2FA enabled: 30 points
        if user.get("totp_enabled"):
            score += 30
        
        # Recent password change: 15 points
        password_changed_at = user.get("password_changed_at")
        if password_changed_at:
            days_since_change = (datetime.utcnow() - password_changed_at).days
            if days_since_change < 90:
                score += 15
        
        # Email verified: 10 points
        if user.get("email_verified"):
            score += 10
        
        # Phone verified: 5 points
        if user.get("phone_verified"):
            score += 5
        
        # No suspicious activity: 15 points
        recent_logs = list(db.security_logs.find({
            "user_id": user_id,
            "tenant_id": tenant_id,
            "flagged": True,
            "timestamp": {"$gt": datetime.utcnow() - timedelta(days=30)}
        }).limit(1))
        
        if not recent_logs:
            score += 15
        
        # Cache score for 1 hour
        RedisCache.set(cache_key, score, timedelta(hours=1))
        
        logger.info(f"Security score calculated for user {user_id}: {score}")
        return score

    # ==================== LOGIN ACTIVITY MONITORING ====================

    @staticmethod
    async def get_login_activity(
        user_id: str,
        tenant_id: str,
        limit: int = 50
    ) -> List[Dict]:
        """
        Get recent login activity
        
        Requirements: 23.1, 23.2
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            limit: Number of records to return
            
        Returns:
            List of login activity records
        """
        db = Database.get_db()
        
        logs = list(db.security_logs.find({
            "user_id": user_id,
            "tenant_id": tenant_id,
            "event_type": "login"
        }).sort("timestamp", -1).limit(limit))
        
        # Convert ObjectId to string
        for log in logs:
            log["id"] = str(log.pop("_id"))
        
        return logs

    @staticmethod
    async def detect_new_device(
        user_id: str,
        tenant_id: str,
        device: str,
        request_info: Dict
    ) -> bool:
        """
        Detect if login is from a new device
        
        Requirements: 23.3
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            device: Device identifier
            request_info: Request metadata
            
        Returns:
            True if device is new
        """
        db = Database.get_db()
        
        # Check if device has been seen in last 30 days
        recent_login = db.security_logs.find_one({
            "user_id": user_id,
            "tenant_id": tenant_id,
            "device": device,
            "success": True,
            "timestamp": {"$gt": datetime.utcnow() - timedelta(days=30)}
        })
        
        return recent_login is None

    @staticmethod
    async def check_account_lockout(user_id: str, tenant_id: str) -> bool:
        """
        Check if account is locked due to failed attempts
        
        Requirements: 23.5
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            
        Returns:
            True if account is locked
        """
        db = Database.get_db()
        
        user = db.users.find_one({"_id": ObjectId(user_id), "tenant_id": tenant_id})
        if not user:
            return False
        
        # Check if account is locked
        locked_until = user.get("account_locked_until")
        if locked_until and locked_until > datetime.utcnow():
            return True
        
        return False

    @staticmethod
    async def increment_failed_login_attempts(
        user_id: str,
        tenant_id: str
    ) -> int:
        """
        Increment failed login attempts and lock account if needed
        
        Requirements: 23.5
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            
        Returns:
            Number of failed attempts
        """
        db = Database.get_db()
        
        user = db.users.find_one({"_id": ObjectId(user_id), "tenant_id": tenant_id})
        if not user:
            raise NotFoundException("User not found")
        
        failed_attempts = user.get("failed_login_attempts", 0) + 1
        
        # Lock account after 5 failed attempts for 15 minutes
        locked_until = None
        if failed_attempts >= 5:
            locked_until = datetime.utcnow() + timedelta(minutes=15)
        
        db.users.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "failed_login_attempts": failed_attempts,
                    "account_locked_until": locked_until
                }
            }
        )
        
        logger.warning(f"Failed login attempt {failed_attempts} for user {user_id}")
        return failed_attempts

    @staticmethod
    async def reset_failed_login_attempts(user_id: str, tenant_id: str) -> None:
        """
        Reset failed login attempts on successful login
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
        """
        db = Database.get_db()
        
        db.users.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "failed_login_attempts": 0,
                    "account_locked_until": None
                }
            }
        )


# Create singleton instance
security_service = SecurityService()
