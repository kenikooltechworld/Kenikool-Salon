"""
Client schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.base import BaseSchema


class ClientCreate(BaseModel):
    """Client creation request"""
    name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=10, max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = Field(None, max_length=500)
    birthday: Optional[str] = Field(None, description="Birthday in YYYY-MM-DD format")
    segment: Optional[str] = Field(None, description="Client segment: new, regular, vip, inactive")
    tags: List[str] = Field(default=[], description="Client tags for categorization")


class ClientUpdate(BaseModel):
    """Client update request"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = Field(None, max_length=500)
    birthday: Optional[str] = None
    segment: Optional[str] = Field(None, description="Client segment: new, regular, vip, inactive")
    tags: Optional[List[str]] = Field(None, description="Client tags for categorization")


class ClientPreferences(BaseModel):
    """Client preferences"""
    preferred_stylist_id: Optional[str] = Field(None, description="Preferred stylist ID")
    preferred_services: List[str] = Field(default_factory=list, description="List of preferred service IDs")
    preferred_products: List[str] = Field(default_factory=list, description="List of preferred product names")
    communication_channel: Optional[str] = Field(None, description="Preferred communication: sms, email, whatsapp")
    appointment_reminders: bool = Field(True, description="Enable appointment reminders")
    marketing_consent: bool = Field(False, description="Consent to marketing messages")


class ClientPhotoInput(BaseModel):
    """Client photo upload input"""
    photo_type: str = Field(..., description="before or after")
    description: Optional[str] = Field(None, max_length=200)


class ClientPhotoResponse(BaseModel):
    """Client photo response"""
    photo_url: str
    photo_type: str
    description: Optional[str] = None
    uploaded_at: datetime


class ClientResponse(BaseSchema):
    """Client response"""
    id: str
    tenant_id: str
    name: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    birthday: Optional[str] = None
    segment: str = "new"
    tags: List[str] = []
    total_visits: int = 0
    total_spent: float = 0.0
    last_visit_date: Optional[datetime] = None
    last_activity_date: Optional[datetime] = None
    photos: List[ClientPhotoResponse] = []
    preferences: Optional[ClientPreferences] = None
    created_at: datetime
    updated_at: datetime


class ClientFilter(BaseModel):
    """Client filter parameters"""
    search: Optional[str] = Field(None, description="Search by name, phone, or email")
    segment: Optional[str] = Field(None, description="Filter by segment: new, regular, vip, inactive")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    min_spent: Optional[float] = Field(None, description="Minimum total spent")
    max_spent: Optional[float] = Field(None, description="Maximum total spent")
    last_visit_start: Optional[datetime] = Field(None, description="Last visit from date")
    last_visit_end: Optional[datetime] = Field(None, description="Last visit to date")
    preferred_stylist_id: Optional[str] = Field(None, description="Filter by preferred stylist")
    birthday_month: Optional[int] = Field(None, ge=1, le=12, description="Filter by birthday month (1-12)")
    offset: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)
