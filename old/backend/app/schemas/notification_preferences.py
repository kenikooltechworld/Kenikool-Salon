"""
Notification Preferences Schemas
"""
from pydantic import BaseModel
from typing import Optional


class NotificationChannelPreferences(BaseModel):
    """Preferences for notification channels"""
    in_app: bool = True
    email: bool = False
    sms: bool = False
    push: bool = True


class NotificationTypePreferences(BaseModel):
    """Preferences for notification types"""
    booking: NotificationChannelPreferences = NotificationChannelPreferences()
    payment: NotificationChannelPreferences = NotificationChannelPreferences()
    review: NotificationChannelPreferences = NotificationChannelPreferences()
    inventory: NotificationChannelPreferences = NotificationChannelPreferences()
    system: NotificationChannelPreferences = NotificationChannelPreferences()
    general: NotificationChannelPreferences = NotificationChannelPreferences()


class NotificationPreferences(BaseModel):
    """User notification preferences"""
    id: Optional[str] = None
    user_id: str
    tenant_id: str
    preferences: NotificationTypePreferences = NotificationTypePreferences()
    quiet_hours_enabled: bool = False
    quiet_hours_start: Optional[str] = None  # Format: "22:00"
    quiet_hours_end: Optional[str] = None    # Format: "08:00"
    sound_enabled: bool = True
    
    class Config:
        from_attributes = True


class NotificationPreferencesUpdate(BaseModel):
    """Schema for updating notification preferences"""
    preferences: Optional[NotificationTypePreferences] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    sound_enabled: Optional[bool] = None
