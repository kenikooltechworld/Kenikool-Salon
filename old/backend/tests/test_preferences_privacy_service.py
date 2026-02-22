"""
Tests for preferences and privacy services
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
from bson import ObjectId

from app.services.preferences_service import preferences_service, BadRequestException
from app.services.privacy_service import privacy_service


class TestPreferencesService:
    """Tests for preferences service"""

    @pytest.mark.asyncio
    async def test_get_preferences_default(self, db_mock):
        """Test getting default preferences"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        
        db_mock.user_preferences.find_one.return_value = None
        
        result = await preferences_service.get_preferences(user_id, tenant_id)
        
        assert result["language"] == "en"
        assert result["timezone"] == "Africa/Lagos"
        assert result["currency"] == "NGN"

    @pytest.mark.asyncio
    async def test_update_preferences_success(self, db_mock):
        """Test successful preferences update"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        
        updated_prefs = {
            "_id": ObjectId(),
            "user_id": user_id,
            "tenant_id": tenant_id,
            "language": "fr",
            "timezone": "Europe/Paris",
            "currency": "EUR"
        }
        
        db_mock.user_preferences.find_one.return_value = None
        db_mock.user_preferences.insert_one.return_value = Mock(inserted_id=updated_prefs["_id"])
        db_mock.user_preferences.find_one.side_effect = [None, updated_prefs]
        
        request_info = {"ip_address": "192.168.1.1"}
        
        with patch('app.services.preferences_service.audit_log_service') as mock_audit:
            mock_audit.log_event = AsyncMock()
            
            result = await preferences_service.update_preferences(
                user_id, tenant_id,
                {"language": "fr", "timezone": "Europe/Paris", "currency": "EUR"},
                request_info
            )
        
        assert result["language"] == "fr"

    @pytest.mark.asyncio
    async def test_update_preferences_invalid_language(self, db_mock):
        """Test preferences update with invalid language"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        
        request_info = {"ip_address": "192.168.1.1"}
        
        with pytest.raises(BadRequestException):
            await preferences_service.update_preferences(
                user_id, tenant_id,
                {"language": "invalid_lang"},
                request_info
            )

    @pytest.mark.asyncio
    async def test_update_preferences_invalid_currency(self, db_mock):
        """Test preferences update with invalid currency"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        
        request_info = {"ip_address": "192.168.1.1"}
        
        with pytest.raises(BadRequestException):
            await preferences_service.update_preferences(
                user_id, tenant_id,
                {"currency": "INVALID"},
                request_info
            )

    @pytest.mark.asyncio
    async def test_get_accessibility_settings(self, db_mock):
        """Test getting accessibility settings"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        
        prefs = {
            "font_size": "large",
            "high_contrast": True,
            "reduce_motion": False,
            "screen_reader": True
        }
        
        db_mock.user_preferences.find_one.return_value = prefs
        
        result = await preferences_service.get_accessibility_settings(user_id, tenant_id)
        
        assert result["font_size"] == "large"
        assert result["high_contrast"] is True


class TestPrivacyService:
    """Tests for privacy service"""

    @pytest.mark.asyncio
    async def test_get_privacy_settings_default(self, db_mock):
        """Test getting default privacy settings"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        
        db_mock.privacy_settings.find_one.return_value = None
        
        result = await privacy_service.get_privacy_settings(user_id, tenant_id)
        
        assert result["analytics_enabled"] is True
        assert result["marketing_emails"] is True
        assert result["third_party_sharing"] is False

    @pytest.mark.asyncio
    async def test_update_privacy_settings_success(self, db_mock):
        """Test successful privacy settings update"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        
        updated_settings = {
            "_id": ObjectId(),
            "user_id": user_id,
            "tenant_id": tenant_id,
            "analytics_enabled": False,
            "marketing_emails": False,
            "third_party_sharing": False
        }
        
        db_mock.privacy_settings.find_one.return_value = None
        db_mock.privacy_settings.insert_one.return_value = Mock(inserted_id=updated_settings["_id"])
        db_mock.privacy_settings.find_one.side_effect = [None, updated_settings]
        
        request_info = {"ip_address": "192.168.1.1"}
        
        with patch('app.services.privacy_service.audit_log_service') as mock_audit:
            mock_audit.log_event = AsyncMock()
            
            result = await privacy_service.update_privacy_settings(
                user_id, tenant_id,
                {"analytics_enabled": False, "marketing_emails": False},
                request_info
            )
        
        assert result["analytics_enabled"] is False

    @pytest.mark.asyncio
    async def test_update_privacy_settings_invalid_type(self, db_mock):
        """Test privacy settings update with invalid type"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        
        request_info = {"ip_address": "192.168.1.1"}
        
        with pytest.raises(BadRequestException):
            await privacy_service.update_privacy_settings(
                user_id, tenant_id,
                {"analytics_enabled": "yes"},  # Should be boolean
                request_info
            )

    @pytest.mark.asyncio
    async def test_opt_out_analytics(self, db_mock):
        """Test opting out of analytics"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        
        updated_settings = {
            "_id": ObjectId(),
            "analytics_enabled": False
        }
        
        db_mock.privacy_settings.find_one.return_value = None
        db_mock.privacy_settings.insert_one.return_value = Mock(inserted_id=updated_settings["_id"])
        db_mock.privacy_settings.find_one.side_effect = [None, updated_settings]
        
        request_info = {"ip_address": "192.168.1.1"}
        
        with patch('app.services.privacy_service.audit_log_service') as mock_audit:
            mock_audit.log_event = AsyncMock()
            
            result = await privacy_service.opt_out_analytics(user_id, tenant_id, request_info)
        
        assert result["analytics_enabled"] is False

    @pytest.mark.asyncio
    async def test_is_analytics_enabled(self, db_mock):
        """Test checking if analytics is enabled"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        
        db_mock.privacy_settings.find_one.return_value = {"analytics_enabled": False}
        
        result = await privacy_service.is_analytics_enabled(user_id, tenant_id)
        
        assert result is False


@pytest.fixture
def db_mock():
    """Mock database for testing"""
    with patch('app.services.preferences_service.Database') as mock_db_class:
        mock_db = Mock()
        mock_db_class.get_db.return_value = mock_db
        yield mock_db
    
    with patch('app.services.privacy_service.Database') as mock_db_class:
        mock_db = Mock()
        mock_db_class.get_db.return_value = mock_db
        yield mock_db
