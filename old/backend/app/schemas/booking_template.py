"""
Booking template schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class BookingTemplateCreate(BaseModel):
    """Schema for creating a booking template"""
    name: str = Field(..., description="Template name")
    client_id: str = Field(..., description="Client ID")
    service_id: str = Field(..., description="Service ID")
    stylist_id: str = Field(..., description="Stylist ID")
    notes: Optional[str] = Field(None, description="Default notes")
    is_active: bool = Field(True, description="Whether template is active")


class BookingTemplateUpdate(BaseModel):
    """Schema for updating a booking template"""
    name: Optional[str] = Field(None, description="Template name")
    service_id: Optional[str] = Field(None, description="Service ID")
    stylist_id: Optional[str] = Field(None, description="Stylist ID")
    notes: Optional[str] = Field(None, description="Default notes")
    is_active: Optional[bool] = Field(None, description="Whether template is active")


class BookingTemplateResponse(BaseModel):
    """Schema for booking template response"""
    id: str
    tenant_id: str
    name: str
    client_id: str
    client_name: str
    service_id: str
    service_name: str
    stylist_id: str
    stylist_name: str
    notes: Optional[str] = None
    is_active: bool
    usage_count: int = 0
    last_used_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class CreateBookingFromTemplate(BaseModel):
    """Schema for creating a booking from a template"""
    template_id: str = Field(..., description="Template ID")
    booking_date: str = Field(..., description="Booking date in ISO format")
    override_notes: Optional[str] = Field(None, description="Override template notes")
