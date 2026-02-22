"""Integration tests for appointment history API endpoints."""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from bson import ObjectId
from fastapi.testclient import TestClient
from app.main import create_app
from app.models.appointment_history import AppointmentHistory
from app.models.appointment import Appointment
from app.models.service import Service
from app.models.customer import Customer
from app.models.staff import Staff
from app.models.tenant import Tenant
from app.models.user import User
from app.models.role import Role


@pytest.fixture
def app():
    """Create test app."""
    return create_app()


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def tenant():
    """Create a test tenant."""
    tenant = Tenant(
        name="Test Salon",
        subscription_tier="professional",
        status="active",
    )
    tenant.save()
    return tenant


@pytest.fixture
def user(tenant):
    """Create a test user."""
    user = User(
        tenant_id=tenant.id,
        email="test@example.com",
        password_hash="hashed_password",
        first_name="Test",
        last_name="User",
        role_id=ObjectId(),
        status="active",
    )
    user.save()
    return user


@pytest.fixture
def customer(tenant):
    """Create a test customer."""
    customer = Customer(
        tenant_id=tenant.id,
        first_name="John",
        last_name="Doe",
        email="customer@example.com",
        phone="+234123456789",
    )
    customer.save()
    return customer


@pytest.fixture
def staff(tenant):
    """Create a test staff member."""
    staff = Staff(
        tenant_id=tenant.id,
        first_name="Jane",
        last_name="Smith",
        email="staff@example.com",
        phone="+234987654321",
        role="stylist",
        status="active",
    )
    staff.save()
    return staff


@pytest.fixture
def service(tenant):
    """Create a test service."""
    service = Service(
        tenant_id=tenant.id,
        name="Haircut",
        description="Professional haircut",
        duration_minutes=60,
        price=Decimal("100.00"),
        category="haircut",
    )
    service.save()
    return service


@pytest.fixture
def completed_appointment(tenant, customer, staff, service):
    """Create a completed appointment."""
    start_time = datetime.utcnow() - timedelta(days=1)
    end_time = start_time + timedelta(hours=1)
    
    appointment = Appointment(
        tenant_id=tenant.id,
        customer_id=customer.id,
        staff_id=staff.id,
        service_id=service.id,
        start_time=start_time,
        end_time=end_time,
        status="completed",
        price=Decimal("100.00"),
        notes="Great service",
    )
    appointment.save()
    return appointment


@pytest.fixture
def history_entry(tenant, customer, staff, service, completed_appointment):
    """Create a history entry."""
    history = AppointmentHistory(
        tenant_id=tenant.id,
        customer_id=customer.id,
        appointment_id=completed_appointment.id,
        service_id=service.id,
        staff_id=staff.id,
        appointment_date=completed_appointment.start_time,
        duration_minutes=60,
        amount_paid=Decimal("100.00"),
        notes="Great service",
    )
    history.save()
    return history


