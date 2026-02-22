from typing import Optional, Any, List, Dict
from datetime import datetime, timedelta
import json
from app.cache import redis_client
from app.context import get_tenant_id


class CacheOptimizationService:
    """Service for performance optimization through caching"""

    # Cache TTLs (in seconds)
    CACHE_TTL = {
        'services': 3600,  # 1 hour
        'staff': 600,  # 10 minutes
        'availability': 60,  # 1 minute
        'permissions': 300,  # 5 minutes
        'customers': 600,  # 10 minutes
        'appointments': 300,  # 5 minutes
        'inventory': 1800,  # 30 minutes
    }

    @staticmethod
    def get_cache_key(resource_type: str, resource_id: Optional[str] = None, tenant_id: Optional[str] = None) -> str:
        """Generate cache key"""
        if not tenant_id:
            tenant_id = get_tenant_id()
        
        if resource_id:
            return f"cache:{tenant_id}:{resource_type}:{resource_id}"
        return f"cache:{tenant_id}:{resource_type}"

    @staticmethod
    def get(key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception:
            return None

    @staticmethod
    def set(key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            if ttl is None:
                ttl = 3600  # Default 1 hour
            
            redis_client.setex(key, ttl, json.dumps(value, default=str))
            return True
        except Exception:
            return False

    @staticmethod
    def delete(key: str) -> bool:
        """Delete value from cache"""
        try:
            redis_client.delete(key)
            return True
        except Exception:
            return False

    @staticmethod
    def invalidate_pattern(pattern: str) -> int:
        """Invalidate all keys matching pattern"""
        try:
            keys = redis_client.keys(pattern)
            if keys:
                return redis_client.delete(*keys)
            return 0
        except Exception:
            return 0

    @staticmethod
    def cache_services(services: List[Dict[str, Any]], tenant_id: Optional[str] = None) -> bool:
        """Cache services list"""
        key = CacheOptimizationService.get_cache_key('services', tenant_id=tenant_id)
        return CacheOptimizationService.set(
            key,
            services,
            ttl=CacheOptimizationService.CACHE_TTL['services'],
        )

    @staticmethod
    def get_cached_services(tenant_id: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        """Get cached services"""
        key = CacheOptimizationService.get_cache_key('services', tenant_id=tenant_id)
        return CacheOptimizationService.get(key)

    @staticmethod
    def invalidate_services(tenant_id: Optional[str] = None) -> int:
        """Invalidate services cache"""
        pattern = CacheOptimizationService.get_cache_key('services', tenant_id=tenant_id) + "*"
        return CacheOptimizationService.invalidate_pattern(pattern)

    @staticmethod
    def cache_staff(staff: List[Dict[str, Any]], tenant_id: Optional[str] = None) -> bool:
        """Cache staff list"""
        key = CacheOptimizationService.get_cache_key('staff', tenant_id=tenant_id)
        return CacheOptimizationService.set(
            key,
            staff,
            ttl=CacheOptimizationService.CACHE_TTL['staff'],
        )

    @staticmethod
    def get_cached_staff(tenant_id: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        """Get cached staff"""
        key = CacheOptimizationService.get_cache_key('staff', tenant_id=tenant_id)
        return CacheOptimizationService.get(key)

    @staticmethod
    def invalidate_staff(tenant_id: Optional[str] = None) -> int:
        """Invalidate staff cache"""
        pattern = CacheOptimizationService.get_cache_key('staff', tenant_id=tenant_id) + "*"
        return CacheOptimizationService.invalidate_pattern(pattern)

    @staticmethod
    def cache_availability(
        staff_id: str,
        date: str,
        availability: List[Dict[str, Any]],
        tenant_id: Optional[str] = None,
    ) -> bool:
        """Cache availability slots"""
        key = f"{CacheOptimizationService.get_cache_key('availability', tenant_id=tenant_id)}:{staff_id}:{date}"
        return CacheOptimizationService.set(
            key,
            availability,
            ttl=CacheOptimizationService.CACHE_TTL['availability'],
        )

    @staticmethod
    def get_cached_availability(
        staff_id: str,
        date: str,
        tenant_id: Optional[str] = None,
    ) -> Optional[List[Dict[str, Any]]]:
        """Get cached availability"""
        key = f"{CacheOptimizationService.get_cache_key('availability', tenant_id=tenant_id)}:{staff_id}:{date}"
        return CacheOptimizationService.get(key)

    @staticmethod
    def invalidate_availability(staff_id: Optional[str] = None, tenant_id: Optional[str] = None) -> int:
        """Invalidate availability cache"""
        if staff_id:
            pattern = f"{CacheOptimizationService.get_cache_key('availability', tenant_id=tenant_id)}:{staff_id}:*"
        else:
            pattern = CacheOptimizationService.get_cache_key('availability', tenant_id=tenant_id) + "*"
        
        return CacheOptimizationService.invalidate_pattern(pattern)

    @staticmethod
    def cache_permissions(user_id: str, permissions: List[str], tenant_id: Optional[str] = None) -> bool:
        """Cache user permissions"""
        key = f"{CacheOptimizationService.get_cache_key('permissions', tenant_id=tenant_id)}:{user_id}"
        return CacheOptimizationService.set(
            key,
            permissions,
            ttl=CacheOptimizationService.CACHE_TTL['permissions'],
        )

    @staticmethod
    def get_cached_permissions(user_id: str, tenant_id: Optional[str] = None) -> Optional[List[str]]:
        """Get cached permissions"""
        key = f"{CacheOptimizationService.get_cache_key('permissions', tenant_id=tenant_id)}:{user_id}"
        return CacheOptimizationService.get(key)

    @staticmethod
    def invalidate_permissions(user_id: Optional[str] = None, tenant_id: Optional[str] = None) -> int:
        """Invalidate permissions cache"""
        if user_id:
            key = f"{CacheOptimizationService.get_cache_key('permissions', tenant_id=tenant_id)}:{user_id}"
            return CacheOptimizationService.delete(key)
        else:
            pattern = CacheOptimizationService.get_cache_key('permissions', tenant_id=tenant_id) + "*"
            return CacheOptimizationService.invalidate_pattern(pattern)

    @staticmethod
    def get_cache_statistics(tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """Get cache statistics"""
        if not tenant_id:
            tenant_id = get_tenant_id()
        
        try:
            info = redis_client.info('stats')
            
            # Count keys by type
            pattern = f"cache:{tenant_id}:*"
            keys = redis_client.keys(pattern)
            
            key_types = {}
            for key in keys:
                key_str = key.decode() if isinstance(key, bytes) else key
                parts = key_str.split(':')
                if len(parts) >= 3:
                    resource_type = parts[2]
                    key_types[resource_type] = key_types.get(resource_type, 0) + 1
            
            return {
                "total_keys": len(keys),
                "key_types": key_types,
                "hits": info.get('keyspace_hits', 0),
                "misses": info.get('keyspace_misses', 0),
                "hit_rate": info.get('keyspace_hits', 0) / (info.get('keyspace_hits', 0) + info.get('keyspace_misses', 1)),
            }
        except Exception:
            return {
                "total_keys": 0,
                "key_types": {},
                "hits": 0,
                "misses": 0,
                "hit_rate": 0,
            }

    @staticmethod
    def clear_all_cache(tenant_id: Optional[str] = None) -> int:
        """Clear all cache for tenant"""
        if not tenant_id:
            tenant_id = get_tenant_id()
        
        pattern = f"cache:{tenant_id}:*"
        return CacheOptimizationService.invalidate_pattern(pattern)

    @staticmethod
    def warm_cache(tenant_id: Optional[str] = None) -> Dict[str, bool]:
        """Warm cache with frequently accessed data"""
        # This would be called during off-peak hours
        # Implementation depends on your data loading strategy
        return {
            "services": True,
            "staff": True,
            "permissions": True,
        }
