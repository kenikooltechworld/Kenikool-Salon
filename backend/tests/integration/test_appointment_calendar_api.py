"""Integration tests for appointment calendar and listing endpoints."""

import pytest
from datetime import datetime, timedelta
from bson import ObjectId
from fastapi.testclient import TestClient
from app.main import app
from app.models.appointment import Appointment
from app.models.service import Service
from app.models.availability import Availability


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


@pytest.fixture
def test_availability(tenant_id, staff_id):
    """Create test availability."""
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


class TestCalendarAvailabilityEndpoint:
    """Test calendar availability endpoint."""

    def test_get_calendar_availability_success(
        self, tenant_id, staff_id, service_id, test_service, test_availability
    ):
        """Test successful calendar availability retrieval."""
        start_date = datetime.utcnow().date().isoformat()
        end_date = (datetime.utcnow().date() + timedelta(days=7)).isoformat()
        
        response = client.get(
            f"/api/v1/appointments/calendar/availability",
            params={
                "staff_id": str(staff_id),
                "service_id": str(service_id),
                "start_date": start_date,
                "end_date": end_date,
                "timezone": "UTC",
            },
            headers={"X-Tenant-ID": str(tenant_id)},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "availability" in data
        assert "start_date" in data
        assert "end_date" in data
        assert "timezone" in data

    def test_get_calendar_availability_without_staff(self, tenant_id):
        """Test calendar availability without staff ID."""
        response = client.get(
            f"/api/v1/appointments/calendar/availability",
            params={
                "timezone": "UTC",
            },
            headers={"X-Tenant-ID": str(tenant_id)},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["availability"] == {}


class TestDayViewEndpoint:
    """Test day view endpoint."""

    def test_get_day_view_success(
        self, tenant_id, staff_id, service_id, customer_id, test_service
    ):
        """Test successful day view retrieval."""
        # Create appointment for today
        today = datetime.utcnow().replace(hour=10, minute=0, second=0, microsecond=0)
        appointment = Appointment(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=staff_id,
            service_id=service_id,
            start_time=today,
            end_time=today + timedelta(hours=1),
            status="confirmed",
        )
        appointment.save()
        
        date_str = today.date().isoformat()
        response = client.get(
            f"/api/v1/appointments/day/{date_str}",
            headers={"X-Tenant-ID": str(tenant_id)},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["date"] == date_str
        assert "appointments" in data
        assert data["total"] >= 1

    def test_get_day_view_with_staff_filter(
        self, tenant_id, staff_id, service_id, customer_id, test_service
    ):
        """Test day view with staff filter."""
        today = datetime.utcnow().replace(hour=10, minute=0, second=0, microsecond=0)
        other_staff_id = ObjectId()
        
        # Create appointment for first staff
        appointment = Appointment(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=staff_id,
            service_id=service_id,
            start_time=today,
            end_time=today + timedelta(hours=1),
            status="confirmed",
        )
        appointment.save()
        
        # Create appointment for other staff
        other_appointment = Appointment(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=other_staff_id,
            service_id=service_id,
            start_time=today + timedelta(hours=2),
            end_time=today + timedelta(hours=3),
            status="confirmed",
        )
        other_appointment.save()
        
        date_str = today.date().isoformat()
        response = client.get(
            f"/api/v1/appointments/day/{date_str}",
            params={"staff_id": str(staff_id)},
            headers={"X-Tenant-ID": str(tenant_id)},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(appt["staff_id"] == str(staff_id) for appt in data["appointments"])


class TestWeekViewEndpoint:
    """Test week view endpoint."""

    def test_get_week_view_success(
        self, tenant_id, staff_id, service_id, customer_id, test_service
    ):
        """Test successful week view retrieval."""
        # Create appointments for this week
        today = datetime.utcnow().replace(hour=10, minute=0, second=0, microsecond=0)
        
        for i in range(3):
            appointment = Appointment(
                tenant_id=tenant_id,
                customer_id=customer_id,
                staff_id=staff_id,
                service_id=service_id,
                start_time=today + timedelta(days=i),
                end_time=today + timedelta(days=i, hours=1),
                status="confirmed",
            )
            appointment.save()
        
        date_str = today.date().isoformat()
        response = client.get(
            f"/api/v1/appointments/week/{date_str}",
            headers={"X-Tenant-ID": str(tenant_id)},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "week_start" in data
        assert "week_end" in data
        assert "appointments" in data
        assert data["total"] >= 3

    def test_get_week_view_with_staff_filter(
        self, tenant_id, staff_id, service_id, customer_id, test_service
    ):
        """Test week view with staff filter."""
        today = datetime.utcnow().replace(hour=10, minute=0, second=0, microsecond=0)
        other_staff_id = ObjectId()
        
        # Create appointments for different staff
        for i in range(2):
            appointment = Appointment(
                tenant_id=tenant_id,
                customer_id=customer_id,
                staff_id=staff_id,
                service_id=service_id,
                start_time=today + timedelta(days=i),
                end_time=today + timedelta(days=i, hours=1),
                status="confirmed",
            )
            appointment.save()
            
            other_appointment = Appointment(
                tenant_id=tenant_id,
                customer_id=customer_id,
                staff_id=other_staff_id,
                service_id=service_id,
                start_time=today + timedelta(days=i, hours=2),
                end_time=today + timedelta(days=i, hours=3),
                status="confirmed",
            )
            other_appointment.save()
        
        date_str = today.date().isoformat()
        response = client.get(
            f"/api/v1/appointments/week/{date_str}",
            params={"staff_id": str(staff_id)},
            headers={"X-Tenant-ID": str(tenant_id)},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(appt["staff_id"] == str(staff_id) for appt in data["appointments"])


class TestMonthViewEndpoint:
    """Test month view endpoint."""

    def test_get_month_view_success(
        self, tenant_id, staff_id, service_id, customer_id, test_service
    ):
        """Test successful month view retrieval."""
        # Create appointments for this month
        today = datetime.utcnow().replace(hour=10, minute=0, second=0, microsecond=0)
        
        for i in range(5):
            appointment = Appointment(
                tenant_id=tenant_id,
                customer_id=customer_id,
                staff_id=staff_id,
                service_id=service_id,
                start_time=today + timedelta(days=i),
                end_time=today + timedelta(days=i, hours=1),
                status="confirmed",
            )
            appointment.save()
        
        date_str = today.date().isoformat()
        response = client.get(
            f"/api/v1/appointments/month/{date_str}",
            headers={"X-Tenant-ID": str(tenant_id)},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "month" in data
        assert "appointments" in data
        assert data["total"] >= 5

    def test_get_month_view_with_staff_filter(
        self, tenant_id, staff_id, service_id, customer_id, test_service
    ):
        """Test month view with staff filter."""
        today = datetime.utcnow().replace(hour=10, minute=0, second=0, microsecond=0)
        other_staff_id = ObjectId()
        
        # Create appointments for different staff
        for i in range(3):
            appointment = Appointment(
                tenant_id=tenant_id,
                customer_id=customer_id,
                staff_id=staff_id,
                service_id=service_id,
                start_time=today + timedelta(days=i),
                end_time=today + timedelta(days=i, hours=1),
                status="confirmed",
            )
            appointment.save()
            
            other_appointment = Appointment(
                tenant_id=tenant_id,
                customer_id=customer_id,
                staff_id=other_staff_id,
                service_id=service_id,
                start_time=today + timedelta(days=i, hours=2),
                end_time=today + timedelta(days=i, hours=3),
                status="confirmed",
            )
            other_appointment.save()
        
        date_str = today.date().isoformat()
        response = client.get(
            f"/api/v1/appointments/month/{date_str}",
            params={"staff_id": str(staff_id)},
            headers={"X-Tenant-ID": str(tenant_id)},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(appt["staff_id"] == str(staff_id) for appt in data["appointments"])
