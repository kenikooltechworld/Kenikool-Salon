"""Tenant settings schema."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class BusinessHours(BaseModel):
    """Business hours for a day."""
    
    open_time: str = Field(..., description="Opening time in HH:MM format")
    close_time: str = Field(..., description="Closing time in HH:MM format")
    is_closed: bool = Field(default=False, description="Whether the business is closed this day")


class TenantSettingsSchema(BaseModel):
    """Tenant settings schema."""
    
    # Basic Information
    salon_name: str = Field(..., description="Salon/business name")
    email: str = Field(..., description="Business email")
    phone: str = Field(..., description="Business phone")
    address: str = Field(..., description="Business address")
    
    # Business Configuration
    tax_rate: float = Field(default=0.0, ge=0, le=100, description="Tax rate as percentage")
    currency: str = Field(default="NGN", description="Currency code (NGN, USD, etc.)")
    timezone: str = Field(default="Africa/Lagos", description="Timezone")
    language: str = Field(default="en", description="Language code")
    
    # Business Hours
    business_hours: Dict[str, BusinessHours] = Field(
        default_factory=lambda: {
            "monday": BusinessHours(open_time="09:00", close_time="18:00"),
            "tuesday": BusinessHours(open_time="09:00", close_time="18:00"),
            "wednesday": BusinessHours(open_time="09:00", close_time="18:00"),
            "thursday": BusinessHours(open_time="09:00", close_time="18:00"),
            "friday": BusinessHours(open_time="09:00", close_time="18:00"),
            "saturday": BusinessHours(open_time="10:00", close_time="16:00"),
            "sunday": BusinessHours(open_time="00:00", close_time="00:00", is_closed=True),
        },
        description="Business hours by day of week"
    )
    
    # Notifications
    notification_email: bool = Field(default=True, description="Send email notifications")
    notification_sms: bool = Field(default=False, description="Send SMS notifications")
    notification_push: bool = Field(default=False, description="Send push notifications")
    
    # Branding
    logo_url: Optional[str] = Field(default=None, description="Logo URL")
    primary_color: str = Field(default="#000000", description="Primary brand color (hex)")
    secondary_color: str = Field(default="#FFFFFF", description="Secondary brand color (hex)")
    
    # Advanced Settings
    appointment_reminder_hours: int = Field(default=24, ge=1, le=168, description="Hours before appointment to send reminder")
    allow_online_booking: bool = Field(default=True, description="Allow customers to book online")
    require_customer_approval: bool = Field(default=False, description="Require customer approval for bookings")
    auto_confirm_bookings: bool = Field(default=True, description="Automatically confirm bookings")
    
    class Config:
        """Pydantic config."""
        schema_extra = {
            "example": {
                "salon_name": "Acme Salon",
                "email": "info@acmesalon.com",
                "phone": "+234801234567",
                "address": "123 Main St, Lagos",
                "tax_rate": 7.5,
                "currency": "NGN",
                "timezone": "Africa/Lagos",
                "language": "en",
                "business_hours": {
                    "monday": {"open_time": "09:00", "close_time": "18:00", "is_closed": False},
                    "sunday": {"open_time": "00:00", "close_time": "00:00", "is_closed": True},
                },
                "notification_email": True,
                "notification_sms": False,
                "primary_color": "#FF6B6B",
                "secondary_color": "#FFFFFF",
            }
        }
