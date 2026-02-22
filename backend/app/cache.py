"""Redis cache configuration and management."""

import logging
import json
from typing import Any, Optional
from redis import Redis, ConnectionPool
from app.config import settings

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis cache manager."""

    def __init__(self):
        """Initialize Redis cache."""
        self.pool = None
        self.redis = None

    def init(self):
        """Initialize Redis connection pool."""
        try:
            self.pool = ConnectionPool.from_url(
                settings.redis_url,
                max_connections=50,
                decode_responses=True,
            )
            self.redis = Redis(connection_pool=self.pool)

            # Test connection
            self.redis.ping()
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Redis cache: {e}")
            raise

    def close(self):
        """Close Redis connection pool."""
        try:
            if self.pool:
                self.pool.disconnect()
            logger.info("Redis cache connection closed")
        except Exception as e:
            logger.error(f"Error closing Redis cache: {e}")

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            if not self.redis:
                return None

            value = self.redis.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL."""
        try:
            if not self.redis:
                return False

            if isinstance(value, (dict, list)):
                value = json.dumps(value)

            self.redis.setex(key, ttl, value)
            return True
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            if not self.redis:
                return False

            self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        try:
            if not self.redis:
                return 0

            keys = self.redis.keys(pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Error clearing cache pattern {pattern}: {e}")
            return 0

    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            if not self.redis:
                return False

            return self.redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Error checking cache key {key}: {e}")
            return False


# Global cache instance
cache = RedisCache()

# Alias for backward compatibility
redis_client = None  # Will be initialized on demand
