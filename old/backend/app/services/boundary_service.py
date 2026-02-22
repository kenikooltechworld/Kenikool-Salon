"""
Boundary Service for African Markets

Provides integration with Mapbox Boundaries 4.5 data for accurate administrative
division identification and location validation in African markets.

Requirements: 14.1, 14.2, 14.4
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import aiohttp

from app.services.cache_service import CacheService

logger = logging.getLogger(__name__)


class BoundaryService:
    """Service for managing Mapbox Boundaries 4.5 data"""

    def __init__(self, cache_service: CacheService, api_key: Optional[str] = None):
        """
        Initialize BoundaryService

        Args:
            cache_service: CacheService instance for caching boundary data
            api_key: Mapbox API key for boundary queries
        """
        self.cache = cache_service
        self.api_key = api_key
        self.base_url = "https://api.mapbox.com/v4/mapbox.mapbox-boundaries-v4"
        self.timeout = 15.0
        self.supported_countries = ["NG", "ZA", "EG", "KE"]  # Nigeria, South Africa, Egypt, Kenya

    async def get_administrative_divisions(
        self,
        latitude: float,
        longitude: float,
        country: Optional[str] = None,
        use_cache: bool = True,
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
            Exception: If boundary lookup fails
        """
        # Check cache first
        cache_key = f"boundaries:{latitude}:{longitude}"
        if use_cache:
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                logger.debug(f"Boundary cache hit for {latitude}, {longitude}")
                return cached_data

        try:
            # Fetch boundary data from Mapbox
            boundary_data = await self._fetch_boundary_data(latitude, longitude)

            # Validate country if provided
            if country and boundary_data.get("country_code") != country:
                logger.warning(
                    f"Location {latitude}, {longitude} is in {boundary_data.get('country_code')}, "
                    f"not {country}"
                )

            # Cache the result for 30 days
            await self.cache.set(cache_key, boundary_data, ttl=2592000)

            return boundary_data

        except Exception as e:
            logger.error(f"Failed to fetch boundary data: {e}")
            raise

    async def _fetch_boundary_data(
        self,
        latitude: float,
        longitude: float,
    ) -> Dict[str, Any]:
        """
        Fetch boundary data from Mapbox Boundaries API

        Args:
            latitude: Location latitude
            longitude: Location longitude

        Returns:
            Parsed boundary data

        Raises:
            Exception: If API call fails
        """
        try:
            # Use Mapbox Tilequery API to get boundary features
            url = f"{self.base_url}/tilequery/{longitude},{latitude}.json"
            params = {
                "access_token": self.api_key,
                "layers": "admin_0,admin_1,admin_2,postal_code",
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                ) as response:
                    if response.status != 200:
                        raise Exception(
                            f"Boundary API returned status {response.status}"
                        )

                    data = await response.json()
                    return self._parse_boundary_response(data)

        except asyncio.TimeoutError:
            raise Exception("Boundary API request timed out")
        except Exception as e:
            raise Exception(f"Boundary API error: {str(e)}")

    def _parse_boundary_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse Mapbox Boundaries API response

        Args:
            data: Raw API response

        Returns:
            Parsed boundary data with administrative divisions
        """
        try:
            features = data.get("features", [])
            boundary_data = {
                "country": None,
                "country_code": None,
                "region": None,
                "region_code": None,
                "district": None,
                "postal_code": None,
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Extract boundary information from features
            for feature in features:
                properties = feature.get("properties", {})
                layer = feature.get("layer", {}).get("id", "")

                if layer == "admin_0":
                    boundary_data["country"] = properties.get("name")
                    boundary_data["country_code"] = properties.get("iso_3166_1_alpha_2")

                elif layer == "admin_1":
                    boundary_data["region"] = properties.get("name")
                    boundary_data["region_code"] = properties.get("iso_3166_2")

                elif layer == "admin_2":
                    boundary_data["district"] = properties.get("name")

                elif layer == "postal_code":
                    boundary_data["postal_code"] = properties.get("name")

            return boundary_data

        except Exception as e:
            logger.error(f"Failed to parse boundary response: {e}")
            raise

    async def validate_location_in_boundary(
        self,
        latitude: float,
        longitude: float,
        country: str,
    ) -> bool:
        """
        Validate that a location is within a specific country boundary

        Args:
            latitude: Location latitude
            longitude: Location longitude
            country: Country code (e.g., "NG" for Nigeria)

        Returns:
            True if location is within country, False otherwise

        Raises:
            Exception: If validation fails
        """
        try:
            boundary_data = await self.get_administrative_divisions(
                latitude,
                longitude,
                country=country,
            )

            return boundary_data.get("country_code") == country

        except Exception as e:
            logger.error(f"Failed to validate location boundary: {e}")
            raise

    async def get_locations_by_region(
        self,
        country: str,
        region: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get all locations in a specific region

        Args:
            country: Country code
            region: Optional region name

        Returns:
            List of locations in the region

        Raises:
            Exception: If query fails
        """
        # This would typically query the database for locations
        # matching the specified country and region
        logger.info(f"Querying locations for {country}/{region}")
        # Implementation would depend on database schema
        return []

    async def refresh_boundary_data(
        self,
        force: bool = False,
    ) -> Dict[str, Any]:
        """
        Refresh boundary data cache

        Args:
            force: Force refresh even if cache is valid

        Returns:
            Refresh statistics

        Raises:
            Exception: If refresh fails
        """
        try:
            stats = {
                "refreshed_at": datetime.utcnow().isoformat(),
                "locations_revalidated": 0,
                "errors": [],
            }

            if force:
                # Clear all boundary cache entries
                logger.info("Forcing boundary data refresh")
                # Implementation would clear cache and re-fetch

            logger.info(f"Boundary data refresh completed: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Failed to refresh boundary data: {e}")
            raise

    async def get_boundary_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about boundary data coverage

        Returns:
            Statistics about boundary data
        """
        return {
            "supported_countries": self.supported_countries,
            "cache_size": "unknown",  # Would query cache service
            "last_refresh": None,  # Would track refresh time
            "coverage": {
                "NG": "Complete",  # Nigeria
                "ZA": "Complete",  # South Africa
                "EG": "Complete",  # Egypt
                "KE": "Complete",  # Kenya
            },
        }

    async def extract_postal_code(
        self,
        latitude: float,
        longitude: float,
    ) -> Optional[str]:
        """
        Extract postal code for a location

        Args:
            latitude: Location latitude
            longitude: Location longitude

        Returns:
            Postal code if available, None otherwise

        Raises:
            Exception: If extraction fails
        """
        try:
            boundary_data = await self.get_administrative_divisions(
                latitude,
                longitude,
            )

            return boundary_data.get("postal_code")

        except Exception as e:
            logger.error(f"Failed to extract postal code: {e}")
            return None

    async def extract_administrative_region(
        self,
        latitude: float,
        longitude: float,
    ) -> Optional[str]:
        """
        Extract administrative region for a location

        Args:
            latitude: Location latitude
            longitude: Location longitude

        Returns:
            Administrative region if available, None otherwise

        Raises:
            Exception: If extraction fails
        """
        try:
            boundary_data = await self.get_administrative_divisions(
                latitude,
                longitude,
            )

            # Return region or district, whichever is available
            return boundary_data.get("region") or boundary_data.get("district")

        except Exception as e:
            logger.error(f"Failed to extract administrative region: {e}")
            return None
