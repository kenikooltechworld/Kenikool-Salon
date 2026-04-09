from datetime import datetime
from typing import List, Optional
from mongoengine import (
    Document,
    ObjectIdField,
    StringField,
    FloatField,
    IntField,
    BooleanField,
    DateTimeField,
    ListField,
    DictField,
)
from bson import ObjectId


class ServicePackage(Document):
    """
    Service Package Model
    Bundles multiple services at a discounted price
    """
    tenant_id = ObjectIdField(required=True)
    
    # Package details
    name = StringField(required=True, min_length=1, max_length=200)
    description = StringField(max_length=1000)
    
    # Services included (list of service IDs with quantities)
    services = ListField(DictField(), default=list)  # [{"service_id": "...", "quantity": 1}]
    
    # Pricing
    original_price = FloatField(required=True, min_value=0)  # Sum of individual service prices
    package_price = FloatField(required=True, min_value=0)  # Discounted package price
    discount_amount = FloatField(required=True, min_value=0)  # original_price - package_price
    discount_percentage = FloatField(required=True, min_value=0, max_value=100)  # (discount_amount / original_price) * 100
    
    # Validity
    valid_from = DateTimeField()
    valid_until = DateTimeField()
    
    # Availability
    is_active = BooleanField(default=True)
    max_bookings_per_customer = IntField(min_value=1)  # Limit per customer
    total_bookings_limit = IntField(min_value=1)  # Total limit across all customers
    current_bookings_count = IntField(default=0, min_value=0)
    
    # Display
    image_url = StringField()
    display_order = IntField(default=0)
    is_featured = BooleanField(default=False)
    
    # Metadata
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    created_by = ObjectIdField()
    updated_by = ObjectIdField()
    
    meta = {
        "collection": "service_packages",
        "indexes": [
            "tenant_id",
            "is_active",
            "is_featured",
            "valid_from",
            "valid_until",
        ]
    }
    
    def is_valid(self) -> bool:
        """Check if package is currently valid"""
        now = datetime.utcnow()
        
        if not self.is_active:
            return False
        
        if self.valid_from and now < self.valid_from:
            return False
        
        if self.valid_until and now > self.valid_until:
            return False
        
        if self.total_bookings_limit and self.current_bookings_count >= self.total_bookings_limit:
            return False
        
        return True
    
    def calculate_savings(self) -> dict:
        """Calculate savings information"""
        return {
            "original_price": self.original_price,
            "package_price": self.package_price,
            "discount_amount": self.discount_amount,
            "discount_percentage": self.discount_percentage,
            "you_save": self.discount_amount,
        }
