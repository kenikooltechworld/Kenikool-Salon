"""
API endpoints for location management.
Handles location CRUD operations, image uploads, and analytics.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from typing import Optional
from datetime import datetime
from bson import ObjectId

from app.api.dependencies import get_current_user, get_tenant_id, require_owner_or_admin

logger = logging.getLogger(__name__)
from app.database import Database
from app.services.location_service import LocationService
from app.schemas.location import (
    LocationCreate,
    LocationUpdate,
    LocationResponse,
    LocationListResponse,
    LocationStatus,
    LocationDependencies,
    LocationAnalytics,
)

router = APIRouter(prefix="/api/locations", tags=["locations"])


def get_db():
    """Get database instance"""
    return Database.get_db()


# ============================================================================
# Geocoding Endpoints
# ============================================================================


@router.post("/geocode", response_model=dict)
async def geocode_address(
    request: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Geocode an address to get latitude and longitude using Mapbox"""
    from app.services.mapbox_service import MapboxService, MapboxException
    from app.services.cache_service import CacheService

    try:
        address = request.get("address")
        country = request.get("country")
        
        if not address:
            raise ValueError("Address is required")

        cache_service = CacheService()
        service = MapboxService(cache_service=cache_service)
        result = await service.geocode_address(address, country=country)

        if not result:
            raise HTTPException(status_code=404, detail="Address not found")

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except MapboxException as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reverse-geocode", response_model=dict)
async def reverse_geocode(
    request: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Reverse geocode coordinates to get address using Mapbox"""
    from app.services.mapbox_service import MapboxService, MapboxException
    from app.services.cache_service import CacheService

    try:
        latitude = request.get("latitude")
        longitude = request.get("longitude")

        if latitude is None or longitude is None:
            raise ValueError("Latitude and longitude are required")

        cache_service = CacheService()
        service = MapboxService(cache_service=cache_service)
        address = await service.reverse_geocode(latitude, longitude)

        if not address:
            raise HTTPException(status_code=404, detail="Address not found for coordinates")

        return {
            "formatted_address": address,
            "latitude": latitude,
            "longitude": longitude,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except MapboxException as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search-addresses", response_model=dict)
async def search_addresses(
    query: str = Query(..., min_length=1),
    limit: int = Query(5, ge=1, le=50),
    country: Optional[str] = Query(None),
):
    """
    Search for address suggestions using Mapbox autocomplete (PUBLIC endpoint)
    
    This endpoint is public to allow customers to search for addresses
    on the marketplace page without authentication.
    
    Requirement 2.1: Real-time address suggestions as users type
    """
    from app.services.mapbox_service import MapboxService, MapboxException
    from app.services.cache_service import CacheService

    try:
        cache_service = CacheService()
        service = MapboxService(cache_service=cache_service)
        suggestions = await service.autocomplete_address(query, country=country, limit=limit)

        return {
            "query": query,
            "suggestions": suggestions,
            "count": len(suggestions),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except MapboxException as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/autocomplete", response_model=dict)
async def autocomplete_address(
    query: str = Query(..., min_length=1),
    limit: int = Query(5, ge=1, le=50),
    country: Optional[str] = Query(None),
    proximity: Optional[str] = Query(None, description="Bias results to location (lon,lat)"),
    bbox: Optional[str] = Query(None, description="Limit results to bounding box (min_lon,min_lat,max_lon,max_lat)"),
):
    """
    Autocomplete address suggestions (PUBLIC endpoint for marketplace)
    
    This endpoint is public to allow customers to search for addresses
    on the marketplace page without authentication.
    
    For African markets, use the country parameter with optional proximity bias
    to get better results. Mapbox Search Box API currently supports US, Canada, and Europe,
    but country filtering and proximity bias can help prioritize African results.
    
    Requirement 2.1: Real-time address suggestions as users type
    """
    from app.services.mapbox_service import MapboxService, MapboxException
    from app.services.cache_service import CacheService

    try:
        cache_service = CacheService()
        service = MapboxService(cache_service=cache_service)
        suggestions = await service.autocomplete_address(
            query, 
            country=country, 
            limit=limit,
            proximity=proximity,
            bbox=bbox,
        )

        return {
            "query": query,
            "suggestions": suggestions,
            "count": len(suggestions),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except MapboxException as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Location CRUD Endpoints
# ============================================================================


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_location(
    location_data: LocationCreate,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Create a new location"""
    db = get_db()
    service = LocationService(db)

    try:
        location = service.create_location(tenant_id=tenant_id, location_data=location_data)
        # Convert ObjectId to string for JSON serialization
        if location and "_id" in location:
            location["_id"] = str(location["_id"])
        return location
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=dict)
async def list_locations(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search by name, city, or address"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """List all locations for tenant with optional filtering"""
    db = get_db()
    service = LocationService(db)

    try:
        status_enum = LocationStatus(status) if status else None
        result = service.get_locations(
            tenant_id=tenant_id,
            status=status_enum,
            search=search,
            page=page,
            limit=limit,
        )
        # Convert ObjectIds to strings for JSON serialization
        locations = []
        for location in result.get("items", []):
            location["_id"] = str(location["_id"])
            locations.append(location)
        
        return {
            "locations": locations,
            "total": result.get("total", 0),
            "page": result.get("page", 1),
            "limit": result.get("limit", 20),
            "pages": result.get("pages", 0),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{location_id}", response_model=dict)
async def get_location(
    location_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get a single location by ID"""
    db = get_db()
    service = LocationService(db)

    try:
        location = service.get_location(location_id=location_id, tenant_id=tenant_id)
        # Convert ObjectId to string for JSON serialization
        if location and "_id" in location:
            location["_id"] = str(location["_id"])
        return location
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{location_id}", response_model=dict)
async def update_location(
    location_id: str,
    updates: LocationUpdate,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Update a location"""
    db = get_db()
    service = LocationService(db)

    try:
        location = service.update_location(
            location_id=location_id,
            tenant_id=tenant_id,
            updates=updates,
        )
        # Convert ObjectId to string for JSON serialization
        if location and "_id" in location:
            location["_id"] = str(location["_id"])
        return location
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(
    location_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Delete a location"""
    db = get_db()
    service = LocationService(db)

    try:
        service.delete_location(location_id=location_id, tenant_id=tenant_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Primary Location Endpoints
# ============================================================================


@router.post("/{location_id}/set-primary", response_model=dict)
async def set_primary_location(
    location_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Set a location as primary"""
    db = get_db()
    service = LocationService(db)

    try:
        location = await service.set_primary_location(tenant_id=tenant_id, location_id=location_id)
        # Convert ObjectId to string for JSON serialization
        if location and "_id" in location:
            location["_id"] = str(location["_id"])
        return location
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/primary/get", response_model=dict)
async def get_primary_location(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get the primary location for tenant"""
    db = get_db()
    service = LocationService(db)

    try:
        location = await service.get_primary_location(tenant_id=tenant_id)
        if not location:
            raise HTTPException(status_code=404, detail="No primary location found")
        # Convert ObjectId to string for JSON serialization
        if location and "_id" in location:
            location["_id"] = str(location["_id"])
        return location
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Dependency Check Endpoint
# ============================================================================


@router.get("/{location_id}/dependencies", response_model=dict)
async def check_location_dependencies(
    location_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Check if location has dependencies"""
    db = get_db()
    service = LocationService(db)

    try:
        dependencies = await service.check_dependencies(location_id=location_id)
        return dependencies
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Image Management Endpoints
# ============================================================================


@router.post("/{location_id}/images", response_model=dict)
async def upload_location_image(
    location_id: str,
    file: UploadFile = File(...),
    is_primary: bool = Query(False),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Upload an image to a location"""
    from app.services.location_image_service import LocationImageService, LocationImageException

    db = get_db()
    location_service = LocationService(db)
    image_service = LocationImageService()

    try:
        # Read file content
        contents = await file.read()

        # Validate and process image
        processed = await image_service.process_image(contents, file.content_type or "image/jpeg")

        # Generate image ID
        image_id = await image_service.generate_image_id()

        # Upload to Cloudinary
        from app.services.cloudinary_service import upload_image as cloudinary_upload
        
        folder = f"salon-locations/{tenant_id}/{location_id}"
        image_url = await cloudinary_upload(
            file_data=processed['content'],
            folder=folder,
            public_id=image_id
        )
        
        # Generate thumbnail URL (Cloudinary transformation)
        thumbnail_url = image_url.replace("/upload/", "/upload/w_400,h_300,c_fill/")

        # Add image to location
        location = await location_service.add_image(
            location_id=location_id,
            tenant_id=tenant_id,
            image_url=image_url,
            is_primary=is_primary,
        )

        logger.info(
            f"Uploaded image {image_id} to location {location_id}: "
            f"{processed['original_size']} -> {processed['processed_size']} bytes"
        )

        # Convert ObjectId to string for JSON serialization
        if location and "_id" in location:
            location["_id"] = str(location["_id"])
        return location
    except LocationImageException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Image upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{location_id}/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location_image(
    location_id: str,
    image_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Delete an image from a location"""
    db = get_db()
    service = LocationService(db)

    try:
        service.delete_image(location_id=location_id, tenant_id=tenant_id, image_id=image_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{location_id}/images/{image_id}/primary", response_model=dict)
async def set_primary_image(
    location_id: str,
    image_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Set an image as primary for a location"""
    db = get_db()
    service = LocationService(db)

    try:
        location = await service.set_primary_image(
            location_id=location_id,
            tenant_id=tenant_id,
            image_id=image_id,
        )
        # Convert ObjectId to string for JSON serialization
        if location and "_id" in location:
            location["_id"] = str(location["_id"])
        return location
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Status Management Endpoints
# ============================================================================


@router.put("/{location_id}/status", response_model=dict)
async def update_location_status(
    location_id: str,
    new_status: LocationStatus = Query(...),
    reopening_date: Optional[datetime] = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Update location status"""
    db = get_db()
    service = LocationService(db)

    try:
        location = await service.update_status(
            location_id=location_id,
            tenant_id=tenant_id,
            status=new_status,
            reopening_date=reopening_date,
        )
        # Convert ObjectId to string for JSON serialization
        if location and "_id" in location:
            location["_id"] = str(location["_id"])
        return location
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Analytics Endpoints
# ============================================================================


# ============================================================================
# Location-Specific Services, Staff, and Pricing Endpoints
# ============================================================================


@router.get("/{location_id}/services", response_model=list)
async def get_location_services(
    location_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get all services offered at a specific location"""
    db = get_db()
    
    try:
        # Verify location exists
        location = db.locations.find_one({
            "_id": ObjectId(location_id),
            "tenant_id": tenant_id
        })
        
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")
        
        # Get services offered at this location
        services = list(db.services.find({
            "tenant_id": tenant_id,
            "offered_locations": location_id,
            "is_active": True
        }))
        
        # Convert ObjectIds to strings
        for service in services:
            service["_id"] = str(service["_id"])
        
        return services
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting location services: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{location_id}/staff", response_model=list)
async def get_location_staff(
    location_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get all staff assigned to a specific location"""
    db = get_db()
    
    try:
        # Verify location exists
        location = db.locations.find_one({
            "_id": ObjectId(location_id),
            "tenant_id": tenant_id
        })
        
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")
        
        # Get staff assigned to this location
        staff = list(db.stylists.find({
            "tenant_id": tenant_id,
            "assigned_locations": location_id,
            "is_active": True
        }))
        
        # Convert ObjectIds to strings
        for stylist in staff:
            stylist["_id"] = str(stylist["_id"])
        
        return staff
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting location staff: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{location_id}/services/{service_id}/pricing", response_model=dict)
async def get_location_service_pricing(
    location_id: str,
    service_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get location-specific pricing for a service"""
    db = get_db()
    
    try:
        # Check for location-specific pricing
        location_pricing = db.location_service_pricing.find_one({
            "service_id": service_id,
            "location_id": location_id,
            "tenant_id": tenant_id
        })
        
        if location_pricing:
            return {
                "price": location_pricing.get("price", 0.0),
                "is_location_specific": True
            }
        
        # Fall back to default service pricing
        service = db.services.find_one({
            "_id": ObjectId(service_id),
            "tenant_id": tenant_id
        })
        
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        return {
            "price": service.get("price", 0.0),
            "is_location_specific": False
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting location service pricing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Analytics Endpoints
# ============================================================================


@router.get("/{location_id}/analytics", response_model=dict)
async def get_location_analytics(
    location_id: str,
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """
    Get analytics for a location
    
    Requirements: 7.1-7.7
    
    Query Parameters:
        - start_date: Start date for analytics (ISO format)
        - end_date: End date for analytics (ISO format)
    
    Returns:
        - location_id: Location ID
        - location_name: Location name
        - period: Date range
        - revenue: Total revenue and average per booking
        - bookings: Total, completed, and completion rate
        - occupancy: Occupancy rate and capacity
        - top_services: Top 5 performing services
        - staff_performance: Staff metrics
    """
    from app.services.location_analytics_service import LocationAnalyticsService
    
    try:
        analytics = LocationAnalyticsService.get_location_metrics(
            location_id=location_id,
            tenant_id=tenant_id,
            start_date=start_date,
            end_date=end_date,
        )
        return analytics
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting location analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
