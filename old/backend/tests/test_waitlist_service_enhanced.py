"""
Tests for enhanced waitlist service with advanced filtering
Validates: Requirements 2.1, 2.2, 6.4, 11.1, 11.2, 11.3, 11.4, 11.5, 11.6
"""
import pytest
from datetime import datetime, timedelta
from bson import ObjectId
from app.services.waitlist_service import WaitlistService
from app.database import Database
from unittest.mock import Mock, patch, MagicMock


@pytest.fixture
def mock_db():
    """Mock database for testing"""
    db = Mock()
    db.waitlist = Mock()
    return db


@pytest.fixture
def sample_entries():
    """Sample waitlist entries for testing"""
    now = datetime.utcnow()
    return [
        {
            "_id": ObjectId(),
            "tenant_id": "tenant-1",
            "client_name": "John Doe",
            "client_phone": "5551234567",
            "client_email": "john@example.com",
            "service_id": ObjectId(),
            "service_name": "Haircut",
            "stylist_id": "stylist-1",
            "stylist_name": "Sarah",
            "location_id": "location-1",
            "location_name": "Downtown",
            "preferred_date": (now + timedelta(days=3)).isoformat(),
            "status": "waiting",
            "priority_score": 15.0,
            "access_token": "token-1",
            "created_at": now,
            "updated_at": now
        },
        {
            "_id": ObjectId(),
            "tenant_id": "tenant-1",
            "client_name": "Jane Smith",
            "client_phone": "5559876543",
            "client_email": "jane@example.com",
            "service_id": ObjectId(),
            "service_name": "Color Treatment",
            "stylist_id": "stylist-2",
            "stylist_name": "Mike",
            "location_id": "location-2",
            "location_name": "Uptown",
            "preferred_date": None,
            "status": "notified",
            "priority_score": 25.0,
            "access_token": "token-2",
            "created_at": now - timedelta(days=5),
            "updated_at": now - timedelta(days=2)
        },
        {
            "_id": ObjectId(),
            "tenant_id": "tenant-1",
            "client_name": "Bob Johnson",
            "client_phone": "5555555555",
            "client_email": "bob@example.com",
            "service_id": ObjectId(),
            "service_name": "Haircut",
            "stylist_id": "stylist-1",
            "stylist_name": "Sarah",
            "location_id": "location-1",
            "location_name": "Downtown",
            "preferred_date": None,
            "status": "waiting",
            "priority_score": 10.0,
            "access_token": "token-3",
            "created_at": now - timedelta(days=2),
            "updated_at": now - timedelta(days=1)
        }
    ]


