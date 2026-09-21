"""In-memory cache configuration and management."""

import logging
import json
import time
import threading
from typing import Any, Optional

logger = logging.getLogger(__name__)


class InMemoryCache:
    """In-memory cache manager with TTL support."""

    def __init__(self):
        self._store: dict[str, tuple[Any, float]] = {}
        self._lock = threading.Lock()

    def _is_expired(self, key: str) -> bool:
        if key not in self._store:
            return True
        _, expiry = self._store[key]
        return time.time() > expiry

    def _cleanup_expired(self) -> None:
        now = time.time()
        expired = [k for k, (_, expiry) in self._store.items() if now > expiry]
        for key in expired:
            del self._store[key]

    def get(self, key: str) -> Optional[Any]:
        try:
            with self._lock:
                if self._is_expired(key):
                    return None
                value, _ = self._store[key]
                return value
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        try:
            with self._lock:
                self._store[key] = (value, time.time() + ttl)
                return True
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False

    def setex(self, key: str, ttl: int, value: Any) -> bool:
        """Set value with TTL."""
        return self.set(key, value, ttl=ttl)

    def delete(self, key: str) -> bool:
        try:
            with self._lock:
                if key in self._store:
                    del self._store[key]
                    return True
                return False
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False

    def incr(self, key: str) -> int:
        """Increment counter key and return new value."""
        with self._lock:
            if self._is_expired(key):
                self._store[key] = (1, time.time() + 3600)
                return 1
            value, expiry = self._store[key]
            try:
                count = int(value) + 1
            except (TypeError, ValueError):
                count = 1
            self._store[key] = (count, expiry)
            return count

    def expire(self, key: str, ttl: int) -> bool:
        """Set TTL on existing key."""
        with self._lock:
            if key in self._store:
                value, _ = self._store[key]
                self._store[key] = (value, time.time() + ttl)
                return True
            return False

    def keys(self, pattern: str) -> list[str]:
        """Return keys matching pattern."""
        with self._lock:
            self._cleanup_expired()
            import fnmatch
            return [k for k in self._store if fnmatch.fnmatch(k, pattern)]

    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        try:
            keys = self.keys(pattern)
            for key in keys:
                del self._store[key]
            return len(keys)
        except Exception as e:
            logger.error(f"Error clearing cache pattern {pattern}: {e}")
            return 0

    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            with self._lock:
                return not self._is_expired(key)
        except Exception as e:
            logger.error(f"Error checking cache key {key}: {e}")
            return False

    def init(self) -> None:
        logger.info("In-memory cache initialized")

    def close(self) -> None:
        with self._lock:
            self._store.clear()
        logger.info("In-memory cache cleared")


# Global cache instance
cache = InMemoryCache()

# Alias for backward compatibility - point to in-memory cache
redis_client = cache
