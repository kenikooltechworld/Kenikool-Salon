"""Unit tests for Shift model."""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from mongoengine import ObjectId
from app.models.shift import Shift
from app.models.staff import Staff
from app.models.user import User
from app.models.tenant import Tenant


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


class TestShiftCreation:
    """Test shift creation."""

    def test_create_shift_with_valid_data(self, test_tenant, test_staff):
        """Test creating a shift with valid data."""
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
        
        assert shift.id is not None
        assert shift.staff_id == test_staff.id
        assert shift.status == "scheduled"
        assert shift.start_time == start_time
        assert shift.end_time == end_time
        
        shift.delete()

    def test_create_shift_with_minimal_data(self, test_tenant, test_staff):
        """Test creating a shift with minimal required data."""
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=4)
        
        shift = Shift(
            tenant_id=test_tenant.id,
            staff_id=test_staff.id,
            start_time=start_time,
            end_time=end_time,
        )
        shift.save()
        
        assert shift.id is not None
        assert shift.status == "scheduled"  # Default status
        
        shift.delete()

    def test_create_shift_with_different_statuses(self, test_tenant, test_staff):
        """Test creating shifts with different statuses."""
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=8)
        
        for status in ["scheduled", "in_progress", "completed", "cancelled"]:
            shift = Shift(
                tenant_id=test_tenant.id,
                staff_id=test_staff.id,
                start_time=start_time,
                end_time=end_time,
                status=status,
            )
            shift.save()
            
            assert shift.status == status
            shift.delete()


class TestLaborCostCalculation:
    """Test labor cost calculation."""

    def test_calculate_labor_cost_8_hours(self, test_tenant, test_staff):
        """Test labor cost calculation for 8-hour shift."""
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=8)
        
        shift = Shift(
            tenant_id=test_tenant.id,
            staff_id=test_staff.id,
            start_time=start_time,
            end_time=end_time,
        )
        
        labor_cost = shift.calculate_labor_cost(test_staff.hourly_rate)
        
        # 8 hours * $50/hour = $400
        assert labor_cost == Decimal("400.00")

    def test_calculate_labor_cost_4_hours(self, test_tenant, test_staff):
        """Test labor cost calculation for 4-hour shift."""
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=4)
        
        shift = Shift(
            tenant_id=test_tenant.id,
            staff_id=test_staff.id,
            start_time=start_time,
            end_time=end_time,
        )
        
        labor_cost = shift.calculate_labor_cost(test_staff.hourly_rate)
        
        # 4 hours * $50/hour = $200
        assert labor_cost == Decimal("200.00")

    def test_calculate_labor_cost_half_hour(self, test_tenant, test_staff):
        """Test labor cost calculation for 30-minute shift."""
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(minutes=30)
        
        shift = Shift(
            tenant_id=test_tenant.id,
            staff_id=test_staff.id,
            start_time=start_time,
            end_time=end_time,
        )
        
        labor_cost = shift.calculate_labor_cost(test_staff.hourly_rate)
        
        # 0.5 hours * $50/hour = $25
        assert labor_cost == Decimal("25.00")

    def test_calculate_labor_cost_with_different_hourly_rate(self, test_tenant, test_staff):
        """Test labor cost calculation with different hourly rates."""
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=8)
        
        shift = Shift(
            tenant_id=test_tenant.id,
            staff_id=test_staff.id,
            start_time=start_time,
            end_time=end_time,
        )
        
        # Test with $75/hour
        labor_cost = shift.calculate_labor_cost(Decimal("75.00"))
        assert labor_cost == Decimal("600.00")
        
        # Test with $25/hour
        labor_cost = shift.calculate_labor_cost(Decimal("25.00"))
        assert labor_cost == Decimal("200.00")

    def test_calculate_labor_cost_zero_rate(self, test_tenant, test_staff):
        """Test labor cost calculation with zero hourly rate."""
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=8)
        
        shift = Shift(
            tenant_id=test_tenant.id,
            staff_id=test_staff.id,
            start_time=start_time,
            end_time=end_time,
        )
        
        labor_cost = shift.calculate_labor_cost(Decimal("0.00"))
        assert labor_cost == Decimal("0.00")

    def test_calculate_labor_cost_no_times(self, test_tenant, test_staff):
        """Test labor cost calculation with no times set."""
        shift = Shift(
            tenant_id=test_tenant.id,
            staff_id=test_staff.id,
        )
        
        labor_cost = shift.calculate_labor_cost(test_staff.hourly_rate)
        assert labor_cost == Decimal("0")


