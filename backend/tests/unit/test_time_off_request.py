"""Unit tests for TimeOffRequest model."""

import pytest
from datetime import datetime, date, timedelta
from bson import ObjectId
from app.models.time_off_request import TimeOffRequest
from app.models.staff import Staff
from app.models.user import User
from app.models.tenant import Tenant


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
def user(tenant):
    """Create a test user."""
    user = User(
        tenant_id=tenant.id,
        email="staff@test.com",
        password_hash="hashed_password",
        first_name="John",
        last_name="Doe",
        phone="+1234567890",
        role_id=ObjectId(),
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
        specialties=["haircut", "coloring"],
        certifications=["Cosmetology License"],
        hourly_rate=25.00,
        status="active"
    )
    staff.save()
    return staff


class TestTimeOffRequestModel:
    """Test TimeOffRequest model."""

    def test_create_time_off_request(self, tenant, staff):
        """Test creating a time-off request."""
        start_date = date.today()
        end_date = start_date + timedelta(days=5)
        
        request = TimeOffRequest(
            tenant_id=tenant.id,
            staff_id=staff.id,
            start_date=start_date,
            end_date=end_date,
            reason="Vacation",
            status="pending"
        )
        request.save()
        
        assert request.id is not None
        assert request.tenant_id == tenant.id
        assert request.staff_id == staff.id
        assert request.start_date == start_date
        assert request.end_date == end_date
        assert request.reason == "Vacation"
        assert request.status == "pending"
        assert request.requested_at is not None
        assert request.reviewed_at is None
        assert request.reviewed_by is None

    def test_time_off_request_default_status(self, tenant, staff):
        """Test that time-off request defaults to pending status."""
        request = TimeOffRequest(
            tenant_id=tenant.id,
            staff_id=staff.id,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=3),
            reason="Sick leave"
        )
        request.save()
        
        assert request.status == "pending"

    def test_time_off_request_approval(self, tenant, staff, user):
        """Test approving a time-off request."""
        request = TimeOffRequest(
            tenant_id=tenant.id,
            staff_id=staff.id,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=3),
            reason="Vacation"
        )
        request.save()
        
        # Approve the request
        request.status = "approved"
        request.reviewed_at = datetime.utcnow()
        request.reviewed_by = user.id
        request.save()
        
        # Verify changes
        updated_request = TimeOffRequest.objects(id=request.id).first()
        assert updated_request.status == "approved"
        assert updated_request.reviewed_at is not None
        assert updated_request.reviewed_by == user.id

    def test_time_off_request_denial(self, tenant, staff, user):
        """Test denying a time-off request."""
        request = TimeOffRequest(
            tenant_id=tenant.id,
            staff_id=staff.id,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=3),
            reason="Vacation"
        )
        request.save()
        
        # Deny the request
        request.status = "denied"
        request.reviewed_at = datetime.utcnow()
        request.reviewed_by = user.id
        request.save()
        
        # Verify changes
        updated_request = TimeOffRequest.objects(id=request.id).first()
        assert updated_request.status == "denied"
        assert updated_request.reviewed_at is not None
        assert updated_request.reviewed_by == user.id

    def test_time_off_request_string_representation(self, tenant, staff):
        """Test string representation of time-off request."""
        start_date = date.today()
        request = TimeOffRequest(
            tenant_id=tenant.id,
            staff_id=staff.id,
            start_date=start_date,
            end_date=start_date + timedelta(days=3),
            reason="Vacation"
        )
        request.save()
        
        str_repr = str(request)
        assert "TimeOffRequest" in str_repr
        assert str(staff.id) in str_repr
        assert "pending" in str_repr

    def test_time_off_request_date_range(self, tenant, staff):
        """Test time-off request with various date ranges."""
        # Single day
        request1 = TimeOffRequest(
            tenant_id=tenant.id,
            staff_id=staff.id,
            start_date=date.today(),
            end_date=date.today(),
            reason="Personal day"
        )
        request1.save()
        assert request1.start_date == request1.end_date
        
        # Multiple days
        start = date.today()
        end = start + timedelta(days=10)
        request2 = TimeOffRequest(
            tenant_id=tenant.id,
            staff_id=staff.id,
            start_date=start,
            end_date=end,
            reason="Vacation"
        )
        request2.save()
        assert (request2.end_date - request2.start_date).days == 10

    def test_time_off_request_reason_max_length(self, tenant, staff):
        """Test time-off request reason field max length."""
        long_reason = "A" * 500
        request = TimeOffRequest(
            tenant_id=tenant.id,
            staff_id=staff.id,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=3),
            reason=long_reason
        )
        request.save()
        
        assert len(request.reason) == 500

    def test_time_off_request_timestamps(self, tenant, staff):
        """Test time-off request timestamps."""
        before_creation = datetime.utcnow()
        request = TimeOffRequest(
            tenant_id=tenant.id,
            staff_id=staff.id,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=3),
            reason="Vacation"
        )
        request.save()
        after_creation = datetime.utcnow()
        
        assert before_creation <= request.created_at <= after_creation
        assert before_creation <= request.updated_at <= after_creation
        assert request.created_at == request.updated_at

    def test_time_off_request_update_timestamp(self, tenant, staff):
        """Test that updated_at changes when request is updated."""
        request = TimeOffRequest(
            tenant_id=tenant.id,
            staff_id=staff.id,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=3),
            reason="Vacation"
        )
        request.save()
        
        original_updated_at = request.updated_at
        
        # Wait a bit and update
        import time
        time.sleep(0.1)
        
        request.status = "approved"
        request.save()
        
        assert request.updated_at > original_updated_at

    def test_time_off_request_multiple_for_same_staff(self, tenant, staff):
        """Test creating multiple time-off requests for the same staff."""
        request1 = TimeOffRequest(
            tenant_id=tenant.id,
            staff_id=staff.id,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=3),
            reason="Vacation"
        )
        request1.save()
        
        request2 = TimeOffRequest(
            tenant_id=tenant.id,
            staff_id=staff.id,
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=12),
            reason="Sick leave"
        )
        request2.save()
        
        requests = TimeOffRequest.objects(staff_id=staff.id, tenant_id=tenant.id)
        assert requests.count() == 2

    def test_time_off_request_tenant_isolation(self, tenant, staff):
        """Test that time-off requests are isolated by tenant."""
        # Create another tenant
        tenant2 = Tenant(
            name="Test Salon 2",
            subscription_tier="professional",
            status="active",
            region="US"
        )
        tenant2.save()
        
        # Create request for first tenant
        request1 = TimeOffRequest(
            tenant_id=tenant.id,
            staff_id=staff.id,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=3),
            reason="Vacation"
        )
        request1.save()
        
        # Query should only return requests for first tenant
        requests = TimeOffRequest.objects(tenant_id=tenant.id)
        assert requests.count() == 1
        
        # Query for second tenant should return nothing
        requests2 = TimeOffRequest.objects(tenant_id=tenant2.id)
        assert requests2.count() == 0
