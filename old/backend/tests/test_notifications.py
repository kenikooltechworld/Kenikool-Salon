"""
Tests for notification service
"""
import pytest
from datetime import datetime
from bson import ObjectId
from app.services.notification_service import NotificationService
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
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = db.clients.insert_one(client)
    return str(result.inserted_id)


class TestNotificationService:
    """Test notification service functionality"""
    
    def test_create_notification_rule(self, db, tenant_id):
        """Test creating notification rule"""
        rule = NotificationService.create_notification_rule(
            tenant_id=tenant_id,
            name="Birthday Greeting",
            trigger="birthday",
            channels=["sms", "email"],
            message_template="Happy Birthday {client_name}!",
            enabled=True
        )
        
        assert rule["name"] == "Birthday Greeting"
        assert rule["trigger"] == "birthday"
        assert rule["channels"] == ["sms", "email"]
        assert rule["enabled"] is True
    
    def test_create_notification_rule_invalid_trigger(self, db, tenant_id):
        """Test creating rule with invalid trigger"""
        with pytest.raises(ValueError):
            NotificationService.create_notification_rule(
                tenant_id=tenant_id,
                name="Test Rule",
                trigger="invalid_trigger",
                channels=["sms"],
                message_template="Test"
            )
    
    def test_create_notification_rule_invalid_channel(self, db, tenant_id):
        """Test creating rule with invalid channel"""
        with pytest.raises(ValueError):
            NotificationService.create_notification_rule(
                tenant_id=tenant_id,
                name="Test Rule",
                trigger="birthday",
                channels=["invalid_channel"],
                message_template="Test"
            )
    
    def test_get_notification_rules(self, db, tenant_id):
        """Test getting notification rules"""
        # Create multiple rules
        NotificationService.create_notification_rule(
            tenant_id=tenant_id,
            name="Birthday Greeting",
            trigger="birthday",
            channels=["sms"],
            message_template="Happy Birthday!"
        )
        
        NotificationService.create_notification_rule(
            tenant_id=tenant_id,
            name="Booking Confirmation",
            trigger="booking_created",
            channels=["email"],
            message_template="Your booking is confirmed"
        )
        
        # Get rules
        rules = NotificationService.get_notification_rules(tenant_id=tenant_id)
        
        assert len(rules) == 2
    
    def test_get_notification_rules_filtered_by_trigger(self, db, tenant_id):
        """Test getting rules filtered by trigger"""
        # Create multiple rules
        NotificationService.create_notification_rule(
            tenant_id=tenant_id,
            name="Birthday Greeting",
            trigger="birthday",
            channels=["sms"],
            message_template="Happy Birthday!"
        )
        
        NotificationService.create_notification_rule(
            tenant_id=tenant_id,
            name="Booking Confirmation",
            trigger="booking_created",
            channels=["email"],
            message_template="Your booking is confirmed"
        )
        
        # Get rules filtered by trigger
        rules = NotificationService.get_notification_rules(
            tenant_id=tenant_id,
            trigger="birthday"
        )
        
        assert len(rules) == 1
        assert rules[0]["trigger"] == "birthday"
    
    def test_get_notification_rules_enabled_only(self, db, tenant_id):
        """Test getting only enabled rules"""
        # Create enabled and disabled rules
        NotificationService.create_notification_rule(
            tenant_id=tenant_id,
            name="Birthday Greeting",
            trigger="birthday",
            channels=["sms"],
            message_template="Happy Birthday!",
            enabled=True
        )
        
        NotificationService.create_notification_rule(
            tenant_id=tenant_id,
            name="Disabled Rule",
            trigger="booking_created",
            channels=["email"],
            message_template="Test",
            enabled=False
        )
        
        # Get enabled rules only
        rules = NotificationService.get_notification_rules(
            tenant_id=tenant_id,
            enabled_only=True
        )
        
        assert len(rules) == 1
        assert rules[0]["enabled"] is True
    
    def test_update_notification_rule(self, db, tenant_id):
        """Test updating notification rule"""
        # Create rule
        rule = NotificationService.create_notification_rule(
            tenant_id=tenant_id,
            name="Birthday Greeting",
            trigger="birthday",
            channels=["sms"],
            message_template="Happy Birthday!"
        )
        
        # Update rule
        updated = NotificationService.update_notification_rule(
            rule_id=rule["_id"],
            tenant_id=tenant_id,
            name="Updated Birthday Greeting",
            channels=["sms", "email"],
            enabled=False
        )
        
        assert updated["name"] == "Updated Birthday Greeting"
        assert updated["channels"] == ["sms", "email"]
        assert updated["enabled"] is False
    
    def test_delete_notification_rule(self, db, tenant_id):
        """Test deleting notification rule"""
        # Create rule
        rule = NotificationService.create_notification_rule(
            tenant_id=tenant_id,
            name="Birthday Greeting",
            trigger="birthday",
            channels=["sms"],
            message_template="Happy Birthday!"
        )
        
        # Delete rule
        result = NotificationService.delete_notification_rule(
            rule_id=rule["_id"],
            tenant_id=tenant_id
        )
        
        assert result["id"] == rule["_id"]
        
        # Verify rule is deleted
        rules = NotificationService.get_notification_rules(tenant_id=tenant_id)
        assert len(rules) == 0
    
    def test_send_notification(self, db, tenant_id, sample_client):
        """Test sending notification"""
        notification = NotificationService.send_notification(
            client_id=sample_client,
            tenant_id=tenant_id,
            channels=["sms", "email"],
            message="Test notification"
        )
        
        assert notification["client_id"] == sample_client
        assert notification["channels"] == ["sms", "email"]
        assert notification["message"] == "Test notification"
        assert notification["status"] == "sent"
    
    def test_send_notification_invalid_client(self, db, tenant_id):
        """Test sending notification to invalid client"""
        with pytest.raises(Exception):
            NotificationService.send_notification(
                client_id="invalid-id",
                tenant_id=tenant_id,
                channels=["sms"],
                message="Test"
            )
    
    def test_get_notification_history(self, db, tenant_id, sample_client):
        """Test getting notification history"""
        # Send multiple notifications
        NotificationService.send_notification(
            client_id=sample_client,
            tenant_id=tenant_id,
            channels=["sms"],
            message="Notification 1"
        )
        
        NotificationService.send_notification(
            client_id=sample_client,
            tenant_id=tenant_id,
            channels=["email"],
            message="Notification 2"
        )
        
        # Get history
        history = NotificationService.get_notification_history(
            tenant_id=tenant_id,
            client_id=sample_client
        )
        
        assert len(history) == 2
    
    def test_get_notification_history_filtered_by_status(self, db, tenant_id, sample_client):
        """Test getting notification history filtered by status"""
        # Send notification
        NotificationService.send_notification(
            client_id=sample_client,
            tenant_id=tenant_id,
            channels=["sms"],
            message="Test notification"
        )
        
        # Get history filtered by status
        history = NotificationService.get_notification_history(
            tenant_id=tenant_id,
            status="sent"
        )
        
        assert len(history) == 1
        assert history[0]["status"] == "sent"
    
    def test_process_notification_rules(self, db, tenant_id, sample_client):
        """Test processing notification rules"""
        # Create rule
        NotificationService.create_notification_rule(
            tenant_id=tenant_id,
            name="Birthday Greeting",
            trigger="birthday",
            channels=["sms"],
            message_template="Happy Birthday!"
        )
        
        # Process rules
        notifications = NotificationService.process_notification_rules(
            tenant_id=tenant_id,
            trigger="birthday",
            client_id=sample_client
        )
        
        assert len(notifications) == 1
        assert notifications[0]["status"] == "sent"
    
    def test_notification_has_delivery_status(self, db, tenant_id, sample_client):
        """Test that notification has delivery status for each channel"""
        notification = NotificationService.send_notification(
            client_id=sample_client,
            tenant_id=tenant_id,
            channels=["sms", "email"],
            message="Test"
        )
        
        assert "sms" in notification["delivery_status"]
        assert "email" in notification["delivery_status"]
        assert notification["delivery_status"]["sms"]["status"] == "sent"
        assert notification["delivery_status"]["email"]["status"] == "sent"


