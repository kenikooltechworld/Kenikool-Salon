"""
Redis caching and rate limiting utilities
"""
import logging
import json
from typing import Any, Optional
from datetime import timedelta
import redis
from app.config import settings

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis cache manager for caching and rate limiting"""
    
    _client: Optional[redis.Redis] = None
    
    @classmethod
    def get_client(cls) -> redis.Redis:
        """Get or create Redis client"""
        if cls._client is None:
            try:
                cls._client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_keepalive=True,
                    health_check_interval=30
                )
                # Test connection
                cls._client.ping()
                logger.info("Connected to Redis")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise
        return cls._client
    
    @classmethod
    def set(
        cls,
        key: str,
        value: Any,
        expire: Optional[timedelta] = None
    ) -> bool:
        """
        Set a value in cache
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            expire: Optional expiration time
        """
        try:
            client = cls.get_client()
            serialized = json.dumps(value) if not isinstance(value, str) else value
            
            if expire:
                return client.setex(key, expire, serialized)
            else:
                return client.set(key, serialized)
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False
    
    @classmethod
    def get(cls, key: str) -> Optional[Any]:
        """
        Get a value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        try:
            client = cls.get_client()
            value = client.get(key)
            
            if value is None:
                return None
            
            # Try to deserialize as JSON
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None
    
    @classmethod
    def delete(cls, key: str) -> bool:
        """Delete a cache key"""
        try:
            client = cls.get_client()
            return client.delete(key) > 0
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False
    
    @classmethod
    def exists(cls, key: str) -> bool:
        """Check if a key exists"""
        try:
            client = cls.get_client()
            return client.exists(key) > 0
        except Exception as e:
            logger.error(f"Error checking cache key {key}: {e}")
            return False
    
    @classmethod
    def increment(cls, key: str, amount: int = 1) -> int:
        """Increment a counter"""
        try:
            client = cls.get_client()
            return client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Error incrementing cache key {key}: {e}")
            return 0
    
    @classmethod
    def decrement(cls, key: str, amount: int = 1) -> int:
        """Decrement a counter"""
        try:
            client = cls.get_client()
            return client.decrby(key, amount)
        except Exception as e:
            logger.error(f"Error decrementing cache key {key}: {e}")
            return 0
    
    @classmethod
    def get_ttl(cls, key: str) -> int:
        """Get time to live for a key in seconds"""
        try:
            client = cls.get_client()
            return client.ttl(key)
        except Exception as e:
            logger.error(f"Error getting TTL for cache key {key}: {e}")
            return -1


class RateLimiter:
    """Rate limiting using Redis"""
    
    @staticmethod
    def is_rate_limited(
        key: str,
        max_attempts: int,
        window_seconds: int
    ) -> bool:
        """
        Check if a key is rate limited
        
        Args:
            key: Rate limit key (e.g., "phone_verification:user_id")
            max_attempts: Maximum attempts allowed
            window_seconds: Time window in seconds
            
        Returns:
            True if rate limited, False otherwise
        """
        try:
            cache = RedisCache.get_client()
            current = cache.incr(key)
            
            if current == 1:
                # First attempt, set expiration
                cache.expire(key, window_seconds)
            
            return current > max_attempts
        except Exception as e:
            logger.error(f"Error checking rate limit for {key}: {e}")
            return False
    
    @staticmethod
    def get_remaining_attempts(
        key: str,
        max_attempts: int
    ) -> int:
        """Get remaining attempts for a rate limited key"""
        try:
            cache = RedisCache.get_client()
            current = cache.get(key)
            
            if current is None:
                return max_attempts
            
            current_int = int(current)
            remaining = max(0, max_attempts - current_int)
            return remaining
        except Exception as e:
            logger.error(f"Error getting remaining attempts for {key}: {e}")
            return 0
    
    @staticmethod
    def reset_rate_limit(key: str) -> bool:
        """Reset rate limit for a key"""
        return RedisCache.delete(key)


class SecurityCache:
    """Security-related caching (API keys, sessions, etc.)"""
    
    @staticmethod
    def cache_api_key(key_hash: str, user_id: str, permissions: list, ttl_hours: int = 1):
        """Cache API key validation result"""
        cache_key = f"api_key:{key_hash}"
        value = {
            "user_id": user_id,
            "permissions": permissions,
            "cached_at": str(datetime.utcnow())
        }
        RedisCache.set(cache_key, value, timedelta(hours=ttl_hours))
    
    @staticmethod
    def get_cached_api_key(key_hash: str) -> Optional[dict]:
        """Get cached API key validation"""
        cache_key = f"api_key:{key_hash}"
        return RedisCache.get(cache_key)
    
    @staticmethod
    def invalidate_api_key(key_hash: str):
        """Invalidate cached API key"""
        cache_key = f"api_key:{key_hash}"
        RedisCache.delete(cache_key)
    
    @staticmethod
    def cache_security_score(user_id: str, score: int, ttl_hours: int = 1):
        """Cache security score calculation"""
        cache_key = f"security_score:{user_id}"
        RedisCache.set(cache_key, score, timedelta(hours=ttl_hours))
    
    @staticmethod
    def get_cached_security_score(user_id: str) -> Optional[int]:
        """Get cached security score"""
        cache_key = f"security_score:{user_id}"
        return RedisCache.get(cache_key)
    
    @staticmethod
    def invalidate_security_score(user_id: str):
        """Invalidate cached security score"""
        cache_key = f"security_score:{user_id}"
        RedisCache.delete(cache_key)


# Import datetime for type hints
from datetime import datetime
