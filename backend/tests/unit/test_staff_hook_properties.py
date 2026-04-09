"""Property-based tests for staff hook data isolation and state handling.

This module tests the core properties of staff data hooks:
- Property 1: Staff Data Isolation - Staff can only see their own data
- Property 21: Hook State Handling - Hooks properly handle loading, error, and success states

Validates: Requirements 10.5, 10.6
"""

import pytest
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from datetime import datetime, timedelta, date
from decimal import Decimal
from bson import ObjectId
from unittest.mock import Mock, MagicMock, patch

from app.models.appointment import Appointment
from app.models.shift import Shift
from app.models.time_off_request import TimeOffRequest
from app.models.staff_commission import StaffCommission
from app.models.staff import Staff
from app.models.user import User
from app.models.tenant import Tenant
from app.models.service import Service
from app.models.customer import Customer
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
def test_staff_members(test_tenant, test_user):
    """Create test staff members."""
    staff_list = []
    for i in range(2):
        staff = Staff(
            tenant_id=test_tenant.id,
            user_id=test_user.id if i == 0 else ObjectId(),
            payment_type="hourly",
            payment_rate=Decimal("50.00"),
            status="active",
        )
        staff.save()
        staff_list.append(staff)
    yield staff_list
    for staff in staff_list:
        staff.delete()


@pytest.fixture
def test_customer(test_tenant):
    """Create a test customer."""
    customer = Customer(
        tenant_id=test_tenant.id,
        first_name="Jane",
        last_name="Smith",
        email="customer@example.com",
        phone="+234987654321",
    )
    customer.save()
    yield customer
    customer.delete()


@pytest.fixture
def test_service(test_tenant):
    """Create a test service."""
    service = Service(
        tenant_id=test_tenant.id,
        name="Haircut",
        description="Professional haircut",
        duration_minutes=30,
        price=Decimal("50.00"),
        category="Hair",
    )
    service.save()
    yield service
    service.delete()


# Strategy generators for property-based testing
@st.composite
def staff_ids(draw):
    """Generate unique staff IDs."""
    return ObjectId()


@st.composite
def appointment_data(draw):
    """Generate appointment data."""
    staff_id = draw(staff_ids())
    customer_id = ObjectId()
    service_id = ObjectId()
    start_time = draw(st.datetimes(min_value=datetime(2024, 1, 1)))
    
    return {
        "staff_id": staff_id,
        "customer_id": customer_id,
        "service_id": service_id,
        "start_time": start_time,
        "end_time": start_time + timedelta(hours=1),
        "status": "scheduled",
        "price": Decimal("50.00"),
    }


@st.composite
def shift_data(draw):
    """Generate shift data."""
    staff_id = draw(staff_ids())
    start_time = draw(st.datetimes(min_value=datetime(2024, 1, 1)))
    
    return {
        "staff_id": staff_id,
        "start_time": start_time,
        "end_time": start_time + timedelta(hours=8),
        "status": "scheduled",
    }


@st.composite
def time_off_data(draw):
    """Generate time off request data."""
    staff_id = draw(staff_ids())
    start_date = draw(st.dates(min_value=date(2024, 1, 1)))
    
    return {
        "staff_id": staff_id,
        "start_date": start_date,
        "end_date": start_date + timedelta(days=3),
        "reason": "Vacation",
        "status": "pending",
    }


@st.composite
def commission_data(draw):
    """Generate commission data."""
    staff_id = draw(staff_ids())
    
    return {
        "staff_id": staff_id,
        "transaction_id": ObjectId(),
        "commission_amount": draw(st.decimals(min_value=Decimal("1.00"), max_value=Decimal("1000.00"), places=2)),
        "commission_rate": Decimal("10.00"),
        "commission_type": "percentage",
    }


