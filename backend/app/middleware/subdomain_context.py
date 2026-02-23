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
        # First try X-Forwarded-Host header (set by proxies), then fall back to Host header
        hostname = (
            request.headers.get("x-forwarded-host") or 
            request.headers.get("host", "")
        ).lower()
        
        logger.info(f"[SubdomainContext] Hostname: {hostname}")
        
        # Remove port if present for hostname checks
        hostname_without_port = hostname.split(":")[0]
        
        # Skip subdomain extraction for plain localhost and IP addresses
        if hostname_without_port == "localhost" or hostname_without_port.startswith("127.0.0.1"):
            # Allow localhost for development
            logger.info(f"[SubdomainContext] Localhost/IP detected, skipping subdomain extraction")
            return await call_next(request)

        # Check if it's an IP address (simple check)
        if self._is_ip_address(hostname_without_port):
            logger.info(f"[SubdomainContext] IP address detected, skipping subdomain extraction")
            return await call_next(request)

        # Extract subdomain from hostname
        subdomain = self._extract_subdomain(hostname_without_port)
        logger.info(f"[SubdomainContext] Extracted subdomain: {subdomain}")
        
        if not subdomain:
            # No subdomain found, allow request to proceed
            # (might be root domain or API gateway)
            logger.info(f"[SubdomainContext] No subdomain found, proceeding without tenant context")
            return await call_next(request)

        # Look up tenant by subdomain
        try:
            # Lazy-load Tenant model to avoid import-time database connection
            from app.models.tenant import Tenant
            
            # Skip tenant lookup if database is not available
            try:
                tenant = Tenant.objects(subdomain=subdomain, status="active").first()
                logger.info(f"[SubdomainContext] Tenant lookup for subdomain '{subdomain}': {tenant}")
            except Exception as db_error:
                logger.warning(f"[SubdomainContext] Database unavailable for tenant lookup: {db_error}")
                # Allow request to proceed without tenant context
                return await call_next(request)
            
            if not tenant:
                logger.warning(f"[SubdomainContext] Tenant not found for subdomain: {subdomain}")
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
            tenant_id_str = str(tenant.id)
            set_tenant_id(tenant_id_str)
            request.state.tenant_id = tenant_id_str
            request.state.tenant = tenant
            # Also set in scope for middleware that reads from scope
            request.scope["tenant_id"] = tenant_id_str

            logger.info(f"[SubdomainContext] ✓ Tenant context set for subdomain '{subdomain}' -> tenant_id: {tenant_id_str}")

        except Exception as e:
            logger.error(f"[SubdomainContext] Error looking up tenant for subdomain {subdomain}: {e}", exc_info=True)
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
        - localhost -> (empty)
        - kenzola-salon.localhost -> kenzola-salon
        """
        # hostname should already have port removed
        
        # Split by dots
        parts = hostname.split(".")
        
        # If less than 2 parts, no subdomain
        if len(parts) < 2:
            return ""
        
        # If exactly 2 parts
        if len(parts) == 2:
            # Check if it's localhost with subdomain (e.g., kenzola-salon.localhost)
            if parts[1] == "localhost":
                return parts[0]
            # Otherwise no subdomain (e.g., kenikool.com)
            return ""
        
        # If more than 2 parts, return first part as subdomain
        # (e.g., acme-salon.kenikool.com -> acme-salon)
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
