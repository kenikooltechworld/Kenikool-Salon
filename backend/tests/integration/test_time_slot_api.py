"""Integration tests for time slot reservation API."""

import pytest
from datetime import datetime, timedelta
from bson import ObjectId
from fastapi.testclient import TestClient
from app.main import app
from app.models.service import Service
from app.models.appointment import Appointment


client = TestClient(app)


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


class TestTimeSlotReservationAPI:
    """Test time slot reservation API."""

    def test_reserve_time_slot_success(
        self, tenant_id, staff_id, service_id, customer_id, test_service
    ):
        """Test successful time slot reservation."""
        start_time = (datetime.utcnow() + timedelta(days=1)).isoformat()
        end_time = (datetime.utcnow() + timedelta(days=1, hours=1)).isoformat()
        
        response = client.post(
            "/api/v1/time-slots",
            json={
                "staff_id": str(staff_id),
                "service_id": str(service_id),
                "start_time": start_time,
                "end_time": end_time,
                "customer_id": str(customer_id),
            },
            headers={"X-Tenant-ID": str(tenant_id)},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "reserved"
        assert data["staff_id"] == str(staff_id)
        assert data["service_id"] == str(service_id)
        assert data["customer_id"] == str(customer_id)

    def test_reserve_time_slot_without_customer(
        self, tenant_id, staff_id, service_id, test_service
    ):
        """Test time slot reservation without customer ID."""
        start_time = (datetime.utcnow() + timedelta(days=1)).isoformat()
        end_time = (datetime.utcnow() + timedelta(days=1, hours=1)).isoformat()
        
        response = client.post(
            "/api/v1/time-slots",
            json={
                "staff_id": str(staff_id),
                "service_id": str(service_id),
                "start_time": start_time,
                "end_time": end_time,
            },
            headers={"X-Tenant-ID": str(tenant_id)},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "reserved"
        assert data["customer_id"] is None

    def test_reserve_time_slot_conflict(
        self, tenant_id, staff_id, service_id, customer_id, test_service
    ):
        """Test that overlapping reservations are prevented."""
        start_time = datetime.utcnow() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        # Create first reservation
        client.post(
            "/api/v1/time-slots",
            json={
                "staff_id": str(staff_id),
                "service_id": str(service_id),
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "customer_id": str(customer_id),
            },
            headers={"X-Tenant-ID": str(tenant_id)},
        )
        
        # Try to create overlapping reservation
        response = client.post(
            "/api/v1/time-slots",
            json={
                "staff_id": str(staff_id),
                "service_id": str(service_id),
                "start_time": (start_time + timedelta(minutes=30)).isoformat(),
                "end_time": (end_time + timedelta(minutes=30)).isoformat(),
                "customer_id": str(customer_id),
            },
            headers={"X-Tenant-ID": str(tenant_id)},
        )
        
        assert response.status_code == 409


class TestTimeSlotConfirmationAPI:
    """Test time slot confirmation API."""

    def test_confirm_time_slot_success(
        self, tenant_id, staff_id, service_id, customer_id, test_service
    ):
        """Test successful time slot confirmation."""
        start_time = datetime.utcnow() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        # Reserve slot
        reserve_response = client.post(
            "/api/v1/time-slots",
            json={
                "staff_id": str(staff_id),
                "service_id": str(service_id),
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "customer_id": str(customer_id),
            },
            headers={"X-Tenant-ID": str(tenant_id)},
        )
        
        time_slot_id = reserve_response.json()["id"]
        
        # Create appointment
        appt_response = client.post(
            "/api/v1/appointments",
            json={
                "customer_id": str(customer_id),
                "staff_id": str(staff_id),
                "service_id": str(service_id),
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
            },
            headers={"X-Tenant-ID": str(tenant_id)},
        )
        
        appointment_id = appt_response.json()["id"]
        
        # Confirm time slot
        response = client.post(
            f"/api/v1/time-slots/{time_slot_id}/confirm",
            json={"appointment_id": appointment_id},
            headers={"X-Tenant-ID": str(tenant_id)},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "confirmed"
        assert data["appointment_id"] == appointment_id


class TestTimeSlotReleaseAPI:
    """Test time slot release API."""

    def test_release_time_slot_success(
        self, tenant_id, staff_id, service_id, customer_id, test_service
    ):
        """Test successful time slot release."""
        start_time = datetime.utcnow() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        # Reserve slot
        reserve_response = client.post(
            "/api/v1/time-slots",
            json={
                "staff_id": str(staff_id),
                "service_id": str(service_id),
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "customer_id": str(customer_id),
            },
            headers={"X-Tenant-ID": str(tenant_id)},
        )
        
        time_slot_id = reserve_response.json()["id"]
        
        # Release slot
        response = client.post(
            f"/api/v1/time-slots/{time_slot_id}/release",
            json={"reason": "Customer cancelled"},
            headers={"X-Tenant-ID": str(tenant_id)},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "released"


class TestTimeSlotListingAPI:
    """Test time slot listing API."""

    def test_list_active_reservations(
        self, tenant_id, staff_id, service_id, customer_id, test_service
    ):
        """Test listing active reservations."""
        start_time = datetime.utcnow() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        # Create multiple reservations
        for i in range(3):
            client.post(
                "/api/v1/time-slots",
                json={
                    "staff_id": str(staff_id),
                    "service_id": str(service_id),
                    "start_time": (start_time + timedelta(hours=i)).isoformat(),
                    "end_time": (end_time + timedelta(hours=i)).isoformat(),
                    "customer_id": str(customer_id),
                },
                headers={"X-Tenant-ID": str(tenant_id)},
            )
        
        # List active reservations
        response = client.get(
            "/api/v1/time-slots",
            headers={"X-Tenant-ID": str(tenant_id)},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 3
        assert all(slot["status"] == "reserved" for slot in data["time_slots"])

    def test_list_active_reservations_by_staff(
        self, tenant_id, staff_id, service_id, customer_id, test_service
    ):
        """Test listing active reservations filtered by staff."""
        start_time = datetime.utcnow() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        other_staff_id = ObjectId()
        
        # Create reservation for first staff
        client.post(
            "/api/v1/time-slots",
            json={
                "staff_id": str(staff_id),
                "service_id": str(service_id),
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "customer_id": str(customer_id),
            },
            headers={"X-Tenant-ID": str(tenant_id)},
        )
        
        # Create reservation for other staff
        client.post(
            "/api/v1/time-slots",
            json={
                "staff_id": str(other_staff_id),
                "service_id": str(service_id),
                "start_time": (start_time + timedelta(hours=2)).isoformat(),
                "end_time": (end_time + timedelta(hours=2)).isoformat(),
                "customer_id": str(customer_id),
            },
            headers={"X-Tenant-ID": str(tenant_id)},
        )
        
        # List reservations for first staff only
        response = client.get(
            "/api/v1/time-slots",
            params={"staff_id": str(staff_id)},
            headers={"X-Tenant-ID": str(tenant_id)},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(slot["staff_id"] == str(staff_id) for slot in data["time_slots"])