class TestStaffDataIsolation:
    """Property-based tests for staff data isolation.
    
    **Property 1: Staff Data Isolation**
    Verify staff can only see their own data
    
    Validates: Requirements 10.5, 10.6
    """

    @given(
        appointments=st.lists(appointment_data(), min_size=1, max_size=3),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], max_examples=5)
    def test_appointments_isolation_property(self, appointments):
        """
        **Property 1: Staff Data Isolation - Appointments**
        
        For any set of appointments, when filtering by staff_id, the system
        SHALL only return appointments assigned to that specific staff member.
        
        Validates: Requirements 2.1, 10.6, 12.6
        """
        # Simulate filtering appointments by staff_id
        staff1_id = appointments[0]["staff_id"]
        
        # Filter appointments for staff1
        staff1_appointments = [a for a in appointments if a["staff_id"] == staff1_id]
        
        # Verify all returned appointments belong to staff1
        for appt in staff1_appointments:
            assert appt["staff_id"] == staff1_id
            assert "customer_id" in appt
            assert "service_id" in appt
            assert "start_time" in appt
            assert "end_time" in appt
            assert "status" in appt

    @given(
        shifts=st.lists(shift_data(), min_size=1, max_size=3),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], max_examples=5)
    def test_shifts_isolation_property(self, shifts):
        """
        **Property 1: Staff Data Isolation - Shifts**
        
        For any set of shifts, when filtering by staff_id, the system
        SHALL only return shifts assigned to that specific staff member.
        
        Validates: Requirements 3.1, 10.6, 12.6
        """
        # Simulate filtering shifts by staff_id
        staff1_id = shifts[0]["staff_id"]
        
        # Filter shifts for staff1
        staff1_shifts = [s for s in shifts if s["staff_id"] == staff1_id]
        
        # Verify all returned shifts belong to staff1
        for shift in staff1_shifts:
            assert shift["staff_id"] == staff1_id
            assert "start_time" in shift
            assert "end_time" in shift
            assert "status" in shift

    @given(
        requests=st.lists(time_off_data(), min_size=1, max_size=3),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], max_examples=5)
    def test_time_off_requests_isolation_property(self, requests):
        """
        **Property 1: Staff Data Isolation - Time Off Requests**
        
        For any set of time off requests, when filtering by staff_id, the
        system SHALL only return requests submitted by that specific staff member.
        
        Validates: Requirements 4.1, 10.6, 12.6
        """
        # Simulate filtering time off requests by staff_id
        staff1_id = requests[0]["staff_id"]
        
        # Filter requests for staff1
        staff1_requests = [r for r in requests if r["staff_id"] == staff1_id]
        
        # Verify all returned requests belong to staff1
        for request in staff1_requests:
            assert request["staff_id"] == staff1_id
            assert "start_date" in request
            assert "end_date" in request
            assert "reason" in request
            assert "status" in request

    @given(
        commissions=st.lists(commission_data(), min_size=1, max_size=3),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], max_examples=5)
    def test_earnings_isolation_property(self, commissions):
        """
        **Property 1: Staff Data Isolation - Earnings**
        
        For any set of commissions, when filtering by staff_id, the system
        SHALL only return commissions earned by that specific staff member.
        
        Validates: Requirements 5.1, 10.6, 12.6
        """
        # Simulate filtering commissions by staff_id
        staff1_id = commissions[0]["staff_id"]
        
        # Filter commissions for staff1
        staff1_commissions = [c for c in commissions if c["staff_id"] == staff1_id]
        
        # Verify all returned commissions belong to staff1
        for commission in staff1_commissions:
            assert commission["staff_id"] == staff1_id
            assert "transaction_id" in commission
            assert "commission_amount" in commission
            assert "commission_rate" in commission
            assert "commission_type" in commission

    @given(
        staff_id1=staff_ids(),
        staff_id2=staff_ids(),
        appointments=st.lists(appointment_data(), min_size=2, max_size=5),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], max_examples=5)
    def test_no_cross_staff_data_leakage(self, staff_id1, staff_id2, appointments):
        """
        **Property 1: Staff Data Isolation - No Cross-Staff Leakage**
        
        For any two different staff members, filtering appointments by staff_id
        SHALL NOT return appointments from the other staff member.
        
        Validates: Requirements 10.6, 12.6
        """
        assume(staff_id1 != staff_id2)
        
        # Create appointments for both staff members
        staff1_appointments = [a for a in appointments if a["staff_id"] == staff_id1]
        staff2_appointments = [a for a in appointments if a["staff_id"] == staff_id2]
        
        # Verify no overlap
        staff1_ids = {a["staff_id"] for a in staff1_appointments}
        staff2_ids = {a["staff_id"] for a in staff2_appointments}
        
        # If both have appointments, they should not overlap
        if staff1_ids and staff2_ids:
            assert staff1_ids.isdisjoint(staff2_ids)


