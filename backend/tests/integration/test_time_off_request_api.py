"""Integration tests for time-off request API endpoints."""

import pytest
from datetime import date, timedelta
from bson import ObjectId
from app.models.time_off_request import TimeOffRequest
from app.models.staff import Staff
from app.models.user import User
from app.models.tenant import Tenant
from app.models.role import Role


@pytest.fixture
def tenant():
    """Create a test tenant."""
    tenant = Tenant(
        name="Test Salon",
        subscription_tier="professional",
        status="active",
        region="US"
    )
    tenant.save()
    return tenant


@pytest.fixture
def role(tenant):
    """Create a test role."""
    role = Role(
        tenant_id=tenant.id,
        name="Manager",
        permissions=["time_off_requests:read", "time_off_requests:write"]
    )
    role.save()
    return role


@pytest.fixture
def user(tenant, role):
    """Create a test user."""
    user = User(
        tenant_id=tenant.id,
        email="staff@test.com",
        password_hash="hashed_password",
        first_name="John",
        last_name="Doe",
        phone="+1234567890",
        role_id=role.id,
        status="active"
    )
    user.save()
    return user


@pytest.fixture
def staff(tenant, user):
    """Create a test staff member."""
    staff = Staff(
        tenant_id=tenant.id,
        user_id=user.id,
        specialties=["haircut"],
        certifications=["License"],
        hourly_rate=25.00,
        status="active"
    )
    staff.save()
    return staff


@pytest.fixture
def client(tenant):
    """Create a test client with tenant context."""
    from fastapi.testclient import TestClient
    from app.main import app
    
    client = TestClient(app)
    # Set tenant context in headers
    client.headers.update({
        "X-Tenant-ID": str(tenant.id)
    })
    return client


