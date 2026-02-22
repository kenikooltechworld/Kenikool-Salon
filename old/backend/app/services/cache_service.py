"""
Cache service for Mapbox API responses using Redis.
Manages caching with configurable TTLs for geocoding, autocomplete, and distance data.
"""

import logging
import hashlib
import json
from typing import Optional, Dict, Any, List
from datetime import timedelta
import redis
from app.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Service for caching Mapbox API responses"""

    # Cache key prefixes
    GEOCODING_PREFIX = "mapbox:geocoding"
    AUTOCOMPLETE_PREFIX = "mapbox:autocomplete"
    DISTANCE_PREFIX = "mapbox:distance"

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """
        Initialize cache service with Redis client.

        Args:
            redis_client: Optional Redis client. If not provided, will create one from settings.
        """
        if redis_client:
            self.redis = redis_client
        else:
            try:
                self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
                # Test connection
                self.redis.ping()
                logger.info("Connected to Redis for caching")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                self.redis = None

        # Cache TTLs from settings
        self.geocoding_ttl = timedelta(days=settings.MAPBOX_GEOCODING_CACHE_TTL_DAYS or 30)
        self.autocomplete_ttl = timedelta(hours=settings.MAPBOX_AUTOCOMPLETE_CACHE_TTL_HOURS or 1)
        self.distance_ttl = timedelta(hours=settings.MAPBOX_DISTANCE_CACHE_TTL_HOURS or 24)

    def _hash_key(self, key: str) -> str:
        """
        Generate a hash for cache key to keep keys short and consistent.

        Args:
            key: Original key string

        Returns:
            SHA256 hash of the key
        """
        return hashlib.sha256(key.encode()).hexdigest()

    async def get_geocoding(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Get cached geocoding result.

        Args:
            address: Address string used as cache key

        Returns:
            Cached geocoding result or None if not found/expired
        """
        if not self.redis:
            return None

        try:
            cache_key = f"{self.GEOCODING_PREFIX}:{self._hash_key(address)}"
            cached_data = self.redis.get(cache_key)

            if cached_data:
                result = json.loads(cached_data)
                logger.debug(f"Cache hit for geocoding: {address}")
                return result

            return None
        except Exception as e:
            logger.error(f"Error retrieving geocoding cache for {address}: {e}")
            return None

    async def set_geocoding(self, address: str, result: Dict[str, Any]) -> None:
        """
        Cache geocoding result.

        Args:
            address: Address string used as cache key
            result: Geocoding result to cache
        """
        if not self.redis:
            return

        try:
            cache_key = f"{self.GEOCODING_PREFIX}:{self._hash_key(address)}"
            ttl_seconds = int(self.geocoding_ttl.total_seconds())
            self.redis.setex(cache_key, ttl_seconds, json.dumps(result))
            logger.debug(f"Cached geocoding result for: {address}")
        except Exception as e:
            logger.error(f"Error caching geocoding result for {address}: {e}")

    async def get_autocomplete(self, query: str, country: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        """
        Get cached autocomplete results.

        Args:
            query: Search query string
            country: Optional country code

        Returns:
            Cached autocomplete results or None if not found/expired
        """
        if not self.redis:
            return None

        try:
            cache_key_str = f"{query}:{country or 'all'}"
            cache_key = f"{self.AUTOCOMPLETE_PREFIX}:{self._hash_key(cache_key_str)}"
            cached_data = self.redis.get(cache_key)

            if cached_data:
                result = json.loads(cached_data)
                logger.debug(f"Cache hit for autocomplete: {query}")
                return result

            return None
        except Exception as e:
            logger.error(f"Error retrieving autocomplete cache for {query}: {e}")
            return None

    async def set_autocomplete(
        self,
        query: str,
        results: List[Dict[str, Any]],
        country: Optional[str] = None
    ) -> None:
        """
        Cache autocomplete results.

        Args:
            query: Search query string
            results: Autocomplete results to cache
            country: Optional country code
        """
        if not self.redis:
            return

        try:
            cache_key_str = f"{query}:{country or 'all'}"
            cache_key = f"{self.AUTOCOMPLETE_PREFIX}:{self._hash_key(cache_key_str)}"
            ttl_seconds = int(self.autocomplete_ttl.total_seconds())
            self.redis.setex(cache_key, ttl_seconds, json.dumps(results))
            logger.debug(f"Cached autocomplete results for: {query}")
        except Exception as e:
            logger.error(f"Error caching autocomplete results for {query}: {e}")

    async def get_distance(self, from_coords: str, to_coords: str) -> Optional[float]:
        """
        Get cached distance calculation.

        Args:
            from_coords: Starting coordinates as "lat,lon" string
            to_coords: Ending coordinates as "lat,lon" string

        Returns:
            Cached distance in kilometers or None if not found/expired
        """
        if not self.redis:
            return None

        try:
            cache_key_str = f"{from_coords}:{to_coords}"
            cache_key = f"{self.DISTANCE_PREFIX}:{self._hash_key(cache_key_str)}"
            cached_data = self.redis.get(cache_key)

            if cached_data:
                distance = float(cached_data)
                logger.debug(f"Cache hit for distance: {from_coords} -> {to_coords}")
                return distance

            return None
        except Exception as e:
            logger.error(f"Error retrieving distance cache for {from_coords} -> {to_coords}: {e}")
            return None

    async def set_distance(self, from_coords: str, to_coords: str, distance: float) -> None:
        """
        Cache distance calculation.

        Args:
            from_coords: Starting coordinates as "lat,lon" string
            to_coords: Ending coordinates as "lat,lon" string
            distance: Distance in kilometers
        """
        if not self.redis:
            return

        try:
            cache_key_str = f"{from_coords}:{to_coords}"
            cache_key = f"{self.DISTANCE_PREFIX}:{self._hash_key(cache_key_str)}"
            ttl_seconds = int(self.distance_ttl.total_seconds())
            self.redis.setex(cache_key, ttl_seconds, str(distance))
            logger.debug(f"Cached distance: {from_coords} -> {to_coords} = {distance:.2f} km")
        except Exception as e:
            logger.error(f"Error caching distance for {from_coords} -> {to_coords}: {e}")

    async def invalidate_location(self, location_id: str) -> None:
        """
        Invalidate all caches related to a location.
        
        This is called when a location is updated to ensure fresh data.

        Args:
            location_id: Location ID to invalidate caches for
        """
        if not self.redis:
            return

        try:
            # For now, we invalidate distance caches that might reference this location
            # In a more sophisticated system, we'd track which caches reference which locations
            pattern = f"{self.DISTANCE_PREFIX}:*"
            keys = self.redis.keys(pattern)
            
            if keys:
                self.redis.delete(*keys)
                logger.info(f"Invalidated {len(keys)} distance cache entries for location {location_id}")
        except Exception as e:
            logger.error(f"Error invalidating cache for location {location_id}: {e}")

    async def clear_all(self) -> None:
        """Clear all Mapbox-related caches."""
        if not self.redis:
            return

        try:
            patterns = [
                f"{self.GEOCODING_PREFIX}:*",
                f"{self.AUTOCOMPLETE_PREFIX}:*",
                f"{self.DISTANCE_PREFIX}:*",
            ]

            total_deleted = 0
            for pattern in patterns:
                keys = self.redis.keys(pattern)
                if keys:
                    self.redis.delete(*keys)
                    total_deleted += len(keys)

            logger.info(f"Cleared {total_deleted} cache entries")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        if not self.redis:
            return {"status": "Redis not available"}

        try:
            stats = {
                "geocoding_entries": len(self.redis.keys(f"{self.GEOCODING_PREFIX}:*")),
                "autocomplete_entries": len(self.redis.keys(f"{self.AUTOCOMPLETE_PREFIX}:*")),
                "distance_entries": len(self.redis.keys(f"{self.DISTANCE_PREFIX}:*")),
                "geocoding_ttl_days": settings.MAPBOX_GEOCODING_CACHE_TTL_DAYS,
                "autocomplete_ttl_hours": settings.MAPBOX_AUTOCOMPLETE_CACHE_TTL_HOURS,
                "distance_ttl_hours": settings.MAPBOX_DISTANCE_CACHE_TTL_HOURS,
            }
            return stats
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"error": str(e)}
