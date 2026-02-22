"""
Tests for API key service - API key generation, management, and validation
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from bson import ObjectId

from app.services.api_key_service import (
    api_key_service, UnauthorizedException, BadRequestException, NotFoundException
)


class TestAPIKeyGeneration:
    """Tests for API key generation"""

    @pytest.mark.asyncio
    async def test_create_api_key_success(self, db_mock):
        """Test successful API key creation"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        key_id = ObjectId()
        
        db_mock.api_keys.insert_one.return_value = Mock(inserted_id=key_id)
        
        plain_key, metadata = await api_key_service.create_api_key(
            user_id, tenant_id, "Test Key", None, ["read:bookings"]
        )
        
        assert plain_key is not None
        assert len(plain_key) == 64  # 32 bytes hex encoded
        assert metadata["id"] == str(key_id)
        assert metadata["name"] == "Test Key"
        assert metadata["key"] == plain_key
        assert "sk_live_" in metadata["key_prefix"]
        db_mock.api_keys.insert_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_api_key_invalid_name(self, db_mock):
        """Test API key creation with invalid name"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        
        with pytest.raises(BadRequestException):
            await api_key_service.create_api_key(
                user_id, tenant_id, "", None, []
            )

    @pytest.mark.asyncio
    async def test_create_api_key_name_too_long(self, db_mock):
        """Test API key creation with name too long"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        
        with pytest.raises(BadRequestException):
            await api_key_service.create_api_key(
                user_id, tenant_id, "x" * 101, None, []
            )

    @pytest.mark.asyncio
    async def test_create_api_key_with_expiration(self, db_mock):
        """Test API key creation with expiration"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        key_id = ObjectId()
        expires_at = datetime.utcnow() + timedelta(days=30)
        
        db_mock.api_keys.insert_one.return_value = Mock(inserted_id=key_id)
        
        plain_key, metadata = await api_key_service.create_api_key(
            user_id, tenant_id, "Test Key", expires_at, []
        )
        
        assert metadata["expires_at"] == expires_at
        db_mock.api_keys.insert_one.assert_called_once()


class TestAPIKeyListing:
    """Tests for API key listing"""

    @pytest.mark.asyncio
    async def test_list_api_keys_success(self, db_mock):
        """Test successful API key listing"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        
        keys = [
            {
                "_id": ObjectId(),
                "user_id": user_id,
                "tenant_id": tenant_id,
                "name": "Key 1",
                "key_prefix": "sk_live_abc123",
                "created_at": datetime.utcnow(),
                "last_used": None,
                "expires_at": None,
                "is_active": True
            }
        ]
        
        db_mock.api_keys.find.return_value.sort.return_value = keys
        
        result = await api_key_service.list_api_keys(user_id, tenant_id)
        
        assert len(result) == 1
        assert result[0]["name"] == "Key 1"
        assert result[0]["key_prefix"] == "sk_live_abc123"

    @pytest.mark.asyncio
    async def test_list_api_keys_empty(self, db_mock):
        """Test listing API keys when none exist"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        
        db_mock.api_keys.find.return_value.sort.return_value = []
        
        result = await api_key_service.list_api_keys(user_id, tenant_id)
        
        assert result == []


class TestAPIKeyRevocation:
    """Tests for API key revocation"""

    @pytest.mark.asyncio
    async def test_revoke_api_key_success(self, db_mock):
        """Test successful API key revocation"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        key_id = str(ObjectId())
        
        db_mock.api_keys.update_one.return_value = Mock(matched_count=1)
        
        with patch('app.services.api_key_service.RedisCache') as mock_cache:
            result = await api_key_service.revoke_api_key(user_id, tenant_id, key_id)
        
        assert result is True
        db_mock.api_keys.update_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_revoke_api_key_not_found(self, db_mock):
        """Test revoking non-existent API key"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        key_id = str(ObjectId())
        
        db_mock.api_keys.update_one.return_value = Mock(matched_count=0)
        
        with pytest.raises(NotFoundException):
            await api_key_service.revoke_api_key(user_id, tenant_id, key_id)


class TestAPIKeyValidation:
    """Tests for API key validation"""

    @pytest.mark.asyncio
    async def test_validate_api_key_success(self, db_mock):
        """Test successful API key validation"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        key_id = str(ObjectId())
        plain_key = "a" * 64
        
        api_key = {
            "_id": ObjectId(key_id),
            "user_id": user_id,
            "tenant_id": tenant_id,
            "key_hash": __import__("hashlib").sha256(plain_key.encode()).hexdigest(),
            "is_active": True,
            "expires_at": None,
            "permissions": ["read:bookings"]
        }
        
        db_mock.api_keys.find_one.return_value = api_key
        
        with patch('app.services.api_key_service.RedisCache') as mock_cache:
            mock_cache.get.return_value = None
            mock_cache.set = Mock()
            
            result = await api_key_service.validate_api_key(plain_key)
        
        assert result["user_id"] == user_id
        assert result["tenant_id"] == tenant_id
        assert result["permissions"] == ["read:bookings"]

    @pytest.mark.asyncio
    async def test_validate_api_key_invalid(self, db_mock):
        """Test validation with invalid API key"""
        db_mock.api_keys.find_one.return_value = None
        
        with patch('app.services.api_key_service.RedisCache') as mock_cache:
            mock_cache.get.return_value = None
            
            with pytest.raises(UnauthorizedException):
                await api_key_service.validate_api_key("invalid_key")

    @pytest.mark.asyncio
    async def test_validate_api_key_expired(self, db_mock):
        """Test validation with expired API key"""
        plain_key = "a" * 64
        
        api_key = {
            "_id": ObjectId(),
            "user_id": str(ObjectId()),
            "tenant_id": str(ObjectId()),
            "key_hash": __import__("hashlib").sha256(plain_key.encode()).hexdigest(),
            "is_active": True,
            "expires_at": datetime.utcnow() - timedelta(days=1),
            "permissions": []
        }
        
        db_mock.api_keys.find_one.return_value = api_key
        
        with patch('app.services.api_key_service.RedisCache') as mock_cache:
            mock_cache.get.return_value = None
            
            with pytest.raises(UnauthorizedException):
                await api_key_service.validate_api_key(plain_key)

    @pytest.mark.asyncio
    async def test_validate_api_key_cached(self, db_mock):
        """Test validation with cached result"""
        plain_key = "a" * 64
        cached_result = {
            "user_id": str(ObjectId()),
            "tenant_id": str(ObjectId()),
            "permissions": ["read:bookings"]
        }
        
        with patch('app.services.api_key_service.RedisCache') as mock_cache:
            mock_cache.get.return_value = cached_result
            
            result = await api_key_service.validate_api_key(plain_key)
        
        assert result == cached_result
        db_mock.api_keys.find_one.assert_not_called()