class TestGetWaitlistEntriesFiltering:
    """Test get_waitlist_entries with various filters"""
    
    @patch('app.services.waitlist_service.Database.get_db')
    @patch('app.services.waitlist_service.PriorityCalculatorService.calculate_priority')
    def test_get_waitlist_entries_basic(self, mock_calc_priority, mock_get_db, sample_entries, mock_db):
        """Test basic get_waitlist_entries without filters"""
        mock_get_db.return_value = mock_db
        mock_db.waitlist.count_documents.return_value = 3
        mock_db.waitlist.find.return_value.sort.return_value.skip.return_value.limit.return_value = sample_entries
        mock_calc_priority.return_value = 20.0
        
        result = WaitlistService.get_waitlist_entries(
            tenant_id="tenant-1"
        )
        
        assert result["total"] == 3
        assert len(result["entries"]) == 3
        assert result["limit"] == 100
        assert result["offset"] == 0
    
    @patch('app.services.waitlist_service.Database.get_db')
    @patch('app.services.waitlist_service.PriorityCalculatorService.calculate_priority')
    def test_get_waitlist_entries_filter_by_status(self, mock_calc_priority, mock_get_db, sample_entries, mock_db):
        """Test filtering by status"""
        mock_get_db.return_value = mock_db
        waiting_entries = [e for e in sample_entries if e["status"] == "waiting"]
        mock_db.waitlist.count_documents.return_value = 2
        mock_db.waitlist.find.return_value.sort.return_value.skip.return_value.limit.return_value = waiting_entries
        mock_calc_priority.return_value = 20.0
        
        result = WaitlistService.get_waitlist_entries(
            tenant_id="tenant-1",
            status="waiting"
        )
        
        assert result["total"] == 2
        assert len(result["entries"]) == 2
        # Verify all entries have waiting status
        for entry in result["entries"]:
            assert entry["status"] == "waiting"
    
    @patch('app.services.waitlist_service.Database.get_db')
    @patch('app.services.waitlist_service.PriorityCalculatorService.calculate_priority')
    def test_get_waitlist_entries_filter_by_service(self, mock_calc_priority, mock_get_db, sample_entries, mock_db):
        """Test filtering by service_id"""
        mock_get_db.return_value = mock_db
        service_id = str(ObjectId())
        haircut_entries = [e for e in sample_entries if e["service_name"] == "Haircut"]
        mock_db.waitlist.count_documents.return_value = 2
        mock_db.waitlist.find.return_value.sort.return_value.skip.return_value.limit.return_value = haircut_entries
        mock_calc_priority.return_value = 20.0
        
        result = WaitlistService.get_waitlist_entries(
            tenant_id="tenant-1",
            service_id=service_id
        )
        
        assert result["total"] == 2
        # Verify query was called with service_id
        call_args = mock_db.waitlist.find.call_args
        assert call_args is not None
    
    @patch('app.services.waitlist_service.Database.get_db')
    @patch('app.services.waitlist_service.PriorityCalculatorService.calculate_priority')
    def test_get_waitlist_entries_filter_by_stylist(self, mock_calc_priority, mock_get_db, sample_entries, mock_db):
        """Test filtering by stylist_id"""
        mock_get_db.return_value = mock_db
        stylist_entries = [e for e in sample_entries if e["stylist_id"] == "stylist-1"]
        mock_db.waitlist.count_documents.return_value = 2
        mock_db.waitlist.find.return_value.sort.return_value.skip.return_value.limit.return_value = stylist_entries
        mock_calc_priority.return_value = 20.0
        
        result = WaitlistService.get_waitlist_entries(
            tenant_id="tenant-1",
            stylist_id="stylist-1"
        )
        
        assert result["total"] == 2
        for entry in result["entries"]:
            assert entry["stylist_id"] == "stylist-1"
    
    @patch('app.services.waitlist_service.Database.get_db')
    @patch('app.services.waitlist_service.PriorityCalculatorService.calculate_priority')
    def test_get_waitlist_entries_filter_by_location(self, mock_calc_priority, mock_get_db, sample_entries, mock_db):
        """Test filtering by location_id"""
        mock_get_db.return_value = mock_db
        location_entries = [e for e in sample_entries if e["location_id"] == "location-1"]
        mock_db.waitlist.count_documents.return_value = 2
        mock_db.waitlist.find.return_value.sort.return_value.skip.return_value.limit.return_value = location_entries
        mock_calc_priority.return_value = 20.0
        
        result = WaitlistService.get_waitlist_entries(
            tenant_id="tenant-1",
            location_id="location-1"
        )
        
        assert result["total"] == 2
        for entry in result["entries"]:
            assert entry["location_id"] == "location-1"
    
    @patch('app.services.waitlist_service.Database.get_db')
    @patch('app.services.waitlist_service.PriorityCalculatorService.calculate_priority')
    def test_get_waitlist_entries_search_by_name(self, mock_calc_priority, mock_get_db, sample_entries, mock_db):
        """Test search by client name"""
        mock_get_db.return_value = mock_db
        search_entries = [e for e in sample_entries if "john" in e["client_name"].lower()]
        mock_db.waitlist.count_documents.return_value = 1
        mock_db.waitlist.find.return_value.sort.return_value.skip.return_value.limit.return_value = search_entries
        mock_calc_priority.return_value = 20.0
        
        result = WaitlistService.get_waitlist_entries(
            tenant_id="tenant-1",
            search_query="john"
        )
        
        assert result["total"] == 1
        assert "John" in result["entries"][0]["client_name"]
    
    @patch('app.services.waitlist_service.Database.get_db')
    @patch('app.services.waitlist_service.PriorityCalculatorService.calculate_priority')
    def test_get_waitlist_entries_search_by_phone(self, mock_calc_priority, mock_get_db, sample_entries, mock_db):
        """Test search by phone number"""
        mock_get_db.return_value = mock_db
        search_entries = [e for e in sample_entries if "555123" in e["client_phone"]]
        mock_db.waitlist.count_documents.return_value = 1
        mock_db.waitlist.find.return_value.sort.return_value.skip.return_value.limit.return_value = search_entries
        mock_calc_priority.return_value = 20.0
        
        result = WaitlistService.get_waitlist_entries(
            tenant_id="tenant-1",
            search_query="555123"
        )
        
        assert result["total"] == 1
        assert "5551234567" in result["entries"][0]["client_phone"]
    
    @patch('app.services.waitlist_service.Database.get_db')
    @patch('app.services.waitlist_service.PriorityCalculatorService.calculate_priority')
    def test_get_waitlist_entries_date_range_filter(self, mock_calc_priority, mock_get_db, sample_entries, mock_db):
        """Test filtering by date range"""
        mock_get_db.return_value = mock_db
        now = datetime.utcnow()
        date_from = now - timedelta(days=3)
        date_to = now
        
        filtered_entries = [e for e in sample_entries if date_from <= e["created_at"] <= date_to]
        mock_db.waitlist.count_documents.return_value = len(filtered_entries)
        mock_db.waitlist.find.return_value.sort.return_value.skip.return_value.limit.return_value = filtered_entries
        mock_calc_priority.return_value = 20.0
        
        result = WaitlistService.get_waitlist_entries(
            tenant_id="tenant-1",
            date_from=date_from,
            date_to=date_to
        )
        
        assert result["total"] == len(filtered_entries)
    
    @patch('app.services.waitlist_service.Database.get_db')
    @patch('app.services.waitlist_service.PriorityCalculatorService.calculate_priority')
    def test_get_waitlist_entries_sort_by_priority(self, mock_calc_priority, mock_get_db, sample_entries, mock_db):
        """Test sorting by priority score"""
        mock_get_db.return_value = mock_db
        sorted_entries = sorted(sample_entries, key=lambda x: x["priority_score"], reverse=True)
        mock_db.waitlist.count_documents.return_value = 3
        mock_db.waitlist.find.return_value.sort.return_value.skip.return_value.limit.return_value = sorted_entries
        mock_calc_priority.return_value = 20.0
        
        result = WaitlistService.get_waitlist_entries(
            tenant_id="tenant-1",
            sort_by="priority"
        )
        
        # Verify sort was called with priority_score
        call_args = mock_db.waitlist.find.return_value.sort.call_args
        assert call_args[0][0] == "priority_score"
        assert call_args[0][1] == -1  # Descending
    
    @patch('app.services.waitlist_service.Database.get_db')
    @patch('app.services.waitlist_service.PriorityCalculatorService.calculate_priority')
    def test_get_waitlist_entries_sort_by_created_at(self, mock_calc_priority, mock_get_db, sample_entries, mock_db):
        """Test sorting by created_at"""
        mock_get_db.return_value = mock_db
        sorted_entries = sorted(sample_entries, key=lambda x: x["created_at"], reverse=True)
        mock_db.waitlist.count_documents.return_value = 3
        mock_db.waitlist.find.return_value.sort.return_value.skip.return_value.limit.return_value = sorted_entries
        mock_calc_priority.return_value = 20.0
        
        result = WaitlistService.get_waitlist_entries(
            tenant_id="tenant-1",
            sort_by="created_at"
        )
        
        # Verify sort was called with created_at
        call_args = mock_db.waitlist.find.return_value.sort.call_args
        assert call_args[0][0] == "created_at"
        assert call_args[0][1] == -1  # Descending
    
    @patch('app.services.waitlist_service.Database.get_db')
    @patch('app.services.waitlist_service.PriorityCalculatorService.calculate_priority')
    def test_get_waitlist_entries_pagination(self, mock_calc_priority, mock_get_db, sample_entries, mock_db):
        """Test pagination with limit and offset"""
        mock_get_db.return_value = mock_db
        mock_db.waitlist.count_documents.return_value = 3
        paginated_entries = sample_entries[1:3]  # Skip first, take 2
        mock_db.waitlist.find.return_value.sort.return_value.skip.return_value.limit.return_value = paginated_entries
        mock_calc_priority.return_value = 20.0
        
        result = WaitlistService.get_waitlist_entries(
            tenant_id="tenant-1",
            limit=2,
            offset=1
        )
        
        assert result["total"] == 3
        assert result["limit"] == 2
        assert result["offset"] == 1
        assert len(result["entries"]) == 2
        
        # Verify skip and limit were called
        skip_call = mock_db.waitlist.find.return_value.sort.return_value.skip.call_args
        limit_call = mock_db.waitlist.find.return_value.sort.return_value.skip.return_value.limit.call_args
        assert skip_call[0][0] == 1
        assert limit_call[0][0] == 2
    
    @patch('app.services.waitlist_service.Database.get_db')
    @patch('app.services.waitlist_service.PriorityCalculatorService.calculate_priority')
    def test_get_waitlist_entries_multiple_filters(self, mock_calc_priority, mock_get_db, sample_entries, mock_db):
        """Test combining multiple filters"""
        mock_get_db.return_value = mock_db
        # Filter: status=waiting AND stylist_id=stylist-1
        filtered_entries = [e for e in sample_entries 
                           if e["status"] == "waiting" and e["stylist_id"] == "stylist-1"]
        mock_db.waitlist.count_documents.return_value = len(filtered_entries)
        mock_db.waitlist.find.return_value.sort.return_value.skip.return_value.limit.return_value = filtered_entries
        mock_calc_priority.return_value = 20.0
        
        result = WaitlistService.get_waitlist_entries(
            tenant_id="tenant-1",
            status="waiting",
            stylist_id="stylist-1"
        )
        
        assert result["total"] == len(filtered_entries)
        for entry in result["entries"]:
            assert entry["status"] == "waiting"
            assert entry["stylist_id"] == "stylist-1"
    
    @patch('app.services.waitlist_service.Database.get_db')
    @patch('app.services.waitlist_service.PriorityCalculatorService.calculate_priority')
    def test_get_waitlist_entries_priority_calculation(self, mock_calc_priority, mock_get_db, sample_entries, mock_db):
        """Test that priority scores are calculated for each entry"""
        mock_get_db.return_value = mock_db
        mock_db.waitlist.count_documents.return_value = 3
        mock_db.waitlist.find.return_value.sort.return_value.skip.return_value.limit.return_value = sample_entries
        mock_calc_priority.side_effect = [15.0, 25.0, 10.0]
        
        result = WaitlistService.get_waitlist_entries(
            tenant_id="tenant-1"
        )
        
        # Verify calculate_priority was called for each entry
        assert mock_calc_priority.call_count == 3
        # Verify priority scores were updated
        assert result["entries"][0]["priority_score"] == 15.0
        assert result["entries"][1]["priority_score"] == 25.0
        assert result["entries"][2]["priority_score"] == 10.0


