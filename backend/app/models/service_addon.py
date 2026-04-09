"""Service Add-on Model"""
from datetime import datetime
from typing import List, Optional
from bson import ObjectId, Decimal128
from mongoengine import Document, fields
from pymongo import IndexModel


class ServiceAddon(Document):
    """Service add-on model for upsells and enhancements"""
    
    tenant_id = fields.ObjectIdField(required=True)
    name = fields.StringField(required=True, max_length=200)
    description = fields.StringField(required=True)
    price = fields.DecimalField(required=True, precision=2)
    duration_minutes = fields.IntField(required=True, min_value=0)
    image_url = fields.StringField()
    is_active = fields.BooleanField(default=True)
    applicable_services = fields.ListField(fields.ObjectIdField())
    category = fields.StringField(required=True, choices=["product", "upgrade", "treatment"])
    display_order = fields.IntField(default=0)
    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)
    
    meta = {
        "collection": "service_addons",
        "indexes": [
            {"fields": ["tenant_id", "is_active"]},
            {"fields": ["applicable_services"]},
            {"fields": ["tenant_id", "display_order"]},
        ]
    }
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "name": self.name,
            "description": self.description,
            "price": float(self.price),
            "duration_minutes": self.duration_minutes,
            "image_url": self.image_url,
            "is_active": self.is_active,
            "applicable_services": [str(sid) for sid in self.applicable_services],
            "category": self.category,
            "display_order": self.display_order,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
