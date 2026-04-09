"""Authentication service for user login, logout, and token management with httpOnly cookies."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
import secrets
import hashlib
import bcrypt
from jose import JWTError, jwt
from app.config import Settings
from app.models.user import User
from app.models.session import Session
from app.context import get_tenant_id

logger = logging.getLogger(__name__)


class AuthenticationService:
    """Service for handling user authentication."""

    def __init__(self, settings: Settings):
        """Initialize authentication service."""
        self.settings = settings
        self.algorithm = settings.jwt_algorithm
        self.secret_key = settings.jwt_secret_key
        self.access_token_expire_minutes = settings.jwt_access_token_expire_minutes
        self.refresh_token_expire_days = settings.jwt_refresh_token_expire_days

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    def create_access_token(
        self, user_id: str, tenant_id: str, email: str, role_ids: list = None, 
        permissions: list = None, expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token with support for multiple roles."""
        if expires_delta is None:
            expires_delta = timedelta(minutes=self.access_token_expire_minutes)

        expire = datetime.utcnow() + expires_delta
        to_encode = {
            "sub": str(user_id),
            "tenant_id": str(tenant_id),
            "email": email,
            "role_ids": [str(rid) for rid in (role_ids or [])],
            "permissions": permissions or [],
            "iat": datetime.utcnow(),
            "exp": expire,
        }

        encoded_jwt = jwt.encode(
            to_encode, self.secret_key, algorithm=self.algorithm
        )
        return encoded_jwt

    def create_refresh_token(
        self, user_id: str, tenant_id: str, expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT refresh token."""
        if expires_delta is None:
            expires_delta = timedelta(days=self.refresh_token_expire_days)

        expire = datetime.utcnow() + expires_delta
        to_encode = {
            "sub": str(user_id),
            "tenant_id": str(tenant_id),
            "type": "refresh",
            "iat": datetime.utcnow(),
            "exp": expire,
        }

        encoded_jwt = jwt.encode(
            to_encode, self.secret_key, algorithm=self.algorithm
        )
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            logger.warning(f"Token verification failed: {e}")
            return None

    def generate_browser_fingerprint(self, user_agent: str, ip_address: str) -> str:
        """Generate a unique browser fingerprint from user agent and IP."""
        fingerprint_data = f"{user_agent}:{ip_address}"
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()

    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """
        Refresh access token using a valid refresh token.
        
        Args:
            refresh_token: The refresh token from the cookie
            
        Returns:
            New access token if refresh is successful, None otherwise
        """
        try:
            # Verify the refresh token
            payload = self.verify_token(refresh_token)
            if not payload:
                logger.warning("Refresh token verification failed")
                return None
            
            # Check if it's actually a refresh token
            if payload.get("type") != "refresh":
                logger.warning("Token is not a refresh token")
                return None
            
            user_id = payload.get("sub")
            tenant_id = payload.get("tenant_id")
            
            if not user_id or not tenant_id:
                logger.warning("Invalid refresh token claims")
                return None
            
            # Get user to extract current role_ids and permissions
            user = User.objects(id=user_id, tenant_id=tenant_id).first()
            if not user:
                logger.warning(f"User not found for refresh: {user_id}")
                return None
            
            # Create new access token
            new_access_token = self.create_access_token(
                user_id=user_id,
                tenant_id=tenant_id,
                email=user.email,
                role_ids=user.role_ids,
            )
            
            logger.info(f"Access token refreshed for user: {user_id}")
            return new_access_token
            
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return None

    def authenticate_user(
        self, email: str, password: str, tenant_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Authenticate a user with email and password.
        
        Args:
            email: User email
            password: User password
            tenant_id: Optional tenant_id. If None, will be looked up from user.
        """
        try:
            from app.models.tenant import Tenant
            from datetime import datetime, timedelta

            # Look up user by email
            user = User.objects(email=email).first()
            if not user:
                logger.warning(f"User not found: {email}")
                return None

            # If tenant_id not provided, get it from user
            if tenant_id is None:
                tenant_id = str(user.tenant_id)
            
            # Verify tenant_id matches if provided
            if str(user.tenant_id) != tenant_id:
                logger.warning(f"Tenant mismatch for user: {email}")
                return None

            # Check if tenant is deleted
            tenant = Tenant.objects(id=tenant_id).first()
            if tenant and tenant.deletion_status == "soft_deleted":
                grace_period_days = 14
                days_remaining = (
                    tenant.recovery_token_expires_at - datetime.utcnow()
                ).days
                
                if days_remaining > 0:
                    logger.warning(f"Tenant deleted but within grace period: {tenant_id}")
                    return {
                        "error": "account_deleted",
                        "message": "Your account is deactivated",
                        "days_remaining": max(0, days_remaining),
                        "recovery_token": tenant.recovery_token,
                    }
                else:
                    logger.warning(f"Tenant deleted and grace period expired: {tenant_id}")
                    return {
                        "error": "account_permanently_deleted",
                        "message": "Your account was permanently deleted",
                        "paid_recovery_available": True,
                    }

            if not self.verify_password(password, user.password_hash):
                logger.warning(f"Invalid password for user: {email}")
                return None

            if user.status != "active":
                logger.warning(f"User account not active: {email}")
                return None

            return {
                "user_id": str(user.id),
                "email": user.email,
                "tenant_id": tenant_id,
                "role_ids": [str(rid) for rid in user.role_ids],
                "mfa_enabled": user.mfa_enabled,
                "mfa_method": user.mfa_method,
                "password_change_required": user.password_change_required,
            }
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None

    def create_session(
        self,
        user_id: str,
        tenant_id: str,
        token: str,
        refresh_token: str,
        ip_address: str,
        user_agent: str,
    ) -> Optional[Session]:
        """Create a new session with CSRF token."""
        try:
            expires_at = datetime.utcnow() + timedelta(
                minutes=self.access_token_expire_minutes
            )

            # Generate browser fingerprint
            browser_fingerprint = self.generate_browser_fingerprint(user_agent, ip_address)

            # Generate CSRF token
            csrf_token = self.generate_csrf_token()
            csrf_token_hash = self.hash_csrf_token(csrf_token)

            session = Session(
                tenant_id=tenant_id,
                user_id=user_id,
                token=token,
                refresh_token=refresh_token,
                csrf_token_hash=csrf_token_hash,
                expires_at=expires_at,
                ip_address=ip_address,
                user_agent=user_agent,
                browser_fingerprint=browser_fingerprint,
                status="active",
            )
            session.save()
            logger.info(f"Session created for user: {user_id} with fingerprint: {browser_fingerprint}")
            # Store CSRF token in session for later retrieval
            session.csrf_token = csrf_token
            return session
        except Exception as e:
            logger.error(f"Session creation error: {e}")
            return None

    def invalidate_session(self, session_id: str, tenant_id: str) -> bool:
        """Invalidate a session."""
        try:
            session = Session.objects(id=session_id, tenant_id=tenant_id).first()
            if session:
                session.status = "revoked"
                session.save()
                logger.info(f"Session invalidated: {session_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Session invalidation error: {e}")
            return False

    def invalidate_user_sessions(self, user_id: str, tenant_id: str) -> bool:
        """Invalidate all sessions for a user."""
        try:
            sessions = Session.objects(
                tenant_id=tenant_id, user_id=user_id, status="active"
            )
            for session in sessions:
                session.status = "revoked"
                session.save()
            logger.info(f"All sessions invalidated for user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"User session invalidation error: {e}")
            return False

    def get_active_sessions(self, user_id: str, tenant_id: str) -> list:
        """Get all active sessions for a user."""
        try:
            sessions = Session.objects(
                tenant_id=tenant_id, user_id=user_id, status="active"
            )
            return list(sessions)
        except Exception as e:
            logger.error(f"Error retrieving sessions: {e}")
            return []

    def enforce_concurrent_session_limit(
        self, user_id: str, tenant_id: str, max_sessions: int = 5
    ) -> bool:
        """Enforce concurrent session limit by invalidating oldest sessions."""
        try:
            active_sessions = Session.objects(
                tenant_id=tenant_id, user_id=user_id, status="active"
            ).order_by("created_at")

            if len(active_sessions) >= max_sessions:
                # Invalidate oldest session
                oldest_session = active_sessions[0]
                oldest_session.status = "revoked"
                oldest_session.save()
                logger.info(
                    f"Oldest session invalidated for user {user_id} to enforce limit"
                )
                return True
            return False
        except Exception as e:
            logger.error(f"Error enforcing session limit: {e}")
            return False

    def generate_csrf_token(self) -> str:
        """Generate a CSRF token."""
        return secrets.token_urlsafe(32)

    def verify_csrf_token(self, token: str, stored_hash: str) -> bool:
        """Verify a CSRF token against its stored hash."""
        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            return token_hash == stored_hash
        except Exception as e:
            logger.error(f"CSRF token verification error: {e}")
            return False

    def hash_csrf_token(self, token: str) -> str:
        """Hash a CSRF token for storage."""
        return hashlib.sha256(token.encode()).hexdigest()
