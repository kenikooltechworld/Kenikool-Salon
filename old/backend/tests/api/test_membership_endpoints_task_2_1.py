"""
Tests for Membership API Endpoints - Task 2.1: Plan Management Endpoints

This test file validates all plan management endpoints:
- GET /api/memberships/plans
- POST /api/memberships/plans
- PUT /api/memberships/plans/{plan_id}
- DELETE /api/memberships/plans/{plan_id}
- GET /api/memberships/plans/{plan_id}/subscribers

Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.12
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from bson import ObjectId
from unittest.mock import Mock, patch, MagicMock

from app.main import app
from app.database import Database


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_db():
    """Create mock database"""
    db = Mock(spec=Database)
    db.__getitem__ = Mock(return_value=Mock())
    return db


@pytest.fixture
def mock_tenant_id():
    """Mock tenant ID"""
    return "test_tenant_123"


@pytest.fixture
def mock_user():
    """Mock authenticated user"""
    return {
        "user_id": "user_123",
        "tenant_id": "test_tenant_123",
        "role": "admin",
        "email": "admin@example.com"
    }


@pytest.fixture
def sample_plan():
    """Sample membership plan"""
    return {
        "_id": ObjectId(),
        "tenant_id": "test_tenant_123",
        "name": "Gold Membership",
        "description": "Premium benefits",
        "price": 99.99,
        "billing_cycle": "monthly",
        "benefits": ["20% off services", "Priority booking"],
        "discount_percentage": 20,
        "trial_period_days": 7,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "created_by": "user_123"
    }


class TestListPlans:
    """Tests for GET /api/memberships/plans"""
    
    @patch('app.api.memberships.Database.get_db')
    @patch('app.api.memberships.MembershipService')
    def test_list_plans_success(self, mock_service_class, mock_get_db, client, mock_db, sample_plan):
        """Test successfully listing plans"""
        # Setup
        mock_get_db.return_value = mock_db
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        mock_service.get_plans.return_value = {
            "plans": [sample_plan],
            "total": 1,
            "page": 1,
            "pages": 1,
            "limit": 20
        }
        
        mock_db.__getitem__.return_value.count_documents.return_value = 5
        
        # Execute
        with patch('app.api.dependencies.get_tenant_id', return_value="test_tenant_123"):
            response = client.get("/api/memberships/plans")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "plans" in data
        assert data["total"] == 1
        assert data["page"] == 1
    
    @patch('app.api.memberships.Database.get_db')
    @patch('app.api.memberships.MembershipService')
    def test_list_plans_with_filters(self, mock_service_class, mock_get_db, client, mock_db, sample_plan):
        """Test listing plans with filters"""
        # Setup
        mock_get_db.return_value = mock_db
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        mock_service.get_plans.return_value = {
            "plans": [sample_plan],
            "total": 1,
            "page": 1,
            "pages": 1,
            "limit": 20
        }
        
        mock_db.__getitem__.return_value.count_documents.return_value = 5
        
        # Execute
        with patch('app.api.dependencies.get_tenant_id', return_value="test_tenant_123"):
            response = client.get(
                "/api/memberships/plans",
                params={"is_active": True, "billing_cycle": "monthly"}
            )
        
        # Assert
        assert response.status_code == 200
        mock_service.get_plans.assert_called_once()
        call_kwargs = mock_service.get_plans.call_args[1]
        assert call_kwargs["is_active"] is True
        assert call_kwargs["billing_cycle"] == "monthly"
    
    @patch('app.api.memberships.Database.get_db')
    @patch('app.api.memberships.MembershipService')
    def test_list_plans_pagination(self, mock_service_class, mock_get_db, client, mock_db, sample_plan):
        """Test listing plans with pagination"""
        # Setup
        mock_get_db.return_value = mock_db
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        mock_service.get_plans.return_value = {
            "plans": [sample_plan],
            "total": 50,
            "page": 2,
            "pages": 3,
            "limit": 20
        }
        
        mock_db.__getitem__.return_value.count_documents.return_value = 5
        
        # Execute
        with patch('app.api.dependencies.get_tenant_id', return_value="test_tenant_123"):
            response = client.get(
                "/api/memberships/plans",
                params={"page": 2, "limit": 20}
            )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert data["pages"] == 3


class TestCreatePlan:
    """Tests for POST /api/memberships/plans"""
    
    @patch('app.api.memberships.Database.get_db')
    @patch('app.api.memberships.MembershipService')
    @patch('app.api.dependencies.get_current_user')
    def test_create_plan_success(self, mock_get_user, mock_service_class, mock_get_db, client, mock_db, mock_user, sample_plan):
        """Test successfully creating a plan"""
        # Setup
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.create_plan.return_value = sample_plan
        
        plan_data = {
            "name": "Gold Membership",
            "description": "Premium benefits",
            "price": 99.99,
            "billing_cycle": "monthly",
            "benefits": ["20% off services", "Priority booking"],
            "discount_percentage": 20,
            "trial_period_days": 7
        }
        
        # Execute
        with patch('app.api.dependencies.get_tenant_id', return_value="test_tenant_123"):
            response = client.post(
                "/api/memberships/plans",
                json=plan_data
            )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Gold Membership"
        assert data["price"] == 99.99
        mock_service.create_plan.assert_called_once()
    
    @patch('app.api.memberships.Database.get_db')
    @patch('app.api.memberships.MembershipService')
    @patch('app.api.dependencies.get_current_user')
    def test_create_plan_validation_error(self, mock_get_user, mock_service_class, mock_get_db, client, mock_db, mock_user):
        """Test plan creation with validation error"""
        # Setup
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.create_plan.side_effect = ValueError("Plan name already exists")
        
        plan_data = {
            "name": "Gold Membership",
            "price": 99.99,
            "billing_cycle": "monthly"
        }
        
        # Execute
        with patch('app.api.dependencies.get_tenant_id', return_value="test_tenant_123"):
            response = client.post(
                "/api/memberships/plans",
                json=plan_data
            )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    @patch('app.api.memberships.Database.get_db')
    @patch('app.api.memberships.MembershipService')
    @patch('app.api.dependencies.get_current_user')
    def test_create_plan_invalid_price(self, mock_get_user, mock_service_class, mock_get_db, client, mock_db, mock_user):
        """Test plan creation with invalid price"""
        # Setup
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user
        
        plan_data = {
            "name": "Gold Membership",
            "price": -10,  # Invalid: negative price
            "billing_cycle": "monthly"
        }
        
        # Execute
        with patch('app.api.dependencies.get_tenant_id', return_value="test_tenant_123"):
            response = client.post(
                "/api/memberships/plans",
                json=plan_data
            )
        
        # Assert
        assert response.status_code == 422  # Validation error


class TestUpdatePlan:
    """Tests for PUT /api/memberships/plans/{plan_id}"""
    
    @patch('app.api.memberships.Database.get_db')
    @patch('app.api.memberships.MembershipService')
    @patch('app.api.dependencies.get_current_user')
    def test_update_plan_success(self, mock_get_user, mock_service_class, mock_get_db, client, mock_db, mock_user, sample_plan):
        """Test successfully updating a plan"""
        # Setup
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        updated_plan = sample_plan.copy()
        updated_plan["price"] = 149.99
        mock_service.update_plan.return_value = updated_plan
        
        update_data = {"price": 149.99}
        
        # Execute
        with patch('app.api.dependencies.get_tenant_id', return_value="test_tenant_123"):
            response = client.put(
                f"/api/memberships/plans/{sample_plan['_id']}",
                json=update_data
            )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["price"] == 149.99
    
    @patch('app.api.memberships.Database.get_db')
    @patch('app.api.memberships.MembershipService')
    @patch('app.api.dependencies.get_current_user')
    def test_update_plan_not_found(self, mock_get_user, mock_service_class, mock_get_db, client, mock_db, mock_user):
        """Test updating non-existent plan"""
        # Setup
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.update_plan.side_effect = ValueError("Plan not found")
        
        # Execute
        with patch('app.api.dependencies.get_tenant_id', return_value="test_tenant_123"):
            response = client.put(
                "/api/memberships/plans/invalid_id",
                json={"price": 149.99}
            )
        
        # Assert
        assert response.status_code == 400


class TestDeletePlan:
    """Tests for DELETE /api/memberships/plans/{plan_id}"""
    
    @patch('app.api.memberships.Database.get_db')
    @patch('app.api.memberships.MembershipService')
    @patch('app.api.dependencies.get_current_user')
    def test_delete_plan_success(self, mock_get_user, mock_service_class, mock_get_db, client, mock_db, mock_user, sample_plan):
        """Test successfully deleting a plan"""
        # Setup
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.delete_plan.return_value = {"deleted_count": 1}
        
        # Execute
        with patch('app.api.dependencies.get_tenant_id', return_value="test_tenant_123"):
            response = client.delete(f"/api/memberships/plans/{sample_plan['_id']}")
        
        # Assert
        assert response.status_code == 204
    
    @patch('app.api.memberships.Database.get_db')
    @patch('app.api.memberships.MembershipService')
    @patch('app.api.dependencies.get_current_user')
    def test_delete_plan_with_active_subscriptions(self, mock_get_user, mock_service_class, mock_get_db, client, mock_db, mock_user, sample_plan):
        """Test deleting plan with active subscriptions"""
        # Setup
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.delete_plan.side_effect = ValueError("Cannot delete plan with 5 active subscriptions")
        
        # Execute
        with patch('app.api.dependencies.get_tenant_id', return_value="test_tenant_123"):
            response = client.delete(f"/api/memberships/plans/{sample_plan['_id']}")
        
        # Assert
        assert response.status_code == 400
    
    @patch('app.api.memberships.Database.get_db')
    @patch('app.api.memberships.MembershipService')
    @patch('app.api.dependencies.get_current_user')
    def test_delete_plan_force(self, mock_get_user, mock_service_class, mock_get_db, client, mock_db, mock_user, sample_plan):
        """Test force deleting plan with active subscriptions"""
        # Setup
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.delete_plan.return_value = {"deleted_count": 1}
        
        # Execute
        with patch('app.api.dependencies.get_tenant_id', return_value="test_tenant_123"):
            response = client.delete(
                f"/api/memberships/plans/{sample_plan['_id']}",
                params={"force": True}
            )
        
        # Assert
        assert response.status_code == 204
        mock_service.delete_plan.assert_called_once()
        call_kwargs = mock_service.delete_plan.call_args[1]
        assert call_kwargs["force"] is True


class TestGetPlanSubscribers:
    """Tests for GET /api/memberships/plans/{plan_id}/subscribers"""
    
    @patch('app.api.memberships.Database.get_db')
    @patch('app.api.memberships.MembershipService')
    @patch('app.api.dependencies.get_current_user')
    def test_get_plan_subscribers_success(self, mock_get_user, mock_service_class, mock_get_db, client, mock_db, mock_user, sample_plan):
        """Test successfully getting plan subscribers"""
        # Setup
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        mock_service.get_plan_subscribers.return_value = {
            "plan": sample_plan,
            "subscribers": [
                {
                    "subscription_id": "sub_1",
                    "client": {"_id": "client_1", "name": "John Doe"},
                    "status": "active",
                    "start_date": datetime.utcnow(),
                    "next_billing": datetime.utcnow()
                }
            ],
            "total_count": 1,
            "total_revenue": 99.99,
            "average_subscription_duration_days": 30
        }
        
        # Execute
        with patch('app.api.dependencies.get_tenant_id', return_value="test_tenant_123"):
            response = client.get(f"/api/memberships/plans/{sample_plan['_id']}/subscribers")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "plan" in data
        assert "subscribers" in data
        assert data["total_count"] == 1
        assert data["total_revenue"] == 99.99
    
    @patch('app.api.memberships.Database.get_db')
    @patch('app.api.memberships.MembershipService')
    @patch('app.api.dependencies.get_current_user')
    def test_get_plan_subscribers_not_found(self, mock_get_user, mock_service_class, mock_get_db, client, mock_db, mock_user):
        """Test getting subscribers for non-existent plan"""
        # Setup
        mock_get_db.return_value = mock_db
        mock_get_user.return_value = mock_user
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.get_plan_subscribers.side_effect = ValueError("Plan not found")
        
        # Execute
        with patch('app.api.dependencies.get_tenant_id', return_value="test_tenant_123"):
            response = client.get("/api/memberships/plans/invalid_id/subscribers")
        
        # Assert
        assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
