"""
Waitlist Pydantic models
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from bson import ObjectId
import uuid


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


class WaitlistBase(BaseModel):
    """Base waitlist model"""
    client_name: str = Field(..., min_length=2, max_length=100)
    client_phone: str = Field(..., min_length=10, max_length=20)
    client_email: Optional[EmailStr] = None
    service_id: str
    stylist_id: Optional[str] = None
    preferred_date: Optional[datetime] = None
    location_id: Optional[str] = None
    notes: Optional[str] = None
    status: str = "waiting"  # waiting, notified, booked, cancelled, expired


class WaitlistCreate(WaitlistBase):
    """Waitlist creation model"""
    tenant_id: str


class WaitlistInDB(WaitlistBase):
    """Waitlist model as stored in database"""
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    tenant_id: str
    service_name: str
    stylist_name: Optional[str] = None
    location_name: Optional[str] = None
    priority_score: float = 0.0
    access_token: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    notified_at: Optional[datetime] = None
    booked_at: Optional[datetime] = None
    booking_id: Optional[str] = None
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
