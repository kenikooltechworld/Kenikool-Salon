"""Property-based tests for service commission system."""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from bson import ObjectId
from hypothesis import given, strategies as st, settings, HealthCheck
from app.models.service_commission import ServiceCommission
from app.models.appointment import Appointment
from app.models.service import Service
from app.models.staff import Staff
from app.models.user import User
from app.models.tenant import Tenant
from app.services.service_commission_service import ServiceCommissionService


@pytest.fixture
def tenant():
    """Create a test tenant."""
    tenant = Tenant(name="Test Tenant", subdomain="test")
    tenant.save()
    return tenant


@pytest.fixture
def user(tenant):
    """Create a test user."""
    user = User(
        tenant_id=tenant.id,
        email="test@example.com",
        password_hash="hashed",
        is_verified=True,
    )
    user.save()
    return user


@pytest.fixture
def staff(tenant, user):
    """Create a test staff member."""
    staff = Staff(
        tenant_id=tenant.id,
        user_id=user.id,
        payment_type="commission",
        payment_rate=Decimal("10"),  # 10% commission
    )
    staff.save()
    return staff


@pytest.fixture
def service(tenant):
    """Create a test service."""
    service = Service(
        tenant_id=tenant.id,
        name="Test Service",
        duration_minutes=60,
        price=Decimal("1000"),
        category="test",
    )
    service.save()
    return service


@pytest.fixture
def customer_user(tenant):
    """Create a test customer user."""
    user = User(
        tenant_id=tenant.id,
        email="customer@example.com",
        password_hash="hashed",
        is_verified=True,
    )
    user.save()
    return user


@pytest.fixture
def appointment(tenant, customer_user, staff, service):
    """Create a test appointment."""
    now = datetime.utcnow()
    appointment = Appointment(
        tenant_id=tenant.id,
        customer_id=customer_user.id,
        staff_id=staff.id,
        service_id=service.id,
        start_time=now,
        end_time=now + timedelta(hours=1),
        price=service.price,
        status="completed",
    )
    appointment.save()
    return appointment


class TestServiceCommissionCalculation:
    """Test service commission calculation."""

    def test_commission_calculation_with_staff_rate(self, tenant, appointment, staff, service):
        """Test commission calculation using staff payment_rate."""
        commission = ServiceCommissionService.calculate_commission_for_appointment(
            tenant.id, appointment.id
        )

        assert commission is not None
        assert commission.staff_id == staff.id
        assert commission.appointment_id == appointment.id
        assert commission.service_id == service.id
        assert commission.commission_percentage == Decimal("10")
        # 1000 * 10 / 100 = 100
        assert commission.commission_amount == Decimal("100")
        assert commission.status == "pending"

    def test_commission_calculation_with_service_override(self, tenant, appointment, staff, service):
        """Test commission calculation with service-level override."""
        # Update service with custom commission percentage
        service.commission_percentage = Decimal("15")
        service.save()

        commission = ServiceCommissionService.calculate_commission_for_appointment(
            tenant.id, appointment.id
        )

        assert commission is not None
        assert commission.commission_percentage == Decimal("15")
        # 1000 * 15 / 100 = 150
        assert commission.commission_amount == Decimal("150")

    def test_commission_not_calculated_for_non_completed(self, tenant, staff, service, customer_user):
        """Test that commission is not calculated for non-completed appointments."""
        now = datetime.utcnow()
        appointment = Appointment(
            tenant_id=tenant.id,
            customer_id=customer_user.id,
            staff_id=staff.id,
            service_id=service.id,
            start_time=now,
            end_time=now + timedelta(hours=1),
            price=service.price,
            status="scheduled",  # Not completed
        )
        appointment.save()

        commission = ServiceCommissionService.calculate_commission_for_appointment(
            tenant.id, appointment.id
        )

        assert commission is None

    def test_commission_idempotency(self, tenant, appointment):
        """Test that calculating commission twice returns the same record."""
        commission1 = ServiceCommissionService.calculate_commission_for_appointment(
            tenant.id, appointment.id
        )
        commission2 = ServiceCommissionService.calculate_commission_for_appointment(
            tenant.id, appointment.id
        )

        assert commission1.id == commission2.id
        assert commission1.commission_amount == commission2.commission_amount

    def test_commission_with_zero_rate(self, tenant, staff, service, customer_user):
        """Test commission calculation with zero rate."""
        staff.payment_rate = Decimal("0")
        staff.save()

        now = datetime.utcnow()
        appointment = Appointment(
            tenant_id=tenant.id,
            customer_id=customer_user.id,
            staff_id=staff.id,
            service_id=service.id,
            start_time=now,
            end_time=now + timedelta(hours=1),
            price=service.price,
            status="completed",
        )
        appointment.save()

        commission = ServiceCommissionService.calculate_commission_for_appointment(
            tenant.id, appointment.id
        )

        assert commission is not None
        assert commission.commission_amount == Decimal("0")

    @given(
        price=st.decimals(min_value=0, max_value=100000, places=2),
        rate=st.decimals(min_value=0, max_value=100, places=2),
    )
    @settings(suppress_health_check=[HealthCheck.filter_too_much])
    def test_commission_calculation_property(self, tenant, staff, service, customer_user, price, rate):
        """Property: commission_amount = price * rate / 100."""
        staff.payment_rate = rate
        staff.save()

        now = datetime.utcnow()
        appointment = Appointment(
            tenant_id=tenant.id,
            customer_id=customer_user.id,
            staff_id=staff.id,
            service_id=service.id,
            start_time=now,
            end_time=now + timedelta(hours=1),
            price=price,
            status="completed",
        )
        appointment.save()

        commission = ServiceCommissionService.calculate_commission_for_appointment(
            tenant.id, appointment.id
        )

        expected = (price * rate) / Decimal("100")
        assert commission.commission_amount == expected


