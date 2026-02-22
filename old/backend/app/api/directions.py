"""
API endpoints for directions and navigation.
Provides route calculation and turn-by-turn instructions.

Requirements: 4.1, 4.2, 4.3, 4.4, 4.5
"""

import logging
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/directions", tags=["directions"])


class CoordinateModel(BaseModel):
    latitude: float
    longitude: float


class DirectionsRequest(BaseModel):
    from_latitude: float
    from_longitude: float
    to_latitude: float
    to_longitude: float
    profile: Optional[str] = "driving"  # driving, walking, cycling
    alternatives: Optional[bool] = True
    steps: Optional[bool] = True


class DirectionsRequestLegacy(BaseModel):
    from_coords: CoordinateModel
    to_coords: CoordinateModel
    profile: Optional[str] = "driving"  # driving, walking, cycling
    alternatives: Optional[bool] = True
    steps: Optional[bool] = True


class MatrixRequest(BaseModel):
    coordinates: list[CoordinateModel]
    profile: Optional[str] = "driving"


@router.post("", response_model=dict)
async def get_directions(request: DirectionsRequest):
    """
    Get directions between two points with multiple route options.
    
    Requirement 4.1, 4.2, 4.3: Use Mapbox Directions API with error handling
    
    Returns multiple routes (if available) with:
    - Distance and duration
    - Turn-by-turn instructions
    - Route geometry for map display
    
    Example:
    POST /api/directions
    {
        "from_latitude": 6.5244,
        "from_longitude": 3.3792,
        "to_latitude": 6.5300,
        "to_longitude": 3.3800,
        "profile": "driving"
    }
    """
    from app.services.directions_service import DirectionsService, DirectionsException

    try:
        service = DirectionsService()

        from_coords = (request.from_latitude, request.from_longitude)
        to_coords = (request.to_latitude, request.to_longitude)

        result = await service.get_directions(
            from_coords=from_coords,
            to_coords=to_coords,
            profile=request.profile or "driving",
            alternatives=request.alternatives if request.alternatives is not None else True,
            steps=request.steps if request.steps is not None else True,
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DirectionsException as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting directions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/route", response_model=dict)
async def get_route(request: DirectionsRequestLegacy):
    """
    Get directions between two points with multiple route options (legacy format).
    
    Returns multiple routes (if available) with:
    - Distance and duration
    - Turn-by-turn instructions
    - Route geometry for map display
    """
    from app.services.directions_service import DirectionsService, DirectionsException

    try:
        service = DirectionsService()

        from_coords = (request.from_coords.latitude, request.from_coords.longitude)
        to_coords = (request.to_coords.latitude, request.to_coords.longitude)

        result = await service.get_directions(
            from_coords=from_coords,
            to_coords=to_coords,
            profile=request.profile or "driving",
            alternatives=request.alternatives if request.alternatives is not None else True,
            steps=request.steps if request.steps is not None else True,
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DirectionsException as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting directions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/route", response_model=dict)
async def get_route_query(
    from_lat: float = Query(..., description="Starting latitude"),
    from_lon: float = Query(..., description="Starting longitude"),
    to_lat: float = Query(..., description="Destination latitude"),
    to_lon: float = Query(..., description="Destination longitude"),
    profile: str = Query("driving", description="driving, walking, or cycling"),
    alternatives: bool = Query(True, description="Return alternative routes"),
    steps: bool = Query(True, description="Include turn-by-turn instructions"),
):
    """
    Get directions using query parameters.
    
    Example:
    GET /api/directions/route?from_lat=6.5244&from_lon=3.3792&to_lat=6.5300&to_lon=3.3800&profile=driving
    """
    from app.services.directions_service import DirectionsService, DirectionsException

    try:
        service = DirectionsService()

        result = await service.get_directions(
            from_coords=(from_lat, from_lon),
            to_coords=(to_lat, to_lon),
            profile=profile,
            alternatives=alternatives,
            steps=steps,
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DirectionsException as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting directions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/matrix", response_model=dict)
async def get_distance_matrix(request: MatrixRequest):
    """
    Get distance matrix between multiple points.
    
    Useful for finding closest salons or calculating distances between many locations.
    
    Requirement 4.4: Calculate distances between locations
    """
    from app.services.directions_service import DirectionsService, DirectionsException

    try:
        if len(request.coordinates) < 2:
            raise ValueError("At least 2 coordinates required")

        if len(request.coordinates) > 25:
            raise ValueError("Maximum 25 coordinates allowed")

        service = DirectionsService()

        coordinates = [
            (coord.latitude, coord.longitude) for coord in request.coordinates
        ]

        result = await service.get_matrix(
            coordinates=coordinates,
            profile=request.profile or "driving",
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DirectionsException as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting distance matrix: {e}")
        raise HTTPException(status_code=500, detail=str(e))
