"""
Waitlist schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.schemas.base import BaseSchema


class WaitlistCreate(BaseModel):
    """Waitlist creation request"""
    client_name: str = Field(..., min_length=2, max_length=100)
    client_phone: str = Field(..., min_length=10, max_length=20)
    client_email: Optional[EmailStr] = None
    service_id: str = Field(..., description="Service ID")
    stylist_id: Optional[str] = Field(None, description="Preferred stylist ID")
    preferred_date: Optional[str] = Field(None, description="Preferred date in ISO format")
    location_id: Optional[str] = Field(None, description="Preferred location ID")
    notes: Optional[str] = Field(None, max_length=500)


class WaitlistUpdate(BaseModel):
    """Waitlist update request"""
    status: str = Field(..., description="Status: waiting, notified, booked, cancelled, expired")


class WaitlistResponse(BaseSchema):
    """Waitlist response"""
    id: str
    tenant_id: str
    client_name: str
    client_phone: str
    client_email: Optional[str] = None
    service_id: str
    service_name: str
    stylist_id: Optional[str] = None
    stylist_name: Optional[str] = None
    location_id: Optional[str] = None
    location_name: Optional[str] = None
    preferred_date: Optional[str] = None
    notes: Optional[str] = None
    status: str
    priority_score: float
    access_token: str
    created_at: datetime
    updated_at: datetime
    notified_at: Optional[datetime] = None
    booked_at: Optional[datetime] = None
    booking_id: Optional[str] = None
