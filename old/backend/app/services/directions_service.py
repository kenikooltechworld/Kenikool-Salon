"""
Mapbox Directions API service for route calculation and navigation.
Provides multiple route options between two locations.
"""

import httpx
import logging
from typing import Optional, Dict, Any, List
from app.config import settings

logger = logging.getLogger(__name__)


class DirectionsException(Exception):
    """Exception raised for Directions API errors"""
    pass


class DirectionsService:
    """Service for Mapbox Directions API interactions"""

    def __init__(self):
        self.api_key = settings.MAPBOX_SECRET_KEY
        self.base_url = settings.MAPBOX_API_URL or "https://api.mapbox.com"
        self.timeout = settings.MAPBOX_TIMEOUT or 10.0

        if not self.api_key or not self.api_key.strip():
            raise DirectionsException("MAPBOX_SECRET_KEY environment variable is not set")

    async def get_directions(
        self,
        from_coords: tuple[float, float],
        to_coords: tuple[float, float],
        profile: str = "driving",
        alternatives: bool = True,
        steps: bool = True,
        geometries: str = "geojson",
        overview: str = "full",
    ) -> Dict[str, Any]:
        """
        Get directions between two points with multiple route options.

        Args:
            from_coords: Tuple of (latitude, longitude) for starting point
            to_coords: Tuple of (latitude, longitude) for destination
            profile: Routing profile - "driving", "walking", "cycling"
            alternatives: Return alternative routes (default True)
            steps: Include turn-by-turn instructions (default True)
            geometries: Format for route geometry - "geojson", "polyline", "polyline6"
            overview: Route overview level - "full", "simplified", "false"

        Returns:
            Dictionary with routes, waypoints, and metadata

        Raises:
            DirectionsException: If API request fails
        """
        if not isinstance(from_coords, (tuple, list)) or len(from_coords) != 2:
            raise ValueError("from_coords must be (latitude, longitude)")

        if not isinstance(to_coords, (tuple, list)) or len(to_coords) != 2:
            raise ValueError("to_coords must be (latitude, longitude)")

        # Validate coordinates
        lat1, lon1 = from_coords
        lat2, lon2 = to_coords

        if not (-90 <= lat1 <= 90 and -180 <= lon1 <= 180):
            raise ValueError("Invalid from_coords: latitude must be -90 to 90, longitude -180 to 180")

        if not (-90 <= lat2 <= 90 and -180 <= lon2 <= 180):
            raise ValueError("Invalid to_coords: latitude must be -90 to 90, longitude -180 to 180")

        if profile not in ["driving", "walking", "cycling"]:
            raise ValueError("profile must be 'driving', 'walking', or 'cycling'")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Mapbox Directions API uses longitude,latitude format
                coordinates = f"{lon1},{lat1};{lon2},{lat2}"

                params = {
                    "access_token": self.api_key,
                    "alternatives": "true" if alternatives else "false",
                    "steps": "true" if steps else "false",
                    "geometries": geometries,
                    "overview": overview,
                }

                url = f"{self.base_url}/directions/v5/mapbox/{profile}/{coordinates}"

                logger.info(
                    f"Calling Mapbox Directions API: {profile} route from "
                    f"({lat1}, {lon1}) to ({lat2}, {lon2})"
                )

                response = await client.get(url, params=params)
                response.raise_for_status()

                data = response.json()

                if data.get("code") != "Ok":
                    error_msg = data.get("message", "Unknown error")
                    logger.error(f"Mapbox Directions API error: {error_msg}")
                    raise DirectionsException(f"Directions API error: {error_msg}")

                # Process routes
                routes = data.get("routes", [])
                logger.info(f"Found {len(routes)} route(s)")

                return {
                    "routes": self._process_routes(routes),
                    "waypoints": data.get("waypoints", []),
                    "code": data.get("code"),
                }

        except httpx.TimeoutException:
            logger.error(f"Directions API timeout")
            raise DirectionsException("Directions request timed out")
        except httpx.HTTPStatusError as e:
            error_text = e.response.text if hasattr(e.response, 'text') else str(e)
            if e.response.status_code == 401:
                logger.error("Mapbox API key is invalid or expired")
                raise DirectionsException("Invalid Mapbox API key")
            elif e.response.status_code == 429:
                logger.error("Mapbox rate limit exceeded")
                raise DirectionsException("Rate limit exceeded")
            else:
                logger.error(f"Mapbox API error: {e.response.status_code} {error_text}")
                raise DirectionsException(f"Directions failed: {str(e)}")
        except httpx.HTTPError as e:
            logger.error(f"Mapbox HTTP error: {e}")
            raise DirectionsException(f"Directions failed: {str(e)}")

    def _process_routes(self, routes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and format routes for frontend consumption"""
        processed = []

        for idx, route in enumerate(routes):
            processed_route = {
                "id": f"route-{idx}",
                "distance_km": route.get("distance", 0) / 1000,
                "duration_minutes": route.get("duration", 0) / 60,
                "geometry": route.get("geometry"),
                "legs": route.get("legs", []),
                "is_primary": idx == 0,  # First route is primary
            }

            # Add turn-by-turn instructions if available
            if route.get("legs"):
                instructions = []
                for leg in route["legs"]:
                    for step in leg.get("steps", []):
                        if step.get("maneuver"):
                            instructions.append({
                                "instruction": step.get("maneuver", {}).get("instruction", ""),
                                "distance_km": step.get("distance", 0) / 1000,
                                "duration_minutes": step.get("duration", 0) / 60,
                                "name": step.get("name", ""),
                            })
                processed_route["instructions"] = instructions

            processed.append(processed_route)

        return processed

    async def get_matrix(
        self,
        coordinates: List[tuple[float, float]],
        profile: str = "driving",
    ) -> Dict[str, Any]:
        """
        Get distance matrix between multiple points.

        Args:
            coordinates: List of (latitude, longitude) tuples
            profile: Routing profile - "driving", "walking", "cycling"

        Returns:
            Dictionary with distances and durations matrix
        """
        if len(coordinates) < 2:
            raise ValueError("At least 2 coordinates required")

        if len(coordinates) > 25:
            raise ValueError("Maximum 25 coordinates allowed")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Convert to longitude,latitude format
                coords_str = ";".join([f"{lon},{lat}" for lat, lon in coordinates])

                params = {
                    "access_token": self.api_key,
                }

                url = f"{self.base_url}/directions-matrix/v1/mapbox/{profile}/{coords_str}"

                logger.info(f"Calling Mapbox Matrix API with {len(coordinates)} points")

                response = await client.get(url, params=params)
                response.raise_for_status()

                data = response.json()

                if data.get("code") != "Ok":
                    error_msg = data.get("message", "Unknown error")
                    logger.error(f"Mapbox Matrix API error: {error_msg}")
                    raise DirectionsException(f"Matrix API error: {error_msg}")

                return {
                    "distances": data.get("distances", []),  # in meters
                    "durations": data.get("durations", []),   # in seconds
                    "code": data.get("code"),
                }

        except httpx.TimeoutException:
            logger.error("Matrix API timeout")
            raise DirectionsException("Matrix request timed out")
        except httpx.HTTPStatusError as e:
            logger.error(f"Matrix API error: {e}")
            raise DirectionsException(f"Matrix failed: {str(e)}")
        except httpx.HTTPError as e:
            logger.error(f"Matrix HTTP error: {e}")
            raise DirectionsException(f"Matrix failed: {str(e)}")