class TestBulkNotify:
    """Test bulk_notify method"""
    
    def test_bulk_notify_all_valid(self, db, tenant_id):
        """Test bulk notify with all valid waitlist IDs"""
        # Create sample waitlist entries
        waitlist_entries = []
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
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            result = db.waitlist.insert_one(entry)
            waitlist_entries.append(str(result.inserted_id))
        
        try:
            # Bulk notify
            result = NotificationService.bulk_notify(
                waitlist_ids=waitlist_entries,
                tenant_id=tenant_id
            )
            
            assert result["success_count"] == 3
            assert result["failure_count"] == 0
            assert len(result["failures"]) == 0
            
            # Verify all entries have status "notified"
            for entry_id in waitlist_entries:
                entry = db.waitlist.find_one({"_id": ObjectId(entry_id)})
                assert entry["status"] == "notified"
                assert entry["notified_at"] is not None
        finally:
            # Clean up
            for entry_id in waitlist_entries:
                db.waitlist.delete_one({"_id": ObjectId(entry_id)})
    
    def test_bulk_notify_some_invalid_ids(self, db, tenant_id):
        """Test bulk notify with some invalid IDs"""
        # Create one valid entry
        valid_entry = {
            "tenant_id": tenant_id,
            "client_name": "Valid Client",
            "client_phone": "5550001",
            "client_email": "valid@example.com",
            "service_id": ObjectId(),
            "service_name": "Haircut",
            "status": "waiting",
            "priority_score": 10.0,
            "access_token": "token-valid",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = db.waitlist.insert_one(valid_entry)
        valid_id = str(result.inserted_id)
        
        try:
            # Mix valid and invalid IDs
            waitlist_ids = [valid_id, "invalid-id", str(ObjectId())]
            
            result = NotificationService.bulk_notify(
                waitlist_ids=waitlist_ids,
                tenant_id=tenant_id
            )
            
            assert result["success_count"] == 1
            assert result["failure_count"] == 2
            assert len(result["failures"]) == 2
            
            # Verify valid entry was notified
            entry = db.waitlist.find_one({"_id": ObjectId(valid_id)})
            assert entry["status"] == "notified"
        finally:
            # Clean up
            db.waitlist.delete_one({"_id": ObjectId(valid_id)})
    
    def test_bulk_notify_with_custom_template(self, db, tenant_id):
        """Test bulk notify with custom template"""
        # Create custom template
        template = {
            "tenant_id": tenant_id,
            "name": "Custom Template",
            "message": "Hello {client_name}, your {service_name} is ready!",
            "variables": ["client_name", "service_name"],
            "is_default": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        template_result = db.notification_templates.insert_one(template)
        template_id = str(template_result.inserted_id)
        
        # Create waitlist entry
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
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = db.waitlist.insert_one(entry)
        entry_id = str(result.inserted_id)
        
        try:
            # Bulk notify with template
            result = NotificationService.bulk_notify(
                waitlist_ids=[entry_id],
                tenant_id=tenant_id,
                template_id=template_id
            )
            
            assert result["success_count"] == 1
            assert result["failure_count"] == 0
            
            # Verify entry was notified
            entry = db.waitlist.find_one({"_id": ObjectId(entry_id)})
            assert entry["status"] == "notified"
        finally:
            # Clean up
            db.waitlist.delete_one({"_id": ObjectId(entry_id)})
            db.notification_templates.delete_one({"_id": ObjectId(template_id)})
    
    def test_bulk_notify_tenant_isolation(self, db, tenant_id):
        """Test that bulk notify respects tenant isolation"""
        # Create entry for different tenant
        other_tenant_id = "other-tenant"
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
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = db.waitlist.insert_one(entry)
        entry_id = str(result.inserted_id)
        
        try:
            # Try to notify with different tenant
            result = NotificationService.bulk_notify(
                waitlist_ids=[entry_id],
                tenant_id=tenant_id
            )
            
            # Should fail
            assert result["success_count"] == 0
            assert result["failure_count"] == 1
            
            # Verify entry status was not changed
            entry = db.waitlist.find_one({"_id": ObjectId(entry_id)})
            assert entry["status"] == "waiting"
        finally:
            # Clean up
            db.waitlist.delete_one({"_id": ObjectId(entry_id)})
    
    def test_bulk_notify_empty_list(self, db, tenant_id):
        """Test bulk notify with empty list"""
        result = NotificationService.bulk_notify(
            waitlist_ids=[],
            tenant_id=tenant_id
        )
        
        assert result["success_count"] == 0
        assert result["failure_count"] == 0
        assert len(result["failures"]) == 0
    
    def test_bulk_notify_returns_failure_details(self, db, tenant_id):
        """Test that bulk notify returns detailed failure information"""
        # Create one valid entry
        valid_entry = {
            "tenant_id": tenant_id,
            "client_name": "Valid Client",
            "client_phone": "5550001",
            "client_email": "valid@example.com",
            "service_id": ObjectId(),
            "service_name": "Haircut",
            "status": "waiting",
            "priority_score": 10.0,
            "access_token": "token-valid",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = db.waitlist.insert_one(valid_entry)
        valid_id = str(result.inserted_id)
        
        try:
            # Mix valid and invalid IDs
            invalid_id = "invalid-id"
            waitlist_ids = [valid_id, invalid_id]
            
            result = NotificationService.bulk_notify(
                waitlist_ids=waitlist_ids,
                tenant_id=tenant_id
            )
            
            # Check failure details
            assert len(result["failures"]) == 1
            assert result["failures"][0]["id"] == invalid_id
            assert "error" in result["failures"][0]
            assert len(result["failures"][0]["error"]) > 0
        finally:
            # Clean up
            db.waitlist.delete_one({"_id": ObjectId(valid_id)})


class TestNotificationServiceProperties:
    """Property-based tests for notification service"""
    
    def test_notification_rule_has_required_fields(self, db, tenant_id):
        """Property: Notification rule should have all required fields"""
        rule = NotificationService.create_notification_rule(
            tenant_id=tenant_id,
            name="Test Rule",
            trigger="birthday",
            channels=["sms"],
            message_template="Test"
        )
        
        assert "name" in rule
        assert "trigger" in rule
        assert "channels" in rule
        assert "message_template" in rule
        assert "enabled" in rule
        assert "created_at" in rule
    
    def test_sent_notification_has_timestamp(self, db, tenant_id, sample_client):
        """Property: Sent notification should have sent_at timestamp"""
        notification = NotificationService.send_notification(
            client_id=sample_client,
            tenant_id=tenant_id,
            channels=["sms"],
            message="Test"
        )
        
        assert notification["sent_at"] is not None
        assert isinstance(notification["sent_at"], datetime)
    
    def test_notification_channels_match_request(self, db, tenant_id, sample_client):
        """Property: Notification channels should match request"""
        channels = ["sms", "email", "whatsapp"]
        
        notification = NotificationService.send_notification(
            client_id=sample_client,
            tenant_id=tenant_id,
            channels=channels,
            message="Test"
        )
        
        assert notification["channels"] == channels
