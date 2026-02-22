"""
Latency optimization service for detecting poor connectivity and adjusting cache TTLs.

This service monitors API response times and automatically adjusts caching behavior
to reduce real-time API calls during high latency periods.

Requirements:
    - 9.2: Use cached data during poor network connectivity
    - 9.4: Detect high latency (>2 seconds) and adjust cache TTL
"""

import logging
import time
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from collections import deque
import asyncio

logger = logging.getLogger(__name__)


class LatencyOptimizationService:
    """Service for detecting latency and optimizing cache behavior"""

    # Latency thresholds
    HIGH_LATENCY_THRESHOLD = 2.0  # seconds
    NORMAL_LATENCY_THRESHOLD = 0.5  # seconds
    
    # Cache TTL multipliers
    NORMAL_CACHE_MULTIPLIER = 1.0
    HIGH_LATENCY_CACHE_MULTIPLIER = 3.0  # 3x longer TTL during high latency

    def __init__(self, window_size: int = 10):
        """
        Initialize latency optimization service.

        Args:
            window_size: Number of recent requests to track for latency calculation
        """
        self.window_size = window_size
        self.latency_history: deque = deque(maxlen=window_size)
        self.high_latency_mode = False
        self.high_latency_start_time: Optional[datetime] = None
        self.high_latency_duration = timedelta(minutes=5)  # Stay in high latency mode for 5 minutes

    def record_latency(self, latency_seconds: float) -> None:
        """
        Record API response latency.

        Args:
            latency_seconds: Response time in seconds
        """
        self.latency_history.append(latency_seconds)
        
        # Check if we should enter high latency mode
        if latency_seconds > self.HIGH_LATENCY_THRESHOLD:
            if not self.high_latency_mode:
                self.high_latency_mode = True
                self.high_latency_start_time = datetime.utcnow()
                logger.warning(
                    f"High latency detected ({latency_seconds:.2f}s). "
                    f"Entering high latency mode for {self.high_latency_duration.total_seconds():.0f} seconds."
                )
        
        # Check if we should exit high latency mode
        if self.high_latency_mode and self.high_latency_start_time:
            elapsed = datetime.utcnow() - self.high_latency_start_time
            if elapsed > self.high_latency_duration:
                # Check if latency has improved
                avg_latency = self.get_average_latency()
                if avg_latency < self.NORMAL_LATENCY_THRESHOLD:
                    self.high_latency_mode = False
                    self.high_latency_start_time = None
                    logger.info(
                        f"Latency improved ({avg_latency:.2f}s). "
                        f"Exiting high latency mode."
                    )

    def get_average_latency(self) -> float:
        """
        Get average latency from recent requests.

        Returns:
            Average latency in seconds
        """
        if not self.latency_history:
            return 0.0
        
        return sum(self.latency_history) / len(self.latency_history)

    def get_max_latency(self) -> float:
        """
        Get maximum latency from recent requests.

        Returns:
            Maximum latency in seconds
        """
        if not self.latency_history:
            return 0.0
        
        return max(self.latency_history)

    def get_cache_ttl_multiplier(self) -> float:
        """
        Get cache TTL multiplier based on current latency.

        Returns:
            Multiplier to apply to base cache TTL
        """
        if self.high_latency_mode:
            return self.HIGH_LATENCY_CACHE_MULTIPLIER
        return self.NORMAL_CACHE_MULTIPLIER

    def is_high_latency_mode(self) -> bool:
        """
        Check if system is in high latency mode.

        Returns:
            True if high latency mode is active
        """
        return self.high_latency_mode

    def get_status(self) -> Dict[str, Any]:
        """
        Get current latency optimization status.

        Returns:
            Dictionary with status information
        """
        return {
            "high_latency_mode": self.high_latency_mode,
            "average_latency_seconds": round(self.get_average_latency(), 3),
            "max_latency_seconds": round(self.get_max_latency(), 3),
            "cache_ttl_multiplier": self.get_cache_ttl_multiplier(),
            "recent_requests": len(self.latency_history),
            "high_latency_start_time": self.high_latency_start_time.isoformat() if self.high_latency_start_time else None,
        }


