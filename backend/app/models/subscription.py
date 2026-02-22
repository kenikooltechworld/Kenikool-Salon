"""Subscription model for tenant billing."""

from datetime import datetime, timedelta
from mongoengine import Document, StringField, ObjectIdField, DateTimeField, BooleanField, IntField, FloatField, DictField


class Subscription(Document):
    """Subscription document tracking tenant's current plan and billing."""

    # Relationships
    tenant_id = ObjectIdField(required=True, unique=True)  # One subscription per tenant
    pricing_plan_id = ObjectIdField(required=True)  # Reference to PricingPlan

    # Billing Cycle
    billing_cycle = StringField(choices=["monthly", "yearly"], default="monthly")  # monthly or yearly
    current_period_start = DateTimeField(required=True)
    current_period_end = DateTimeField(required=True)
    next_billing_date = DateTimeField(required=True)

    # Trial
    trial_end = DateTimeField(null=True)  # When trial ends, None if not in trial
    is_trial = BooleanField(default=False)  # Currently in trial period

    # Status
    status = StringField(
        choices=["trial", "active", "past_due", "canceled", "expired"],
        default="trial"
    )
    # trial: In free trial period
    # active: Paid subscription, within billing period
    # past_due: Payment failed, in grace period (3 days)
    # canceled: User canceled subscription
    # expired: Subscription ended, grace period passed

    # Grace Period (for failed payments)
    grace_period_end = DateTimeField(null=True)  # When grace period ends
    is_in_grace_period = BooleanField(default=False)

    # Payment Info
    paystack_subscription_id = StringField(null=True)  # Paystack subscription ID
    paystack_plan_id = StringField(null=True)  # Paystack plan ID
    last_payment_date = DateTimeField(null=True)
    last_payment_amount = FloatField(null=True)
    failed_payment_count = IntField(default=0)

    # Auto-renewal
    auto_renew = BooleanField(default=True)
    renewal_reminders_sent = DictField(default={})  # {"7_days": True, "3_days": True, "expiry": True}

    # Metadata
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    canceled_at = DateTimeField(null=True)

    meta = {
        "collection": "subscriptions",
        "indexes": [
            "tenant_id",
            "status",
            "next_billing_date",
            "current_period_end",
            ("tenant_id", "status"),
        ],
    }

    def save(self, *args, **kwargs):
        """Override save to update updated_at timestamp."""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def is_expired(self):
        """Check if subscription has expired."""
        return datetime.utcnow() > self.current_period_end

    def is_grace_period_expired(self):
        """Check if grace period has expired."""
        if not self.grace_period_end:
            return False
        return datetime.utcnow() > self.grace_period_end

    def days_until_expiry(self):
        """Get days until subscription expires."""
        delta = self.current_period_end - datetime.utcnow()
        return max(0, delta.days)

    def __str__(self):
        """String representation of subscription."""
        return f"Subscription(tenant={self.tenant_id}, status={self.status})"

    def __repr__(self):
        """Representation of subscription."""
        return f"<Subscription id={self.id} tenant={self.tenant_id} status={self.status}>"
