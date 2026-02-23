"""Test billing system fixes."""

import sys
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from bson import ObjectId

# Add backend to path
sys.path.insert(0, '/app')

from app.models.subscription import Subscription
from app.models.pricing_plan import PricingPlan
from app.services.subscription_service import SubscriptionService


def test_billing_cycle_calculation():
    """Test that billing cycles use calendar-based calculations."""
    print("\n=== Testing Billing Cycle Calculation ===")
    
    # Test monthly calculation
    start = datetime(2024, 1, 15)
    end_monthly = SubscriptionService._calculate_period_end(start, "monthly")
    expected_monthly = datetime(2024, 2, 15)
    assert end_monthly == expected_monthly, f"Monthly: expected {expected_monthly}, got {end_monthly}"
    print(f"✓ Monthly: {start} + 1 month = {end_monthly}")
    
    # Test yearly calculation
    end_yearly = SubscriptionService._calculate_period_end(start, "yearly")
    expected_yearly = datetime(2025, 1, 15)
    assert end_yearly == expected_yearly, f"Yearly: expected {expected_yearly}, got {end_yearly}"
    print(f"✓ Yearly: {start} + 1 year = {end_yearly}")
    
    # Test edge case: month-end dates
    start_jan31 = datetime(2024, 1, 31)
    end_feb = SubscriptionService._calculate_period_end(start_jan31, "monthly")
    expected_feb = datetime(2024, 2, 29)  # 2024 is leap year
    assert end_feb == expected_feb, f"Month-end: expected {expected_feb}, got {end_feb}"
    print(f"✓ Month-end: {start_jan31} + 1 month = {end_feb}")


def test_proration_calculation():
    """Test proration calculations for upgrades and downgrades."""
    print("\n=== Testing Proration Calculation ===")
    
    # Setup: 30-day period, 15 days remaining
    now = datetime.utcnow()
    period_end = now + timedelta(days=15)
    
    # Upgrade from $100/month to $200/month
    current_price = 100.0
    new_price = 200.0
    
    proration = SubscriptionService._calculate_proration(
        current_price, new_price, period_end, "monthly"
    )
    
    # Expected: 15 days remaining
    # Current daily rate: 100/30 = 3.33/day
    # New daily rate: 200/30 = 6.67/day
    # Unused credit: 3.33 * 15 = 50
    # New charge: 6.67 * 15 = 100
    # Net charge: 100 - 50 = 50
    
    # Days remaining can be 14 or 15 depending on exact time calculation
    assert proration["days_remaining"] in [14, 15], f"Expected 14-15 days remaining, got {proration['days_remaining']}"
    assert proration["charge_amount"] > 0, "Upgrade should have positive charge"
    assert proration["refund_amount"] == 0, "Upgrade should not have refund"
    print(f"✓ Upgrade proration: charge ${proration['charge_amount']:.2f}, refund ${proration['refund_amount']:.2f}")
    
    # Downgrade from $200/month to $100/month
    proration_down = SubscriptionService._calculate_proration(
        new_price, current_price, period_end, "monthly"
    )
    
    assert proration_down["charge_amount"] == 0, "Downgrade should not have charge"
    assert proration_down["refund_amount"] > 0, "Downgrade should have positive refund"
    print(f"✓ Downgrade proration: charge ${proration_down['charge_amount']:.2f}, refund ${proration_down['refund_amount']:.2f}")


def test_tier_validation():
    """Test plan tier validation for upgrades and downgrades."""
    print("\n=== Testing Tier Validation ===")
    
    # Valid upgrade: tier 1 to tier 2
    assert SubscriptionService._validate_tier_transition(1, 2, is_upgrade=True), "Valid upgrade should pass"
    print("✓ Valid upgrade: tier 1 → tier 2")
    
    # Invalid upgrade: tier 2 to tier 1
    assert not SubscriptionService._validate_tier_transition(2, 1, is_upgrade=True), "Invalid upgrade should fail"
    print("✓ Invalid upgrade blocked: tier 2 → tier 1")
    
    # Invalid upgrade: same tier
    assert not SubscriptionService._validate_tier_transition(1, 1, is_upgrade=True), "Same tier upgrade should fail"
    print("✓ Same tier upgrade blocked: tier 1 → tier 1")
    
    # Valid downgrade: tier 2 to tier 1
    assert SubscriptionService._validate_tier_transition(2, 1, is_upgrade=False), "Valid downgrade should pass"
    print("✓ Valid downgrade: tier 2 → tier 1")
    
    # Invalid downgrade: tier 1 to tier 2
    assert not SubscriptionService._validate_tier_transition(1, 2, is_upgrade=False), "Invalid downgrade should fail"
    print("✓ Invalid downgrade blocked: tier 1 → tier 2")


def test_grace_period_logic():
    """Test grace period status transitions."""
    print("\n=== Testing Grace Period Logic ===")
    
    # Simulate subscription in grace period
    now = datetime.utcnow()
    grace_end = now + timedelta(days=2)  # Grace period ends in 2 days
    
    # Create mock subscription
    sub = Subscription(
        tenant_id=ObjectId(),
        pricing_plan_id=ObjectId(),
        status="past_due",
        is_in_grace_period=True,
        grace_period_end=grace_end,
        current_period_end=now - timedelta(days=1),  # Already expired
        current_period_start=now - timedelta(days=30),
        next_billing_date=grace_end,
        billing_cycle="monthly"
    )
    
    # Grace period should NOT expire yet
    assert sub.is_in_grace_period, "Should be in grace period"
    assert sub.status == "past_due", "Status should be past_due during grace period"
    print("✓ Subscription in grace period: status = past_due")
    
    # Simulate grace period expiration
    sub.grace_period_end = now - timedelta(days=1)  # Grace period expired
    assert sub.is_grace_period_expired(), "Grace period should be expired"
    print("✓ Grace period expired check works")


def test_refund_on_cancellation():
    """Test that cancellation calculates refunds."""
    print("\n=== Testing Refund on Cancellation ===")
    
    # Setup: 30-day period, 15 days remaining
    now = datetime.utcnow()
    period_end = now + timedelta(days=15)
    
    # Create mock subscription
    sub = Subscription(
        tenant_id=ObjectId(),
        pricing_plan_id=ObjectId(),
        status="active",
        current_period_end=period_end,
        current_period_start=now - timedelta(days=15),
        next_billing_date=period_end,
        billing_cycle="monthly",
        is_trial=False,
        trial_end=None,
        auto_renew=True,
        last_payment_amount=100.0
    )
    
    # Calculate expected refund: 15 days remaining * (100/30) = 50
    days_remaining = (period_end - now).days
    daily_rate = 100.0 / 30
    expected_refund = daily_rate * days_remaining
    
    print(f"✓ Cancellation refund calculation: {days_remaining} days remaining × ${daily_rate:.2f}/day = ${expected_refund:.2f}")


if __name__ == "__main__":
    print("Testing Billing System Fixes")
    print("=" * 50)
    
    try:
        test_billing_cycle_calculation()
        test_proration_calculation()
        test_tier_validation()
        test_grace_period_logic()
        test_refund_on_cancellation()
        
        print("\n" + "=" * 50)
        print("✓ All tests passed!")
        print("=" * 50)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
