#!/usr/bin/env python
"""Test script to verify subscription endpoint works."""

import os
import sys
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.db import init_db
from app.models.pricing_plan import PricingPlan
from app.models.subscription import Subscription
from app.models.tenant import Tenant
from bson import ObjectId

def seed_pricing_plans():
    """Create the 6 pricing tiers."""
    print("Seeding pricing plans...")
    
    plans = [
        {
            "name": "Free",
            "tier_level": 0,
            "description": "Perfect for getting started",
            "monthly_price": 0.0,
            "yearly_price": 0.0,
            "trial_days": 30,
            "is_trial_plan": True,
            "is_featured": False,
            "features": {
                "max_staff_count": 1,
                "has_pos": False,
                "has_api_access": False,
                "has_advanced_reports": False,
                "has_multi_location": False,
                "has_white_label": False,
                "support_level": "email",
            },
        },
        {
            "name": "Starter",
            "tier_level": 1,
            "description": "For small salons",
            "monthly_price": 5000.0,
            "yearly_price": 50000.0,
            "trial_days": 0,
            "is_trial_plan": False,
            "is_featured": False,
            "features": {
                "max_staff_count": 5,
                "has_pos": True,
                "has_api_access": False,
                "has_advanced_reports": False,
                "has_multi_location": False,
                "has_white_label": False,
                "support_level": "email",
            },
        },
        {
            "name": "Professional",
            "tier_level": 2,
            "description": "For growing businesses",
            "monthly_price": 15000.0,
            "yearly_price": 150000.0,
            "trial_days": 0,
            "is_trial_plan": False,
            "is_featured": True,
            "features": {
                "max_staff_count": 15,
                "has_pos": True,
                "has_api_access": True,
                "has_advanced_reports": True,
                "has_multi_location": False,
                "has_white_label": False,
                "support_level": "priority",
            },
        },
        {
            "name": "Business",
            "tier_level": 3,
            "description": "For established businesses",
            "monthly_price": 35000.0,
            "yearly_price": 350000.0,
            "trial_days": 0,
            "is_trial_plan": False,
            "is_featured": False,
            "features": {
                "max_staff_count": 50,
                "has_pos": True,
                "has_api_access": True,
                "has_advanced_reports": True,
                "has_multi_location": True,
                "has_white_label": False,
                "support_level": "priority",
            },
        },
        {
            "name": "Enterprise",
            "tier_level": 4,
            "description": "For large operations",
            "monthly_price": 75000.0,
            "yearly_price": 750000.0,
            "trial_days": 0,
            "is_trial_plan": False,
            "is_featured": False,
            "features": {
                "max_staff_count": 200,
                "has_pos": True,
                "has_api_access": True,
                "has_advanced_reports": True,
                "has_multi_location": True,
                "has_white_label": True,
                "support_level": "dedicated",
            },
        },
        {
            "name": "Premium",
            "tier_level": 5,
            "description": "Top tier with all features",
            "monthly_price": 150000.0,
            "yearly_price": 1500000.0,
            "trial_days": 0,
            "is_trial_plan": False,
            "is_featured": False,
            "features": {
                "max_staff_count": 500,
                "has_pos": True,
                "has_api_access": True,
                "has_advanced_reports": True,
                "has_multi_location": True,
                "has_white_label": True,
                "support_level": "dedicated",
            },
        },
    ]

    for plan_data in plans:
        existing = PricingPlan.objects(tier_level=plan_data["tier_level"]).first()
        if existing:
            for key, value in plan_data.items():
                setattr(existing, key, value)
            existing.save()
            print(f"✓ Updated plan: {plan_data['name']}")
        else:
            plan = PricingPlan(**plan_data)
            plan.save()
            print(f"✓ Created plan: {plan_data['name']}")

    print("✅ Pricing plans seeded successfully!\n")


def test_subscription_for_tenant():
    """Test creating a subscription for a test tenant."""
    print("Testing subscription creation...")
    
    # Find a test tenant
    tenant = Tenant.objects().first()
    if not tenant:
        print("❌ No tenant found in database")
        return
    
    print(f"Found tenant: {tenant.name} (ID: {tenant.id})")
    
    # Check if subscription exists
    subscription = Subscription.objects(tenant_id=tenant.id).first()
    if subscription:
        print(f"✓ Subscription already exists for tenant")
        print(f"  - Status: {subscription.status}")
        print(f"  - Plan: {subscription.pricing_plan_id}")
        print(f"  - Is Trial: {subscription.is_trial}")
        print(f"  - Days Until Expiry: {subscription.days_until_expiry()}")
    else:
        print("❌ No subscription found for tenant")
        print("Creating trial subscription...")
        
        from app.services.subscription_service import SubscriptionService
        try:
            sub = SubscriptionService.create_trial_subscription(str(tenant.id), trial_days=30)
            print(f"✓ Trial subscription created!")
            print(f"  - Status: {sub.status}")
            print(f"  - Is Trial: {sub.is_trial}")
            print(f"  - Days Until Expiry: {sub.days_until_expiry()}")
        except Exception as e:
            print(f"❌ Error creating subscription: {str(e)}")


if __name__ == "__main__":
    init_db()
    seed_pricing_plans()
    test_subscription_for_tenant()
