"""Settings management routes."""

import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.services.tenant_settings_service import TenantSettingsService
from app.context import get_tenant_id
from app.schemas.tenant_settings import TenantSettingsSchema

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/settings", tags=["settings"])


# Financial Settings Schema
class FinancialConfigSchema(BaseModel):
    balance_enforcement_enabled: bool = True
    minimum_balance_threshold: float = 0
    refund_policy_enabled: bool = True
    refund_window_days: int = 30
    commission_tracking_enabled: bool = True
    staff_commission_percentage: float = 10
    service_commission_percentage: float = 5
    invoice_numbering_prefix: str = "INV"
    invoice_numbering_start: int = 1000


# Operational Settings Schema
class OperationalConfigSchema(BaseModel):
    inventory_tracking_enabled: bool = True
    low_stock_threshold: int = 10
    waiting_room_enabled: bool = True
    waiting_room_max_capacity: int = 50
    resource_management_enabled: bool = True
    notification_preferences_enabled: bool = True
    sms_provider: str = "termii"
    email_provider: str = "smtp"
    backup_enabled: bool = True
    backup_frequency: str = "daily"
    cache_optimization_enabled: bool = True
    cache_ttl_minutes: int = 60


@router.get("")
async def get_settings(tenant_id: str = Depends(get_tenant_id)):
    """Get tenant settings."""
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    
    settings = TenantSettingsService.get_settings(tenant_id)
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")
    
    return {"data": settings}


@router.put("")
async def update_settings(
    updates: TenantSettingsSchema,
    tenant_id: str = Depends(get_tenant_id),
):
    """Update tenant settings."""
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    
    settings = TenantSettingsService.update_settings(tenant_id, updates.model_dump())
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")

    logger.info(f"Settings updated for tenant: {tenant_id}")
    return {"data": settings}


@router.post("/reset")
async def reset_settings(tenant_id: str = Depends(get_tenant_id)):
    """Reset tenant settings to defaults."""
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    
    settings = TenantSettingsService.reset_settings(tenant_id)
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")

    logger.info(f"Settings reset for tenant: {tenant_id}")
    return {"data": settings}


# Financial Settings Endpoints
@router.get("/financial")
async def get_financial_settings(tenant_id: str = Depends(get_tenant_id)):
    """Get financial configuration settings."""
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    
    try:
        settings = TenantSettingsService.get_settings(tenant_id)
        if not settings:
            raise HTTPException(status_code=404, detail="Settings not found")
        
        financial_config = settings.get("financial_config")
        if not financial_config:
            raise HTTPException(status_code=404, detail="Financial configuration not found")
        
        return financial_config
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching financial settings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch financial settings")


@router.put("/financial")
async def update_financial_settings(
    config: FinancialConfigSchema,
    tenant_id: str = Depends(get_tenant_id),
):
    """Update financial configuration settings."""
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    
    try:
        settings = TenantSettingsService.get_settings(tenant_id)
        if not settings:
            raise HTTPException(status_code=404, detail="Settings not found")
        
        settings["financial_config"] = config.model_dump()
        updated = TenantSettingsService.update_settings(tenant_id, settings)
        if not updated:
            raise HTTPException(status_code=500, detail="Failed to update settings")
        
        logger.info(f"Financial settings updated for tenant: {tenant_id}")
        return updated.get("financial_config")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating financial settings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update financial settings")


# Operational Settings Endpoints
@router.get("/operational")
async def get_operational_settings(tenant_id: str = Depends(get_tenant_id)):
    """Get operational configuration settings."""
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    
    try:
        settings = TenantSettingsService.get_settings(tenant_id)
        if not settings:
            raise HTTPException(status_code=404, detail="Settings not found")
        
        operational_config = settings.get("operational_config")
        if not operational_config:
            raise HTTPException(status_code=404, detail="Operational configuration not found")
        
        return operational_config
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching operational settings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch operational settings")


@router.put("/operational")
async def update_operational_settings(
    config: OperationalConfigSchema,
    tenant_id: str = Depends(get_tenant_id),
):
    """Update operational configuration settings."""
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    
    try:
        settings = TenantSettingsService.get_settings(tenant_id)
        if not settings:
            raise HTTPException(status_code=404, detail="Settings not found")
        
        settings["operational_config"] = config.model_dump()
        updated = TenantSettingsService.update_settings(tenant_id, settings)
        if not updated:
            raise HTTPException(status_code=500, detail="Failed to update settings")
        
        logger.info(f"Operational settings updated for tenant: {tenant_id}")
        return updated.get("operational_config")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating operational settings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update operational settings")