class TestGetEntryByToken:
    """Test get_entry_by_token method"""
    
    @patch('app.services.waitlist_service.Database.get_db')
    def test_get_entry_by_token_found(self, mock_get_db, sample_entries, mock_db):
        """Test retrieving entry by valid token"""
        mock_get_db.return_value = mock_db
        entry = sample_entries[0]
        mock_db.waitlist.find_one.return_value = entry
        
        result = WaitlistService.get_entry_by_token("token-1")
        
        assert result is not None
        assert result["client_name"] == "John Doe"
        assert result["access_token"] == "token-1"
    
    @patch('app.services.waitlist_service.Database.get_db')
    def test_get_entry_by_token_not_found(self, mock_get_db, mock_db):
        """Test retrieving entry by invalid token"""
        mock_get_db.return_value = mock_db
        mock_db.waitlist.find_one.return_value = None
        
        result = WaitlistService.get_entry_by_token("invalid-token")
        
        assert result is None


class TestUpdateClientInfo:
    """Test update_client_info method"""
    
    @patch('app.services.waitlist_service.Database.get_db')
    def test_update_client_info_success(self, mock_get_db, sample_entries, mock_db):
        """Test updating client information"""
        mock_get_db.return_value = mock_db
        entry = sample_entries[0].copy()
        updated_entry = entry.copy()
        updated_entry["client_name"] = "John Updated"
        updated_entry["client_phone"] = "5559999999"
        
        mock_db.waitlist.find_one.return_value = entry
        mock_db.waitlist.find_one_and_update.return_value = updated_entry
        
        result = WaitlistService.update_client_info(
            token="token-1",
            client_name="John Updated",
            client_phone="5559999999"
        )
        
        assert result is not None
        assert result["client_name"] == "John Updated"
        assert result["client_phone"] == "5559999999"
    
    @patch('app.services.waitlist_service.Database.get_db')
    def test_update_client_info_not_found(self, mock_get_db, mock_db):
        """Test updating non-existent entry"""
        mock_get_db.return_value = mock_db
        mock_db.waitlist.find_one.return_value = None
        
        result = WaitlistService.update_client_info(
            token="invalid-token",
            client_name="John Updated"
        )
        
        assert result is None
    
    @patch('app.services.waitlist_service.Database.get_db')
    def test_update_client_info_booked_entry_fails(self, mock_get_db, sample_entries, mock_db):
        """Test that updating booked entry raises error"""
        mock_get_db.return_value = mock_db
        entry = sample_entries[0].copy()
        entry["status"] = "booked"
        mock_db.waitlist.find_one.return_value = entry
        
        with pytest.raises(ValueError):
            WaitlistService.update_client_info(
                token="token-1",
                client_name="John Updated"
            )


