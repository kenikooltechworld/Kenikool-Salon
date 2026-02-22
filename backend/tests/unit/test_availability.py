"""Unit tests for availability management."""

import pytest
from datetime import date, timedelta
from bson import ObjectId
from app.models.availability import Availability


@pytest.fixture
def tenant_id():
    """Create a test tenant ID."""
    return ObjectId()


@pytest.fixture
def staff_id():
    """Create a test staff ID."""
    return ObjectId()


class TestAvailabilityModel:
    """Test Availability model."""

    def test_create_recurring_availability(self, tenant_id, staff_id):
        """Test creating a recurring availability."""
        availability = Availability(
            tenant_id=tenant_id,
            staff_id=staff_id,
            day_of_week=0,
            start_time="09:00:00",
            end_time="17:00:00",
            is_recurring=True,
            effective_from=date.today(),
            is_active=True,
        )
        availability.save()

        assert availability.id is not None
        assert availability.tenant_id == tenant_id
        assert availability.staff_id == staff_id
        assert availability.day_of_week == 0
        assert availability.is_recurring is True

    def test_create_custom_date_range_availability(self, tenant_id, staff_id):
        """Test creating a custom date range availability."""
        start_date = date.today()
        end_date = start_date + timedelta(days=30)

        availability = Availability(
            tenant_id=tenant_id,
            staff_id=staff_id,
            start_time="10:00:00",
            end_time="18:00:00",
            is_recurring=False,
            effective_from=start_date,
            effective_to=end_date,
            is_active=True,
        )
        availability.save()

        assert availability.id is not None
        assert availability.is_recurring is False
        assert availability.effective_from == start_date
        assert availability.effective_to == end_date

    def test_availability_with_breaks(self, tenant_id, staff_id):
        """Test creating availability with break times."""
        breaks = [
            {"start_time": "12:00:00", "end_time": "13:00:00"},
            {"start_time": "15:00:00", "end_time": "15:30:00"},
        ]

        availability = Availability(
            tenant_id=tenant_id,
            staff_id=staff_id,
            day_of_week=1,
            start_time="09:00:00",
            end_time="17:00:00",
            is_recurring=True,
            effective_from=date.today(),
            breaks=breaks,
            is_active=True,
        )
        availability.save()

        assert len(availability.breaks) == 2
        assert availability.breaks[0]["start_time"] == "12:00:00"

    def test_query_by_staff_id(self, tenant_id, staff_id):
        """Test querying availability by staff_id."""
        availability = Availability(
            tenant_id=tenant_id,
            staff_id=staff_id,
            day_of_week=0,
            start_time="09:00:00",
            end_time="17:00:00",
            is_recurring=True,
            effective_from=date.today(),
        )
        availability.save()

        result = Availability.objects(
            tenant_id=tenant_id,
            staff_id=staff_id
        ).first()

        assert result is not None
        assert result.id == availability.id

    def test_query_by_recurring_status(self, tenant_id, staff_id):
        """Test querying availability by recurring status."""
        recurring = Availability(
            tenant_id=tenant_id,
            staff_id=staff_id,
            day_of_week=0,
            start_time="09:00:00",
            end_time="17:00:00",
            is_recurring=True,
            effective_from=date.today(),
        )
        recurring.save()

        custom = Availability(
            tenant_id=tenant_id,
            staff_id=ObjectId(),
            start_time="10:00:00",
            end_time="18:00:00",
            is_recurring=False,
            effective_from=date.today(),
        )
        custom.save()

        recurring_results = Availability.objects(
            tenant_id=tenant_id,
            is_recurring=True
        )
        assert recurring_results.count() >= 1

    def test_tenant_isolation(self, staff_id):
        """Test that queries are isolated by tenant."""
        tenant1 = ObjectId()
        tenant2 = ObjectId()

        avail1 = Availability(
            tenant_id=tenant1,
            staff_id=staff_id,
            day_of_week=0,
            start_time="09:00:00",
            end_time="17:00:00",
            is_recurring=True,
            effective_from=date.today(),
        )
        avail1.save()

        avail2 = Availability(
            tenant_id=tenant2,
            staff_id=staff_id,
            day_of_week=0,
            start_time="09:00:00",
            end_time="17:00:00",
            is_recurring=True,
            effective_from=date.today(),
        )
        avail2.save()

        results = Availability.objects(tenant_id=tenant1)
        assert results.count() >= 1
        for result in results:
            assert result.tenant_id == tenant1

    def test_availability_with_null_effective_to(self, tenant_id, staff_id):
        """Test availability with null effective_to (ongoing)."""
        availability = Availability(
            tenant_id=tenant_id,
            staff_id=staff_id,
            start_time="09:00:00",
            end_time="17:00:00",
            is_recurring=False,
            effective_from=date.today(),
            effective_to=None,
        )
        availability.save()

        assert availability.effective_to is None

    def test_availability_all_days_of_week(self, tenant_id, staff_id):
        """Test creating availability for all days of week."""
        for day in range(7):
            availability = Availability(
                tenant_id=tenant_id,
                staff_id=staff_id,
                day_of_week=day,
                start_time="09:00:00",
                end_time="17:00:00",
                is_recurring=True,
                effective_from=date.today(),
            )
            availability.save()

            assert availability.day_of_week == day
