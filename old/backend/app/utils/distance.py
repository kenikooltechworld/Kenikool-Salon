"""
Distance calculation utilities using Haversine formula.
Provides functions for calculating distances between geographic coordinates.
"""

import logging
from typing import Tuple
from math import radians, cos, sin, asin, sqrt

logger = logging.getLogger(__name__)


def calculate_haversine_distance(
    from_coords: Tuple[float, float],
    to_coords: Tuple[float, float]
) -> float:
    """
    Calculate distance between two points using Haversine formula.
    
    This is a simple client-side calculation that doesn't require API calls.
    Accurate for distances up to several thousand kilometers.
    
    Args:
        from_coords: Tuple of (latitude, longitude) for starting point
        to_coords: Tuple of (latitude, longitude) for ending point
    
    Returns:
        Distance in kilometers
    
    Raises:
        ValueError: If coordinates are invalid
    
    Requirement 4.1: Distance calculation using Haversine formula
    """
    lat1, lon1 = from_coords
    lat2, lon2 = to_coords

    # Validate coordinates
    if not all(isinstance(c, (int, float)) for c in [lat1, lon1, lat2, lon2]):
        raise ValueError("Coordinates must be numbers")

    if lat1 < -90 or lat1 > 90 or lat2 < -90 or lat2 > 90:
        raise ValueError("Latitude must be between -90 and 90")

    if lon1 < -180 or lon1 > 180 or lon2 < -180 or lon2 > 180:
        raise ValueError("Longitude must be between -180 and 180")

    # Haversine formula
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    distance_km = c * r

    logger.debug(
        f"Calculated Haversine distance from ({lat1}, {lon1}) to ({lat2}, {lon2}): {distance_km:.2f} km"
    )
    return distance_km


def format_distance(distance_km: float, decimal_places: int = 1) -> str:
    """
    Format distance for display with specified decimal places.
    
    Args:
        distance_km: Distance in kilometers
        decimal_places: Number of decimal places (default 1)
    
    Returns:
        Formatted distance string (e.g., "2.5 km")
    
    Raises:
        ValueError: If distance is not a number
    
    Requirement 4.2: Distance formatting with one decimal place
    Requirement 9.5: Use kilometers for African markets
    """
    if not isinstance(distance_km, (int, float)):
        raise ValueError("Distance must be a number")
    
    if distance_km < 0:
        raise ValueError("Distance cannot be negative")
    
    format_str = f"{{:.{decimal_places}f}} km"
    return format_str.format(distance_km)


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """
    Validate that coordinates are within valid ranges.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
    
    Returns:
        True if coordinates are valid, False otherwise
    """
    if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
        return False
    
    if latitude < -90 or latitude > 90:
        return False
    
    if longitude < -180 or longitude > 180:
        return False
    
    return True


def get_bounding_box(
    center_coords: Tuple[float, float],
    radius_km: float
) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """
    Get bounding box coordinates for a circular area.
    
    Useful for filtering locations within a radius.
    
    Args:
        center_coords: Tuple of (latitude, longitude) for center point
        radius_km: Radius in kilometers
    
    Returns:
        Tuple of ((min_lat, min_lon), (max_lat, max_lon))
    
    Raises:
        ValueError: If coordinates or radius are invalid
    """
    lat, lon = center_coords
    
    if not validate_coordinates(lat, lon):
        raise ValueError("Invalid center coordinates")
    
    if radius_km <= 0:
        raise ValueError("Radius must be positive")
    
    # Approximate conversion: 1 degree ≈ 111 km
    lat_delta = radius_km / 111.0
    lon_delta = radius_km / (111.0 * cos(radians(lat)))
    
    min_lat = max(-90, lat - lat_delta)
    max_lat = min(90, lat + lat_delta)
    min_lon = max(-180, lon - lon_delta)
    max_lon = min(180, lon + lon_delta)
    
    return ((min_lat, min_lon), (max_lat, max_lon))
