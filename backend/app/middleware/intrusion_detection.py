"""
Intrusion Detection Middleware

Monitors all requests for suspicious activity, tracks user behavior patterns,
detects anomalies in real-time, and generates alerts.
"""

import logging
import time
from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.security.intrusion_detection import IntrusionDetection, RequestMetrics

logger = logging.getLogger(__name__)


class IntrusionDetectionMiddleware(BaseHTTPMiddleware):
    """
    Middleware for intrusion detection with anomaly detection and behavioral analysis.
    """

    def __init__(self, app, intrusion_detection: IntrusionDetection):
        """
        Initialize intrusion detection middleware.

        Args:
            app: FastAPI application
            intrusion_detection: Intrusion detection instance
        """
        super().__init__(app)
        self.intrusion_detection = intrusion_detection

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request through intrusion detection.

        Args:
            request: HTTP request
            call_next: Next middleware/handler

        Returns:
            HTTP response
        """
        # Record request start time
        start_time = time.time()

        try:
            # Call next middleware/handler
            response = await call_next(request)
            response_time_ms = (time.time() - start_time) * 1000

            # Extract metrics
            metrics = self._extract_metrics(request, response, response_time_ms, start_time)

            # Detect anomalies
            anomalies = self.intrusion_detection.detect_anomalies(metrics)

            # Update user behavior
            self.intrusion_detection.update_user_behavior(metrics)

            # Generate alert if anomalies detected
            if anomalies:
                alert = self.intrusion_detection.generate_alert(metrics, anomalies)
                severity = alert.get("severity", "low")

                # Block request if critical
                if severity == "critical":
                    logger.error(f"Critical intrusion detected: {alert}")
                    return JSONResponse(
                        status_code=403,
                        content={"error": "Access denied"}
                    )

            return response

        except Exception as e:
            logger.error(f"Error in intrusion detection middleware: {e}")
            # Fail open - allow request if error occurs
            return await call_next(request)

    def _extract_metrics(
        self,
        request: Request,
        response: Response,
        response_time_ms: float,
        timestamp: float
    ) -> RequestMetrics:
        """
        Extract metrics from request and response.

        Args:
            request: HTTP request
            response: HTTP response
            response_time_ms: Response time in milliseconds
            timestamp: Request timestamp

        Returns:
            RequestMetrics object
        """
        # Get user ID from token if available
        user_id = self._extract_user_id(request)

        # Get client IP
        client_ip = self._get_client_ip(request)

        # Get geolocation (placeholder - would integrate with GeoIP service)
        geolocation = self._get_geolocation(client_ip)

        # Get request size
        request_size = len(await request.body()) if hasattr(request, 'body') else 0

        # Get user agent
        user_agent = request.headers.get("user-agent", "")

        return RequestMetrics(
            timestamp=timestamp,
            user_id=user_id,
            ip_address=client_ip,
            endpoint=request.url.path,
            method=request.method,
            request_size=request_size,
            response_time_ms=response_time_ms,
            status_code=response.status_code,
            user_agent=user_agent,
            geolocation=geolocation
        )

    def _extract_user_id(self, request: Request) -> Optional[str]:
        """
        Extract user ID from request.

        Args:
            request: HTTP request

        Returns:
            User ID or None
        """
        # Try to get from Authorization header
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            # In production, would decode JWT token
            return None

        # Try to get from query parameter
        user_id = request.query_params.get("user_id")
        if user_id:
            return user_id

        return None

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

    def _get_geolocation(self, ip_address: str) -> Optional[str]:
        """
        Get geolocation for IP address.

        Args:
            ip_address: IP address

        Returns:
            Geolocation or None
        """
        # Placeholder - would integrate with GeoIP service
        # For now, return None
        return None
