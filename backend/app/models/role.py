"""Role and Permission models for RBAC."""

from datetime import datetime
from mongoengine import StringField, BooleanField, DateTimeField, ListField, ObjectIdField
from app.models.base import BaseDocument


class Permission(BaseDocument):
    """Permission document model."""

    resource = StringField(required=True, max_length=100)
    action = StringField(
        choices=["view", "create", "edit", "delete", "export"], required=True
    )
    description = StringField(max_length=500)

    meta = {
        "collection": "permissions",
        "indexes": [
            ("tenant_id", "resource", "action"),
        ],
    }

    def __str__(self):
        """Return permission string representation."""
        return f"{self.resource}:{self.action}"


class Role(BaseDocument):
    """Role document model with permissions."""

    name = StringField(required=True, max_length=100)
    description = StringField(max_length=500)
    is_custom = BooleanField(default=False)
    permissions = ListField(ObjectIdField(), default=[])

    meta = {
        "collection": "roles",
        "indexes": [
            ("tenant_id", "name"),
            ("tenant_id", "is_custom"),
        ],
    }

    def __str__(self):
        """Return role string representation."""
        return self.name
