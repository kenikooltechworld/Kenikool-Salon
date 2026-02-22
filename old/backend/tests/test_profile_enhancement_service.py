"""
Tests for profile enhancement service
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from bson import ObjectId

from app.services.profile_enhancement_service import (
    profile_enhancement_service, BadRequestException, NotFoundException, ConflictException
)


class TestProfileEnhancementService:
    """Tests for profile enhancement service"""

    @pytest.mark.asyncio
    async def test_upload_profile_picture_success(self, db_mock):
        """Test successful profile picture upload"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        
        file_content = b"fake_image_data"
        file_name = "profile.jpg"
        
        request_info = {"ip_address": "192.168.1.1"}
        
        with patch('app.services.profile_enhancement_service.audit_log_service') as mock_audit:
            mock_audit.log_event = AsyncMock()
            
            result = await profile_enhancement_service.upload_profile_picture(
                user_id, tenant_id, file_content, file_name, request_info
            )
        
        assert "original_url" in result
        assert "thumbnail_url" in result
        db_mock.users.update_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_upload_profile_picture_invalid_type(self, db_mock):
        """Test profile picture upload with invalid file type"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        
        file_content = b"fake_data"
        file_name = "document.pdf"
        
        request_info = {"ip_address": "192.168.1.1"}
        
        with pytest.raises(BadRequestException):
            await profile_enhancement_service.upload_profile_picture(
                user_id, tenant_id, file_content, file_name, request_info
            )

    @pytest.mark.asyncio
    async def test_upload_profile_picture_too_large(self, db_mock):
        """Test profile picture upload with file too large"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        
        # Create file larger than 5MB
        file_content = b"x" * (6 * 1024 * 1024)
        file_name = "large.jpg"
        
        request_info = {"ip_address": "192.168.1.1"}
        
        with pytest.raises(BadRequestException):
            await profile_enhancement_service.upload_profile_picture(
                user_id, tenant_id, file_content, file_name, request_info
            )

    @pytest.mark.asyncio
    async def test_delete_profile_picture(self, db_mock):
        """Test profile picture deletion"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        
        request_info = {"ip_address": "192.168.1.1"}
        
        with patch('app.services.profile_enhancement_service.audit_log_service') as mock_audit:
            mock_audit.log_event = AsyncMock()
            
            result = await profile_enhancement_service.delete_profile_picture(
                user_id, tenant_id, request_info
            )
        
        assert result is True
        db_mock.users.update_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_initiate_email_change_success(self, db_mock):
        """Test successful email change initiation"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        new_email = "newemail@example.com"
        
        user = {
            "_id": ObjectId(user_id),
            "email": "oldemail@example.com",
            "full_name": "Test User"
        }
        
        db_mock.users.find_one.return_value = user
        
        request_info = {"ip_address": "192.168.1.1"}
        
        with patch('app.services.profile_enhancement_service.email_service') as mock_email:
            mock_email.send_email_change_verification = AsyncMock()
            
            with patch('app.services.profile_enhancement_service.audit_log_service') as mock_audit:
                mock_audit.log_event = AsyncMock()
                
                token = await profile_enhancement_service.initiate_email_change(
                    user_id, tenant_id, new_email, request_info
                )
        
        assert token is not None
        db_mock.users.update_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_initiate_email_change_duplicate(self, db_mock):
        """Test email change with duplicate email"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        new_email = "existing@example.com"
        
        user = {
            "_id": ObjectId(user_id),
            "email": "oldemail@example.com"
        }
        
        existing_user = {
            "_id": ObjectId(),
            "email": new_email
        }
        
        db_mock.users.find_one.side_effect = [existing_user, user]
        
        request_info = {"ip_address": "192.168.1.1"}
        
        with pytest.raises(ConflictException):
            await profile_enhancement_service.initiate_email_change(
                user_id, tenant_id, new_email, request_info
            )

    @pytest.mark.asyncio
    async def test_initiate_phone_verification(self, db_mock):
        """Test phone verification initiation"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        phone_number = "+2348012345678"
        
        request_info = {"ip_address": "192.168.1.1"}
        
        with patch('app.services.profile_enhancement_service.RedisCache') as mock_cache:
            mock_cache.get.return_value = None
            mock_cache.set = Mock()
            
            with patch('app.services.profile_enhancement_service.audit_log_service') as mock_audit:
                mock_audit.log_event = AsyncMock()
                
                result = await profile_enhancement_service.initiate_phone_verification(
                    user_id, tenant_id, phone_number, request_info
                )
        
        assert result is True
        db_mock.users.update_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_initiate_phone_verification_rate_limit(self, db_mock):
        """Test phone verification rate limiting"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        phone_number = "+2348012345678"
        
        request_info = {"ip_address": "192.168.1.1"}
        
        with patch('app.services.profile_enhancement_service.RedisCache') as mock_cache:
            mock_cache.get.return_value = 3  # Already 3 attempts
            
            with pytest.raises(BadRequestException):
                await profile_enhancement_service.initiate_phone_verification(
                    user_id, tenant_id, phone_number, request_info
                )

    @pytest.mark.asyncio
    async def test_verify_phone_success(self, db_mock):
        """Test successful phone verification"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        code = "123456"
        phone_number = "+2348012345678"
        
        user = {
            "_id": ObjectId(user_id),
            "phone_verification_number": phone_number
        }
        
        db_mock.users.find_one.return_value = user
        
        request_info = {"ip_address": "192.168.1.1"}
        
        with patch('app.services.profile_enhancement_service.RedisCache') as mock_cache:
            mock_cache.get.return_value = code
            mock_cache.delete = Mock()
            
            with patch('app.services.profile_enhancement_service.audit_log_service') as mock_audit:
                mock_audit.log_event = AsyncMock()
                
                result = await profile_enhancement_service.verify_phone(
                    user_id, tenant_id, code, request_info
                )
        
        assert result is True
        db_mock.users.update_one.assert_called_once()


@pytest.fixture
def db_mock():
    """Mock database for testing"""
    with patch('app.services.profile_enhancement_service.Database') as mock_db_class:
        mock_db = Mock()
        mock_db_class.get_db.return_value = mock_db
        yield mock_db
