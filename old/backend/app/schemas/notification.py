"""
Notification Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class NotificationBase(BaseModel):
    """Base notification schema"""
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=500)
    type: Literal["booking", "payment", "review", "inventory", "system", "general"] = "general"
    link: Optional[str] = None


class NotificationCreate(NotificationBase):
    """Schema for creating a notification"""
    pass


class NotificationUpdate(BaseModel):
    """Schema for updating a notification"""
    is_read: Optional[bool] = None


class Notification(NotificationBase):
    """Schema for notification response"""
    id: str
    tenant_id: str
    user_id: Optional[str] = None
    is_read: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Schema for notification list response"""
    notifications: list[Notification]
    total: int
    unread_count: int


class NotificationStats(BaseModel):
    """Schema for notification statistics"""
    total: int
    unread: int
    by_type: dict[str, int]
