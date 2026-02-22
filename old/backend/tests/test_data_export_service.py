"""
Tests for data export service
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from bson import ObjectId

from app.services.data_export_service import data_export_service


class TestDataExportService:
    """Tests for data export service"""

    @pytest.mark.asyncio
    async def test_request_export_success(self, db_mock):
        """Test successful export request"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        export_id = ObjectId()
        
        db_mock.data_exports.insert_one.return_value = Mock(inserted_id=export_id)
        
        request_info = {"ip_address": "192.168.1.1"}
        options = {"include_bookings": True, "include_clients": True}
        
        with patch('app.services.data_export_service.audit_log_service') as mock_audit:
            mock_audit.log_event = AsyncMock()
            
            result = await data_export_service.request_export(
                user_id, tenant_id, options, request_info
            )
        
        assert result == str(export_id)
        db_mock.data_exports.insert_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_exports(self, db_mock):
        """Test listing exports"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        
        exports = [
            {
                "_id": ObjectId(),
                "user_id": user_id,
                "status": "completed",
                "file_url": "https://example.com/export.json",
                "file_size": 1024,
                "requested_at": datetime.utcnow(),
                "completed_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(days=7)
            }
        ]
        
        db_mock.data_exports.find.return_value.sort.return_value.limit.return_value = exports
        
        result = await data_export_service.list_exports(user_id, tenant_id)
        
        assert len(result) == 1
        assert result[0]["status"] == "completed"

    @pytest.mark.asyncio
    async def test_cleanup_expired_exports(self, db_mock):
        """Test cleanup of expired exports"""
        db_mock.data_exports.delete_many.return_value = Mock(deleted_count=3)
        
        result = await data_export_service.cleanup_expired_exports()
        
        assert result == 3
        db_mock.data_exports.delete_many.assert_called_once()


@pytest.fixture
def db_mock():
    """Mock database for testing"""
    with patch('app.services.data_export_service.Database') as mock_db_class:
        mock_db = Mock()
        mock_db_class.get_db.return_value = mock_db
        yield mock_db
