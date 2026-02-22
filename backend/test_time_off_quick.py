"""Quick test to verify TimeOffRequest implementation."""

from datetime import date, timedelta
from bson import ObjectId
from app.models.time_off_request import TimeOffRequest
from app.models.staff import Staff
from app.models.user import User
from app.models.tenant import Tenant
from app.db import init_db, close_db

# Initialize database
init_db()

try:
    # Create test tenant
    tenant = Tenant(
        name="Test Salon",
        subscription_tier="professional",
        status="active",
        region="US"
    )
    tenant.save()
    print(f"✓ Created tenant: {tenant.id}")

    # Create test user
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
    print(f"✓ Created user: {user.id}")

    # Create test staff
    staff = Staff(
        tenant_id=tenant.id,
        user_id=user.id,
        specialties=["haircut"],
        certifications=["License"],
        hourly_rate=25.00,
        status="active"
    )
    staff.save()
    print(f"✓ Created staff: {staff.id}")

    # Create time-off request
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
    print(f"✓ Created time-off request: {request.id}")

    # Verify request
    retrieved = TimeOffRequest.objects(id=request.id).first()
    assert retrieved is not None
    assert retrieved.status == "pending"
    assert retrieved.reason == "Vacation"
    print(f"✓ Verified time-off request")

    # Test approval
    retrieved.status = "approved"
    retrieved.save()
    
    updated = TimeOffRequest.objects(id=request.id).first()
    assert updated.status == "approved"
    print(f"✓ Approved time-off request")

    # Test listing
    requests = TimeOffRequest.objects(tenant_id=tenant.id, staff_id=staff.id)
    assert requests.count() == 1
    print(f"✓ Listed time-off requests: {requests.count()}")

    print("\n✅ All tests passed!")

finally:
    close_db()
