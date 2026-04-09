"""Video testimonial model for social proof"""

from datetime import datetime
from mongoengine import Document, StringField, DateTimeField, BooleanField, IntField, ObjectIdField
from bson import ObjectId


class VideoTestimonial(Document):
    """Video testimonial for social proof"""
    
    meta = {
        'collection': 'video_testimonials',
        'indexes': [
            'tenant_id',
            'is_active',
            '-created_at',
        ]
    }
    
    tenant_id = ObjectIdField(required=True)
    customer_name = StringField(required=True, max_length=200)
    video_url = StringField(required=True, max_length=500)
    thumbnail_url = StringField(max_length=500)
    testimonial_text = StringField(max_length=1000)
    rating = IntField(min_value=1, max_value=5, default=5)
    is_active = BooleanField(default=True)
    display_order = IntField(default=0)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "customer_name": self.customer_name,
            "video_url": self.video_url,
            "thumbnail_url": self.thumbnail_url,
            "testimonial_text": self.testimonial_text,
            "rating": self.rating,
            "is_active": self.is_active,
            "display_order": self.display_order,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