class TestTimeOffRequestAPI:
    """Test time-off request API endpoints."""

    def test_create_time_off_request(self, client, tenant, staff):
        """Test creating a time-off request."""
        start_date = date.today()
        end_date = start_date + timedelta(days=5)
        
        response = client.post(
            "/v1/time-off-requests",
            json={
                "staff_id": str(staff.id),
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "reason": "Vacation"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["staff_id"] == str(staff.id)
        assert data["reason"] == "Vacation"
        assert data["status"] == "pending"
        assert data["start_date"] == start_date.isoformat()
        assert data["end_date"] == end_date.isoformat()

    def test_create_time_off_request_missing_staff_id(self, client):
        """Test creating time-off request without staff_id."""
        response = client.post(
            "/v1/time-off-requests",
            json={
                "start_date": date.today().isoformat(),
                "end_date": (date.today() + timedelta(days=3)).isoformat(),
                "reason": "Vacation"
            }
        )
        
        assert response.status_code == 400

    def test_create_time_off_request_invalid_staff(self, client):
        """Test creating time-off request with invalid staff_id."""
        response = client.post(
            "/v1/time-off-requests",
            json={
                "staff_id": str(ObjectId()),
                "start_date": date.today().isoformat(),
                "end_date": (date.today() + timedelta(days=3)).isoformat(),
                "reason": "Vacation"
            }
        )
        
        assert response.status_code == 400

    def test_create_time_off_request_invalid_dates(self, client, staff):
        """Test creating time-off request with end_date before start_date."""
        start_date = date.today()
        end_date = start_date - timedelta(days=3)
        
        response = client.post(
            "/v1/time-off-requests",
            json={
                "staff_id": str(staff.id),
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "reason": "Vacation"
            }
        )
        
        assert response.status_code == 400

    def test_list_time_off_requests(self, client, tenant, staff):
        """Test listing time-off requests."""
        # Create multiple requests
        for i in range(3):
            TimeOffRequest(
                tenant_id=tenant.id,
                staff_id=staff.id,
                start_date=date.today() + timedelta(days=i*10),
                end_date=date.today() + timedelta(days=i*10+3),
                reason=f"Vacation {i+1}"
            ).save()
        
        response = client.get("/v1/time-off-requests")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["requests"]) == 3
        assert data["page"] == 1
        assert data["page_size"] == 10

    def test_list_time_off_requests_with_pagination(self, client, tenant, staff):
        """Test listing time-off requests with pagination."""
        # Create 15 requests
        for i in range(15):
            TimeOffRequest(
                tenant_id=tenant.id,
                staff_id=staff.id,
                start_date=date.today() + timedelta(days=i),
                end_date=date.today() + timedelta(days=i+1),
                reason=f"Day off {i+1}"
            ).save()
        
        # Get first page
        response = client.get("/v1/time-off-requests?page=1&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 15
        assert len(data["requests"]) == 10
        
        # Get second page
        response = client.get("/v1/time-off-requests?page=2&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["requests"]) == 5

    def test_list_time_off_requests_filter_by_status(self, client, tenant, staff):
        """Test listing time-off requests filtered by status."""
        # Create pending request
        pending = TimeOffRequest(
            tenant_id=tenant.id,
            staff_id=staff.id,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=3),
            reason="Vacation",
            status="pending"
        )
        pending.save()
        
        # Create approved request
        approved = TimeOffRequest(
            tenant_id=tenant.id,
            staff_id=staff.id,
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=13),
            reason="Vacation",
            status="approved"
        )
        approved.save()
        
        # Filter by pending
        response = client.get("/v1/time-off-requests?status=pending")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["requests"][0]["status"] == "pending"

    def test_get_time_off_request(self, client, tenant, staff):
        """Test getting a specific time-off request."""
        request = TimeOffRequest(
            tenant_id=tenant.id,
            staff_id=staff.id,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=3),
            reason="Vacation"
        )
        request.save()
        
        response = client.get(f"/v1/time-off-requests/{request.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(request.id)
        assert data["reason"] == "Vacation"
        assert data["status"] == "pending"

    def test_get_time_off_request_not_found(self, client):
        """Test getting a non-existent time-off request."""
        response = client.get(f"/v1/time-off-requests/{ObjectId()}")
        
        assert response.status_code == 404

    def test_approve_time_off_request(self, client, tenant, staff, user):
        """Test approving a time-off request."""
        request = TimeOffRequest(
            tenant_id=tenant.id,
            staff_id=staff.id,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=3),
            reason="Vacation",
            status="pending"
        )
        request.save()
        
        response = client.put(f"/v1/time-off-requests/{request.id}/approve")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "approved"
        assert data["reviewed_at"] is not None

    def test_approve_non_pending_request(self, client, tenant, staff):
        """Test approving a non-pending request."""
        request = TimeOffRequest(
            tenant_id=tenant.id,
            staff_id=staff.id,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=3),
            reason="Vacation",
            status="approved"
        )
        request.save()
        
        response = client.put(f"/v1/time-off-requests/{request.id}/approve")
        
        assert response.status_code == 400

    def test_deny_time_off_request(self, client, tenant, staff):
        """Test denying a time-off request."""
        request = TimeOffRequest(
            tenant_id=tenant.id,
            staff_id=staff.id,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=3),
            reason="Vacation",
            status="pending"
        )
        request.save()
        
        response = client.put(
            f"/v1/time-off-requests/{request.id}/deny",
            json={"denial_reason": "Insufficient coverage"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "denied"
        assert data["reviewed_at"] is not None

    def test_deny_non_pending_request(self, client, tenant, staff):
        """Test denying a non-pending request."""
        request = TimeOffRequest(
            tenant_id=tenant.id,
            staff_id=staff.id,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=3),
            reason="Vacation",
            status="denied"
        )
        request.save()
        
        response = client.put(
            f"/v1/time-off-requests/{request.id}/deny",
            json={"denial_reason": "Already denied"}
        )
        
        assert response.status_code == 400

    def test_time_off_request_workflow(self, client, tenant, staff):
        """Test complete time-off request workflow."""
        # Create request
        start_date = date.today()
        end_date = start_date + timedelta(days=5)
        
        create_response = client.post(
            "/v1/time-off-requests",
            json={
                "staff_id": str(staff.id),
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "reason": "Vacation"
            }
        )
        assert create_response.status_code == 200
        request_id = create_response.json()["id"]
        
        # Get request
        get_response = client.get(f"/v1/time-off-requests/{request_id}")
        assert get_response.status_code == 200
        assert get_response.json()["status"] == "pending"
        
        # Approve request
        approve_response = client.put(f"/v1/time-off-requests/{request_id}/approve")
        assert approve_response.status_code == 200
        assert approve_response.json()["status"] == "approved"
        
        # Verify approval
        final_response = client.get(f"/v1/time-off-requests/{request_id}")
        assert final_response.status_code == 200
        assert final_response.json()["status"] == "approved"
