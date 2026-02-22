"""Input validation middleware for FastAPI."""

import logging
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)

# Maximum request body size: 10MB
MAX_REQUEST_SIZE = 10 * 1024 * 1024

# Allowed content types for POST/PUT/PATCH
ALLOWED_CONTENT_TYPES = {
    "application/json",
    "application/x-www-form-urlencoded",
    "multipart/form-data",
}


class ValidationMiddleware(BaseHTTPMiddleware):
    """Validate incoming requests."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """Validate request before processing."""
        # Check Content-Type for requests with body
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "").split(";")[0]

            if content_type and content_type not in ALLOWED_CONTENT_TYPES:
                logger.warning(
                    f"Invalid Content-Type: {content_type} from {request.client.host}"
                )
                raise HTTPException(
                    status_code=415,
                    detail="Unsupported Media Type",
                )

        # Check Content-Length
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                if size > MAX_REQUEST_SIZE:
                    logger.warning(
                        f"Request too large: {size} bytes from {request.client.host}"
                    )
                    raise HTTPException(
                        status_code=413,
                        detail="Request entity too large",
                    )
            except ValueError:
                logger.warning(
                    f"Invalid Content-Length header from {request.client.host}"
                )
                raise HTTPException(
                    status_code=400,
                    detail="Invalid Content-Length",
                )

        response = await call_next(request)
        return response
