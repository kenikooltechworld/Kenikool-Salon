"""
Tests for booking integration service
Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5
"""
import pytest
from datetime import datetime, timedelta
from bson import ObjectId
from app.services.booking_integration_service import WaitlistBookingIntegration
from app.database import Database


@pytest.fixture
def db():
    """Get database instance"""
    return Database.get_db()


@pytest.fixture
def tenant_id():
    """Test tenant ID"""
    return "test-tenant-booking"


class TestBookingIntegrationService:
    """Test booking integration service functionality"""
    
    def test_successful_booking_creation_from_waitlist(self, db, tenant_id):
        """Test successful booking creation from waitlist"""
        # Clean up
        db.waitlist.delete_many({"tenant_id": tenant_id})
        db.bookings.delete_many({"tenant_id": tenant_id})
        
        # Create waitlist entry
        service_id = ObjectId()
        stylist_id = ObjectId()
        entry = {
            "tenant_id": tenant_id,
            "client_id": ObjectId(),
            "client_name": "John Doe",
            "client_phone": "5551234567",
            "client_email": "john@example.com",
            "service_id": service_id,
            "service_name": "Haircut",
            "stylist_id": stylist_id,
            "stylist_name": "Alice",
            "location_id": ObjectId(),
            "location_name": "Main Salon",
            "status": "waiting",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = db.waitlist.insert_one(entry)
        waitlist_id = str(result.inserted_id)
        
        # Create booking
        booking_date = datetime.utcnow() + timedelta(days=7)
        booking_result = WaitlistBookingIntegration.create_booking_from_waitlist(
            waitlist_id=waitlist_id,
            tenant_id=tenant_id,
            booking_date=booking_date,
            booking_time="14:00",
            notes="Test booking"
        )
        
        # Verify
        assert booking_result["success"] is True
        assert "booking_id" in booking_result
        
        # Verify booking was created
        booking = db.bookings.find_one({"_id": ObjectId(booking_result["booking_id"])})
        assert booking is not None
        assert booking["client_name"] == "John Doe"
        assert booking["service_name"] == "Haircut"
        assert booking["status"] == "confirmed"
        assert booking["source"] == "waitlist"
        
        # Clean up
        db.waitlist.delete_many({"tenant_id": tenant_id})
        db.bookings.delete_many({"tenant_id": tenant_id})
    
    def test_waitlist_status_update_to_booked(self, db, tenant_id):
        """Test waitlist status update to booked"""
        # Clean up
        db.waitlist.delete_many({"tenant_id": tenant_id})
        db.bookings.delete_many({"tenant_id": tenant_id})
        
        # Create waitlist entry
        entry = {
            "tenant_id": tenant_id,
            "client_name": "Jane Doe",
            "status": "waiting",
            "created_at": datetime.utcnow()
        }
        result = db.waitlist.insert_one(entry)
        waitlist_id = str(result.inserted_id)
        
        # Create booking
        booking_date = datetime.utcnow() + timedelta(days=7)
        WaitlistBookingIntegration.create_booking_from_waitlist(
            waitlist_id=waitlist_id,
            tenant_id=tenant_id,
            booking_date=booking_date,
            booking_time="10:00"
        )
        
        # Verify waitlist status updated
        updated_entry = db.waitlist.find_one({"_id": ObjectId(waitlist_id)})
        assert updated_entry["status"] == "booked"
        assert "booking_id" in updated_entry
        assert "booked_at" in updated_entry
        
        # Clean up
        db.waitlist.delete_many({"tenant_id": tenant_id})
        db.bookings.delete_many({"tenant_id": tenant_id})
    
    def test_booking_timestamp_recording(self, db, tenant_id):
        """Test booking timestamp recording"""
        # Clean up
        db.waitlist.delete_many({"tenant_id": tenant_id})
        db.bookings.delete_many({"tenant_id": tenant_id})
        
        # Create waitlist entry
        entry = {
            "tenant_id": tenant_id,
            "client_name": "Test Client",
            "status": "waiting",
            "created_at": datetime.utcnow()
        }
        result = db.waitlist.insert_one(entry)
        waitlist_id = str(result.inserted_id)
        
        # Create booking
        booking_date = datetime.utcnow() + timedelta(days=7)
        booking_result = WaitlistBookingIntegration.create_booking_from_waitlist(
            waitlist_id=waitlist_id,
            tenant_id=tenant_id,
            booking_date=booking_date,
            booking_time="15:30"
        )
        
        # Verify booking has timestamps
        booking = db.bookings.find_one({"_id": ObjectId(booking_result["booking_id"])})
        assert "created_at" in booking
        assert "updated_at" in booking
        assert booking["created_at"] is not None
        assert booking["updated_at"] is not None
        
        # Verify booking datetime is correct
        assert booking["booking_time"] == "15:30"
        assert booking["booking_date"].date() == booking_date.date()
        
        # Clean up
        db.waitlist.delete_many({"tenant_id": tenant_id})
        db.bookings.delete_many({"tenant_id": tenant_id})
    
    def test_handling_of_booking_creation_failure(self, db, tenant_id):
        """Test handling of booking creation failure"""
        # Clean up
        db.waitlist.delete_many({"tenant_id": tenant_id})
        
        # Try to create booking with invalid waitlist ID
        booking_result = WaitlistBookingIntegration.create_booking_from_waitlist(
            waitlist_id="invalid-id",
            tenant_id=tenant_id,
            booking_date=datetime.utcnow(),
            booking_time="10:00"
        )
        
        # Verify failure
        assert booking_result["success"] is False
        assert "error" in booking_result
    
    def test_cannot_book_already_booked_entry(self, db, tenant_id):
        """Test that already booked entries cannot be booked again"""
        # Clean up
        db.waitlist.delete_many({"tenant_id": tenant_id})
        db.bookings.delete_many({"tenant_id": tenant_id})
        
        # Create already booked entry
        entry = {
            "tenant_id": tenant_id,
            "client_name": "Test Client",
            "status": "booked",
            "booking_id": str(ObjectId()),
            "created_at": datetime.utcnow()
        }
        result = db.waitlist.insert_one(entry)
        waitlist_id = str(result.inserted_id)
        
        # Try to create booking
        booking_result = WaitlistBookingIntegration.create_booking_from_waitlist(
            waitlist_id=waitlist_id,
            tenant_id=tenant_id,
            booking_date=datetime.utcnow(),
            booking_time="10:00"
        )
        
        # Verify failure
        assert booking_result["success"] is False
        assert "already booked" in booking_result["error"]
        
        # Clean up
        db.waitlist.delete_many({"tenant_id": tenant_id})
    
    def test_cannot_book_cancelled_entry(self, db, tenant_id):
        """Test that cancelled entries cannot be booked"""
        # Clean up
        db.waitlist.delete_many({"tenant_id": tenant_id})
        
        # Create cancelled entry
        entry = {
            "tenant_id": tenant_id,
            "client_name": "Test Client",
            "status": "cancelled",
            "created_at": datetime.utcnow()
        }
        result = db.waitlist.insert_one(entry)
        waitlist_id = str(result.inserted_id)
        
        # Try to create booking
        booking_result = WaitlistBookingIntegration.create_booking_from_waitlist(
            waitlist_id=waitlist_id,
            tenant_id=tenant_id,
            booking_date=datetime.utcnow(),
            booking_time="10:00"
        )
        
        # Verify failure
        assert booking_result["success"] is False
        assert "already cancelled" in booking_result["error"]
        
        # Clean up
        db.waitlist.delete_many({"tenant_id": tenant_id})
    
    def test_booking_data_preparation(self, db, tenant_id):
        """Test booking data preparation from waitlist entry"""
        # Create waitlist entry
        service_id = ObjectId()
        stylist_id = ObjectId()
        entry = {
            "tenant_id": tenant_id,
            "client_id": ObjectId(),
            "client_name": "John Doe",
            "client_phone": "5551234567",
            "client_email": "john@example.com",
            "service_id": service_id,
            "service_name": "Haircut",
            "stylist_id": stylist_id,
            "stylist_name": "Alice",
            "location_id": ObjectId(),
            "location_name": "Main Salon",
            "_id": ObjectId()
        }
        
        # Prepare booking data
        booking_date = datetime.utcnow() + timedelta(days=7)
        booking_data = WaitlistBookingIntegration._prepare_booking_data(
            entry,
            booking_date,
            "14:30",
            "Test notes"
        )
        
        # Verify all fields are present
        assert booking_data["client_name"] == "John Doe"
        assert booking_data["service_name"] == "Haircut"
        assert booking_data["stylist_name"] == "Alice"
        assert booking_data["booking_time"] == "14:30"
        assert booking_data["status"] == "confirmed"
        assert booking_data["source"] == "waitlist"
        assert booking_data["notes"] == "Test notes"
    
    def test_booking_with_different_time_formats(self, db, tenant_id):
        """Test booking creation with different time formats"""
        # Clean up
        db.waitlist.delete_many({"tenant_id": tenant_id})
        db.bookings.delete_many({"tenant_id": tenant_id})
        
        # Create waitlist entry
        entry = {
            "tenant_id": tenant_id,
            "client_name": "Test Client",
            "status": "waiting",
            "created_at": datetime.utcnow()
        }
        result = db.waitlist.insert_one(entry)
        waitlist_id = str(result.inserted_id)
        
        # Create booking with different time
        booking_date = datetime.utcnow() + timedelta(days=7)
        booking_result = WaitlistBookingIntegration.create_booking_from_waitlist(
            waitlist_id=waitlist_id,
            tenant_id=tenant_id,
            booking_date=booking_date,
            booking_time="09:00"
        )
        
        # Verify
        assert booking_result["success"] is True
        booking = db.bookings.find_one({"_id": ObjectId(booking_result["booking_id"])})
        assert booking["booking_time"] == "09:00"
        
        # Clean up
        db.waitlist.delete_many({"tenant_id": tenant_id})
        db.bookings.delete_many({"tenant_id": tenant_id})
    
    def test_tenant_isolation_in_booking(self, db):
        """Test tenant isolation in booking creation"""
        tenant_1 = "tenant-1"
        tenant_2 = "tenant-2"
        
        # Clean up
        db.waitlist.delete_many({"tenant_id": {"$in": [tenant_1, tenant_2]}})
        db.bookings.delete_many({"tenant_id": {"$in": [tenant_1, tenant_2]}})
        
        # Create entry for tenant 1
        entry_1 = {
            "tenant_id": tenant_1,
            "client_name": "Client 1",
            "status": "waiting",
            "created_at": datetime.utcnow()
        }
        result_1 = db.waitlist.insert_one(entry_1)
        waitlist_id_1 = str(result_1.inserted_id)
        
        # Try to create booking for tenant 1 entry using tenant 2 context
        booking_result = WaitlistBookingIntegration.create_booking_from_waitlist(
            waitlist_id=waitlist_id_1,
            tenant_id=tenant_2,  # Different tenant
            booking_date=datetime.utcnow(),
            booking_time="10:00"
        )
        
        # Verify failure due to tenant isolation
        assert booking_result["success"] is False
        assert "not found" in booking_result["error"]
        
        # Clean up
        db.waitlist.delete_many({"tenant_id": {"$in": [tenant_1, tenant_2]}})
        db.bookings.delete_many({"tenant_id": {"$in": [tenant_1, tenant_2]}})
