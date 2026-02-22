"""
Boundary API Endpoints

Provides endpoints for managing Mapbox Boundaries 4.5 data for African markets,
geofencing, and service zones.

Requirements: 11.1, 11.2, 11.3, 11.4, 12.1, 12.2, 12.3, 12.4, 12.5, 14.1, 14.2, 14.4
"""

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.api.dependencies import get_current_user, get_db
from app.services.boundary_service import BoundaryService
from app.services.cache_service import CacheService
from app.services.location_service import LocationService
from app.services.geofencing_service import GeofencingService
from app.services.service_zone_service import ServiceZoneService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/boundaries", tags=["boundaries"])


# ============================================================================
# Request/Response Models
# ============================================================================


class CreateGeofenceRequest(BaseModel):
    customer_id: str
    salon_id: str
    latitude: float
    longitude: float
    radius_meters: Optional[int] = 500
    enabled: Optional[bool] = True


class UpdateGeofenceRequest(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_meters: Optional[int] = None
    enabled: Optional[bool] = None


class LogGeofenceEventRequest(BaseModel):
    customer_id: str
    salon_id: str
    geofence_id: str
    latitude: float
    longitude: float
    duration_seconds: Optional[int] = None


class CreateServiceZoneRequest(BaseModel):
    salon_id: str
    name: str
    type: str  # "service" or "restricted"
    coordinates: list  # GeoJSON polygon coordinates
    enabled: Optional[bool] = True


class UpdateServiceZoneRequest(BaseModel):
    name: Optional[str] = None
    coordinates: Optional[list] = None
    enabled: Optional[bool] = None


class ValidateServiceZoneRequest(BaseModel):
    salon_id: str
    latitude: float
    longitude: float


# ============================================================================
# Dependency Injection
# ============================================================================


def get_boundary_service(db=Depends(get_db)) -> BoundaryService:
    """Get BoundaryService instance"""
    cache_service = CacheService(db.redis)
    api_key = db.config.get("MAPBOX_SECRET_KEY")
    return BoundaryService(cache_service, api_key)


def get_location_service(db=Depends(get_db)) -> LocationService:
    """Get LocationService instance"""
    return LocationService(db)


def get_geofencing_service(db=Depends(get_db)) -> GeofencingService:
    """Get GeofencingService instance"""
    return GeofencingService(db)


def get_service_zone_service(db=Depends(get_db)) -> ServiceZoneService:
    """Get ServiceZoneService instance"""
    return ServiceZoneService(db)


# ============================================================================
# Boundary Endpoints
# ============================================================================


@router.get("/location")
async def get_administrative_divisions(
    latitude: float = Query(..., description="Location latitude"),
    longitude: float = Query(..., description="Location longitude"),
    country: Optional[str] = Query(None, description="Country code for validation"),
    use_cache: bool = Query(True, description="Use cached data if available"),
    boundary_service: BoundaryService = Depends(get_boundary_service),
) -> Dict[str, Any]:
    """
    Get administrative divisions for a location

    Args:
        latitude: Location latitude
        longitude: Location longitude
        country: Optional country code for validation
        use_cache: Whether to use cached data

    Returns:
        Administrative division data including region, postal code, etc.

    Raises:
        HTTPException: If boundary lookup fails
    """
    try:
        boundary_data = await boundary_service.get_administrative_divisions(
            latitude,
            longitude,
            country=country,
            use_cache=use_cache,
        )

        return {
            "latitude": latitude,
            "longitude": longitude,
            "boundary_data": boundary_data,
        }

    except Exception as e:
        logger.error(f"Failed to get administrative divisions: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get administrative divisions",
        )


@router.post("/validate-location/{location_id}")
async def validate_location_boundary(
    location_id: str,
    current_user=Depends(get_current_user),
    location_service: LocationService = Depends(get_location_service),
) -> Dict[str, Any]:
    """
    Validate a location against boundary data

    Args:
        location_id: Location ID to validate

    Returns:
        Validation result with boundary information

    Raises:
        HTTPException: If validation fails
    """
    try:
        tenant_id = current_user.get("tenant_id")
        
        result = await location_service.validate_location_boundary(
            location_id,
            tenant_id,
        )

        if not result.get("valid"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Validation failed"),
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to validate location boundary: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to validate location boundary",
        )


@router.post("/refresh-boundaries")
async def refresh_boundary_data(
    current_user=Depends(get_current_user),
    location_service: LocationService = Depends(get_location_service),
) -> Dict[str, Any]:
    """
    Refresh boundary data for all locations in a tenant

    Returns:
        Refresh statistics

    Raises:
        HTTPException: If refresh fails
    """
    try:
        tenant_id = current_user.get("tenant_id")
        
        stats = await location_service.refresh_boundary_data_for_locations(tenant_id)

        return {
            "message": "Boundary data refresh completed",
            "statistics": stats,
        }

    except Exception as e:
        logger.error(f"Failed to refresh boundary data: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to refresh boundary data",
        )


@router.get("/statistics")
async def get_boundary_statistics(
    boundary_service: BoundaryService = Depends(get_boundary_service),
) -> Dict[str, Any]:
    """
    Get statistics about boundary data coverage

    Returns:
        Statistics about boundary data
    """
    try:
        stats = await boundary_service.get_boundary_statistics()
        return stats

    except Exception as e:
        logger.error(f"Failed to get boundary statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get boundary statistics",
        )


@router.get("/postal-code")
async def extract_postal_code(
    latitude: float = Query(..., description="Location latitude"),
    longitude: float = Query(..., description="Location longitude"),
    boundary_service: BoundaryService = Depends(get_boundary_service),
) -> Dict[str, Any]:
    """
    Extract postal code for a location

    Args:
        latitude: Location latitude
        longitude: Location longitude

    Returns:
        Postal code if available

    Raises:
        HTTPException: If extraction fails
    """
    try:
        postal_code = await boundary_service.extract_postal_code(latitude, longitude)

        return {
            "latitude": latitude,
            "longitude": longitude,
            "postal_code": postal_code,
        }

    except Exception as e:
        logger.error(f"Failed to extract postal code: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to extract postal code",
        )


@router.get("/region")
async def extract_administrative_region(
    latitude: float = Query(..., description="Location latitude"),
    longitude: float = Query(..., description="Location longitude"),
    boundary_service: BoundaryService = Depends(get_boundary_service),
) -> Dict[str, Any]:
    """
    Extract administrative region for a location

    Args:
        latitude: Location latitude
        longitude: Location longitude

    Returns:
        Administrative region if available

    Raises:
        HTTPException: If extraction fails
    """
    try:
        region = await boundary_service.extract_administrative_region(latitude, longitude)

        return {
            "latitude": latitude,
            "longitude": longitude,
            "region": region,
        }

    except Exception as e:
        logger.error(f"Failed to extract administrative region: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to extract administrative region",
        )


@router.get("/locations-by-region")
async def get_locations_by_region(
    region: str = Query(..., description="Administrative region name"),
    current_user=Depends(get_current_user),
    location_service: LocationService = Depends(get_location_service),
) -> Dict[str, Any]:
    """
    Get all locations in a specific administrative region

    Args:
        region: Administrative region name

    Returns:
        List of locations in the region

    Raises:
        HTTPException: If query fails
    """
    try:
        tenant_id = current_user.get("tenant_id")
        
        locations = await location_service.get_locations_by_region(tenant_id, region)

        return {
            "region": region,
            "count": len(locations),
            "locations": locations,
        }

    except Exception as e:
        logger.error(f"Failed to get locations by region: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get locations by region",
        )


# ============================================================================
# Geofencing Endpoints
# ============================================================================


@router.post("/geofences")
async def create_geofence(
    request: CreateGeofenceRequest,
    geofencing_service: GeofencingService = Depends(get_geofencing_service),
) -> Dict[str, Any]:
    """
    Create a geofence for a customer around a salon
    
    Requirement 11.1: Define circular zones around salon locations
    """
    try:
        geofence_id = await geofencing_service.create_geofence(
            customer_id=request.customer_id,
            salon_id=request.salon_id,
            latitude=request.latitude,
            longitude=request.longitude,
            radius_meters=request.radius_meters or 500,
            enabled=request.enabled if request.enabled is not None else True,
        )

        return {
            "message": "Geofence created successfully",
            "geofence_id": geofence_id,
        }

    except Exception as e:
        logger.error(f"Failed to create geofence: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/geofences/{geofence_id}")
async def update_geofence(
    geofence_id: str,
    request: UpdateGeofenceRequest,
    geofencing_service: GeofencingService = Depends(get_geofencing_service),
) -> Dict[str, Any]:
    """
    Update a geofence
    
    Requirement 11.4: Update geofence boundaries when salon location changes
    """
    try:
        geofence = await geofencing_service.update_geofence(
            geofence_id=geofence_id,
            latitude=request.latitude,
            longitude=request.longitude,
            radius_meters=request.radius_meters,
            enabled=request.enabled,
        )

        return geofence

    except Exception as e:
        logger.error(f"Failed to update geofence: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/geofences/{geofence_id}")
async def delete_geofence(
    geofence_id: str,
    geofencing_service: GeofencingService = Depends(get_geofencing_service),
) -> Dict[str, Any]:
    """Delete a geofence"""
    try:
        await geofencing_service.delete_geofence(geofence_id)
        return {"message": "Geofence deleted successfully"}

    except Exception as e:
        logger.error(f"Failed to delete geofence: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/geofences/customer/{customer_id}")
async def get_customer_geofences(
    customer_id: str,
    geofencing_service: GeofencingService = Depends(get_geofencing_service),
) -> Dict[str, Any]:
    """Get all geofences for a customer"""
    try:
        geofences = await geofencing_service.get_customer_geofences(customer_id)
        return {"geofences": geofences}

    except Exception as e:
        logger.error(f"Failed to get customer geofences: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/geofences/salon/{salon_id}")
async def get_salon_geofences(
    salon_id: str,
    geofencing_service: GeofencingService = Depends(get_geofencing_service),
) -> Dict[str, Any]:
    """Get all geofences for a salon"""
    try:
        geofences = await geofencing_service.get_salon_geofences(salon_id)
        return {"geofences": geofences}

    except Exception as e:
        logger.error(f"Failed to get salon geofences: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/geofences/events/entry")
async def log_geofence_entry(
    request: LogGeofenceEventRequest,
    geofencing_service: GeofencingService = Depends(get_geofencing_service),
) -> Dict[str, Any]:
    """
    Log a geofence entry event
    
    Requirement 11.2: Trigger notifications on zone entry
    """
    try:
        event_id = await geofencing_service.log_geofence_entry(
            customer_id=request.customer_id,
            salon_id=request.salon_id,
            geofence_id=request.geofence_id,
            latitude=request.latitude,
            longitude=request.longitude,
        )

        return {
            "message": "Geofence entry logged",
            "event_id": event_id,
        }

    except Exception as e:
        logger.error(f"Failed to log geofence entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/geofences/events/exit")
async def log_geofence_exit(
    request: LogGeofenceEventRequest,
    geofencing_service: GeofencingService = Depends(get_geofencing_service),
) -> Dict[str, Any]:
    """
    Log a geofence exit event
    
    Requirement 11.3: Log exit events for analytics
    """
    try:
        event_id = await geofencing_service.log_geofence_exit(
            customer_id=request.customer_id,
            salon_id=request.salon_id,
            geofence_id=request.geofence_id,
            latitude=request.latitude,
            longitude=request.longitude,
            duration_seconds=request.duration_seconds,
        )

        return {
            "message": "Geofence exit logged",
            "event_id": event_id,
        }

    except Exception as e:
        logger.error(f"Failed to log geofence exit: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/geofences/events")
async def get_geofence_events(
    customer_id: Optional[str] = Query(None),
    salon_id: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0),
    geofencing_service: GeofencingService = Depends(get_geofencing_service),
) -> Dict[str, Any]:
    """Get geofence events with optional filtering"""
    try:
        result = await geofencing_service.get_geofence_events(
            customer_id=customer_id,
            salon_id=salon_id,
            event_type=event_type,
            limit=limit,
            skip=skip,
        )
        return result

    except Exception as e:
        logger.error(f"Failed to get geofence events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/geofences/analytics")
