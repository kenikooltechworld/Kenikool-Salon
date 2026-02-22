"""Resource model for managing physical resources."""

from datetime import datetime, time
from mongoengine import (
    StringField,
    DateTimeField,
    BooleanField,
    IntField,
    ListField,
    DictField,
    DecimalField,
    ObjectIdField,
)
from app.models.base import BaseDocument


class Resource(BaseDocument):
    """Resource document model for tracking physical assets."""

    RESOURCE_TYPES = ["room", "chair", "equipment", "tool", "supply"]
    STATUSES = ["active", "inactive", "maintenance"]

    name = StringField(required=True, max_length=255)
    type = StringField(choices=RESOURCE_TYPES, required=True)
    description = StringField(null=True)
    location_id = ObjectIdField(null=True)  # Reference to location

    # Capacity and quantity
    quantity = IntField(default=1, min_value=1)  # Total quantity available
    available_quantity = IntField(default=1, min_value=0)  # Currently available

    # Status and maintenance
    status = StringField(choices=STATUSES, default="active")
    is_active = BooleanField(default=True)

    # Financial tracking
    purchase_date = DateTimeField(null=True)
    purchase_price = DecimalField(null=True, precision=2)
    depreciation_value = DecimalField(null=True, precision=2)
    maintenance_cost = DecimalField(default=0, precision=2)

    # Availability schedule
    availability_schedule = ListField(DictField(), default=[])  # List of availability windows

    # Resource dependencies (other resources required for this resource)
    required_resources = ListField(ObjectIdField(), default=[])

    # Metadata
    tags = ListField(StringField(), default=[])
    notes = StringField(null=True)

    meta = {
        "collection": "resources",
        "indexes": [
            ("tenant_id", "name"),
            ("tenant_id", "type"),
            ("tenant_id", "status"),
            ("tenant_id", "location_id"),
            ("tenant_id", "is_active"),
            ("tenant_id", "-created_at"),
        ],
    }

    def __str__(self):
        """Return resource string representation."""
        return f"{self.name} ({self.type}) - {self.status}"

    def is_available(self) -> bool:
        """Check if resource is available."""
        return self.status == "active" and self.is_active and self.available_quantity > 0

    def reserve(self, quantity: int = 1) -> bool:
        """Reserve resource quantity."""
        if self.available_quantity >= quantity:
            self.available_quantity -= quantity
            self.save()
            return True
        return False

    def release(self, quantity: int = 1):
        """Release reserved resource quantity."""
        self.available_quantity = min(self.available_quantity + quantity, self.quantity)
        self.save()

    def mark_maintenance(self):
        """Mark resource as under maintenance."""
        self.status = "maintenance"
        self.save()

    def mark_active(self):
        """Mark resource as active."""
        self.status = "active"
        self.save()

    def mark_inactive(self):
        """Mark resource as inactive."""
        self.status = "inactive"
        self.save()


class ResourceAvailability(BaseDocument):
    """Resource availability schedule model."""

    DAYS_OF_WEEK = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

    resource_id = ObjectIdField(required=True)
    day_of_week = StringField(choices=DAYS_OF_WEEK, null=True)  # For recurring availability
    start_time = StringField(required=True)  # Store as HH:MM format
    end_time = StringField(required=True)  # Store as HH:MM format

    # For non-recurring availability
    is_recurring = BooleanField(default=True)
    effective_from = DateTimeField(null=True)
    effective_to = DateTimeField(null=True)

    is_active = BooleanField(default=True)

    meta = {
        "collection": "resource_availability",
        "indexes": [
            ("tenant_id", "resource_id"),
            ("tenant_id", "resource_id", "day_of_week"),
            ("tenant_id", "is_active"),
        ],
    }

    def __str__(self):
        """Return availability string representation."""
        if self.is_recurring:
            return f"{self.day_of_week} {self.start_time} - {self.end_time}"
        else:
            return f"{self.effective_from} - {self.effective_to}"


class ResourceAssignment(BaseDocument):
    """Resource assignment to appointments model."""

    appointment_id = ObjectIdField(required=True)
    resource_id = ObjectIdField(required=True)
    quantity_used = IntField(default=1, min_value=1)

    # Assignment status
    status = StringField(
        choices=["assigned", "in_use", "released", "cancelled"], default="assigned"
    )
    assigned_at = DateTimeField(default=datetime.utcnow)
    released_at = DateTimeField(null=True)

    meta = {
        "collection": "resource_assignments",
        "indexes": [
            ("tenant_id", "appointment_id"),
            ("tenant_id", "resource_id"),
            ("tenant_id", "status"),
            ("tenant_id", "-assigned_at"),
        ],
    }

    def __str__(self):
        """Return assignment string representation."""
        return f"Resource {self.resource_id} assigned to appointment {self.appointment_id}"

    def release(self):
        """Release resource assignment."""
        self.status = "released"
        self.released_at = datetime.utcnow()
        self.save()


class ResourceUtilization(BaseDocument):
    """Resource utilization tracking model."""

    resource_id = ObjectIdField(required=True)
    date = DateTimeField(required=True)
    usage_hours = DecimalField(default=0, precision=2)
    utilization_percent = DecimalField(default=0, precision=2)
    total_available_hours = DecimalField(default=24, precision=2)

    meta = {
        "collection": "resource_utilization",
        "indexes": [
            ("tenant_id", "resource_id", "date"),
            ("tenant_id", "resource_id", "-date"),
        ],
    }

    def __str__(self):
        """Return utilization string representation."""
        return f"Resource {self.resource_id} - {self.utilization_percent}% utilized on {self.date}"


class ResourceMaintenance(BaseDocument):
    """Resource maintenance scheduling model."""

    resource_id = ObjectIdField(required=True)
    maintenance_type = StringField(required=True)  # e.g., "cleaning", "repair", "inspection"
    description = StringField(null=True)

    scheduled_date = DateTimeField(required=True)
    completed_date = DateTimeField(null=True)
    estimated_duration_hours = IntField(null=True)

    status = StringField(
        choices=["scheduled", "in_progress", "completed", "cancelled"], default="scheduled"
    )
    notes = StringField(null=True)
    cost = DecimalField(null=True, precision=2)

    meta = {
        "collection": "resource_maintenance",
        "indexes": [
            ("tenant_id", "resource_id"),
            ("tenant_id", "status"),
            ("tenant_id", "scheduled_date"),
            ("tenant_id", "-scheduled_date"),
        ],
    }

    def __str__(self):
        """Return maintenance string representation."""
        return f"{self.maintenance_type} for resource {self.resource_id} on {self.scheduled_date}"

    def mark_completed(self):
        """Mark maintenance as completed."""
        self.status = "completed"
        self.completed_date = datetime.utcnow()
        self.save()

    def mark_in_progress(self):
        """Mark maintenance as in progress."""
        self.status = "in_progress"
        self.save()

    def mark_cancelled(self):
        """Mark maintenance as cancelled."""
        self.status = "cancelled"
        self.save()
