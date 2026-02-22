"""
Unit tests for package bulk operations service
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from bson import ObjectId

from app.services.package_bulk_operations_service import PackageBulkOperationsService


@pytest.fixture
def mock_db():
    """Create a mock database"""
    db = Mock()
    db.client = Mock()
    db.packages = Mock()
    db.package_purchases = Mock()
    db.package_audit_logs = Mock()
    return db


@pytest.fixture
def service(mock_db):
    """Create a service instance with mock database"""
    return PackageBulkOperationsService(mock_db)


class TestBulkActivatePackages:
    """Tests for bulk_activate_packages method"""
    
    @pytest.mark.asyncio
    async def test_bulk_activate_success(self, service, mock_db):
        """Test successful bulk activation of packages"""
        # Setup
        tenant_id = "tenant_123"
        package_ids = ["pkg_1", "pkg_2", "pkg_3"]
        staff_id = "staff_123"
        
        # Mock session
        mock_session = MagicMock()
        mock_db.client.start_session.return_value = mock_session
        
        # Mock package lookups
        mock_db.packages.find_one.side_effect = [
            {"_id": ObjectId(pid), "name": f"Package {i}", "tenant_id": tenant_id}
            for i, pid in enumerate(package_ids)
        ]
        
        # Mock update results
        mock_update_result = Mock()
        mock_update_result.modified_count = 1
        mock_db.packages.update_one.return_value = mock_update_result
        
        # Execute
        result = await service.bulk_activate_packages(tenant_id, package_ids, staff_id)
        
        # Assert
        assert result["operation"] == "bulk_activate"
        assert result["total_requested"] == 3
        assert result["successful"] == 3
        assert result["failed"] == 0
        assert len(result["successful_ids"]) == 3
        assert len(result["failed_details"]) == 0
        
        # Verify session was used
        mock_session.start_transaction.assert_called_once()
        mock_session.commit_transaction.assert_called_once()
        mock_session.end_session.assert_called_once()
        
        # Verify audit logs were created
        assert mock_db.package_audit_logs.insert_one.call_count == 3
    
    @pytest.mark.asyncio
    async def test_bulk_activate_package_not_found(self, service, mock_db):
        """Test bulk activation with non-existent package"""
        # Setup
        tenant_id = "tenant_123"
        package_ids = ["pkg_1", "pkg_2"]
        staff_id = "staff_123"
        
        # Mock session
        mock_session = MagicMock()
        mock_db.client.start_session.return_value = mock_session
        
        # Mock package lookups - first exists, second doesn't
        mock_db.packages.find_one.side_effect = [
            {"_id": ObjectId("pkg_1"), "name": "Package 1", "tenant_id": tenant_id},
            None  # Package not found
        ]
        
        # Mock update result
        mock_update_result = Mock()
        mock_update_result.modified_count = 1
        mock_db.packages.update_one.return_value = mock_update_result
        
        # Execute
        result = await service.bulk_activate_packages(tenant_id, package_ids, staff_id)
        
        # Assert
        assert result["successful"] == 1
        assert result["failed"] == 1
        assert len(result["failed_details"]) == 1
        assert result["failed_details"][0]["error"] == "Package not found"
        
        # Verify transaction was committed
        mock_session.commit_transaction.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_bulk_activate_transaction_rollback(self, service, mock_db):
        """Test transaction rollback on error"""
        # Setup
        tenant_id = "tenant_123"
        package_ids = ["pkg_1"]
        staff_id = "staff_123"
        
        # Mock session
        mock_session = MagicMock()
        mock_db.client.start_session.return_value = mock_session
        
        # Mock package lookup
        mock_db.packages.find_one.return_value = {
            "_id": ObjectId("pkg_1"),
            "name": "Package 1",
            "tenant_id": tenant_id
        }
        
        # Mock update to raise exception
        mock_db.packages.update_one.side_effect = Exception("Database error")
        
        # Execute and expect exception
        with pytest.raises(Exception) as exc_info:
            await service.bulk_activate_packages(tenant_id, package_ids, staff_id)
        
        # Assert
        assert "Bulk activation failed" in str(exc_info.value)
        mock_session.abort_transaction.assert_called_once()
        mock_session.end_session.assert_called_once()


class TestBulkDeactivatePackages:
    """Tests for bulk_deactivate_packages method"""
    
    @pytest.mark.asyncio
    async def test_bulk_deactivate_success(self, service, mock_db):
        """Test successful bulk deactivation of packages"""
        # Setup
        tenant_id = "tenant_123"
        package_ids = ["pkg_1", "pkg_2"]
        staff_id = "staff_123"
        
        # Mock session
        mock_session = MagicMock()
        mock_db.client.start_session.return_value = mock_session
        
        # Mock package lookups
        mock_db.packages.find_one.side_effect = [
            {"_id": ObjectId(pid), "name": f"Package {i}", "tenant_id": tenant_id}
            for i, pid in enumerate(package_ids)
        ]
        
        # Mock update results
        mock_update_result = Mock()
        mock_update_result.modified_count = 1
        mock_db.packages.update_one.return_value = mock_update_result
        
        # Execute
        result = await service.bulk_deactivate_packages(tenant_id, package_ids, staff_id)
        
        # Assert
        assert result["operation"] == "bulk_deactivate"
        assert result["successful"] == 2
        assert result["failed"] == 0
        
        # Verify audit logs
        assert mock_db.package_audit_logs.insert_one.call_count == 2
        
        # Verify transaction
        mock_session.commit_transaction.assert_called_once()


class TestBulkUpdatePrices:
    """Tests for bulk_update_prices method"""
    
    @pytest.mark.asyncio
    async def test_bulk_update_prices_success(self, service, mock_db):
        """Test successful bulk price update"""
        # Setup
        tenant_id = "tenant_123"
        package_updates = [
            {"package_id": "pkg_1", "new_price": 99.99},
            {"package_id": "pkg_2", "new_price": 149.99}
        ]
        staff_id = "staff_123"
        
        # Mock session
        mock_session = MagicMock()
        mock_db.client.start_session.return_value = mock_session
        
        # Mock package lookups
        mock_db.packages.find_one.side_effect = [
            {"_id": ObjectId("pkg_1"), "name": "Package 1", "package_price": 89.99, "tenant_id": tenant_id},
            {"_id": ObjectId("pkg_2"), "name": "Package 2", "package_price": 139.99, "tenant_id": tenant_id}
        ]
        
        # Mock update results
        mock_update_result = Mock()
        mock_update_result.modified_count = 1
        mock_db.packages.update_one.return_value = mock_update_result
        
        # Execute
        result = await service.bulk_update_prices(tenant_id, package_updates, staff_id)
        
        # Assert
        assert result["operation"] == "bulk_update_prices"
        assert result["successful"] == 2
        assert result["failed"] == 0
        
        # Verify audit logs
        assert mock_db.package_audit_logs.insert_one.call_count == 2
    
    @pytest.mark.asyncio
    async def test_bulk_update_prices_negative_price(self, service, mock_db):
        """Test bulk price update with negative price"""
        # Setup
        tenant_id = "tenant_123"
        package_updates = [
            {"package_id": "pkg_1", "new_price": -10.00}
        ]
        staff_id = "staff_123"
        
        # Mock session
        mock_session = MagicMock()
        mock_db.client.start_session.return_value = mock_session
        
        # Execute
        result = await service.bulk_update_prices(tenant_id, package_updates, staff_id)
        
        # Assert
        assert result["successful"] == 0
        assert result["failed"] == 1
        assert "Price cannot be negative" in result["failed_details"][0]["error"]
    
    @pytest.mark.asyncio
    async def test_bulk_update_prices_missing_fields(self, service, mock_db):
        """Test bulk price update with missing fields"""
        # Setup
        tenant_id = "tenant_123"
        package_updates = [
            {"package_id": "pkg_1"},  # Missing new_price
            {"new_price": 99.99}  # Missing package_id
        ]
        staff_id = "staff_123"
        
        # Mock session
        mock_session = MagicMock()
        mock_db.client.start_session.return_value = mock_session
        
        # Execute
        result = await service.bulk_update_prices(tenant_id, package_updates, staff_id)
        
        # Assert
        assert result["successful"] == 0
        assert result["failed"] == 2
        assert all("Missing" in detail["error"] for detail in result["failed_details"])


class TestBulkExtendExpiration:
    """Tests for bulk_extend_expiration method"""
    
    @pytest.mark.asyncio
    async def test_bulk_extend_expiration_success(self, service, mock_db):
        """Test successful bulk expiration extension"""
        # Setup
        tenant_id = "tenant_123"
        current_expiration = datetime.utcnow() + timedelta(days=30)
        purchase_updates = [
            {"purchase_id": "purch_1", "additional_days": 30},
            {"purchase_id": "purch_2", "additional_days": 60}
        ]
        staff_id = "staff_123"
        
        # Mock session
        mock_session = MagicMock()
        mock_db.client.start_session.return_value = mock_session
        
        # Mock purchase lookups
        mock_db.package_purchases.find_one.side_effect = [
            {
                "_id": ObjectId("purch_1"),
                "expiration_date": current_expiration,
                "client_id": "client_1",
                "tenant_id": tenant_id
            },
            {
                "_id": ObjectId("purch_2"),
                "expiration_date": current_expiration,
                "client_id": "client_2",
                "tenant_id": tenant_id
            }
        ]
        
        # Mock update results
        mock_update_result = Mock()
        mock_update_result.modified_count = 1
        mock_db.package_purchases.update_one.return_value = mock_update_result
        
        # Execute
        result = await service.bulk_extend_expiration(tenant_id, purchase_updates, staff_id)
        
        # Assert
        assert result["operation"] == "bulk_extend_expiration"
        assert result["successful"] == 2
        assert result["failed"] == 0
        
        # Verify audit logs
        assert mock_db.package_audit_logs.insert_one.call_count == 2
    
    @pytest.mark.asyncio
    async def test_bulk_extend_expiration_no_expiration_date(self, service, mock_db):
        """Test bulk extension with package having no expiration date"""
        # Setup
        tenant_id = "tenant_123"
        purchase_updates = [
            {"purchase_id": "purch_1", "additional_days": 30}
        ]
        staff_id = "staff_123"
        
        # Mock session
        mock_session = MagicMock()
        mock_db.client.start_session.return_value = mock_session
        
        # Mock purchase lookup - no expiration date
        mock_db.package_purchases.find_one.return_value = {
            "_id": ObjectId("purch_1"),
            "expiration_date": None,
            "client_id": "client_1",
            "tenant_id": tenant_id
        }
        
        # Execute
        result = await service.bulk_extend_expiration(tenant_id, purchase_updates, staff_id)
        
        # Assert
        assert result["successful"] == 0
        assert result["failed"] == 1
        assert "no expiration date" in result["failed_details"][0]["error"]
    
    @pytest.mark.asyncio
    async def test_bulk_extend_expiration_negative_days(self, service, mock_db):
        """Test bulk extension with negative additional days"""
        # Setup
        tenant_id = "tenant_123"
        purchase_updates = [
            {"purchase_id": "purch_1", "additional_days": -10}
        ]
        staff_id = "staff_123"
        
        # Mock session
        mock_session = MagicMock()
        mock_db.client.start_session.return_value = mock_session
        
        # Execute
        result = await service.bulk_extend_expiration(tenant_id, purchase_updates, staff_id)
        
        # Assert
        assert result["successful"] == 0
        assert result["failed"] == 1
        assert "must be positive" in result["failed_details"][0]["error"]
    
    @pytest.mark.asyncio
    async def test_bulk_extend_expiration_purchase_not_found(self, service, mock_db):
        """Test bulk extension with non-existent purchase"""
        # Setup
        tenant_id = "tenant_123"
        purchase_updates = [
            {"purchase_id": "purch_1", "additional_days": 30}
        ]
        staff_id = "staff_123"
        
        # Mock session
        mock_session = MagicMock()
        mock_db.client.start_session.return_value = mock_session
        
        # Mock purchase lookup - not found
        mock_db.package_purchases.find_one.return_value = None
        
        # Execute
        result = await service.bulk_extend_expiration(tenant_id, purchase_updates, staff_id)
        
        # Assert
        assert result["successful"] == 0
        assert result["failed"] == 1
        assert "not found" in result["failed_details"][0]["error"]


class TestBulkOperationsAtomicity:
    """Tests for transaction atomicity in bulk operations"""
    
    @pytest.mark.asyncio
    async def test_bulk_activate_atomicity_on_partial_failure(self, service, mock_db):
        """Test that bulk activate rolls back on partial failure"""
        # Setup
        tenant_id = "tenant_123"
        package_ids = ["pkg_1", "pkg_2", "pkg_3"]
        staff_id = "staff_123"
        
        # Mock session
        mock_session = MagicMock()
        mock_db.client.start_session.return_value = mock_session
        
        # Mock package lookups - all exist
        mock_db.packages.find_one.side_effect = [
            {"_id": ObjectId(pid), "name": f"Package {i}", "tenant_id": tenant_id}
            for i, pid in enumerate(package_ids)
        ]
        
        # Mock update - first succeeds, second fails
        mock_update_result_success = Mock()
        mock_update_result_success.modified_count = 1
        mock_update_result_fail = Mock()
        mock_update_result_fail.modified_count = 0
        
        mock_db.packages.update_one.side_effect = [
            mock_update_result_success,
            mock_update_result_fail,
            mock_update_result_success
        ]
        
        # Execute
        result = await service.bulk_activate_packages(tenant_id, package_ids, staff_id)
        
        # Assert - transaction should still commit (partial success is allowed)
        assert result["successful"] == 2
        assert result["failed"] == 1
        mock_session.commit_transaction.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_bulk_update_prices_atomicity_on_exception(self, service, mock_db):
        """Test that bulk update prices rolls back on exception"""
        # Setup
        tenant_id = "tenant_123"
        package_updates = [
            {"package_id": "pkg_1", "new_price": 99.99}
        ]
        staff_id = "staff_123"
        
        # Mock session
        mock_session = MagicMock()
        mock_db.client.start_session.return_value = mock_session
        
        # Mock package lookup
        mock_db.packages.find_one.return_value = {
            "_id": ObjectId("pkg_1"),
            "name": "Package 1",
            "package_price": 89.99,
            "tenant_id": tenant_id
        }
        
        # Mock update to raise exception
        mock_db.packages.update_one.side_effect = Exception("Database connection lost")
        
        # Execute and expect exception
        with pytest.raises(Exception) as exc_info:
            await service.bulk_update_prices(tenant_id, package_updates, staff_id)
        
        # Assert
        assert "Bulk price update failed" in str(exc_info.value)
        mock_session.abort_transaction.assert_called_once()


class TestBulkOperationsAuditLogging:
    """Tests for audit logging in bulk operations"""
    
    @pytest.mark.asyncio
    async def test_bulk_activate_creates_audit_logs(self, service, mock_db):
        """Test that bulk activate creates audit logs for each operation"""
        # Setup
        tenant_id = "tenant_123"
        package_ids = ["pkg_1", "pkg_2"]
        staff_id = "staff_123"
        
        # Mock session
        mock_session = MagicMock()
        mock_db.client.start_session.return_value = mock_session
        
        # Mock package lookups
        mock_db.packages.find_one.side_effect = [
            {"_id": ObjectId("pkg_1"), "name": "Package 1", "tenant_id": tenant_id},
            {"_id": ObjectId("pkg_2"), "name": "Package 2", "tenant_id": tenant_id}
        ]
        
        # Mock update results
        mock_update_result = Mock()
        mock_update_result.modified_count = 1
        mock_db.packages.update_one.return_value = mock_update_result
        
        # Execute
        await service.bulk_activate_packages(tenant_id, package_ids, staff_id)
        
        # Assert audit logs
        assert mock_db.package_audit_logs.insert_one.call_count == 2
        
        # Verify audit log details
        calls = mock_db.package_audit_logs.insert_one.call_args_list
        for i, call in enumerate(calls):
            log_entry = call[0][0]
            assert log_entry["tenant_id"] == tenant_id
            assert log_entry["action_type"] == "activate"
            assert log_entry["entity_type"] == "definition"
            assert log_entry["performed_by_user_id"] == staff_id
            assert log_entry["details"]["operation"] == "bulk_activate"
    
    @pytest.mark.asyncio
    async def test_bulk_extend_expiration_creates_audit_logs(self, service, mock_db):
        """Test that bulk extend creates audit logs with details"""
        # Setup
        tenant_id = "tenant_123"
        current_expiration = datetime.utcnow() + timedelta(days=30)
        purchase_updates = [
            {"purchase_id": "purch_1", "additional_days": 30}
        ]
        staff_id = "staff_123"
        
        # Mock session
        mock_session = MagicMock()
        mock_db.client.start_session.return_value = mock_session
        
        # Mock purchase lookup
        mock_db.package_purchases.find_one.return_value = {
            "_id": ObjectId("purch_1"),
            "expiration_date": current_expiration,
            "client_id": "client_1",
            "tenant_id": tenant_id
        }
        
        # Mock update result
        mock_update_result = Mock()
        mock_update_result.modified_count = 1
        mock_db.package_purchases.update_one.return_value = mock_update_result
        
        # Execute
        await service.bulk_extend_expiration(tenant_id, purchase_updates, staff_id)
        
        # Assert audit log
        mock_db.package_audit_logs.insert_one.assert_called_once()
        log_entry = mock_db.package_audit_logs.insert_one.call_args[0][0]
        
        assert log_entry["action_type"] == "extend"
        assert log_entry["entity_type"] == "purchase"
        assert log_entry["details"]["operation"] == "bulk_extend_expiration"
        assert log_entry["details"]["additional_days"] == 30
        assert log_entry["details"]["old_expiration"] == current_expiration


class TestBulkOperationsEdgeCases:
    """Tests for edge cases in bulk operations"""
    
    @pytest.mark.asyncio
    async def test_bulk_activate_empty_list(self, service, mock_db):
        """Test bulk activate with empty package list"""
        # Setup
        tenant_id = "tenant_123"
        package_ids = []
        staff_id = "staff_123"
        
        # Mock session
        mock_session = MagicMock()
        mock_db.client.start_session.return_value = mock_session
        
        # Execute
        result = await service.bulk_activate_packages(tenant_id, package_ids, staff_id)
        
        # Assert
        assert result["total_requested"] == 0
        assert result["successful"] == 0
        assert result["failed"] == 0
    
    @pytest.mark.asyncio
    async def test_bulk_update_prices_zero_price(self, service, mock_db):
        """Test bulk price update with zero price"""
        # Setup
        tenant_id = "tenant_123"
        package_updates = [
            {"package_id": "pkg_1", "new_price": 0.00}
        ]
        staff_id = "staff_123"
        
        # Mock session
        mock_session = MagicMock()
        mock_db.client.start_session.return_value = mock_session
        
        # Mock package lookup
        mock_db.packages.find_one.return_value = {
            "_id": ObjectId("pkg_1"),
            "name": "Package 1",
            "package_price": 89.99,
            "tenant_id": tenant_id
        }
        
        # Mock update result
        mock_update_result = Mock()
        mock_update_result.modified_count = 1
        mock_db.packages.update_one.return_value = mock_update_result
        
        # Execute
        result = await service.bulk_update_prices(tenant_id, package_updates, staff_id)
        
        # Assert - zero price should be allowed
        assert result["successful"] == 1
        assert result["failed"] == 0
    
    @pytest.mark.asyncio
    async def test_bulk_extend_expiration_zero_days(self, service, mock_db):
        """Test bulk extend with zero additional days"""
        # Setup
        tenant_id = "tenant_123"
        purchase_updates = [
            {"purchase_id": "purch_1", "additional_days": 0}
        ]
        staff_id = "staff_123"
        
        # Mock session
        mock_session = MagicMock()
        mock_db.client.start_session.return_value = mock_session
        
        # Execute
        result = await service.bulk_extend_expiration(tenant_id, purchase_updates, staff_id)
        
        # Assert - zero days should fail
        assert result["successful"] == 0
        assert result["failed"] == 1
        assert "must be positive" in result["failed_details"][0]["error"]
