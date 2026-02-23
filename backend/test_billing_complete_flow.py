"""Complete end-to-end test of billing system."""

import sys
import os
from datetime import datetime, timedelta
from bson import ObjectId

# Add backend to path
sys.path.insert(0, '/app')
os.environ['MONGODB_URL'] = 'mongodb://localhost:27017/salon_test'

from app.models.subscription import Subscription
from app.models.pricing_plan import PricingPlan
from app.models.tenant import Tenant
from app.services.subscription_service import SubscriptionService


def test_complete_billing_flow():
    """Test complete billing flow: trial → upgrade → downgrade → cancel."""
    print("\n=== Complete Billing Flow Test ===\n")
    
    # Create test tenant
    tenant = Tenant(
        name="Flow Test Tenant",
        subdomain="flow-test",
        owner_email="flow@example.com",
        status="active"
    )
    tenant.save()
    tenant_id = str(tenant.id)
    print(f"✓ Created tenant: {tenant_id}")
    
    # Step 1: Get subscription (auto-create trial)
    print("\n--- Step 1: Auto-create Trial Subscription ---")
    sub = SubscriptionService.get_subscription(tenant_id)
    assert sub is not None, "Subscription should be auto-created"
    assert sub.is_trial, "Should be trial subscription"
    assert sub.status == "trial", "Status should be 'trial'"
    print(f"✓ Trial subscription created")
    print(f"  - Status: {sub.status}")
    print(f"  - Is Trial: {sub.is_trial}")
    print(f"  - Days until expiry: {sub.days_until_expiry()}")
    
    # Step 2: Upgrade to Starter plan
    print("\n--- Step 2: Upgrade to Starter Plan ---")
    starter_plan = PricingPlan.objects(tier_level=1).first()
    assert starter_plan is not None, "Starter plan should exist"
    
    sub_upgraded = SubscriptionService.upgrade_subscription(
        tenant_id=tenant_id,
        new_plan_id=str(starter_plan.id),
        billing_cycle="monthly"
    )
    assert sub_upgraded.status == "active", "Status should be 'active' after upgrade"
    assert not sub_upgraded.is_trial, "Should no longer be trial"
    print(f"✓ Upgraded to Starter plan")
    print(f"  - Status: {sub_upgraded.status}")
    print(f"  - Plan: {starter_plan.name}")
    print(f"  - Billing cycle: {sub_upgraded.billing_cycle}")
    
    # Step 3: Downgrade to Free plan
    print("\n--- Step 3: Downgrade to Free Plan ---")
    free_plan = PricingPlan.objects(tier_level=0).first()
    assert free_plan is not None, "Free plan should exist"
    
    sub_downgraded = SubscriptionService.downgrade_subscription(
        tenant_id=tenant_id,
        new_plan_id=str(free_plan.id),
        billing_cycle="monthly"
    )
    assert sub_downgraded.status == "active", "Status should remain 'active' after downgrade"
    print(f"✓ Downgraded to Free plan")
    print(f"  - Status: {sub_downgraded.status}")
    print(f"  - Plan: {free_plan.name}")
    
    # Step 4: Cancel subscription
    print("\n--- Step 4: Cancel Subscription ---")
    sub_canceled = SubscriptionService.cancel_subscription(tenant_id)
    assert sub_canceled.status == "canceled", "Status should be 'canceled'"
    assert sub_canceled.canceled_at is not None, "canceled_at should be set"
    print(f"✓ Subscription canceled")
    print(f"  - Status: {sub_canceled.status}")
    print(f"  - Canceled at: {sub_canceled.canceled_at}")
    
    # Step 5: Verify subscription endpoint returns canceled subscription
    print("\n--- Step 5: Verify Endpoint Returns Canceled Subscription ---")
    sub_final = SubscriptionService.get_subscription(tenant_id)
    assert sub_final is not None, "Should still return subscription"
    assert sub_final.status == "canceled", "Should return canceled subscription"
    print(f"✓ Endpoint returns canceled subscription")
    print(f"  - Status: {sub_final.status}")
    
    # Cleanup
    print("\n--- Cleanup ---")
    Subscription.objects(tenant_id=ObjectId(tenant_id)).delete()
    tenant.delete()
    print("✓ Cleanup complete")
    
    print("\n=== All Tests Passed ===\n")


if __name__ == "__main__":
    try:
        test_complete_billing_flow()
    except Exception as e:
        print(f"\n✗ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