class TestAppointmentHistoryAPI:
    """Tests for appointment history API endpoints."""

    def test_get_customer_history_empty(self, client, tenant, customer):
        """Test getting history for customer with no appointments."""
        response = client.get(
            f"/v1/customers/{customer.id}/history",
            headers={"X-Tenant-ID": str(tenant.id)},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["history"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["page_size"] == 20

    def test_get_customer_history_with_entries(self, client, tenant, customer, staff, service):
        """Test getting history for customer with appointments."""
        # Create multiple history entries
        for i in range(3):
            history = AppointmentHistory(
                tenant_id=tenant.id,
                customer_id=customer.id,
                appointment_id=ObjectId(),
                service_id=service.id,
                staff_id=staff.id,
                appointment_date=datetime.utcnow() - timedelta(days=i),
                duration_minutes=60,
                amount_paid=Decimal("100.00"),
            )
            history.save()
        
        response = client.get(
            f"/v1/customers/{customer.id}/history",
            headers={"X-Tenant-ID": str(tenant.id)},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["history"]) == 3
        assert data["total"] == 3
        assert data["page"] == 1
        assert data["page_size"] == 20

    def test_get_customer_history_pagination(self, client, tenant, customer, staff, service):
        """Test history pagination."""
        # Create 25 history entries
        for i in range(25):
            history = AppointmentHistory(
                tenant_id=tenant.id,
                customer_id=customer.id,
                appointment_id=ObjectId(),
                service_id=service.id,
                staff_id=staff.id,
                appointment_date=datetime.utcnow() - timedelta(days=i),
                duration_minutes=60,
                amount_paid=Decimal("100.00"),
            )
            history.save()
        
        # Get first page
        response = client.get(
            f"/v1/customers/{customer.id}/history?page=1&page_size=10",
            headers={"X-Tenant-ID": str(tenant.id)},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["history"]) == 10
        assert data["total"] == 25
        assert data["page"] == 1
        assert data["page_size"] == 10
        
        # Get second page
        response = client.get(
            f"/v1/customers/{customer.id}/history?page=2&page_size=10",
            headers={"X-Tenant-ID": str(tenant.id)},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["history"]) == 10
        assert data["total"] == 25
        assert data["page"] == 2

    def test_get_customer_history_invalid_customer_id(self, client, tenant):
        """Test getting history with invalid customer ID."""
        response = client.get(
            "/v1/customers/invalid_id/history",
            headers={"X-Tenant-ID": str(tenant.id)},
        )
        
        assert response.status_code == 400

    def test_get_history_entry(self, client, tenant, customer, history_entry):
        """Test getting a specific history entry."""
        response = client.get(
            f"/v1/customers/{customer.id}/history/{history_entry.id}",
            headers={"X-Tenant-ID": str(tenant.id)},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(history_entry.id)
        assert data["customer_id"] == str(customer.id)
        assert data["appointment_id"] == str(history_entry.appointment_id)
        assert data["service_id"] == str(history_entry.service_id)
        assert data["staff_id"] == str(history_entry.staff_id)
        assert data["duration_minutes"] == 60
        assert data["amount_paid"] == "100.00"
        assert data["notes"] == "Great service"

    def test_get_history_entry_not_found(self, client, tenant, customer):
        """Test getting nonexistent history entry."""
        response = client.get(
            f"/v1/customers/{customer.id}/history/{ObjectId()}",
            headers={"X-Tenant-ID": str(tenant.id)},
        )
        
        assert response.status_code == 404

    def test_get_history_entry_invalid_ids(self, client, tenant):
        """Test getting history entry with invalid IDs."""
        response = client.get(
            "/v1/customers/invalid_customer/history/invalid_history",
            headers={"X-Tenant-ID": str(tenant.id)},
        )
        
        assert response.status_code == 400

    def test_get_history_entry_wrong_customer(self, client, tenant, customer, staff, service):
        """Test getting history entry for wrong customer."""
        # Create history for one customer
        history = AppointmentHistory(
            tenant_id=tenant.id,
            customer_id=customer.id,
            appointment_id=ObjectId(),
            service_id=service.id,
            staff_id=staff.id,
            appointment_date=datetime.utcnow(),
            duration_minutes=60,
            amount_paid=Decimal("100.00"),
        )
        history.save()
        
        # Try to get with different customer
        other_customer = Customer(
            tenant_id=tenant.id,
            first_name="Jane",
            last_name="Doe",
            email="other@example.com",
            phone="+234111111111",
        )
        other_customer.save()
        
        response = client.get(
            f"/v1/customers/{other_customer.id}/history/{history.id}",
            headers={"X-Tenant-ID": str(tenant.id)},
        )
        
        assert response.status_code == 404

    def test_history_entry_response_format(self, client, tenant, customer, history_entry):
        """Test that history entry response has correct format."""
        response = client.get(
            f"/v1/customers/{customer.id}/history/{history_entry.id}",
            headers={"X-Tenant-ID": str(tenant.id)},
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all required fields are present
        required_fields = [
            "id",
            "customer_id",
            "appointment_id",
            "service_id",
            "staff_id",
            "appointment_date",
            "duration_minutes",
            "amount_paid",
            "notes",
            "created_at",
        ]
        
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_history_list_response_format(self, client, tenant, customer, staff, service):
        """Test that history list response has correct format."""
        # Create a history entry
        history = AppointmentHistory(
            tenant_id=tenant.id,
            customer_id=customer.id,
            appointment_id=ObjectId(),
            service_id=service.id,
            staff_id=staff.id,
            appointment_date=datetime.utcnow(),
            duration_minutes=60,
            amount_paid=Decimal("100.00"),
        )
        history.save()
        
        response = client.get(
            f"/v1/customers/{customer.id}/history",
            headers={"X-Tenant-ID": str(tenant.id)},
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify list response format
        assert "history" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        
        # Verify each entry has required fields
        for entry in data["history"]:
            required_fields = [
                "id",
                "customer_id",
                "appointment_id",
                "service_id",
                "staff_id",
                "appointment_date",
                "duration_minutes",
                "amount_paid",
                "created_at",
            ]
            
            for field in required_fields:
                assert field in entry, f"Missing field in entry: {field}"

    def test_history_sorted_by_date_descending(self, client, tenant, customer, staff, service):
        """Test that history is sorted by appointment_date descending."""
        # Create history entries with different dates
        dates = [
            datetime.utcnow() - timedelta(days=2),
            datetime.utcnow() - timedelta(days=1),
            datetime.utcnow(),
        ]
        
        for date in dates:
            history = AppointmentHistory(
                tenant_id=tenant.id,
                customer_id=customer.id,
                appointment_id=ObjectId(),
                service_id=service.id,
                staff_id=staff.id,
                appointment_date=date,
                duration_minutes=60,
                amount_paid=Decimal("100.00"),
            )
            history.save()
        
        response = client.get(
            f"/v1/customers/{customer.id}/history",
            headers={"X-Tenant-ID": str(tenant.id)},
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify sorted descending
        for i in range(len(data["history"]) - 1):
            current_date = datetime.fromisoformat(data["history"][i]["appointment_date"])
            next_date = datetime.fromisoformat(data["history"][i + 1]["appointment_date"])
            assert current_date >= next_date
