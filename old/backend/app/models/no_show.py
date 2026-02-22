"""
No-Show Model
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


class NoShowBase(BaseModel):
    """Base no-show model"""
    booking_id: str
    client_id: str
    recorded_by: str
    fee_charged: Optional[float] = None
    notes: Optional[str] = None


class NoShowCreate(NoShowBase):
    """No-show creation model"""
    tenant_id: str


class NoShowInDB(NoShowBase):
    """No-show model as stored in database"""
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    tenant_id: str
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
