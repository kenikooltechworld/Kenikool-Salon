"""
Tests for package system caching strategy
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import timedelta
from app.services.package_caching_strategy import (
    PackageCachingStrategy,
    PackageCacheInvalidationManager
)


class TestPackageCachingStrategy:
    """Test package caching strategy"""
    
    @patch('app.services.package_caching_strategy.RedisCache')
    def test_cache_package_definitions(self, mock_redis):
        """Test caching package definitions"""
        mock_redis.set.return_value = True
        
        tenant_id = "tenant_123"
        packages = [
            {"id": "pkg_1", "name": "Package 1", "price": 100},
            {"id": "pkg_2", "name": "Package 2", "price": 200}
        ]
        
        result = PackageCachingStrategy.cache_package_definitions(tenant_id, packages)
        
        assert result is True
        mock_redis.set.assert_called_once()
        call_args = mock_redis.set.call_args
        assert "package:definitions:tenant_123" in str(call_args)
    
    @patch('app.services.package_caching_strategy.RedisCache')
    def test_get_cached_package_definitions(self, mock_redis):
        """Test retrieving cached package definitions"""
        packages = [
            {"id": "pkg_1", "name": "Package 1", "price": 100}
        ]
        mock_redis.get.return_value = packages
        
        tenant_id = "tenant_123"
        result = PackageCachingStrategy.get_cached_package_definitions(tenant_id)
        
        assert result == packages
        mock_redis.get.assert_called_once_with("package:definitions:tenant_123")
    
    @patch('app.services.package_caching_strategy.RedisCache')
    def test_get_cached_package_definitions_not_found(self, mock_redis):
        """Test retrieving non-existent cached package definitions"""
        mock_redis.get.return_value = None
        
        tenant_id = "tenant_123"
        result = PackageCachingStrategy.get_cached_package_definitions(tenant_id)
        
        assert result is None
    
    @patch('app.services.package_caching_strategy.RedisCache')
    def test_invalidate_package_definitions(self, mock_redis):
        """Test invalidating package definitions cache"""
        mock_redis.delete.return_value = True
        
        tenant_id = "tenant_123"
        result = PackageCachingStrategy.invalidate_package_definitions(tenant_id)
        
        assert result is True
        mock_redis.delete.assert_called_once_with("package:definitions:tenant_123")
    
    @patch('app.services.package_caching_strategy.RedisCache')
    def test_cache_client_packages(self, mock_redis):
        """Test caching client packages"""
        mock_redis.set.return_value = True
        
        client_id = "client_456"
        packages = [
            {"id": "purchase_1", "package_name": "Package 1", "status": "active"}
        ]
        
        result = PackageCachingStrategy.cache_client_packages(client_id, packages)
        
        assert result is True
        mock_redis.set.assert_called_once()
        call_args = mock_redis.set.call_args
        assert "package:client:client_456" in str(call_args)
    
    @patch('app.services.package_caching_strategy.RedisCache')
    def test_get_cached_client_packages(self, mock_redis):
        """Test retrieving cached client packages"""
        packages = [
            {"id": "purchase_1", "package_name": "Package 1", "status": "active"}
        ]
        mock_redis.get.return_value = packages
        
        client_id = "client_456"
        result = PackageCachingStrategy.get_cached_client_packages(client_id)
        
        assert result == packages
        mock_redis.get.assert_called_once_with("package:client:client_456")
    
    @patch('app.services.package_caching_strategy.RedisCache')
    def test_invalidate_client_packages(self, mock_redis):
        """Test invalidating client packages cache"""
        mock_redis.delete.return_value = True
        
        client_id = "client_456"
        result = PackageCachingStrategy.invalidate_client_packages(client_id)
        
        assert result is True
        mock_redis.delete.assert_called_once_with("package:client:client_456")
    
    @patch('app.services.package_caching_strategy.RedisCache')
    def test_cache_analytics(self, mock_redis):
        """Test caching analytics results"""
        mock_redis.set.return_value = True
        
        tenant_id = "tenant_123"
        analytics_type = "sales"
        data = {
            "total_revenue": 5000,
            "total_packages_sold": 50,
            "average_package_price": 100
        }
        
        result = PackageCachingStrategy.cache_analytics(tenant_id, analytics_type, data)
        
        assert result is True
        mock_redis.set.assert_called_once()
        call_args = mock_redis.set.call_args
        assert "package:analytics:tenant_123:sales" in str(call_args)
    
    @patch('app.services.package_caching_strategy.RedisCache')
    def test_get_cached_analytics(self, mock_redis):
        """Test retrieving cached analytics"""
        data = {
            "total_revenue": 5000,
            "total_packages_sold": 50
        }
        mock_redis.get.return_value = data
        
        tenant_id = "tenant_123"
        analytics_type = "sales"
        result = PackageCachingStrategy.get_cached_analytics(tenant_id, analytics_type)
        
        assert result == data
        mock_redis.get.assert_called_once_with("package:analytics:tenant_123:sales")
    
    @patch('app.services.package_caching_strategy.RedisCache')
    def test_invalidate_analytics_specific_type(self, mock_redis):
        """Test invalidating specific analytics type"""
        mock_redis.delete.return_value = True
        
        tenant_id = "tenant_123"
        analytics_type = "sales"
        result = PackageCachingStrategy.invalidate_analytics(tenant_id, analytics_type)
        
        assert result is True
        mock_redis.delete.assert_called_once_with("package:analytics:tenant_123:sales")
    
    @patch('app.services.package_caching_strategy.RedisCache')
    def test_invalidate_analytics_all_types(self, mock_redis):
        """Test invalidating all analytics types for tenant"""
        mock_redis.delete.return_value = True
        
        tenant_id = "tenant_123"
        result = PackageCachingStrategy.invalidate_analytics(tenant_id)
        
        assert result is True
        # Should call delete for each analytics type
        assert mock_redis.delete.call_count >= 5
    
    @patch('app.services.package_caching_strategy.RedisCache')
    def test_invalidate_all_package_caches(self, mock_redis):
        """Test invalidating all package caches for tenant"""
        mock_redis.delete.return_value = True
        
        tenant_id = "tenant_123"
        result = PackageCachingStrategy.invalidate_all_package_caches(tenant_id)
        
        assert result is True
        # Should call delete multiple times
        assert mock_redis.delete.call_count > 0
    
    @patch('app.services.package_caching_strategy.RedisCache')
    def test_invalidate_client_all_caches(self, mock_redis):
        """Test invalidating all caches for client"""
        mock_redis.delete.return_value = True
        
        client_id = "client_456"
        result = PackageCachingStrategy.invalidate_client_all_caches(client_id)
        
        assert result is True
        mock_redis.delete.assert_called_once_with("package:client:client_456")
    
    def test_get_cache_stats(self):
        """Test getting cache statistics"""
        stats = PackageCachingStrategy.get_cache_stats()
        
        assert "package_definitions_ttl_minutes" in stats
        assert "client_packages_ttl_minutes" in stats
        assert "analytics_ttl_minutes" in stats
        assert "credit_balances_cached" in stats
        
        # Verify TTL values
        assert stats["package_definitions_ttl_minutes"] == 5
        assert stats["client_packages_ttl_minutes"] == 1
        assert stats["analytics_ttl_minutes"] == 15
        assert stats["credit_balances_cached"] is False
    
    @patch('app.services.package_caching_strategy.RedisCache')
    def test_cache_error_handling(self, mock_redis):
        """Test error handling in caching operations"""
        mock_redis.set.side_effect = Exception("Redis connection error")
        
        tenant_id = "tenant_123"
        packages = [{"id": "pkg_1"}]
        
        result = PackageCachingStrategy.cache_package_definitions(tenant_id, packages)
        
        assert result is False
    
    @patch('app.services.package_caching_strategy.RedisCache')
    def test_get_error_handling(self, mock_redis):
        """Test error handling in get operations"""
        mock_redis.get.side_effect = Exception("Redis connection error")
        
        tenant_id = "tenant_123"
        result = PackageCachingStrategy.get_cached_package_definitions(tenant_id)
        
        assert result is None


class TestPackageCacheInvalidationManager:
    """Test cache invalidation manager"""
    
    @patch('app.services.package_caching_strategy.PackageCachingStrategy')
    def test_on_package_definition_created(self, mock_strategy):
        """Test cache invalidation on package definition creation"""
        tenant_id = "tenant_123"
        
        PackageCacheInvalidationManager.on_package_definition_created(tenant_id)
        
        mock_strategy.invalidate_package_definitions.assert_called_once_with(tenant_id)
    
    @patch('app.services.package_caching_strategy.PackageCachingStrategy')
    def test_on_package_definition_updated(self, mock_strategy):
        """Test cache invalidation on package definition update"""
        tenant_id = "tenant_123"
        
        PackageCacheInvalidationManager.on_package_definition_updated(tenant_id)
        
        mock_strategy.invalidate_package_definitions.assert_called_once_with(tenant_id)
    
    @patch('app.services.package_caching_strategy.PackageCachingStrategy')
    def test_on_package_definition_deleted(self, mock_strategy):
        """Test cache invalidation on package definition deletion"""
        tenant_id = "tenant_123"
        
        PackageCacheInvalidationManager.on_package_definition_deleted(tenant_id)
        
        mock_strategy.invalidate_package_definitions.assert_called_once_with(tenant_id)
    
    @patch('app.services.package_caching_strategy.PackageCachingStrategy')
    def test_on_package_purchased(self, mock_strategy):
        """Test cache invalidation on package purchase"""
        tenant_id = "tenant_123"
        client_id = "client_456"
        
        PackageCacheInvalidationManager.on_package_purchased(tenant_id, client_id)
        
        mock_strategy.invalidate_client_packages.assert_called_once_with(client_id)
        mock_strategy.invalidate_analytics.assert_called_once_with(tenant_id)
    
    @patch('app.services.package_caching_strategy.PackageCachingStrategy')
    def test_on_package_redeemed(self, mock_strategy):
        """Test cache invalidation on package redemption"""
        tenant_id = "tenant_123"
        client_id = "client_456"
        
        PackageCacheInvalidationManager.on_package_redeemed(tenant_id, client_id)
        
        mock_strategy.invalidate_client_packages.assert_called_once_with(client_id)
        mock_strategy.invalidate_analytics.assert_called_once_with(tenant_id)
    
    @patch('app.services.package_caching_strategy.PackageCachingStrategy')
    def test_on_package_transferred(self, mock_strategy):
        """Test cache invalidation on package transfer"""
        tenant_id = "tenant_123"
        from_client_id = "client_456"
        to_client_id = "client_789"
        
        PackageCacheInvalidationManager.on_package_transferred(
            tenant_id, from_client_id, to_client_id
        )
        
        assert mock_strategy.invalidate_client_packages.call_count == 2
        mock_strategy.invalidate_analytics.assert_called_once_with(tenant_id)
    
    @patch('app.services.package_caching_strategy.PackageCachingStrategy')
    def test_on_package_refunded(self, mock_strategy):
        """Test cache invalidation on package refund"""
        tenant_id = "tenant_123"
        client_id = "client_456"
        
        PackageCacheInvalidationManager.on_package_refunded(tenant_id, client_id)
        
        mock_strategy.invalidate_client_packages.assert_called_once_with(client_id)
        mock_strategy.invalidate_analytics.assert_called_once_with(tenant_id)
    
    @patch('app.services.package_caching_strategy.PackageCachingStrategy')
    def test_on_bulk_operation(self, mock_strategy):
        """Test cache invalidation on bulk operations"""
        tenant_id = "tenant_123"
        
        PackageCacheInvalidationManager.on_bulk_operation(tenant_id)
        
        mock_strategy.invalidate_package_definitions.assert_called_once_with(tenant_id)
        mock_strategy.invalidate_analytics.assert_called_once_with(tenant_id)


class TestCacheTTLValues:
    """Test cache TTL values match design specifications"""
    
    def test_package_definitions_ttl(self):
        """Test package definitions cache TTL is 5 minutes"""
        ttl = PackageCachingStrategy.PACKAGE_DEFINITIONS_TTL
        assert ttl == timedelta(minutes=5)
    
    def test_client_packages_ttl(self):
        """Test client packages cache TTL is 1 minute"""
        ttl = PackageCachingStrategy.CLIENT_PACKAGES_TTL
        assert ttl == timedelta(minutes=1)
    
    def test_analytics_ttl(self):
        """Test analytics cache TTL is 15 minutes"""
        ttl = PackageCachingStrategy.ANALYTICS_TTL
        assert ttl == timedelta(minutes=15)


class TestCacheKeyFormats:
    """Test cache key format consistency"""
    
    def test_package_definitions_key_format(self):
        """Test package definitions cache key format"""
        tenant_id = "tenant_123"
        expected_prefix = "package:definitions"
        
        # Verify the prefix is used correctly
        assert PackageCachingStrategy.PACKAGE_DEFINITIONS_PREFIX == expected_prefix
    
    def test_client_packages_key_format(self):
        """Test client packages cache key format"""
        client_id = "client_456"
        expected_prefix = "package:client"
        
        # Verify the prefix is used correctly
        assert PackageCachingStrategy.CLIENT_PACKAGES_PREFIX == expected_prefix
    
    def test_analytics_key_format(self):
        """Test analytics cache key format"""
        tenant_id = "tenant_123"
        analytics_type = "sales"
        expected_prefix = "package:analytics"
        
        # Verify the prefix is used correctly
        assert PackageCachingStrategy.ANALYTICS_PREFIX == expected_prefix
