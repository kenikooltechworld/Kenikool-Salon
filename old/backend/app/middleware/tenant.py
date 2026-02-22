"""
Multi-tenant middleware for automatic tenant filtering
"""
from fastapi import Request, HTTPException, status
from typing import Optional
from app.database import Database
import logging
import re

logger = logging.getLogger(__name__)


def get_tenant_from_subdomain(request: Request) -> Optional[dict]:
    """
    Extract tenant from subdomain in request
    Supports both subdomain.domain.com and custom domains
    """
    host = request.headers.get("host", "")
    
    # Remove port if present
    host = host.split(":")[0]
    
    # Check if it's a custom domain first
    db = Database.get_db()
    tenant = db.tenants.find_one({"custom_domain": host})
    if tenant is not None:
        tenant["id"] = str(tenant["_id"])
        logger.debug(f"Tenant found by custom domain: {host}")
        return tenant
    
    # Extract subdomain
    # Assuming format: subdomain.yourdomain.com
    parts = host.split(".")
    
    # If localhost or IP, check for subdomain in query params or headers
    if host.startswith("localhost") or re.match(r"^\d+\.\d+\.\d+\.\d+$", host):
        # Check X-Tenant-Subdomain header
        subdomain = request.headers.get("X-Tenant-Subdomain")
        if subdomain:
            tenant = db.tenants.find_one({"subdomain": subdomain})
            if tenant is not None:
                tenant["id"] = str(tenant["_id"])
                logger.debug(f"Tenant found by header: {subdomain}")
                return tenant
        return None
    
    # Extract subdomain from host
    if len(parts) >= 3:
        subdomain = parts[0]
        tenant = db.tenants.find_one({"subdomain": subdomain})
        if tenant is not None:
            tenant["id"] = str(tenant["_id"])
            logger.debug(f"Tenant found by subdomain: {subdomain}")
            return tenant
    
    return None


def get_tenant_from_request(request: Request) -> dict:
    """
    Get tenant from request or raise exception
    FastAPI dependency for routes that require tenant context
    """
    tenant = get_tenant_from_subdomain(request)
    
    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found. Please check your subdomain or custom domain."
        )
    
    if not tenant.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This salon account is inactive. Please contact support."
        )
    
    return tenant


def get_tenant_id_from_context(info) -> Optional[str]:
    """
    Extract tenant_id from GraphQL context
    Used in resolvers to filter data by tenant
    """
    context = info.context
    tenant = context.get("tenant")
    if tenant:
        return tenant.get("id") or str(tenant.get("_id"))
    return None


def validate_subdomain_unique(subdomain: str, exclude_tenant_id: Optional[str] = None) -> bool:
    """
    Check if subdomain is unique
    """
    db = Database.get_db()
    
    query = {"subdomain": subdomain}
    if exclude_tenant_id:
        from bson import ObjectId
        query["_id"] = {"$ne": ObjectId(exclude_tenant_id)}
    
    existing = db.tenants.find_one(query)
    return existing is None
