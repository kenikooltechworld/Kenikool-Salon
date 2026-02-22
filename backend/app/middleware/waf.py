"""WAF middleware for enforcing security rules."""

import logging
import json
from typing import Callable
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from app.security.waf_rules import WAFRules

logger = logging.getLogger(__name__)


class WAFMiddleware(BaseHTTPMiddleware):
    """Web Application Firewall middleware."""

    # Endpoints that should skip WAF checks (e.g., health checks)
    SKIP_WAF_PATHS = {
        "/health",
        "/docs",
        "/openapi.json",
        "/redoc",
    }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Apply WAF rules to incoming requests."""
        # Skip WAF checks for certain paths
        if request.url.path in self.SKIP_WAF_PATHS:
            return await call_next(request)

        # Check query parameters
        if request.query_params:
            violations = WAFRules.validate_all(dict(request.query_params))
            if violations:
                logger.warning(f"WAF violation in query params: {violations}")
                raise HTTPException(
                    status_code=400,
                    detail="Invalid request parameters",
                )

        # Check request body for POST/PUT/PATCH requests
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    try:
                        data = json.loads(body)
                        violations = WAFRules.validate_all(data)
                        if violations:
                            logger.warning(f"WAF violation in request body: {violations}")
                            raise HTTPException(
                                status_code=400,
                                detail="Invalid request data",
                            )
                    except json.JSONDecodeError:
                        # Not JSON, skip validation
                        pass

                # Recreate request body for downstream handlers
                async def receive():
                    return {"type": "http.request", "body": body}

                request._receive = receive
            except Exception as e:
                logger.error(f"Error reading request body: {e}")
                raise HTTPException(
                    status_code=400,
                    detail="Invalid request",
                )

        # Check headers
        headers_dict = dict(request.headers)
        violations = WAFRules.validate_all(headers_dict)
        if violations:
            logger.warning(f"WAF violation in headers: {violations}")
            raise HTTPException(
                status_code=400,
                detail="Invalid request headers",
            )

        response = await call_next(request)
        return response
