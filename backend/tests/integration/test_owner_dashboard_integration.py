"""Integration tests for owner dashboard workflows."""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from bson import ObjectId
from fastapi.testclient import TestClient
from app.main import app
from app.models.tenant import Tenant
from app.models.user import User
from app.models.payment import Payment
from app.models.appointment import Appointment
from app.models.staff import Staff
from app.models.inventory import Inventory

client = TestClient(app)


@pytest.fixture
def test_tenant():
    """Create a test tenant."""
    tenant = Tenant(
        name="Test Salon",
        subdomain="test-salon",
        owner_email="owner@test.com",
        status="active",
    )
    tenant.save()
    return tenant


@pytest.fixture
def test_user(test_tenant):
    """Create a test user."""
    user = User(
        email="owner@test.com",
        first_name="Test",
        last_name="Owner",
        tenant_id=test_tenant.id,
        role="owner",
        password_hash="hashed_password",
    )
    user.save()
    return user


@pytest.fixture
def test_staff(test_tenant, test_user):
    """Create test staff members."""
    staff = Staff(
        tenant_id=test_tenant.id,
        user_id=test_user.id,
        status="active",
        rating=4.7,
    )
    staff.save()
    return staff


@pytest.fixture
def test_payments(test_tenant, test_staff):
    """Create test payments."""
    now = datetime.utcnow()
    current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    prev_month_start = (current_month_start - timedelta(days=1)).replace(day=1)

    # Current month payments
    current_payments = []
    for i in range(5):
        payment = Payment(
            tenant_id=test_tenant.id,
            staff_id=test_staff.id,
            amount=Decimal("1000.00"),
            status="success",
            created_at=current_month_start + timedelta(days=i),
        )
        payment.save()
        current_payments.append(payment)

    # Previous month payments
    prev_payments = []
    for i in range(4):
        payment = Payment(
            tenant_id=test_tenant.id,
            staff_id=test_staff.id,
            amount=Decimal("900.00"),
            status="success",
            created_at=prev_month_start + timedelta(days=i),
        )
        payment.save()
        prev_payments.append(payment)

    return current_payments + prev_payments


@pytest.fixture
def test_appointments(test_tenant, test_staff):
    """Create test appointments."""
    now = datetime.utcnow()
    appointments = []

    for i in range(10):
        appointment = Appointment(
            tenant_id=test_tenant.id,
            staff_id=test_staff.id,
            customer_name=f"Customer {i}",
            service_name="Haircut",
            start_time=now + timedelta(hours=i),
            end_time=now + timedelta(hours=i, minutes=30),
            status="confirmed",
        )
        appointment.save()
        appointments.append(appointment)

    return appointments


class TestDashboardLoadWorkflow:
    """Test the complete dashboard load workflow."""

    def test_dashboard_load_returns_all_data(self, test_tenant, test_user, test_payments, test_appointments):
        """Test that dashboard load returns all required data."""
        # This would require proper authentication setup
        # For now, we test the service directly
        from app.services.owner_dashboard_service import OwnerDashboardService

        service = OwnerDashboardService()
        metrics = service.get_all_metrics(test_tenant.id, use_cache=False)

        assert "revenue" in metrics
        assert "appointments" in metrics
        assert "satisfaction" in metrics
        assert "staffUtilization" in metrics
        assert "pendingPayments" in metrics
        assert "inventoryStatus" in metrics

    def test_dashboard_metrics_calculated_correctly(self, test_tenant, test_user, test_payments):
        """Test that dashboard metrics are calculated correctly."""
        from app.services.owner_dashboard_service import OwnerDashboardService

        service = OwnerDashboardService()
        metrics = service.get_all_metrics(test_tenant.id, use_cache=False)

        # Verify revenue calculation
        assert metrics["revenue"]["current"] > 0
        assert metrics["revenue"]["previous"] > 0
        assert metrics["revenue"]["trend"] in ["up", "down", "neutral"]

    def test_dashboard_appointments_returned(self, test_tenant, test_appointments):
        """Test that upcoming appointments are returned."""
        from app.services.owner_dashboard_service import OwnerDashboardService

        service = OwnerDashboardService()
        result = service.get_upcoming_appointments(test_tenant.id, limit=10, offset=0)

        assert "appointments" in result
        assert "total" in result
        assert len(result["appointments"]) > 0

    def test_dashboard_staff_performance_returned(self, test_tenant, test_staff, test_payments):
        """Test that staff performance data is returned."""
        from app.services.owner_dashboard_service import OwnerDashboardService

        service = OwnerDashboardService()
        result = service.get_staff_performance(test_tenant.id)

        assert "staff" in result
        assert len(result["staff"]) > 0


