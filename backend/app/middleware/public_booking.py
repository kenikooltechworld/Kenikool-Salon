"""Middleware for public booking validation and rate limiting."""

import logging
from datetime import datetime, timedelta
from typing import Callable

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.cache import cache
from app.models.tenant import Tenant
from bson import ObjectId

logger = logging.getLogger(__name__)


class PublicBookingMiddleware(BaseHTTPMiddleware):
    """Middleware for public booking validation and rate limiting."""

    RATE_LIMIT_BOOKINGS_PER_MINUTE = 10
    RATE_LIMIT_WINDOW_SECONDS = 60

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """
        Process public booking requests.

        Validates:
        - Tenant is active and published
        - Rate limiting (10 bookings per minute per IP)
        - Logs all public booking requests
        """
        # Only apply to public booking endpoints
        if not request.url.path.startswith("/public"):
            return await call_next(request)

        # Get tenant ID from request context (set by subdomain middleware)
        tenant_id = request.scope.get("tenant_id")
        if not tenant_id:
            logger.warning(f"Public booking request without tenant_id: {request.url}")
            raise HTTPException(status_code=403, detail="Tenant not found")

        try:
            tenant_id_obj = ObjectId(tenant_id)
        except Exception:
            logger.warning(f"Invalid tenant_id format: {tenant_id}")
            raise HTTPException(status_code=400, detail="Invalid tenant ID")

        # Verify tenant is active and published
        tenant = Tenant.objects(id=tenant_id_obj).first()
        if not tenant or not tenant.is_published:
            logger.warning(f"Public booking request for inactive tenant: {tenant_id}")
            raise HTTPException(status_code=404, detail="Salon not found")

        # Apply rate limiting for booking creation
        if request.method == "POST" and request.url.path == "/public/bookings":
            client_ip = request.client.host if request.client else "unknown"
            rate_limit_key = f"public_booking_rate_limit:{tenant_id}:{client_ip}"

            # Get current count
            current_count = cache.get(rate_limit_key) or 0

            if current_count >= self.RATE_LIMIT_BOOKINGS_PER_MINUTE:
                logger.warning(
                    f"Rate limit exceeded for {client_ip} on tenant {tenant_id}"
                )
                raise HTTPException(
                    status_code=429,
                    detail="Too many booking requests. Please try again later.",
                )

            # Increment counter
            cache.set(
                rate_limit_key,
                current_count + 1,
                self.RATE_LIMIT_WINDOW_SECONDS,
            )

        # Log public booking request
        logger.info(
            f"Public booking request: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'} "
            f"for tenant {tenant_id}"
        )

        # Set is_public flag in request context
        request.scope["is_public"] = True

        # Process request
        response = await call_next(request)

        return response


class PublicBookingRateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for public booking rate limiting."""

    RATE_LIMIT_REQUESTS_PER_MINUTE = 100
    RATE_LIMIT_WINDOW_SECONDS = 60

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """
        Rate limit public booking requests.

        Limits:
        - 100 requests per minute per IP address
        """
        # Only apply to public endpoints
        if not request.url.path.startswith("/public"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        rate_limit_key = f"public_api_rate_limit:{client_ip}"

        # Get current count
        current_count = cache.get(rate_limit_key) or 0

        if current_count >= self.RATE_LIMIT_REQUESTS_PER_MINUTE:
            logger.warning(f"API rate limit exceeded for {client_ip}")
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later.",
                headers={"Retry-After": str(self.RATE_LIMIT_WINDOW_SECONDS)},
            )

        # Increment counter
        cache.set(
            rate_limit_key,
            current_count + 1,
            self.RATE_LIMIT_WINDOW_SECONDS,
        )

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(
            self.RATE_LIMIT_REQUESTS_PER_MINUTE
        )
        response.headers["X-RateLimit-Remaining"] = str(
            max(0, self.RATE_LIMIT_REQUESTS_PER_MINUTE - current_count - 1)
        )
        response.headers["X-RateLimit-Reset"] = str(
            int((datetime.utcnow() + timedelta(seconds=self.RATE_LIMIT_WINDOW_SECONDS)).timestamp())
        )

        return response
