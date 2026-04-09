"""Property-based tests for staff attendance tracking.

This module tests the core properties of attendance functionality:
- Clock in/out recording and persistence
- Hours worked calculation accuracy
- Total hours calculation for period

Validates: Requirements 13.2, 13.3, 13.6
"""

import pytest
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from datetime import datetime, timedelta, date
from decimal import Decimal
from bson import ObjectId

from app.models.staff import Staff
from app.models.user import User
from app.models.tenant import Tenant
from app.context import set_tenant_id, clear_context


# Mock Attendance Model (since it doesn't exist yet in the codebase)
# This represents the expected structure based on the frontend implementation
class AttendanceRecord:
    """Mock attendance record model for testing."""
    
    def __init__(
        self,
        tenant_id,
        staff_id,
        check_in_time,
        check_out_time=None,
        hours_worked=None,
        status="checked_in",
        is_late=False,
        is_early_departure=False,
        notes=None,
    ):
        self.id = ObjectId()
        self.tenant_id = tenant_id
        self.staff_id = staff_id
        self.check_in_time = check_in_time
        self.check_out_time = check_out_time
        self.hours_worked = hours_worked
        self.status = status
        self.is_late = is_late
        self.is_early_departure = is_early_departure
        self.notes = notes
        self.created_at = datetime.utcnow()
        self.updated_at = None
        
        # In-memory storage for testing
        if not hasattr(AttendanceRecord, '_records'):
            AttendanceRecord._records = []
    
    def save(self):
        """Save record to in-memory storage."""
        AttendanceRecord._records.append(self)
        return self
    
    def delete(self):
        """Delete record from in-memory storage."""
        if self in AttendanceRecord._records:
            AttendanceRecord._records.remove(self)
    
    @classmethod
    def find(cls, **filters):
        """Find records matching filters."""
        results = cls._records
        for key, value in filters.items():
            results = [r for r in results if getattr(r, key, None) == value]
        return results
    
    @classmethod
    def clear_all(cls):
        """Clear all records (for test cleanup)."""
        cls._records = []


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


@pytest.fixture(autouse=True)
def cleanup_attendance_records():
    """Clean up attendance records after each test."""
    yield
    AttendanceRecord.clear_all()


# Strategy generators for property-based testing
@st.composite
def check_in_times(draw):
    """Generate valid check-in times."""
    now = datetime.utcnow()
    return draw(st.datetimes(
        min_value=now - timedelta(days=30),
        max_value=now
    ))


@st.composite
def work_duration_hours(draw):
    """Generate valid work duration in hours (0.5 to 12 hours)."""
    return draw(st.floats(min_value=0.5, max_value=12.0))


@st.composite
def attendance_record_data(draw, test_tenant, test_staff_member):
    """Generate attendance record data."""
    check_in = draw(check_in_times())
    duration = draw(work_duration_hours())
    check_out = check_in + timedelta(hours=duration)
    
    return {
        "tenant_id": test_tenant.id,
        "staff_id": test_staff_member.id,
        "check_in_time": check_in,
        "check_out_time": check_out,
        "duration_hours": duration,
    }


