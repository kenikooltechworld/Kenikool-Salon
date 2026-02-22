"""
Simple caching utility for analytics data
"""
import json
import logging
from typing import Optional, Any
from functools import wraps
from app.config import settings

logger = logging.getLogger(__name__)

# Try to import redis, but make it optional
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available - caching disabled")


class AnalyticsCache:
    """Cache for analytics data with Redis backend"""
    
    def __init__(self):
        self.redis_url = settings.REDIS_URL
        self.redis_client: Optional[Any] = None
        self.default_ttl = 300  # 5 minutes default TTL
        self.enabled = REDIS_AVAILABLE
        
    async def connect(self):
        """Connect to Redis"""
        if not self.enabled:
            return
            
        if self.redis_client is None:
            try:
                self.redis_client = await redis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=2,
                    socket_timeout=2
                )
                logger.info("Analytics cache connected to Redis")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}. Caching disabled.")
                self.redis_client = None
                self.enabled = False
    
    async def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        if not self.enabled:
            return None
            
        try:
            await self.connect()
            if self.redis_client is None:
                return None
                
            data = await self.redis_client.get(f"analytics:{key}")
            if data:
                logger.debug(f"Cache hit: {key}")
                return json.loads(data)
            
            logger.debug(f"Cache miss: {key}")
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set cached value with TTL"""
        if not self.enabled:
            return
            
        try:
            await self.connect()
            if self.redis_client is None:
                return
                
            ttl = ttl or self.default_ttl
            await self.redis_client.setex(
                f"analytics:{key}",
                ttl,
                json.dumps(value)
            )
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    async def delete(self, key: str):
        """Delete cached value"""
        if not self.enabled:
            return
            
        try:
            await self.connect()
            if self.redis_client is None:
                return
                
            await self.redis_client.delete(f"analytics:{key}")
            logger.debug(f"Cache deleted: {key}")
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
    
    async def clear_service_cache(self, service_id: str, tenant_id: str):
        """Clear all cache entries for a service"""
        if not self.enabled:
            return
            
        try:
            await self.connect()
            if self.redis_client is None:
                return
                
            # Delete all keys matching the pattern
            pattern = f"analytics:{tenant_id}:service:{service_id}:*"
            cursor = 0
            while True:
                cursor, keys = await self.redis_client.scan(
                    cursor, match=pattern, count=100
                )
                if keys:
                    await self.redis_client.delete(*keys)
                if cursor == 0:
                    break
            
            logger.info(f"Cleared cache for service {service_id}")
        except Exception as e:
            logger.error(f"Cache clear error: {e}")


# Global cache instance
analytics_cache = AnalyticsCache()


def cache_key(tenant_id: str, service_id: str, suffix: str) -> str:
    """Generate cache key for analytics data"""
    return f"{tenant_id}:service:{service_id}:{suffix}"


class ServiceCache:
    """Cache for service data with Redis backend"""
    
    def __init__(self):
        self.redis_url = settings.REDIS_URL
        self.redis_client: Optional[Any] = None
        self.default_ttl = 600  # 10 minutes default TTL for service data
        self.enabled = REDIS_AVAILABLE
        
    async def connect(self):
        """Connect to Redis"""
        if not self.enabled:
            return
            
        if self.redis_client is None:
            try:
                self.redis_client = await redis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=2,
                    socket_timeout=2
                )
                logger.info("Service cache connected to Redis")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}. Caching disabled.")
                self.redis_client = None
                self.enabled = False
    
    async def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        if not self.enabled:
            return None
            
        try:
            await self.connect()
            if self.redis_client is None:
                return None
                
            data = await self.redis_client.get(f"service:{key}")
            if data:
                logger.debug(f"Service cache hit: {key}")
                return json.loads(data)
            
            logger.debug(f"Service cache miss: {key}")
            return None
        except Exception as e:
            logger.error(f"Service cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set cached value with TTL"""
        if not self.enabled:
            return
            
        try:
            await self.connect()
            if self.redis_client is None:
                return
                
            ttl = ttl or self.default_ttl
            await self.redis_client.setex(
                f"service:{key}",
                ttl,
                json.dumps(value, default=str)  # default=str handles datetime serialization
            )
            logger.debug(f"Service cache set: {key} (TTL: {ttl}s)")
        except Exception as e:
            logger.error(f"Service cache set error: {e}")
    
    async def delete(self, key: str):
        """Delete cached value"""
        if not self.enabled:
            return
            
        try:
            await self.connect()
            if self.redis_client is None:
                return
                
            await self.redis_client.delete(f"service:{key}")
            logger.debug(f"Service cache deleted: {key}")
        except Exception as e:
            logger.error(f"Service cache delete error: {e}")
    
    async def invalidate_service(self, service_id: str, tenant_id: str):
        """Invalidate all cache entries for a service"""
        if not self.enabled:
            return
            
        try:
            await self.connect()
            if self.redis_client is None:
                return
                
            # Delete all keys matching the pattern
            patterns = [
                f"service:{tenant_id}:service:{service_id}:*",
                f"service:{tenant_id}:services:*",  # Invalidate list caches
            ]
            
            for pattern in patterns:
                cursor = 0
                while True:
                    cursor, keys = await self.redis_client.scan(
                        cursor, match=pattern, count=100
                    )
                    if keys:
                        await self.redis_client.delete(*keys)
                    if cursor == 0:
                        break
            
            logger.info(f"Invalidated cache for service {service_id}")
        except Exception as e:
            logger.error(f"Service cache invalidation error: {e}")


