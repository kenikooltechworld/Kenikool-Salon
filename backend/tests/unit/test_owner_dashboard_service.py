"""Unit tests for owner dashboard service."""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from bson import ObjectId
from app.models.payment import Payment
from app.models.appointment import Appointment
from app.models.inventory import Inventory
from app.models.staff import Staff
from app.models.tenant import Tenant
from app.models.user import User
from app.models.service import Service
from app.services.owner_dashboard_service import OwnerDashboardService
from app.cache import cache


@pytest.fixture
def setup_test_data(clear_db):
    """Set up test data for dashboard service tests."""
    import time
    
    # Use timestamp to ensure uniqueness
    timestamp = str(int(time.time() * 1000000))
    
    # Create tenant
    tenant = Tenant(
        name=f"Test Salon {timestamp}",
        subdomain=f"test-salon-{timestamp}",
        subscription_tier="professional",
        status="active",
    )
    tenant.save()

    # Create user for staff
    user = User(
        tenant_id=tenant.id,
        email=f"staff-{timestamp}@test.com",
        password_hash="hashed_password",
        first_name="John",
        last_name="Doe",
    )
    user.save()

    # Create staff member
    staff = Staff(
        tenant_id=tenant.id,
        user_id=user.id,
        payment_type="hourly",
        payment_rate=Decimal("5000"),
        status="active",
        rating=Decimal("4.5"),
        review_count=10,
    )
    staff.save()

    # Create service
    service = Service(
        tenant_id=tenant.id,
        name="Haircut",
        description="Professional haircut",
        duration_minutes=30,
        price=Decimal("5000"),
        category="Hair",
    )
    service.save()

    # Create appointments
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Today's appointment
    appt_today = Appointment(
        tenant_id=tenant.id,
        staff_id=staff.id,
        service_id=service.id,
        start_time=today_start + timedelta(hours=10),
        end_time=today_start + timedelta(hours=10, minutes=30),
        status="confirmed",
        idempotency_key=f"appt-today-{timestamp}",
    )
    appt_today.save()

    # This week's appointment
    appt_week = Appointment(
        tenant_id=tenant.id,
        staff_id=staff.id,
        service_id=service.id,
        start_time=today_start + timedelta(days=2, hours=14),
        end_time=today_start + timedelta(days=2, hours=14, minutes=30),
        status="confirmed",
        idempotency_key=f"appt-week-{timestamp}",
    )
    appt_week.save()

    # This month's appointment
    appt_month = Appointment(
        tenant_id=tenant.id,
        staff_id=staff.id,
        service_id=service.id,
        start_time=today_start + timedelta(days=15, hours=9),
        end_time=today_start + timedelta(days=15, hours=9, minutes=30),
        status="confirmed",
        idempotency_key=f"appt-month-{timestamp}",
    )
    appt_month.save()

    # Create payments
    payment_current = Payment(
        tenant_id=tenant.id,
        amount=Decimal("5000"),
        status="success",
        reference=f"ref-current-{timestamp}",
        gateway="paystack",
        created_at=today_start,
        idempotency_key=f"pay-current-{timestamp}",
    )
    payment_current.save()

    payment_pending = Payment(
        tenant_id=tenant.id,
        amount=Decimal("3000"),
        status="pending",
        reference=f"ref-pending-{timestamp}",
        gateway="paystack",
        created_at=today_start - timedelta(days=5),
        idempotency_key=f"pay-pending-{timestamp}",
    )
    payment_pending.save()

    # Create inventory
    inventory = Inventory(
        tenant_id=tenant.id,
        name="Hair Dye",
        sku="HD-001",
        quantity=5,
        reorder_level=10,
        unit_cost=500.0,
        unit="bottle",
        category="Supplies",
        is_active=True,
    )
    inventory.save()

    # Clear cache before tests
    cache.delete(f"dashboard_metrics:{tenant.id}")

    return {
        "tenant": tenant,
        "staff": staff,
        "service": service,
        "appointments": [appt_today, appt_week, appt_month],
        "payments": [payment_current, payment_pending],
        "inventory": inventory,
    }


