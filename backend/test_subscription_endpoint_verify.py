"""Verify subscription endpoint works correctly."""

import sys
import os
from datetime import datetime
from bson import ObjectId

# Add backend to path
sys.path.insert(0, '/app')
os.environ['MONGODB_URL'] = 'mongodb://localhost:27017/salon_test'

from app.models.subscription import Subscription
from app.models.pricing_plan import PricingPlan
from app.models.tenant import Tenant
from app.services.subscription_service import SubscriptionService


def test_subscription_endpoint():
    """Test that subscription endpoint returns subscription (auto-created if needed)."""
    print("\n=== Testing Subscription Endpoint ===")
    
    # Create a test tenant
    tenant = Tenant(
        name="Test Tenant",
        subdomain="test-tenant",
        owner_email="test@example.com",
        status="active"
    )
    tenant.save()
    tenant_id = str(tenant.id)
    print(f"✓ Created test tenant: {tenant_id}")
    
    # Test 1: Get subscription for tenant with no subscription (should auto-create)
    print("\nTest 1: Auto-create subscription on first request")
    sub = SubscriptionService.get_subscription(tenant_id)
    assert sub is not None, "Subscription should be auto-created"
    assert sub.tenant_id == ObjectId(tenant_id), "Subscription should belong to tenant"
    assert sub.is_trial, "New subscription should be trial"
    print(f"✓ Subscription auto-created: {sub.id}")
    print(f"  - Status: {sub.status}")
    print(f"  - Plan: {sub.pricing_plan_id}")
    print(f"  - Trial: {sub.is_trial}")
    
    # Test 2: Get subscription again (should return same subscription)
    print("\nTest 2: Get existing subscription")
    sub2 = SubscriptionService.get_subscription(tenant_id)
    assert sub2 is not None, "Subscription should be found"
    assert str(sub2.id) == str(sub.id), "Should return same subscription"
    print(f"✓ Retrieved existing subscription: {sub2.id}")
    
    # Test 3: Verify subscription has valid plan
    print("\nTest 3: Verify subscription has valid plan")
    plan = PricingPlan.objects(id=sub.pricing_plan_id).first()
    assert plan is not None, "Subscription should have valid plan"
    print(f"✓ Plan found: {plan.name} (tier {plan.tier_level})")
    
    # Cleanup
    print("\nCleaning up...")
    Subscription.objects(tenant_id=ObjectId(tenant_id)).delete()
    tenant.delete()
    print("✓ Cleanup complete")
    
    print("\n=== All Tests Passed ===")


if __name__ == "__main__":
    try:
        test_subscription_endpoint()
    except Exception as e:
        print(f"\n✗ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