class TestAPIKeyMetadataUpdate:
    """Tests for API key metadata updates"""

    @pytest.mark.asyncio
    async def test_update_api_key_metadata_success(self, db_mock):
        """Test successful API key metadata update"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        key_id = str(ObjectId())
        
        updated_key = {
            "_id": ObjectId(key_id),
            "user_id": user_id,
            "tenant_id": tenant_id,
            "name": "Updated Key",
            "key_prefix": "sk_live_abc123",
            "created_at": datetime.utcnow(),
            "last_used": None,
            "expires_at": datetime.utcnow() + timedelta(days=30),
            "permissions": ["read:bookings", "write:clients"],
            "is_active": True
        }
        
        db_mock.api_keys.find_one_and_update.return_value = updated_key
        
        with patch('app.services.api_key_service.RedisCache') as mock_cache:
            result = await api_key_service.update_api_key_metadata(
                user_id, tenant_id, key_id,
                name="Updated Key",
                permissions=["read:bookings", "write:clients"]
            )
        
        assert result["name"] == "Updated Key"
        assert result["permissions"] == ["read:bookings", "write:clients"]

    @pytest.mark.asyncio
    async def test_update_api_key_metadata_not_found(self, db_mock):
        """Test updating non-existent API key"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        key_id = str(ObjectId())
        
        db_mock.api_keys.find_one_and_update.return_value = None
        
        with pytest.raises(NotFoundException):
            await api_key_service.update_api_key_metadata(
                user_id, tenant_id, key_id, name="Updated"
            )

    @pytest.mark.asyncio
    async def test_update_api_key_metadata_no_fields(self, db_mock):
        """Test updating with no fields"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        key_id = str(ObjectId())
        
        with pytest.raises(BadRequestException):
            await api_key_service.update_api_key_metadata(
                user_id, tenant_id, key_id
            )


class TestAPIKeyCleanup:
    """Tests for API key cleanup"""

    @pytest.mark.asyncio
    async def test_cleanup_expired_keys(self, db_mock):
        """Test cleanup of expired API keys"""
        db_mock.api_keys.delete_many.return_value = Mock(deleted_count=3)
        
        result = await api_key_service.cleanup_expired_keys()
        
        assert result == 3
        db_mock.api_keys.delete_many.assert_called_once()


@pytest.fixture
def db_mock():
    """Mock database for testing"""
    with patch('app.services.api_key_service.Database') as mock_db_class:
        mock_db = Mock()
        mock_db_class.get_db.return_value = mock_db
        yield mock_db
