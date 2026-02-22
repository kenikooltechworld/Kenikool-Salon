"""Logging and request ID middleware."""

import logging
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add request ID to all requests for tracing."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add request ID to request and response."""
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests and responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request and response details."""
        request_id = getattr(request.state, "request_id", "unknown")
        
        # Log request with query params
        query_string = str(request.url.query) if request.url.query else ""
        query_info = f"?{query_string}" if query_string else ""
        
        logger.info(
            f"[{request_id}] {request.method} {request.url.path}{query_info}"
        )

        response = await call_next(request)

        logger.info(
            f"[{request_id}] {request.method} {request.url.path}{query_info} - {response.status_code}"
        )

        return response
