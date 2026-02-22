"""Integration tests for service commission API."""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi.testclient import TestClient
from app.main import app
from app.models.tenant import Tenant
from app.models.user import User
from app.models.staff import Staff
from app.models.service import Service
from app.models.appointment import Appointment
from app.models.service_commission import ServiceCommission


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def tenant():
    """Create test tenant."""
    tenant = Tenant(name="Test Tenant", subdomain="test")
    tenant.save()
    return tenant


@pytest.fixture
def user(tenant):
    """Create test user."""
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
    """Create test staff."""
    staff = Staff(
        tenant_id=tenant.id,
        user_id=user.id,
        payment_type="commission",
        payment_rate=Decimal("10"),
    )
    staff.save()
    return staff


@pytest.fixture
def service(tenant):
    """Create test service."""
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
    """Create test customer."""
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
    """Create test appointment."""
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


class TestServiceCommissionAPI:
    """Test service commission API endpoints."""

    def test_calculate_commission(self, client, tenant, appointment):
        """Test commission calculation endpoint."""
        # Note: In real tests, you'd need proper authentication
        # This is a simplified test structure
        response = client.post(
            f"/api/service-commissions/calculate/{appointment.id}",
            headers={"X-Tenant-ID": str(tenant.id)},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["commission_amount"] == 100  # 1000 * 10 / 100
        assert data["status"] == "pending"

    def test_get_staff_commissions(self, client, tenant, staff, appointment):
        """Test getting staff commissions."""
        # Create commission
        commission = ServiceCommission(
            tenant_id=tenant.id,
            staff_id=staff.id,
            appointment_id=appointment.id,
            service_id=appointment.service_id,
            service_price=Decimal("1000"),
            commission_percentage=Decimal("10"),
            commission_amount=Decimal("100"),
            status="pending",
        )
        commission.save()

        response = client.get(
            f"/api/service-commissions/staff/{staff.id}",
            headers={"X-Tenant-ID": str(tenant.id)},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["commissions"]) == 1
        assert data["commissions"][0]["commission_amount"] == 100

    def test_get_commission_summary(self, client, tenant, staff, appointment):
        """Test getting commission summary."""
        # Create commission
        commission = ServiceCommission(
            tenant_id=tenant.id,
            staff_id=staff.id,
            appointment_id=appointment.id,
            service_id=appointment.service_id,
            service_price=Decimal("1000"),
            commission_percentage=Decimal("10"),
            commission_amount=Decimal("100"),
            status="pending",
        )
        commission.save()

        response = client.get(
            f"/api/service-commissions/staff/{staff.id}/summary",
            headers={"X-Tenant-ID": str(tenant.id)},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["summary"]["total_earned"] == 100
        assert data["summary"]["total_pending"] == 100
        assert data["summary"]["total_paid"] == 0
        assert data["summary"]["total_services"] == 1

    def test_get_pending_commissions(self, client, tenant, staff, appointment):
        """Test getting pending commissions."""
        # Create commission
        commission = ServiceCommission(
            tenant_id=tenant.id,
            staff_id=staff.id,
            appointment_id=appointment.id,
            service_id=appointment.service_id,
            service_price=Decimal("1000"),
            commission_percentage=Decimal("10"),
            commission_amount=Decimal("100"),
            status="pending",
        )
        commission.save()

        response = client.get(
            f"/api/service-commissions/staff/{staff.id}/pending",
            headers={"X-Tenant-ID": str(tenant.id)},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["commissions"]) == 1
        assert data["total_pending"] == 100

    def test_mark_commission_as_paid(self, client, tenant, staff, appointment):
        """Test marking commission as paid."""
        # Create commission
        commission = ServiceCommission(
            tenant_id=tenant.id,
            staff_id=staff.id,
            appointment_id=appointment.id,
            service_id=appointment.service_id,
            service_price=Decimal("1000"),
            commission_percentage=Decimal("10"),
            commission_amount=Decimal("100"),
            status="pending",
        )
        commission.save()

        response = client.patch(
            f"/api/service-commissions/{commission.id}/mark-paid",
            headers={"X-Tenant-ID": str(tenant.id)},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "paid"
        assert data["paid_date"] is not None

    def test_mark_commissions_as_paid_batch(self, client, tenant, staff, appointment):
        """Test marking multiple commissions as paid."""
        # Create multiple commissions
        commission_ids = []
        for i in range(3):
            commission = ServiceCommission(
                tenant_id=tenant.id,
                staff_id=staff.id,
                appointment_id=appointment.id,
                service_id=appointment.service_id,
                service_price=Decimal("1000"),
                commission_percentage=Decimal("10"),
                commission_amount=Decimal("100"),
                status="pending",
            )
            commission.save()
            commission_ids.append(str(commission.id))

        response = client.post(
            f"/api/service-commissions/staff/{staff.id}/mark-paid-batch",
            json=commission_ids,
            headers={"X-Tenant-ID": str(tenant.id)},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["updated_count"] == 3

    def test_filter_by_status(self, client, tenant, staff, appointment):
        """Test filtering commissions by status."""
        # Create pending commission
        pending = ServiceCommission(
            tenant_id=tenant.id,
            staff_id=staff.id,
            appointment_id=appointment.id,
            service_id=appointment.service_id,
            service_price=Decimal("1000"),
            commission_percentage=Decimal("10"),
            commission_amount=Decimal("100"),
            status="pending",
        )
        pending.save()

        # Create paid commission
        paid = ServiceCommission(
            tenant_id=tenant.id,
            staff_id=staff.id,
            appointment_id=appointment.id,
            service_id=appointment.service_id,
            service_price=Decimal("1000"),
            commission_percentage=Decimal("10"),
            commission_amount=Decimal("100"),
            status="paid",
            paid_date=datetime.utcnow(),
        )
        paid.save()

        # Get pending
        response = client.get(
            f"/api/service-commissions/staff/{staff.id}?status=pending",
            headers={"X-Tenant-ID": str(tenant.id)},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1

        # Get paid
        response = client.get(
            f"/api/service-commissions/staff/{staff.id}?status=paid",
            headers={"X-Tenant-ID": str(tenant.id)},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1

    def test_filter_by_date_range(self, client, tenant, staff, appointment):
        """Test filtering commissions by date range."""
        # Create commission
        commission = ServiceCommission(
            tenant_id=tenant.id,
            staff_id=staff.id,
            appointment_id=appointment.id,
            service_id=appointment.service_id,
            service_price=Decimal("1000"),
            commission_percentage=Decimal("10"),
            commission_amount=Decimal("100"),
            status="pending",
        )
        commission.save()

        now = datetime.utcnow()
        start_date = (now - timedelta(days=1)).isoformat()
        end_date = (now + timedelta(days=1)).isoformat()

        response = client.get(
            f"/api/service-commissions/staff/{staff.id}?start_date={start_date}&end_date={end_date}",
            headers={"X-Tenant-ID": str(tenant.id)},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1

        # Test with date range that excludes commission
        start_date = (now + timedelta(days=1)).isoformat()
        end_date = (now + timedelta(days=2)).isoformat()

        response = client.get(
            f"/api/service-commissions/staff/{staff.id}?start_date={start_date}&end_date={end_date}",
            headers={"X-Tenant-ID": str(tenant.id)},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
