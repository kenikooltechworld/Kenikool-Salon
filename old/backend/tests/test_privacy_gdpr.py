"""
Tests for privacy and GDPR compliance service
"""
import pytest
from datetime import datetime, timedelta
from bson import ObjectId
from app.services.privacy_gdpr_service import PrivacyGDPRService
from app.database import Database


@pytest.fixture
def db():
    """Get database instance"""
    return Database.get_db()


@pytest.fixture
def tenant_id():
    """Test tenant ID"""
    return "test-tenant-123"


@pytest.fixture
def sample_client(db, tenant_id):
    """Create sample client for testing"""
    client = {
        "tenant_id": tenant_id,
        "name": "John Smith",
        "phone": "+1-555-0101",
        "email": "john.smith@example.com",
        "address": "123 Main St",
        "birthday": "1990-01-15",
        "notes": "VIP client",
        "tags": ["vip"],
        "total_visits": 5,
        "total_spent": 500.0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "last_activity_date": datetime.utcnow()
    }
    
    result = db.clients.insert_one(client)
    return str(result.inserted_id)


class TestPrivacyGDPR:
    """Test privacy and GDPR functionality"""
    
    def test_record_consent(self, db, tenant_id, sample_client):
        """Test recording client consent"""
        consent = PrivacyGDPRService.record_consent(
            client_id=sample_client,
            tenant_id=tenant_id,
            consent_type="marketing",
            granted=True,
            ip_address="192.168.1.1"
        )
        
        assert consent["client_id"] == sample_client
        assert consent["consent_type"] == "marketing"
        assert consent["granted"] is True
        assert consent["ip_address"] == "192.168.1.1"
    
    def test_record_consent_updates_client(self, db, tenant_id, sample_client):
        """Test that recording consent updates client record"""
        PrivacyGDPRService.record_consent(
            client_id=sample_client,
            tenant_id=tenant_id,
            consent_type="marketing",
            granted=True
        )
        
        # Check client was updated
        client = db.clients.find_one({"_id": ObjectId(sample_client)})
        assert client["consent"]["marketing"] is True
    
    def test_get_consent_history(self, db, tenant_id, sample_client):
        """Test getting consent history"""
        # Record multiple consents
        PrivacyGDPRService.record_consent(
            client_id=sample_client,
            tenant_id=tenant_id,
            consent_type="marketing",
            granted=True
        )
        
        PrivacyGDPRService.record_consent(
            client_id=sample_client,
            tenant_id=tenant_id,
            consent_type="analytics",
            granted=False
        )
        
        # Get history
        history = PrivacyGDPRService.get_consent_history(
            client_id=sample_client,
            tenant_id=tenant_id
        )
        
        assert len(history) == 2
        assert history[0]["consent_type"] in ["marketing", "analytics"]
    
    def test_get_consent_history_filtered(self, db, tenant_id, sample_client):
        """Test getting consent history with filter"""
        # Record multiple consents
        PrivacyGDPRService.record_consent(
            client_id=sample_client,
            tenant_id=tenant_id,
            consent_type="marketing",
            granted=True
        )
        
        PrivacyGDPRService.record_consent(
            client_id=sample_client,
            tenant_id=tenant_id,
            consent_type="analytics",
            granted=False
        )
        
        # Get history filtered by type
        history = PrivacyGDPRService.get_consent_history(
            client_id=sample_client,
            tenant_id=tenant_id,
            consent_type="marketing"
        )
        
        assert len(history) == 1
        assert history[0]["consent_type"] == "marketing"
    
    def test_export_client_data(self, db, tenant_id, sample_client):
        """Test exporting client data"""
        # Create related records
        db.bookings.insert_one({
            "tenant_id": tenant_id,
            "client_id": sample_client,
            "service_id": "service-1",
            "date": datetime.utcnow(),
            "status": "completed",
            "created_at": datetime.utcnow()
        })
        
        db.payments.insert_one({
            "tenant_id": tenant_id,
            "client_id": sample_client,
            "amount": 100.0,
            "method": "card",
            "status": "completed",
            "created_at": datetime.utcnow()
        })
        
        # Export data
        export = PrivacyGDPRService.export_client_data(
            client_id=sample_client,
            tenant_id=tenant_id
        )
        
        assert export["client"]["id"] == sample_client
        assert export["client"]["name"] == "John Smith"
        assert len(export["bookings"]) == 1
        assert len(export["payments"]) == 1
    
    def test_export_client_data_includes_all_sections(self, db, tenant_id, sample_client):
        """Test that export includes all data sections"""
        export = PrivacyGDPRService.export_client_data(
            client_id=sample_client,
            tenant_id=tenant_id
        )
        
        # Check all sections exist
        assert "export_date" in export
        assert "client" in export
        assert "bookings" in export
        assert "payments" in export
        assert "communications" in export
        assert "activities" in export
        assert "consents" in export
        assert "documents" in export
    
    def test_anonymize_client_data(self, db, tenant_id, sample_client):
        """Test anonymizing client data"""
        anonymized = PrivacyGDPRService.anonymize_client_data(
            client_id=sample_client,
            tenant_id=tenant_id
        )
        
        assert anonymized["is_anonymized"] is True
        assert anonymized["phone"] is None
        assert anonymized["email"] is None
        assert anonymized["address"] is None
        assert anonymized["birthday"] is None
        assert anonymized["name"].startswith("Anonymous_")
    
    def test_anonymize_client_data_preserves_analytics(self, db, tenant_id, sample_client):
        """Test that anonymization preserves analytics data"""
        # Add analytics data
        db.clients.update_one(
            {"_id": ObjectId(sample_client)},
            {"$set": {
                "total_visits": 10,
                "total_spent": 1000.0,
                "segment": "vip"
            }}
        )
        
        anonymized = PrivacyGDPRService.anonymize_client_data(
            client_id=sample_client,
            tenant_id=tenant_id
        )
        
        # Check analytics data is preserved
        client = db.clients.find_one({"_id": ObjectId(sample_client)})
        assert client["total_visits"] == 10
        assert client["total_spent"] == 1000.0
        assert client["segment"] == "vip"
    
    def test_anonymize_client_data_anonymizes_communications(self, db, tenant_id, sample_client):
        """Test that anonymization anonymizes communications"""
        # Create communication
        db.communications.insert_one({
            "tenant_id": tenant_id,
            "client_id": sample_client,
            "channel": "sms",
            "message": "Hello John",
            "status": "sent",
            "sent_at": datetime.utcnow()
        })
        
        PrivacyGDPRService.anonymize_client_data(
            client_id=sample_client,
            tenant_id=tenant_id
        )
        
        # Check communication was anonymized
        comm = db.communications.find_one({"client_id": sample_client})
        assert comm["message"] == "[Anonymized]"
    
    def test_set_retention_policy(self, db, tenant_id):
        """Test setting retention policy"""
        policy = PrivacyGDPRService.set_data_retention_policy(
            tenant_id=tenant_id,
            retention_days=365,
            auto_anonymize=True
        )
        
        assert policy["tenant_id"] == tenant_id
        assert policy["retention_days"] == 365
        assert policy["auto_anonymize"] is True
    
    def test_get_retention_policy(self, db, tenant_id):
        """Test getting retention policy"""
        # Set policy
        PrivacyGDPRService.set_data_retention_policy(
            tenant_id=tenant_id,
            retention_days=365,
            auto_anonymize=True
        )
        
        # Get policy
        policy = PrivacyGDPRService.get_data_retention_policy(tenant_id=tenant_id)
        
        assert policy is not None
        assert policy["retention_days"] == 365
        assert policy["auto_anonymize"] is True
    
    def test_apply_retention_policies(self, db, tenant_id):
        """Test applying retention policies"""
        # Create old inactive client
        old_client = {
            "tenant_id": tenant_id,
            "name": "Old Client",
            "phone": "+1-555-0102",
            "email": "old@example.com",
            "last_activity_date": datetime.utcnow() - timedelta(days=400),
            "created_at": datetime.utcnow() - timedelta(days=400),
            "updated_at": datetime.utcnow() - timedelta(days=400)
        }
        
        db.clients.insert_one(old_client)
        
        # Set retention policy
        PrivacyGDPRService.set_data_retention_policy(
            tenant_id=tenant_id,
            retention_days=365,
            auto_anonymize=True
        )
        
        # Apply policies
        result = PrivacyGDPRService.apply_retention_policies(tenant_id=tenant_id)
        
        assert result["anonymized_count"] >= 1
    
    def test_log_data_access(self, db, tenant_id, sample_client):
        """Test logging data access"""
        log = PrivacyGDPRService.log_data_access(
            client_id=sample_client,
            tenant_id=tenant_id,
            user_id="user-123",
            action="data_export",
            details={"format": "json"}
        )
        
        assert log["client_id"] == sample_client
        assert log["user_id"] == "user-123"
        assert log["action"] == "data_export"
        assert log["details"]["format"] == "json"
    
    def test_get_audit_logs(self, db, tenant_id, sample_client):
        """Test getting audit logs"""
        # Log multiple accesses
        PrivacyGDPRService.log_data_access(
            client_id=sample_client,
            tenant_id=tenant_id,
            user_id="user-123",
            action="data_export"
        )
        
        PrivacyGDPRService.log_data_access(
            client_id=sample_client,
            tenant_id=tenant_id,
            user_id="user-456",
            action="data_view"
        )
        
        # Get logs
        logs = PrivacyGDPRService.get_audit_logs(
            tenant_id=tenant_id,
            client_id=sample_client
        )
        
        assert len(logs) == 2
    
    def test_get_audit_logs_filtered_by_action(self, db, tenant_id, sample_client):
        """Test getting audit logs filtered by action"""
        # Log multiple accesses
        PrivacyGDPRService.log_data_access(
            client_id=sample_client,
            tenant_id=tenant_id,
            user_id="user-123",
            action="data_export"
        )
        
        PrivacyGDPRService.log_data_access(
            client_id=sample_client,
            tenant_id=tenant_id,
            user_id="user-456",
            action="data_view"
        )
        
        # Get logs filtered by action
        logs = PrivacyGDPRService.get_audit_logs(
            tenant_id=tenant_id,
            action="data_export"
        )
        
        assert len(logs) == 1
        assert logs[0]["action"] == "data_export"


