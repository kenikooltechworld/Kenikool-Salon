"""Seed script to create pricing plans in the database."""

import os
import sys
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.db import init_db
from app.models.pricing_plan import PricingPlan


def seed_pricing_plans():
    """Create the 6 pricing tiers."""
    init_db()

    # Define the 6 tiers
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
                "max_customers": 100,
                "max_appointments_per_month": 500,
            },
        },
        {
            "name": "Starter",
            "tier_level": 1,
            "description": "For small salons",
            "monthly_price": 5000.0,  # NGN
            "yearly_price": 50000.0,  # 20% discount
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
                "max_customers": 500,
                "max_appointments_per_month": 2000,
            },
        },
        {
            "name": "Professional",
            "tier_level": 2,
            "description": "For growing businesses",
            "monthly_price": 15000.0,  # NGN
            "yearly_price": 150000.0,  # 20% discount
            "trial_days": 0,
            "is_trial_plan": False,
            "is_featured": True,  # Recommended tier
            "features": {
                "max_staff_count": 15,
                "has_pos": True,
                "has_api_access": True,
                "has_advanced_reports": True,
                "has_multi_location": False,
                "has_white_label": False,
                "support_level": "priority",
                "max_customers": 2000,
                "max_appointments_per_month": 10000,
            },
        },
        {
            "name": "Business",
            "tier_level": 3,
            "description": "For established businesses",
            "monthly_price": 35000.0,  # NGN
            "yearly_price": 350000.0,  # 20% discount
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
                "max_customers": 10000,
                "max_appointments_per_month": 50000,
            },
        },
        {
            "name": "Enterprise",
            "tier_level": 4,
            "description": "For large operations",
            "monthly_price": 75000.0,  # NGN
            "yearly_price": 750000.0,  # 20% discount
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
                "max_customers": 50000,
                "max_appointments_per_month": 200000,
            },
        },
        {
            "name": "Premium",
            "tier_level": 5,
            "description": "Top tier with all features",
            "monthly_price": 150000.0,  # NGN
            "yearly_price": 1500000.0,  # 20% discount
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
                "max_customers": 100000,
                "max_appointments_per_month": 500000,
            },
        },
    ]

    # Create or update plans
    for plan_data in plans:
        existing = PricingPlan.objects(tier_level=plan_data["tier_level"]).first()
        if existing:
            # Update existing plan
            for key, value in plan_data.items():
                setattr(existing, key, value)
            existing.save()
            print(f"✓ Updated plan: {plan_data['name']}")
        else:
            # Create new plan
            plan = PricingPlan(**plan_data)
            plan.save()
            print(f"✓ Created plan: {plan_data['name']}")

    print("\n✅ Pricing plans seeded successfully!")


if __name__ == "__main__":
    seed_pricing_plans()
