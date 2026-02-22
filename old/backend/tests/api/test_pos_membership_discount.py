"""
Integration tests for POS membership discount endpoints
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from bson import ObjectId


@pytest.fixture
def test_tenant_id():
    """Test tenant ID"""
    return "test_tenant_123"


@pytest.fixture
def test_client_id():
    """Test client ID"""
    return str(ObjectId())


@pytest.fixture
def test_plan(db, test_tenant_id):
    """Create a test membership plan"""
    plan_data = {
        "tenant_id": test_tenant_id,
        "name": "Gold Membership",
        "description": "Premium benefits",
        "price": 99.99,
        "billing_cycle": "monthly",
        "benefits": ["20% off services", "Priority booking"],
        "discount_percentage": 20.0,
        "trial_period_days": 7,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = db["membership_plans"].insert_one(plan_data)
    plan_data["_id"] = result.inserted_id
    return plan_data


@pytest.fixture
def test_subscription(db, test_tenant_id, test_client_id, test_plan):
    """Create a test subscription"""
    sub_data = {
        "tenant_id": test_tenant_id,
        "client_id": test_client_id,
        "plan_id": str(test_plan["_id"]),
        "status": "active",
        "start_date": datetime.utcnow(),
        "end_date": datetime.utcnow() + timedelta(days=30),
        "trial_end_date": None,
        "auto_renew": True,
        "payment_method_id": "auth_code_123",
        "payment_history": [],
        "renewal_history": [],
        "benefit_usage": {
            "cycle_start": datetime.utcnow(),
            "usage_count": 0,
            "limit": -1,
        },
        "grace_period_start": None,
        "retry_count": 0,
        "cancellation_reason": None,
        "cancelled_at": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = db["membership_subscriptions"].insert_one(sub_data)
    sub_data["_id"] = result.inserted_id
    return sub_data


def test_get_client_discount_endpoint(client, test_tenant_id, test_client_id, test_subscription):
    """Test getting client discount via API"""
    response = client.get(
        f"/api/pos/client-discount/{test_client_id}",
        headers={"X-Tenant-ID": test_tenant_id}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["has_discount"] is True
    assert data["discount_percentage"] == 20.0
    assert data["plan_name"] == "Gold Membership"


def test_get_client_discount_no_subscription(client, test_tenant_id):
    """Test getting discount for client without subscription"""
    response = client.get(
        f"/api/pos/client-discount/{str(ObjectId())}",
        headers={"X-Tenant-ID": test_tenant_id}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["has_discount"] is False
    assert data["discount_percentage"] == 0.0


def test_apply_membership_discount_endpoint(client, test_tenant_id, test_client_id, test_subscription):
    """Test applying membership discount via API"""
    items = [
        {
            "type": "service",
            "price": 100.0,
            "quantity": 1,
            "item_name": "Haircut",
        },
        {
            "type": "product",
            "price": 50.0,
            "quantity": 1,
            "item_name": "Shampoo",
        },
    ]
    
    response = client.post(
        "/api/pos/apply-membership-discount",
        json={
            "client_id": test_client_id,
            "items": items,
        },
        headers={"X-Tenant-ID": test_tenant_id}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["membership_discount_applied"] is True
    assert data["discount_source"] == "membership"
    assert data["original_total"] == 150.0
    assert data["discount_amount"] == 20.0  # 20% of 100
    assert data["discounted_total"] == 130.0


def test_apply_membership_discount_with_promo_code(client, test_tenant_id, test_client_id, test_subscription):
    """Test that membership discount is not applied when promo code is present"""
    items = [
        {
            "type": "service",
            "price": 100.0,
            "quantity": 1,
            "item_name": "Haircut",
        },
    ]
    
    response = client.post(
        "/api/pos/apply-membership-discount",
        json={
            "client_id": test_client_id,
            "items": items,
            "promo_code": "PROMO123",
        },
        headers={"X-Tenant-ID": test_tenant_id}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["membership_discount_applied"] is False
    assert data["discount_source"] == "promo_code"
    assert data["discount_amount"] == 0.0
