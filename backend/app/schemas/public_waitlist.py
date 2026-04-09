"""Public waitlist schemas for customer-facing waitlist features."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PublicWaitlistJoin(BaseModel):
    """Schema for joining the public waitlist."""

    service_id: str = Field(..., description="Service ID")
    staff_id: Optional[str] = Field(None, description="Preferred staff ID (optional)")
    customer_name: str = Field(..., min_length=2, max_length=100)
    customer_email: str = Field(..., description="Customer email")
    customer_phone: str = Field(..., description="Customer phone")
    preferred_date: Optional[str] = Field(None, description="Preferred date (YYYY-MM-DD)")
    notes: Optional[str] = Field(None, max_length=500)


class PublicWaitlistPosition(BaseModel):
    """Schema for waitlist position response."""

    position: int = Field(..., description="Position in queue")
    estimated_wait_time_minutes: int = Field(..., description="Estimated wait time")
    status: str = Field(..., description="Queue status")
    check_in_time: datetime = Field(..., description="Check-in time")
    service_name: Optional[str] = None
    staff_name: Optional[str] = None


class PublicWaitlistStatus(BaseModel):
    """Schema for public waitlist status."""

    queue_length: int = Field(..., description="Current queue length")
    average_wait_time_minutes: int = Field(..., description="Average wait time")
    is_accepting: bool = Field(..., description="Whether accepting new entries")
    message: Optional[str] = None


class WaitlistNotificationPreferences(BaseModel):
    """Schema for waitlist notification preferences."""

    sms_notifications: bool = Field(True, description="Receive SMS notifications")
    email_notifications: bool = Field(True, description="Receive email notifications")