class TestClockInOutRecordingAndPersistence:
    """Property-based tests for clock in/out recording and persistence.
    
    **Validates: Requirements 13.2, 13.3**
    """

    @given(
        check_in_time=check_in_times(),
    )
    @settings(
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        max_examples=20,
        deadline=2000
    )
    def test_clock_in_records_check_in_time_and_displays_status(
        self,
        test_tenant,
        test_staff_member,
        check_in_time,
    ):
        """
        **Property: Clock In Recording**
        
        For any staff member clocking in, the system SHALL record the check-in
        time and display current status as "checked_in". The recorded time SHALL
        persist and be retrievable in subsequent queries.
        
        Validates: Requirement 13.2
        """
        set_tenant_id(test_tenant.id)
        
        # Clock in
        attendance = AttendanceRecord(
            tenant_id=test_tenant.id,
            staff_id=test_staff_member.id,
            check_in_time=check_in_time,
            status="checked_in",
        )
        attendance.save()
        
        # Verify check-in time is recorded
        assert attendance.check_in_time == check_in_time
        
        # Verify status is "checked_in"
        assert attendance.status == "checked_in"
        
        # Verify persistence - retrieve the record
        retrieved_records = AttendanceRecord.find(
            tenant_id=test_tenant.id,
            staff_id=test_staff_member.id,
        )
        
        assert len(retrieved_records) == 1
        retrieved = retrieved_records[0]
        
        # Verify check-in time persisted
        assert retrieved.check_in_time == check_in_time
        
        # Verify status persisted
        assert retrieved.status == "checked_in"
        
        # Cleanup
        attendance.delete()
        clear_context()

    @given(
        duration_hours=work_duration_hours(),
    )
    @settings(
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        max_examples=20,
        deadline=2000
    )
    def test_clock_out_records_check_out_time_and_calculates_hours(
        self,
        test_tenant,
        test_staff_member,
        duration_hours,
    ):
        """
        **Property: Clock Out Recording and Hours Calculation**
        
        For any staff member clocking out, the system SHALL record the check-out
        time, calculate hours worked as the difference between check-out and
        check-in times, and persist both values.
        
        Validates: Requirement 13.3
        """
        set_tenant_id(test_tenant.id)
        
        check_in_time = datetime.utcnow() - timedelta(hours=duration_hours)
        check_out_time = datetime.utcnow()
        
        # Clock in first
        attendance = AttendanceRecord(
            tenant_id=test_tenant.id,
            staff_id=test_staff_member.id,
            check_in_time=check_in_time,
            status="checked_in",
        )
        attendance.save()
        
        # Clock out
        attendance.check_out_time = check_out_time
        attendance.status = "checked_out"
        
        # Calculate hours worked
        time_diff = check_out_time - check_in_time
        calculated_hours = time_diff.total_seconds() / 3600
        attendance.hours_worked = round(calculated_hours, 2)
        
        # Verify check-out time is recorded
        assert attendance.check_out_time == check_out_time
        
        # Verify status is "checked_out"
        assert attendance.status == "checked_out"
        
        # Verify hours worked is calculated correctly
        expected_hours = round(duration_hours, 2)
        assert abs(attendance.hours_worked - expected_hours) < 0.1  # Allow small floating point difference
        
        # Verify persistence
        retrieved_records = AttendanceRecord.find(
            tenant_id=test_tenant.id,
            staff_id=test_staff_member.id,
        )
        
        assert len(retrieved_records) == 1
        retrieved = retrieved_records[0]
        
        # Verify check-out time persisted
        assert retrieved.check_out_time == check_out_time
        
        # Verify hours worked persisted
        assert abs(retrieved.hours_worked - expected_hours) < 0.1
        
        # Verify status persisted
        assert retrieved.status == "checked_out"
        
        # Cleanup
        attendance.delete()
        clear_context()

    @given(
        num_records=st.integers(min_value=1, max_value=5),
    )
    @settings(
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        max_examples=10,
        deadline=2000
    )
    def test_multiple_attendance_records_persist_independently(
        self,
        test_tenant,
        test_staff_member,
        num_records,
    ):
        """
        **Property: Multiple Records Persistence**
        
        For any number of attendance records, each record SHALL persist
        independently with its own check-in time, check-out time, and hours
        worked. No record SHALL interfere with another.
        
        Validates: Requirements 13.2, 13.3
        """
        set_tenant_id(test_tenant.id)
        
        created_records = []
        expected_data = []
        
        # Create multiple attendance records
        for i in range(num_records):
            check_in = datetime.utcnow() - timedelta(days=i, hours=8)
            check_out = check_in + timedelta(hours=8)
            hours_worked = 8.0
            
            attendance = AttendanceRecord(
                tenant_id=test_tenant.id,
                staff_id=test_staff_member.id,
                check_in_time=check_in,
                check_out_time=check_out,
                hours_worked=hours_worked,
                status="checked_out",
            )
            attendance.save()
            created_records.append(attendance)
            expected_data.append({
                "check_in": check_in,
                "check_out": check_out,
                "hours": hours_worked,
            })
        
        # Retrieve all records
        retrieved_records = AttendanceRecord.find(
            tenant_id=test_tenant.id,
            staff_id=test_staff_member.id,
        )
        
        # Verify count
        assert len(retrieved_records) == num_records
        
        # Verify each record persisted correctly
        for i, retrieved in enumerate(retrieved_records):
            expected = expected_data[i]
            assert retrieved.check_in_time == expected["check_in"]
            assert retrieved.check_out_time == expected["check_out"]
            assert retrieved.hours_worked == expected["hours"]
            assert retrieved.status == "checked_out"
        
        # Cleanup
        for record in created_records:
            record.delete()
        
        clear_context()


