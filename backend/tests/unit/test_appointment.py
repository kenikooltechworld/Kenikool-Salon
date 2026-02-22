"""Unit tests for appointment management."""

import pytest
from datetime import datetime, timedelta
from bson import ObjectId
from app.models.appointment import Appointment
from app.models.service import Service
from app.models.availability import Availability
from app.services.appointment_service import AppointmentService


@pytest.fixture
def tenant_id():
    """Create a test tenant ID."""
    return ObjectId()


@pytest.fixture
def customer_id():
    """Create a test customer ID."""
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
def test_service(tenant_id, service_id):
    """Create a test service."""
    service = Service(
        id=service_id,
        tenant_id=tenant_id,
        name="Test Service",
        description="A test service",
        duration_minutes=60,
        price=100.00,
        category="test",
        is_active=True,
    )
    service.save()
    return service


@pytest.fixture
def test_availability(tenant_id, staff_id):
    """Create a test availability."""
    today = datetime.utcnow().date()
    availability = Availability(
        tenant_id=tenant_id,
        staff_id=staff_id,
        day_of_week=today.weekday(),
        start_time="09:00:00",
        end_time="17:00:00",
        is_recurring=True,
        effective_from=today,
        is_active=True,
    )
    availability.save()
    return availability


class TestAppointmentCreation:
    """Test appointment creation."""

    def test_create_appointment_success(self, tenant_id, customer_id, staff_id, service_id, test_service):
        """Test successful appointment creation."""
        start_time = datetime.utcnow() + timedelta(days=1, hours=10)
        end_time = start_time + timedelta(hours=1)
        
        appointment = AppointmentService.create_appointment(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=staff_id,
            service_id=service_id,
            start_time=start_time,
            end_time=end_time,
            notes="Test appointment",
        )
        
        assert appointment.id is not None
        assert appointment.tenant_id == tenant_id
        assert appointment.customer_id == customer_id
        assert appointment.staff_id == staff_id
        assert appointment.service_id == service_id
        assert appointment.start_time == start_time
        assert appointment.end_time == end_time
        assert appointment.status == "scheduled"
        assert appointment.notes == "Test appointment"
        assert appointment.price == test_service.price

    def test_create_appointment_with_location(self, tenant_id, customer_id, staff_id, service_id, test_service):
        """Test appointment creation with location."""
        location_id = ObjectId()
        start_time = datetime.utcnow() + timedelta(days=1, hours=10)
        end_time = start_time + timedelta(hours=1)
        
        appointment = AppointmentService.create_appointment(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=staff_id,
            service_id=service_id,
            start_time=start_time,
            end_time=end_time,
            location_id=location_id,
        )
        
        assert appointment.location_id == location_id


class TestDoubleBookingPrevention:
    """Test double-booking prevention."""

    def test_prevent_overlapping_appointment(self, tenant_id, customer_id, staff_id, service_id, test_service):
        """Test that overlapping appointments are prevented."""
        start_time = datetime.utcnow() + timedelta(days=1, hours=10)
        end_time = start_time + timedelta(hours=1)
        
        # Create first appointment
        appointment1 = AppointmentService.create_appointment(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=staff_id,
            service_id=service_id,
            start_time=start_time,
            end_time=end_time,
        )
        assert appointment1.id is not None
        
        # Try to create overlapping appointment
        with pytest.raises(ValueError, match="overlapping appointment"):
            AppointmentService.create_appointment(
                tenant_id=tenant_id,
                customer_id=ObjectId(),
                staff_id=staff_id,
                service_id=service_id,
                start_time=start_time + timedelta(minutes=30),
                end_time=end_time + timedelta(minutes=30),
            )

    def test_allow_non_overlapping_appointment(self, tenant_id, customer_id, staff_id, service_id, test_service):
        """Test that non-overlapping appointments are allowed."""
        start_time1 = datetime.utcnow() + timedelta(days=1, hours=10)
        end_time1 = start_time1 + timedelta(hours=1)
        
        # Create first appointment
        appointment1 = AppointmentService.create_appointment(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=staff_id,
            service_id=service_id,
            start_time=start_time1,
            end_time=end_time1,
        )
        assert appointment1.id is not None
        
        # Create non-overlapping appointment
        start_time2 = end_time1 + timedelta(minutes=30)
        end_time2 = start_time2 + timedelta(hours=1)
        
        appointment2 = AppointmentService.create_appointment(
            tenant_id=tenant_id,
            customer_id=ObjectId(),
            staff_id=staff_id,
            service_id=service_id,
            start_time=start_time2,
            end_time=end_time2,
        )
        assert appointment2.id is not None

    def test_allow_appointment_after_cancellation(self, tenant_id, customer_id, staff_id, service_id, test_service):
        """Test that cancelled appointments don't prevent new bookings."""
        start_time = datetime.utcnow() + timedelta(days=1, hours=10)
        end_time = start_time + timedelta(hours=1)
        
        # Create and cancel first appointment
        appointment1 = AppointmentService.create_appointment(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=staff_id,
            service_id=service_id,
            start_time=start_time,
            end_time=end_time,
        )
        AppointmentService.cancel_appointment(tenant_id, appointment1.id)
        
        # Create new appointment at same time
        appointment2 = AppointmentService.create_appointment(
            tenant_id=tenant_id,
            customer_id=ObjectId(),
            staff_id=staff_id,
            service_id=service_id,
            start_time=start_time,
            end_time=end_time,
        )
        assert appointment2.id is not None


