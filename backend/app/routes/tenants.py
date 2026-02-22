"""Tenant management routes."""

import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from app.services.tenant_service import TenantProvisioningService
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tenants", tags=["tenants"])


class TenantProvisioningRequest(BaseModel):
    """Tenant provisioning request schema."""

    name: str
    email: EmailStr
    phone: str
    subscription_tier: str = "starter"
    region: str = "us-east-1"


class TenantProvisioningResponse(BaseModel):
    """Tenant provisioning response schema."""

    tenant_id: str
    admin_user_id: str
    admin_email: str
    admin_password: str
    api_key: str
    subscription_tier: str
    status: str
    created_at: str


def get_tenant_service() -> TenantProvisioningService:
    """Get tenant provisioning service."""
    return TenantProvisioningService(settings)


@router.post("", response_model=TenantProvisioningResponse)
async def provision_tenant(
    request: TenantProvisioningRequest,
    service: TenantProvisioningService = Depends(get_tenant_service),
):
    """
    Provision a new tenant.

    Creates a new tenant with admin user, roles, and permissions.
    """
    result = service.provision_tenant(
        name=request.name,
        email=request.email,
        phone=request.phone,
        subscription_tier=request.subscription_tier,
        region=request.region,
    )

    if not result:
        logger.error(f"Failed to provision tenant: {request.name}")
        raise HTTPException(status_code=400, detail="Failed to provision tenant")

    logger.info(f"Tenant provisioned: {request.name}")

    return TenantProvisioningResponse(**result)


@router.get("/{tenant_id}")
async def get_tenant(
    tenant_id: str,
    service: TenantProvisioningService = Depends(get_tenant_service),
):
    """
    Get tenant information.

    Returns the tenant's profile and settings.
    """
    tenant = service.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    return {
        "data": {
            "id": str(tenant.id),
            "name": tenant.name,
            "address": tenant.address,
            "subscription_tier": tenant.subscription_tier,
            "status": tenant.status,
            "region": tenant.region,
            "settings": tenant.settings or {},
            "created_at": tenant.created_at.isoformat(),
            "updated_at": tenant.updated_at.isoformat(),
        }
    }


@router.put("/{tenant_id}")
async def update_tenant(
    tenant_id: str,
    updates: dict,
    service: TenantProvisioningService = Depends(get_tenant_service),
):
    """
    Update tenant settings.

    Updates the tenant's configuration.
    """
    tenant = service.update_tenant(tenant_id, **updates)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    logger.info(f"Tenant updated: {tenant_id}")

    return {
        "data": {
            "id": str(tenant.id),
            "name": tenant.name,
            "address": tenant.address,
            "subscription_tier": tenant.subscription_tier,
            "status": tenant.status,
            "region": tenant.region,
            "settings": tenant.settings or {},
            "updated_at": tenant.updated_at.isoformat(),
        }
    }


@router.post("/{tenant_id}/suspend")
async def suspend_tenant(
    tenant_id: str,
    service: TenantProvisioningService = Depends(get_tenant_service),
):
    """
    Suspend a tenant.

    Prevents the tenant from accessing the platform.
    """
    success = service.suspend_tenant(tenant_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tenant not found")

    logger.info(f"Tenant suspended: {tenant_id}")

    return {"message": "Tenant suspended successfully"}


@router.post("/{tenant_id}/delete")
async def delete_tenant(
    tenant_id: str,
    service: TenantProvisioningService = Depends(get_tenant_service),
):
    """
    Delete a tenant (soft delete).

    Marks the tenant as deleted without removing data.
    """
    success = service.delete_tenant(tenant_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tenant not found")

    logger.info(f"Tenant deleted: {tenant_id}")

    return {"message": "Tenant deleted successfully"}
