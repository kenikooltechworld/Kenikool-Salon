"""Customer recommendation models for personalized service suggestions"""
from datetime import datetime
from typing import Optional, List, Dict
from mongoengine import (
    Document,
    ObjectIdField,
    StringField,
    FloatField,
    IntField,
    BooleanField,
    DateTimeField,
    ListField,
)
from bson import ObjectId


class CustomerPreference(Document):
    """Customer preference tracking for recommendations"""
    tenant_id = ObjectIdField(required=True)
    customer_id = ObjectIdField(required=True)
    
    # Service preferences
    preferred_service_categories = ListField(StringField(), default=list)
    preferred_services = ListField(ObjectIdField(), default=list)
    preferred_staff = ListField(ObjectIdField(), default=list)
    preferred_time_slots = ListField(StringField(), default=list)  # e.g., ["morning", "afternoon", "evening"]
    preferred_days = ListField(StringField(), default=list)  # e.g., ["monday", "friday"]
    
    # Behavioral data
    average_booking_frequency_days = IntField()
    average_spend = FloatField()
    last_booking_date = DateTimeField()
    total_bookings = IntField(default=0)
    
    # Explicit preferences
    avoid_services = ListField(ObjectIdField(), default=list)
    avoid_staff = ListField(ObjectIdField(), default=list)
    
    # Metadata
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        "collection": "customer_preferences",
        "indexes": [
            "tenant_id",
            "customer_id",
            {"fields": ["tenant_id", "customer_id"]},
        ]
    }


class BookingRecommendation(Document):
    """Generated recommendations for customers"""
    tenant_id = ObjectIdField(required=True)
    customer_id = ObjectIdField(required=True)
    
    # Recommendation details
    recommended_service_id = ObjectIdField(required=True)
    recommended_staff_id = ObjectIdField()
    
    # Scoring
    confidence_score = FloatField(required=True)  # 0.0 to 1.0
    recommendation_type = StringField(required=True)  # "collaborative", "content_based", "popular", "seasonal"
    reasoning = StringField(required=True)  # Human-readable explanation
    
    # Metadata
    generated_at = DateTimeField(default=datetime.utcnow)
    expires_at = DateTimeField(required=True)  # Recommendations expire after some time
    shown_to_customer = BooleanField(default=False)
    clicked = BooleanField(default=False)
    booked = BooleanField(default=False)
    
    meta = {
        "collection": "booking_recommendations",
        "indexes": [
            "tenant_id",
            "customer_id",
            {"fields": ["tenant_id", "customer_id"]},
            {"fields": ["expires_at"]},  # For cleanup
        ]
    }
