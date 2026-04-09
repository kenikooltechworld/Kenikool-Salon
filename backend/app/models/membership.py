"""Membership models for recurring subscriptions."""

from datetime import datetime
from typing import Optional, List, Dict
from mongoengine import (
    Document, 
    ObjectIdField, 
    StringField, 
    DecimalField,
    IntField,
    BooleanField,
    DateTimeField,
    ListField,
    DictField,
    EmbeddedDocument,
    EmbeddedDocumentField,
)
from bson import ObjectId


class MembershipBenefit(EmbeddedDocument):
    """Embedded document for membership benefits."""
    benefit_type = StringField(required=True)  # "discount", "priority_booking", "exclusive_service", "free_service"
    description = StringField(required=True)
    value = StringField()  # e.g., "20%", "1 free haircut per month"


class MembershipTier(Document):
    """Membership tier/plan definition."""
    tenant_id = ObjectIdField(required=True)
    name = StringField(required=True)  # e.g., "Gold", "Platinum", "VIP"
    description = StringField()
    monthly_price = DecimalField(required=True)
    annual_price = DecimalField()  # Optional discounted annual price
    billing_cycle = StringField(required=True, choices=["monthly", "annual"])
    
    # Benefits
    discount_percentage = IntField(default=0)  # General discount on services
    priority_booking = BooleanField(default=False)
    exclusive_services = ListField(ObjectIdField())  # Service IDs only for members
    free_services_per_month = IntField(default=0)
    rollover_unused = BooleanField(default=False)  # Can unused services rollover?
    
    # Additional benefits
    benefits = ListField(EmbeddedDocumentField(MembershipBenefit))
    
    # Settings
    is_active = BooleanField(default=True)
    max_members = IntField()  # Optional cap on members
    display_order = IntField(default=0)
    
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'membership_tiers',
        'indexes': [
            'tenant_id',
            ('tenant_id', 'is_active'),
            'display_order',
        ]
    }


class Membership(Document):
    """Customer membership subscription."""
    tenant_id = ObjectIdField(required=True)
    customer_id = ObjectIdField(required=True)
    tier_id = ObjectIdField(required=True)
    
    # Subscription details
    status = StringField(
        required=True,
        choices=["active", "paused", "cancelled", "expired"],
        default="active"
    )
    start_date = DateTimeField(required=True)
    end_date = DateTimeField()  # For fixed-term memberships
    next_billing_date = DateTimeField(required=True)
    
    # Payment
    payment_method_id = StringField()  # Tokenized payment method
    last_payment_date = DateTimeField()
    last_payment_amount = DecimalField()
    
    # Usage tracking
    services_used_this_cycle = IntField(default=0)
    services_remaining_this_cycle = IntField(default=0)
    rollover_services = IntField(default=0)
    
    # Cancellation
    cancelled_at = DateTimeField()
    cancellation_reason = StringField()
    cancelled_by = ObjectIdField()  # User ID who cancelled
    
    # Pause
    paused_at = DateTimeField()
    pause_reason = StringField()
    resume_date = DateTimeField()
    
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'memberships',
        'indexes': [
            'tenant_id',
            'customer_id',
            'tier_id',
            ('tenant_id', 'status'),
            ('tenant_id', 'customer_id', 'status'),
            'next_billing_date',
        ]
    }


class MembershipTransaction(Document):
    """Transaction history for membership payments."""
    tenant_id = ObjectIdField(required=True)
    membership_id = ObjectIdField(required=True)
    customer_id = ObjectIdField(required=True)
    
    transaction_type = StringField(
        required=True,
        choices=["payment", "refund", "adjustment"]
    )
    amount = DecimalField(required=True)
    status = StringField(
        required=True,
        choices=["pending", "completed", "failed", "refunded"]
    )
    
    payment_id = ObjectIdField()  # Link to Payment model
    payment_method = StringField()
    
    description = StringField()
    metadata = DictField()
    
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'membership_transactions',
        'indexes': [
            'tenant_id',
            'membership_id',
            'customer_id',
            ('tenant_id', 'created_at'),
        ]
    }
