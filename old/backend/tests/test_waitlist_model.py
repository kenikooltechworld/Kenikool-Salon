"""
Tests for waitlist model validation
Validates: Requirements 1.1, 1.2, 1.6
"""
import pytest
from datetime import datetime
from bson import ObjectId
from app.models.waitlist import WaitlistInDB, WaitlistCreate, WaitlistBase
from app.schemas.waitlist import WaitlistResponse, WaitlistCreate as WaitlistCreateSchema
import uuid


class TestWaitlistModelValidation:
    """Test waitlist model validation"""
    
    def test_waitlist_entry_creation_with_required_fields(self):
        """Test creating waitlist entry with required fields"""
        entry = WaitlistInDB(
            tenant_id="test-tenant-123",
            client_name="John Doe",
            client_phone="5551234567",
            service_id="service-123",
            service_name="Haircut",
            status="waiting"
        )
        
        assert entry.client_name == "John Doe"
        assert entry.client_phone == "5551234567"
        assert entry.service_id == "service-123"
        assert entry.status == "waiting"
        assert entry.priority_score == 0.0
        assert entry.access_token is not None
        assert len(entry.access_token) > 0
        assert entry.created_at is not None
        assert entry.updated_at is not None
    
    def test_waitlist_entry_creation_with_all_fields(self):
        """Test creating waitlist entry with all optional fields"""
        entry = WaitlistInDB(
            tenant_id="test-tenant-123",
            client_name="Jane Smith",
            client_phone="5559876543",
            client_email="jane@example.com",
            service_id="service-456",
            service_name="Color Treatment",
            stylist_id="stylist-789",
            stylist_name="Sarah",
            location_id="location-101",
            location_name="Downtown",
            preferred_date=datetime(2024, 2, 15),
            notes="Prefers morning appointments",
            status="waiting"
        )
        
        assert entry.client_email == "jane@example.com"
        assert entry.stylist_id == "stylist-789"
        assert entry.stylist_name == "Sarah"
        assert entry.location_id == "location-101"
        assert entry.location_name == "Downtown"
        assert entry.preferred_date == datetime(2024, 2, 15)
        assert entry.notes == "Prefers morning appointments"
    
    def test_waitlist_entry_has_unique_access_token(self):
        """Test that each entry gets a unique access token"""
        entry1 = WaitlistInDB(
            tenant_id="test-tenant-123",
            client_name="Client 1",
            client_phone="5551111111",
            service_id="service-123",
            service_name="Service 1"
        )
        
        entry2 = WaitlistInDB(
            tenant_id="test-tenant-123",
            client_name="Client 2",
            client_phone="5552222222",
            service_id="service-123",
            service_name="Service 1"
        )
        
        assert entry1.access_token != entry2.access_token
    
    def test_waitlist_entry_status_validation(self):
        """Test that status field accepts valid values"""
        valid_statuses = ["waiting", "notified", "booked", "cancelled", "expired"]
        
        for status in valid_statuses:
            entry = WaitlistInDB(
                tenant_id="test-tenant-123",
                client_name="Test Client",
                client_phone="5551234567",
                service_id="service-123",
                service_name="Test Service",
                status=status
            )
            assert entry.status == status
    
    def test_waitlist_entry_phone_validation_min_length(self):
        """Test phone number minimum length validation"""
        with pytest.raises(ValueError):
            WaitlistBase(
                client_name="Test",
                client_phone="123",  # Too short
                service_id="service-123"
            )
    
    def test_waitlist_entry_phone_validation_max_length(self):
        """Test phone number maximum length validation"""
        with pytest.raises(ValueError):
            WaitlistBase(
                client_name="Test",
                client_phone="12345678901234567890123",  # Too long
                service_id="service-123"
            )
    
    def test_waitlist_entry_phone_validation_valid_lengths(self):
        """Test phone number valid lengths"""
        # Minimum valid length (10)
        entry1 = WaitlistBase(
            client_name="Test",
            client_phone="1234567890",
            service_id="service-123"
        )
        assert entry1.client_phone == "1234567890"
        
        # Maximum valid length (20)
        entry2 = WaitlistBase(
            client_name="Test",
            client_phone="12345678901234567890",
            service_id="service-123"
        )
        assert entry2.client_phone == "12345678901234567890"
    
    def test_waitlist_entry_client_name_validation_min_length(self):
        """Test client name minimum length validation"""
        with pytest.raises(ValueError):
            WaitlistBase(
                client_name="A",  # Too short
                client_phone="5551234567",
                service_id="service-123"
            )
    
    def test_waitlist_entry_client_name_validation_max_length(self):
        """Test client name maximum length validation"""
        with pytest.raises(ValueError):
            WaitlistBase(
                client_name="A" * 101,  # Too long
                client_phone="5551234567",
                service_id="service-123"
            )
    
    def test_waitlist_entry_client_name_validation_valid_lengths(self):
        """Test client name valid lengths"""
        # Minimum valid length (2)
        entry1 = WaitlistBase(
            client_name="Jo",
            client_phone="5551234567",
            service_id="service-123"
        )
        assert entry1.client_name == "Jo"
        
        # Maximum valid length (100)
        entry2 = WaitlistBase(
            client_name="A" * 100,
            client_phone="5551234567",
            service_id="service-123"
        )
        assert entry2.client_name == "A" * 100
    
    def test_waitlist_entry_timestamps_auto_generated(self):
        """Test that timestamps are automatically generated"""
        before = datetime.utcnow()
        entry = WaitlistInDB(
            tenant_id="test-tenant-123",
            client_name="Test Client",
            client_phone="5551234567",
            service_id="service-123",
            service_name="Test Service"
        )
        after = datetime.utcnow()
        
        assert before <= entry.created_at <= after
        assert before <= entry.updated_at <= after
    
    def test_waitlist_entry_booked_at_optional(self):
        """Test that booked_at is optional"""
        entry = WaitlistInDB(
            tenant_id="test-tenant-123",
            client_name="Test Client",
            client_phone="5551234567",
            service_id="service-123",
            service_name="Test Service"
        )
        
        assert entry.booked_at is None
    
    def test_waitlist_entry_booking_id_optional(self):
        """Test that booking_id is optional"""
        entry = WaitlistInDB(
            tenant_id="test-tenant-123",
            client_name="Test Client",
            client_phone="5551234567",
            service_id="service-123",
            service_name="Test Service"
        )
        
        assert entry.booking_id is None
    
    def test_waitlist_entry_with_booking_info(self):
        """Test waitlist entry with booking information"""
        entry = WaitlistInDB(
            tenant_id="test-tenant-123",
            client_name="Test Client",
            client_phone="5551234567",
            service_id="service-123",
            service_name="Test Service",
            status="booked",
            booked_at=datetime(2024, 2, 15, 10, 30),
            booking_id="booking-456"
        )
        
        assert entry.status == "booked"
        assert entry.booked_at == datetime(2024, 2, 15, 10, 30)
        assert entry.booking_id == "booking-456"
    
    def test_waitlist_response_schema_includes_all_fields(self):
        """Test that response schema includes all new fields"""
        response_data = {
            "id": "entry-123",
            "tenant_id": "test-tenant-123",
            "client_name": "Test Client",
            "client_phone": "5551234567",
            "service_id": "service-123",
            "service_name": "Test Service",
            "status": "waiting",
            "priority_score": 10.5,
            "access_token": str(uuid.uuid4()),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        response = WaitlistResponse(**response_data)
        
        assert response.priority_score == 10.5
        assert response.access_token is not None
        assert response.location_id is None
        assert response.location_name is None
        assert response.booked_at is None
        assert response.booking_id is None
    
    def test_waitlist_create_schema_includes_location(self):
        """Test that create schema includes location_id"""
        create_data = {
            "client_name": "Test Client",
            "client_phone": "5551234567",
            "service_id": "service-123",
            "location_id": "location-101"
        }
        
        create = WaitlistCreateSchema(**create_data)
        
        assert create.location_id == "location-101"
    
    def test_waitlist_entry_default_priority_score(self):
        """Test that priority_score defaults to 0.0"""
        entry = WaitlistInDB(
            tenant_id="test-tenant-123",
            client_name="Test Client",
            client_phone="5551234567",
            service_id="service-123",
            service_name="Test Service"
        )
        
        assert entry.priority_score == 0.0
        assert isinstance(entry.priority_score, float)