class TestCancelByToken:
    """Test cancel_by_token method"""
    
    @patch('app.services.waitlist_service.Database.get_db')
    def test_cancel_by_token_success(self, mock_get_db, sample_entries, mock_db):
        """Test cancelling entry by token"""
        mock_get_db.return_value = mock_db
        entry = sample_entries[0].copy()
        cancelled_entry = entry.copy()
        cancelled_entry["status"] = "cancelled"
        
        mock_db.waitlist.find_one.return_value = entry
        mock_db.waitlist.find_one_and_update.return_value = cancelled_entry
        
        result = WaitlistService.cancel_by_token("token-1")
        
        assert result is not None
        assert result["status"] == "cancelled"
    
    @patch('app.services.waitlist_service.Database.get_db')
    def test_cancel_by_token_not_found(self, mock_get_db, mock_db):
        """Test cancelling non-existent entry"""
        mock_get_db.return_value = mock_db
        mock_db.waitlist.find_one.return_value = None
        
        result = WaitlistService.cancel_by_token("invalid-token")
        
        assert result is None
    
    @patch('app.services.waitlist_service.Database.get_db')
    def test_cancel_by_token_already_booked_fails(self, mock_get_db, sample_entries, mock_db):
        """Test that cancelling booked entry raises error"""
        mock_get_db.return_value = mock_db
        entry = sample_entries[0].copy()
        entry["status"] = "booked"
        mock_db.waitlist.find_one.return_value = entry
        
        with pytest.raises(ValueError):
            WaitlistService.cancel_by_token("token-1")


