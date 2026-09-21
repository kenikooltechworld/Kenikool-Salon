"""Goal model for staff performance targets and incentives."""
from datetime import datetime
from mongoengine import (
    StringField, ObjectIdField, FloatField, IntField, BooleanField, DictField,
    DateTimeField,
)
from app.models.base import BaseDocument


class Goal(BaseDocument):
    """Performance goal or target for a staff member."""

    staff_id = ObjectIdField(required=True)
    tenant_id = ObjectIdField(required=True)

    goal_type = StringField(
        required=True,
        choices=["sales", "commission", "appointments", "customer_satisfaction"],
    )
    target_value = FloatField(required=True, min_value=0)
    current_value = FloatField(default=0)

    period_start = DateTimeField(required=True)
    period_end = DateTimeField(required=True)

    status = StringField(
        required=True,
        choices=["active", "completed", "expired"],
        default="active",
    )

    is_active = BooleanField(default=True)

    meta = {
        "collection": "goals",
        "indexes": [
            ("tenant_id", "staff_id"),
            ("tenant_id", "staff_id", "status"),
            ("tenant_id", "goal_type"),
            ("tenant_id", "period_start"),
            ("tenant_id", "period_end"),
        ],
    }

    def __str__(self):
        return f"Goal(staff={self.staff_id}, type={self.goal_type}, status={self.status})"


class GoalAchievement(BaseDocument):
    """Record of a staff member achieving a goal."""

    goal_id = ObjectIdField(required=True)
    staff_id = ObjectIdField(required=True)
    tenant_id = ObjectIdField(required=True)

    achieved_at = DateTimeField(default=datetime.utcnow, required=True)
    target_value = FloatField(required=True)
    achieved_value = FloatField(required=True)
    bonus_earned = FloatField(null=True, default=0.0)
    incentive_details = StringField(max_length=1000, null=True)

    meta = {
        "collection": "goal_achievements",
        "indexes": [
            ("tenant_id", "staff_id"),
            ("tenant_id", "goal_id"),
            ("tenant_id", "achieved_at"),
        ],
    }

    def __str__(self):
        return f"GoalAchievement(goal={self.goal_id}, staff={self.staff_id})"
