"""Unit tests for AppointmentHistory model and service."""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from bson import ObjectId
from app.models.appointment_history import AppointmentHistory
from app.models.appointment import Appointment
from app.models.service import Service
from app.models.customer import Customer
from app.models.staff import Staff
from app.services.appointment_history_service import AppointmentHistoryService
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
        description="Test service description",
        duration_minutes=60,
        price=Decimal("100.00"),
        category="haircut",
    )
    service.save()
    return service


@pytest.fixture
def test_appointment(tenant_id, customer_id, staff_id, service_id, test_service):
    """Create a test appointment."""
    start_time = datetime.utcnow() + timedelta(days=1, hours=10)
    end_time = start_time + timedelta(hours=1)
    
    appointment = Appointment(
        tenant_id=tenant_id,
        customer_id=customer_id,
        staff_id=staff_id,
        service_id=service_id,
        start_time=start_time,
        end_time=end_time,
        status="completed",
        price=Decimal("100.00"),
        notes="Test appointment",
    )
    appointment.save()
    return appointment


class TestAppointmentHistoryModel:
    """Tests for AppointmentHistory model."""

    def test_create_appointment_history(self, tenant_id, customer_id, staff_id, service_id):
        """Test creating an appointment history entry."""
        appointment_date = datetime.utcnow()
        
        history = AppointmentHistory(
            tenant_id=tenant_id,
            customer_id=customer_id,
            appointment_id=ObjectId(),
            service_id=service_id,
            staff_id=staff_id,
            appointment_date=appointment_date,
            duration_minutes=60,
            amount_paid=Decimal("100.00"),
            notes="Test history entry",
        )
        history.save()
        
        assert history.id is not None
        assert history.tenant_id == tenant_id
        assert history.customer_id == customer_id
        assert history.service_id == service_id
        assert history.staff_id == staff_id
        assert history.appointment_date == appointment_date
        assert history.duration_minutes == 60
        assert history.amount_paid == Decimal("100.00")
        assert history.notes == "Test history entry"
        assert history.created_at is not None

    def test_appointment_history_without_notes(self, tenant_id, customer_id, staff_id, service_id):
        """Test creating appointment history without notes."""
        appointment_date = datetime.utcnow()
        
        history = AppointmentHistory(
            tenant_id=tenant_id,
            customer_id=customer_id,
            appointment_id=ObjectId(),
            service_id=service_id,
            staff_id=staff_id,
            appointment_date=appointment_date,
            duration_minutes=30,
            amount_paid=Decimal("50.00"),
        )
        history.save()
        
        assert history.notes is None
        assert history.duration_minutes == 30
        assert history.amount_paid == Decimal("50.00")

    def test_appointment_history_zero_amount(self, tenant_id, customer_id, staff_id, service_id):
        """Test creating appointment history with zero amount."""
        appointment_date = datetime.utcnow()
        
        history = AppointmentHistory(
            tenant_id=tenant_id,
            customer_id=customer_id,
            appointment_id=ObjectId(),
            service_id=service_id,
            staff_id=staff_id,
            appointment_date=appointment_date,
            duration_minutes=45,
            amount_paid=Decimal("0.00"),
        )
        history.save()
        
        assert history.amount_paid == Decimal("0.00")

    def test_appointment_history_string_representation(self, tenant_id, customer_id, staff_id, service_id):
        """Test string representation of appointment history."""
        appointment_id = ObjectId()
        
        history = AppointmentHistory(
            tenant_id=tenant_id,
            customer_id=customer_id,
            appointment_id=appointment_id,
            service_id=service_id,
            staff_id=staff_id,
            appointment_date=datetime.utcnow(),
            duration_minutes=60,
            amount_paid=Decimal("100.00"),
        )
        history.save()
        
        assert str(history) == f"AppointmentHistory(customer={customer_id}, appointment={appointment_id})"


