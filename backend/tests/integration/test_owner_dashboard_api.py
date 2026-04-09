"""Integration tests for owner dashboard API."""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from bson import ObjectId
from fastapi.testclient import TestClient
from app.main import app
from app.models.tenant import Tenant
from app.models.user import User
from app.models.role import Role
from app.models.staff import Staff
from app.models.service import Service
from app.models.appointment import Appointment
from app.models.payment import Payment
from app.models.inventory import Inventory
from app.cache import cache


client = TestClient(app)


class TestOwnerDashboardAPI:
    """Test owner dashboard API endpoints."""

    def test_get_dashboard_metrics_returns_all_metrics(self, clear_db):
        """Test that metrics endpoint returns all required metrics."""
        import time
        timestamp = str(int(time.time() * 1000000))
        
        # Create tenant
        tenant = Tenant(
            name=f"Test Salon {timestamp}",
            subdomain=f"test-salon-{timestamp}",
            subscription_tier="professional",
            status="active",
            region="us-east-1",
        )
        tenant.save()
        
        # Make request to metrics endpoint
        response = client.get(
            f"/api/owner/dashboard/metrics",
            headers={"X-Tenant-ID": str(tenant.id)},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data

        metrics = data["data"]
        assert "revenue" in metrics
        assert "appointments" in metrics
        assert "satisfaction" in metrics
        assert "staffUtilization" in metrics
        assert "pendingPayments" in metrics
        assert "inventoryStatus" in metrics

    def test_metrics_endpoint_returns_correct_revenue(self, clear_db):
        """Test that revenue metrics are calculated correctly."""
        import time
        timestamp = str(int(time.time() * 1000000))
        
        # Create tenant
        tenant = Tenant(
            name=f"Test Salon {timestamp}",
            subdomain=f"test-salon-{timestamp}",
            subscription_tier="professional",
            status="active",
        )
        tenant.save()
        
        # Create payment
        payment = Payment(
            tenant_id=tenant.id,
            amount=Decimal("5000"),
            status="success",
            reference=f"ref-{timestamp}",
            gateway="paystack",
            idempotency_key=f"pay-{timestamp}",
        )
        payment.save()
        
        # Clear cache
        cache.delete(f"dashboard_metrics:{tenant.id}")
        
        response = client.get(
            f"/api/owner/dashboard/metrics",
            headers={"X-Tenant-ID": str(tenant.id)},
        )

        assert response.status_code == 200
        metrics = response.json()["data"]
        revenue = metrics["revenue"]

        assert revenue["current"] == 5000.0
        assert revenue["previous"] == 0.0
        assert revenue["trend"] in ["up", "down", "neutral"]
        assert "trendPercentage" in revenue

    def test_metrics_endpoint_requires_tenant_context(self):
        """Test that metrics endpoint requires tenant context."""
        response = client.get("/api/owner/dashboard/metrics")
        
        # Should fail without tenant context
        assert response.status_code in [401, 400]

    def test_metrics_endpoint_tenant_isolation(self, clear_db):
        """Test that metrics endpoint only returns current tenant's data."""
        import time
        timestamp = str(int(time.time() * 1000000))
        
        # Create tenant 1
        tenant1 = Tenant(
            name=f"Salon 1 {timestamp}",
            subdomain=f"salon-1-{timestamp}",
            subscription_tier="professional",
            status="active",
        )
        tenant1.save()

        # Create tenant 2
        tenant2 = Tenant(
            name=f"Salon 2 {timestamp}",
            subdomain=f"salon-2-{timestamp}",
            subscription_tier="professional",
            status="active",
        )
        tenant2.save()

        # Create payment for tenant1
        payment1 = Payment(
            tenant_id=tenant1.id,
            amount=Decimal("5000"),
            status="success",
            reference=f"ref1-{timestamp}",
            gateway="paystack",
            idempotency_key=f"pay1-{timestamp}",
        )
        payment1.save()

        # Create payment for tenant2
        payment2 = Payment(
            tenant_id=tenant2.id,
            amount=Decimal("10000"),
            status="success",
            reference=f"ref2-{timestamp}",
            gateway="paystack",
            idempotency_key=f"pay2-{timestamp}",
        )
        payment2.save()

        # Clear cache
        cache.delete(f"dashboard_metrics:{tenant1.id}")
        cache.delete(f"dashboard_metrics:{tenant2.id}")

        # Get metrics for tenant1
        response1 = client.get(
            f"/api/owner/dashboard/metrics",
            headers={"X-Tenant-ID": str(tenant1.id)},
        )
        metrics1 = response1.json()["data"]

        # Get metrics for tenant2
        response2 = client.get(
            f"/api/owner/dashboard/metrics",
            headers={"X-Tenant-ID": str(tenant2.id)},
        )
        metrics2 = response2.json()["data"]

        # Tenant1 should have 5000 revenue, tenant2 should have 10000
        assert metrics1["revenue"]["current"] == 5000.0
        assert metrics2["revenue"]["current"] == 10000.0

    def test_metrics_endpoint_handles_empty_data(self, clear_db):
        """Test that metrics endpoint handles empty data gracefully."""
        import time
        timestamp = str(int(time.time() * 1000000))
        
        # Create tenant with no data
        tenant = Tenant(
            name=f"Empty Salon {timestamp}",
            subdomain=f"empty-salon-{timestamp}",
            subscription_tier="professional",
            status="active",
        )
        tenant.save()

        response = client.get(
            f"/api/owner/dashboard/metrics",
            headers={"X-Tenant-ID": str(tenant.id)},
        )

        assert response.status_code == 200
        metrics = response.json()["data"]

        # Should return valid structure with zero values
        assert metrics["revenue"]["current"] == 0.0
        assert metrics["appointments"]["today"] == 0
        assert metrics["satisfaction"]["score"] == 0.0
        assert metrics["pendingPayments"]["count"] == 0
        assert metrics["inventoryStatus"]["lowStockCount"] == 0



class TestUpcomingAppointmentsAPI:
    """Test upcoming appointments API endpoint."""

    def test_get_upcoming_appointments_returns_appointments(self, clear_db):
        """Test that appointments endpoint returns upcoming appointments."""
        import time
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

        # Create staff
        staff = Staff(
            tenant_id=tenant.id,
            user_id=user.id,
            payment_type="hourly",
            payment_rate=Decimal("5000"),
            status="active",
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

        # Create appointment
        now = datetime.utcnow()
        appointment = Appointment(
            tenant_id=tenant.id,
            staff_id=staff.id,
            service_id=service.id,
            start_time=now + timedelta(hours=2),
            end_time=now + timedelta(hours=2, minutes=30),
            status="confirmed",
            idempotency_key=f"appt-{timestamp}",
        )
        appointment.save()

        # Make request
        response = client.get(
            f"/api/owner/dashboard/appointments",
            headers={"X-Tenant-ID": str(tenant.id)},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data

        result = data["data"]
        assert "appointments" in result
        assert "total" in result
        assert "limit" in result
        assert "offset" in result
        assert len(result["appointments"]) > 0

    def test_upcoming_appointments_includes_required_fields(self, clear_db):
        """Test that appointments include all required fields."""
        import time
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

        # Create staff
        staff = Staff(
            tenant_id=tenant.id,
            user_id=user.id,
            payment_type="hourly",
            payment_rate=Decimal("5000"),
            status="active",
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

        # Create appointment
        now = datetime.utcnow()
        appointment = Appointment(
            tenant_id=tenant.id,
            staff_id=staff.id,
            service_id=service.id,
            start_time=now + timedelta(hours=2),
            end_time=now + timedelta(hours=2, minutes=30),
            status="confirmed",
            idempotency_key=f"appt-{timestamp}",
        )
        appointment.save()

        # Make request
        response = client.get(
            f"/api/owner/dashboard/appointments",
            headers={"X-Tenant-ID": str(tenant.id)},
        )

        assert response.status_code == 200
        result = response.json()["data"]
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

    def test_upcoming_appointments_pagination(self, clear_db):
        """Test that pagination works correctly."""
        import time
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

        # Create staff
        staff = Staff(
            tenant_id=tenant.id,
            user_id=user.id,
            payment_type="hourly",
            payment_rate=Decimal("5000"),
            status="active",
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

        # Create multiple appointments
        now = datetime.utcnow()
        for i in range(5):
            appointment = Appointment(
                tenant_id=tenant.id,
                staff_id=staff.id,
                service_id=service.id,
                start_time=now + timedelta(hours=2 + i),
                end_time=now + timedelta(hours=2 + i, minutes=30),
                status="confirmed",
                idempotency_key=f"appt-{timestamp}-{i}",
            )
            appointment.save()

        # Get first page
        response1 = client.get(
            f"/api/owner/dashboard/appointments?limit=2&offset=0",
            headers={"X-Tenant-ID": str(tenant.id)},
        )
        result1 = response1.json()["data"]

        # Get second page
        response2 = client.get(
            f"/api/owner/dashboard/appointments?limit=2&offset=2",
            headers={"X-Tenant-ID": str(tenant.id)},
        )
        result2 = response2.json()["data"]

        assert len(result1["appointments"]) <= 2
        assert len(result2["appointments"]) <= 2
        assert result1["total"] == result2["total"]

    def test_upcoming_appointments_tenant_isolation(self, clear_db):
        """Test that only current tenant's appointments are returned."""
        import time
        timestamp = str(int(time.time() * 1000000))
        
        # Create tenant 1
        tenant1 = Tenant(
            name=f"Salon 1 {timestamp}",
            subdomain=f"salon-1-{timestamp}",
            subscription_tier="professional",
            status="active",
        )
        tenant1.save()

        # Create tenant 2
        tenant2 = Tenant(
            name=f"Salon 2 {timestamp}",
            subdomain=f"salon-2-{timestamp}",
            subscription_tier="professional",
            status="active",
        )
        tenant2.save()

        # Create staff for tenant1
        user1 = User(
            tenant_id=tenant1.id,
            email=f"staff1-{timestamp}@test.com",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
        )
        user1.save()

        staff1 = Staff(
            tenant_id=tenant1.id,
            user_id=user1.id,
            payment_type="hourly",
            payment_rate=Decimal("5000"),
            status="active",
        )
        staff1.save()

        # Create staff for tenant2
        user2 = User(
            tenant_id=tenant2.id,
            email=f"staff2-{timestamp}@test.com",
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

        # Create service for tenant1
        service1 = Service(
            tenant_id=tenant1.id,
            name="Haircut",
            description="Professional haircut",
            duration_minutes=30,
            price=Decimal("5000"),
            category="Hair",
        )
        service1.save()

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

        # Create appointment for tenant1
        now = datetime.utcnow()
        appt1 = Appointment(
            tenant_id=tenant1.id,
            staff_id=staff1.id,
            service_id=service1.id,
            start_time=now + timedelta(hours=2),
            end_time=now + timedelta(hours=2, minutes=30),
            status="confirmed",
            idempotency_key=f"appt1-{timestamp}",
        )
        appt1.save()

        # Create appointment for tenant2
        appt2 = Appointment(
            tenant_id=tenant2.id,
            staff_id=staff2.id,
            service_id=service2.id,
            start_time=now + timedelta(hours=3),
            end_time=now + timedelta(hours=4),
            status="confirmed",
            idempotency_key=f"appt2-{timestamp}",
        )
        appt2.save()

        # Get appointments for tenant1
        response1 = client.get(
            f"/api/owner/dashboard/appointments",
            headers={"X-Tenant-ID": str(tenant1.id)},
        )
        result1 = response1.json()["data"]

        # Get appointments for tenant2
        response2 = client.get(
            f"/api/owner/dashboard/appointments",
            headers={"X-Tenant-ID": str(tenant2.id)},
        )
        result2 = response2.json()["data"]

        # Verify tenant isolation
        for appt in result1["appointments"]:
            assert appt["serviceName"] != "Massage"

        for appt in result2["appointments"]:
            assert appt["serviceName"] == "Massage"

    def test_upcoming_appointments_requires_tenant_context(self):
        """Test that appointments endpoint requires tenant context."""
        response = client.get("/api/owner/dashboard/appointments")
        
        # Should fail without tenant context
        assert response.status_code in [401, 400]

    def test_upcoming_appointments_sorted_chronologically(self, clear_db):
        """Test that appointments are sorted chronologically."""
        import time
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

        # Create staff
        staff = Staff(
            tenant_id=tenant.id,
            user_id=user.id,
            payment_type="hourly",
            payment_rate=Decimal("5000"),
            status="active",
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

        # Create appointments in random order
        now = datetime.utcnow()
        times = [
            now + timedelta(hours=5),
            now + timedelta(hours=2),
            now + timedelta(hours=8),
            now + timedelta(hours=3),
        ]

        for i, start_time in enumerate(times):
            appointment = Appointment(
                tenant_id=tenant.id,
                staff_id=staff.id,
                service_id=service.id,
                start_time=start_time,
                end_time=start_time + timedelta(minutes=30),
                status="confirmed",
                idempotency_key=f"appt-{timestamp}-{i}",
            )
            appointment.save()

        # Make request
        response = client.get(
            f"/api/owner/dashboard/appointments",
            headers={"X-Tenant-ID": str(tenant.id)},
        )

        result = response.json()["data"]
        appointments = result["appointments"]

        # Verify appointments are sorted chronologically
        for i in range(len(appointments) - 1):
            assert appointments[i]["startTime"] <= appointments[i + 1]["startTime"]
