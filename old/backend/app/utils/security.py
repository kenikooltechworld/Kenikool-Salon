"""
Security utilities for password hashing and JWT tokens
"""
import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
from app.config import settings
import logging

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt
    
    Note: Bcrypt has a 72-byte limit on passwords. Passwords longer than 72 bytes
    are truncated at the byte level to ensure compatibility.
    """
    # Bcrypt has a 72-byte limit - truncate at byte level
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # Hash using bcrypt directly
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash
    
    Note: Passwords are truncated to 72 bytes to match the hashing behavior.
    """
    # Apply same truncation for consistency with hash_password
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # Verify using bcrypt directly
    try:
        return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))
    except Exception as e:
        logger.error(f"Password verification error: {str(e)}")
        return False


def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict]:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        return None


def decode_access_token(token: str) -> Dict:
    """
    Decode and validate JWT access token
    
    Raises:
        Exception: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        
        # Verify it's an access token
        if payload.get("type") != "access":
            raise Exception("Invalid token type")
        
        return payload
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise Exception(f"Invalid or expired token: {str(e)}")


def generate_subdomain(salon_name: str) -> str:
    """Generate a URL-safe subdomain from salon name"""
    import re
    # Convert to lowercase and replace spaces with hyphens
    subdomain = salon_name.lower().strip()
    # Remove special characters
    subdomain = re.sub(r'[^a-z0-9\s-]', '', subdomain)
    # Replace spaces with hyphens
    subdomain = re.sub(r'\s+', '-', subdomain)
    # Remove consecutive hyphens
    subdomain = re.sub(r'-+', '-', subdomain)
    # Remove leading/trailing hyphens
    subdomain = subdomain.strip('-')
    return subdomain
