"""Integration tests for Shift API endpoints."""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from mongoengine import ObjectId
from fastapi.testclient import TestClient
from app.main import app
from app.models.shift import Shift
from app.models.staff import Staff
from app.models.user import User
from app.models.tenant import Tenant


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def test_tenant():
    """Create a test tenant."""
    tenant = Tenant(name="Test Salon", subscription_tier="professional")
    tenant.save()
    yield tenant
    tenant.delete()


@pytest.fixture
def test_user(test_tenant):
    """Create a test user."""
    user = User(
        tenant_id=test_tenant.id,
        email="staff@test.com",
        password_hash="hashed_password",
        first_name="John",
        last_name="Doe",
        role_id=ObjectId(),
    )
    user.save()
    yield user
    user.delete()


@pytest.fixture
def test_staff(test_tenant, test_user):
    """Create a test staff member."""
    staff = Staff(
        tenant_id=test_tenant.id,
        user_id=test_user.id,
        hourly_rate=Decimal("50.00"),
        specialties=["haircut", "coloring"],
    )
    staff.save()
    yield staff
    staff.delete()


@pytest.fixture
def auth_headers(test_tenant):
    """Create authentication headers."""
    # Mock JWT token with tenant_id
    return {
        "Authorization": f"Bearer mock_token",
        "X-Tenant-ID": str(test_tenant.id),
    }


class TestShiftCreation:
    """Test shift creation endpoint."""

    def test_create_shift_success(self, client, test_tenant, test_staff, auth_headers):
        """Test successful shift creation."""
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=8)
        
        payload = {
            "staff_id": str(test_staff.id),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "status": "scheduled",
        }
        
        response = client.post("/shifts", json=payload, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["staff_id"] == str(test_staff.id)
        assert data["status"] == "scheduled"
        assert data["labor_cost"] == "400.00"  # 8 hours * $50/hour
        
        # Clean up
        Shift.objects(id=ObjectId(data["id"])).delete()

    def test_create_shift_with_conflict(self, client, test_tenant, test_staff, auth_headers):
        """Test shift creation with conflict detection."""
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=8)
        
        # Create first shift
        shift1 = Shift(
            tenant_id=test_tenant.id,
            staff_id=test_staff.id,
            start_time=start_time,
            end_time=end_time,
            status="scheduled",
        )
        shift1.save()
        
        # Try to create overlapping shift
        payload = {
            "staff_id": str(test_staff.id),
            "start_time": (start_time + timedelta(hours=4)).isoformat(),
            "end_time": (end_time + timedelta(hours=4)).isoformat(),
            "status": "scheduled",
        }
        
        response = client.post("/shifts", json=payload, headers=auth_headers)
        
        assert response.status_code == 409
        assert "conflicts" in response.json()["detail"].lower()
        
        # Clean up
        shift1.delete()

    def test_create_shift_invalid_staff(self, client, test_tenant, auth_headers):
        """Test shift creation with invalid staff ID."""
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=8)
        
        payload = {
            "staff_id": str(ObjectId()),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "status": "scheduled",
        }
        
        response = client.post("/shifts", json=payload, headers=auth_headers)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_create_shift_invalid_times(self, client, test_tenant, test_staff, auth_headers):
        """Test shift creation with invalid times."""
        start_time = datetime.utcnow()
        end_time = start_time - timedelta(hours=1)  # End before start
        
        payload = {
            "staff_id": str(test_staff.id),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "status": "scheduled",
        }
        
        response = client.post("/shifts", json=payload, headers=auth_headers)
        
        assert response.status_code == 422  # Validation error


