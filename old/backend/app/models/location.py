"""
Location Pydantic models for multi-location management
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict
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


class LocationBase(BaseModel):
    """Base location model"""
    name: str = Field(..., min_length=2, max_length=100)
    address: str = Field(..., min_length=5, max_length=200)
    phone: str = Field(..., min_length=10, max_length=20)
    email: Optional[EmailStr] = None
    manager_name: Optional[str] = None
    is_active: bool = True


class LocationCreate(LocationBase):
    """Location creation model"""
    tenant_id: str
    coordinates: Optional[Dict] = None  # {"latitude": float, "longitude": float}


class LocationInDB(LocationBase):
    """Location model as stored in database"""
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    tenant_id: str
    location: Optional[Dict] = None  # GeoJSON format
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
