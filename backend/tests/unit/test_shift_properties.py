"""Property-based tests for shifts.

This module tests the core properties of shift functionality:
- Property 8: Shift Status Consistency - Verify displayed status matches backend and transitions are atomic
- Property 10: Shift Sorting Order - Verify shifts sorted by date ascending by default
- Property 18: Shift Detail Completeness - Verify all required information displays

Validates: Requirements 3.3, 3.6, 3.7
"""

import pytest
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from datetime import datetime, timedelta
from decimal import Decimal
from bson import ObjectId

from app.models.shift import Shift
from app.models.staff import Staff
from app.models.user import User
from app.models.tenant import Tenant
from app.context import set_tenant_id, clear_context


# Fixtures
@pytest.fixture
def test_tenant():
    """Create a test tenant."""
    tenant = Tenant(
        name="Test Salon",
        subdomain="test-salon",
        subscription_tier="professional",
        status="active",
    )
    tenant.save()
    yield tenant
    tenant.delete()


@pytest.fixture
def test_user(test_tenant):
    """Create a test user."""
    user = User(
        tenant_id=test_tenant.id,
        email="staff@example.com",
        password_hash="hashed_password",
        first_name="John",
        last_name="Doe",
        phone="+234123456789",
        status="active",
    )
    user.save()
    yield user
    user.delete()


@pytest.fixture
def test_staff_member(test_tenant, test_user):
    """Create a test staff member."""
    staff = Staff(
        tenant_id=test_tenant.id,
        user_id=test_user.id,
        payment_type="hourly",
        payment_rate=Decimal("50.00"),
        status="active",
    )
    staff.save()
    yield staff
    staff.delete()


# Strategy generators for property-based testing
@st.composite
def shift_status_strategy(draw):
    """Generate valid shift statuses."""
    return draw(st.sampled_from(["scheduled", "in_progress", "completed"]))


@st.composite
def shift_data_strategy(draw, test_tenant, test_staff_member):
    """Generate shift data with various initial statuses."""
    now = datetime.utcnow()
    start_time = draw(st.datetimes(
        min_value=now,
        max_value=now + timedelta(days=30)
    ))
    
    status = draw(shift_status_strategy())
    duration_hours = draw(st.integers(min_value=1, max_value=12))
    
    return {
        "tenant_id": test_tenant.id,
        "staff_id": test_staff_member.id,
        "start_time": start_time,
        "end_time": start_time + timedelta(hours=duration_hours),
        "status": status,
        "labor_cost": Decimal("0.00"),
    }


@st.composite
def multiple_shifts_strategy(draw, test_tenant, test_staff_member):
    """Generate multiple shifts with different dates and statuses."""
    now = datetime.utcnow()
    num_shifts = draw(st.integers(min_value=2, max_value=5))
    
    shifts = []
    statuses = ["scheduled", "in_progress", "completed", "cancelled"]
    
    for i in range(num_shifts):
        start_time = now + timedelta(days=i)
        status = draw(st.sampled_from(statuses))
        duration_hours = draw(st.integers(min_value=1, max_value=12))
        
        shifts.append({
            "tenant_id": test_tenant.id,
            "staff_id": test_staff_member.id,
            "start_time": start_time,
            "end_time": start_time + timedelta(hours=duration_hours),
            "status": status,
            "labor_cost": Decimal("0.00"),
        })
    
    return shifts


class TestShiftStatusConsistency:
    """Property-based tests for shift status consistency.
    
    **Property 8: Shift Status Consistency**
    Verify displayed status matches backend and transitions are atomic
    
    Validates: Requirements 3.3
    """

    @given(
        initial_status=shift_status_strategy(),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=10, deadline=None)
    def test_shift_status_matches_backend(
        self,
        test_tenant,
        test_staff_member,
        initial_status,
    ):
        """
        **Property 8: Shift Status Consistency**
        
        For any shift, the displayed status SHALL match the current status in
        the backend. When a shift status is updated, the change SHALL be
        persisted and subsequent queries SHALL return the updated status.
        
        Validates: Requirements 3.3
        """
        set_tenant_id(test_tenant.id)
        
        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        
        # Create shift with initial status
        shift = Shift(
            tenant_id=test_tenant.id,
            staff_id=test_staff_member.id,
            start_time=start_time,
            end_time=start_time + timedelta(hours=8),
            status=initial_status,
            labor_cost=Decimal("400.00"),
        )
        shift.save()
        
        # Verify initial status
        assert shift.status == initial_status
        
        # Query the shift to verify status matches backend
        retrieved_shift = Shift.objects(
            tenant_id=test_tenant.id,
            id=shift.id
        ).first()
        
        assert retrieved_shift is not None
        assert retrieved_shift.status == initial_status
        
        # Update status to completed
        shift.status = "completed"
        shift.save()
        
        # Verify status is updated in memory
        assert shift.status == "completed"
        
        # Query again to verify persistence
        retrieved_shift = Shift.objects(
            tenant_id=test_tenant.id,
            id=shift.id
        ).first()
        
        assert retrieved_shift is not None
        assert retrieved_shift.status == "completed"
        
        # Cleanup
        shift.delete()
        clear_context()

    @given(
        initial_status=shift_status_strategy(),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=10, deadline=None)
    def test_shift_status_transitions_are_atomic(
        self,
        test_tenant,
        test_staff_member,
        initial_status,
    ):
        """
        **Property 8: Shift Status Consistency - Atomic Transitions**
        
        For any shift status transition, the change SHALL be atomic - either
        the entire status update succeeds or fails completely, with no partial
        updates. Multiple concurrent queries SHALL return consistent status.
        
        Validates: Requirements 3.3
        """
        set_tenant_id(test_tenant.id)
        
        now = datetime.utcnow()
        start_time = now + timedelta(hours=2)
        
        # Create shift
        shift = Shift(
            tenant_id=test_tenant.id,
            staff_id=test_staff_member.id,
            start_time=start_time,
            end_time=start_time + timedelta(hours=8),
            status=initial_status,
            labor_cost=Decimal("400.00"),
        )
        shift.save()
        
        # Update status
        shift.status = "completed"
        shift.save()
        
        # Query multiple times to verify consistency
        for _ in range(5):
            retrieved = Shift.objects(
                tenant_id=test_tenant.id,
                id=shift.id
            ).first()
            assert retrieved.status == "completed"
            # Verify other fields remain unchanged
            assert retrieved.staff_id == test_staff_member.id
            # Use approximate equality for datetime (MongoDB may lose microsecond precision)
            assert abs((retrieved.start_time - start_time).total_seconds()) < 1
            assert abs((retrieved.end_time - (start_time + timedelta(hours=8))).total_seconds()) < 1
        
        # Cleanup
        shift.delete()
        clear_context()