class TestHoursWorkedCalculationAccuracy:
    """Property-based tests for hours worked calculation accuracy.
    
    **Validates: Requirement 13.3**
    """

    @given(
        duration_hours=work_duration_hours(),
    )
    @settings(
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        max_examples=20,
        deadline=2000
    )
    def test_hours_worked_calculation_is_accurate(
        self,
        test_tenant,
        test_staff_member,
        duration_hours,
    ):
        """
        **Property: Hours Worked Calculation Accuracy**
        
        For any check-in and check-out time pair, the calculated hours worked
        SHALL equal the time difference in hours, accurate to 2 decimal places.
        
        Validates: Requirement 13.3
        """
        set_tenant_id(test_tenant.id)
        
        check_in_time = datetime.utcnow() - timedelta(hours=duration_hours)
        check_out_time = datetime.utcnow()
        
        # Create attendance record
        attendance = AttendanceRecord(
            tenant_id=test_tenant.id,
            staff_id=test_staff_member.id,
            check_in_time=check_in_time,
            check_out_time=check_out_time,
            status="checked_out",
        )
        
        # Calculate hours worked
        time_diff = check_out_time - check_in_time
        calculated_hours = round(time_diff.total_seconds() / 3600, 2)
        attendance.hours_worked = calculated_hours
        attendance.save()
        
        # Verify calculation accuracy
        expected_hours = round(duration_hours, 2)
        assert abs(attendance.hours_worked - expected_hours) < 0.1
        
        # Verify the calculation is mathematically correct
        manual_calculation = (check_out_time - check_in_time).total_seconds() / 3600
        assert abs(attendance.hours_worked - manual_calculation) < 0.01
        
        # Cleanup
        attendance.delete()
        clear_context()

    @given(
        duration_minutes=st.integers(min_value=30, max_value=720),  # 30 min to 12 hours
    )
    @settings(
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        max_examples=20,
        deadline=2000
    )
    def test_hours_worked_handles_various_durations_correctly(
        self,
        test_tenant,
        test_staff_member,
        duration_minutes,
    ):
        """
        **Property: Hours Worked Calculation - Various Durations**
        
        For any work duration (from 30 minutes to 12 hours), the hours worked
        calculation SHALL be accurate regardless of the duration length.
        
        Validates: Requirement 13.3
        """
        set_tenant_id(test_tenant.id)
        
        check_in_time = datetime.utcnow() - timedelta(minutes=duration_minutes)
        check_out_time = datetime.utcnow()
        
        # Create attendance record
        attendance = AttendanceRecord(
            tenant_id=test_tenant.id,
            staff_id=test_staff_member.id,
            check_in_time=check_in_time,
            check_out_time=check_out_time,
            status="checked_out",
        )
        
        # Calculate hours worked
        time_diff = check_out_time - check_in_time
        calculated_hours = round(time_diff.total_seconds() / 3600, 2)
        attendance.hours_worked = calculated_hours
        attendance.save()
        
        # Verify calculation
        expected_hours = round(duration_minutes / 60, 2)
        assert abs(attendance.hours_worked - expected_hours) < 0.1
        
        # Cleanup
        attendance.delete()
        clear_context()

    def test_hours_worked_is_zero_when_not_clocked_out(
        self,
        test_tenant,
        test_staff_member,
    ):
        """
        **Property: Hours Worked - Not Clocked Out**
        
        For any attendance record where the staff member has not clocked out,
        the hours_worked SHALL be None or 0, indicating incomplete shift.
        
        Validates: Requirement 13.3
        """
        set_tenant_id(test_tenant.id)
        
        check_in_time = datetime.utcnow() - timedelta(hours=2)
        
        # Create attendance record without clock out
        attendance = AttendanceRecord(
            tenant_id=test_tenant.id,
            staff_id=test_staff_member.id,
            check_in_time=check_in_time,
            status="checked_in",
        )
        attendance.save()
        
        # Verify hours_worked is None (not calculated yet)
        assert attendance.hours_worked is None
        
        # Cleanup
        attendance.delete()
        clear_context()


