"""
Domain routing middleware - Routes requests based on custom domain.

This middleware checks if the incoming request is for a custom domain,
looks up the tenant associated with that domain, and injects the tenant_id
into the request state for use by downstream handlers.

Features:
- Caches domain-to-tenant mappings in Redis for performance
- Supports both www and non-www variants
- Handles multiple custom domains per tenant
- Returns 404 for unknown domains
- Redirects inactive configurations to default domain
"""
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import redis
from app.database import Database
from app.config import settings

logger = logging.getLogger(__name__)

# Platform's main domain
PLATFORM_DOMAIN = "salonapp.com"

# Redis cache for domain-to-tenant mappings (1 hour TTL)
DOMAIN_CACHE_TTL = 3600


class DomainRoutingMiddleware(BaseHTTPMiddleware):
    """Middleware to route requests based on custom domain"""

    def __init__(self, app):
        super().__init__(app)
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True
            )
            self.redis_client.ping()
            self.redis_available = True
            logger.info("✅ Redis connected for domain routing cache")
        except Exception as e:
            logger.warning(f"⚠️  Redis not available for domain routing: {e}")
            self.redis_available = False
            self.redis_client = None

    async def dispatch(self, request: Request, call_next):
        """Process request and route based on domain"""
        try:
            host = request.headers.get("host", "").split(":")[0].lower()

            # Check if it's a custom domain (not the platform domain)
            if not host.endswith(PLATFORM_DOMAIN) and host != "localhost":
                # Try to get tenant from cache first
                tenant_id = None
                if self.redis_available:
                    try:
                        cached_tenant = self.redis_client.get(f"domain:{host}")
                        if cached_tenant:
                            tenant_id = cached_tenant
                            logger.debug(f"Domain from cache: {host} -> {tenant_id}")
                    except Exception as e:
                        logger.warning(f"Redis cache error: {e}")

                # If not in cache, look up in database
                if not tenant_id:
                    db = Database.get_db()
                    
                    # Check both www and non-www variants
                    domain_variants = [host]
                    if host.startswith("www."):
                        domain_variants.append(host[4:])
                    else:
                        domain_variants.append(f"www.{host}")
                    
                    domain_doc = db.domains.find_one({
                        "domain": {"$in": domain_variants},
                        "status": "verified"
                    })

                    if domain_doc:
                        tenant_id = str(domain_doc["tenant_id"])
                        
                        # Cache the mapping
                        if self.redis_available:
                            try:
                                self.redis_client.setex(
                                    f"domain:{host}",
                                    DOMAIN_CACHE_TTL,
                                    tenant_id
                                )
                            except Exception as e:
                                logger.warning(f"Failed to cache domain mapping: {e}")
                        
                        logger.debug(f"Custom domain routed: {host} -> tenant {tenant_id}")
                    else:
                        # Unknown custom domain - return 404
                        logger.warning(f"Unknown custom domain: {host}")
                        return JSONResponse(
                            status_code=404,
                            content={"detail": "Domain not found"}
                        )

                # Inject tenant_id and domain info into request state
                request.state.tenant_id = tenant_id
                request.state.is_custom_domain = True
                request.state.custom_domain = host
            else:
                # Platform domain or localhost
                request.state.is_custom_domain = False

            response = await call_next(request)
            return response

        except Exception as e:
            logger.error(f"Domain routing middleware error: {e}", exc_info=True)
            # Continue processing even if middleware fails
            response = await call_next(request)
            return response


def get_tenant_id_from_request(request: Request) -> str:
    """
    Extract tenant_id from request state.

    This function is used by API endpoints to get the tenant_id
    that was injected by the domain routing middleware or from
    the Authorization header.

    Args:
        request: Starlette Request object

    Returns:
        str: Tenant ID, or None if not found
    """
    # First check if injected by domain routing middleware
    if hasattr(request.state, "tenant_id"):
        return request.state.tenant_id

    # Otherwise, try to extract from Authorization header or other sources
    # This would typically be done by an auth middleware
    return None
