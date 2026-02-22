"""Middleware for extracting subdomain and setting tenant context."""

import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.context import set_tenant_id

logger = logging.getLogger(__name__)


class SubdomainContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract subdomain from request hostname and set tenant context.
    
    Supports:
    - Subdomain routing: acme-salon.kenikool.com -> tenant lookup
    - Localhost development: localhost:8000 -> no tenant required
    - Direct IP access: 192.168.1.1:8000 -> no tenant required
    """

    async def dispatch(self, request: Request, call_next):
        """Process request and extract subdomain."""
        # Skip subdomain extraction for webhooks (they're server-to-server calls)
        if request.url.path.startswith("/webhooks"):
            return await call_next(request)
        
        # Get hostname from request
        hostname = request.headers.get("host", "").lower()
        
        # Skip subdomain extraction for localhost and IP addresses
        if hostname.startswith("localhost") or hostname.startswith("127.0.0.1"):
            # Allow localhost for development
            return await call_next(request)

        # Check if it's an IP address (simple check)
        if self._is_ip_address(hostname):
            return await call_next(request)

        # Extract subdomain from hostname
        subdomain = self._extract_subdomain(hostname)
        
        if not subdomain:
            # No subdomain found, allow request to proceed
            # (might be root domain or API gateway)
            return await call_next(request)

        # Look up tenant by subdomain
        try:
            # Lazy-load Tenant model to avoid import-time database connection
            from app.models.tenant import Tenant
            
            # Skip tenant lookup if database is not available
            try:
                tenant = Tenant.objects(subdomain=subdomain, status="active").first()
            except Exception as db_error:
                logger.warning(f"Database unavailable for tenant lookup: {db_error}")
                # Allow request to proceed without tenant context
                return await call_next(request)
            
            if not tenant:
                logger.warning(f"Tenant not found for subdomain: {subdomain}")
                return JSONResponse(
                    status_code=404,
                    content={
                        "success": False,
                        "error": {
                            "code": "TENANT_NOT_FOUND",
                            "message": "Salon not found",
                        },
                    },
                )

            # Set tenant context for this request
            set_tenant_id(str(tenant.id))
            request.state.tenant_id = str(tenant.id)
            request.state.tenant = tenant

            logger.debug(f"Tenant context set for subdomain: {subdomain}")

        except Exception as e:
            logger.error(f"Error looking up tenant for subdomain {subdomain}: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": {
                        "code": "INTERNAL_SERVER_ERROR",
                        "message": "Failed to process request",
                    },
                },
            )

        # Continue with request
        response = await call_next(request)
        return response

    @staticmethod
    def _extract_subdomain(hostname: str) -> str:
        """
        Extract subdomain from hostname.
        
        Examples:
        - acme-salon.kenikool.com -> acme-salon
        - api.kenikool.com -> api
        - kenikool.com -> (empty)
        - localhost:8000 -> (empty)
        """
        # Remove port if present
        hostname = hostname.split(":")[0]
        
        # Split by dots
        parts = hostname.split(".")
        
        # If less than 2 parts, no subdomain
        if len(parts) < 2:
            return ""
        
        # If exactly 2 parts (e.g., kenikool.com), no subdomain
        if len(parts) == 2:
            return ""
        
        # Return first part as subdomain
        return parts[0]

    @staticmethod
    def _is_ip_address(hostname: str) -> bool:
        """Check if hostname is an IP address."""
        # Remove port if present
        host = hostname.split(":")[0]
        
        # Simple check for IPv4
        parts = host.split(".")
        if len(parts) == 4:
            try:
                for part in parts:
                    num = int(part)
                    if num < 0 or num > 255:
                        return False
                return True
            except ValueError:
                return False
        
        # Check for IPv6 (contains colons)
        if ":" in host:
            return True
        
        return False
