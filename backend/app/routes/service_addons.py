"""Service Add-on Routes"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from typing import List
from bson import ObjectId

from app.schemas.service_addon import (
    ServiceAddonCreate,
    ServiceAddonUpdate,
    ServiceAddonResponse
)
from app.services.service_addon_service import ServiceAddonService
from app.middleware.tenant_context import get_tenant_id
from app.routes.auth import get_current_user_dependency

# Public routes for customers
public_router = APIRouter(prefix="/public/service-addons", tags=["Public Service Addons"])

@public_router.get("/{service_id}", response_model=List[ServiceAddonResponse])
async def get_service_addons(
    request: Request,
    service_id: str
):
    """Get all active addons for a specific service (public endpoint)"""
    tenant_id = get_tenant_id(request)
    
    try:
        service_oid = ObjectId(service_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid service ID"
        )
    
    addons = ServiceAddonService.get_addons_for_service(
        tenant_id=tenant_id,
        service_id=service_oid
    )
    
    return [ServiceAddonResponse(**addon.to_dict()) for addon in addons]


# Admin routes for managing addons
admin_router = APIRouter(prefix="/service-addons", tags=["Service Addons Management"])

@admin_router.get("/", response_model=List[ServiceAddonResponse])
async def list_addons(
    is_active: bool = None,
    current_user: dict = Depends(get_current_user_dependency)
):
    """List all service addons (admin only)"""
    tenant_id = current_user.get("tenant_id")
    
    addons = ServiceAddonService.get_all_addons(
        tenant_id=tenant_id,
        is_active=is_active
    )
    
    return [ServiceAddonResponse(**addon.to_dict()) for addon in addons]


@admin_router.get("/{addon_id}", response_model=ServiceAddonResponse)
async def get_addon(
    addon_id: str,
    current_user: dict = Depends(get_current_user_dependency)
):
    """Get specific addon by ID (admin only)"""
    tenant_id = current_user.get("tenant_id")
    
    try:
        addon_oid = ObjectId(addon_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid addon ID"
        )
    
    addon = ServiceAddonService.get_addon_by_id(tenant_id, addon_oid)
    
    if not addon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Addon not found"
        )
    
    return ServiceAddonResponse(**addon.to_dict())


@admin_router.post("/", response_model=ServiceAddonResponse, status_code=status.HTTP_201_CREATED)
async def create_addon(
    addon_data: ServiceAddonCreate,
    current_user: dict = Depends(get_current_user_dependency)
):
    """Create a new service addon (admin only)"""
    tenant_id = current_user.get("tenant_id")
    
    addon = ServiceAddonService.create_addon(
        tenant_id=tenant_id,
        addon_data=addon_data
    )
    
    return ServiceAddonResponse(**addon.to_dict())


@admin_router.put("/{addon_id}", response_model=ServiceAddonResponse)
async def update_addon(
    addon_id: str,
    addon_data: ServiceAddonUpdate,
    current_user: dict = Depends(get_current_user_dependency)
):
    """Update service addon (admin only)"""
    try:
        addon_oid = ObjectId(addon_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid addon ID"
        )
    
    addon = ServiceAddonService.update_addon(addon_oid, addon_data)
    
    if not addon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Addon not found"
        )
    
    return ServiceAddonResponse(**addon.to_dict())


@admin_router.delete("/{addon_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_addon(
    addon_id: str,
    current_user: dict = Depends(get_current_user_dependency)
):
    """Delete service addon (soft delete) (admin only)"""
    try:
        addon_oid = ObjectId(addon_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid addon ID"
        )
    
    success = ServiceAddonService.delete_addon(addon_oid)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Addon not found"
        )
    
    return None
