"""Staff settings schema for validation."""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List


class StaffSettingsBase(BaseModel):
    """Base staff settings schema."""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email_bookings: bool = True
    email_reminders: bool = True
    email_messages: bool = True
    sms_bookings: bool = False
    sms_reminders: bool = False
    push_bookings: bool = True
    push_reminders: bool = True
    
    # Phase 3: Availability preferences
    working_hours_start: Optional[str] = Field(None, max_length=5)
    working_hours_end: Optional[str] = Field(None, max_length=5)
    days_off: List[str] = Field(default_factory=list)
    
    # Phase 3: Emergency contact
    emergency_contact_name: Optional[str] = Field(None, max_length=100)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    emergency_contact_relationship: Optional[str] = Field(None, max_length=50)
    
    # Phase 3: Work preferences
    service_specializations: List[str] = Field(default_factory=list)
    preferred_customer_types: List[str] = Field(default_factory=list)


class StaffSettingsCreate(StaffSettingsBase):
    """Schema for creating staff settings."""

    pass


class StaffSettingsUpdate(BaseModel):
    """Schema for updating staff settings."""

    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email_bookings: Optional[bool] = None
    email_reminders: Optional[bool] = None
    email_messages: Optional[bool] = None
    sms_bookings: Optional[bool] = None
    sms_reminders: Optional[bool] = None
    push_bookings: Optional[bool] = None
    push_reminders: Optional[bool] = None
    
    # Phase 3: Availability preferences
    working_hours_start: Optional[str] = Field(None, max_length=5)
    working_hours_end: Optional[str] = Field(None, max_length=5)
    days_off: Optional[List[str]] = None
    
    # Phase 3: Emergency contact
    emergency_contact_name: Optional[str] = Field(None, max_length=100)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    emergency_contact_relationship: Optional[str] = Field(None, max_length=50)
    
    # Phase 3: Work preferences
    service_specializations: Optional[List[str]] = None
    preferred_customer_types: Optional[List[str]] = None


class StaffSettingsResponse(StaffSettingsBase):
    """Schema for staff settings response."""

    id: str = Field(..., alias="_id")
    user_id: str
    created_at: str
    updated_at: str

    class Config:
        """Pydantic config."""

        populate_by_name = True