class TestAppointmentHistoryService:
    """Tests for AppointmentHistoryService."""

    def test_create_history_from_appointment(self, tenant_id, test_appointment):
        """Test creating history from a completed appointment."""
        history = AppointmentHistoryService.create_history_from_appointment(
            tenant_id=tenant_id,
            appointment_id=test_appointment.id,
        )
        
        assert history.id is not None
        assert history.tenant_id == tenant_id
        assert history.customer_id == test_appointment.customer_id
        assert history.appointment_id == test_appointment.id
        assert history.service_id == test_appointment.service_id
        assert history.staff_id == test_appointment.staff_id
        assert history.appointment_date == test_appointment.start_time
        assert history.duration_minutes == 60
        assert history.amount_paid == Decimal("100.00")
        assert history.notes == "Test appointment"

    def test_create_history_from_incomplete_appointment(self, tenant_id, customer_id, staff_id, service_id, test_service):
        """Test that creating history from incomplete appointment raises error."""
        start_time = datetime.utcnow() + timedelta(days=1, hours=10)
        end_time = start_time + timedelta(hours=1)
        
        appointment = Appointment(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=staff_id,
            service_id=service_id,
            start_time=start_time,
            end_time=end_time,
            status="scheduled",
            price=Decimal("100.00"),
        )
        appointment.save()
        
        with pytest.raises(ValueError, match="not completed"):
            AppointmentHistoryService.create_history_from_appointment(
                tenant_id=tenant_id,
                appointment_id=appointment.id,
            )

    def test_create_history_from_nonexistent_appointment(self, tenant_id):
        """Test that creating history from nonexistent appointment raises error."""
        with pytest.raises(ValueError, match="not found"):
            AppointmentHistoryService.create_history_from_appointment(
                tenant_id=tenant_id,
                appointment_id=ObjectId(),
            )

    def test_get_customer_history(self, tenant_id, customer_id, staff_id, service_id):
        """Test retrieving customer history."""
        # Create multiple history entries
        for i in range(3):
            history = AppointmentHistory(
                tenant_id=tenant_id,
                customer_id=customer_id,
                appointment_id=ObjectId(),
                service_id=service_id,
                staff_id=staff_id,
                appointment_date=datetime.utcnow() - timedelta(days=i),
                duration_minutes=60,
                amount_paid=Decimal("100.00"),
            )
            history.save()
        
        entries, total = AppointmentHistoryService.get_customer_history(
            tenant_id=tenant_id,
            customer_id=customer_id,
            page=1,
            page_size=20,
        )
        
        assert len(entries) == 3
        assert total == 3
        # Verify sorted by appointment_date descending
        assert entries[0].appointment_date > entries[1].appointment_date

    def test_get_customer_history_pagination(self, tenant_id, customer_id, staff_id, service_id):
        """Test customer history pagination."""
        # Create 25 history entries
        for i in range(25):
            history = AppointmentHistory(
                tenant_id=tenant_id,
                customer_id=customer_id,
                appointment_id=ObjectId(),
                service_id=service_id,
                staff_id=staff_id,
                appointment_date=datetime.utcnow() - timedelta(days=i),
                duration_minutes=60,
                amount_paid=Decimal("100.00"),
            )
            history.save()
        
        # Get first page
        entries_page1, total = AppointmentHistoryService.get_customer_history(
            tenant_id=tenant_id,
            customer_id=customer_id,
            page=1,
            page_size=10,
        )
        
        assert len(entries_page1) == 10
        assert total == 25
        
        # Get second page
        entries_page2, total = AppointmentHistoryService.get_customer_history(
            tenant_id=tenant_id,
            customer_id=customer_id,
            page=2,
            page_size=10,
        )
        
        assert len(entries_page2) == 10
        assert total == 25
        
        # Verify different entries
        assert entries_page1[0].id != entries_page2[0].id

    def test_get_history_entry(self, tenant_id, customer_id, staff_id, service_id):
        """Test retrieving a specific history entry."""
        history = AppointmentHistory(
            tenant_id=tenant_id,
            customer_id=customer_id,
            appointment_id=ObjectId(),
            service_id=service_id,
            staff_id=staff_id,
            appointment_date=datetime.utcnow(),
            duration_minutes=60,
            amount_paid=Decimal("100.00"),
        )
        history.save()
        
        retrieved = AppointmentHistoryService.get_history_entry(
            tenant_id=tenant_id,
            history_id=history.id,
        )
        
        assert retrieved is not None
        assert retrieved.id == history.id
        assert retrieved.customer_id == customer_id

    def test_get_history_entry_with_customer_filter(self, tenant_id, customer_id, staff_id, service_id):
        """Test retrieving history entry with customer filter."""
        history = AppointmentHistory(
            tenant_id=tenant_id,
            customer_id=customer_id,
            appointment_id=ObjectId(),
            service_id=service_id,
            staff_id=staff_id,
            appointment_date=datetime.utcnow(),
            duration_minutes=60,
            amount_paid=Decimal("100.00"),
        )
        history.save()
        
        # Retrieve with correct customer
        retrieved = AppointmentHistoryService.get_history_entry(
            tenant_id=tenant_id,
            history_id=history.id,
            customer_id=customer_id,
        )
        
        assert retrieved is not None
        
        # Retrieve with wrong customer
        retrieved = AppointmentHistoryService.get_history_entry(
            tenant_id=tenant_id,
            history_id=history.id,
            customer_id=ObjectId(),
        )
        
        assert retrieved is None

    def test_get_customer_history_stats(self, tenant_id, customer_id, staff_id, service_id):
        """Test getting customer history statistics."""
        # Create history entries with different amounts and durations
        for i in range(3):
            history = AppointmentHistory(
                tenant_id=tenant_id,
                customer_id=customer_id,
                appointment_id=ObjectId(),
                service_id=service_id,
                staff_id=staff_id,
                appointment_date=datetime.utcnow() - timedelta(days=i),
                duration_minutes=60 + (i * 10),
                amount_paid=Decimal("100.00") + Decimal(i * 10),
            )
            history.save()
        
        stats = AppointmentHistoryService.get_customer_history_stats(
            tenant_id=tenant_id,
            customer_id=customer_id,
        )
        
        assert stats["total_appointments"] == 3
        assert stats["total_duration_minutes"] == 180  # 60 + 70 + 80
        assert stats["total_amount_paid"] == 330.0  # 100 + 110 + 120
        assert stats["average_duration_minutes"] == 60.0
        assert stats["first_appointment_date"] is not None
        assert stats["last_appointment_date"] is not None

    def test_get_customer_history_stats_empty(self, tenant_id, customer_id):
        """Test getting history stats for customer with no history."""
        stats = AppointmentHistoryService.get_customer_history_stats(
            tenant_id=tenant_id,
            customer_id=customer_id,
        )
        
        assert stats["total_appointments"] == 0
        assert stats["total_amount_paid"] == 0
        assert stats["total_duration_minutes"] == 0
        assert stats["average_duration_minutes"] == 0
        assert stats["first_appointment_date"] is None
        assert stats["last_appointment_date"] is None

    def test_get_service_history(self, tenant_id, customer_id, staff_id, service_id):
        """Test retrieving customer history for a specific service."""
        other_service_id = ObjectId()
        
        # Create history for service_id
        for i in range(2):
            history = AppointmentHistory(
                tenant_id=tenant_id,
                customer_id=customer_id,
                appointment_id=ObjectId(),
                service_id=service_id,
                staff_id=staff_id,
                appointment_date=datetime.utcnow() - timedelta(days=i),
                duration_minutes=60,
                amount_paid=Decimal("100.00"),
            )
            history.save()
        
        # Create history for other_service_id
        history = AppointmentHistory(
            tenant_id=tenant_id,
            customer_id=customer_id,
            appointment_id=ObjectId(),
            service_id=other_service_id,
            staff_id=staff_id,
            appointment_date=datetime.utcnow(),
            duration_minutes=30,
            amount_paid=Decimal("50.00"),
        )
        history.save()
        
        entries = AppointmentHistoryService.get_service_history(
            tenant_id=tenant_id,
            customer_id=customer_id,
            service_id=service_id,
        )
        
        assert len(entries) == 2
        assert all(entry.service_id == service_id for entry in entries)

    def test_get_staff_history(self, tenant_id, customer_id, staff_id, service_id):
        """Test retrieving customer history with a specific staff member."""
        other_staff_id = ObjectId()
        
        # Create history with staff_id
        for i in range(2):
            history = AppointmentHistory(
                tenant_id=tenant_id,
                customer_id=customer_id,
                appointment_id=ObjectId(),
                service_id=service_id,
                staff_id=staff_id,
                appointment_date=datetime.utcnow() - timedelta(days=i),
                duration_minutes=60,
                amount_paid=Decimal("100.00"),
            )
            history.save()
        
        # Create history with other_staff_id
        history = AppointmentHistory(
            tenant_id=tenant_id,
            customer_id=customer_id,
            appointment_id=ObjectId(),
            service_id=service_id,
            staff_id=other_staff_id,
            appointment_date=datetime.utcnow(),
            duration_minutes=30,
            amount_paid=Decimal("50.00"),
        )
        history.save()
        
        entries = AppointmentHistoryService.get_staff_history(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=staff_id,
        )
        
        assert len(entries) == 2
        assert all(entry.staff_id == staff_id for entry in entries)
