"""
Tests for expiration task
Validates: Requirements 7.4
"""
import pytest
from datetime import datetime, timedelta
from bson import ObjectId
from unittest.mock import patch, Mock
from app.tasks.waitlist_tasks import expire_old_waitlist_entries
from app.database import Database


@pytest.fixture
def db():
    """Get database instance"""
    return Database.get_db()


@pytest.fixture
def tenant_id():
    """Test tenant ID"""
    return "test-tenant-123"


class TestExpirationTask:
    """Test expiration task functionality"""
    
    def test_expiration_task_execution(self, db, tenant_id):
        """Test that expiration task executes successfully"""
        # Create old entry
        created_at = datetime.utcnow() - timedelta(days=31)
        entry = {
            "tenant_id": tenant_id,
            "client_name": "Test Client",
            "client_phone": "5550001",
            "client_email": "test@example.com",
            "service_id": ObjectId(),
            "service_name": "Haircut",
            "status": "waiting",
            "priority_score": 10.0,
            "access_token": "token-test",
            "created_at": created_at,
            "updated_at": created_at
        }
        result = db.waitlist.insert_one(entry)
        entry_id = str(result.inserted_id)
        
        try:
            # Execute task
            result = expire_old_waitlist_entries()
            
            # Verify task returned result
            assert result is not None
            assert "waiting_expired" in result
            assert "notified_expired" in result
            assert "total_expired" in result
            
            # Verify entry was expired
            expired_entry = db.waitlist.find_one({"_id": ObjectId(entry_id)})
            assert expired_entry["status"] == "expired"
        finally:
            # Clean up
            db.waitlist.delete_one({"_id": ObjectId(entry_id)})
    
    def test_expiration_task_returns_counts(self, db, tenant_id):
        """Test that expiration task returns correct counts"""
        # Create multiple old entries
        created_at = datetime.utcnow() - timedelta(days=31)
        entry_ids = []
        
        for i in range(2):
            entry = {
                "tenant_id": tenant_id,
                "client_name": f"Client {i}",
                "client_phone": f"555000{i}",
                "client_email": f"client{i}@example.com",
                "service_id": ObjectId(),
                "service_name": "Haircut",
                "status": "waiting",
                "priority_score": 10.0 + i,
                "access_token": f"token-{i}",
                "created_at": created_at,
                "updated_at": created_at
            }
            result = db.waitlist.insert_one(entry)
            entry_ids.append(str(result.inserted_id))
        
        try:
            # Execute task
            result = expire_old_waitlist_entries()
            
            # Verify counts
            assert result["total_expired"] >= 2
        finally:
            # Clean up
            for entry_id in entry_ids:
                db.waitlist.delete_one({"_id": ObjectId(entry_id)})
    
    def test_expiration_task_handles_errors(self):
        """Test that expiration task handles errors gracefully"""
        # Mock database to raise error
        with patch('app.services.expiration_service.Database.get_db') as mock_get_db:
            mock_db = Mock()
            mock_db.waitlist.find.side_effect = Exception("Database error")
            mock_get_db.return_value = mock_db
            
            # Task should retry on error
            with pytest.raises(Exception):
                expire_old_waitlist_entries()
    
    def test_expiration_task_with_no_entries(self, db, tenant_id):
        """Test expiration task with no entries to expire"""
        # Execute task with no old entries
        result = expire_old_waitlist_entries()
        
        # Verify task completed successfully
        assert result is not None
        assert result["total_expired"] >= 0
    
    def test_expiration_task_processes_both_statuses(self, db, tenant_id):
        """Test that expiration task processes both waiting and notified entries"""
        # Create old waiting entry
        created_at = datetime.utcnow() - timedelta(days=31)
        waiting_entry = {
            "tenant_id": tenant_id,
            "client_name": "Waiting Client",
            "client_phone": "5550001",
            "client_email": "waiting@example.com",
            "service_id": ObjectId(),
            "service_name": "Haircut",
            "status": "waiting",
            "priority_score": 10.0,
            "access_token": "token-waiting",
            "created_at": created_at,
            "updated_at": created_at
        }
        waiting_result = db.waitlist.insert_one(waiting_entry)
        waiting_id = str(waiting_result.inserted_id)
        
        # Create old notified entry
        notified_at = datetime.utcnow() - timedelta(days=8)
        notified_entry = {
            "tenant_id": tenant_id,
            "client_name": "Notified Client",
            "client_phone": "5550002",
            "client_email": "notified@example.com",
            "service_id": ObjectId(),
            "service_name": "Haircut",
            "status": "notified",
            "priority_score": 10.0,
            "access_token": "token-notified",
            "created_at": datetime.utcnow() - timedelta(days=10),
            "notified_at": notified_at,
            "updated_at": notified_at
        }
        notified_result = db.waitlist.insert_one(notified_entry)
        notified_id = str(notified_result.inserted_id)
        
        try:
            # Execute task
            result = expire_old_waitlist_entries()
            
            # Verify both entries were processed
            waiting_entry = db.waitlist.find_one({"_id": ObjectId(waiting_id)})
            notified_entry = db.waitlist.find_one({"_id": ObjectId(notified_id)})
            
            assert waiting_entry["status"] == "expired"
            assert notified_entry["status"] == "expired"
            assert result["waiting_expired"] >= 1
            assert result["notified_expired"] >= 1
        finally:
            # Clean up
            db.waitlist.delete_one({"_id": ObjectId(waiting_id)})
            db.waitlist.delete_one({"_id": ObjectId(notified_id)})
