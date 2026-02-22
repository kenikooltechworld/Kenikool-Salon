"""Audit logging middleware for tracking all operations."""

import logging
import json
from typing import Any, Dict
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)

# Sensitive fields to redact from logs
SENSITIVE_FIELDS = {
    "password",
    "password_hash",
    "token",
    "access_token",
    "refresh_token",
    "csrf_token",
    "mfa_secret",
    "api_key",
    "secret",
    "credit_card",
    "ssn",
}

# Endpoints to exclude from audit logging
EXCLUDED_ENDPOINTS = {
    "/health",
    "/docs",
    "/openapi.json",
    "/redoc",
}


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """Log all operations for audit trail."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """Log request and response."""
        # Skip excluded endpoints
        if request.url.path in EXCLUDED_ENDPOINTS:
            return await call_next(request)

        # Get request details
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path
        user_id = request.headers.get("X-User-ID")
        tenant_id = request.headers.get("X-Tenant-ID")

        # Read request body if present
        body = None
        if method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    body = body.decode("utf-8")
            except Exception as e:
                logger.error(f"Error reading request body: {e}")

        # Process request
        response = await call_next(request)

        # Log audit event
        try:
            audit_service = AuditService()
            request_body_dict = None
            if body:
                try:
                    request_body_dict = json.loads(body) if isinstance(body, str) else body
                    if not isinstance(request_body_dict, dict):
                        request_body_dict = None
                except (json.JSONDecodeError, TypeError):
                    request_body_dict = None
            
            await audit_service.log_event(
                event_type=method,
                resource=path,
                user_id=user_id,
                tenant_id=tenant_id,
                ip_address=client_ip,
                status_code=response.status_code,
                request_body=_redact_sensitive_data(request_body_dict) if request_body_dict else None,
                user_agent=request.headers.get("user-agent"),
            )
        except Exception as e:
            logger.error(f"Error logging audit event: {e}")

        return response


def _redact_sensitive_data(data: Any) -> Any:
    """Redact sensitive fields from data."""
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except (json.JSONDecodeError, TypeError):
            return data

    if isinstance(data, dict):
        redacted = {}
        for key, value in data.items():
            if key.lower() in SENSITIVE_FIELDS:
                redacted[key] = "[REDACTED]"
            elif isinstance(value, dict):
                redacted[key] = _redact_sensitive_data(value)
            elif isinstance(value, list):
                redacted[key] = [
                    _redact_sensitive_data(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                redacted[key] = value
        return redacted

    return data
