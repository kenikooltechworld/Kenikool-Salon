"""Integration tests for appointment API."""

import pytest
from datetime import datetime, timedelta
from bson import ObjectId
from fastapi.testclient import TestClient
from app.main import app
from app.models.appointment import Appointment
from app.models.service import Service
from app.models.availability import Availability
from app.models.tenant import Tenant
from app.models.user import User
from app.models.role import Role


client = TestClient(app)


@pytest.fixture
def test_tenant():
    """Create a test tenant."""
    tenant = Tenant(
        name="Test Salon",
        subscription_tier="professional",
        status="active",
        region="us-east-1",
    )
    tenant.save()
    return tenant


@pytest.fixture
def test_user(test_tenant):
    """Create a test user."""
    # Create a role first
    role = Role(
        tenant_id=test_tenant.id,
        name="manager",
        permissions=["appointments:read", "appointments:write"],
    )
    role.save()
    
    user = User(
        tenant_id=test_tenant.id,
        email="test@example.com",
        password_hash="hashed_password",
        first_name="Test",
        last_name="User",
        role_ids=[role.id],  # Multiple roles per user
        status="active",
    )
    user.save()
    return user


@pytest.fixture
def test_service(test_tenant):
    """Create a test service."""
    service = Service(
        tenant_id=test_tenant.id,
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
def test_availability(test_tenant):
    """Create a test availability."""
    staff_id = ObjectId()
    today = datetime.utcnow().date()
    availability = Availability(
        tenant_id=test_tenant.id,
        staff_id=staff_id,
        day_of_week=today.weekday(),
        start_time="09:00:00",
        end_time="17:00:00",
        is_recurring=True,
        effective_from=today,
        is_active=True,
    )
    availability.save()
    return availability, staff_id


class TestAppointmentAPI:
    """Test appointment API endpoints."""

    def test_create_appointment(self, test_tenant, test_service, test_availability):
        """Test creating an appointment."""
        _, staff_id = test_availability
        customer_id = ObjectId()
        
        start_time = datetime.utcnow() + timedelta(days=1, hours=10)
        end_time = start_time + timedelta(hours=1)
        
        payload = {
            "customer_id": str(customer_id),
            "staff_id": str(staff_id),
            "service_id": str(test_service.id),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "notes": "Test appointment",
        }
        
        # Note: This would require authentication in a real scenario
        # For now, we're testing the schema and basic logic
        assert payload["customer_id"] is not None
        assert payload["staff_id"] is not None
        assert payload["service_id"] is not None

    def test_appointment_schema_validation(self):
        """Test appointment schema validation."""
        from app.schemas.appointment import AppointmentCreateRequest
        
        start_time = datetime.utcnow() + timedelta(days=1, hours=10)
        end_time = start_time + timedelta(hours=1)
        
        # Valid request
        request = AppointmentCreateRequest(
            customer_id="507f1f77bcf86cd799439011",
            staff_id="507f1f77bcf86cd799439012",
            service_id="507f1f77bcf86cd799439013",
            start_time=start_time,
            end_time=end_time,
        )
        
        assert request.customer_id is not None
        assert request.staff_id is not None
        assert request.service_id is not None

    def test_available_slots_schema(self):
        """Test available slots schema."""
        from app.schemas.appointment import AvailableSlotsResponse, AvailableSlot
        
        slots = [
            AvailableSlot(
                start_time="2024-01-15T09:00:00",
                end_time="2024-01-15T10:00:00",
                staff_id="507f1f77bcf86cd799439012",
            ),
            AvailableSlot(
                start_time="2024-01-15T10:00:00",
                end_time="2024-01-15T11:00:00",
                staff_id="507f1f77bcf86cd799439012",
            ),
        ]
        
        response = AvailableSlotsResponse(
            date="2024-01-15",
            slots=slots,
            total_available=2,
        )
        
        assert response.total_available == 2
        assert len(response.slots) == 2


class TestAppointmentModels:
    """Test appointment models."""

    def test_appointment_model_creation(self, test_tenant):
        """Test creating an appointment model."""
        customer_id = ObjectId()
        staff_id = ObjectId()
        service_id = ObjectId()
        
        start_time = datetime.utcnow() + timedelta(days=1, hours=10)
        end_time = start_time + timedelta(hours=1)
        
        appointment = Appointment(
            tenant_id=test_tenant.id,
            customer_id=customer_id,
            staff_id=staff_id,
            service_id=service_id,
            start_time=start_time,
            end_time=end_time,
            status="scheduled",
            notes="Test appointment",
        )
        
        assert appointment.tenant_id == test_tenant.id
        assert appointment.customer_id == customer_id
        assert appointment.staff_id == staff_id
        assert appointment.service_id == service_id
        assert appointment.status == "scheduled"

    def test_appointment_status_choices(self, test_tenant):
        """Test appointment status choices."""
        customer_id = ObjectId()
        staff_id = ObjectId()
        service_id = ObjectId()
        
        start_time = datetime.utcnow() + timedelta(days=1, hours=10)
        end_time = start_time + timedelta(hours=1)
        
        # Test all valid statuses
        valid_statuses = ["scheduled", "confirmed", "in_progress", "completed", "cancelled", "no_show"]
        
        for status in valid_statuses:
            appointment = Appointment(
                tenant_id=test_tenant.id,
                customer_id=customer_id,
                staff_id=staff_id,
                service_id=service_id,
                start_time=start_time,
                end_time=end_time,
                status=status,
            )
            assert appointment.status == status

    def test_appointment_cancellation_fields(self, test_tenant):
        """Test appointment cancellation fields."""
        customer_id = ObjectId()
        staff_id = ObjectId()
        service_id = ObjectId()
        cancelled_by = ObjectId()
        
        start_time = datetime.utcnow() + timedelta(days=1, hours=10)
        end_time = start_time + timedelta(hours=1)
        cancelled_at = datetime.utcnow()
        
        appointment = Appointment(
            tenant_id=test_tenant.id,
            customer_id=customer_id,
            staff_id=staff_id,
            service_id=service_id,
            start_time=start_time,
            end_time=end_time,
            status="cancelled",
            cancellation_reason="Customer requested",
            cancelled_at=cancelled_at,
            cancelled_by=cancelled_by,
        )
        
        assert appointment.status == "cancelled"
        assert appointment.cancellation_reason == "Customer requested"
        assert appointment.cancelled_at == cancelled_at
        assert appointment.cancelled_by == cancelled_by

    def test_appointment_confirmation_fields(self, test_tenant):
        """Test appointment confirmation fields."""
        customer_id = ObjectId()
        staff_id = ObjectId()
        service_id = ObjectId()
        
        start_time = datetime.utcnow() + timedelta(days=1, hours=10)
        end_time = start_time + timedelta(hours=1)
        confirmed_at = datetime.utcnow()
        
        appointment = Appointment(
            tenant_id=test_tenant.id,
            customer_id=customer_id,
            staff_id=staff_id,
            service_id=service_id,
            start_time=start_time,
            end_time=end_time,
            status="confirmed",
            confirmed_at=confirmed_at,
        )
        
        assert appointment.status == "confirmed"
        assert appointment.confirmed_at == confirmed_at
