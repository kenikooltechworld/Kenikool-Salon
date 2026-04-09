"""Tenant context middleware for multi-tenant isolation."""

import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from bson import ObjectId
from jose import jwt, JWTError
from app.context import set_tenant_id, set_user_id, clear_context, get_tenant_id as context_get_tenant_id
from app.config import settings
from app.models.tenant import Tenant

logger = logging.getLogger(__name__)


def get_tenant_id():
    """Get tenant_id from context."""
    return context_get_tenant_id()


class TenantContextMiddleware(BaseHTTPMiddleware):
    """Middleware to extract and set tenant context from JWT token or cookies."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Extract tenant_id and user_id from JWT token or cookies and set in context."""
        try:
            # Skip tenant context for public endpoints that don't require authentication
            if self._should_skip_tenant_context(request):
                logger.info(f"[TenantContext] Skipping tenant context for {request.method} {request.url.path}")
                response = await call_next(request)
                return response
            
            # Extract tenant_id and user_id from request state (set by auth middleware)
            tenant_id = getattr(request.state, "tenant_id", None)
            user_id = getattr(request.state, "user_id", None)

            logger.info(f"[TenantContext] Initial state - tenant_id: {tenant_id}, user_id: {user_id}")
            logger.info(f"[TenantContext] Cookies: {list(request.cookies.keys())}")

            # Check if tenant_id is already set in scope (from SubdomainContextMiddleware for public endpoints)
            if not tenant_id:
                tenant_id = request.scope.get("tenant_id")
                logger.info(f"[TenantContext] tenant_id from scope: {tenant_id}")

            # If not in request state or scope, try to extract from JWT token in access_token cookie
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

            # Check if tenant is soft deleted (skip for recovery endpoints)
            if tenant_id and not request.url.path.startswith("/api/tenants/recover"):
                try:
                    tenant = Tenant.objects(id=tenant_id).first()
                    if tenant and tenant.deletion_status == "soft_deleted":
                        logger.warning(f"[TenantContext] Tenant is soft deleted: {tenant_id}")
                        # Don't set tenant_id in context for deleted tenants
                        tenant_id = None
                except Exception as e:
                    logger.warning(f"[TenantContext] Error checking tenant deletion status: {e}")

            if tenant_id:
                try:
                    if isinstance(tenant_id, str):
                        # Validate that tenant_id is a valid ObjectId before converting
                        try:
                            tenant_oid = ObjectId(tenant_id)
                            set_tenant_id(tenant_oid)
                        except Exception as oid_error:
                            logger.warning(f"[TenantContext] Invalid ObjectId format for tenant_id '{tenant_id}': {oid_error}")
                            # Don't set tenant_id if it's not a valid ObjectId
                    else:
                        set_tenant_id(tenant_id)
                    # Also set in scope for middleware that reads from scope
                    request.scope["tenant_id"] = str(tenant_id) if isinstance(tenant_id, ObjectId) else tenant_id
                except Exception as e:
                    logger.error(f"[TenantContext] Failed to set tenant_id: {e}")
                    # Don't set tenant_id if conversion fails
            else:
                logger.warning(f"[TenantContext] No tenant_id found in request")

            if user_id:
                try:
                    if isinstance(user_id, str):
                        # Validate that user_id is a valid ObjectId before converting
                        try:
                            user_oid = ObjectId(user_id)
                            set_user_id(user_oid)
                        except Exception as oid_error:
                            logger.warning(f"[TenantContext] Invalid ObjectId format for user_id '{user_id}': {oid_error}")
                            # Don't set user_id if it's not a valid ObjectId
                    else:
                        set_user_id(user_id)
                except Exception as e:
                    logger.warning(f"[TenantContext] Failed to set user_id: {e}")

            response = await call_next(request)

        finally:
            # Clear context after request
            clear_context()

        return response

    @staticmethod
    def _should_skip_tenant_context(request: Request) -> bool:
        """Check if request should skip tenant context extraction."""
        path = request.url.path
        
        # Skip for auth endpoints (login, register, etc.)
        if path.startswith("/api/auth/"):
            return True
        
        # Skip for registration endpoints
        if path.startswith("/api/registration/"):
            return True
        
        # Skip for tenant recovery endpoints
        if path.startswith("/api/tenants/recover"):
            return True
        
        # Skip for public booking endpoints
        if path.startswith("/api/public-booking/"):
            return True
        
        # Skip for health check
        if path in ["/health", "/"]:
            return True
        
        return False
