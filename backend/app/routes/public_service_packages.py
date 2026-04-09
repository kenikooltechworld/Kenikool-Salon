from typing import Optional
from fastapi import APIRouter, Query, Depends

from app.middleware.public_booking import get_public_tenant_id
from app.schemas.service_package import (
    ServicePackageResponse,
    ServicePackageListResponse,
)
from app.services.service_package_service import ServicePackageService

router = APIRouter(prefix="/public/service-packages", tags=["Public Service Packages"])


@router.get(
    "",
    response_model=ServicePackageListResponse,
    summary="List available service packages (Public)"
)
async def list_public_service_packages(
    tenant_id: str = Depends(get_public_tenant_id),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_featured: Optional[bool] = Query(None)
):
    """
    List available service packages for public booking.
    
    Only returns:
    - Active packages
    - Valid packages (not expired)
    - Packages with available booking slots
    """
    skip = (page - 1) * page_size
    
    packages, total = await ServicePackageService.list_packages(
        tenant_id=tenant_id,
        skip=skip,
        limit=page_size,
        is_active=True,
        is_featured=is_featured,
        include_expired=False
    )
    
    # Filter out packages that have reached booking limit
    available_packages = [
        pkg for pkg in packages
        if pkg.is_valid()
    ]
    
    package_responses = [
        await ServicePackageService.format_package_response(pkg)
        for pkg in available_packages
    ]
    
    total_pages = (len(available_packages) + page_size - 1) // page_size
    
    return ServicePackageListResponse(
        packages=package_responses,
        total=len(available_packages),
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get(
    "/{package_id}",
    response_model=ServicePackageResponse,
    summary="Get service package details (Public)"
)
async def get_public_service_package(
    package_id: str,
    tenant_id: str = Depends(get_public_tenant_id)
):
    """
    Get detailed information about a specific service package.
    
    Includes:
    - All services in the package
    - Pricing and savings
    - Validity information
    - Total duration
    """
    package = await ServicePackageService.get_package(package_id, tenant_id)
    
    # Verify package is available for public booking
    if not package.is_active or not package.is_valid():
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service package not available"
        )
    
    return await ServicePackageService.format_package_response(package)
