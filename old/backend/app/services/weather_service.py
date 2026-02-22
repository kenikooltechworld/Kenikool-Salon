"""
Weather Service for 3D Map Visualization

Provides weather data integration for animated 3D weather effects on maps.
Fetches weather data from external APIs and caches results.

Requirements: 13.2
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import aiohttp

from app.services.cache_service import CacheService

logger = logging.getLogger(__name__)


class WeatherService:
    """Service for fetching and managing weather data for map visualization"""

    def __init__(self, cache_service: CacheService, api_key: Optional[str] = None):
        """
        Initialize WeatherService

        Args:
            cache_service: CacheService instance for caching weather data
            api_key: Optional API key for weather service (e.g., OpenWeatherMap)
        """
        self.cache = cache_service
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        self.timeout = 10.0

    async def get_weather(
        self,
        latitude: float,
        longitude: float,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Get weather data for a location

        Args:
            latitude: Location latitude
            longitude: Location longitude
            use_cache: Whether to use cached data

        Returns:
            Weather data with condition, temperature, humidity, wind speed

        Raises:
            ValueError: If API key is not configured
            Exception: If weather API call fails
        """
        if not self.api_key:
            logger.warning("Weather API key not configured, returning default weather")
            return self._get_default_weather()

        # Check cache first
        cache_key = f"weather:{latitude}:{longitude}"
        if use_cache:
            cached_weather = await self.cache.get(cache_key)
            if cached_weather:
                logger.debug(f"Weather cache hit for {latitude}, {longitude}")
                return cached_weather

        try:
            # Fetch weather from API
            weather_data = await self._fetch_weather_from_api(latitude, longitude)

            # Cache the result for 1 hour
            await self.cache.set(cache_key, weather_data, ttl=3600)

            return weather_data

        except Exception as e:
            logger.error(f"Failed to fetch weather data: {e}")
            # Return default weather on error
            return self._get_default_weather()

    async def _fetch_weather_from_api(
        self,
        latitude: float,
        longitude: float,
    ) -> Dict[str, Any]:
        """
        Fetch weather data from OpenWeatherMap API

        Args:
            latitude: Location latitude
            longitude: Location longitude

        Returns:
            Parsed weather data

        Raises:
            Exception: If API call fails
        """
        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": self.api_key,
            "units": "metric",  # Use metric units for African markets
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.base_url,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                ) as response:
                    if response.status != 200:
                        raise Exception(
                            f"Weather API returned status {response.status}"
                        )

                    data = await response.json()
                    return self._parse_weather_response(data)

        except asyncio.TimeoutError:
            raise Exception("Weather API request timed out")
        except Exception as e:
            raise Exception(f"Weather API error: {str(e)}")

    def _parse_weather_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse OpenWeatherMap API response

        Args:
            data: Raw API response

        Returns:
            Parsed weather data with condition, temperature, humidity, wind speed
        """
        try:
            # Extract weather condition
            weather_main = data.get("weather", [{}])[0].get("main", "Clear").lower()
            condition = self._map_weather_condition(weather_main)

            # Extract temperature and other metrics
            main_data = data.get("main", {})
            wind_data = data.get("wind", {})

            return {
                "condition": condition,
                "temperature": main_data.get("temp"),
                "humidity": main_data.get("humidity"),
                "windSpeed": wind_data.get("speed"),
                "description": data.get("weather", [{}])[0].get("description", ""),
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to parse weather response: {e}")
            return self._get_default_weather()

    def _map_weather_condition(self, weather_main: str) -> str:
        """
        Map OpenWeatherMap condition to our weather conditions

        Args:
            weather_main: Weather condition from API

        Returns:
            Mapped weather condition (clear, rain, clouds, fog, snow)
        """
        weather_mapping = {
            "clear": "clear",
            "clouds": "clouds",
            "rain": "rain",
            "drizzle": "rain",
            "thunderstorm": "rain",
            "mist": "fog",
            "smoke": "fog",
            "haze": "fog",
            "dust": "fog",
            "fog": "fog",
            "sand": "fog",
            "ash": "fog",
            "squall": "rain",
            "tornado": "rain",
            "snow": "snow",
        }

        return weather_mapping.get(weather_main, "clear")

    def _get_default_weather(self) -> Dict[str, Any]:
        """
        Get default weather data (clear conditions)

        Returns:
            Default weather data
        """
        return {
            "condition": "clear",
            "temperature": None,
            "humidity": None,
            "windSpeed": None,
            "description": "Clear",
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def get_weather_for_locations(
        self,
        locations: list[Dict[str, float]],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get weather data for multiple locations

        Args:
            locations: List of location dicts with 'latitude' and 'longitude'

        Returns:
            Dict mapping location coordinates to weather data

        Raises:
            Exception: If any weather fetch fails
        """
        results = {}

        # Fetch weather for all locations concurrently
        tasks = [
            self.get_weather(loc["latitude"], loc["longitude"])
            for loc in locations
        ]

        weather_data_list = await asyncio.gather(*tasks, return_exceptions=True)

        for i, location in enumerate(locations):
            key = f"{location['latitude']},{location['longitude']}"
            weather = weather_data_list[i]

            if isinstance(weather, Exception):
                logger.error(f"Failed to fetch weather for location {key}: {weather}")
                results[key] = self._get_default_weather()
            else:
                results[key] = weather

        return results

    async def update_weather_cache(
        self,
        latitude: float,
        longitude: float,
        weather_data: Dict[str, Any],
    ) -> None:
        """
        Manually update weather cache

        Args:
            latitude: Location latitude
            longitude: Location longitude
            weather_data: Weather data to cache
        """
        cache_key = f"weather:{latitude}:{longitude}"
        await self.cache.set(cache_key, weather_data, ttl=3600)
        logger.debug(f"Weather cache updated for {latitude}, {longitude}")

    async def clear_weather_cache(
        self,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> None:
        """
        Clear weather cache

        Args:
            latitude: Optional latitude to clear specific location
            longitude: Optional longitude to clear specific location
        """
        if latitude is not None and longitude is not None:
            cache_key = f"weather:{latitude}:{longitude}"
            await self.cache.delete(cache_key)
            logger.debug(f"Weather cache cleared for {latitude}, {longitude}")
        else:
            # Clear all weather cache entries
            logger.debug("Clearing all weather cache entries")
