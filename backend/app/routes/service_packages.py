from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

from app.routes.auth import get_current_user_dependency
from app.schemas.service_package import (
    ServicePackageCreate,
    ServicePackageUpdate,
    ServicePackageResponse,
    ServicePackageListResponse,
)
from app.services.service_package_service import ServicePackageService

router = APIRouter(prefix="/service-packages", tags=["Service Packages"])


@router.post(
    "",
    response_model=ServicePackageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create service package"
)
async def create_service_package(
    package_data: ServicePackageCreate,
    current_user: dict = Depends(get_current_user_dependency)
):
    """
    Create a new service package.
    
    Requires:
    - At least 2 services
    - Package price lower than original price
    - All services must belong to the tenant
    """
    tenant_id = current_user.get("tenant_id")
    package = await ServicePackageService.create_package(
        tenant_id=tenant_id,
        package_data=package_data,
        user_id=current_user["id"]
    )
    
    return await ServicePackageService.format_package_response(package)


@router.get(
    "",
    response_model=ServicePackageListResponse,
    summary="List service packages"
)
async def list_service_packages(
    current_user: dict = Depends(get_current_user_dependency),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = Query(None),
    is_featured: Optional[bool] = Query(None),
    include_expired: bool = Query(False)
):
    """
    List service packages with pagination and filters.
    
    Filters:
    - is_active: Filter by active status
    - is_featured: Filter by featured status
    - include_expired: Include expired packages
    """
    tenant_id = current_user.get("tenant_id")
    skip = (page - 1) * page_size
    
    packages, total = await ServicePackageService.list_packages(
        tenant_id=tenant_id,
        skip=skip,
        limit=page_size,
        is_active=is_active,
        is_featured=is_featured,
        include_expired=include_expired
    )
    
    package_responses = [
        await ServicePackageService.format_package_response(pkg)
        for pkg in packages
    ]
    
    total_pages = (total + page_size - 1) // page_size
    
    return ServicePackageListResponse(
        packages=package_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get(
    "/{package_id}",
    response_model=ServicePackageResponse,
    summary="Get service package"
)
async def get_service_package(
    package_id: str,
    current_user: dict = Depends(get_current_user_dependency)
):
    """
    Get a specific service package by ID.
    """
    tenant_id = current_user.get("tenant_id")
    package = await ServicePackageService.get_package(package_id, tenant_id)
    return await ServicePackageService.format_package_response(package)


@router.put(
    "/{package_id}",
    response_model=ServicePackageResponse,
    summary="Update service package"
)
async def update_service_package(
    package_id: str,
    package_data: ServicePackageUpdate,
    current_user: dict = Depends(get_current_user_dependency)
):
    """
    Update a service package.
    
    Can update:
    - Package details (name, description)
    - Services included
    - Pricing
    - Validity dates
    - Availability settings
    """
    tenant_id = current_user.get("tenant_id")
    package = await ServicePackageService.update_package(
        package_id=package_id,
        tenant_id=tenant_id,
        package_data=package_data,
        user_id=current_user["id"]
    )
    
    return await ServicePackageService.format_package_response(package)


@router.delete(
    "/{package_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete service package"
)
async def delete_service_package(
    package_id: str,
    current_user: dict = Depends(get_current_user_dependency)
):
    """
    Delete a service package.
    
    This will also delete all associated service items.
    """
    tenant_id = current_user.get("tenant_id")
    await ServicePackageService.delete_package(package_id, tenant_id)
    return JSONResponse(
        status_code=status.HTTP_204_NO_CONTENT,
        content={"message": "Service package deleted successfully"}
    )


@router.post(
    "/{package_id}/toggle-active",
    response_model=ServicePackageResponse,
    summary="Toggle package active status"
)
async def toggle_package_active(
    package_id: str,
    current_user: dict = Depends(get_current_user_dependency)
):
    """
    Toggle the active status of a service package.
    """
    tenant_id = current_user.get("tenant_id")
    package = await ServicePackageService.get_package(package_id, tenant_id)
    
    update_data = ServicePackageUpdate(is_active=not package.is_active)
    
    package = await ServicePackageService.update_package(
        package_id=package_id,
        tenant_id=tenant_id,
        package_data=update_data,
        user_id=current_user["id"]
    )
    
    return await ServicePackageService.format_package_response(package)


@router.post(
    "/{package_id}/toggle-featured",
    response_model=ServicePackageResponse,
    summary="Toggle package featured status"
)
async def toggle_package_featured(
    package_id: str,
    current_user: dict = Depends(get_current_user_dependency)
):
    """
    Toggle the featured status of a service package.
    """
    tenant_id = current_user.get("tenant_id")
    package = await ServicePackageService.get_package(package_id, tenant_id)
    
    update_data = ServicePackageUpdate(is_featured=not package.is_featured)
    
    package = await ServicePackageService.update_package(
        package_id=package_id,
        tenant_id=tenant_id,
        package_data=update_data,
        user_id=current_user["id"]
    )
    
    return await ServicePackageService.format_package_response(package)
