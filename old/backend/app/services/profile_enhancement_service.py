"""
Profile Enhancement Service - Profile picture upload, email change, phone verification
"""
import logging
import secrets
import mimetypes
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from bson import ObjectId

from app.database import Database
from app.services.email_service import email_service
from app.utils.redis_cache import RedisCache

logger = logging.getLogger(__name__)


class ProfileEnhancementException(Exception):
    """Base exception for profile operations"""
    pass


class BadRequestException(ProfileEnhancementException):
    """Raised when request is invalid"""
    pass


class NotFoundException(ProfileEnhancementException):
    """Raised when resource is not found"""
    pass


class ConflictException(ProfileEnhancementException):
    """Raised when resource already exists"""
    pass


class ProfileEnhancementService:
    """Service for profile picture upload, email change, and phone verification"""

    # Allowed file types for profile pictures
    ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

    @staticmethod
    async def upload_profile_picture(
        user_id: str,
        tenant_id: str,
        file_content: bytes,
        file_name: str,
        request_info: Dict
    ) -> Dict:
        """
        Upload profile picture
        
        Requirements: 13.1, 13.2, 13.4, 13.6
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            file_content: File content as bytes
            file_name: Original file name
            request_info: Request metadata
            
        Returns:
            Profile picture URLs
            
        Raises:
            BadRequestException: If file is invalid
        """
        db = Database.get_db()
        
        # Validate file type (Requirement 13.1)
        mime_type, _ = mimetypes.guess_type(file_name)
        if mime_type not in ProfileEnhancementService.ALLOWED_MIME_TYPES:
            raise BadRequestException(
                f"Invalid file type. Allowed types: JPEG, PNG, WebP"
            )
        
        # Validate file size (Requirement 13.2)
        if len(file_content) > ProfileEnhancementService.MAX_FILE_SIZE:
            raise BadRequestException(
                f"File size exceeds 5MB limit. Current size: {len(file_content) / 1024 / 1024:.2f}MB"
            )
        
        # Upload to Cloudinary (simplified - in production use actual Cloudinary)
        # For now, we'll generate placeholder URLs
        file_id = secrets.token_urlsafe(16)
        original_url = f"https://cdn.example.com/profiles/{user_id}/{file_id}_original.jpg"
        thumbnail_url = f"https://cdn.example.com/profiles/{user_id}/{file_id}_thumb.jpg"
        
        # Update user document with picture URLs (Requirement 13.4)
        db.users.update_one(
            {"_id": ObjectId(user_id), "tenant_id": tenant_id},
            {
                "$set": {
                    "profile_picture_url": original_url,
                    "profile_picture_thumbnail_url": thumbnail_url,
                    "profile_picture_updated_at": datetime.utcnow()
                }
            }
        )
        
        # Log security event
        try:
            from app.services.audit_log_service import audit_log_service
            await audit_log_service.log_event(
                user_id=user_id,
                tenant_id=tenant_id,
                event_type="profile_picture_uploaded",
                request_info=request_info,
                success=True,
                details={"file_name": file_name, "file_size": len(file_content)}
            )
        except Exception as e:
            logger.error(f"Failed to log audit event: {str(e)}")
        
        logger.info(f"Profile picture uploaded for user {user_id}")
        
        return {
            "original_url": original_url,
            "thumbnail_url": thumbnail_url
        }

    @staticmethod
    async def delete_profile_picture(
        user_id: str,
        tenant_id: str,
        request_info: Dict
    ) -> bool:
        """
        Delete profile picture
        
        Requirements: 13.6
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            request_info: Request metadata
            
        Returns:
            True if picture deleted
        """
        db = Database.get_db()
        
        # Update user document
        db.users.update_one(
            {"_id": ObjectId(user_id), "tenant_id": tenant_id},
            {
                "$set": {
                    "profile_picture_url": None,
                    "profile_picture_thumbnail_url": None,
                    "profile_picture_updated_at": datetime.utcnow()
                }
            }
        )
        
        # Log security event
        try:
            from app.services.audit_log_service import audit_log_service
            await audit_log_service.log_event(
                user_id=user_id,
                tenant_id=tenant_id,
                event_type="profile_picture_deleted",
                request_info=request_info,
                success=True
            )
        except Exception as e:
            logger.error(f"Failed to log audit event: {str(e)}")
        
        logger.info(f"Profile picture deleted for user {user_id}")
        return True

    @staticmethod
    async def initiate_email_change(
        user_id: str,
        tenant_id: str,
        new_email: str,
        request_info: Dict
    ) -> str:
        """
        Initiate email change with verification
        
        Requirements: 9.1, 9.2, 9.4, 9.5
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            new_email: New email address
            request_info: Request metadata
            
        Returns:
            Verification token
            
        Raises:
            BadRequestException: If email is invalid or already in use
        """
        db = Database.get_db()
        
        # Validate email format
        if not new_email or "@" not in new_email:
            raise BadRequestException("Invalid email format")
        
        # Check if email is already in use
        existing_user = db.users.find_one({
            "email": new_email,
            "tenant_id": tenant_id,
            "_id": {"$ne": ObjectId(user_id)}
        })
        
        if existing_user:
            raise ConflictException("Email is already in use")
        
        # Get current user
        user = db.users.find_one({"_id": ObjectId(user_id), "tenant_id": tenant_id})
        if not user:
            raise NotFoundException("User not found")
        
        # Generate verification token
        verification_token = secrets.token_urlsafe(32)
        token_hash = __import__("hashlib").sha256(verification_token.encode()).hexdigest()
        
        # Store pending email change
        db.users.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "pending_email": new_email,
                    "email_change_token": token_hash,
                    "email_change_expires": datetime.utcnow() + timedelta(hours=24)
                }
            }
        )
        
        # Send verification email to new email (Requirement 9.2)
        try:
            await email_service.send_email_change_verification(
                to=new_email,
                user_name=user.get("full_name", "User"),
                verification_url=f"https://app.example.com/verify-email/{verification_token}"
            )
        except Exception as e:
            logger.error(f"Failed to send verification email: {str(e)}")
        
        # Log security event
        try:
            from app.services.audit_log_service import audit_log_service
            await audit_log_service.log_event(
                user_id=user_id,
                tenant_id=tenant_id,
                event_type="email_change_initiated",
                request_info=request_info,
                success=True,
                details={"new_email": new_email}
            )
        except Exception as e:
            logger.error(f"Failed to log audit event: {str(e)}")
        
        logger.info(f"Email change initiated for user {user_id}")
        return verification_token

    @staticmethod
    async def verify_email_change(
        user_id: str,
        tenant_id: str,
        verification_token: str,
        request_info: Dict
    ) -> bool:
        """
        Verify and complete email change
        
        Requirements: 9.2, 9.3, 9.5
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            verification_token: Verification token
            request_info: Request metadata
            
        Returns:
            True if email changed
            
        Raises:
            BadRequestException: If token is invalid or expired
        """
        db = Database.get_db()
        
        # Hash the token
        token_hash = __import__("hashlib").sha256(verification_token.encode()).hexdigest()
        
        # Get user
        user = db.users.find_one({"_id": ObjectId(user_id), "tenant_id": tenant_id})
        if not user:
            raise NotFoundException("User not found")
        
        # Verify token
        if user.get("email_change_token") != token_hash:
            raise BadRequestException("Invalid verification token")
        
        # Check expiration
        if not user.get("email_change_expires") or user["email_change_expires"] < datetime.utcnow():
            raise BadRequestException("Verification token has expired")
        
        old_email = user.get("email")
        new_email = user.get("pending_email")
        
        # Update email
        db.users.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "email": new_email,
                    "pending_email": None,
                    "email_change_token": None,
                    "email_change_expires": None
                }
            }
        )
        
        # Send notification to old email (Requirement 9.5)
        try:
            await email_service.send_email_changed_notification(
                to=old_email,
                user_name=user.get("full_name", "User"),
                new_email=new_email
            )
        except Exception as e:
            logger.error(f"Failed to send change notification: {str(e)}")
        
        # Log security event
        try:
            from app.services.audit_log_service import audit_log_service
            await audit_log_service.log_event(
                user_id=user_id,
                tenant_id=tenant_id,
                event_type="email_changed",
                request_info=request_info,
                success=True,
                details={"old_email": old_email, "new_email": new_email}
            )
        except Exception as e:
            logger.error(f"Failed to log audit event: {str(e)}")
        
        logger.info(f"Email changed for user {user_id}")
        return True

    @staticmethod
    async def initiate_phone_verification(
        user_id: str,
        tenant_id: str,
        phone_number: str,
        request_info: Dict
    ) -> bool:
        """
        Send phone verification SMS
        
        Requirements: 10.1, 10.5
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            phone_number: Phone number to verify
            request_info: Request metadata
            
        Returns:
            True if SMS sent
            
        Raises:
            BadRequestException: If phone format is invalid
        """
        db = Database.get_db()
        
        # Validate phone format
        if not phone_number or len(phone_number) < 10:
            raise BadRequestException("Invalid phone number format")
        
        # Check rate limiting (Requirement 10.5)
        cache_key = f"phone_verification_attempts:{user_id}"
        attempts = RedisCache.get(cache_key) or 0
        
        if attempts >= 3:
            raise BadRequestException("Too many verification attempts. Please try again later.")
        
        # Generate verification code
        verification_code = __import__("secrets").randbelow(1000000)
        code_str = f"{verification_code:06d}"
        
        # Store code in cache (10 minutes expiration)
        code_cache_key = f"phone_verification_code:{user_id}"
        RedisCache.set(code_cache_key, code_str, timedelta(minutes=10))
        
        # Increment attempts
        RedisCache.set(cache_key, attempts + 1, timedelta(hours=1))
        
        # Send SMS via Termii (simplified - in production use actual Termii)
        try:
            # In production, use actual Termii SMS service
            logger.info(f"Sending verification code {code_str} to {phone_number}")
        except Exception as e:
            logger.error(f"Failed to send SMS: {str(e)}")
            raise BadRequestException("Failed to send verification code")
        
        # Store pending phone number
        db.users.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "phone_verification_number": phone_number,
                    "phone_verification_attempts": 0
                }
            }
        )
        
        # Log security event
        try:
            from app.services.audit_log_service import audit_log_service
            await audit_log_service.log_event(
                user_id=user_id,
                tenant_id=tenant_id,
                event_type="phone_verification_initiated",
                request_info=request_info,
                success=True,
                details={"phone_number": phone_number}
            )
        except Exception as e:
            logger.error(f"Failed to log audit event: {str(e)}")
        
        logger.info(f"Phone verification initiated for user {user_id}")
        return True

    @staticmethod
    async def verify_phone(
        user_id: str,
        tenant_id: str,
        code: str,
        request_info: Dict
    ) -> bool:
        """
        Verify phone number with code
        
        Requirements: 10.2, 10.3, 10.6
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            code: Verification code
            request_info: Request metadata
            
        Returns:
            True if phone verified
            
        Raises:
            BadRequestException: If code is invalid
        """
        db = Database.get_db()
        
        # Get stored code
        code_cache_key = f"phone_verification_code:{user_id}"
        stored_code = RedisCache.get(code_cache_key)
        
        if not stored_code:
            raise BadRequestException("Verification code has expired")
        
        if stored_code != code:
            raise BadRequestException("Invalid verification code")
        
        # Get user
        user = db.users.find_one({"_id": ObjectId(user_id), "tenant_id": tenant_id})
        if not user:
            raise NotFoundException("User not found")
        
        phone_number = user.get("phone_verification_number")
        
        # Mark phone as verified
        db.users.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "phone_number": phone_number,
                    "phone_verified": True,
                    "phone_verified_at": datetime.utcnow(),
                    "phone_verification_number": None,
                    "phone_verification_attempts": 0
                }
            }
        )
        
        # Clear verification code
        RedisCache.delete(code_cache_key)
        
        # Log security event
        try:
            from app.services.audit_log_service import audit_log_service
            await audit_log_service.log_event(
                user_id=user_id,
                tenant_id=tenant_id,
                event_type="phone_verified",
                request_info=request_info,
                success=True,
                details={"phone_number": phone_number}
            )
        except Exception as e:
            logger.error(f"Failed to log audit event: {str(e)}")
        
        logger.info(f"Phone verified for user {user_id}")
        return True


# Create singleton instance
profile_enhancement_service = ProfileEnhancementService()