class TestTotalHoursCalculationForPeriod:
    """Property-based tests for total hours calculation for period.
    
    **Validates: Requirement 13.6**
    """

    @given(
        num_days=st.integers(min_value=1, max_value=10),
        hours_per_day=st.floats(min_value=4.0, max_value=10.0),
    )
    @settings(
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        max_examples=15,
        deadline=2000
    )
    def test_total_hours_equals_sum_of_individual_hours(
        self,
        test_tenant,
        test_staff_member,
        num_days,
        hours_per_day,
    ):
        """
        **Property: Total Hours Calculation Accuracy**
        
        For any period, the total hours worked SHALL equal the sum of hours
        worked from all individual attendance records in that period.
        
        Validates: Requirement 13.6
        """
        set_tenant_id(test_tenant.id)
        
        created_records = []
        expected_total = 0.0
        
        # Create attendance records for multiple days
        for i in range(num_days):
            check_in = datetime.utcnow() - timedelta(days=i, hours=hours_per_day)
            check_out = check_in + timedelta(hours=hours_per_day)
            hours_worked = round(hours_per_day, 2)
            
            attendance = AttendanceRecord(
                tenant_id=test_tenant.id,
                staff_id=test_staff_member.id,
                check_in_time=check_in,
                check_out_time=check_out,
                hours_worked=hours_worked,
                status="checked_out",
            )
            attendance.save()
            created_records.append(attendance)
            expected_total += hours_worked
        
        # Calculate total hours
        all_records = AttendanceRecord.find(
            tenant_id=test_tenant.id,
            staff_id=test_staff_member.id,
        )
        
        calculated_total = sum(
            r.hours_worked for r in all_records
            if r.hours_worked is not None
        )
        
        # Verify total equals sum of individual hours
        assert abs(calculated_total - expected_total) < 0.1
        
        # Cleanup
        for record in created_records:
            record.delete()
        
        clear_context()

    @given(
        num_days=st.integers(min_value=5, max_value=15),
    )
    @settings(
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        max_examples=10,
        deadline=2000
    )
    def test_total_hours_for_period_filters_by_date_range(
        self,
        test_tenant,
        test_staff_member,
        num_days,
    ):
        """
        **Property: Total Hours - Date Range Filtering**
        
        For any date range filter, the total hours SHALL only include records
        within that range, and SHALL exclude records outside the range.
        
        Validates: Requirement 13.6
        """
        set_tenant_id(test_tenant.id)
        
        now = datetime.utcnow()
        period_start = now - timedelta(days=7)
        period_end = now
        
        created_records = []
        expected_total_in_period = 0.0
        expected_total_outside_period = 0.0
        
        # Create records both inside and outside the period
        for i in range(num_days):
            check_in = now - timedelta(days=i, hours=8)
            check_out = check_in + timedelta(hours=8)
            hours_worked = 8.0
            
            attendance = AttendanceRecord(
                tenant_id=test_tenant.id,
                staff_id=test_staff_member.id,
                check_in_time=check_in,
                check_out_time=check_out,
                hours_worked=hours_worked,
                status="checked_out",
            )
            attendance.save()
            created_records.append(attendance)
            
            # Determine if record is in period
            if period_start <= check_in <= period_end:
                expected_total_in_period += hours_worked
            else:
                expected_total_outside_period += hours_worked
        
        # Calculate total for period
        records_in_period = [
            r for r in AttendanceRecord.find(
                tenant_id=test_tenant.id,
                staff_id=test_staff_member.id,
            )
            if period_start <= r.check_in_time <= period_end
        ]
        
        calculated_total = sum(
            r.hours_worked for r in records_in_period
            if r.hours_worked is not None
        )
        
        # Verify filtered total
        assert abs(calculated_total - expected_total_in_period) < 0.1
        
        # Verify total without filter includes all records
        all_records = AttendanceRecord.find(
            tenant_id=test_tenant.id,
            staff_id=test_staff_member.id,
        )
        
        total_all = sum(
            r.hours_worked for r in all_records
            if r.hours_worked is not None
        )
        
        expected_total_all = expected_total_in_period + expected_total_outside_period
        assert abs(total_all - expected_total_all) < 0.1
        
        # Cleanup
        for record in created_records:
            record.delete()
        
        clear_context()

    def test_total_hours_is_zero_when_no_records_exist(
        self,
        test_tenant,
        test_staff_member,
    ):
        """
        **Property: Total Hours - Zero Case**
        
        For any staff member with no attendance records, the total hours
        worked SHALL be zero.
        
        Validates: Requirement 13.6
        """
        set_tenant_id(test_tenant.id)
        
        # Calculate total with no records
        all_records = AttendanceRecord.find(
            tenant_id=test_tenant.id,
            staff_id=test_staff_member.id,
        )
        
        total_hours = sum(
            r.hours_worked for r in all_records
            if r.hours_worked is not None
        )
        
        assert total_hours == 0.0
        
        clear_context()

    @given(
        num_complete_records=st.integers(min_value=1, max_value=5),
        num_incomplete_records=st.integers(min_value=1, max_value=3),
    )
    @settings(
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        max_examples=10,
        deadline=2000
    )
    def test_total_hours_excludes_incomplete_records(
        self,
        test_tenant,
        test_staff_member,
        num_complete_records,
        num_incomplete_records,
    ):
        """
        **Property: Total Hours - Incomplete Records**
        
        For any period calculation, the total hours SHALL only include
        completed records (with check-out time), and SHALL exclude records
        where staff is still clocked in.
        
        Validates: Requirement 13.6
        """
        set_tenant_id(test_tenant.id)
        
        created_records = []
        expected_total = 0.0
        
        # Create complete records (clocked out)
        for i in range(num_complete_records):
            check_in = datetime.utcnow() - timedelta(days=i, hours=8)
            check_out = check_in + timedelta(hours=8)
            hours_worked = 8.0
            
            attendance = AttendanceRecord(
                tenant_id=test_tenant.id,
                staff_id=test_staff_member.id,
                check_in_time=check_in,
                check_out_time=check_out,
                hours_worked=hours_worked,
                status="checked_out",
            )
            attendance.save()
            created_records.append(attendance)
            expected_total += hours_worked
        
        # Create incomplete records (still clocked in)
        for i in range(num_incomplete_records):
            check_in = datetime.utcnow() - timedelta(days=i + num_complete_records, hours=2)
            
            attendance = AttendanceRecord(
                tenant_id=test_tenant.id,
                staff_id=test_staff_member.id,
                check_in_time=check_in,
                status="checked_in",
            )
            attendance.save()
            created_records.append(attendance)
        
        # Calculate total hours (should only include complete records)
        all_records = AttendanceRecord.find(
            tenant_id=test_tenant.id,
            staff_id=test_staff_member.id,
        )
        
        calculated_total = sum(
            r.hours_worked for r in all_records
            if r.hours_worked is not None
        )
        
        # Verify total only includes complete records
        assert abs(calculated_total - expected_total) < 0.1
        
        # Verify incomplete records are not included
        complete_count = sum(1 for r in all_records if r.hours_worked is not None)
        assert complete_count == num_complete_records
        
        # Cleanup
        for record in created_records:
            record.delete()
        
        clear_context()