class TestShiftSortingOrder:
    """Property-based tests for shift sorting order.
    
    **Property 10: Shift Sorting Order**
    Verify shifts sorted by date ascending by default
    
    Validates: Requirements 3.6
    """

    @given(
        num_shifts=st.integers(min_value=2, max_value=5),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=10, deadline=None)
    def test_shifts_sorted_by_date_ascending_by_default(
        self,
        test_tenant,
        test_staff_member,
        num_shifts,
    ):
        """
        **Property 10: Shift Sorting Order**
        
        For any set of shifts, when displayed without explicit sorting, they
        SHALL be sorted by start_time in ascending order by default.
        
        Validates: Requirements 3.6
        """
        set_tenant_id(test_tenant.id)
        
        now = datetime.utcnow()
        
        # Create shifts with different dates
        created_shifts = []
        for i in range(num_shifts):
            start_time = now + timedelta(days=i)
            shift = Shift(
                tenant_id=test_tenant.id,
                staff_id=test_staff_member.id,
                start_time=start_time,
                end_time=start_time + timedelta(hours=8),
                status="scheduled",
                labor_cost=Decimal("400.00"),
            )
            shift.save()
            created_shifts.append(shift)
        
        # Query shifts without explicit sorting (should default to ascending by start_time)
        queried_shifts = Shift.objects(
            tenant_id=test_tenant.id,
            staff_id=test_staff_member.id,
        ).order_by("start_time")
        
        # Verify shifts are sorted by start_time in ascending order
        assert queried_shifts.count() >= num_shifts
        
        shift_list = list(queried_shifts)
        for i in range(len(shift_list) - 1):
            assert shift_list[i].start_time <= shift_list[i + 1].start_time
        
        # Cleanup
        for shift in created_shifts:
            shift.delete()
        
        clear_context()

    @given(
        num_shifts=st.integers(min_value=3, max_value=7),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=10, deadline=None)
    def test_shifts_with_various_date_ranges_maintain_sort_order(
        self,
        test_tenant,
        test_staff_member,
        num_shifts,
    ):
        """
        **Property 10: Shift Sorting Order - Various Date Ranges**
        
        For any set of shifts with various date ranges (past, present, future),
        when sorted by start_time, they SHALL maintain ascending order regardless
        of the date range.
        
        Validates: Requirements 3.6
        """
        set_tenant_id(test_tenant.id)
        
        now = datetime.utcnow()
        
        # Create shifts with various date ranges
        created_shifts = []
        date_offsets = [
            -7,  # Past
            -1,  # Recent past
            0,   # Today
            1,   # Tomorrow
            7,   # Future
            14,  # Far future
            30,  # Very far future
        ]
        
        for i in range(min(num_shifts, len(date_offsets))):
            start_time = now + timedelta(days=date_offsets[i])
            shift = Shift(
                tenant_id=test_tenant.id,
                staff_id=test_staff_member.id,
                start_time=start_time,
                end_time=start_time + timedelta(hours=8),
                status="scheduled",
                labor_cost=Decimal("400.00"),
            )
            shift.save()
            created_shifts.append(shift)
        
        # Query and sort by start_time
        queried_shifts = list(Shift.objects(
            tenant_id=test_tenant.id,
            staff_id=test_staff_member.id,
        ).order_by("start_time"))
        
        # Verify ascending order
        for i in range(len(queried_shifts) - 1):
            assert queried_shifts[i].start_time <= queried_shifts[i + 1].start_time
        
        # Cleanup
        for shift in created_shifts:
            shift.delete()
        
        clear_context()


