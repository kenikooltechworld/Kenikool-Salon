"""Settings management routes."""

import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.services.tenant_settings_service import TenantSettingsService
from app.context import get_tenant_id
from app.schemas.tenant_settings import TenantSettingsSchema

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/settings", tags=["settings"])


# System Settings Schema
class SystemConfigSchema(BaseModel):
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 60
    ddos_protection_enabled: bool = True
    ddos_threshold: int = 1000
    waf_enabled: bool = True
    intrusion_detection_enabled: bool = True
    audit_logging_enabled: bool = True
    feature_flags: dict = {}


# Integration Settings Schema
class IntegrationConfigSchema(BaseModel):
    termii_enabled: bool = False
    termii_api_key: str = ""
    paystack_enabled: bool = False
    paystack_public_key: str = ""
    paystack_webhook_url: str = ""
    payment_retry_enabled: bool = True
    payment_retry_attempts: int = 3
    payment_retry_delay: int = 300


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
    settings = TenantSettingsService.update_settings(tenant_id, updates.model_dump())
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")

    logger.info(f"Settings updated for tenant: {tenant_id}")
    return {"data": settings}


@router.post("/reset")
async def reset_settings(tenant_id: str = Depends(get_tenant_id)):
    """Reset tenant settings to defaults."""
    settings = TenantSettingsService.reset_settings(tenant_id)
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")

    logger.info(f"Settings reset for tenant: {tenant_id}")
    return {"data": settings}


# System Settings Endpoints
@router.get("/system")
async def get_system_settings(tenant_id: str = Depends(get_tenant_id)):
    """Get system configuration settings."""
    try:
        settings = TenantSettingsService.get_settings(tenant_id)
        if not settings:
            raise HTTPException(status_code=404, detail="Settings not found")
        
        system_config = settings.get("system_config", {})
        return {"data": system_config}
    except Exception as e:
        logger.error(f"Error fetching system settings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch system settings")


@router.put("/system")
async def update_system_settings(
    config: SystemConfigSchema,
    tenant_id: str = Depends(get_tenant_id),
):
    """Update system configuration settings."""
    try:
        settings = TenantSettingsService.get_settings(tenant_id)
        if not settings:
            raise HTTPException(status_code=404, detail="Settings not found")
        
        settings["system_config"] = config.model_dump()
        updated = TenantSettingsService.update_settings(tenant_id, settings)
        logger.info(f"System settings updated for tenant: {tenant_id}")
        return {"data": updated.get("system_config", {})}
    except Exception as e:
        logger.error(f"Error updating system settings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update system settings")


# Integration Settings Endpoints
@router.get("/integrations")
async def get_integration_settings(tenant_id: str = Depends(get_tenant_id)):
    """Get integration configuration settings."""
    try:
        settings = TenantSettingsService.get_settings(tenant_id)
        if not settings:
            raise HTTPException(status_code=404, detail="Settings not found")
        
        integration_config = settings.get("integration_config", {})
        return {"data": integration_config}
    except Exception as e:
        logger.error(f"Error fetching integration settings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch integration settings")


@router.put("/integrations")
async def update_integration_settings(
    config: IntegrationConfigSchema,
    tenant_id: str = Depends(get_tenant_id),
):
    """Update integration configuration settings."""
    try:
        settings = TenantSettingsService.get_settings(tenant_id)
        if not settings:
            raise HTTPException(status_code=404, detail="Settings not found")
        
        settings["integration_config"] = config.model_dump()
        updated = TenantSettingsService.update_settings(tenant_id, settings)
        logger.info(f"Integration settings updated for tenant: {tenant_id}")
        return {"data": updated.get("integration_config", {})}
    except Exception as e:
        logger.error(f"Error updating integration settings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update integration settings")


# Financial Settings Endpoints
@router.get("/financial")
async def get_financial_settings(tenant_id: str = Depends(get_tenant_id)):
    """Get financial configuration settings."""
    try:
        settings = TenantSettingsService.get_settings(tenant_id)
        if not settings:
            raise HTTPException(status_code=404, detail="Settings not found")
        
        financial_config = settings.get("financial_config", {})
        return {"data": financial_config}
    except Exception as e:
        logger.error(f"Error fetching financial settings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch financial settings")


@router.put("/financial")
async def update_financial_settings(
    config: FinancialConfigSchema,
    tenant_id: str = Depends(get_tenant_id),
):
    """Update financial configuration settings."""
    try:
        settings = TenantSettingsService.get_settings(tenant_id)
        if not settings:
            raise HTTPException(status_code=404, detail="Settings not found")
        
        settings["financial_config"] = config.model_dump()
        updated = TenantSettingsService.update_settings(tenant_id, settings)
        logger.info(f"Financial settings updated for tenant: {tenant_id}")
        return {"data": updated.get("financial_config", {})}
    except Exception as e:
        logger.error(f"Error updating financial settings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update financial settings")


# Operational Settings Endpoints
@router.get("/operational")
async def get_operational_settings(tenant_id: str = Depends(get_tenant_id)):
    """Get operational configuration settings."""
    try:
        settings = TenantSettingsService.get_settings(tenant_id)
        if not settings:
            raise HTTPException(status_code=404, detail="Settings not found")
        
        operational_config = settings.get("operational_config", {})
        return {"data": operational_config}
    except Exception as e:
        logger.error(f"Error fetching operational settings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch operational settings")


@router.put("/operational")
async def update_operational_settings(
    config: OperationalConfigSchema,
    tenant_id: str = Depends(get_tenant_id),
):
    """Update operational configuration settings."""
    try:
        settings = TenantSettingsService.get_settings(tenant_id)
        if not settings:
            raise HTTPException(status_code=404, detail="Settings not found")
        
        settings["operational_config"] = config.model_dump()
        updated = TenantSettingsService.update_settings(tenant_id, settings)
        logger.info(f"Operational settings updated for tenant: {tenant_id}")
        return {"data": updated.get("operational_config", {})}
    except Exception as e:
        logger.error(f"Error updating operational settings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update operational settings")