class TestOwnerDashboardService:
    """Test owner dashboard service."""

    def test_get_all_metrics_returns_all_metrics(self, setup_test_data):
        """Test that all metrics are returned."""
        tenant = setup_test_data["tenant"]
        service = OwnerDashboardService()

        metrics = service.get_all_metrics(tenant.id, use_cache=False)

        assert "revenue" in metrics
        assert "appointments" in metrics
        assert "satisfaction" in metrics
        assert "staffUtilization" in metrics
        assert "pendingPayments" in metrics
        assert "inventoryStatus" in metrics

    def test_revenue_metrics_calculated_correctly(self, setup_test_data):
        """Test that revenue metrics are calculated correctly."""
        tenant = setup_test_data["tenant"]
        service = OwnerDashboardService()

        metrics = service.get_all_metrics(tenant.id, use_cache=False)
        revenue = metrics["revenue"]

        assert revenue["current"] == 5000.0
        assert revenue["previous"] == 0.0
        assert revenue["trend"] == "up"
        assert revenue["trendPercentage"] == 100.0

    def test_appointment_metrics_calculated_correctly(self, setup_test_data):
        """Test that appointment metrics are calculated correctly."""
        tenant = setup_test_data["tenant"]
        service = OwnerDashboardService()

        metrics = service.get_all_metrics(tenant.id, use_cache=False)
        appointments = metrics["appointments"]

        assert appointments["today"] == 1
        assert appointments["thisWeek"] >= 1
        assert appointments["thisMonth"] >= 1
        assert appointments["trend"] in ["up", "down", "neutral"]

    def test_satisfaction_metrics_calculated_correctly(self, setup_test_data):
        """Test that satisfaction metrics are calculated correctly."""
        tenant = setup_test_data["tenant"]
        service = OwnerDashboardService()

        metrics = service.get_all_metrics(tenant.id, use_cache=False)
        satisfaction = metrics["satisfaction"]

        assert satisfaction["score"] == 4.5
        assert satisfaction["count"] == 1
        assert satisfaction["trend"] == "neutral"

    def test_utilization_metrics_calculated_correctly(self, setup_test_data):
        """Test that utilization metrics are calculated correctly."""
        tenant = setup_test_data["tenant"]
        service = OwnerDashboardService()

        metrics = service.get_all_metrics(tenant.id, use_cache=False)
        utilization = metrics["staffUtilization"]

        assert "percentage" in utilization
        assert "bookedHours" in utilization
        assert "availableHours" in utilization
        assert utilization["percentage"] >= 0
        assert utilization["bookedHours"] >= 0
        assert utilization["availableHours"] >= 0

    def test_pending_payments_calculated_correctly(self, setup_test_data):
        """Test that pending payments are calculated correctly."""
        tenant = setup_test_data["tenant"]
        service = OwnerDashboardService()

        metrics = service.get_all_metrics(tenant.id, use_cache=False)
        pending = metrics["pendingPayments"]

        assert pending["count"] == 1
        assert pending["totalAmount"] == 3000.0
        assert pending["oldestDate"] is not None

    def test_inventory_status_calculated_correctly(self, setup_test_data):
        """Test that inventory status is calculated correctly."""
        tenant = setup_test_data["tenant"]
        service = OwnerDashboardService()

        metrics = service.get_all_metrics(tenant.id, use_cache=False)
        inventory = metrics["inventoryStatus"]

        assert "lowStockCount" in inventory
        assert "expiringCount" in inventory
        assert inventory["lowStockCount"] >= 0
        assert inventory["expiringCount"] >= 0

    def test_metrics_are_cached(self, setup_test_data):
        """Test that metrics are cached for 30 seconds."""
        tenant = setup_test_data["tenant"]
        service = OwnerDashboardService()

        # First call should calculate and cache
        metrics1 = service.get_all_metrics(tenant.id, use_cache=True)

        # Second call should return cached value
        metrics2 = service.get_all_metrics(tenant.id, use_cache=True)

        assert metrics1 == metrics2

    def test_cache_can_be_bypassed(self, setup_test_data):
        """Test that cache can be bypassed with use_cache=False."""
        tenant = setup_test_data["tenant"]
        service = OwnerDashboardService()

        # First call with cache
        metrics1 = service.get_all_metrics(tenant.id, use_cache=True)

        # Second call without cache
        metrics2 = service.get_all_metrics(tenant.id, use_cache=False)

        # Both should have same values (since no data changed)
        assert metrics1 == metrics2

    def test_tenant_isolation(self, setup_test_data, clear_db):
        """Test that only current tenant's data is returned."""
        tenant1 = setup_test_data["tenant"]

        # Create another tenant
        tenant2 = Tenant(
            name="Another Salon",
            subdomain="another-salon",
            subscription_tier="professional",
            status="active",
        )
        tenant2.save()

        # Create payment for tenant2
        payment = Payment(
            tenant_id=tenant2.id,
            amount=Decimal("10000"),
            status="success",
            reference="ref_tenant2_1",
            gateway="paystack",
        )
        payment.save()

        service = OwnerDashboardService()

        # Get metrics for tenant1
        metrics1 = service.get_all_metrics(tenant1.id, use_cache=False)

        # Get metrics for tenant2
        metrics2 = service.get_all_metrics(tenant2.id, use_cache=False)

        # Tenant1 should have 5000 revenue, tenant2 should have 10000
        assert metrics1["revenue"]["current"] == 5000.0
        assert metrics2["revenue"]["current"] == 10000.0

    def test_invalidate_cache(self, setup_test_data):
        """Test that cache can be invalidated."""
        tenant = setup_test_data["tenant"]
        service = OwnerDashboardService()

        # Cache metrics
        metrics1 = service.get_all_metrics(tenant.id, use_cache=True)

        # Invalidate cache
        service.invalidate_cache(tenant.id)

        # Verify cache is cleared
        cache_key = f"dashboard_metrics:{tenant.id}"
        assert cache.get(cache_key) is None

    def test_handles_empty_data_gracefully(self, clear_db):
        """Test that service handles empty data gracefully."""
        # Create tenant with no data
        tenant = Tenant(
            name="Empty Salon",
            subdomain="empty-salon",
            subscription_tier="professional",
            status="active",
        )
        tenant.save()

        service = OwnerDashboardService()
        metrics = service.get_all_metrics(tenant.id, use_cache=False)

        # Should return valid structure with zero values
        assert metrics["revenue"]["current"] == 0.0
        assert metrics["appointments"]["today"] == 0
        assert metrics["satisfaction"]["score"] == 0.0
        assert metrics["pendingPayments"]["count"] == 0
        assert metrics["inventoryStatus"]["lowStockCount"] == 0

    def test_handles_errors_gracefully(self, setup_test_data):
        """Test that service handles errors gracefully."""
        service = OwnerDashboardService()

        # Call with invalid tenant ID
        metrics = service.get_all_metrics(ObjectId(), use_cache=False)

        # Should return valid structure with zero values
        assert metrics["revenue"]["current"] == 0.0
        assert metrics["appointments"]["today"] == 0


