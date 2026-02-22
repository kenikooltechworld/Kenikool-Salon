"""
Cancellation Reason Model
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


class CancellationReasonBase(BaseModel):
    """Base cancellation reason model"""
    booking_id: str
    reason: str
    category: str  # customer_request, stylist_unavailable, conflict, other
    notes: Optional[str] = None


class CancellationReasonCreate(CancellationReasonBase):
    """Cancellation reason creation model"""
    tenant_id: str


class CancellationReasonInDB(CancellationReasonBase):
    """Cancellation reason model as stored in database"""
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    tenant_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
