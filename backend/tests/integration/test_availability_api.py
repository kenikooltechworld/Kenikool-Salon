"""Integration tests for availability API endpoints."""

import pytest
from datetime import datetime, date, time, timedelta
from bson import ObjectId
from fastapi.testclient import TestClient
from app.main import app
from app.models.availability import Availability
from app.models.service import Service
from app.models.tenant import Tenant
from app.models.user import User
from app.context import set_tenant_id, get_tenant_id
from app.services.auth_service import AuthService


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


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
    user = User(
        tenant_id=test_tenant.id,
        email="test@example.com",
        password_hash=AuthService.hash_password("password123"),
        first_name="Test",
        last_name="User",
        role_id=ObjectId(),
        status="active",
    )
    user.save()
    return user


@pytest.fixture
def auth_headers(client, test_user, test_tenant):
    """Get authentication headers."""
    # Create a token for the test user
    token = AuthService.create_token(
        user_id=str(test_user.id),
        tenant_id=str(test_tenant.id),
        role="manager",
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_service(test_tenant):
    """Create a test service."""
    service = Service(
        tenant_id=test_tenant.id,
        name="Haircut",
        description="Professional haircut",
        duration_minutes=30,
        price=50.00,
        category="Hair",
        is_active=True,
    )
    service.save()
    return service


@pytest.fixture
def test_staff_id():
    """Create a test staff ID."""
    return ObjectId()


class TestAvailabilityEndpoints:
    """Test availability API endpoints."""

    def test_create_recurring_availability(self, client, auth_headers, test_tenant, test_staff_id):
        """Test creating a recurring availability."""
        payload = {
            "staff_id": str(test_staff_id),
            "day_of_week": 0,
            "start_time": "09:00:00",
            "end_time": "17:00:00",
            "is_recurring": True,
            "effective_from": date.today().isoformat(),
            "is_active": True,
        }

        response = client.post(
            "/v1/availability",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["staff_id"] == str(test_staff_id)
        assert data["day_of_week"] == 0
        assert data["is_recurring"] is True
        assert data["is_active"] is True

    def test_create_custom_date_range_availability(self, client, auth_headers, test_tenant, test_staff_id):
        """Test creating a custom date range availability."""
        start_date = date.today()
        end_date = start_date + timedelta(days=30)

        payload = {
            "staff_id": str(test_staff_id),
            "start_time": "10:00:00",
            "end_time": "18:00:00",
            "is_recurring": False,
            "effective_from": start_date.isoformat(),
            "effective_to": end_date.isoformat(),
            "is_active": True,
        }

        response = client.post(
            "/v1/availability",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_recurring"] is False
        assert data["effective_to"] == end_date.isoformat()

    def test_create_availability_with_breaks(self, client, auth_headers, test_tenant, test_staff_id):
        """Test creating availability with break times."""
        payload = {
            "staff_id": str(test_staff_id),
            "day_of_week": 1,
            "start_time": "09:00:00",
            "end_time": "17:00:00",
            "is_recurring": True,
            "effective_from": date.today().isoformat(),
            "breaks": [
                {"start_time": "12:00:00", "end_time": "13:00:00"},
                {"start_time": "15:00:00", "end_time": "15:30:00"},
            ],
            "is_active": True,
        }

        response = client.post(
            "/v1/availability",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["breaks"]) == 2

    def test_create_availability_invalid_time_range(self, client, auth_headers, test_tenant, test_staff_id):
        """Test creating availability with invalid time range."""
        payload = {
            "staff_id": str(test_staff_id),
            "day_of_week": 0,
            "start_time": "17:00:00",
            "end_time": "09:00:00",  # End before start
            "is_recurring": True,
            "effective_from": date.today().isoformat(),
        }

        response = client.post(
            "/v1/availability",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 400

    def test_create_recurring_without_day_of_week(self, client, auth_headers, test_tenant, test_staff_id):
        """Test creating recurring availability without day_of_week."""
        payload = {
            "staff_id": str(test_staff_id),
            "start_time": "09:00:00",
            "end_time": "17:00:00",
            "is_recurring": True,
            "effective_from": date.today().isoformat(),
        }

        response = client.post(
            "/v1/availability",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 400

    def test_get_availability(self, client, auth_headers, test_tenant, test_staff_id):
        """Test getting a specific availability."""
        # Create availability
        availability = Availability(
            tenant_id=test_tenant.id,
            staff_id=test_staff_id,
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(17, 0),
            is_recurring=True,
            effective_from=date.today(),
        )
        availability.save()

        response = client.get(
            f"/v1/availability/{availability.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(availability.id)
        assert data["staff_id"] == str(test_staff_id)

    def test_get_nonexistent_availability(self, client, auth_headers):
        """Test getting a nonexistent availability."""
        fake_id = ObjectId()

        response = client.get(
            f"/v1/availability/{fake_id}",
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_list_availability(self, client, auth_headers, test_tenant, test_staff_id):
        """Test listing availability."""
        # Create multiple availabilities
        for day in range(3):
            availability = Availability(
                tenant_id=test_tenant.id,
                staff_id=test_staff_id,
                day_of_week=day,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_recurring=True,
                effective_from=date.today(),
            )
            availability.save()

        response = client.get(
            "/v1/availability",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 3
        assert len(data["availabilities"]) >= 3

    def test_list_availability_filter_by_staff(self, client, auth_headers, test_tenant, test_staff_id):
        """Test listing availability filtered by staff."""
        # Create availability for test staff
        availability = Availability(
            tenant_id=test_tenant.id,
            staff_id=test_staff_id,
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(17, 0),
            is_recurring=True,
            effective_from=date.today(),
        )
        availability.save()

        response = client.get(
            f"/v1/availability?staff_id={test_staff_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        for avail in data["availabilities"]:
            assert avail["staff_id"] == str(test_staff_id)

    def test_list_availability_filter_by_recurring(self, client, auth_headers, test_tenant, test_staff_id):
        """Test listing availability filtered by recurring status."""
        # Create recurring availability
        recurring = Availability(
            tenant_id=test_tenant.id,
            staff_id=test_staff_id,
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(17, 0),
            is_recurring=True,
            effective_from=date.today(),
        )
        recurring.save()

        response = client.get(
            "/v1/availability?is_recurring=true",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        for avail in data["availabilities"]:
            assert avail["is_recurring"] is True

    def test_update_availability(self, client, auth_headers, test_tenant, test_staff_id):
        """Test updating an availability."""
        # Create availability
        availability = Availability(
            tenant_id=test_tenant.id,
            staff_id=test_staff_id,
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(17, 0),
            is_recurring=True,
            effective_from=date.today(),
            is_active=True,
        )
        availability.save()

        payload = {
            "is_active": False,
            "notes": "Updated notes",
        }

        response = client.put(
            f"/v1/availability/{availability.id}",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False
        assert data["notes"] == "Updated notes"

    def test_delete_availability(self, client, auth_headers, test_tenant, test_staff_id):
        """Test deleting an availability."""
        # Create availability
        availability = Availability(
            tenant_id=test_tenant.id,
            staff_id=test_staff_id,
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(17, 0),
            is_recurring=True,
            effective_from=date.today(),
        )
        availability.save()

        response = client.delete(
            f"/v1/availability/{availability.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200

        # Verify it's deleted
        deleted = Availability.objects(id=availability.id).first()
        assert deleted is None

    def test_get_available_slots(self, client, auth_headers, test_tenant, test_staff_id, test_service):
        """Test getting available slots."""
        # Create availability for today
        today = date.today()
        availability = Availability(
            tenant_id=test_tenant.id,
            staff_id=test_staff_id,
            day_of_week=today.weekday(),
            start_time=time(9, 0),
            end_time=time(17, 0),
            is_recurring=True,
            effective_from=today,
        )
        availability.save()

        response = client.get(
            f"/v1/availability/slots/available?staff_id={test_staff_id}&service_id={test_service.id}&target_date={today.isoformat()}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["date"] == today.isoformat()
        assert data["staff_id"] == str(test_staff_id)
        assert data["total_slots"] > 0
        assert len(data["slots"]) > 0

    def test_get_available_slots_with_breaks(self, client, auth_headers, test_tenant, test_staff_id, test_service):
        """Test getting available slots with breaks."""
        today = date.today()
        availability = Availability(
            tenant_id=test_tenant.id,
            staff_id=test_staff_id,
            day_of_week=today.weekday(),
            start_time=time(9, 0),
            end_time=time(17, 0),
            is_recurring=True,
            effective_from=today,
            breaks=[
                {"start_time": time(12, 0), "end_time": time(13, 0)},
            ],
        )
        availability.save()

        response = client.get(
            f"/v1/availability/slots/available?staff_id={test_staff_id}&service_id={test_service.id}&target_date={today.isoformat()}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        # Verify no slots during break time
        for slot in data["slots"]:
            slot_start = datetime.fromisoformat(slot["start_time"])
            slot_end = datetime.fromisoformat(slot["end_time"])
            break_start = datetime.combine(today, time(12, 0))
            break_end = datetime.combine(today, time(13, 0))
            # Slot should not overlap with break
            assert not (slot_start < break_end and slot_end > break_start)

    def test_get_available_slots_no_availability(self, client, auth_headers, test_tenant, test_staff_id, test_service):
        """Test getting available slots when no availability exists."""
        today = date.today()

        response = client.get(
            f"/v1/availability/slots/available?staff_id={test_staff_id}&service_id={test_service.id}&target_date={today.isoformat()}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_slots"] == 0
        assert len(data["slots"]) == 0

    def test_get_available_slots_invalid_date_format(self, client, auth_headers, test_tenant, test_staff_id, test_service):
        """Test getting available slots with invalid date format."""
        response = client.get(
            f"/v1/availability/slots/available?staff_id={test_staff_id}&service_id={test_service.id}&target_date=invalid-date",
            headers=auth_headers,
        )

        assert response.status_code == 400

    def test_get_available_slots_nonexistent_service(self, client, auth_headers, test_tenant, test_staff_id):
        """Test getting available slots for nonexistent service."""
        today = date.today()
        fake_service_id = ObjectId()

        response = client.get(
            f"/v1/availability/slots/available?staff_id={test_staff_id}&service_id={fake_service_id}&target_date={today.isoformat()}",
            headers=auth_headers,
        )

        assert response.status_code == 404
