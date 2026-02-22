"""Rate limiting and brute force protection middleware."""

import logging
import time
from typing import Optional
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from app.cache import redis_client

logger = logging.getLogger(__name__)

# Rate limiting configuration
LOGIN_RATE_LIMIT = 5  # attempts per minute
LOGIN_RATE_WINDOW = 60  # seconds
ACCOUNT_LOCKOUT_THRESHOLD = 5  # failed attempts
ACCOUNT_LOCKOUT_DURATION = 15 * 60  # 15 minutes in seconds


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting and brute force protection."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """Apply rate limiting to requests."""
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Apply rate limiting to login endpoint
        if request.url.path.endswith("/auth/login"):
            is_limited = await self._check_login_rate_limit(client_ip)
            if is_limited:
                logger.warning(f"Login rate limit exceeded for IP: {client_ip}")
                raise HTTPException(
                    status_code=429,
                    detail="Too many login attempts. Please try again later.",
                )

        response = await call_next(request)
        return response

    async def _check_login_rate_limit(self, client_ip: str) -> bool:
        """Check if client has exceeded login rate limit."""
        if not redis_client:
            return False

        key = f"login_attempts:{client_ip}"

        try:
            attempts = redis_client.incr(key)

            # Set expiration on first attempt
            if attempts == 1:
                redis_client.expire(key, LOGIN_RATE_WINDOW)

            return attempts > LOGIN_RATE_LIMIT
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return False


def get_login_attempts(email: str) -> int:
    """Get failed login attempts for user."""
    if not redis_client:
        return 0

    key = f"failed_login:{email}"
    try:
        attempts = redis_client.get(key)
        return int(attempts) if attempts else 0
    except Exception as e:
        logger.error(f"Error getting login attempts: {e}")
        return 0


def increment_login_attempts(email: str) -> int:
    """Increment failed login attempts for user."""
    if not redis_client:
        return 0

    key = f"failed_login:{email}"
    try:
        attempts = redis_client.incr(key)
        # Set expiration to 1 hour
        redis_client.expire(key, 3600)
        return attempts
    except Exception as e:
        logger.error(f"Error incrementing login attempts: {e}")
        return 0


def reset_login_attempts(email: str) -> None:
    """Reset failed login attempts for user."""
    if not redis_client:
        return

    key = f"failed_login:{email}"
    try:
        redis_client.delete(key)
    except Exception as e:
        logger.error(f"Error resetting login attempts: {e}")


def is_account_locked(email: str) -> bool:
    """Check if account is locked due to failed attempts."""
    if not redis_client:
        return False

    key = f"account_locked:{email}"
    try:
        locked = redis_client.get(key)
        return locked is not None
    except Exception as e:
        logger.error(f"Error checking account lock: {e}")
        return False


def lock_account(email: str) -> None:
    """Lock account after too many failed attempts."""
    if not redis_client:
        return

    key = f"account_locked:{email}"
    try:
        redis_client.setex(key, ACCOUNT_LOCKOUT_DURATION, "1")
        logger.warning(f"Account locked: {email}")
    except Exception as e:
        logger.error(f"Error locking account: {e}")


def unlock_account(email: str) -> None:
    """Unlock account."""
    if not redis_client:
        return

    key = f"account_locked:{email}"
    try:
        redis_client.delete(key)
        logger.info(f"Account unlocked: {email}")
    except Exception as e:
        logger.error(f"Error unlocking account: {e}")
