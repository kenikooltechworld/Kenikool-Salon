"""
Booking Template Model
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


class ServiceTemplate(BaseModel):
    """Service template within booking template"""
    service_id: str
    variants: List[str] = []
    add_ons: List[str] = []


class BookingTemplateBase(BaseModel):
    """Base booking template model"""
    client_id: str
    name: str
    description: Optional[str] = None
    services: List[ServiceTemplate]
    duration: int
    pricing: float
    category: Optional[str] = None


class BookingTemplateCreate(BookingTemplateBase):
    """Booking template creation model"""
    tenant_id: str


class BookingTemplateInDB(BookingTemplateBase):
    """Booking template model as stored in database"""
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    tenant_id: str
    usage_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
