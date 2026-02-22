"""
Nominatim geocoding service for address lookup and reverse geocoding.
Provides free, open-source geocoding using OpenStreetMap data.
"""

import httpx
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from app.config import settings

logger = logging.getLogger(__name__)


class NominatimException(Exception):
    """Exception raised for Nominatim API errors"""
    pass


class NominatimService:
    """Service for geocoding addresses using Nominatim API"""

    def __init__(self):
        """Initialize Nominatim service"""
        self.base_url = settings.NOMINATIM_API_URL or "https://nominatim.openstreetmap.org"
        self.timeout = 10.0
        # Simple in-memory cache for geocoding results
        # In production, use Redis or similar
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = timedelta(days=30)

    async def geocode_address(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Convert address to latitude and longitude using Nominatim.

        Args:
            address: Address string to geocode

        Returns:
            Dictionary with latitude, longitude, and formatted_address, or None if not found

        Raises:
            NominatimException: If API request fails
        """
        if not address or not address.strip():
            raise ValueError("Address cannot be empty")

        # Check cache first
        cached = self._get_from_cache(address)
        if cached:
            logger.debug(f"Cache hit for address: {address}")
            return cached

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {
                    "q": address,
                    "format": "json",
                    "limit": 1,
                    "user_agent": "kenikool-salon-api"
                }

                response = await client.get(f"{self.base_url}/search", params=params)
                response.raise_for_status()

                results = response.json()

                if not results:
                    logger.warning(f"No geocoding results for address: {address}")
                    return None

                data = results[0]
                result = {
                    "latitude": float(data["lat"]),
                    "longitude": float(data["lon"]),
                    "formatted_address": data.get("display_name", address),
                    "place_id": data.get("place_id"),
                    "osm_id": data.get("osm_id"),
                    "osm_type": data.get("osm_type"),
                }

                # Cache the result
                self._set_cache(address, result)

                logger.info(f"Geocoded address: {address} -> ({result['latitude']}, {result['longitude']})")
                return result

        except httpx.TimeoutException:
            logger.error(f"Nominatim request timeout for address: {address}")
            raise NominatimException("Geocoding request timed out")
        except httpx.HTTPError as e:
            logger.error(f"Nominatim API error for address {address}: {e}")
            raise NominatimException(f"Geocoding failed: {str(e)}")
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing Nominatim response for address {address}: {e}")
            raise NominatimException("Invalid geocoding response")

    async def reverse_geocode(self, latitude: float, longitude: float) -> Optional[str]:
        """
        Convert latitude and longitude to address using Nominatim.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate

        Returns:
            Formatted address string, or None if not found

        Raises:
            NominatimException: If API request fails
        """
        if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
            raise ValueError("Latitude and longitude must be numbers")

        if latitude < -90 or latitude > 90:
            raise ValueError("Latitude must be between -90 and 90")

        if longitude < -180 or longitude > 180:
            raise ValueError("Longitude must be between -180 and 180")

        # Check cache first
        cache_key = f"reverse_{latitude}_{longitude}"
        cached = self._get_from_cache(cache_key)
        if cached:
            logger.debug(f"Cache hit for coordinates: {latitude}, {longitude}")
            return cached.get("formatted_address")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {
                    "lat": latitude,
                    "lon": longitude,
                    "format": "json",
                    "user_agent": "kenikool-salon-api"
                }

                response = await client.get(f"{self.base_url}/reverse", params=params)
                response.raise_for_status()

                data = response.json()

                if "error" in data:
                    logger.warning(f"No reverse geocoding results for coordinates: {latitude}, {longitude}")
                    return None

                address = data.get("display_name")

                if address:
                    # Cache the result
                    result = {
                        "formatted_address": address,
                        "latitude": latitude,
                        "longitude": longitude,
                    }
                    self._set_cache(cache_key, result)

                    logger.info(f"Reverse geocoded ({latitude}, {longitude}) -> {address}")

                return address

        except httpx.TimeoutException:
            logger.error(f"Nominatim request timeout for coordinates: {latitude}, {longitude}")
            raise NominatimException("Reverse geocoding request timed out")
        except httpx.HTTPError as e:
            logger.error(f"Nominatim API error for coordinates {latitude}, {longitude}: {e}")
            raise NominatimException(f"Reverse geocoding failed: {str(e)}")
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing Nominatim response for coordinates {latitude}, {longitude}: {e}")
            raise NominatimException("Invalid reverse geocoding response")

    async def search_addresses(self, query: str, limit: int = 5) -> list:
        """
        Search for addresses matching a query string.

        Args:
            query: Search query string
            limit: Maximum number of results to return

        Returns:
            List of address suggestions

        Raises:
            NominatimException: If API request fails
        """
        if not query or not query.strip():
            raise ValueError("Search query cannot be empty")

        if limit < 1 or limit > 50:
            limit = 5

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {
                    "q": query,
                    "format": "json",
                    "limit": limit,
                    "user_agent": "kenikool-salon-api"
                }

                response = await client.get(f"{self.base_url}/search", params=params)
                response.raise_for_status()

                results = response.json()

                suggestions = []
                for result in results:
                    suggestion = {
                        "display_name": result.get("display_name"),
                        "latitude": float(result.get("lat", 0)),
                        "longitude": float(result.get("lon", 0)),
                        "place_id": result.get("place_id"),
                        "osm_type": result.get("osm_type"),
                    }
                    suggestions.append(suggestion)

                logger.info(f"Found {len(suggestions)} address suggestions for query: {query}")
                return suggestions

        except httpx.TimeoutException:
            logger.error(f"Nominatim request timeout for search query: {query}")
            raise NominatimException("Address search request timed out")
        except httpx.HTTPError as e:
            logger.error(f"Nominatim API error for search query {query}: {e}")
            raise NominatimException(f"Address search failed: {str(e)}")
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing Nominatim response for search query {query}: {e}")
            raise NominatimException("Invalid search response")

    def _get_from_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """Get value from cache if not expired"""
        if key in self._cache:
            entry = self._cache[key]
            if datetime.utcnow() < entry["expires_at"]:
                return entry["data"]
            else:
                # Remove expired entry
                del self._cache[key]
        return None

    def _set_cache(self, key: str, data: Dict[str, Any]) -> None:
        """Set value in cache with TTL"""
        self._cache[key] = {
            "data": data,
            "expires_at": datetime.utcnow() + self._cache_ttl,
        }

    def clear_cache(self) -> None:
        """Clear all cached entries"""
        self._cache.clear()
        logger.info("Nominatim cache cleared")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        expired_count = 0
        for key, entry in list(self._cache.items()):
            if datetime.utcnow() >= entry["expires_at"]:
                expired_count += 1

        return {
            "total_entries": len(self._cache),
            "expired_entries": expired_count,
            "active_entries": len(self._cache) - expired_count,
        }