class TestCommissionListing:
    """Test commission listing and filtering."""

    def test_list_staff_commissions(self, tenant, staff, appointment):
        """Test listing staff commissions."""
        ServiceCommissionService.calculate_commission_for_appointment(
            tenant.id, appointment.id
        )

        commissions, total = ServiceCommissionService.list_staff_commissions(
            tenant.id, staff.id
        )

        assert len(commissions) == 1
        assert total == 1

    def test_list_commissions_with_status_filter(self, tenant, staff, appointment):
        """Test listing commissions with status filter."""
        commission = ServiceCommissionService.calculate_commission_for_appointment(
            tenant.id, appointment.id
        )

        # Get pending commissions
        pending, pending_total = ServiceCommissionService.list_staff_commissions(
            tenant.id, staff.id, status="pending"
        )
        assert pending_total == 1

        # Mark as paid
        ServiceCommissionService.mark_commission_as_paid(tenant.id, commission.id)

        # Get paid commissions
        paid, paid_total = ServiceCommissionService.list_staff_commissions(
            tenant.id, staff.id, status="paid"
        )
        assert paid_total == 1

        # Get pending (should be 0)
        pending, pending_total = ServiceCommissionService.list_staff_commissions(
            tenant.id, staff.id, status="pending"
        )
        assert pending_total == 0

    def test_list_commissions_with_date_filter(self, tenant, staff, appointment):
        """Test listing commissions with date filter."""
        ServiceCommissionService.calculate_commission_for_appointment(
            tenant.id, appointment.id
        )

        now = datetime.utcnow()
        start_date = now - timedelta(days=1)
        end_date = now + timedelta(days=1)

        commissions, total = ServiceCommissionService.list_staff_commissions(
            tenant.id, staff.id, start_date=start_date, end_date=end_date
        )

        assert total == 1

        # Test with date range that excludes the commission
        start_date = now + timedelta(days=1)
        end_date = now + timedelta(days=2)

        commissions, total = ServiceCommissionService.list_staff_commissions(
            tenant.id, staff.id, start_date=start_date, end_date=end_date
        )

        assert total == 0

    def test_list_commissions_pagination(self, tenant, staff, service, customer_user):
        """Test commission listing pagination."""
        # Create multiple appointments
        for i in range(25):
            now = datetime.utcnow() + timedelta(hours=i)
            appointment = Appointment(
                tenant_id=tenant.id,
                customer_id=customer_user.id,
                staff_id=staff.id,
                service_id=service.id,
                start_time=now,
                end_time=now + timedelta(hours=1),
                price=service.price,
                status="completed",
            )
            appointment.save()
            ServiceCommissionService.calculate_commission_for_appointment(
                tenant.id, appointment.id
            )

        # Get first page
        commissions, total = ServiceCommissionService.list_staff_commissions(
            tenant.id, staff.id, page=1, page_size=10
        )
        assert len(commissions) == 10
        assert total == 25

        # Get second page
        commissions, total = ServiceCommissionService.list_staff_commissions(
            tenant.id, staff.id, page=2, page_size=10
        )
        assert len(commissions) == 10

        # Get third page
        commissions, total = ServiceCommissionService.list_staff_commissions(
            tenant.id, staff.id, page=3, page_size=10
        )
        assert len(commissions) == 5