async def get_geofence_analytics(
    salon_id: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=365),
    geofencing_service: GeofencingService = Depends(get_geofencing_service),
) -> Dict[str, Any]:
    """Get geofence analytics"""
    try:
        analytics = await geofencing_service.get_geofence_analytics(
            salon_id=salon_id,
            days=days,
        )
        return analytics

    except Exception as e:
        logger.error(f"Failed to get geofence analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Service Zone Endpoints
# ============================================================================


@router.post("/service-zones")
async def create_service_zone(
    request: CreateServiceZoneRequest,
    service_zone_service: ServiceZoneService = Depends(get_service_zone_service),
) -> Dict[str, Any]:
    """
    Create a service zone for a salon
    
    Requirement 12.1: Allow salon owners to define custom service zones
    """
    try:
        zone = await service_zone_service.create_service_zone(
            salon_id=request.salon_id,
            name=request.name,
            zone_type=request.type,
            coordinates=request.coordinates,
            enabled=request.enabled if request.enabled is not None else True,
        )

        return zone

    except Exception as e:
        logger.error(f"Failed to create service zone: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/service-zones/{zone_id}")
async def update_service_zone(
    zone_id: str,
    request: UpdateServiceZoneRequest,
    service_zone_service: ServiceZoneService = Depends(get_service_zone_service),
) -> Dict[str, Any]:
    """Update a service zone"""
    try:
        zone = await service_zone_service.update_service_zone(
            zone_id=zone_id,
            name=request.name,
            coordinates=request.coordinates,
            enabled=request.enabled,
        )

        return zone

    except Exception as e:
        logger.error(f"Failed to update service zone: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/service-zones/{zone_id}")
async def delete_service_zone(
    zone_id: str,
    service_zone_service: ServiceZoneService = Depends(get_service_zone_service),
) -> Dict[str, Any]:
    """Delete a service zone"""
    try:
        await service_zone_service.delete_service_zone(zone_id)
        return {"message": "Service zone deleted successfully"}

    except Exception as e:
        logger.error(f"Failed to delete service zone: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/service-zones/salon/{salon_id}")
async def get_salon_service_zones(
    salon_id: str,
    service_zone_service: ServiceZoneService = Depends(get_service_zone_service),
) -> Dict[str, Any]:
    """Get all service zones for a salon"""
    try:
        zones = await service_zone_service.get_salon_service_zones(salon_id)
        return {"zones": zones}

    except Exception as e:
        logger.error(f"Failed to get salon service zones: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/service-zones/{zone_id}")
async def get_service_zone(
    zone_id: str,
    service_zone_service: ServiceZoneService = Depends(get_service_zone_service),
) -> Dict[str, Any]:
    """Get a single service zone"""
    try:
        zone = await service_zone_service.get_service_zone(zone_id)
        return zone

    except Exception as e:
        logger.error(f"Failed to get service zone: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/service-zones/validate")
async def validate_service_zone(
    request: ValidateServiceZoneRequest,
    service_zone_service: ServiceZoneService = Depends(get_service_zone_service),
) -> Dict[str, Any]:
    """
    Validate if a location is within service zones
    
    Requirement 12.2: Display message when service is unavailable in restricted zone
    """
    try:
        result = await service_zone_service.validate_location(
            salon_id=request.salon_id,
            latitude=request.latitude,
            longitude=request.longitude,
        )

        return result

    except Exception as e:
        logger.error(f"Failed to validate service zone: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/service-zones/salon/{salon_id}/stats")
async def get_service_zone_stats(
    salon_id: str,
    service_zone_service: ServiceZoneService = Depends(get_service_zone_service),
) -> Dict[str, Any]:
    """Get service zone statistics"""
    try:
        stats = await service_zone_service.get_service_zone_stats(salon_id)
        return stats

    except Exception as e:
        logger.error(f"Failed to get service zone stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
