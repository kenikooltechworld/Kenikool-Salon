"""
Group Booking Pydantic models
"""
from pydantic import BaseModel, Field
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


class GroupBookingMember(BaseModel):
    """Individual member in a group booking"""
    client_id: str
    client_name: str
    client_phone: str
    service_id: str
    service_name: str
    service_price: float
    stylist_id: str
    stylist_name: str
    booking_id: Optional[str] = None  # Individual booking ID
    status: str = "pending"


class GroupBookingBase(BaseModel):
    """Base group booking model"""
    group_name: str = Field(..., min_length=2, max_length=100)
    organizer_client_id: str
    booking_date: datetime
    members: List[GroupBookingMember]
    group_size: int
    total_price: float
    discount_percentage: float = 0
    discount_amount: float = 0
    final_price: float
    status: str = "pending"  # pending, confirmed, completed, cancelled
    notes: Optional[str] = None


class GroupBookingCreate(GroupBookingBase):
    """Group booking creation model"""
    tenant_id: str


class GroupBookingInDB(GroupBookingBase):
    """Group booking model as stored in database"""
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    tenant_id: str
    organizer_name: str
    organizer_phone: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    confirmed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
