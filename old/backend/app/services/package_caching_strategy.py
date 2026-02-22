"""
Package system caching strategy service
Implements caching for package definitions, client packages, and analytics
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import timedelta
from app.utils.redis_cache import RedisCache

logger = logging.getLogger(__name__)


class PackageCachingStrategy:
    """Caching strategy for package system"""
    
    # Cache key prefixes
    PACKAGE_DEFINITIONS_PREFIX = "package:definitions"
    CLIENT_PACKAGES_PREFIX = "package:client"
    ANALYTICS_PREFIX = "package:analytics"
    
    # Cache TTLs
    PACKAGE_DEFINITIONS_TTL = timedelta(minutes=5)
    CLIENT_PACKAGES_TTL = timedelta(minutes=1)
    ANALYTICS_TTL = timedelta(minutes=15)
    
    @classmethod
    def cache_package_definitions(
        cls,
        tenant_id: str,
        packages: List[Dict[str, Any]]
    ) -> bool:
        """
        Cache active package definitions for a tenant
        
        Args:
            tenant_id: Tenant ID
            packages: List of package definitions
            
        Returns:
            True if cached successfully
        """
        try:
            cache_key = f"{cls.PACKAGE_DEFINITIONS_PREFIX}:{tenant_id}"
            return RedisCache.set(
                cache_key,
                packages,
                cls.PACKAGE_DEFINITIONS_TTL
            )
        except Exception as e:
            logger.error(f"Error caching package definitions for tenant {tenant_id}: {e}")
            return False
    
    @classmethod
    def get_cached_package_definitions(
        cls,
        tenant_id: str
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get cached package definitions for a tenant
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Cached package definitions or None if not found
        """
        try:
            cache_key = f"{cls.PACKAGE_DEFINITIONS_PREFIX}:{tenant_id}"
            return RedisCache.get(cache_key)
        except Exception as e:
            logger.error(f"Error retrieving cached package definitions for tenant {tenant_id}: {e}")
            return None
    
    @classmethod
    def invalidate_package_definitions(cls, tenant_id: str) -> bool:
        """
        Invalidate cached package definitions for a tenant
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            True if invalidated successfully
        """
        try:
            cache_key = f"{cls.PACKAGE_DEFINITIONS_PREFIX}:{tenant_id}"
            return RedisCache.delete(cache_key)
        except Exception as e:
            logger.error(f"Error invalidating package definitions for tenant {tenant_id}: {e}")
            return False
    
    @classmethod
    def cache_client_packages(
        cls,
        client_id: str,
        packages: List[Dict[str, Any]]
    ) -> bool:
        """
        Cache client's package list
        
        Args:
            client_id: Client ID
            packages: List of client's packages
            
        Returns:
            True if cached successfully
        """
        try:
            cache_key = f"{cls.CLIENT_PACKAGES_PREFIX}:{client_id}"
            return RedisCache.set(
                cache_key,
                packages,
                cls.CLIENT_PACKAGES_TTL
            )
        except Exception as e:
            logger.error(f"Error caching packages for client {client_id}: {e}")
            return False
    
    @classmethod
    def get_cached_client_packages(
        cls,
        client_id: str
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get cached client packages
        
        Args:
            client_id: Client ID
            
        Returns:
            Cached client packages or None if not found
        """
        try:
            cache_key = f"{cls.CLIENT_PACKAGES_PREFIX}:{client_id}"
            return RedisCache.get(cache_key)
        except Exception as e:
            logger.error(f"Error retrieving cached packages for client {client_id}: {e}")
            return None
    
    @classmethod
    def invalidate_client_packages(cls, client_id: str) -> bool:
        """
        Invalidate cached packages for a client
        
        Args:
            client_id: Client ID
            
        Returns:
            True if invalidated successfully
        """
        try:
            cache_key = f"{cls.CLIENT_PACKAGES_PREFIX}:{client_id}"
            return RedisCache.delete(cache_key)
        except Exception as e:
            logger.error(f"Error invalidating packages for client {client_id}: {e}")
            return False
    
    @classmethod
    def cache_analytics(
        cls,
        tenant_id: str,
        analytics_type: str,
        data: Dict[str, Any]
    ) -> bool:
        """
        Cache analytics results
        
        Args:
            tenant_id: Tenant ID
            analytics_type: Type of analytics (e.g., 'sales', 'redemption', 'performance')
            data: Analytics data
            
        Returns:
            True if cached successfully
        """
        try:
            cache_key = f"{cls.ANALYTICS_PREFIX}:{tenant_id}:{analytics_type}"
            return RedisCache.set(
                cache_key,
                data,
                cls.ANALYTICS_TTL
            )
        except Exception as e:
            logger.error(f"Error caching analytics for tenant {tenant_id}: {e}")
            return False
    
    @classmethod
    def get_cached_analytics(
        cls,
        tenant_id: str,
        analytics_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached analytics results
        
        Args:
            tenant_id: Tenant ID
            analytics_type: Type of analytics
            
        Returns:
            Cached analytics data or None if not found
        """
        try:
            cache_key = f"{cls.ANALYTICS_PREFIX}:{tenant_id}:{analytics_type}"
            return RedisCache.get(cache_key)
        except Exception as e:
            logger.error(f"Error retrieving cached analytics for tenant {tenant_id}: {e}")
            return None
    
    @classmethod
    def invalidate_analytics(
        cls,
        tenant_id: str,
        analytics_type: Optional[str] = None
    ) -> bool:
        """
        Invalidate cached analytics
        
        Args:
            tenant_id: Tenant ID
            analytics_type: Optional specific analytics type to invalidate
                           If None, invalidates all analytics for tenant
            
        Returns:
            True if invalidated successfully
        """
        try:
            if analytics_type:
                cache_key = f"{cls.ANALYTICS_PREFIX}:{tenant_id}:{analytics_type}"
                return RedisCache.delete(cache_key)
            else:
                # Invalidate all analytics for tenant
                # Note: This is a simplified approach - in production, you might want
                # to use Redis SCAN to find all matching keys
                for atype in ['sales', 'redemption', 'performance', 'expiration', 'roi']:
                    cache_key = f"{cls.ANALYTICS_PREFIX}:{tenant_id}:{atype}"
                    RedisCache.delete(cache_key)
                return True
        except Exception as e:
            logger.error(f"Error invalidating analytics for tenant {tenant_id}: {e}")
            return False
    
    @classmethod
    def invalidate_all_package_caches(cls, tenant_id: str) -> bool:
        """
        Invalidate all package-related caches for a tenant
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            True if all caches invalidated successfully
        """
        try:
            success = True
            success &= cls.invalidate_package_definitions(tenant_id)
            success &= cls.invalidate_analytics(tenant_id)
            return success
        except Exception as e:
            logger.error(f"Error invalidating all package caches for tenant {tenant_id}: {e}")
            return False
    
    @classmethod
    def invalidate_client_all_caches(cls, client_id: str) -> bool:
        """
        Invalidate all caches for a specific client
        
        Args:
            client_id: Client ID
            
        Returns:
            True if all caches invalidated successfully
        """
        try:
            return cls.invalidate_client_packages(client_id)
        except Exception as e:
            logger.error(f"Error invalidating all caches for client {client_id}: {e}")
            return False
    
    @classmethod
    def get_cache_stats(cls) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache statistics
        """
        try:
            stats = {
                "package_definitions_ttl_minutes": cls.PACKAGE_DEFINITIONS_TTL.total_seconds() / 60,
                "client_packages_ttl_minutes": cls.CLIENT_PACKAGES_TTL.total_seconds() / 60,
                "analytics_ttl_minutes": cls.ANALYTICS_TTL.total_seconds() / 60,
                "credit_balances_cached": False,  # By design, not cached
            }
            return stats
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}


class PackageCacheInvalidationManager:
    """Manages cache invalidation for package operations"""
    
    @staticmethod
    def on_package_definition_created(tenant_id: str) -> None:
        """Invalidate caches when package definition is created"""
        PackageCachingStrategy.invalidate_package_definitions(tenant_id)
        logger.info(f"Invalidated package definitions cache for tenant {tenant_id}")
    
    @staticmethod
    def on_package_definition_updated(tenant_id: str) -> None:
        """Invalidate caches when package definition is updated"""
        PackageCachingStrategy.invalidate_package_definitions(tenant_id)
        logger.info(f"Invalidated package definitions cache for tenant {tenant_id}")
    
    @staticmethod
    def on_package_definition_deleted(tenant_id: str) -> None:
        """Invalidate caches when package definition is deleted"""
        PackageCachingStrategy.invalidate_package_definitions(tenant_id)
        logger.info(f"Invalidated package definitions cache for tenant {tenant_id}")
    
    @staticmethod
    def on_package_purchased(tenant_id: str, client_id: str) -> None:
        """Invalidate caches when package is purchased"""
        PackageCachingStrategy.invalidate_client_packages(client_id)
        PackageCachingStrategy.invalidate_analytics(tenant_id)
        logger.info(f"Invalidated caches for client {client_id} after package purchase")
    
    @staticmethod
    def on_package_redeemed(tenant_id: str, client_id: str) -> None:
        """Invalidate caches when package is redeemed"""
        PackageCachingStrategy.invalidate_client_packages(client_id)
        PackageCachingStrategy.invalidate_analytics(tenant_id)
        logger.info(f"Invalidated caches for client {client_id} after package redemption")
    
    @staticmethod
    def on_package_transferred(tenant_id: str, from_client_id: str, to_client_id: str) -> None:
        """Invalidate caches when package is transferred"""
        PackageCachingStrategy.invalidate_client_packages(from_client_id)
        PackageCachingStrategy.invalidate_client_packages(to_client_id)
        PackageCachingStrategy.invalidate_analytics(tenant_id)
        logger.info(f"Invalidated caches for clients {from_client_id} and {to_client_id} after transfer")
    
    @staticmethod
    def on_package_refunded(tenant_id: str, client_id: str) -> None:
        """Invalidate caches when package is refunded"""
        PackageCachingStrategy.invalidate_client_packages(client_id)
        PackageCachingStrategy.invalidate_analytics(tenant_id)
        logger.info(f"Invalidated caches for client {client_id} after package refund")
    
    @staticmethod
    def on_bulk_operation(tenant_id: str) -> None:
        """Invalidate caches after bulk operations"""
        PackageCachingStrategy.invalidate_package_definitions(tenant_id)
        PackageCachingStrategy.invalidate_analytics(tenant_id)
        logger.info(f"Invalidated all package caches for tenant {tenant_id} after bulk operation")
