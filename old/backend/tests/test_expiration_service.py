"""
Tests for expiration service
Validates: Requirements 7.1, 7.2, 7.3, 7.5
"""
import pytest
from datetime import datetime, timedelta
from bson import ObjectId
from app.services.expiration_service import ExpirationService
from app.database import Database


@pytest.fixture
def db():
    """Get database instance"""
    return Database.get_db()


@pytest.fixture
def tenant_id():
    """Test tenant ID"""
    return "test-tenant-123"


class TestExpirationService:
    """Test expiration service functionality"""
    
    def test_expire_waiting_entries_31_days_old(self, db, tenant_id):
        """Test expiration of 31-day-old waiting entry"""
        # Create entry 31 days old
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
            # Run expiration
            result = ExpirationService.check_and_expire_entries(tenant_id)
            
            # Verify entry was expired
            expired_entry = db.waitlist.find_one({"_id": ObjectId(entry_id)})
            assert expired_entry["status"] == "expired"
            assert result["waiting_expired"] >= 1
        finally:
            # Clean up
            db.waitlist.delete_one({"_id": ObjectId(entry_id)})
    
    def test_no_expire_waiting_entries_29_days_old(self, db, tenant_id):
        """Test non-expiration of 29-day-old waiting entry"""
        # Create entry 29 days old
        created_at = datetime.utcnow() - timedelta(days=29)
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
            # Run expiration
            ExpirationService.check_and_expire_entries(tenant_id)
            
            # Verify entry was NOT expired
            entry = db.waitlist.find_one({"_id": ObjectId(entry_id)})
            assert entry["status"] == "waiting"
        finally:
            # Clean up
            db.waitlist.delete_one({"_id": ObjectId(entry_id)})
    
    def test_expire_notified_entries_8_days_old(self, db, tenant_id):
        """Test expiration of 8-day-old notified entry"""
        # Create entry notified 8 days ago
        notified_at = datetime.utcnow() - timedelta(days=8)
        entry = {
            "tenant_id": tenant_id,
            "client_name": "Test Client",
            "client_phone": "5550001",
            "client_email": "test@example.com",
            "service_id": ObjectId(),
            "service_name": "Haircut",
            "status": "notified",
            "priority_score": 10.0,
            "access_token": "token-test",
            "created_at": datetime.utcnow() - timedelta(days=10),
            "notified_at": notified_at,
            "updated_at": notified_at
        }
        result = db.waitlist.insert_one(entry)
        entry_id = str(result.inserted_id)
        
        try:
            # Run expiration
            result = ExpirationService.check_and_expire_entries(tenant_id)
            
            # Verify entry was expired
            expired_entry = db.waitlist.find_one({"_id": ObjectId(entry_id)})
            assert expired_entry["status"] == "expired"
            assert result["notified_expired"] >= 1
        finally:
            # Clean up
            db.waitlist.delete_one({"_id": ObjectId(entry_id)})
    
    def test_no_expire_notified_entries_6_days_old(self, db, tenant_id):
        """Test non-expiration of 6-day-old notified entry"""
        # Create entry notified 6 days ago
        notified_at = datetime.utcnow() - timedelta(days=6)
        entry = {
            "tenant_id": tenant_id,
            "client_name": "Test Client",
            "client_phone": "5550001",
            "client_email": "test@example.com",
            "service_id": ObjectId(),
            "service_name": "Haircut",
            "status": "notified",
            "priority_score": 10.0,
            "access_token": "token-test",
            "created_at": datetime.utcnow() - timedelta(days=8),
            "notified_at": notified_at,
            "updated_at": notified_at
        }
        result = db.waitlist.insert_one(entry)
        entry_id = str(result.inserted_id)
        
        try:
            # Run expiration
            ExpirationService.check_and_expire_entries(tenant_id)
            
            # Verify entry was NOT expired
            entry = db.waitlist.find_one({"_id": ObjectId(entry_id)})
            assert entry["status"] == "notified"
        finally:
            # Clean up
            db.waitlist.delete_one({"_id": ObjectId(entry_id)})
    
    def test_expire_multiple_entries(self, db, tenant_id):
        """Test expiration of multiple entries"""
        # Create multiple old entries
        created_at = datetime.utcnow() - timedelta(days=31)
        entry_ids = []
        
        for i in range(3):
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
            # Run expiration
            result = ExpirationService.check_and_expire_entries(tenant_id)
            
            # Verify all entries were expired
            for entry_id in entry_ids:
                entry = db.waitlist.find_one({"_id": ObjectId(entry_id)})
                assert entry["status"] == "expired"
            
            assert result["waiting_expired"] >= 3
        finally:
            # Clean up
            for entry_id in entry_ids:
                db.waitlist.delete_one({"_id": ObjectId(entry_id)})
    
    def test_tenant_isolation_in_expiration(self, db, tenant_id):
        """Test that expiration respects tenant isolation"""
        # Create entry for different tenant
        other_tenant_id = "other-tenant"
        created_at = datetime.utcnow() - timedelta(days=31)
        entry = {
            "tenant_id": other_tenant_id,
            "client_name": "Other Tenant Client",
            "client_phone": "5550001",
            "client_email": "other@example.com",
            "service_id": ObjectId(),
            "service_name": "Haircut",
            "status": "waiting",
            "priority_score": 10.0,
            "access_token": "token-other",
            "created_at": created_at,
            "updated_at": created_at
        }
        result = db.waitlist.insert_one(entry)
        entry_id = str(result.inserted_id)
        
        try:
            # Run expiration for different tenant
            ExpirationService.check_and_expire_entries(tenant_id)
            
            # Verify entry was NOT expired (belongs to different tenant)
            entry = db.waitlist.find_one({"_id": ObjectId(entry_id)})
            assert entry["status"] == "waiting"
        finally:
            # Clean up
            db.waitlist.delete_one({"_id": ObjectId(entry_id)})
    
    def test_expiration_updates_timestamp(self, db, tenant_id):
        """Test that expiration updates the updated_at timestamp"""
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
            # Run expiration
            ExpirationService.check_and_expire_entries(tenant_id)
            
            # Verify timestamp was updated
            expired_entry = db.waitlist.find_one({"_id": ObjectId(entry_id)})
            assert expired_entry["updated_at"] > created_at
        finally:
            # Clean up
            db.waitlist.delete_one({"_id": ObjectId(entry_id)})
    
    def test_expiration_returns_correct_counts(self, db, tenant_id):
        """Test that expiration returns correct counts"""
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
            # Run expiration
            result = ExpirationService.check_and_expire_entries(tenant_id)
            
            # Verify counts
            assert result["waiting_expired"] >= 1
            assert result["notified_expired"] >= 1
            assert result["total_expired"] >= 2
        finally:
            # Clean up
            db.waitlist.delete_one({"_id": ObjectId(waiting_id)})
            db.waitlist.delete_one({"_id": ObjectId(notified_id)})