class TestShiftUpdate:
    """Test shift updates."""

    def test_update_shift_status(self, test_tenant, test_staff):
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
        
        shift.status = "in_progress"
        shift.save()
        
        updated_shift = Shift.objects(id=shift.id).first()
        assert updated_shift.status == "in_progress"
        
        shift.delete()

    def test_update_shift_times(self, test_tenant, test_staff):
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
        
        shift.start_time = new_start
        shift.end_time = new_end
        shift.save()
        
        updated_shift = Shift.objects(id=shift.id).first()
        assert updated_shift.start_time == new_start
        assert updated_shift.end_time == new_end
        
        shift.delete()


class TestShiftQuerying:
    """Test shift querying."""

    def test_query_shifts_by_staff(self, test_tenant, test_staff):
        """Test querying shifts by staff member."""
        start_time = datetime.utcnow()
        
        # Create multiple shifts for same staff
        for i in range(3):
            shift = Shift(
                tenant_id=test_tenant.id,
                staff_id=test_staff.id,
                start_time=start_time + timedelta(days=i),
                end_time=start_time + timedelta(days=i, hours=8),
            )
            shift.save()
        
        shifts = Shift.objects(tenant_id=test_tenant.id, staff_id=test_staff.id)
        assert len(shifts) == 3
        
        # Clean up
        for shift in shifts:
            shift.delete()

    def test_query_shifts_by_status(self, test_tenant, test_staff):
        """Test querying shifts by status."""
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
        
        scheduled_shifts = Shift.objects(tenant_id=test_tenant.id, status="scheduled")
        assert len(scheduled_shifts) == 1
        
        # Clean up
        for shift in Shift.objects(tenant_id=test_tenant.id):
            shift.delete()

    def test_query_shifts_by_date_range(self, test_tenant, test_staff):
        """Test querying shifts by date range."""
        base_time = datetime.utcnow()
        
        # Create shifts on different days
        for i in range(5):
            shift = Shift(
                tenant_id=test_tenant.id,
                staff_id=test_staff.id,
                start_time=base_time + timedelta(days=i),
                end_time=base_time + timedelta(days=i, hours=8),
            )
            shift.save()
        
        # Query shifts within a date range
        start_range = base_time + timedelta(days=1)
        end_range = base_time + timedelta(days=3)
        
        shifts_in_range = Shift.objects(
            tenant_id=test_tenant.id,
            start_time__gte=start_range,
            start_time__lte=end_range,
        )
        
        assert len(shifts_in_range) == 3
        
        # Clean up
        for shift in Shift.objects(tenant_id=test_tenant.id):
            shift.delete()


class TestShiftValidation:
    """Test shift validation."""

    def test_shift_requires_staff_id(self, test_tenant):
        """Test that shift requires staff_id."""
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=8)
        
        shift = Shift(
            tenant_id=test_tenant.id,
            start_time=start_time,
            end_time=end_time,
        )
        
        with pytest.raises(Exception):
            shift.save()

    def test_shift_requires_start_time(self, test_tenant, test_staff):
        """Test that shift requires start_time."""
        end_time = datetime.utcnow() + timedelta(hours=8)
        
        shift = Shift(
            tenant_id=test_tenant.id,
            staff_id=test_staff.id,
            end_time=end_time,
        )
        
        with pytest.raises(Exception):
            shift.save()

    def test_shift_requires_end_time(self, test_tenant, test_staff):
        """Test that shift requires end_time."""
        start_time = datetime.utcnow()
        
        shift = Shift(
            tenant_id=test_tenant.id,
            staff_id=test_staff.id,
            start_time=start_time,
        )
        
        with pytest.raises(Exception):
            shift.save()

    def test_shift_status_must_be_valid(self, test_tenant, test_staff):
        """Test that shift status must be valid."""
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=8)
        
        shift = Shift(
            tenant_id=test_tenant.id,
            staff_id=test_staff.id,
            start_time=start_time,
            end_time=end_time,
            status="invalid_status",
        )
        
        with pytest.raises(Exception):
            shift.save()
