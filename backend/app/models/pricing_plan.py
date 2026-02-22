"""Pricing plan model for subscription tiers."""

from datetime import datetime
from mongoengine import Document, StringField, IntField, FloatField, DictField, BooleanField, DateTimeField


class PricingPlan(Document):
    """Pricing plan representing a subscription tier."""

    # Basic info
    name = StringField(required=True, unique=True, max_length=50)  # Free, Starter, Professional, etc.
    tier_level = IntField(required=True, unique=True)  # 0=Free, 1=Starter, 2=Professional, 3=Business, 4=Enterprise, 5=Premium
    description = StringField(max_length=500)

    # Pricing
    monthly_price = FloatField(required=True, default=0.0)  # in NGN
    yearly_price = FloatField(required=True, default=0.0)  # in NGN
    currency = StringField(default="NGN")

    # Features & Limits
    features = DictField(default={})
    # Example: {
    #   "max_staff_count": 5,
    #   "has_pos": True,
    #   "has_api_access": False,
    #   "has_advanced_reports": False,
    #   "has_multi_location": False,
    #   "has_white_label": False,
    #   "support_level": "email"
    # }

    # Trial
    trial_days = IntField(default=0)  # 0 = no trial, 30 = 30 day trial
    is_trial_plan = BooleanField(default=False)  # True for Free tier

    # Status
    is_active = BooleanField(default=True)
    is_featured = BooleanField(default=False)  # Show as recommended

    # Metadata
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "pricing_plans",
        "indexes": [
            "tier_level",
            "is_active",
            "created_at",
        ],
    }

    def save(self, *args, **kwargs):
        """Override save to update updated_at timestamp."""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def __str__(self):
        """String representation of pricing plan."""
        return f"PricingPlan({self.name})"

    def __repr__(self):
        """Representation of pricing plan."""
        return f"<PricingPlan id={self.id} name={self.name} tier={self.tier_level}>"
