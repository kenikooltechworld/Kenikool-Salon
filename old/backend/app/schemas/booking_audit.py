"""
Booking Audit Log schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
from app.schemas.base import BaseSchema


class AuditActionType(str, Enum):
    """Audit action types"""
    CREATED = "created"
    UPDATED = "updated"
    RESCHEDULED = "rescheduled"
    CANCELLED = "cancelled"
    STATUS_CHANGED = "status_changed"
    PAYMENT_UPDATED = "payment_updated"


class BookingAuditLog(BaseSchema):
    """Booking audit log model"""
    id: str
    booking_id: str
    tenant_id: str
    action: AuditActionType
    user_id: Optional[str] = Field(None, description="User who performed the action")
    user_name: Optional[str] = Field(None, description="Name of user who performed the action")
    changes: Dict[str, Any] = Field(default_factory=dict, description="Old and new values")
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime


class BookingAuditLogCreate(BaseModel):
    """Booking audit log creation request"""
    booking_id: str
    action: AuditActionType
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    changes: Dict[str, Any] = Field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
