"""Tenant context middleware for multi-tenant isolation."""

import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from bson import ObjectId
from jose import jwt, JWTError
from app.context import set_tenant_id, set_user_id, clear_context, get_tenant_id as context_get_tenant_id
from app.config import settings

logger = logging.getLogger(__name__)


def get_tenant_id():
    """Get tenant_id from context."""
    return context_get_tenant_id()


class TenantContextMiddleware(BaseHTTPMiddleware):
    """Middleware to extract and set tenant context from JWT token or cookies."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Extract tenant_id and user_id from JWT token or cookies and set in context."""
        try:
            # Extract tenant_id and user_id from request state (set by auth middleware)
            tenant_id = getattr(request.state, "tenant_id", None)
            user_id = getattr(request.state, "user_id", None)

            logger.info(f"[TenantContext] Initial state - tenant_id: {tenant_id}, user_id: {user_id}")
            logger.info(f"[TenantContext] Cookies: {list(request.cookies.keys())}")

            # If not in request state, try to extract from JWT token in access_token cookie
            if not tenant_id or not user_id:
                access_token = request.cookies.get("access_token")
                logger.info(f"[TenantContext] access_token present: {bool(access_token)}")
                
                if access_token:
                    try:
                        payload = jwt.decode(
                            access_token,
                            settings.jwt_secret_key,
                            algorithms=[settings.jwt_algorithm]
                        )
                        logger.info(f"[TenantContext] JWT payload: {payload}")
                        if not tenant_id:
                            tenant_id = payload.get("tenant_id")
                        if not user_id:
                            user_id = payload.get("sub")
                    except JWTError as e:
                        logger.warning(f"[TenantContext] Failed to decode JWT token: {e}")

            # Fallback to cookies if JWT extraction failed
            if not tenant_id:
                tenant_id = request.cookies.get("tenant_id")
                logger.info(f"[TenantContext] tenant_id from cookie: {tenant_id}")
            
            if not user_id:
                user_id = request.cookies.get("user_id")
                logger.info(f"[TenantContext] user_id from cookie: {user_id}")

            logger.info(f"[TenantContext] Final - tenant_id: {tenant_id}, user_id: {user_id}")

            if tenant_id:
                try:
                    if isinstance(tenant_id, str):
                        set_tenant_id(ObjectId(tenant_id))
                    else:
                        set_tenant_id(tenant_id)
                except Exception as e:
                    logger.warning(f"[TenantContext] Failed to convert tenant_id to ObjectId: {e}")

            if user_id:
                try:
                    if isinstance(user_id, str):
                        set_user_id(ObjectId(user_id))
                    else:
                        set_user_id(user_id)
                except Exception as e:
                    logger.warning(f"[TenantContext] Failed to convert user_id to ObjectId: {e}")

            response = await call_next(request)

        finally:
            # Clear context after request
            clear_context()

        return response
