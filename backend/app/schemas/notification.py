"""Notification schemas."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class NotificationCreate(BaseModel):
    """Schema for creating a notification."""

    recipient_id: str
    recipient_type: str  # customer, staff, owner
    notification_type: str
    channel: str  # email, sms, push, in_app
    content: str
    subject: Optional[str] = None
    template_id: Optional[str] = None
    template_variables: Optional[Dict[str, Any]] = None
    appointment_id: Optional[str] = None
    payment_id: Optional[str] = None
    shift_id: Optional[str] = None
    time_off_request_id: Optional[str] = None
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None


class InterDepartmentMessageCreate(BaseModel):
    """Schema for sending inter-departmental messages."""

    recipient_type: str = "staff"  # staff, owner, all
    role_id: Optional[str] = None
    recipient_ids: Optional[List[str]] = None
    notification_type: str = "custom"  # manager_message, team_announcement, custom
    channel: str = "in_app"
    content: str
    subject: Optional[str] = None
    send_email: bool = False


class StaffMessageCreate(BaseModel):
    """Schema for staff sending messages to owners/managers or other staff."""

    recipient_type: str  # owner, specific_staff, role
    recipient_ids: Optional[List[str]] = None
    role_id: Optional[str] = None
    notification_type: str = "custom"
    channel: str = "in_app"
    content: str
    subject: Optional[str] = None
    send_email: bool = False


class CustomerMessageCreate(BaseModel):
    """Schema for customers sending messages to staff or owners."""

    recipient_type: str  # staff, owner
    recipient_ids: Optional[List[str]] = None
    notification_type: str = "custom"
    channel: str = "in_app"
    content: str
    subject: Optional[str] = None
    send_email: bool = False


class NotificationResponse(BaseModel):
    """Schema for notification response."""

    id: str = Field(alias="_id")
    recipient_id: str
    recipient_type: str
    notification_type: str
    channel: str
    content: str
    subject: Optional[str] = None
    status: str
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    failure_reason: Optional[str] = None
    retry_count: int
    is_read: bool
    read_at: Optional[datetime] = None
    appointment_id: Optional[str] = None
    payment_id: Optional[str] = None
    shift_id: Optional[str] = None
    time_off_request_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationPreferenceUpdate(BaseModel):
    """Schema for updating notification preference."""

    customer_id: Optional[str] = None
    user_id: Optional[str] = None
    recipient_type: str = "customer"  # customer or staff
    notification_type: str
    channel: str
    enabled: bool


class NotificationPreferencesBatchUpdate(BaseModel):
    """Schema for batch updating notification preferences."""

    preferences: List[NotificationPreferenceUpdate]


class NotificationPreferenceResponse(BaseModel):
    """Schema for notification preference response."""

    id: str = Field(alias="_id")
    customer_id: Optional[str] = None
    user_id: Optional[str] = None
    recipient_type: str = "customer"
    notification_type: str
    channel: str
    enabled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationTemplateCreate(BaseModel):
    """Schema for creating a notification template."""

    template_type: str
    channel: str
    subject: Optional[str] = None
    body: str
    variables: Optional[List[str]] = None
    is_default: bool = False


class NotificationTemplateResponse(BaseModel):
    """Schema for notification template response."""

    id: str = Field(alias="_id")
    template_type: str
    channel: str
    subject: Optional[str] = None
    body: str
    variables: List[str]
    is_active: bool
    is_default: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
