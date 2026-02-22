"""
Tests for account deletion service
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from bson import ObjectId

from app.services.account_deletion_service import (
    account_deletion_service, UnauthorizedException, BadRequestException, NotFoundException
)
from app.utils.security import hash_password


class TestAccountDeletionService:
    """Tests for account deletion service"""

    @pytest.mark.asyncio
    async def test_request_deletion_success(self, db_mock):
        """Test successful deletion request"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        password = "TestPassword123!"
        
        user = {
            "_id": ObjectId(user_id),
            "tenant_id": tenant_id,
            "email": "test@example.com",
            "full_name": "Test User",
            "password_hash": hash_password(password),
            "role": "staff"
        }
        
        db_mock.users.find_one.return_value = user
        
        request_info = {"ip_address": "192.168.1.1"}
        
        with patch('app.services.account_deletion_service.email_service') as mock_email:
            mock_email.send_account_deletion_scheduled = AsyncMock()
            
            with patch('app.services.account_deletion_service.audit_log_service') as mock_audit:
                mock_audit.log_event = AsyncMock()
                
                result = await account_deletion_service.request_deletion(
                    user_id, tenant_id, password, request_info
                )
        
        assert result["status"] == "pending"
        assert "cancellation_token" in result
        db_mock.users.update_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_request_deletion_wrong_password(self, db_mock):
        """Test deletion request with wrong password"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        
        user = {
            "_id": ObjectId(user_id),
            "tenant_id": tenant_id,
            "password_hash": hash_password("CorrectPassword123!")
        }
        
        db_mock.users.find_one.return_value = user
        
        request_info = {"ip_address": "192.168.1.1"}
        
        with pytest.raises(UnauthorizedException):
            await account_deletion_service.request_deletion(
                user_id, tenant_id, "WrongPassword", request_info
            )

    @pytest.mark.asyncio
    async def test_request_deletion_owner_no_transfer(self, db_mock):
        """Test deletion request for owner without transfer"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        password = "TestPassword123!"
        
        user = {
            "_id": ObjectId(user_id),
            "tenant_id": tenant_id,
            "password_hash": hash_password(password),
            "role": "owner"
        }
        
        db_mock.users.find_one.return_value = user
        db_mock.users.find_one.side_effect = [user, None]  # First call returns user, second returns None
        
        request_info = {"ip_address": "192.168.1.1"}
        
        with pytest.raises(BadRequestException):
            await account_deletion_service.request_deletion(
                user_id, tenant_id, password, request_info
            )

    @pytest.mark.asyncio
    async def test_cancel_deletion_success(self, db_mock):
        """Test successful deletion cancellation"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        token = "test_token_123"
        
        deletion = {
            "_id": ObjectId(),
            "user_id": user_id,
            "tenant_id": tenant_id,
            "status": "pending",
            "cancellation_token": token
        }
        
        db_mock.account_deletions.find_one.return_value = deletion
        
        user = {
            "_id": ObjectId(user_id),
            "email": "test@example.com",
            "full_name": "Test User"
        }
        
        db_mock.users.find_one.return_value = user
        
        request_info = {"ip_address": "192.168.1.1"}
        
        with patch('app.services.account_deletion_service.email_service') as mock_email:
            mock_email.send_account_deletion_cancelled = AsyncMock()
            
            with patch('app.services.account_deletion_service.audit_log_service') as mock_audit:
                mock_audit.log_event = AsyncMock()
                
                result = await account_deletion_service.cancel_deletion(
                    user_id, tenant_id, token, request_info
                )
        
        assert result is True
        db_mock.account_deletions.update_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_cancel_deletion_invalid_token(self, db_mock):
        """Test cancellation with invalid token"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        
        deletion = {
            "_id": ObjectId(),
            "user_id": user_id,
            "status": "pending",
            "cancellation_token": "correct_token"
        }
        
        db_mock.account_deletions.find_one.return_value = deletion
        
        request_info = {"ip_address": "192.168.1.1"}
        
        with pytest.raises(BadRequestException):
            await account_deletion_service.cancel_deletion(
                user_id, tenant_id, "wrong_token", request_info
            )

    @pytest.mark.asyncio
    async def test_check_soft_deleted_login(self, db_mock):
        """Test checking soft-deleted account"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        
        user = {
            "_id": ObjectId(user_id),
            "tenant_id": tenant_id,
            "account_deleted": True
        }
        
        db_mock.users.find_one.return_value = user
        
        result = await account_deletion_service.check_soft_deleted_login(user_id, tenant_id)
        
        assert result is True

    @pytest.mark.asyncio
    async def test_cleanup_old_deletions(self, db_mock):
        """Test cleanup of old deletion records"""
        db_mock.account_deletions.delete_many.return_value = Mock(deleted_count=5)
        
        result = await account_deletion_service.cleanup_old_deletions()
        
        assert result == 5
        db_mock.account_deletions.delete_many.assert_called_once()


@pytest.fixture
def db_mock():
    """Mock database for testing"""
    with patch('app.services.account_deletion_service.Database') as mock_db_class:
        mock_db = Mock()
        mock_db_class.get_db.return_value = mock_db
        yield mock_db
