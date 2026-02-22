"""
Add-On Model
"""
from pydantic import BaseModel, Field
from typing import Optional
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


class AddOnBase(BaseModel):
    """Base add-on model"""
    service_id: str
    name: str
    description: Optional[str] = None
    price: float
    duration_minutes: int


class AddOnCreate(AddOnBase):
    """Add-on creation model"""
    tenant_id: str


class AddOnInDB(AddOnBase):
    """Add-on model as stored in database"""
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    tenant_id: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
