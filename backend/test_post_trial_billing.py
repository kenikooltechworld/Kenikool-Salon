"""Test post-trial billing model implementation."""

import sys
from datetime import datetime, timedelta
from decimal import Decimal
from bson import ObjectId

# Add backend to path
sys.path.insert(0, '/app/backend')

from app.models.subscription import Subscription
from app.models.pricing_plan import PricingPlan
from app.models.transaction import Transaction, TransactionItem
from app.services.subscription_service import SubscriptionService
from app.services.transaction_service import TransactionService


def test_trial_expiry_flow():
    """Test the complete trial expiry flow."""
    print("\n=== Testing Trial Expiry Flow ===\n")
    
    # Create test tenant ID
    tenant_id = str(ObjectId())
    print(f"Test Tenant ID: {tenant_id}")
    
    # 1. Create trial subscription
    print("\n1. Creating trial subscription...")
    try:
        sub = SubscriptionService.create_trial_subscription(tenant_id, trial_days=30)
        print(f"✓ Trial subscription created")
        print(f"  - Status: {sub.subscription_status}")
        print(f"  - Trial End: {sub.trial_end}")
        print(f"  - Transaction Fee: {sub.transaction_fee_percentage}%")
        assert sub.subscription_status == "trial"
        assert sub.transaction_fee_percentage == 0.0
        assert sub.trial_expiry_action_required == False
    except Exception as e:
        print(f"✗ Failed to create trial subscription: {e}")
        return False
    
    # 2. Handle trial expiry
    print("\n2. Handling trial expiry...")
    try:
        sub = SubscriptionService.handle_trial_expiry(tenant_id)
        print(f"✓ Trial expiry handled")
        print(f"  - Status: {sub.subscription_status}")
        print(f"  - Action Required: {sub.trial_expiry_action_required}")
        assert sub.subscription_status == "expired_trial"
        assert sub.trial_expiry_action_required == True
    except Exception as e:
        print(f"✗ Failed to handle trial expiry: {e}")
        return False
    
    # 3. Continue free with fee
    print("\n3. Continuing on free tier with 10% fee...")
    try:
        sub = SubscriptionService.continue_free_with_fee(tenant_id)
        print(f"✓ Continued on free tier")
        print(f"  - Status: {sub.subscription_status}")
        print(f"  - Transaction Fee: {sub.transaction_fee_percentage}%")
        print(f"  - Action Required: {sub.trial_expiry_action_required}")
        assert sub.subscription_status == "free_with_fee"
        assert sub.transaction_fee_percentage == 10.0
        assert sub.trial_expiry_action_required == False
    except Exception as e:
        print(f"✗ Failed to continue free with fee: {e}")
        return False
    
    # 4. Test transaction fee calculation
    print("\n4. Testing transaction fee calculation...")
    try:
        # Create a test transaction with fee
        customer_id = ObjectId()
        staff_id = ObjectId()
        
        items_data = [
            {
                "item_type": "service",
                "item_id": str(ObjectId()),
                "item_name": "Haircut",
                "quantity": 1,
                "unit_price": 100.0,
                "tax_rate": 0,
                "discount_rate": 0,
            }
        ]
        
        transaction = TransactionService.create_transaction(
            tenant_id=ObjectId(tenant_id),
            customer_id=customer_id,
            staff_id=staff_id,
            items_data=items_data,
            payment_method="cash",
        )
        
        print(f"✓ Transaction created with fee")
        print(f"  - Subtotal: {transaction.subtotal}")
        print(f"  - Transaction Fee: {transaction.transaction_fee}")
        print(f"  - Total: {transaction.total}")
        
        # Verify fee was applied (10% of total)
        expected_fee = Decimal("100") * Decimal("0.10")
        assert transaction.transaction_fee == expected_fee, f"Expected fee {expected_fee}, got {transaction.transaction_fee}"
        assert transaction.total == Decimal("110"), f"Expected total 110, got {transaction.total}"
        
    except Exception as e:
        print(f"✗ Failed to create transaction with fee: {e}")
        return False
    
    # 5. Test upgrade from expired trial
    print("\n5. Testing upgrade from expired trial...")
    try:
        # Get a paid plan
        paid_plan = PricingPlan.objects(tier_level__gt=0).first()
        if not paid_plan:
            print("⚠ No paid plan found, skipping upgrade test")
        else:
            sub = SubscriptionService.upgrade_from_expired_trial(
                tenant_id=tenant_id,
                new_plan_id=str(paid_plan.id),
                billing_cycle="monthly",
            )
            print(f"✓ Upgraded from expired trial")
            print(f"  - Status: {sub.subscription_status}")
            print(f"  - Transaction Fee: {sub.transaction_fee_percentage}%")
            assert sub.subscription_status == "active"
            assert sub.transaction_fee_percentage == 0.0
    except Exception as e:
        print(f"✗ Failed to upgrade from expired trial: {e}")
        return False
    
    print("\n=== All Tests Passed! ===\n")
    return True


if __name__ == "__main__":
    success = test_trial_expiry_flow()
    sys.exit(0 if success else 1)