class TestUpcomingAppointments:
    """Test upcoming appointments functionality."""

    def test_get_upcoming_appointments_returns_appointments(self, setup_test_data):
        """Test that upcoming appointments are returned."""
        tenant = setup_test_data["tenant"]
        service = OwnerDashboardService()

        result = service.get_upcoming_appointments(tenant.id, limit=10, offset=0)

        assert "appointments" in result
        assert "total" in result
        assert "limit" in result
        assert "offset" in result
        assert result["limit"] == 10
        assert result["offset"] == 0
        assert result["total"] >= 1

    def test_upcoming_appointments_sorted_chronologically(self, setup_test_data):
        """Test that appointments are sorted chronologically."""
        tenant = setup_test_data["tenant"]
        service = OwnerDashboardService()

        result = service.get_upcoming_appointments(tenant.id, limit=10, offset=0)
        appointments = result["appointments"]

        # Verify appointments are sorted by start time
        for i in range(len(appointments) - 1):
            assert appointments[i]["startTime"] <= appointments[i + 1]["startTime"]

    def test_upcoming_appointments_include_required_fields(self, setup_test_data):
        """Test that appointments include all required fields."""
        tenant = setup_test_data["tenant"]
        service = OwnerDashboardService()

        result = service.get_upcoming_appointments(tenant.id, limit=10, offset=0)
        appointments = result["appointments"]

        assert len(appointments) > 0
        appt = appointments[0]

        assert "id" in appt
        assert "customerName" in appt
        assert "serviceName" in appt
        assert "staffName" in appt
        assert "startTime" in appt
        assert "endTime" in appt
        assert "status" in appt
        assert "isPublicBooking" in appt

    def test_upcoming_appointments_excludes_past_appointments(self, setup_test_data):
        """Test that past appointments are excluded."""
        tenant = setup_test_data["tenant"]
        service = OwnerDashboardService()

        # Create a past appointment
        now = datetime.utcnow()
        past_appt = Appointment(
            tenant_id=tenant.id,
            staff_id=setup_test_data["staff"].id,
            service_id=setup_test_data["service"].id,
            start_time=now - timedelta(hours=1),
            end_time=now - timedelta(minutes=30),
            status="completed",
            idempotency_key=f"past-appt-{ObjectId()}",
        )
        past_appt.save()

        result = service.get_upcoming_appointments(tenant.id, limit=10, offset=0)
        appointments = result["appointments"]

        # Verify no past appointments are included
        for appt in appointments:
            assert appt["startTime"] >= now.isoformat()

    def test_upcoming_appointments_excludes_cancelled_appointments(self, setup_test_data):
        """Test that cancelled appointments are excluded."""
        tenant = setup_test_data["tenant"]
        service = OwnerDashboardService()

        # Create a cancelled appointment
        now = datetime.utcnow()
        cancelled_appt = Appointment(
            tenant_id=tenant.id,
            staff_id=setup_test_data["staff"].id,
            service_id=setup_test_data["service"].id,
            start_time=now + timedelta(hours=5),
            end_time=now + timedelta(hours=5, minutes=30),
            status="cancelled",
            idempotency_key=f"cancelled-appt-{ObjectId()}",
        )
        cancelled_appt.save()

        result = service.get_upcoming_appointments(tenant.id, limit=10, offset=0)
        appointments = result["appointments"]

        # Verify no cancelled appointments are included
        for appt in appointments:
            assert appt["status"] != "cancelled"

    def test_upcoming_appointments_pagination(self, setup_test_data):
        """Test that pagination works correctly."""
        tenant = setup_test_data["tenant"]
        service = OwnerDashboardService()

        # Get first page
        result1 = service.get_upcoming_appointments(tenant.id, limit=2, offset=0)
        appointments1 = result1["appointments"]

        # Get second page
        result2 = service.get_upcoming_appointments(tenant.id, limit=2, offset=2)
        appointments2 = result2["appointments"]

        # Verify pagination
        assert len(appointments1) <= 2
        assert len(appointments2) <= 2
        assert result1["total"] == result2["total"]

    def test_upcoming_appointments_includes_internal_bookings(self, setup_test_data):
        """Test that internal appointments are included."""
        tenant = setup_test_data["tenant"]
        service = OwnerDashboardService()

        result = service.get_upcoming_appointments(tenant.id, limit=10, offset=0)
        appointments = result["appointments"]

        # Verify at least one internal booking
        internal_bookings = [a for a in appointments if not a["isPublicBooking"]]
        assert len(internal_bookings) > 0

    def test_upcoming_appointments_includes_public_bookings(self, setup_test_data):
        """Test that public bookings are included."""
        from app.models.public_booking import PublicBooking
        from datetime import date

        tenant = setup_test_data["tenant"]
        service = OwnerDashboardService()

        # Create a public booking
        now = datetime.utcnow()
        public_booking = PublicBooking(
            tenant_id=tenant.id,
            service_id=setup_test_data["service"].id,
            staff_id=setup_test_data["staff"].id,
            customer_name="Jane Smith",
            customer_email="jane@example.com",
            customer_phone="1234567890",
            booking_date=now.date() + timedelta(days=1),
            booking_time="14:00",
            duration_minutes=30,
            status="confirmed",
            idempotency_key=f"public-booking-{ObjectId()}",
        )
        public_booking.save()

        result = service.get_upcoming_appointments(tenant.id, limit=10, offset=0)
        appointments = result["appointments"]

        # Verify public booking is included
        public_bookings = [a for a in appointments if a["isPublicBooking"]]
        assert len(public_bookings) > 0

    def test_upcoming_appointments_tenant_isolation(self, setup_test_data, clear_db):
        """Test that only current tenant's appointments are returned."""
        tenant1 = setup_test_data["tenant"]

        # Create another tenant
        tenant2 = Tenant(
            name="Another Salon",
            subdomain="another-salon",
            subscription_tier="professional",
            status="active",
        )
        tenant2.save()

        # Create user and staff for tenant2
        user2 = User(
            tenant_id=tenant2.id,
            email="staff2@test.com",
            password_hash="hashed_password",
            first_name="Jane",
            last_name="Smith",
        )
        user2.save()

        staff2 = Staff(
            tenant_id=tenant2.id,
            user_id=user2.id,
            payment_type="hourly",
            payment_rate=Decimal("5000"),
            status="active",
        )
        staff2.save()

        # Create service for tenant2
        service2 = Service(
            tenant_id=tenant2.id,
            name="Massage",
            description="Professional massage",
            duration_minutes=60,
            price=Decimal("10000"),
            category="Wellness",
        )
        service2.save()

        # Create appointment for tenant2
        now = datetime.utcnow()
        appt2 = Appointment(
            tenant_id=tenant2.id,
            staff_id=staff2.id,
            service_id=service2.id,
            start_time=now + timedelta(hours=2),
            end_time=now + timedelta(hours=3),
            status="confirmed",
            idempotency_key=f"appt-tenant2-{ObjectId()}",
        )
        appt2.save()

        dashboard_service = OwnerDashboardService()

        # Get appointments for tenant1
        result1 = dashboard_service.get_upcoming_appointments(tenant1.id, limit=10, offset=0)
        appointments1 = result1["appointments"]

        # Get appointments for tenant2
        result2 = dashboard_service.get_upcoming_appointments(tenant2.id, limit=10, offset=0)
        appointments2 = result2["appointments"]

        # Verify tenant isolation
        for appt in appointments1:
            assert appt["serviceName"] != "Massage"

        for appt in appointments2:
            assert appt["serviceName"] == "Massage"

    def test_upcoming_appointments_handles_missing_customer(self, setup_test_data):
        """Test that appointments with missing customer are handled gracefully."""
        tenant = setup_test_data["tenant"]
        service = OwnerDashboardService()

        # Create appointment without customer
        now = datetime.utcnow()
        appt = Appointment(
            tenant_id=tenant.id,
            staff_id=setup_test_data["staff"].id,
            service_id=setup_test_data["service"].id,
            start_time=now + timedelta(hours=3),
            end_time=now + timedelta(hours=3, minutes=30),
            status="confirmed",
            idempotency_key=f"no-customer-{ObjectId()}",
        )
        appt.save()

        result = service.get_upcoming_appointments(tenant.id, limit=10, offset=0)
        appointments = result["appointments"]

        # Verify appointment is included with default customer name
        assert len(appointments) > 0
        for appt_data in appointments:
            assert appt_data["customerName"] is not None

    def test_upcoming_appointments_handles_missing_service(self, setup_test_data):
        """Test that appointments with missing service are handled gracefully."""
        tenant = setup_test_data["tenant"]
        service = OwnerDashboardService()

        # Create appointment with non-existent service
        now = datetime.utcnow()
        appt = Appointment(
            tenant_id=tenant.id,
            staff_id=setup_test_data["staff"].id,
            service_id=ObjectId(),
            start_time=now + timedelta(hours=4),
            end_time=now + timedelta(hours=4, minutes=30),
            status="confirmed",
            idempotency_key=f"no-service-{ObjectId()}",
        )
        appt.save()

        result = service.get_upcoming_appointments(tenant.id, limit=10, offset=0)
        appointments = result["appointments"]

        # Verify appointment is included with default service name
        assert len(appointments) > 0
        for appt_data in appointments:
            assert appt_data["serviceName"] is not None

    def test_upcoming_appointments_handles_missing_staff(self, setup_test_data):
        """Test that appointments with missing staff are handled gracefully."""
        tenant = setup_test_data["tenant"]
        service = OwnerDashboardService()

        # Create appointment with non-existent staff
        now = datetime.utcnow()
        appt = Appointment(
            tenant_id=tenant.id,
            staff_id=ObjectId(),
            service_id=setup_test_data["service"].id,
            start_time=now + timedelta(hours=5),
            end_time=now + timedelta(hours=5, minutes=30),
            status="confirmed",
            idempotency_key=f"no-staff-{ObjectId()}",
        )
        appt.save()

        result = service.get_upcoming_appointments(tenant.id, limit=10, offset=0)
        appointments = result["appointments"]

        # Verify appointment is included with default staff name
        assert len(appointments) > 0
        for appt_data in appointments:
            assert appt_data["staffName"] is not None

    def test_upcoming_appointments_response_time(self, setup_test_data):
        """Test that response time is under 500ms."""
        import time

        tenant = setup_test_data["tenant"]
        service = OwnerDashboardService()

        start_time = time.time()
        result = service.get_upcoming_appointments(tenant.id, limit=10, offset=0)
        end_time = time.time()

        response_time_ms = (end_time - start_time) * 1000

        # Response should be under 500ms
        assert response_time_ms < 500, f"Response time {response_time_ms}ms exceeds 500ms limit"

    def test_upcoming_appointments_limit_parameter(self, setup_test_data):
        """Test that limit parameter works correctly."""
        tenant = setup_test_data["tenant"]
        service = OwnerDashboardService()

        # Test with limit=5
        result = service.get_upcoming_appointments(tenant.id, limit=5, offset=0)
        appointments = result["appointments"]

        assert len(appointments) <= 5
        assert result["limit"] == 5

    def test_upcoming_appointments_offset_parameter(self, setup_test_data):
        """Test that offset parameter works correctly."""
        tenant = setup_test_data["tenant"]
        service = OwnerDashboardService()

        # Get all appointments
        result_all = service.get_upcoming_appointments(tenant.id, limit=100, offset=0)
        all_appointments = result_all["appointments"]

        if len(all_appointments) > 2:
            # Get with offset
            result_offset = service.get_upcoming_appointments(tenant.id, limit=100, offset=2)
            offset_appointments = result_offset["appointments"]

            # Verify offset works
            assert len(offset_appointments) == len(all_appointments) - 2