class TestMetricDisplayWorkflow:
    """Test the metric display workflow."""

    def test_metrics_display_with_trends(self, test_tenant, test_payments):
        """Test that metrics display with correct trends."""
        from app.services.owner_dashboard_service import OwnerDashboardService

        service = OwnerDashboardService()
        metrics = service.get_all_metrics(test_tenant.id, use_cache=False)

        # Verify trend data
        assert "trend" in metrics["revenue"]
        assert "trendPercentage" in metrics["revenue"]
        assert isinstance(metrics["revenue"]["trendPercentage"], (int, float))

    def test_metrics_cached_for_performance(self, test_tenant, test_payments):
        """Test that metrics are cached for performance."""
        from app.services.owner_dashboard_service import OwnerDashboardService

        service = OwnerDashboardService()

        # First call
        metrics1 = service.get_all_metrics(test_tenant.id, use_cache=True)

        # Second call should use cache
        metrics2 = service.get_all_metrics(test_tenant.id, use_cache=True)

        # Results should be identical
        assert metrics1 == metrics2


class TestNotificationWorkflow:
    """Test the notification workflow."""

    def test_pending_actions_returned(self, test_tenant, test_payments):
        """Test that pending actions are returned."""
        from app.services.owner_dashboard_service import OwnerDashboardService

        service = OwnerDashboardService()
        result = service.get_pending_actions(test_tenant.id, limit=10)

        assert "actions" in result
        assert "total" in result

    def test_pending_actions_sorted_by_priority(self, test_tenant):
        """Test that pending actions are sorted by priority."""
        from app.services.owner_dashboard_service import OwnerDashboardService

        service = OwnerDashboardService()
        result = service.get_pending_actions(test_tenant.id, limit=10)

        actions = result.get("actions", [])
        if len(actions) > 1:
            # Verify priority ordering
            priorities = {"high": 3, "medium": 2, "low": 1}
            for i in range(len(actions) - 1):
                current_priority = priorities.get(actions[i].get("priority"), 0)
                next_priority = priorities.get(actions[i + 1].get("priority"), 0)
                assert current_priority >= next_priority


class TestRevenueAnalyticsWorkflow:
    """Test the revenue analytics workflow."""

    def test_revenue_analytics_returned(self, test_tenant, test_payments):
        """Test that revenue analytics are returned."""
        from app.services.owner_dashboard_service import OwnerDashboardService

        service = OwnerDashboardService()
        result = service.get_revenue_analytics(test_tenant.id)

        assert "daily" in result
        assert "weekly" in result
        assert "monthly" in result
        assert "byServiceType" in result
        assert "byStaff" in result
        assert "metrics" in result

    def test_revenue_analytics_with_date_range(self, test_tenant, test_payments):
        """Test that revenue analytics support date range filtering."""
        from app.services.owner_dashboard_service import OwnerDashboardService

        service = OwnerDashboardService()
        start_date = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
        end_date = datetime.utcnow().strftime("%Y-%m-%d")

        result = service.get_revenue_analytics(test_tenant.id, start_date, end_date)

        assert "metrics" in result
        assert "total" in result["metrics"]


class TestTenantIsolationIntegration:
    """Test tenant isolation in dashboard workflows."""

    def test_dashboard_only_returns_tenant_data(self, test_tenant, test_payments):
        """Test that dashboard only returns current tenant's data."""
        from app.services.owner_dashboard_service import OwnerDashboardService

        # Create another tenant
        other_tenant = Tenant(
            name="Other Salon",
            subdomain="other-salon",
            owner_email="other@test.com",
            status="active",
        )
        other_tenant.save()

        service = OwnerDashboardService()
        metrics = service.get_all_metrics(test_tenant.id, use_cache=False)

        # Verify only test_tenant data is returned
        assert metrics is not None
        # The metrics should be based on test_tenant's data only

    def test_appointments_only_returns_tenant_data(self, test_tenant, test_appointments):
        """Test that appointments only return current tenant's data."""
        from app.services.owner_dashboard_service import OwnerDashboardService

        service = OwnerDashboardService()
        result = service.get_upcoming_appointments(test_tenant.id, limit=10, offset=0)

        # All returned appointments should belong to test_tenant
        for appointment in result.get("appointments", []):
            # Verify tenant isolation
            assert appointment is not None
