"""Unit tests for time slot reservation system."""

import pytest
from datetime import datetime, timedelta
from bson import ObjectId
from app.models.time_slot import TimeSlot
from app.models.appointment import Appointment
from app.models.service import Service
from app.services.time_slot_service import TimeSlotService


@pytest.fixture
def tenant_id():
    """Create a test tenant ID."""
    return ObjectId()


@pytest.fixture
def staff_id():
    """Create a test staff ID."""
    return ObjectId()


@pytest.fixture
def service_id():
    """Create a test service ID."""
    return ObjectId()


@pytest.fixture
def customer_id():
    """Create a test customer ID."""
    return ObjectId()


@pytest.fixture
def test_service(tenant_id, service_id):
    """Create a test service."""
    service = Service(
        id=service_id,
        tenant_id=tenant_id,
        name="Test Service",
        duration_minutes=60,
        price=100.0,
        category="test",
    )
    service.save()
    return service


class TestTimeSlotReservation:
    """Test time slot reservation functionality."""

    def test_reserve_slot_success(self, tenant_id, staff_id, service_id, customer_id, test_service):
        """Test successful time slot reservation."""
        start_time = datetime.utcnow() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        time_slot = TimeSlotService.reserve_slot(
            tenant_id=tenant_id,
            staff_id=staff_id,
            service_id=service_id,
            start_time=start_time,
            end_time=end_time,
            customer_id=customer_id,
        )
        
        assert time_slot.id is not None
        assert time_slot.tenant_id == tenant_id
        assert time_slot.staff_id == staff_id
        assert time_slot.service_id == service_id
        assert time_slot.customer_id == customer_id
        assert time_slot.status == "reserved"
        assert time_slot.start_time == start_time
        assert time_slot.end_time == end_time
        assert time_slot.is_expired() is False

    def test_reserve_slot_without_customer(self, tenant_id, staff_id, service_id, test_service):
        """Test time slot reservation without customer ID."""
        start_time = datetime.utcnow() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        time_slot = TimeSlotService.reserve_slot(
            tenant_id=tenant_id,
            staff_id=staff_id,
            service_id=service_id,
            start_time=start_time,
            end_time=end_time,
        )
        
        assert time_slot.customer_id is None
        assert time_slot.status == "reserved"

    def test_reserve_slot_conflict_with_existing_reservation(
        self, tenant_id, staff_id, service_id, customer_id, test_service
    ):
        """Test that overlapping reservations are prevented."""
        start_time = datetime.utcnow() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        # Create first reservation
        TimeSlotService.reserve_slot(
            tenant_id=tenant_id,
            staff_id=staff_id,
            service_id=service_id,
            start_time=start_time,
            end_time=end_time,
            customer_id=customer_id,
        )
        
        # Try to create overlapping reservation
        with pytest.raises(ValueError, match="already reserved"):
            TimeSlotService.reserve_slot(
                tenant_id=tenant_id,
                staff_id=staff_id,
                service_id=service_id,
                start_time=start_time + timedelta(minutes=30),
                end_time=end_time + timedelta(minutes=30),
                customer_id=customer_id,
            )

    def test_reserve_slot_conflict_with_appointment(
        self, tenant_id, staff_id, service_id, customer_id, test_service
    ):
        """Test that reservations cannot overlap with confirmed appointments."""
        start_time = datetime.utcnow() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        # Create confirmed appointment
        appointment = Appointment(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=staff_id,
            service_id=service_id,
            start_time=start_time,
            end_time=end_time,
            status="confirmed",
        )
        appointment.save()
        
        # Try to reserve overlapping slot
        with pytest.raises(ValueError, match="already booked"):
            TimeSlotService.reserve_slot(
                tenant_id=tenant_id,
                staff_id=staff_id,
                service_id=service_id,
                start_time=start_time + timedelta(minutes=30),
                end_time=end_time + timedelta(minutes=30),
                customer_id=customer_id,
            )


class TestTimeSlotConfirmation:
    """Test time slot confirmation functionality."""

    def test_confirm_reservation_success(
        self, tenant_id, staff_id, service_id, customer_id, test_service
    ):
        """Test successful time slot confirmation."""
        start_time = datetime.utcnow() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        # Reserve slot
        time_slot = TimeSlotService.reserve_slot(
            tenant_id=tenant_id,
            staff_id=staff_id,
            service_id=service_id,
            start_time=start_time,
            end_time=end_time,
            customer_id=customer_id,
        )
        
        # Create appointment
        appointment = Appointment(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=staff_id,
            service_id=service_id,
            start_time=start_time,
            end_time=end_time,
            status="scheduled",
        )
        appointment.save()
        
        # Confirm reservation
        confirmed_slot = TimeSlotService.confirm_reservation(
            tenant_id=tenant_id,
            time_slot_id=time_slot.id,
            appointment_id=appointment.id,
        )
        
        assert confirmed_slot.status == "confirmed"
        assert confirmed_slot.appointment_id == appointment.id

    def test_confirm_expired_reservation(
        self, tenant_id, staff_id, service_id, customer_id, test_service
    ):
        """Test that expired reservations cannot be confirmed."""
        start_time = datetime.utcnow() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        # Create reservation with past expiration
        time_slot = TimeSlot(
            tenant_id=tenant_id,
            staff_id=staff_id,
            service_id=service_id,
            customer_id=customer_id,
            start_time=start_time,
            end_time=end_time,
            status="reserved",
            reserved_at=datetime.utcnow() - timedelta(minutes=15),
            expires_at=datetime.utcnow() - timedelta(minutes=5),
        )
        time_slot.save()
        
        # Create appointment
        appointment = Appointment(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=staff_id,
            service_id=service_id,
            start_time=start_time,
            end_time=end_time,
            status="scheduled",
        )
        appointment.save()
        
        # Try to confirm expired reservation
        with pytest.raises(ValueError, match="expired"):
            TimeSlotService.confirm_reservation(
                tenant_id=tenant_id,
                time_slot_id=time_slot.id,
                appointment_id=appointment.id,
            )


