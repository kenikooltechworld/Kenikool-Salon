"""
Location Management API Endpoints

Provides REST API for multi-location salon management including:
- Location CRUD operations
- Primary location management
- Image upload/management
- Location analytics
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from typing import List, Optional
from datetime import datetime
import logging

from app.schemas.location import (
    LocationCreate,
    LocationUpdate,
    LocationResponse,
    LocationAnalytics,
    LocationDependencies
)
from app.services.salon_location_service import SalonLocationService
from app.api.dependencies import get_tenant_id, require_owner_or_admin
from app.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/locations", tags=["locations"])


def get_location_service(db=Depends(get_db)) -> SalonLocationService:
    """Get location service instance"""
    return SalonLocationService(db)


@router.post("", response_model=LocationResponse, status_code=201)
async def create_location(
    request: LocationCreate,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_owner_or_admin),
    service: SalonLocationService = Depends(get_location_service)
):
    """
    Create a new location
    
    **Requirements**: 1.1, 1.6
    """
    try:
        # Verify tenant_id matches
        if request.tenant_id != tenant_id:
            raise HTTPException(status_code=403, detail="Tenant mismatch")

        location = await service.create_location(tenant_id, request.dict())
        return location
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating location: {e}")
        raise HTTPException(status_code=500, detail="Failed to create location")


@router.get("", response_model=List[LocationResponse])
async def get_locations(
    status: Optional[str] = Query(None, description="Filter by status"),
    amenities: Optional[str] = Query(None, description="Filter by amenities (comma-separated)"),
    tenant_id: str = Depends(get_tenant_id),
    service: SalonLocationService = Depends(get_location_service)
):
    """
    Get all locations for a tenant
    
    **Requirements**: 1.2
    """
    try:
        filters = {}
        if status:
            filters['status'] = status
        if amenities:
            filters['amenities'] = amenities.split(',')

        locations = await service.get_locations(tenant_id, filters)
        return locations
    except Exception as e:
        logger.error(f"Error getting locations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get locations")


@router.get("/{location_id}", response_model=LocationResponse)
async def get_location(
    location_id: str,
    tenant_id: str = Depends(get_tenant_id),
    service: SalonLocationService = Depends(get_location_service)
):
    """
    Get a single location by ID
    
    **Requirements**: 1.3
    """
    try:
        location = await service.get_location(location_id, tenant_id)
        return location
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting location: {e}")
        raise HTTPException(status_code=500, detail="Failed to get location")


@router.put("/{location_id}", response_model=LocationResponse)
async def update_location(
    location_id: str,
    request: LocationUpdate,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_owner_or_admin),
    service: SalonLocationService = Depends(get_location_service)
):
    """
    Update a location
    
    **Requirements**: 1.4
    """
    try:
        location = await service.update_location(location_id, tenant_id, request.dict(exclude_unset=True))
        return location
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating location: {e}")
        raise HTTPException(status_code=500, detail="Failed to update location")


@router.delete("/{location_id}", status_code=204)
async def delete_location(
    location_id: str,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_owner_or_admin),
    service: SalonLocationService = Depends(get_location_service)
):
    """
    Delete a location
    
    **Requirements**: 1.5, 1.8
    """
    try:
        await service.delete_location(location_id, tenant_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting location: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete location")


@router.post("/{location_id}/primary", response_model=LocationResponse)
async def set_primary_location(
    location_id: str,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_owner_or_admin),
    service: SalonLocationService = Depends(get_location_service)
):
    """
    Set a location as the primary location
    
    **Requirements**: 1.7
    """
    try:
        location = await service.set_primary_location(tenant_id, location_id)
        return location
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error setting primary location: {e}")
        raise HTTPException(status_code=500, detail="Failed to set primary location")


@router.get("/{location_id}/dependencies", response_model=LocationDependencies)
async def check_location_dependencies(
    location_id: str,
    tenant_id: str = Depends(get_tenant_id),
    service: SalonLocationService = Depends(get_location_service)
):
    """
    Check dependencies for a location (staff, services, bookings)
    
    **Requirements**: 1.8
    """
    try:
        dependencies = await service.check_dependencies(location_id)
        return dependencies
    except Exception as e:
        logger.error(f"Error checking dependencies: {e}")
        raise HTTPException(status_code=500, detail="Failed to check dependencies")


@router.get("/{location_id}/analytics", response_model=LocationAnalytics)
async def get_location_analytics(
    location_id: str,
    start_date: datetime = Query(..., description="Start date for analytics period"),
    end_date: datetime = Query(..., description="End date for analytics period"),
    tenant_id: str = Depends(get_tenant_id),
    service: SalonLocationService = Depends(get_location_service)
):
    """
    Get analytics for a location
    
    **Requirements**: 7.1-7.7
    """
    try:
        analytics = await service.get_location_analytics(location_id, start_date, end_date)
        return analytics
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analytics")


@router.post("/{location_id}/images", response_model=LocationResponse)
async def upload_location_image(
    location_id: str,
    file: UploadFile = File(...),
    is_primary: bool = Query(False),
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_owner_or_admin),
    service: SalonLocationService = Depends(get_location_service)
):
    """
    Upload an image for a location
    
    **Requirements**: 8.1-8.8
    """
    try:
        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/webp']
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Invalid file type. Allowed: JPEG, PNG, WebP")

        # TODO: Upload file to storage service and get URL
        # For now, use placeholder
        image_url = f"https://storage.example.com/locations/{location_id}/{file.filename}"

        location = await service.upload_location_image(location_id, tenant_id, image_url, is_primary)
        return location
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading image: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload image")


@router.delete("/{location_id}/images/{image_id}", response_model=LocationResponse)
async def delete_location_image(
    location_id: str,
    image_id: str,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(require_owner_or_admin),
    service: SalonLocationService = Depends(get_location_service)
):
    """
    Delete an image from a location
    
    **Requirements**: 8.1-8.8
    """
    try:
        location = await service.delete_location_image(location_id, tenant_id, image_id)
        return location
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting image: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete image")
