"""
Booking and Client Pydantic models
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from bson import ObjectId


class PyObjectId(str):
    """Custom type for MongoDB ObjectId"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)


class ClientBase(BaseModel):
    """Base client model"""
    name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=10, max_length=20)
    email: Optional[EmailStr] = None
    notes: Optional[str] = None
    preferences: Optional[str] = None


class ClientCreate(ClientBase):
    """Client creation model"""
    tenant_id: str


class ClientInDB(ClientBase):
    """Client model as stored in database"""
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    tenant_id: str
    total_visits: int = 0
    total_spent: float = 0.0
    last_visit_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class BookingBase(BaseModel):
    """Base booking model"""
    client_id: str
    service_id: str
    stylist_id: str
    booking_date: datetime
    duration_minutes: int
    status: str = "pending"  # pending, confirmed, completed, cancelled, no_show
    notes: Optional[str] = None


class BookingCreate(BookingBase):
    """Booking creation model"""
    tenant_id: str


class BookingInDB(BookingBase):
    """Booking model as stored in database"""
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    tenant_id: str
    service_name: str
    service_price: float
    client_name: str
    client_phone: str
    stylist_name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    confirmed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
