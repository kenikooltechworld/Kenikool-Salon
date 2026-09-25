"""Location management routes."""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from bson import ObjectId
from app.models.location import Location
from app.schemas.location import (
    LocationCreateRequest,
    LocationUpdateRequest,
    LocationResponse,
    LocationListResponse,
)
from app.context import get_tenant_id
from app.decorators.tenant_isolated import tenant_isolated

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/locations", tags=["locations"])


def get_tenant_id_from_context() -> ObjectId:
    """Get tenant_id from context."""
    tenant_id = get_tenant_id()
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    return tenant_id


def location_to_response(location: Location) -> LocationResponse:
    """Convert Location model to response schema."""
    return LocationResponse(
        id=str(location.id),
        name=location.name,
        address=location.address,
        phone=location.phone,
        email=location.email,
        is_active=location.is_active,
        timezone=location.timezone,
        created_at=location.created_at.isoformat() if location.created_at else None,
        updated_at=location.updated_at.isoformat() if location.updated_at else None,
    )


@router.post("", response_model=LocationResponse)
@tenant_isolated
async def create_location(
    request: LocationCreateRequest,
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """Create a new location."""
    try:
        location = Location(
            tenant_id=tenant_id,
            name=request.name,
            address=request.address,
            phone=request.phone,
            email=request.email,
            is_active=request.is_active,
            timezone=request.timezone,
        )
        location.save()
        logger.info(f"Location created: {location.id} for tenant {tenant_id}")
        return location_to_response(location)
    except Exception as e:
        logger.error(f"Failed to create location: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to create location")


@router.get("/{location_id}", response_model=LocationResponse)
@tenant_isolated
async def get_location(
    location_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """Get a specific location."""
    try:
        location = Location.objects(id=ObjectId(location_id), tenant_id=tenant_id).first()
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")
        return location_to_response(location)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get location: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to get location")


@router.get("", response_model=LocationListResponse)
@tenant_isolated
async def list_locations(
    is_active: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """List locations for the tenant."""
    try:
        query = Location.objects(tenant_id=tenant_id)

        if is_active is not None:
            query = query(is_active=is_active)

        total = query.count()
        skip = (page - 1) * page_size
        locations = query.skip(skip).limit(page_size).order_by("-created_at")

        return LocationListResponse(
            locations=[location_to_response(loc) for loc in locations],
            total=total,
            page=page,
            page_size=page_size,
        )
    except Exception as e:
        logger.error(f"Failed to list locations: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to list locations")


@router.put("/{location_id}", response_model=LocationResponse)
@tenant_isolated
async def update_location(
    location_id: str,
    request: LocationUpdateRequest,
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """Update a location."""
    try:
        location = Location.objects(id=ObjectId(location_id), tenant_id=tenant_id).first()
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")

        update_data = request.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(location, key, value)

        location.save()
        logger.info(f"Location updated: {location_id} for tenant {tenant_id}")
        return location_to_response(location)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update location: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to update location")


@router.delete("/{location_id}")
@tenant_isolated
async def delete_location(
    location_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """Soft delete a location by marking it inactive."""
    try:
        location = Location.objects(id=ObjectId(location_id), tenant_id=tenant_id).first()
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")

        location.is_active = False
        location.save()
        logger.info(f"Location deactivated: {location_id}")
        return {"message": "Location deactivated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete location: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to delete location")