class TestAvailableSlots:
    """Test available slot calculation."""

    def test_get_available_slots_success(self, tenant_id, staff_id, service_id, test_service, test_availability):
        """Test getting available slots."""
        today = datetime.utcnow().date()
        date_obj = datetime.combine(today, datetime.min.time())
        
        slots = AppointmentService.get_available_slots(
            tenant_id=tenant_id,
            staff_id=staff_id,
            service_id=service_id,
            date=date_obj,
        )
        
        # Should have slots from 9 AM to 5 PM with 30-minute intervals
        assert len(slots) > 0
        # First slot should start at 9 AM
        assert slots[0][0].hour == 9

    def test_get_available_slots_with_booking(self, tenant_id, customer_id, staff_id, service_id, test_service, test_availability):
        """Test available slots with existing booking."""
        today = datetime.utcnow().date()
        date_obj = datetime.combine(today, datetime.min.time())
        
        # Create appointment at 10 AM
        start_time = date_obj.replace(hour=10, minute=0)
        end_time = start_time + timedelta(hours=1)
        
        appointment = AppointmentService.create_appointment(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=staff_id,
            service_id=service_id,
            start_time=start_time,
            end_time=end_time,
        )
        
        # Get available slots
        slots = AppointmentService.get_available_slots(
            tenant_id=tenant_id,
            staff_id=staff_id,
            service_id=service_id,
            date=date_obj,
        )
        
        # Check that 10 AM slot is not available
        for slot_start, slot_end in slots:
            assert not (slot_start.hour == 10 and slot_start.minute == 0)

    def test_get_available_slots_no_availability(self, tenant_id, staff_id, service_id, test_service):
        """Test available slots when staff has no availability."""
        today = datetime.utcnow().date()
        date_obj = datetime.combine(today, datetime.min.time())
        
        slots = AppointmentService.get_available_slots(
            tenant_id=tenant_id,
            staff_id=ObjectId(),  # Staff with no availability
            service_id=service_id,
            date=date_obj,
        )
        
        assert len(slots) == 0


class TestAppointmentConfirmation:
    """Test appointment confirmation."""

    def test_confirm_appointment_success(self, tenant_id, customer_id, staff_id, service_id, test_service):
        """Test successful appointment confirmation."""
        start_time = datetime.utcnow() + timedelta(days=1, hours=10)
        end_time = start_time + timedelta(hours=1)
        
        appointment = AppointmentService.create_appointment(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=staff_id,
            service_id=service_id,
            start_time=start_time,
            end_time=end_time,
        )
        
        confirmed = AppointmentService.confirm_appointment(tenant_id, appointment.id)
        
        assert confirmed.status == "confirmed"
        assert confirmed.confirmed_at is not None

    def test_confirm_nonexistent_appointment(self, tenant_id):
        """Test confirming non-existent appointment."""
        with pytest.raises(ValueError, match="not found"):
            AppointmentService.confirm_appointment(tenant_id, ObjectId())


class TestAppointmentCancellation:
    """Test appointment cancellation."""

    def test_cancel_appointment_success(self, tenant_id, customer_id, staff_id, service_id, test_service):
        """Test successful appointment cancellation."""
        start_time = datetime.utcnow() + timedelta(days=1, hours=10)
        end_time = start_time + timedelta(hours=1)
        
        appointment = AppointmentService.create_appointment(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=staff_id,
            service_id=service_id,
            start_time=start_time,
            end_time=end_time,
        )
        
        cancelled = AppointmentService.cancel_appointment(
            tenant_id, appointment.id, reason="Customer requested"
        )
        
        assert cancelled.status == "cancelled"
        assert cancelled.cancellation_reason == "Customer requested"
        assert cancelled.cancelled_at is not None

    def test_cancel_nonexistent_appointment(self, tenant_id):
        """Test cancelling non-existent appointment."""
        with pytest.raises(ValueError, match="not found"):
            AppointmentService.cancel_appointment(tenant_id, ObjectId())