class TestCommissionSummary:
    """Test commission summary calculations."""

    def test_commission_summary(self, tenant, staff, appointment):
        """Test commission summary calculation."""
        ServiceCommissionService.calculate_commission_for_appointment(
            tenant.id, appointment.id
        )

        summary = ServiceCommissionService.get_commission_summary(tenant.id, staff.id)

        assert summary["total_earned"] == Decimal("100")
        assert summary["total_pending"] == Decimal("100")
        assert summary["total_paid"] == Decimal("0")
        assert summary["total_services"] == 1
        assert summary["average_commission"] == Decimal("100")

    def test_commission_summary_with_paid(self, tenant, staff, appointment):
        """Test commission summary with paid commissions."""
        commission = ServiceCommissionService.calculate_commission_for_appointment(
            tenant.id, appointment.id
        )

        ServiceCommissionService.mark_commission_as_paid(tenant.id, commission.id)

        summary = ServiceCommissionService.get_commission_summary(tenant.id, staff.id)

        assert summary["total_earned"] == Decimal("100")
        assert summary["total_pending"] == Decimal("0")
        assert summary["total_paid"] == Decimal("100")

    def test_commission_breakdown_by_service(self, tenant, staff, appointment):
        """Test commission breakdown by service."""
        ServiceCommissionService.calculate_commission_for_appointment(
            tenant.id, appointment.id
        )

        breakdown = ServiceCommissionService.get_commission_by_service(
            tenant.id, staff.id
        )

        assert len(breakdown) == 1
        assert breakdown[0]["total_commission"] == Decimal("100")
        assert breakdown[0]["count"] == 1


class TestCommissionPayment:
    """Test commission payment operations."""

    def test_mark_commission_as_paid(self, tenant, staff, appointment):
        """Test marking commission as paid."""
        commission = ServiceCommissionService.calculate_commission_for_appointment(
            tenant.id, appointment.id
        )

        assert commission.status == "pending"
        assert commission.paid_date is None

        updated = ServiceCommissionService.mark_commission_as_paid(
            tenant.id, commission.id
        )

        assert updated.status == "paid"
        assert updated.paid_date is not None

    def test_mark_commissions_as_paid_batch(self, tenant, staff, service, customer_user):
        """Test marking multiple commissions as paid."""
        commission_ids = []
        for i in range(3):
            now = datetime.utcnow() + timedelta(hours=i)
            appointment = Appointment(
                tenant_id=tenant.id,
                customer_id=customer_user.id,
                staff_id=staff.id,
                service_id=service.id,
                start_time=now,
                end_time=now + timedelta(hours=1),
                price=service.price,
                status="completed",
            )
            appointment.save()
            commission = ServiceCommissionService.calculate_commission_for_appointment(
                tenant.id, appointment.id
            )
            commission_ids.append(commission.id)

        count = ServiceCommissionService.mark_commissions_as_paid(
            tenant.id, staff.id, commission_ids
        )

        assert count == 3

        # Verify all are marked as paid
        commissions, _ = ServiceCommissionService.list_staff_commissions(
            tenant.id, staff.id, status="paid"
        )
        assert len(commissions) == 3

    def test_get_pending_commissions(self, tenant, staff, appointment):
        """Test getting pending commissions."""
        commission = ServiceCommissionService.calculate_commission_for_appointment(
            tenant.id, appointment.id
        )

        pending, total_pending = ServiceCommissionService.get_pending_commissions(
            tenant.id, staff.id
        )

        assert len(pending) == 1
        assert total_pending == Decimal("100")

        # Mark as paid
        ServiceCommissionService.mark_commission_as_paid(tenant.id, commission.id)

        pending, total_pending = ServiceCommissionService.get_pending_commissions(
            tenant.id, staff.id
        )

        assert len(pending) == 0
        assert total_pending == Decimal("0")