# Global cache instances
service_cache = ServiceCache()



class ClientAnalyticsCache:
    """Cache for client analytics data with Redis backend"""
    
    def __init__(self):
        self.redis_url = settings.REDIS_URL
        self.redis_client: Optional[Any] = None
        self.default_ttl = 3600  # 1 hour default TTL for client analytics
        self.enabled = REDIS_AVAILABLE
        
    async def connect(self):
        """Connect to Redis"""
        if not self.enabled:
            return
            
        if self.redis_client is None:
            try:
                self.redis_client = await redis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=2,
                    socket_timeout=2
                )
                logger.info("Client analytics cache connected to Redis")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}. Caching disabled.")
                self.redis_client = None
                self.enabled = False
    
    async def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        if not self.enabled:
            return None
            
        try:
            await self.connect()
            if self.redis_client is None:
                return None
                
            data = await self.redis_client.get(f"client_analytics:{key}")
            if data:
                logger.debug(f"Client analytics cache hit: {key}")
                return json.loads(data)
            
            logger.debug(f"Client analytics cache miss: {key}")
            return None
        except Exception as e:
            logger.error(f"Client analytics cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set cached value with TTL"""
        if not self.enabled:
            return
            
        try:
            await self.connect()
            if self.redis_client is None:
                return
                
            ttl = ttl or self.default_ttl
            await self.redis_client.setex(
                f"client_analytics:{key}",
                ttl,
                json.dumps(value, default=str)  # default=str handles datetime serialization
            )
            logger.debug(f"Client analytics cache set: {key} (TTL: {ttl}s)")
        except Exception as e:
            logger.error(f"Client analytics cache set error: {e}")
    
    async def delete(self, key: str):
        """Delete cached value"""
        if not self.enabled:
            return
            
        try:
            await self.connect()
            if self.redis_client is None:
                return
                
            await self.redis_client.delete(f"client_analytics:{key}")
            logger.debug(f"Client analytics cache deleted: {key}")
        except Exception as e:
            logger.error(f"Client analytics cache delete error: {e}")
    
    async def invalidate_client(self, client_id: str, tenant_id: str):
        """Invalidate all cache entries for a client"""
        if not self.enabled:
            return
            
        try:
            await self.connect()
            if self.redis_client is None:
                return
                
            # Delete all keys matching the pattern
            patterns = [
                f"client_analytics:{tenant_id}:client:{client_id}:*",
                f"client_analytics:{tenant_id}:global",  # Invalidate global analytics
            ]
            
            for pattern in patterns:
                cursor = 0
                while True:
                    cursor, keys = await self.redis_client.scan(
                        cursor, match=pattern, count=100
                    )
                    if keys:
                        await self.redis_client.delete(*keys)
                    if cursor == 0:
                        break
            
            logger.info(f"Invalidated cache for client {client_id}")
        except Exception as e:
            logger.error(f"Client analytics cache invalidation error: {e}")


# Global cache instance
client_analytics_cache = ClientAnalyticsCache()