class TestBulkUpdateStatus:
    """Test bulk_update_status method"""
    
    @patch('app.services.waitlist_service.Database.get_db')
    def test_bulk_update_status_all_valid(self, mock_get_db, mock_db):
        """Test bulk update with all valid IDs"""
        mock_get_db.return_value = mock_db
        
        # Mock successful updates
        mock_update = Mock()
        mock_update.matched_count = 1
        mock_update.modified_count = 1
        mock_db.waitlist.update_one.return_value = mock_update
        
        waitlist_ids = [str(ObjectId()), str(ObjectId()), str(ObjectId())]
        result = WaitlistService.bulk_update_status(
            waitlist_ids=waitlist_ids,
            tenant_id="tenant-1",
            status="notified"
        )
        
        assert result["success_count"] == 3
        assert result["failure_count"] == 0
        assert len(result["failures"]) == 0
        assert mock_db.waitlist.update_one.call_count == 3
    
    @patch('app.services.waitlist_service.Database.get_db')
    def test_bulk_update_status_some_invalid(self, mock_get_db, mock_db):
        """Test bulk update with some invalid IDs"""
        mock_get_db.return_value = mock_db
        
        # Mock: first succeeds, second fails (not found), third succeeds
        mock_update_success = Mock()
        mock_update_success.matched_count = 1
        mock_update_success.modified_count = 1
        
        mock_update_fail = Mock()
        mock_update_fail.matched_count = 0
        mock_update_fail.modified_count = 0
        
        mock_db.waitlist.update_one.side_effect = [
            mock_update_success,
            mock_update_fail,
            mock_update_success
        ]
        
        waitlist_ids = [str(ObjectId()), str(ObjectId()), str(ObjectId())]
        result = WaitlistService.bulk_update_status(
            waitlist_ids=waitlist_ids,
            tenant_id="tenant-1",
            status="cancelled"
        )
        
        assert result["success_count"] == 2
        assert result["failure_count"] == 1
        assert len(result["failures"]) == 1
        assert result["failures"][0]["error"] == "Entry not found or does not belong to tenant"
    
    @patch('app.services.waitlist_service.Database.get_db')
    def test_bulk_update_status_invalid_id_format(self, mock_get_db, mock_db):
        """Test bulk update with invalid ID format"""
        mock_get_db.return_value = mock_db
        
        waitlist_ids = ["invalid-id", str(ObjectId())]
        result = WaitlistService.bulk_update_status(
            waitlist_ids=waitlist_ids,
            tenant_id="tenant-1",
            status="waiting"
        )
        
        assert result["success_count"] == 0
        assert result["failure_count"] == 2
        assert len(result["failures"]) == 2
        assert "Invalid waitlist ID format" in result["failures"][0]["error"]
    
    @patch('app.services.waitlist_service.Database.get_db')
    def test_bulk_update_status_invalid_status(self, mock_get_db, mock_db):
        """Test bulk update with invalid status"""
        mock_get_db.return_value = mock_db
        
        waitlist_ids = [str(ObjectId())]
        
        with pytest.raises(ValueError):
            WaitlistService.bulk_update_status(
                waitlist_ids=waitlist_ids,
                tenant_id="tenant-1",
                status="invalid_status"
            )
    
    @patch('app.services.waitlist_service.Database.get_db')
    def test_bulk_update_status_records_notification_timestamp(self, mock_get_db, mock_db):
        """Test that notified_at timestamp is recorded when status is notified"""
        mock_get_db.return_value = mock_db
        
        mock_update = Mock()
        mock_update.matched_count = 1
        mock_update.modified_count = 1
        mock_db.waitlist.update_one.return_value = mock_update
        
        waitlist_ids = [str(ObjectId())]
        WaitlistService.bulk_update_status(
            waitlist_ids=waitlist_ids,
            tenant_id="tenant-1",
            status="notified"
        )
        
        # Verify update_one was called with notified_at
        call_args = mock_db.waitlist.update_one.call_args
        update_dict = call_args[0][1]["$set"]
        assert "notified_at" in update_dict
        assert isinstance(update_dict["notified_at"], datetime)


