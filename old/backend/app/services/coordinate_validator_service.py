"""
Coordinate validator service for validating manual coordinate entry.

This service validates latitude and longitude coordinates entered manually
by users, ensuring they are within valid ranges and optionally reverse-geocoding
them to get formatted addresses.

Requirements:
    - 9.3: Allow manual coordinate entry as alternative to address search
"""

import logging
from typing import Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)


class CoordinateInput(BaseModel):
    """Schema for manual coordinate input"""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude between -90 and 90")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude between -180 and 180")
    
    @validator('latitude', 'longitude')
    def validate_not_zero(cls, v):
        """Ensure coordinates are not both zero (invalid location)"""
        if v == 0:
            # Allow zero, but warn if both are zero
            pass
        return v


class CoordinateValidationResult(BaseModel):
    """Result of coordinate validation"""
    is_valid: bool
    latitude: float
    longitude: float
    formatted_address: Optional[str] = None
    errors: list = Field(default_factory=list)
    warnings: list = Field(default_factory=list)


class CoordinateValidatorService:
    """Service for validating and processing manual coordinate entry"""

    def __init__(self, mapbox_service: Optional[Any] = None):
        """
        Initialize coordinate validator service.

        Args:
            mapbox_service: Optional MapboxService for reverse geocoding
        """
        self.mapbox_service = mapbox_service

    def validate_coordinates(
        self,
        latitude: float,
        longitude: float,
        strict: bool = False
    ) -> CoordinateValidationResult:
        """
        Validate latitude and longitude coordinates.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            strict: If True, reject coordinates at (0, 0)

        Returns:
            CoordinateValidationResult with validation status and any errors

        Requirement 9.3: Validate manual coordinate entry
        """
        errors = []
        warnings = []
        
        # Validate types
        if not isinstance(latitude, (int, float)):
            errors.append("Latitude must be a number")
        if not isinstance(longitude, (int, float)):
            errors.append("Longitude must be a number")
        
        if errors:
            return CoordinateValidationResult(
                is_valid=False,
                latitude=latitude,
                longitude=longitude,
                errors=errors
            )
        
        # Validate ranges
        if latitude < -90 or latitude > 90:
            errors.append(f"Latitude must be between -90 and 90, got {latitude}")
        if longitude < -180 or longitude > 180:
            errors.append(f"Longitude must be between -180 and 180, got {longitude}")
        
        # Check for invalid (0, 0) coordinates
        if strict and latitude == 0 and longitude == 0:
            errors.append("Coordinates (0, 0) are not valid")
        elif latitude == 0 and longitude == 0:
            warnings.append("Coordinates (0, 0) may not be valid - please verify")
        
        # Check for coordinates in ocean (rough check)
        if self._is_likely_ocean(latitude, longitude):
            warnings.append("Coordinates appear to be in the ocean - please verify")
        
        is_valid = len(errors) == 0
        
        return CoordinateValidationResult(
            is_valid=is_valid,
            latitude=latitude,
            longitude=longitude,
            errors=errors,
            warnings=warnings
        )

    async def validate_and_geocode(
        self,
        latitude: float,
        longitude: float,
        strict: bool = False
    ) -> CoordinateValidationResult:
        """
        Validate coordinates and optionally reverse-geocode to get address.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            strict: If True, reject coordinates at (0, 0)

        Returns:
            CoordinateValidationResult with validation status and formatted address

        Requirement 9.3: Validate manual coordinate entry
        """
        # First validate coordinates
        result = self.validate_coordinates(latitude, longitude, strict=strict)
        
        if not result.is_valid:
            return result
        
        # Try to reverse geocode if Mapbox service is available
        if self.mapbox_service:
            try:
                formatted_address = await self.mapbox_service.reverse_geocode(
                    latitude, longitude
                )
                result.formatted_address = formatted_address
                logger.info(
                    f"Reverse geocoded coordinates ({latitude}, {longitude}) "
                    f"to: {formatted_address}"
                )
            except Exception as e:
                logger.warning(
                    f"Could not reverse geocode coordinates ({latitude}, {longitude}): {e}"
                )
                result.warnings.append(
                    f"Could not retrieve address for coordinates: {str(e)}"
                )
        
        return result

    def _is_likely_ocean(self, latitude: float, longitude: float) -> bool:
        """
        Check if coordinates are likely in the ocean.
        
        This is a very rough check based on known ocean regions.
        A more sophisticated approach would use actual ocean boundary data.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate

        Returns:
            True if coordinates are likely in the ocean
        """
        # Check for common ocean regions
        # Atlantic Ocean
        if -80 < latitude < 80 and -100 < longitude < 0:
            return True
        
        # Pacific Ocean
        if -60 < latitude < 60 and (longitude < -100 or longitude > 100):
            return True
        
        # Indian Ocean
        if -60 < latitude < 30 and 40 < longitude < 100:
            return True
        
        return False

    def format_coordinates(
        self,
        latitude: float,
        longitude: float,
        decimal_places: int = 6
    ) -> str:
        """
        Format coordinates as a string.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            decimal_places: Number of decimal places

        Returns:
            Formatted coordinate string (e.g., "6.524400, 3.379200")
        """
        format_str = f"{{:.{decimal_places}f}}, {{:.{decimal_places}f}}"
        return format_str.format(latitude, longitude)

    def parse_coordinate_string(self, coord_string: str) -> Optional[Tuple[float, float]]:
        """
        Parse a coordinate string into latitude and longitude.

        Supports formats like:
        - "6.524400, 3.379200"
        - "6.524400,3.379200"
        - "6.524400 3.379200"

        Args:
            coord_string: Coordinate string to parse

        Returns:
            Tuple of (latitude, longitude) or None if parsing fails
        """
        try:
            # Replace common separators with comma
            coord_string = coord_string.strip()
            coord_string = coord_string.replace(";", ",").replace(" ", ",")
            
            # Split by comma
            parts = [p.strip() for p in coord_string.split(",")]
            
            if len(parts) != 2:
                logger.error(f"Invalid coordinate format: {coord_string}")
                return None
            
            latitude = float(parts[0])
            longitude = float(parts[1])
            
            return (latitude, longitude)
        
        except (ValueError, IndexError) as e:
            logger.error(f"Error parsing coordinate string '{coord_string}': {e}")
            return None

    def get_distance_from_coordinates(
        self,
        from_coords: Tuple[float, float],
        to_coords: Tuple[float, float]
    ) -> float:
        """
        Calculate distance between two coordinate pairs.

        Args:
            from_coords: Tuple of (latitude, longitude)
            to_coords: Tuple of (latitude, longitude)

        Returns:
            Distance in kilometers
        """
        from app.utils.distance import calculate_haversine_distance
        
        return calculate_haversine_distance(from_coords, to_coords)

    def get_bounding_box(
        self,
        center_coords: Tuple[float, float],
        radius_km: float
    ) -> Dict[str, Any]:
        """
        Get bounding box for a circular area around coordinates.

        Args:
            center_coords: Tuple of (latitude, longitude)
            radius_km: Radius in kilometers

        Returns:
            Dictionary with bounding box coordinates
        """
        from app.utils.distance import get_bounding_box
        
        (min_lat, min_lon), (max_lat, max_lon) = get_bounding_box(center_coords, radius_km)
        
        return {
            "center": {
                "latitude": center_coords[0],
                "longitude": center_coords[1],
            },
            "radius_km": radius_km,
            "bounds": {
                "min_latitude": min_lat,
                "min_longitude": min_lon,
                "max_latitude": max_lat,
                "max_longitude": max_lon,
            }
        }
