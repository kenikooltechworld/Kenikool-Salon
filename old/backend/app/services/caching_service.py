"""
Caching Service for Performance Optimization - Task 22
"""
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
import json
import logging

from app.database import Database

logger = logging.getLogger(__name__)


class CachingService:
    """Service for caching frequently accessed data"""
    
    @staticmethod
    async def get_cached(
        key: str,
        salon_id: str,
        ttl_minutes: int = 30
    ) -> Optional[Any]:
        """Get cached value - Requirements: 20"""
        db = Database.get_db()
        
        cache_entry = db.cache.find_one({
            "key": key,
            "tenant_id": salon_id,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if cache_entry:
            logger.debug(f"Cache hit for key: {key}")
            return json.loads(cache_entry.get("value", "{}"))
        
        logger.debug(f"Cache miss for key: {key}")
        return None
    
    @staticmethod
    async def set_cached(
        key: str,
        value: Any,
        salon_id: str,
        ttl_minutes: int = 30
    ) -> bool:
        """Set cached value - Requirements: 20"""
        db = Database.get_db()
        
        cache_entry = {
            "key": key,
            "tenant_id": salon_id,
            "value": json.dumps(value) if not isinstance(value, str) else value,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=ttl_minutes)
        }
        
        result = db.cache.update_one(
            {"key": key, "tenant_id": salon_id},
            {"$set": cache_entry},
            upsert=True
        )
        
        logger.debug(f"Cached value for key: {key}")
        return result.modified_count > 0 or result.upserted_id is not None
    
    @staticmethod
    async def invalidate_cache(
        key: str,
        salon_id: str
    ) -> bool:
        """Invalidate cached value - Requirements: 20"""
        db = Database.get_db()
        
        result = db.cache.delete_one({
            "key": key,
            "tenant_id": salon_id
        })
        
        logger.debug(f"Invalidated cache for key: {key}")
        return result.deleted_count > 0
    
    @staticmethod
    async def invalidate_pattern(
        pattern: str,
        salon_id: str
    ) -> int:
        """Invalidate cache entries matching pattern - Requirements: 20"""
        db = Database.get_db()
        
        result = db.cache.delete_many({
            "key": {"$regex": pattern},
            "tenant_id": salon_id
        })
        
        logger.debug(f"Invalidated {result.deleted_count} cache entries matching pattern: {pattern}")
        return result.deleted_count
    
    @staticmethod
    async def cleanup_expired_cache() -> int:
        """Clean up expired cache entries - Requirements: 20"""
        db = Database.get_db()
        
        result = db.cache.delete_many({
            "expires_at": {"$lt": datetime.utcnow()}
        })
        
        logger.info(f"Cleaned up {result.deleted_count} expired cache entries")
        return result.deleted_count
    
    @staticmethod
    async def get_cache_stats(salon_id: str) -> Dict:
        """Get cache statistics - Requirements: 20"""
        db = Database.get_db()
        
        total_entries = db.cache.count_documents({"tenant_id": salon_id})
        expired_entries = db.cache.count_documents({
            "tenant_id": salon_id,
            "expires_at": {"$lt": datetime.utcnow()}
        })
        
        return {
            "total_entries": total_entries,
            "expired_entries": expired_entries,
            "active_entries": total_entries - expired_entries
        }


caching_service = CachingService()