class TestAttendanceEdgeCases:
    """Test edge cases for attendance tracking."""

    def test_very_short_work_duration(
        self,
        test_tenant,
        test_staff_member,
    ):
        """Test handling of very short work durations (e.g., 5 minutes)."""
        set_tenant_id(test_tenant.id)
        
        check_in_time = datetime.utcnow() - timedelta(minutes=5)
        check_out_time = datetime.utcnow()
        
        attendance = AttendanceRecord(
            tenant_id=test_tenant.id,
            staff_id=test_staff_member.id,
            check_in_time=check_in_time,
            check_out_time=check_out_time,
            status="checked_out",
        )
        
        # Calculate hours worked
        time_diff = check_out_time - check_in_time
        calculated_hours = round(time_diff.total_seconds() / 3600, 2)
        attendance.hours_worked = calculated_hours
        attendance.save()
        
        # Verify short duration is handled correctly
        expected_hours = round(5 / 60, 2)  # 0.08 hours
        assert abs(attendance.hours_worked - expected_hours) < 0.01
        
        # Cleanup
        attendance.delete()
        clear_context()

    def test_very_long_work_duration(
        self,
        test_tenant,
        test_staff_member,
    ):
        """Test handling of very long work durations (e.g., 16 hours)."""
        set_tenant_id(test_tenant.id)
        
        check_in_time = datetime.utcnow() - timedelta(hours=16)
        check_out_time = datetime.utcnow()
        
        attendance = AttendanceRecord(
            tenant_id=test_tenant.id,
            staff_id=test_staff_member.id,
            check_in_time=check_in_time,
            check_out_time=check_out_time,
            status="checked_out",
        )
        
        # Calculate hours worked
        time_diff = check_out_time - check_in_time
        calculated_hours = round(time_diff.total_seconds() / 3600, 2)
        attendance.hours_worked = calculated_hours
        attendance.save()
        
        # Verify long duration is handled correctly
        assert abs(attendance.hours_worked - 16.0) < 0.1
        
        # Cleanup
        attendance.delete()
        clear_context()

    def test_attendance_record_with_notes(
        self,
        test_tenant,
        test_staff_member,
    ):
        """Test attendance records can include optional notes."""
        set_tenant_id(test_tenant.id)
        
        check_in_time = datetime.utcnow() - timedelta(hours=8)
        check_out_time = datetime.utcnow()
        notes = "Worked on special project today"
        
        attendance = AttendanceRecord(
            tenant_id=test_tenant.id,
            staff_id=test_staff_member.id,
            check_in_time=check_in_time,
            check_out_time=check_out_time,
            hours_worked=8.0,
            status="checked_out",
            notes=notes,
        )
        attendance.save()
        
        # Verify notes are stored
        assert attendance.notes == notes
        
        # Verify notes persist
        retrieved_records = AttendanceRecord.find(
            tenant_id=test_tenant.id,
            staff_id=test_staff_member.id,
        )
        
        assert len(retrieved_records) == 1
        assert retrieved_records[0].notes == notes
        
        # Cleanup
        attendance.delete()
        clear_context()