class TestShiftRetrieval:
    """Test shift retrieval endpoints."""

    def test_get_shift_success(self, client, test_tenant, test_staff, auth_headers):
        """Test successful shift retrieval."""
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=8)
        
        shift = Shift(
            tenant_id=test_tenant.id,
            staff_id=test_staff.id,
            start_time=start_time,
            end_time=end_time,
            status="scheduled",
        )
        shift.save()
        
        response = client.get(f"/shifts/{shift.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(shift.id)
        assert data["staff_id"] == str(test_staff.id)
        
        shift.delete()

    def test_get_shift_not_found(self, client, test_tenant, auth_headers):
        """Test shift retrieval with non-existent ID."""
        response = client.get(f"/shifts/{ObjectId()}", headers=auth_headers)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_list_shifts_success(self, client, test_tenant, test_staff, auth_headers):
        """Test successful shift listing."""
        start_time = datetime.utcnow()
        
        # Create multiple shifts
        for i in range(3):
            shift = Shift(
                tenant_id=test_tenant.id,
                staff_id=test_staff.id,
                start_time=start_time + timedelta(days=i),
                end_time=start_time + timedelta(days=i, hours=8),
                status="scheduled",
            )
            shift.save()
        
        response = client.get("/shifts", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["shifts"]) == 3
        
        # Clean up
        for shift in Shift.objects(tenant_id=test_tenant.id):
            shift.delete()

    def test_list_shifts_with_staff_filter(self, client, test_tenant, test_staff, test_user, auth_headers):
        """Test shift listing with staff filter."""
        start_time = datetime.utcnow()
        
        # Create staff member 2
        staff2 = Staff(
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            hourly_rate=Decimal("60.00"),
        )
        staff2.save()
        
        # Create shifts for both staff
        shift1 = Shift(
            tenant_id=test_tenant.id,
            staff_id=test_staff.id,
            start_time=start_time,
            end_time=start_time + timedelta(hours=8),
        )
        shift1.save()
        
        shift2 = Shift(
            tenant_id=test_tenant.id,
            staff_id=staff2.id,
            start_time=start_time,
            end_time=start_time + timedelta(hours=8),
        )
        shift2.save()
        
        # Query with staff filter
        response = client.get(f"/shifts?staff_id={test_staff.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["shifts"][0]["staff_id"] == str(test_staff.id)
        
        # Clean up
        shift1.delete()
        shift2.delete()
        staff2.delete()

    def test_list_shifts_with_status_filter(self, client, test_tenant, test_staff, auth_headers):
        """Test shift listing with status filter."""
        start_time = datetime.utcnow()
        
        # Create shifts with different statuses
        for status in ["scheduled", "in_progress", "completed"]:
            shift = Shift(
                tenant_id=test_tenant.id,
                staff_id=test_staff.id,
                start_time=start_time,
                end_time=start_time + timedelta(hours=8),
                status=status,
            )
            shift.save()
        
        # Query with status filter
        response = client.get("/shifts?status=scheduled", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["shifts"][0]["status"] == "scheduled"
        
        # Clean up
        for shift in Shift.objects(tenant_id=test_tenant.id):
            shift.delete()


class TestShiftUpdate:
    """Test shift update endpoint."""

    def test_update_shift_status(self, client, test_tenant, test_staff, auth_headers):
        """Test updating shift status."""
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=8)
        
        shift = Shift(
            tenant_id=test_tenant.id,
            staff_id=test_staff.id,
            start_time=start_time,
            end_time=end_time,
            status="scheduled",
        )
        shift.save()
        
        payload = {"status": "in_progress"}
        response = client.put(f"/shifts/{shift.id}", json=payload, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "in_progress"
        
        shift.delete()

    def test_update_shift_times(self, client, test_tenant, test_staff, auth_headers):
        """Test updating shift times."""
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=8)
        
        shift = Shift(
            tenant_id=test_tenant.id,
            staff_id=test_staff.id,
            start_time=start_time,
            end_time=end_time,
        )
        shift.save()
        
        new_start = start_time + timedelta(hours=1)
        new_end = new_start + timedelta(hours=8)
        
        payload = {
            "start_time": new_start.isoformat(),
            "end_time": new_end.isoformat(),
        }
        response = client.put(f"/shifts/{shift.id}", json=payload, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["labor_cost"] == "400.00"  # Still 8 hours
        
        shift.delete()

    def test_update_shift_with_conflict(self, client, test_tenant, test_staff, auth_headers):
        """Test updating shift with conflict detection."""
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=8)
        
        # Create two shifts
        shift1 = Shift(
            tenant_id=test_tenant.id,
            staff_id=test_staff.id,
            start_time=start_time,
            end_time=end_time,
        )
        shift1.save()
        
        shift2 = Shift(
            tenant_id=test_tenant.id,
            staff_id=test_staff.id,
            start_time=start_time + timedelta(days=1),
            end_time=start_time + timedelta(days=1, hours=8),
        )
        shift2.save()
        
        # Try to update shift2 to overlap with shift1
        payload = {
            "start_time": (start_time + timedelta(hours=4)).isoformat(),
            "end_time": (end_time + timedelta(hours=4)).isoformat(),
        }
        response = client.put(f"/shifts/{shift2.id}", json=payload, headers=auth_headers)
        
        assert response.status_code == 409
        assert "conflicts" in response.json()["detail"].lower()
        
        # Clean up
        shift1.delete()
        shift2.delete()


class TestShiftDeletion:
    """Test shift deletion endpoint."""

    def test_delete_shift_success(self, client, test_tenant, test_staff, auth_headers):
        """Test successful shift deletion."""
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=8)
        
        shift = Shift(
            tenant_id=test_tenant.id,
            staff_id=test_staff.id,
            start_time=start_time,
            end_time=end_time,
        )
        shift.save()
        shift_id = shift.id
        
        response = client.delete(f"/shifts/{shift_id}", headers=auth_headers)
        
        assert response.status_code == 200
        assert "deleted" in response.json()["message"].lower()
        
        # Verify shift is deleted
        deleted_shift = Shift.objects(id=shift_id).first()
        assert deleted_shift is None

    def test_delete_shift_not_found(self, client, test_tenant, auth_headers):
        """Test deletion of non-existent shift."""
        response = client.delete(f"/shifts/{ObjectId()}", headers=auth_headers)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
