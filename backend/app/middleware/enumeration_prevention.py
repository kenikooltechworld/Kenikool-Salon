"""Account enumeration prevention middleware."""

import logging
import time
import hmac
import hashlib
from typing import Callable
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from app.cache import redis_client

logger = logging.getLogger(__name__)

# Rate limiting configuration for enumeration prevention
REGISTRATION_RATE_LIMIT = 3  # attempts per minute
REGISTRATION_RATE_WINDOW = 60  # seconds
PASSWORD_RESET_RATE_LIMIT = 3  # attempts per minute
PASSWORD_RESET_RATE_WINDOW = 60  # seconds


class EnumerationPreventionMiddleware(BaseHTTPMiddleware):
    """Prevent account enumeration attacks."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Apply enumeration prevention to requests."""
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Apply rate limiting to registration endpoint
        if request.url.path.endswith("/auth/register"):
            is_limited = await self._check_registration_rate_limit(client_ip)
            if is_limited:
                logger.warning(f"Registration rate limit exceeded for IP: {client_ip}")
                # Return generic error to prevent enumeration
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests. Please try again later.",
                )

        # Apply rate limiting to password reset endpoint
        if request.url.path.endswith("/auth/forgot-password"):
            is_limited = await self._check_password_reset_rate_limit(client_ip)
            if is_limited:
                logger.warning(f"Password reset rate limit exceeded for IP: {client_ip}")
                # Return generic error to prevent enumeration
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests. Please try again later.",
                )

        response = await call_next(request)
        return response

    async def _check_registration_rate_limit(self, client_ip: str) -> bool:
        """Check if client has exceeded registration rate limit."""
        if not redis_client:
            return False

        key = f"registration_attempts:{client_ip}"

        try:
            attempts = redis_client.incr(key)

            # Set expiration on first attempt
            if attempts == 1:
                redis_client.expire(key, REGISTRATION_RATE_WINDOW)

            return attempts > REGISTRATION_RATE_LIMIT
        except Exception as e:
            logger.error(f"Error checking registration rate limit: {e}")
            return False

    async def _check_password_reset_rate_limit(self, client_ip: str) -> bool:
        """Check if client has exceeded password reset rate limit."""
        if not redis_client:
            return False

        key = f"password_reset_attempts:{client_ip}"

        try:
            attempts = redis_client.incr(key)

            # Set expiration on first attempt
            if attempts == 1:
                redis_client.expire(key, PASSWORD_RESET_RATE_WINDOW)

            return attempts > PASSWORD_RESET_RATE_LIMIT
        except Exception as e:
            logger.error(f"Error checking password reset rate limit: {e}")
            return False


def constant_time_compare(a: str, b: str) -> bool:
    """Compare two strings in constant time to prevent timing attacks."""
    return hmac.compare_digest(a, b)


def get_generic_error_message(error_type: str) -> str:
    """Get generic error message to prevent account enumeration."""
    generic_messages = {
        "login": "Invalid credentials",
        "registration": "Registration failed. Please try again.",
        "password_reset": "If an account exists with that email, you will receive a password reset link.",
        "email_exists": "If an account exists with that email, you will receive a password reset link.",
        "user_not_found": "Invalid credentials",
    }
    return generic_messages.get(error_type, "An error occurred. Please try again.")


def add_timing_delay(base_time: float = 0.1) -> None:
    """Add random delay to prevent timing attacks."""
    import random

    # Add random delay between 0 and base_time
    delay = random.uniform(0, base_time)
    time.sleep(delay)
