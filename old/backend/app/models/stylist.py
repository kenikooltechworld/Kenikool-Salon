"""
Stylist Pydantic models
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime, time
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


class WorkingHours(BaseModel):
    """Working hours for a specific day"""
    day: str  # monday, tuesday, etc.
    start_time: str  # HH:MM format
    end_time: str  # HH:MM format
    is_working: bool = True


class StylistSchedule(BaseModel):
    """Stylist weekly schedule"""
    working_hours: List[WorkingHours] = []
    break_start: Optional[str] = None  # HH:MM format
    break_end: Optional[str] = None  # HH:MM format


class StylistBase(BaseModel):
    """Base stylist model"""
    name: str = Field(..., min_length=2, max_length=100)
    email: Optional[str] = None
    phone: str = Field(..., min_length=10, max_length=20)
    bio: Optional[str] = None
    photo_url: Optional[str] = None
    is_active: bool = True
    schedule: Optional[StylistSchedule] = None
    specialties: List[str] = []  # List of service categories


class StylistCreate(StylistBase):
    """Stylist creation model"""
    tenant_id: str


class StylistUpdate(BaseModel):
    """Stylist update model"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[str] = None
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    bio: Optional[str] = None
    photo_url: Optional[str] = None
    is_active: Optional[bool] = None
    schedule: Optional[StylistSchedule] = None
    specialties: Optional[List[str]] = None


class StylistInDB(StylistBase):
    """Stylist model as stored in database"""
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    tenant_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