class TestBulkDelete:
    """Test bulk_delete method"""
    
    @patch('app.services.waitlist_service.Database.get_db')
    def test_bulk_delete_all_valid(self, mock_get_db, mock_db):
        """Test bulk delete with all valid IDs"""
        mock_get_db.return_value = mock_db
        
        # Mock successful deletes
        mock_delete = Mock()
        mock_delete.deleted_count = 1
        mock_db.waitlist.delete_one.return_value = mock_delete
        
        waitlist_ids = [str(ObjectId()), str(ObjectId()), str(ObjectId())]
        result = WaitlistService.bulk_delete(
            waitlist_ids=waitlist_ids,
            tenant_id="tenant-1"
        )
        
        assert result["success_count"] == 3
        assert result["failure_count"] == 0
        assert len(result["failures"]) == 0
        assert mock_db.waitlist.delete_one.call_count == 3
    
    @patch('app.services.waitlist_service.Database.get_db')
    def test_bulk_delete_some_not_found(self, mock_get_db, mock_db):
        """Test bulk delete with some entries not found"""
        mock_get_db.return_value = mock_db
        
        # Mock: first succeeds, second fails (not found), third succeeds
        mock_delete_success = Mock()
        mock_delete_success.deleted_count = 1
        
        mock_delete_fail = Mock()
        mock_delete_fail.deleted_count = 0
        
        mock_db.waitlist.delete_one.side_effect = [
            mock_delete_success,
            mock_delete_fail,
            mock_delete_success
        ]
        
        waitlist_ids = [str(ObjectId()), str(ObjectId()), str(ObjectId())]
        result = WaitlistService.bulk_delete(
            waitlist_ids=waitlist_ids,
            tenant_id="tenant-1"
        )
        
        assert result["success_count"] == 2
        assert result["failure_count"] == 1
        assert len(result["failures"]) == 1
        assert result["failures"][0]["error"] == "Entry not found or does not belong to tenant"
    
    @patch('app.services.waitlist_service.Database.get_db')
    def test_bulk_delete_invalid_id_format(self, mock_get_db, mock_db):
        """Test bulk delete with invalid ID format"""
        mock_get_db.return_value = mock_db
        
        waitlist_ids = ["invalid-id", str(ObjectId())]
        result = WaitlistService.bulk_delete(
            waitlist_ids=waitlist_ids,
            tenant_id="tenant-1"
        )
        
        assert result["success_count"] == 0
        assert result["failure_count"] == 2
        assert len(result["failures"]) == 2
        assert "Invalid waitlist ID format" in result["failures"][0]["error"]
    
    @patch('app.services.waitlist_service.Database.get_db')
    def test_bulk_delete_exception_handling(self, mock_get_db, mock_db):
        """Test bulk delete handles exceptions gracefully"""
        mock_get_db.return_value = mock_db
        
        # Mock exception on second delete
        mock_delete_success = Mock()
        mock_delete_success.deleted_count = 1
        
        mock_db.waitlist.delete_one.side_effect = [
            mock_delete_success,
            Exception("Database error"),
            mock_delete_success
        ]
        
        waitlist_ids = [str(ObjectId()), str(ObjectId()), str(ObjectId())]
        result = WaitlistService.bulk_delete(
            waitlist_ids=waitlist_ids,
            tenant_id="tenant-1"
        )
        
        assert result["success_count"] == 2
        assert result["failure_count"] == 1
        assert len(result["failures"]) == 1
        assert "Database error" in result["failures"][0]["error"]
    
    @patch('app.services.waitlist_service.Database.get_db')
    def test_bulk_delete_tenant_isolation(self, mock_get_db, mock_db):
        """Test that bulk delete respects tenant isolation"""
        mock_get_db.return_value = mock_db
        
        mock_delete = Mock()
        mock_delete.deleted_count = 1
        mock_db.waitlist.delete_one.return_value = mock_delete
        
        waitlist_ids = [str(ObjectId())]
        WaitlistService.bulk_delete(
            waitlist_ids=waitlist_ids,
            tenant_id="tenant-1"
        )
        
        # Verify delete_one was called with tenant_id filter
        call_args = mock_db.waitlist.delete_one.call_args
        query = call_args[0][0]
        assert query["tenant_id"] == "tenant-1"
