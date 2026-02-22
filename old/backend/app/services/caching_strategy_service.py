"""
Multi-level caching strategy for analytics
"""
import logging
import json
from typing import Any, Optional
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)


class CachingStrategyService:
    """Service for managing multi-level caching (browser, Redis, MongoDB)"""

    def __init__(self):
        """Initialize caching strategy service"""
        self.cache_config = {
            "peak_hours": {"ttl": 300, "level": "redis"},  # 5 minutes
            "inventory": {"ttl": 600, "level": "redis"},  # 10 minutes
            "financial": {"ttl": 600, "level": "redis"},  # 10 minutes
            "clients": {"ttl": 900, "level": "redis"},  # 15 minutes
            "campaigns": {"ttl": 900, "level": "redis"},  # 15 minutes
            "predictions": {"ttl": 3600, "level": "mongodb"},  # 1 hour
            "reports": {"ttl": 1800, "level": "redis"},  # 30 minutes
            "realtime": {"ttl": 0, "level": "memory"},  # No cache
        }

    def get_cache_key(self, endpoint: str, params: dict) -> str:
        """Generate cache key from endpoint and parameters"""
        param_str = json.dumps(params, sort_keys=True, default=str)
        param_hash = hashlib.md5(param_str.encode()).hexdigest()
        return f"{endpoint}:{param_hash}"

    def get_cache_config(self, endpoint: str) -> dict:
        """Get cache configuration for an endpoint"""
        for key, config in self.cache_config.items():
            if key in endpoint:
                return config
        return {"ttl": 300, "level": "redis"}  # Default: 5 minutes in Redis

    async def get_cached_data(
        self,
        cache_key: str,
        redis_client=None,
        mongodb_client=None
    ) -> Optional[Any]:
        """Get data from cache (Redis or MongoDB)"""
        try:
            # Try Redis first
            if redis_client:
                cached = await redis_client.get(cache_key)
                if cached:
                    logger.debug(f"Cache hit (Redis): {cache_key}")
                    return json.loads(cached)
            
            # Try MongoDB
            if mongodb_client:
                cache_doc = await mongodb_client.analytics_cache.find_one(
                    {"key": cache_key}
                )
                if cache_doc:
                    # Check if expired
                    if datetime.utcnow() < cache_doc.get("expires_at", datetime.utcnow()):
                        logger.debug(f"Cache hit (MongoDB): {cache_key}")
                        return cache_doc.get("data")
                    else:
                        # Delete expired cache
                        await mongodb_client.analytics_cache.delete_one({"key": cache_key})
            
            logger.debug(f"Cache miss: {cache_key}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting cached data: {e}")
            return None

    async def set_cached_data(
        self,
        cache_key: str,
        data: Any,
        ttl: int,
        level: str = "redis",
        redis_client=None,
        mongodb_client=None
    ) -> bool:
        """Set data in cache"""
        try:
            if level == "redis" and redis_client:
                await redis_client.setex(
                    cache_key,
                    ttl,
                    json.dumps(data, default=str)
                )
                logger.debug(f"Cached in Redis: {cache_key} (TTL: {ttl}s)")
                return True
            
            elif level == "mongodb" and mongodb_client:
                await mongodb_client.analytics_cache.update_one(
                    {"key": cache_key},
                    {
                        "$set": {
                            "key": cache_key,
                            "data": data,
                            "created_at": datetime.utcnow(),
                            "expires_at": datetime.utcnow() + timedelta(seconds=ttl)
                        }
                    },
                    upsert=True
                )
                logger.debug(f"Cached in MongoDB: {cache_key} (TTL: {ttl}s)")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error setting cached data: {e}")
            return False

    async def invalidate_cache(
        self,
        pattern: str,
        redis_client=None,
        mongodb_client=None
    ) -> int:
        """Invalidate cache entries matching a pattern"""
        try:
            count = 0
            
            # Invalidate Redis
            if redis_client:
                keys = await redis_client.keys(f"{pattern}*")
                if keys:
                    count += await redis_client.delete(*keys)
                    logger.info(f"Invalidated {len(keys)} Redis cache entries")
            
            # Invalidate MongoDB
            if mongodb_client:
                result = await mongodb_client.analytics_cache.delete_many(
                    {"key": {"$regex": f"^{pattern}"}}
                )
                count += result.deleted_count
                logger.info(f"Invalidated {result.deleted_count} MongoDB cache entries")
            
            return count
            
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")
            return 0

    async def clear_all_cache(
        self,
        redis_client=None,
        mongodb_client=None
    ) -> bool:
        """Clear all analytics cache"""
        try:
            if redis_client:
                await redis_client.flushdb()
                logger.info("Cleared all Redis cache")
            
            if mongodb_client:
                await mongodb_client.analytics_cache.delete_many({})
                logger.info("Cleared all MongoDB cache")
            
            return True
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False

    async def get_cache_stats(
        self,
        redis_client=None,
        mongodb_client=None
    ) -> dict:
        """Get cache statistics"""
        try:
            stats = {
                "redis": {"entries": 0, "memory": 0},
                "mongodb": {"entries": 0}
            }
            
            if redis_client:
                info = await redis_client.info()
                stats["redis"]["memory"] = info.get("used_memory", 0)
                stats["redis"]["entries"] = await redis_client.dbsize()
            
            if mongodb_client:
                count = await mongodb_client.analytics_cache.count_documents({})
                stats["mongodb"]["entries"] = count
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}

    def get_browser_cache_headers(self, endpoint: str) -> dict:
        """Get cache headers for browser caching"""
        config = self.get_cache_config(endpoint)
        ttl = config.get("ttl", 300)
        
        if ttl == 0:
            # No cache
            return {
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        else:
            # Cache for specified TTL
            return {
                "Cache-Control": f"public, max-age={ttl}",
                "Expires": (datetime.utcnow() + timedelta(seconds=ttl)).strftime(
                    "%a, %d %b %Y %H:%M:%S GMT"
                )
            }

    async def warm_cache(
        self,
        endpoints: list,
        data_fetcher,
        redis_client=None,
        mongodb_client=None
    ) -> int:
        """Warm up cache with frequently accessed data"""
        try:
            count = 0
            for endpoint in endpoints:
                try:
                    data = await data_fetcher(endpoint)
                    config = self.get_cache_config(endpoint)
                    cache_key = self.get_cache_key(endpoint, {})
                    
                    success = await self.set_cached_data(
                        cache_key,
                        data,
                        config["ttl"],
                        config["level"],
                        redis_client,
                        mongodb_client
                    )
                    
                    if success:
                        count += 1
                        logger.info(f"Warmed cache for: {endpoint}")
                
                except Exception as e:
                    logger.error(f"Error warming cache for {endpoint}: {e}")
            
            logger.info(f"Cache warming complete: {count}/{len(endpoints)} endpoints")
            return count
            
        except Exception as e:
            logger.error(f"Error warming cache: {e}")
            return 0
