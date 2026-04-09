"""Gift card models"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from bson import ObjectId, Decimal128
from mongoengine import (
    Document,
    ObjectIdField,
    StringField,
    DecimalField,
    DateTimeField,
    BooleanField,
    ListField,
)


class GiftCard(Document):
    """Gift card model"""
    tenant_id = ObjectIdField(required=True)
    code = StringField(required=True)  # Unique gift card code (e.g., "GC-XXXX-XXXX-XXXX")
    initial_amount = DecimalField(required=True, precision=2)
    current_balance = DecimalField(required=True, precision=2)
    currency = StringField(default="NGN")
    
    # Purchase information
    purchased_by_name = StringField()
    purchased_by_email = StringField()
    purchased_by_phone = StringField()
    purchase_date = DateTimeField(required=True)
    
    # Recipient information
    recipient_name = StringField()
    recipient_email = StringField()
    recipient_phone = StringField()
    
    # Status and validity
    status = StringField(required=True)  # "active", "redeemed", "expired", "cancelled"
    expiry_date = DateTimeField()
    is_active = BooleanField(default=True)
    
    # Delivery
    delivery_method = StringField(required=True)  # "email", "sms", "both"
    delivery_date = DateTimeField()  # For scheduled delivery
    is_delivered = BooleanField(default=False)
    delivered_at = DateTimeField()
    
    # Message
    personal_message = StringField()
    
    # Restrictions
    min_purchase_amount = DecimalField(precision=2)  # Minimum booking amount to use card
    applicable_services = ListField(ObjectIdField(), default=list)  # Empty = all services
    
    # Metadata
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        "collection": "gift_cards",
        "indexes": [
            {"fields": ["tenant_id", "code"], "unique": True},
            {"fields": ["tenant_id", "status"]},
            {"fields": ["tenant_id", "recipient_email"]},
            {"fields": ["expiry_date"]},
            {"fields": ["code"]},
        ]
    }


class GiftCardTransaction(Document):
    """Gift card transaction history"""
    tenant_id = ObjectIdField(required=True)
    gift_card_id = ObjectIdField(required=True)
    gift_card_code = StringField(required=True)
    
    transaction_type = StringField(required=True)  # "purchase", "redemption", "refund", "adjustment"
    amount = DecimalField(required=True, precision=2)
    balance_before = DecimalField(required=True, precision=2)
    balance_after = DecimalField(required=True, precision=2)
    
    # Related entities
    booking_id = ObjectIdField()  # If redeemed for a booking
    payment_id = ObjectIdField()  # If purchased with payment
    
    # Transaction details
    description = StringField(required=True)
    performed_by = StringField()  # User/customer who performed action
    
    # Metadata
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        "collection": "gift_card_transactions",
        "indexes": [
            {"fields": ["tenant_id", "gift_card_id"]},
            {"fields": ["tenant_id", "booking_id"]},
            {"fields": ["-created_at"]},
        ]
    }