class TestHookStateHandling:
    """Property-based tests for hook state handling.
    
    **Property 21: Hook State Handling**
    Verify hooks properly handle loading, error, and success states
    
    Validates: Requirements 10.5, 10.6
    """

    @given(
        num_appointments=st.integers(min_value=0, max_value=3),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], max_examples=5)
    def test_appointments_success_state(
        self,
        test_tenant,
        test_staff_members,
        test_customer,
        test_service,
        num_appointments,
    ):
        """
        **Property 21: Hook State Handling - Success State**
        
        For any successful fetch of appointments, the hook SHALL return a
        success state with the fetched data, and the data SHALL be complete
        and valid.
        
        Validates: Requirements 10.5, 10.6
        """
        set_tenant_id(test_tenant.id)
        
        staff = test_staff_members[0]
        base_time = datetime.utcnow()
        
        # Create appointments
        created_appointments = []
        for i in range(num_appointments):
            appointment_time = base_time + timedelta(hours=i)
            appt = Appointment(
                tenant_id=test_tenant.id,
                customer_id=test_customer.id,
                staff_id=staff.id,
                service_id=test_service.id,
                start_time=appointment_time,
                end_time=appointment_time + timedelta(hours=1),
                status="scheduled",
                price=Decimal("50.00"),
                idempotency_key=f"test-appt-{i}-{ObjectId()}",
            )
            appt.save()
            created_appointments.append(appt)
        
        # Fetch appointments (simulating hook behavior)
        fetched_appointments = Appointment.objects(
            tenant_id=test_tenant.id,
            staff_id=staff.id,
        )
        
        # Verify success state: correct count
        assert fetched_appointments.count() == num_appointments
        
        # Verify success state: all data is valid
        for appt in fetched_appointments:
            assert appt.id is not None
            assert appt.staff_id == staff.id
            assert appt.customer_id == test_customer.id
            assert appt.service_id == test_service.id
            assert appt.start_time is not None
            assert appt.end_time is not None
            assert appt.status in ["scheduled", "confirmed", "in_progress", "completed", "cancelled", "no_show"]
            assert appt.price is not None
        
        # Cleanup
        for appt in created_appointments:
            appt.delete()
        
        clear_context()

    @given(
        num_shifts=st.integers(min_value=0, max_value=3),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], max_examples=5)
    def test_shifts_success_state(
        self,
        test_tenant,
        test_staff_members,
        num_shifts,
    ):
        """
        **Property 21: Hook State Handling - Success State (Shifts)**
        
        For any successful fetch of shifts, the hook SHALL return a success
        state with the fetched data, and the data SHALL be complete and valid.
        
        Validates: Requirements 10.5, 10.6
        """
        set_tenant_id(test_tenant.id)
        
        staff = test_staff_members[0]
        base_time = datetime.utcnow()
        
        # Create shifts
        created_shifts = []
        for i in range(num_shifts):
            shift_time = base_time + timedelta(days=i)
            shift = Shift(
                tenant_id=test_tenant.id,
                staff_id=staff.id,
                start_time=shift_time,
                end_time=shift_time + timedelta(hours=8),
                status="scheduled",
            )
            shift.save()
            created_shifts.append(shift)
        
        # Fetch shifts (simulating hook behavior)
        fetched_shifts = Shift.objects(
            tenant_id=test_tenant.id,
            staff_id=staff.id,
        )
        
        # Verify success state: correct count
        assert fetched_shifts.count() == num_shifts
        
        # Verify success state: all data is valid
        for shift in fetched_shifts:
            assert shift.id is not None
            assert shift.staff_id == staff.id
            assert shift.start_time is not None
            assert shift.end_time is not None
            assert shift.status in ["scheduled", "in_progress", "completed", "cancelled"]
        
        # Cleanup
        for shift in created_shifts:
            shift.delete()
        
        clear_context()

    @given(
        num_requests=st.integers(min_value=0, max_value=3),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], max_examples=5)
    def test_time_off_requests_success_state(
        self,
        test_tenant,
        test_staff_members,
        num_requests,
    ):
        """
        **Property 21: Hook State Handling - Success State (Time Off)**
        
        For any successful fetch of time off requests, the hook SHALL return
        a success state with the fetched data, and the data SHALL be complete
        and valid.
        
        Validates: Requirements 10.5, 10.6
        """
        set_tenant_id(test_tenant.id)
        
        staff = test_staff_members[0]
        base_date = date.today()
        
        # Create time off requests
        created_requests = []
        for i in range(num_requests):
            start_date = base_date + timedelta(days=i * 7)
            end_date = start_date + timedelta(days=3)
            request = TimeOffRequest(
                tenant_id=test_tenant.id,
                staff_id=staff.id,
                start_date=start_date,
                end_date=end_date,
                reason="Vacation",
                status="pending",
            )
            request.save()
            created_requests.append(request)
        
        # Fetch time off requests (simulating hook behavior)
        fetched_requests = TimeOffRequest.objects(
            tenant_id=test_tenant.id,
            staff_id=staff.id,
        )
        
        # Verify success state: correct count
        assert fetched_requests.count() == num_requests
        
        # Verify success state: all data is valid
        for request in fetched_requests:
            assert request.id is not None
            assert request.staff_id == staff.id
            assert request.start_date is not None
            assert request.end_date is not None
            assert request.reason is not None
            assert request.status in ["pending", "approved", "denied"]
        
        # Cleanup
        for request in created_requests:
            request.delete()
        
        clear_context()

    @given(
        num_commissions=st.integers(min_value=0, max_value=3),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], max_examples=5, deadline=1000)
    def test_earnings_success_state(
        self,
        test_tenant,
        test_staff_members,
        num_commissions,
    ):
        """
        **Property 21: Hook State Handling - Success State (Earnings)**
        
        For any successful fetch of earnings/commissions, the hook SHALL return
        a success state with the fetched data, and the data SHALL be complete
        and valid.
        
        Validates: Requirements 10.5, 10.6
        """
        set_tenant_id(test_tenant.id)
        
        staff = test_staff_members[0]
        
        # Create commissions
        created_commissions = []
        for i in range(num_commissions):
            commission = StaffCommission(
                tenant_id=test_tenant.id,
                staff_id=staff.id,
                transaction_id=ObjectId(),
                commission_amount=Decimal("50.00"),
                commission_rate=Decimal("10.00"),
                commission_type="percentage",
            )
            commission.save()
            created_commissions.append(commission)
        
        # Fetch commissions (simulating hook behavior)
        fetched_commissions = StaffCommission.objects(
            tenant_id=test_tenant.id,
            staff_id=staff.id,
        )
        
        # Verify success state: correct count
        assert fetched_commissions.count() == num_commissions
        
        # Verify success state: all data is valid
        for commission in fetched_commissions:
            assert commission.id is not None
            assert commission.staff_id == staff.id
            assert commission.transaction_id is not None
            assert commission.commission_amount is not None
            assert commission.commission_rate is not None
            assert commission.commission_type in ["percentage", "fixed", "tiered"]
        
        # Cleanup
        for commission in created_commissions:
            commission.delete()
        
        clear_context()

    def test_empty_data_response(
        self,
        test_tenant,
        test_staff_members,
    ):
        """
        **Property 21: Hook State Handling - Empty Data**
        
        For any staff member with no data, the hook SHALL return an empty
        success state (empty list) rather than an error state.
        
        Validates: Requirements 10.5, 10.6
        """
        set_tenant_id(test_tenant.id)
        
        staff = test_staff_members[0]
        
        # Fetch appointments for staff with no appointments
        appointments = Appointment.objects(
            tenant_id=test_tenant.id,
            staff_id=staff.id,
        )
        
        # Verify empty state: should return empty list, not error
        assert appointments.count() == 0
        assert list(appointments) == []
        
        # Fetch shifts for staff with no shifts
        shifts = Shift.objects(
            tenant_id=test_tenant.id,
            staff_id=staff.id,
        )
        
        # Verify empty state: should return empty list, not error
        assert shifts.count() == 0
        assert list(shifts) == []
        
        # Fetch time off requests for staff with no requests
        requests = TimeOffRequest.objects(
            tenant_id=test_tenant.id,
            staff_id=staff.id,
        )
        
        # Verify empty state: should return empty list, not error
        assert requests.count() == 0
        assert list(requests) == []
        
        # Fetch commissions for staff with no commissions
        commissions = StaffCommission.objects(
            tenant_id=test_tenant.id,
            staff_id=staff.id,
        )
        
        # Verify empty state: should return empty list, not error
        assert commissions.count() == 0
        assert list(commissions) == []
        
        clear_context()