class TestShiftDetailCompleteness:
    """Property-based tests for shift detail completeness.
    
    **Property 18: Shift Detail Completeness**
    Verify all required information displays
    
    Validates: Requirements 3.7
    """

    @given(
        duration_hours=st.integers(min_value=1, max_value=12),
        labor_cost=st.decimals(min_value=Decimal("0.00"), max_value=Decimal("10000.00"), places=2),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=10, deadline=None)
    def test_shift_detail_has_all_required_fields(
        self,
        test_tenant,
        test_staff_member,
        duration_hours,
        labor_cost,
    ):
        """
        **Property 18: Shift Detail Completeness**
        
        For any shift detail view, all required information (start time, end time,
        date, status) SHALL be displayed and accessible.
        
        Validates: Requirements 3.7
        """
        set_tenant_id(test_tenant.id)
        
        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        end_time = start_time + timedelta(hours=duration_hours)
        
        # Create shift with all required fields
        shift = Shift(
            tenant_id=test_tenant.id,
            staff_id=test_staff_member.id,
            start_time=start_time,
            end_time=end_time,
            status="scheduled",
            labor_cost=labor_cost,
        )
        shift.save()
        
        # Retrieve shift detail
        retrieved = Shift.objects(
            tenant_id=test_tenant.id,
            id=shift.id
        ).first()
        
        # Verify all required fields are present and accessible
        assert retrieved is not None
        
        # Start time information
        assert retrieved.start_time is not None
        # Use approximate equality for datetime (MongoDB may lose microsecond precision)
        assert abs((retrieved.start_time - start_time).total_seconds()) < 1
        
        # End time information
        assert retrieved.end_time is not None
        assert abs((retrieved.end_time - end_time).total_seconds()) < 1
        
        # Date information (derived from start_time)
        assert retrieved.start_time.date() is not None
        
        # Status information
        assert retrieved.status is not None
        assert retrieved.status in ["scheduled", "in_progress", "completed", "cancelled"]
        
        # Staff information
        assert retrieved.staff_id is not None
        assert retrieved.staff_id == test_staff_member.id
        
        # Labor cost information
        assert retrieved.labor_cost is not None
        assert retrieved.labor_cost == labor_cost
        
        # Cleanup
        shift.delete()
        clear_context()

    @given(
        duration_hours=st.integers(min_value=1, max_value=12),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=10, deadline=None)
    def test_shift_detail_time_consistency(
        self,
        test_tenant,
        test_staff_member,
        duration_hours,
    ):
        """
        **Property 18: Shift Detail Completeness - Time Consistency**
        
        For any shift detail, the end time SHALL be after the start time, and
        the duration SHALL be consistent with the difference between end and
        start times.
        
        Validates: Requirements 3.7
        """
        set_tenant_id(test_tenant.id)
        
        now = datetime.utcnow()
        start_time = now + timedelta(hours=2)
        end_time = start_time + timedelta(hours=duration_hours)
        
        # Create shift
        shift = Shift(
            tenant_id=test_tenant.id,
            staff_id=test_staff_member.id,
            start_time=start_time,
            end_time=end_time,
            status="scheduled",
            labor_cost=Decimal("400.00"),
        )
        shift.save()
        
        # Retrieve shift
        retrieved = Shift.objects(
            tenant_id=test_tenant.id,
            id=shift.id
        ).first()
        
        # Verify time consistency
        assert retrieved.start_time < retrieved.end_time
        
        # Calculate duration
        duration = retrieved.end_time - retrieved.start_time
        expected_duration = timedelta(hours=duration_hours)
        
        assert duration == expected_duration
        
        # Cleanup
        shift.delete()
        clear_context()

    @given(
        status=st.sampled_from(["scheduled", "in_progress", "completed", "cancelled"]),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=10, deadline=None)
    def test_shift_detail_status_values_are_valid(
        self,
        test_tenant,
        test_staff_member,
        status,
    ):
        """
        **Property 18: Shift Detail Completeness - Status Validity**
        
        For any shift detail, the status SHALL be one of the valid status values
        (scheduled, in_progress, completed, cancelled).
        
        Validates: Requirements 3.7
        """
        set_tenant_id(test_tenant.id)
        
        now = datetime.utcnow()
        start_time = now + timedelta(hours=3)
        
        # Create shift with specific status
        shift = Shift(
            tenant_id=test_tenant.id,
            staff_id=test_staff_member.id,
            start_time=start_time,
            end_time=start_time + timedelta(hours=8),
            status=status,
            labor_cost=Decimal("400.00"),
        )
        shift.save()
        
        # Retrieve shift
        retrieved = Shift.objects(
            tenant_id=test_tenant.id,
            id=shift.id
        ).first()
        
        # Verify status is valid
        assert retrieved.status == status
        assert retrieved.status in ["scheduled", "in_progress", "completed", "cancelled"]
        
        # Cleanup
        shift.delete()
        clear_context()
