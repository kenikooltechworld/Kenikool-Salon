"""
Weather API Endpoints

Provides endpoints for fetching weather data for map visualization.

Requirements: 13.2
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_current_user, get_db
from app.services.cache_service import CacheService
from app.services.weather_service import WeatherService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/weather", tags=["weather"])


def get_weather_service(db=Depends(get_db)) -> WeatherService:
    """Get WeatherService instance"""
    cache_service = CacheService(db.redis)
    api_key = db.config.get("OPENWEATHER_API_KEY")
    return WeatherService(cache_service, api_key)


@router.get("/location")
async def get_weather_for_location(
    latitude: float = Query(..., description="Location latitude"),
    longitude: float = Query(..., description="Location longitude"),
    use_cache: bool = Query(True, description="Use cached data if available"),
    weather_service: WeatherService = Depends(get_weather_service),
) -> Dict[str, Any]:
    """
    Get weather data for a specific location

    Args:
        latitude: Location latitude
        longitude: Location longitude
        use_cache: Whether to use cached data

    Returns:
        Weather data with condition, temperature, humidity, wind speed

    Raises:
        HTTPException: If weather fetch fails
    """
    try:
        weather_data = await weather_service.get_weather(
            latitude,
            longitude,
            use_cache=use_cache,
        )

        return {
            "latitude": latitude,
            "longitude": longitude,
            "weather": weather_data,
        }

    except Exception as e:
        logger.error(f"Failed to fetch weather: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch weather data",
        )


@router.post("/locations")
async def get_weather_for_locations(
    locations: List[Dict[str, float]],
    weather_service: WeatherService = Depends(get_weather_service),
) -> Dict[str, Any]:
    """
    Get weather data for multiple locations

    Args:
        locations: List of location dicts with 'latitude' and 'longitude'

    Returns:
        Dict mapping location coordinates to weather data

    Raises:
        HTTPException: If weather fetch fails
    """
    try:
        # Validate locations
        if not locations:
            raise ValueError("At least one location is required")

        if len(locations) > 50:
            raise ValueError("Maximum 50 locations allowed per request")

        for loc in locations:
            if "latitude" not in loc or "longitude" not in loc:
                raise ValueError("Each location must have latitude and longitude")

        # Fetch weather for all locations
        weather_data = await weather_service.get_weather_for_locations(locations)

        return {
            "count": len(locations),
            "weather": weather_data,
        }

    except ValueError as e:
        logger.error(f"Invalid request: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Failed to fetch weather for locations: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch weather data",
        )


@router.post("/update-cache")
async def update_weather_cache(
    latitude: float = Query(..., description="Location latitude"),
    longitude: float = Query(..., description="Location longitude"),
    weather_data: Dict[str, Any] = None,
    current_user=Depends(get_current_user),
    weather_service: WeatherService = Depends(get_weather_service),
) -> Dict[str, str]:
    """
    Manually update weather cache for a location

    Args:
        latitude: Location latitude
        longitude: Location longitude
        weather_data: Weather data to cache

    Returns:
        Success message

    Raises:
        HTTPException: If update fails
    """
    try:
        if weather_data is None:
            weather_data = await weather_service.get_weather(latitude, longitude)

        await weather_service.update_weather_cache(latitude, longitude, weather_data)

        return {
            "message": "Weather cache updated successfully",
            "latitude": str(latitude),
            "longitude": str(longitude),
        }

    except Exception as e:
        logger.error(f"Failed to update weather cache: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update weather cache",
        )


@router.delete("/cache")
async def clear_weather_cache(
    latitude: Optional[float] = Query(None, description="Location latitude"),
    longitude: Optional[float] = Query(None, description="Location longitude"),
    current_user=Depends(get_current_user),
    weather_service: WeatherService = Depends(get_weather_service),
) -> Dict[str, str]:
    """
    Clear weather cache

    Args:
        latitude: Optional latitude to clear specific location
        longitude: Optional longitude to clear specific location

    Returns:
        Success message

    Raises:
        HTTPException: If clear fails
    """
    try:
        await weather_service.clear_weather_cache(latitude, longitude)

        if latitude is not None and longitude is not None:
            message = f"Weather cache cleared for {latitude}, {longitude}"
        else:
            message = "All weather cache cleared"

        return {"message": message}

    except Exception as e:
        logger.error(f"Failed to clear weather cache: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to clear weather cache",
        )