class TestPrivacyGDPRProperties:
    """Property-based tests for privacy and GDPR"""
    
    def test_consent_record_has_required_fields(self, db, tenant_id, sample_client):
        """Property: Consent record should have all required fields"""
        consent = PrivacyGDPRService.record_consent(
            client_id=sample_client,
            tenant_id=tenant_id,
            consent_type="marketing",
            granted=True
        )
        
        assert "client_id" in consent
        assert "consent_type" in consent
        assert "granted" in consent
        assert "recorded_at" in consent
    
    def test_export_data_is_complete(self, db, tenant_id, sample_client):
        """Property: Exported data should include all client information"""
        export = PrivacyGDPRService.export_client_data(
            client_id=sample_client,
            tenant_id=tenant_id
        )
        
        # Check client data
        assert export["client"]["name"] is not None
        assert export["client"]["id"] == sample_client
        
        # Check all sections exist
        assert isinstance(export["bookings"], list)
        assert isinstance(export["payments"], list)
        assert isinstance(export["communications"], list)
        assert isinstance(export["activities"], list)
        assert isinstance(export["consents"], list)
        assert isinstance(export["documents"], list)
    
    def test_anonymized_data_removes_pii(self, db, tenant_id, sample_client):
        """Property: Anonymized data should remove all PII"""
        anonymized = PrivacyGDPRService.anonymize_client_data(
            client_id=sample_client,
            tenant_id=tenant_id
        )
        
        # Check PII is removed
        assert anonymized["phone"] is None
        assert anonymized["email"] is None
        assert anonymized["address"] is None
        assert anonymized["birthday"] is None
        assert not anonymized["name"].startswith("John")
    
    def test_audit_log_has_timestamp(self, db, tenant_id, sample_client):
        """Property: Audit log should have timestamp"""
        log = PrivacyGDPRService.log_data_access(
            client_id=sample_client,
            tenant_id=tenant_id,
            user_id="user-123",
            action="data_export"
        )
        
        assert "timestamp" in log
        assert isinstance(log["timestamp"], datetime)
