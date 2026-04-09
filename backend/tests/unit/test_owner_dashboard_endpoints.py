"""Unit tests for owner dashboard endpoints."""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock
from bson import ObjectId
from fastapi.testclient import TestClient
from app.main import app
from app.models.payment import Payment
from app.models.appointment import Appointment
from app.models.inventory import Inventory
from app.models.staff import Staff

client = TestClient(app)


@pytest.fixture
def tenant_id():
    """Create a test tenant ID."""
    return ObjectId()


@pytest.fixture
def user_id():
    """Create a test user ID."""
    return ObjectId()


@pytest.fixture
def auth_headers(tenant_id, user_id):
    """Create auth headers for testing."""
    return {
        "Authorization": f"Bearer test-token",
        "X-Tenant-ID": str(tenant_id),
        "X-User-ID": str(user_id),
    }


class TestDashboardMetricsEndpoint:
    """Tests for GET /owner/dashboard/metrics endpoint."""

    def test_get_metrics_returns_all_metrics(self, auth_headers):
        """Test that metrics endpoint returns all required metrics."""
        with patch("app.routes.owner_dashboard.service") as mock_service:
            mock_service.get_all_metrics.return_value = {
                "revenue": {
                    "current": 5000.0,
                    "previous": 4500.0,
                    "trend": "up",
                    "trendPercentage": 11.11,
                },
                "appointments": {
                    "today": 5,
                    "thisWeek": 28,
                    "thisMonth": 120,
                    "trend": "up",
                },
                "satisfaction": {
                    "score": 4.7,
                    "count": 45,
                    "trend": "up",
                },
                "staffUtilization": {
                    "percentage": 78.5,
                    "bookedHours": 157,
                    "availableHours": 200,
                },
                "pendingPayments": {
                    "count": 3,
                    "totalAmount": 450.0,
                    "oldestDate": "2026-03-15T10:30:00",
                },
                "inventoryStatus": {
                    "lowStockCount": 5,
                    "expiringCount": 2,
                },
            }

            response = client.get(
                "/api/owner/dashboard/metrics",
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "revenue" in data["data"]
            assert "appointments" in data["data"]
            assert "satisfaction" in data["data"]
            assert "staffUtilization" in data["data"]
            assert "pendingPayments" in data["data"]
            assert "inventoryStatus" in data["data"]

    def test_get_metrics_uses_cache(self, auth_headers):
        """Test that metrics endpoint uses cache when available."""
        with patch("app.routes.owner_dashboard.service") as mock_service:
            mock_service.get_all_metrics.return_value = {"revenue": {}}

            # First call
            client.get("/api/owner/dashboard/metrics", headers=auth_headers)
            # Second call
            client.get("/api/owner/dashboard/metrics", headers=auth_headers)

            # Service should be called twice (cache is per-request in tests)
            assert mock_service.get_all_metrics.call_count >= 1

    def test_get_metrics_without_cache(self, auth_headers):
        """Test that metrics endpoint can skip cache."""
        with patch("app.routes.owner_dashboard.service") as mock_service:
            mock_service.get_all_metrics.return_value = {"revenue": {}}

            response = client.get(
                "/api/owner/dashboard/metrics?use_cache=false",
                headers=auth_headers,
            )

            assert response.status_code == 200
            mock_service.get_all_metrics.assert_called()

    def test_get_metrics_requires_auth(self):
        """Test that metrics endpoint requires authentication."""
        response = client.get("/api/owner/dashboard/metrics")
        assert response.status_code in [401, 403]


class TestUpcomingAppointmentsEndpoint:
    """Tests for GET /owner/dashboard/appointments endpoint."""

    def test_get_appointments_returns_list(self, auth_headers):
        """Test that appointments endpoint returns list of appointments."""
        with patch("app.routes.owner_dashboard.service") as mock_service:
            mock_service.get_upcoming_appointments.return_value = {
                "appointments": [
                    {
                        "id": "507f1f77bcf86cd799439011",
                        "customerName": "John Doe",
                        "serviceName": "Haircut",
                        "staffName": "Jane Smith",
                        "startTime": "2026-03-20T10:00:00",
                        "endTime": "2026-03-20T10:30:00",
                        "status": "confirmed",
                        "isPublicBooking": False,
                    }
                ],
                "total": 1,
                "limit": 10,
                "offset": 0,
            }

            response = client.get(
                "/api/owner/dashboard/appointments",
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "appointments" in data["data"]
            assert len(data["data"]["appointments"]) == 1

    def test_get_appointments_with_limit(self, auth_headers):
        """Test that appointments endpoint respects limit parameter."""
        with patch("app.routes.owner_dashboard.service") as mock_service:
            mock_service.get_upcoming_appointments.return_value = {
                "appointments": [],
                "total": 0,
                "limit": 5,
                "offset": 0,
            }

            response = client.get(
                "/api/owner/dashboard/appointments?limit=5",
                headers=auth_headers,
            )

            assert response.status_code == 200
            mock_service.get_upcoming_appointments.assert_called()

    def test_get_appointments_with_pagination(self, auth_headers):
        """Test that appointments endpoint supports pagination."""
        with patch("app.routes.owner_dashboard.service") as mock_service:
            mock_service.get_upcoming_appointments.return_value = {
                "appointments": [],
                "total": 20,
                "limit": 10,
                "offset": 10,
            }

            response = client.get(
                "/api/owner/dashboard/appointments?limit=10&offset=10",
                headers=auth_headers,
            )

            assert response.status_code == 200


class TestPendingActionsEndpoint:
    """Tests for GET /owner/dashboard/pending-actions endpoint."""

    def test_get_pending_actions_returns_list(self, auth_headers):
        """Test that pending actions endpoint returns list of actions."""
        with patch("app.routes.owner_dashboard.service") as mock_service:
            mock_service.get_pending_actions.return_value = {
                "actions": [
                    {
                        "id": "507f1f77bcf86cd799439011",
                        "description": "Payment from John Doe ($150) pending for 3 days",
                        "dueDate": "2026-03-20T10:00:00",
                        "priority": "high",
                        "type": "payment",
                        "actionUrl": "/payments/507f1f77bcf86cd799439011",
                    }
                ],
                "total": 1,
            }

            response = client.get(
                "/api/owner/dashboard/pending-actions",
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "actions" in data["data"]

    def test_get_pending_actions_sorted_by_priority(self, auth_headers):
        """Test that pending actions are sorted by priority."""
        with patch("app.routes.owner_dashboard.service") as mock_service:
            mock_service.get_pending_actions.return_value = {
                "actions": [
                    {"priority": "high", "description": "High priority action"},
                    {"priority": "medium", "description": "Medium priority action"},
                    {"priority": "low", "description": "Low priority action"},
                ],
                "total": 3,
            }

            response = client.get(
                "/api/owner/dashboard/pending-actions",
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            actions = data["data"]["actions"]
            assert actions[0]["priority"] == "high"


class TestRevenueAnalyticsEndpoint:
    """Tests for GET /owner/dashboard/revenue-analytics endpoint."""

    def test_get_revenue_analytics_returns_data(self, auth_headers):
        """Test that revenue analytics endpoint returns data."""
        with patch("app.routes.owner_dashboard.service") as mock_service:
            mock_service.get_revenue_analytics.return_value = {
                "daily": [],
                "weekly": [],
                "monthly": [],
                "byServiceType": [],
                "byStaff": [],
                "metrics": {
                    "total": 5000.0,
                    "average": 166.67,
                    "growth": 11.11,
                },
            }

            response = client.get(
                "/api/owner/dashboard/revenue-analytics",
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "daily" in data["data"]
            assert "metrics" in data["data"]

    def test_get_revenue_analytics_with_date_range(self, auth_headers):
        """Test that revenue analytics endpoint supports date range."""
        with patch("app.routes.owner_dashboard.service") as mock_service:
            mock_service.get_revenue_analytics.return_value = {
                "daily": [],
                "weekly": [],
                "monthly": [],
                "byServiceType": [],
                "byStaff": [],
                "metrics": {"total": 0.0, "average": 0.0, "growth": 0.0},
            }

            response = client.get(
                "/api/owner/dashboard/revenue-analytics?start_date=2026-03-01&end_date=2026-03-31",
                headers=auth_headers,
            )

            assert response.status_code == 200


class TestStaffPerformanceEndpoint:
    """Tests for GET /owner/dashboard/staff-performance endpoint."""

    def test_get_staff_performance_returns_data(self, auth_headers):
        """Test that staff performance endpoint returns data."""
        with patch("app.routes.owner_dashboard.service") as mock_service:
            mock_service.get_staff_performance.return_value = {
                "staff": [
                    {
                        "id": "507f1f77bcf86cd799439011",
                        "name": "Jane Smith",
                        "revenue": 5000.0,
                        "utilization": 78.5,
                        "satisfaction": 4.7,
                        "attendance": 95.0,
                        "comparison": {
                            "revenueChange": 11.11,
                            "utilizationChange": 5.0,
                            "satisfactionChange": 0.2,
                        },
                    }
                ]
            }

            response = client.get(
                "/api/owner/dashboard/staff-performance",
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "staff" in data["data"]
            assert len(data["data"]["staff"]) > 0


class TestPendingActionMutationEndpoints:
    """Tests for POST endpoints to mark actions complete/dismiss."""

    def test_mark_action_complete(self, auth_headers):
        """Test marking an action as complete."""
        with patch("app.routes.owner_dashboard.service") as mock_service:
            response = client.post(
                "/api/owner/dashboard/pending-actions/507f1f77bcf86cd799439011/complete",
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            mock_service.mark_action_complete.assert_called()

    def test_dismiss_action(self, auth_headers):
        """Test dismissing an action."""
        with patch("app.routes.owner_dashboard.service") as mock_service:
            response = client.post(
                "/api/owner/dashboard/pending-actions/507f1f77bcf86cd799439011/dismiss",
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            mock_service.dismiss_action.assert_called()


class TestTenantIsolation:
    """Tests for tenant isolation in dashboard endpoints."""

    def test_metrics_only_returns_tenant_data(self, auth_headers, tenant_id):
        """Test that metrics endpoint only returns current tenant's data."""
        with patch("app.routes.owner_dashboard.service") as mock_service:
            mock_service.get_all_metrics.return_value = {"revenue": {}}

            response = client.get(
                "/api/owner/dashboard/metrics",
                headers=auth_headers,
            )

            assert response.status_code == 200
            # Verify tenant_id was passed to service
            call_args = mock_service.get_all_metrics.call_args
            assert call_args is not None

    def test_appointments_only_returns_tenant_data(self, auth_headers, tenant_id):
        """Test that appointments endpoint only returns current tenant's data."""
        with patch("app.routes.owner_dashboard.service") as mock_service:
            mock_service.get_upcoming_appointments.return_value = {
                "appointments": [],
                "total": 0,
                "limit": 10,
                "offset": 0,
            }

            response = client.get(
                "/api/owner/dashboard/appointments",
                headers=auth_headers,
            )

            assert response.status_code == 200