class TestAppointmentListing:
    """Test appointment listing."""

    def test_list_appointments_success(self, tenant_id, customer_id, staff_id, service_id, test_service):
        """Test listing appointments."""
        start_time = datetime.utcnow() + timedelta(days=1, hours=10)
        end_time = start_time + timedelta(hours=1)
        
        # Create multiple appointments
        for i in range(3):
            AppointmentService.create_appointment(
                tenant_id=tenant_id,
                customer_id=customer_id,
                staff_id=staff_id,
                service_id=service_id,
                start_time=start_time + timedelta(hours=i),
                end_time=end_time + timedelta(hours=i),
            )
        
        appointments, total = AppointmentService.list_appointments(tenant_id=tenant_id)
        
        assert total >= 3
        assert len(appointments) >= 3

    def test_list_appointments_by_customer(self, tenant_id, customer_id, staff_id, service_id, test_service):
        """Test listing appointments filtered by customer."""
        start_time = datetime.utcnow() + timedelta(days=1, hours=10)
        end_time = start_time + timedelta(hours=1)
        
        # Create appointment for specific customer
        AppointmentService.create_appointment(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=staff_id,
            service_id=service_id,
            start_time=start_time,
            end_time=end_time,
        )
        
        # Create appointment for different customer
        AppointmentService.create_appointment(
            tenant_id=tenant_id,
            customer_id=ObjectId(),
            staff_id=staff_id,
            service_id=service_id,
            start_time=start_time + timedelta(hours=2),
            end_time=end_time + timedelta(hours=2),
        )
        
        appointments, total = AppointmentService.list_appointments(
            tenant_id=tenant_id, customer_id=customer_id
        )
        
        assert total == 1
        assert appointments[0].customer_id == customer_id

    def test_list_appointments_by_status(self, tenant_id, customer_id, staff_id, service_id, test_service):
        """Test listing appointments filtered by status."""
        start_time = datetime.utcnow() + timedelta(days=1, hours=10)
        end_time = start_time + timedelta(hours=1)
        
        # Create and confirm appointment
        appointment1 = AppointmentService.create_appointment(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=staff_id,
            service_id=service_id,
            start_time=start_time,
            end_time=end_time,
        )
        AppointmentService.confirm_appointment(tenant_id, appointment1.id)
        
        # Create scheduled appointment
        AppointmentService.create_appointment(
            tenant_id=tenant_id,
            customer_id=ObjectId(),
            staff_id=staff_id,
            service_id=service_id,
            start_time=start_time + timedelta(hours=2),
            end_time=end_time + timedelta(hours=2),
        )
        
        appointments, total = AppointmentService.list_appointments(
            tenant_id=tenant_id, status="confirmed"
        )
        
        assert total == 1
        assert appointments[0].status == "confirmed"

    def test_list_appointments_pagination(self, tenant_id, customer_id, staff_id, service_id, test_service):
        """Test appointment listing pagination."""
        start_time = datetime.utcnow() + timedelta(days=1, hours=10)
        end_time = start_time + timedelta(hours=1)
        
        # Create 5 appointments
        for i in range(5):
            AppointmentService.create_appointment(
                tenant_id=tenant_id,
                customer_id=customer_id,
                staff_id=staff_id,
                service_id=service_id,
                start_time=start_time + timedelta(hours=i),
                end_time=end_time + timedelta(hours=i),
            )
        
        # Get first page
        appointments1, total1 = AppointmentService.list_appointments(
            tenant_id=tenant_id, page=1, page_size=2
        )
        
        # Get second page
        appointments2, total2 = AppointmentService.list_appointments(
            tenant_id=tenant_id, page=2, page_size=2
        )
        
        assert len(appointments1) == 2
        assert len(appointments2) == 2
        assert total1 == total2
        assert appointments1[0].id != appointments2[0].id


class TestNoShowMarking:
    """Test marking appointments as no-show."""

    def test_mark_no_show_success(self, tenant_id, customer_id, staff_id, service_id, test_service):
        """Test marking appointment as no-show."""
        start_time = datetime.utcnow() + timedelta(days=1, hours=10)
        end_time = start_time + timedelta(hours=1)
        
        appointment = AppointmentService.create_appointment(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=staff_id,
            service_id=service_id,
            start_time=start_time,
            end_time=end_time,
        )
        
        no_show = AppointmentService.mark_no_show(
            tenant_id, appointment.id, reason="Customer did not arrive"
        )
        
        assert no_show.status == "no_show"
        assert no_show.no_show_reason == "Customer did not arrive"
        assert no_show.marked_no_show_at is not None
