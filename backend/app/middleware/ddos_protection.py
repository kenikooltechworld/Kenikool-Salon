"""
DDoS Protection Middleware

Monitors request rates per IP, blocks IPs exceeding thresholds,
implements exponential backoff, and tracks DDoS attempts.
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import redis

from app.security.ddos_protection import DDoSProtection, RequestPattern, ThreatLevel

logger = logging.getLogger(__name__)


class DDoSProtectionMiddleware(BaseHTTPMiddleware):
    """
    Middleware for DDoS protection with rate limiting and pattern analysis.
    """

    def __init__(self, app, redis_client: redis.Redis, ddos_protection: DDoSProtection, trusted_ips: list = None):
        """
        Initialize DDoS protection middleware.

        Args:
            app: FastAPI application
            redis_client: Redis client for distributed rate limiting
            ddos_protection: DDoS protection instance
            trusted_ips: List of trusted IP addresses
        """
        super().__init__(app)
        self.redis = redis_client
        self.ddos_protection = ddos_protection
        self.trusted_ips = set(trusted_ips or [])

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request through DDoS protection.

        Args:
            request: HTTP request
            call_next: Next middleware/handler

        Returns:
            HTTP response
        """
        # Get client IP address
        client_ip = self._get_client_ip(request)

        # Check if IP is trusted
        is_trusted = client_ip in self.trusted_ips

        # Check rate limit
        allowed, reason = self.ddos_protection.check_rate_limit(client_ip, is_trusted)
        if not allowed:
            logger.warning(f"DDoS protection: {reason} for IP {client_ip}")
            return JSONResponse(
                status_code=429,
                content={"error": "Too many requests", "detail": reason}
            )

        # Record request start time
        start_time = time.time()

        try:
            # Call next middleware/handler
            response = await call_next(request)
            response_time_ms = (time.time() - start_time) * 1000

            # Analyze request pattern
            pattern = RequestPattern(
                timestamp=start_time,
                ip_address=client_ip,
                endpoint=request.url.path,
                method=request.method,
                response_time_ms=response_time_ms,
                status_code=response.status_code,
                payload_size=len(await request.body()) if hasattr(request, 'body') else 0
            )

            threat_level, threat_score = self.ddos_protection.analyze_request_pattern(pattern)

            # Log threat if detected
            if threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
                logger.warning(
                    f"DDoS threat detected: IP={client_ip}, level={threat_level.value}, "
                    f"score={threat_score:.1f}, endpoint={request.url.path}"
                )
                self._log_ddos_event(client_ip, threat_level, threat_score)

            # Check circuit breaker
            if self.ddos_protection.is_circuit_open(request.url.path):
                logger.warning(f"Circuit breaker open for {request.url.path}")
                return JSONResponse(
                    status_code=503,
                    content={"error": "Service temporarily unavailable"}
                )

            # Record request result
            self.ddos_protection.record_request(request.url.path, response.status_code < 500)

            return response

        except Exception as e:
            logger.error(f"Error in DDoS protection middleware: {e}")
            # Fail open - allow request if error occurs
            return await call_next(request)

    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP address from request.

        Args:
            request: HTTP request

        Returns:
            Client IP address
        """
        # Check X-Forwarded-For header (for proxied requests)
        if "x-forwarded-for" in request.headers:
            return request.headers["x-forwarded-for"].split(",")[0].strip()

        # Check X-Real-IP header
        if "x-real-ip" in request.headers:
            return request.headers["x-real-ip"]

        # Use direct connection IP
        return request.client.host if request.client else "unknown"

    def _log_ddos_event(self, ip_address: str, threat_level: ThreatLevel, threat_score: float):
        """
        Log DDoS event to Redis for monitoring.

        Args:
            ip_address: Client IP address
            threat_level: Threat level classification
            threat_score: Threat score
        """
        try:
            event_key = f"ddos:events:{ip_address}"
            event_data = {
                "timestamp": time.time(),
                "threat_level": threat_level.value,
                "threat_score": threat_score
            }
            self.redis.lpush(event_key, str(event_data))
            self.redis.expire(event_key, 86400)  # Keep for 24 hours
        except Exception as e:
            logger.error(f"Error logging DDoS event: {e}")
