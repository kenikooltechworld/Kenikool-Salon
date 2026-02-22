"""
Mapbox geocoding and location services.
Provides address geocoding, reverse geocoding, autocomplete, and distance calculations.
"""

import httpx
import logging
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
from app.config import settings

logger = logging.getLogger(__name__)


class MapboxException(Exception):
    """Exception raised for Mapbox API errors"""
    pass


class MapboxService:
    """Service for Mapbox API interactions"""

    def __init__(self, cache_service: Optional[Any] = None):
        """
        Initialize Mapbox service with API key validation.
        
        Args:
            cache_service: Optional CacheService instance for caching results
        """
        self.api_key = settings.MAPBOX_SECRET_KEY
        self.public_key = settings.MAPBOX_PUBLIC_KEY
        self.base_url = settings.MAPBOX_API_URL or "https://api.mapbox.com"
        self.timeout = settings.MAPBOX_TIMEOUT or 10.0
        self.cache = cache_service
        
        # Validate API keys are present
        if not self.api_key or not self.api_key.strip():
            raise MapboxException("MAPBOX_SECRET_KEY environment variable is not set")
        if not self.public_key or not self.public_key.strip():
            raise MapboxException("MAPBOX_PUBLIC_KEY environment variable is not set")
        
        logger.info("MapboxService initialized successfully")

    async def geocode_address(
        self,
        address: str,
        country: Optional[str] = None,
        limit: int = 1
    ) -> Optional[Dict[str, Any]]:
        """
        Convert address to latitude and longitude using Mapbox Geocoding API.

        Args:
            address: Address string to geocode
            country: Optional country code (e.g., 'NG' for Nigeria) for African market optimization
            limit: Maximum number of results to return (default 1)

        Returns:
            Dictionary with latitude, longitude, formatted_address, and confidence, or None if not found

        Raises:
            MapboxException: If API request fails

        Requirement 1.1: Geocode address to coordinates
        Requirement 1.5: Country-specific geocoding for African markets
        Requirement 6.5: Retry logic with exponential backoff
        """
        if not address or not address.strip():
            raise ValueError("Address cannot be empty")

        if len(address.strip()) < 3:
            raise ValueError("Address must be at least 3 characters")

        # Check cache first
        if self.cache:
            cached_result = await self.cache.get_geocoding(address)
            if cached_result:
                return cached_result

        from app.utils.retry import retry_with_backoff

        async def _geocode():
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # URL encode the address
                encoded_address = httpx.URL(address).raw[0]
                
                params = {
                    "access_token": self.api_key,
                    "limit": min(limit, 5),  # Mapbox limit is 5
                }
                
                # Add country parameter for African market optimization
                if country:
                    params["country"] = country

                url = f"{self.base_url}/geocoding/v5/mapbox.places/{encoded_address}.json"
                
                response = await client.get(url, params=params)
                response.raise_for_status()

                data = response.json()

                if not data.get("features"):
                    logger.warning(f"No geocoding results for address: {address}")
                    return None

                # Get the top result
                feature = data["features"][0]
                
                # Extract coordinates (Mapbox returns [longitude, latitude])
                coords = feature.get("geometry", {}).get("coordinates", [])
                if len(coords) < 2:
                    raise MapboxException("Invalid coordinates in Mapbox response")

                result = {
                    "latitude": float(coords[1]),
                    "longitude": float(coords[0]),
                    "formatted_address": feature.get("place_name", address),
                    "confidence": self._calculate_confidence(feature),
                    "place_id": feature.get("id"),
                    "place_type": feature.get("place_type", []),
                    "source": "mapbox",
                }

                # Cache the result
                if self.cache:
                    await self.cache.set_geocoding(address, result)

                logger.info(
                    f"Geocoded address: {address} -> "
                    f"({result['latitude']}, {result['longitude']}) "
                    f"confidence: {result['confidence']}"
                )
                return result

        try:
            return await retry_with_backoff(
                _geocode,
                max_attempts=3,
                initial_delay=1.0,
                backoff_factor=2.0
            )
        except Exception as e:
            logger.error(f"Geocoding failed after retries for address {address}: {e}")
            raise MapboxException(f"Geocoding failed: {str(e)}")

    async def reverse_geocode(
        self,
        latitude: float,
        longitude: float
    ) -> Optional[str]:
        """
        Convert latitude and longitude to address using Mapbox Reverse Geocoding API.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate

        Returns:
            Formatted address string, or None if not found

        Raises:
            MapboxException: If API request fails
        """
        if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
            raise ValueError("Latitude and longitude must be numbers")

        if latitude < -90 or latitude > 90:
            raise ValueError("Latitude must be between -90 and 90")

        if longitude < -180 or longitude > 180:
            raise ValueError("Longitude must be between -180 and 180")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {
                    "access_token": self.api_key,
                }

                # Mapbox reverse geocoding uses {longitude},{latitude} format
                url = f"{self.base_url}/geocoding/v5/mapbox.places/{longitude},{latitude}.json"
                
                response = await client.get(url, params=params)
                response.raise_for_status()

                data = response.json()

                if not data.get("features"):
                    logger.warning(f"No reverse geocoding results for coordinates: {latitude}, {longitude}")
                    return None

                # Get the top result
                feature = data["features"][0]
                address = feature.get("place_name")

                if address:
                    logger.info(f"Reverse geocoded ({latitude}, {longitude}) -> {address}")
                    return address

                return None

        except httpx.TimeoutException:
            logger.error(f"Mapbox request timeout for coordinates: {latitude}, {longitude}")
            raise MapboxException("Reverse geocoding request timed out")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                logger.error("Mapbox API key is invalid or expired")
                raise MapboxException("Invalid Mapbox API key")
            elif e.response.status_code == 429:
                logger.error("Mapbox rate limit exceeded")
                raise MapboxException("Rate limit exceeded")
            else:
                logger.error(f"Mapbox API error for coordinates {latitude}, {longitude}: {e}")
                raise MapboxException(f"Reverse geocoding failed: {str(e)}")
        except httpx.HTTPError as e:
            logger.error(f"Mapbox HTTP error for coordinates {latitude}, {longitude}: {e}")
            raise MapboxException(f"Reverse geocoding failed: {str(e)}")
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing Mapbox response for coordinates {latitude}, {longitude}: {e}")
            raise MapboxException("Invalid reverse geocoding response")

    async def autocomplete_address(
        self,
        query: str,
        country: Optional[str] = None,
        limit: int = 5,
        proximity: Optional[str] = None,
        bbox: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get address autocomplete suggestions using Mapbox Search Box API (latest).

        The Search Box API is the recommended way to add interactive location search.
        It supports addresses, places, POIs, categories, streets, neighborhoods, etc.

        Args:
            query: Search query string (max 256 characters)
            country: Optional country code for filtering results (ISO 3166 alpha 2)
            limit: Maximum number of results to return (1-10, default 5)
            proximity: Optional coordinates to bias results (format: "longitude,latitude")
                      Helps prioritize results near a specific location
            bbox: Optional bounding box to limit results (format: "min_lon,min_lat,max_lon,max_lat")
                  Restricts results to a geographic area

        Returns:
            List of address suggestions with coordinates and metadata

        Raises:
            MapboxException: If API request fails

        API Reference: https://docs.mapbox.com/api/search/search-box/
        
        Note: Mapbox Search Box API currently supports United States, Canada, and Europe.
        For African markets, use country parameter with proximity bias for best results.
        """
        if not query or not query.strip():
            raise ValueError("Search query cannot be empty")

        if len(query.strip()) < 2:
            raise ValueError("Search query must be at least 2 characters")

        if len(query.strip()) > 256:
            raise ValueError("Search query cannot exceed 256 characters")

        if limit < 1 or limit > 10:
            limit = 5

        # Check cache first
        if self.cache:
            cached_results = await self.cache.get_autocomplete(query, country)
            if cached_results:
                logger.info(f"Returning cached autocomplete results for query: {query}")
                return cached_results

        try:
            import uuid
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Use Mapbox Search Box API /suggest endpoint for autocomplete
                # session_token is REQUIRED for the API to work
                session_token = str(uuid.uuid4())
                
                params = {
                    "access_token": self.api_key,
                    "q": query,
                    "session_token": session_token,
                    "limit": limit,
                }

                if country:
                    params["country"] = country
                
                if proximity:
                    params["proximity"] = proximity
                
                if bbox:
                    params["bbox"] = bbox

                url = f"{self.base_url}/search/searchbox/v1/suggest"
                
                logger.info(
                    f"Calling Mapbox autocomplete: {url} with query={query}, "
                    f"country={country}, proximity={proximity}, bbox={bbox}, limit={limit}"
                )
                
                response = await client.get(url, params=params)
                
                logger.info(f"Mapbox response status: {response.status_code}")
                
                response.raise_for_status()

                data = response.json()
                suggestions = []

                for suggestion in data.get("suggestions", []):
                    # Extract coordinates if available
                    coords = suggestion.get("geometry", {}).get("coordinates", [])
                    
                    item = {
                        "formatted_address": suggestion.get("name", ""),
                        "place_id": suggestion.get("id", ""),
                        "place_type": suggestion.get("type", ""),
                    }
                    
                    if len(coords) >= 2:
                        item["longitude"] = float(coords[0])
                        item["latitude"] = float(coords[1])
                    
                    suggestions.append(item)

                logger.info(f"Found {len(suggestions)} autocomplete suggestions for query: {query}")
                
                # Cache the results
                if self.cache:
                    await self.cache.set_autocomplete(query, suggestions, country)
                
                return suggestions

        except httpx.TimeoutException:
            logger.error(f"Mapbox request timeout for search query: {query}")
            raise MapboxException("Autocomplete request timed out")
        except httpx.HTTPStatusError as e:
            error_text = e.response.text if hasattr(e.response, 'text') else str(e)
            if e.response.status_code == 401:
                logger.error(f"Mapbox API key is invalid or expired. Response: {error_text}")
                raise MapboxException("Invalid Mapbox API key")
            elif e.response.status_code == 429:
                logger.error(f"Mapbox rate limit exceeded. Response: {error_text}")
                raise MapboxException("Rate limit exceeded")
            else:
                logger.error(f"Mapbox API error for search query {query}: {e.response.status_code} {error_text}")
                raise MapboxException(f"Autocomplete failed: {str(e)}")
        except httpx.HTTPError as e:
            logger.error(f"Mapbox HTTP error for search query {query}: {e}")
            raise MapboxException(f"Autocomplete failed: {str(e)}")
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing Mapbox response for search query {query}: {e}")
            raise MapboxException("Invalid autocomplete response")

    async def calculate_distance(
        self,
        from_coords: Tuple[float, float],
        to_coords: Tuple[float, float]
    ) -> float:
        """
        Calculate distance between two points using Haversine formula.
        
        This is a simple client-side calculation that doesn't require API calls.
        For more advanced routing with turn-by-turn directions, use Mapbox Directions API.

        Args:
            from_coords: Tuple of (latitude, longitude) for starting point
            to_coords: Tuple of (latitude, longitude) for ending point

        Returns:
            Distance in kilometers

        Raises:
            ValueError: If coordinates are invalid
        
        Requirement 4.1: Distance calculation using Haversine formula
        Requirement 5.4: Distance caching with 24-hour TTL
        """
        from app.utils.distance import calculate_haversine_distance

        lat1, lon1 = from_coords
        lat2, lon2 = to_coords

        # Check cache first
        from_coords_str = f"{lat1},{lon1}"
        to_coords_str = f"{lat2},{lon2}"
        
        if self.cache:
            cached_distance = await self.cache.get_distance(from_coords_str, to_coords_str)
            if cached_distance is not None:
                return cached_distance

        # Calculate using Haversine formula
        distance_km = calculate_haversine_distance(from_coords, to_coords)

        # Cache the result
        if self.cache:
            await self.cache.set_distance(from_coords_str, to_coords_str, distance_km)

        return distance_km

    def format_distance(self, distance_km: float) -> str:
        """
        Format distance for display with one decimal place.

        Args:
            distance_km: Distance in kilometers

        Returns:
            Formatted distance string (e.g., "2.5 km")
        
        Requirement 4.2: Distance formatting with one decimal place
        Requirement 9.5: Use kilometers for African markets
        """
        from app.utils.distance import format_distance
        return format_distance(distance_km, decimal_places=1)

    def _calculate_confidence(self, feature: Dict[str, Any]) -> float:
        """
        Calculate confidence score for a geocoding result.
        
        Based on Mapbox relevance score and place type.
        """
        relevance = feature.get("relevance", 0.5)
        
        # Boost confidence for specific place types
        place_type = feature.get("place_type", [])
        if "address" in place_type:
            relevance = min(1.0, relevance * 1.1)
        
        return min(1.0, max(0.0, relevance))

    def validate_api_keys(self) -> Dict[str, bool]:
        """
        Validate that API keys are properly configured.

        Returns:
            Dictionary with validation results
        """
        return {
            "secret_key_present": bool(self.api_key and self.api_key.strip()),
            "public_key_present": bool(self.public_key and self.public_key.strip()),
            "base_url_configured": bool(self.base_url),
            "timeout_configured": self.timeout > 0,
        }

    def get_service_info(self) -> Dict[str, Any]:
        """
        Get service information and configuration.

        Returns:
            Dictionary with service details
        """
        return {
            "service": "MapboxService",
            "base_url": self.base_url,
            "timeout": self.timeout,
            "api_keys_valid": all(self.validate_api_keys().values()),
            "version": "1.0.0",
        }