class TestTimeSlotRelease:
    """Test time slot release functionality."""

    def test_release_reservation_success(
        self, tenant_id, staff_id, service_id, customer_id, test_service
    ):
        """Test successful time slot release."""
        start_time = datetime.utcnow() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        # Reserve slot
        time_slot = TimeSlotService.reserve_slot(
            tenant_id=tenant_id,
            staff_id=staff_id,
            service_id=service_id,
            start_time=start_time,
            end_time=end_time,
            customer_id=customer_id,
        )
        
        # Release reservation
        released_slot = TimeSlotService.release_reservation(
            tenant_id=tenant_id,
            time_slot_id=time_slot.id,
        )
        
        assert released_slot.status == "released"


class TestTimeSlotExpiration:
    """Test time slot expiration functionality."""

    def test_cleanup_expired_reservations(
        self, tenant_id, staff_id, service_id, customer_id, test_service
    ):
        """Test cleanup of expired reservations."""
        start_time = datetime.utcnow() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        # Create expired reservation
        time_slot = TimeSlot(
            tenant_id=tenant_id,
            staff_id=staff_id,
            service_id=service_id,
            customer_id=customer_id,
            start_time=start_time,
            end_time=end_time,
            status="reserved",
            reserved_at=datetime.utcnow() - timedelta(minutes=15),
            expires_at=datetime.utcnow() - timedelta(minutes=5),
        )
        time_slot.save()
        
        # Cleanup expired reservations
        count = TimeSlotService.cleanup_expired_reservations(tenant_id)
        
        assert count >= 1
        
        # Verify slot is marked as expired
        updated_slot = TimeSlotService.get_time_slot(tenant_id, time_slot.id)
        assert updated_slot.status == "expired"

    def test_is_expired_method(self, tenant_id, staff_id, service_id, customer_id):
        """Test the is_expired method."""
        start_time = datetime.utcnow() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        # Create non-expired reservation
        time_slot = TimeSlot(
            tenant_id=tenant_id,
            staff_id=staff_id,
            service_id=service_id,
            customer_id=customer_id,
            start_time=start_time,
            end_time=end_time,
            status="reserved",
            reserved_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(minutes=10),
        )
        
        assert time_slot.is_expired() is False
        
        # Create expired reservation
        expired_slot = TimeSlot(
            tenant_id=tenant_id,
            staff_id=staff_id,
            service_id=service_id,
            customer_id=customer_id,
            start_time=start_time,
            end_time=end_time,
            status="reserved",
            reserved_at=datetime.utcnow() - timedelta(minutes=15),
            expires_at=datetime.utcnow() - timedelta(minutes=5),
        )
        
        assert expired_slot.is_expired() is True


class TestTimeSlotListing:
    """Test time slot listing functionality."""

    def test_list_active_reservations(
        self, tenant_id, staff_id, service_id, customer_id, test_service
    ):
        """Test listing active reservations."""
        start_time = datetime.utcnow() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        # Create multiple reservations
        for i in range(3):
            TimeSlotService.reserve_slot(
                tenant_id=tenant_id,
                staff_id=staff_id,
                service_id=service_id,
                start_time=start_time + timedelta(hours=i),
                end_time=end_time + timedelta(hours=i),
                customer_id=customer_id,
            )
        
        # List active reservations
        slots = TimeSlotService.list_active_reservations(tenant_id)
        
        assert len(slots) >= 3
        assert all(slot.status == "reserved" for slot in slots)

    def test_list_active_reservations_by_staff(
        self, tenant_id, staff_id, service_id, customer_id, test_service
    ):
        """Test listing active reservations filtered by staff."""
        start_time = datetime.utcnow() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        other_staff_id = ObjectId()
        
        # Create reservation for first staff
        TimeSlotService.reserve_slot(
            tenant_id=tenant_id,
            staff_id=staff_id,
            service_id=service_id,
            start_time=start_time,
            end_time=end_time,
            customer_id=customer_id,
        )
        
        # Create reservation for other staff
        TimeSlotService.reserve_slot(
            tenant_id=tenant_id,
            staff_id=other_staff_id,
            service_id=service_id,
            start_time=start_time + timedelta(hours=2),
            end_time=end_time + timedelta(hours=2),
            customer_id=customer_id,
        )
        
        # List reservations for first staff only
        slots = TimeSlotService.list_active_reservations(tenant_id, staff_id=staff_id)
        
        assert all(slot.staff_id == staff_id for slot in slots)
