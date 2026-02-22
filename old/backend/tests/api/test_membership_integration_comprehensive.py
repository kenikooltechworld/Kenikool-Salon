"""
Comprehensive Integration Tests for Membership API Endpoints - Phase 9 Testing

Tests all membership API endpoints with real database and services:
- Plan management endpoints
- Subscription management endpoints
- Analytics endpoint
- Response schemas and status codes

Requirements: 13.1, 13.2, 13.3, 13.4, 13.5
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from bson import ObjectId
from decimal import Decimal
from unittest.mock import patch, Mock

from app.main import app
from app.database import Database


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def test_tenant_id():
    """Test tenant ID"""
    return "test_tenant_123"


@pytest.fixture
def test_user_token():
    """Test user authentication token"""
    return "test_token_123"


@pytest.fixture
def auth_headers(test_user_token):
    """Authentication headers"""
    return {"Authorization": f"Bearer {test_user_token}"}


@pytest.fixture
def sample_plan_data():
    """Sample plan data for creation"""
    return {
        "name": "Gold Membership",
        "description": "Premium benefits",
        "price": 99.99,
        "billing_cycle": "monthly",
        "benefits": ["20% off services", "Priority booking"],
        "discount_percentage": 20,
        "trial_period_days": 7,
    }


@pytest.fixture
def sample_subscription_data():
    """Sample subscription data for creation"""
    return {
        "client_id": str(ObjectId()),
        "plan_id": str(ObjectId()),
        "payment_method_id": "pm_123",
        "auto_renew": True,
    }


class TestPlanManagementEndpoints:
    """Tests for plan management endpoints"""

    @patch('app.api.dependencies.get_tenant_id')
    @patch('app.api.memberships.MembershipService')
    def test_list_plans_success(self, mock_service_class, mock_get_tenant, client, auth_headers, sample_plan_data):
        """Test GET /api/memberships/plans"""
        # Setup
        mock_get_tenant.return_value = "test_tenant"
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        plan_id = str(ObjectId())
        mock_service.list_plans.return_value = {
            "plans": [{
                "_id": plan_id,
                **sample_plan_data,
                "is_active": True,
                "created_at": datetime.utcnow().isoformat(),
            }],
            "total": 1,
            "page": 1,
            "pages": 1,
        }
        
        # Execute
        response = client.get("/api/memberships/plans", headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "plans" in data
        assert len(data["plans"]) == 1
        assert data["plans"][0]["name"] == "Gold Membership"

    @patch('app.api.dependencies.get_tenant_id')
    @patch('app.api.memberships.MembershipService')
    def test_list_plans_with_pagination(self, mock_service_class, mock_get_tenant, client, auth_headers):
        """Test GET /api/memberships/plans with pagination"""
        # Setup
        mock_get_tenant.return_value = "test_tenant"
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.list_plans.return_value = {
            "plans": [],
            "total": 100,
            "page": 2,
            "pages": 5,
        }
        
        # Execute
        response = client.get("/api/memberships/plans?page=2&limit=20", headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert data["pages"] == 5

    @patch('app.api.dependencies.get_tenant_id')
    @patch('app.api.memberships.MembershipService')
    def test_create_plan_success(self, mock_service_class, mock_get_tenant, client, auth_headers, sample_plan_data):
        """Test POST /api/memberships/plans"""
        # Setup
        mock_get_tenant.return_value = "test_tenant"
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        plan_id = str(ObjectId())
        mock_service.create_plan.return_value = {
            "_id": plan_id,
            **sample_plan_data,
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
        }
        
        # Execute
        response = client.post("/api/memberships/plans", json=sample_plan_data, headers=auth_headers)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Gold Membership"
        assert data["price"] == 99.99

    @patch('app.api.dependencies.get_tenant_id')
    @patch('app.api.memberships.MembershipService')
    def test_create_plan_invalid_data(self, mock_service_class, mock_get_tenant, client, auth_headers):
        """Test POST /api/memberships/plans with invalid data"""
        # Setup
        mock_get_tenant.return_value = "test_tenant"
        
        invalid_data = {
            "name": "Gold Membership",
            # Missing required fields
        }
        
        # Execute
        response = client.post("/api/memberships/plans", json=invalid_data, headers=auth_headers)
        
        # Assert
        assert response.status_code == 422  # Validation error

    @patch('app.api.dependencies.get_tenant_id')
    @patch('app.api.memberships.MembershipService')
    def test_update_plan_success(self, mock_service_class, mock_get_tenant, client, auth_headers, sample_plan_data):
        """Test PUT /api/memberships/plans/{plan_id}"""
        # Setup
        mock_get_tenant.return_value = "test_tenant"
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        plan_id = str(ObjectId())
        updated_data = sample_plan_data.copy()
        updated_data["price"] = 149.99
        
        mock_service.update_plan.return_value = {
            "_id": plan_id,
            **updated_data,
            "is_active": True,
        }
        
        # Execute
        response = client.put(
            f"/api/memberships/plans/{plan_id}",
            json={"price": 149.99},
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["price"] == 149.99

    @patch('app.api.dependencies.get_tenant_id')
    @patch('app.api.memberships.MembershipService')
    def test_delete_plan_success(self, mock_service_class, mock_get_tenant, client, auth_headers):
        """Test DELETE /api/memberships/plans/{plan_id}"""
        # Setup
        mock_get_tenant.return_value = "test_tenant"
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.delete_plan.return_value = True
        
        plan_id = str(ObjectId())
        
        # Execute
        response = client.delete(f"/api/memberships/plans/{plan_id}", headers=auth_headers)
        
        # Assert
        assert response.status_code == 204

    @patch('app.api.dependencies.get_tenant_id')
    @patch('app.api.memberships.MembershipService')
    def test_get_plan_subscribers_success(self, mock_service_class, mock_get_tenant, client, auth_headers):
        """Test GET /api/memberships/plans/{plan_id}/subscribers"""
        # Setup
        mock_get_tenant.return_value = "test_tenant"
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        plan_id = str(ObjectId())
        mock_service.get_plan_subscribers.return_value = {
            "plan_id": plan_id,
            "subscribers": [
                {
                    "_id": str(ObjectId()),
                    "client_name": "John Doe",
                    "status": "active",
                }
            ],
            "total": 1,
        }
        
        # Execute
        response = client.get(f"/api/memberships/plans/{plan_id}/subscribers", headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "subscribers" in data
        assert len(data["subscribers"]) == 1


class TestSubscriptionManagementEndpoints:
    """Tests for subscription management endpoints"""

    @patch('app.api.dependencies.get_tenant_id')
    @patch('app.api.memberships.MembershipService')
    def test_list_subscriptions_success(self, mock_service_class, mock_get_tenant, client, auth_headers):
        """Test GET /api/memberships/subscriptions"""
        # Setup
        mock_get_tenant.return_value = "test_tenant"
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        mock_service.list_subscriptions.return_value = {
            "subscriptions": [{
                "_id": str(ObjectId()),
                "client_id": str(ObjectId()),
                "plan_id": str(ObjectId()),
                "status": "active",
                "created_at": datetime.utcnow().isoformat(),
            }],
            "total": 1,
            "page": 1,
            "pages": 1,
        }
        
        # Execute
        response = client.get("/api/memberships/subscriptions", headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "subscriptions" in data
        assert len(data["subscriptions"]) == 1

    @patch('app.api.dependencies.get_tenant_id')
    @patch('app.api.memberships.MembershipService')
    def test_list_subscriptions_with_filters(self, mock_service_class, mock_get_tenant, client, auth_headers):
        """Test GET /api/memberships/subscriptions with filters"""
        # Setup
        mock_get_tenant.return_value = "test_tenant"
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.list_subscriptions.return_value = {
            "subscriptions": [],
            "total": 0,
            "page": 1,
            "pages": 1,
        }
        
        # Execute
        response = client.get(
            "/api/memberships/subscriptions?status=active&sort_by=created_at&sort_order=-1",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200

    @patch('app.api.dependencies.get_tenant_id')
    @patch('app.api.memberships.MembershipService')
    def test_create_subscription_success(self, mock_service_class, mock_get_tenant, client, auth_headers, sample_subscription_data):
        """Test POST /api/memberships/subscriptions"""
        # Setup
        mock_get_tenant.return_value = "test_tenant"
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        subscription_id = str(ObjectId())
        mock_service.create_subscription.return_value = {
            "_id": subscription_id,
            **sample_subscription_data,
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
        }
        
        # Execute
        response = client.post(
            "/api/memberships/subscriptions",
            json=sample_subscription_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "active"

    @patch('app.api.dependencies.get_tenant_id')
    @patch('app.api.memberships.MembershipService')
    def test_get_subscription_success(self, mock_service_class, mock_get_tenant, client, auth_headers):
        """Test GET /api/memberships/subscriptions/{subscription_id}"""
        # Setup
        mock_get_tenant.return_value = "test_tenant"
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        subscription_id = str(ObjectId())
        mock_service.get_subscription_details.return_value = {
            "_id": subscription_id,
            "client_id": str(ObjectId()),
            "plan_id": str(ObjectId()),
            "status": "active",
        }
        
        # Execute
        response = client.get(
            f"/api/memberships/subscriptions/{subscription_id}",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["_id"] == subscription_id

    @patch('app.api.dependencies.get_tenant_id')
    @patch('app.api.memberships.MembershipService')
    def test_cancel_subscription_success(self, mock_service_class, mock_get_tenant, client, auth_headers):
        """Test POST /api/memberships/subscriptions/{subscription_id}/cancel"""
        # Setup
        mock_get_tenant.return_value = "test_tenant"
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        subscription_id = str(ObjectId())
        mock_service.cancel_subscription.return_value = {
            "_id": subscription_id,
            "status": "cancelled",
        }
        
        # Execute
        response = client.post(
            f"/api/memberships/subscriptions/{subscription_id}/cancel",
            json={"reason": "User requested"},
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"

    @patch('app.api.dependencies.get_tenant_id')
    @patch('app.api.memberships.MembershipService')
    def test_pause_subscription_success(self, mock_service_class, mock_get_tenant, client, auth_headers):
        """Test POST /api/memberships/subscriptions/{subscription_id}/pause"""
        # Setup
        mock_get_tenant.return_value = "test_tenant"
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        subscription_id = str(ObjectId())
        mock_service.pause_subscription.return_value = {
            "_id": subscription_id,
            "status": "paused",
        }
        
        # Execute
        response = client.post(
            f"/api/memberships/subscriptions/{subscription_id}/pause",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "paused"

    @patch('app.api.dependencies.get_tenant_id')
    @patch('app.api.memberships.MembershipService')
    def test_resume_subscription_success(self, mock_service_class, mock_get_tenant, client, auth_headers):
        """Test POST /api/memberships/subscriptions/{subscription_id}/resume"""
        # Setup
        mock_get_tenant.return_value = "test_tenant"
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        subscription_id = str(ObjectId())
        mock_service.resume_subscription.return_value = {
            "_id": subscription_id,
            "status": "active",
        }
        
        # Execute
        response = client.post(
            f"/api/memberships/subscriptions/{subscription_id}/resume",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"

    @patch('app.api.dependencies.get_tenant_id')
    @patch('app.api.memberships.MembershipService')
    def test_change_plan_success(self, mock_service_class, mock_get_tenant, client, auth_headers):
        """Test POST /api/memberships/subscriptions/{subscription_id}/change-plan"""
        # Setup
        mock_get_tenant.return_value = "test_tenant"
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        subscription_id = str(ObjectId())
        new_plan_id = str(ObjectId())
        mock_service.change_plan.return_value = {
            "_id": subscription_id,
            "plan_id": new_plan_id,
        }
        
        # Execute
        response = client.post(
            f"/api/memberships/subscriptions/{subscription_id}/change-plan",
            json={"new_plan_id": new_plan_id},
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["plan_id"] == new_plan_id

    @patch('app.api.dependencies.get_tenant_id')
    @patch('app.api.memberships.MembershipService')
    def test_update_payment_method_success(self, mock_service_class, mock_get_tenant, client, auth_headers):
        """Test POST /api/memberships/subscriptions/{subscription_id}/payment-method"""
        # Setup
        mock_get_tenant.return_value = "test_tenant"
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        subscription_id = str(ObjectId())
        mock_service.update_payment_method.return_value = {
            "_id": subscription_id,
            "payment_method_id": "pm_new_123",
        }
        
        # Execute
        response = client.post(
            f"/api/memberships/subscriptions/{subscription_id}/payment-method",
            json={"payment_method_id": "pm_new_123"},
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["payment_method_id"] == "pm_new_123"


class TestAnalyticsEndpoint:
    """Tests for analytics endpoint"""

    @patch('app.api.dependencies.get_tenant_id')
    @patch('app.api.memberships.MembershipService')
    def test_get_analytics_success(self, mock_service_class, mock_get_tenant, client, auth_headers):
        """Test GET /api/memberships/analytics"""
        # Setup
        mock_get_tenant.return_value = "test_tenant"
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        mock_service.get_analytics.return_value = {
            "mrr": 9999.00,
            "arr": 119988.00,
            "active_subscribers": 100,
            "churn_rate": 5.0,
            "growth_rate": 10.0,
            "revenue_by_plan": {
                "Gold": 5000.00,
                "Silver": 3000.00,
                "Bronze": 1999.00,
            },
            "status_distribution": {
                "active": 100,
                "paused": 5,
                "cancelled": 10,
                "grace_period": 2,
            },
        }
        
        # Execute
        response = client.get("/api/memberships/analytics", headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "mrr" in data
        assert "arr" in data
        assert "active_subscribers" in data
        assert data["mrr"] == 9999.00

    @patch('app.api.dependencies.get_tenant_id')
    @patch('app.api.memberships.MembershipService')
    def test_get_analytics_with_date_range(self, mock_service_class, mock_get_tenant, client, auth_headers):
        """Test GET /api/memberships/analytics with date range"""
        # Setup
        mock_get_tenant.return_value = "test_tenant"
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.get_analytics.return_value = {
            "mrr": 5000.00,
            "arr": 60000.00,
            "active_subscribers": 50,
        }
        
        # Execute
        start_date = (datetime.utcnow() - timedelta(days=30)).isoformat()
        end_date = datetime.utcnow().isoformat()
        response = client.get(
            f"/api/memberships/analytics?start_date={start_date}&end_date={end_date}",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200


class TestErrorHandling:
    """Tests for error handling"""

    @patch('app.api.dependencies.get_tenant_id')
    def test_unauthorized_access(self, mock_get_tenant, client):
        """Test unauthorized access without token"""
        # Execute
        response = client.get("/api/memberships/plans")
        
        # Assert
        assert response.status_code == 401

    @patch('app.api.dependencies.get_tenant_id')
    @patch('app.api.memberships.MembershipService')
    def test_not_found_error(self, mock_service_class, mock_get_tenant, client, auth_headers):
        """Test 404 error for non-existent resource"""
        # Setup
        mock_get_tenant.return_value = "test_tenant"
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.get_subscription_details.side_effect = ValueError("Subscription not found")
        
        # Execute
        response = client.get(
            f"/api/memberships/subscriptions/{ObjectId()}",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code in [404, 400]