class LatencyTrackingDecorator:
    """Decorator for tracking latency of async functions"""

    def __init__(self, optimization_service: LatencyOptimizationService):
        """
        Initialize latency tracking decorator.

        Args:
            optimization_service: LatencyOptimizationService instance
        """
        self.optimization_service = optimization_service

    def __call__(self, func: Callable) -> Callable:
        """
        Decorate an async function to track its latency.

        Args:
            func: Async function to decorate

        Returns:
            Decorated function
        """
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                elapsed = time.time() - start_time
                self.optimization_service.record_latency(elapsed)
                
                if elapsed > self.optimization_service.HIGH_LATENCY_THRESHOLD:
                    logger.debug(
                        f"High latency detected in {func.__name__}: {elapsed:.2f}s"
                    )
        
        return wrapper


class AdaptiveCacheService:
    """Cache service that adapts TTL based on latency"""

    def __init__(
        self,
        base_cache_service,
        optimization_service: LatencyOptimizationService
    ):
        """
        Initialize adaptive cache service.

        Args:
            base_cache_service: Base cache service (e.g., CacheService)
            optimization_service: LatencyOptimizationService instance
        """
        self.base_cache = base_cache_service
        self.optimization_service = optimization_service

    def _get_adjusted_ttl(self, base_ttl: timedelta) -> timedelta:
        """
        Get adjusted TTL based on current latency.

        Args:
            base_ttl: Base TTL duration

        Returns:
            Adjusted TTL duration
        """
        multiplier = self.optimization_service.get_cache_ttl_multiplier()
        adjusted_seconds = base_ttl.total_seconds() * multiplier
        return timedelta(seconds=adjusted_seconds)

    async def get_geocoding(self, address: str) -> Optional[Dict[str, Any]]:
        """Get cached geocoding result"""
        return await self.base_cache.get_geocoding(address)

    async def set_geocoding(self, address: str, result: Dict[str, Any]) -> None:
        """
        Set geocoding cache with adjusted TTL.

        Args:
            address: Address string
            result: Geocoding result
        """
        # Get base TTL from cache service
        base_ttl = self.base_cache.geocoding_ttl
        adjusted_ttl = self._get_adjusted_ttl(base_ttl)
        
        # Temporarily override TTL
        original_ttl = self.base_cache.geocoding_ttl
        self.base_cache.geocoding_ttl = adjusted_ttl
        
        try:
            await self.base_cache.set_geocoding(address, result)
        finally:
            # Restore original TTL
            self.base_cache.geocoding_ttl = original_ttl

    async def get_autocomplete(self, query: str, country: Optional[str] = None) -> Optional[list]:
        """Get cached autocomplete results"""
        return await self.base_cache.get_autocomplete(query, country)

    async def set_autocomplete(
        self,
        query: str,
        results: list,
        country: Optional[str] = None
    ) -> None:
        """
        Set autocomplete cache with adjusted TTL.

        Args:
            query: Search query
            results: Autocomplete results
            country: Optional country code
        """
        # Get base TTL from cache service
        base_ttl = self.base_cache.autocomplete_ttl
        adjusted_ttl = self._get_adjusted_ttl(base_ttl)
        
        # Temporarily override TTL
        original_ttl = self.base_cache.autocomplete_ttl
        self.base_cache.autocomplete_ttl = adjusted_ttl
        
        try:
            await self.base_cache.set_autocomplete(query, results, country)
        finally:
            # Restore original TTL
            self.base_cache.autocomplete_ttl = original_ttl

    async def get_distance(self, from_coords: str, to_coords: str) -> Optional[float]:
        """Get cached distance"""
        return await self.base_cache.get_distance(from_coords, to_coords)

    async def set_distance(self, from_coords: str, to_coords: str, distance: float) -> None:
        """
        Set distance cache with adjusted TTL.

        Args:
            from_coords: Starting coordinates
            to_coords: Ending coordinates
            distance: Distance in kilometers
        """
        # Get base TTL from cache service
        base_ttl = self.base_cache.distance_ttl
        adjusted_ttl = self._get_adjusted_ttl(base_ttl)
        
        # Temporarily override TTL
        original_ttl = self.base_cache.distance_ttl
        self.base_cache.distance_ttl = adjusted_ttl
        
        try:
            await self.base_cache.set_distance(from_coords, to_coords, distance)
        finally:
            # Restore original TTL
            self.base_cache.distance_ttl = original_ttl

    async def invalidate_location(self, location_id: str) -> None:
        """Invalidate location caches"""
        return await self.base_cache.invalidate_location(location_id)

    async def clear_all(self) -> None:
        """Clear all caches"""
        return await self.base_cache.clear_all()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self.base_cache.get_cache_stats()
