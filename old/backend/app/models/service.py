"""
Service Pydantic models
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


class ServiceBase(BaseModel):
    """Base service model"""
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    duration_minutes: int = Field(..., gt=0)
    category: Optional[str] = None
    photo_url: Optional[str] = None
    is_active: bool = True
    assigned_stylists: List[str] = []  # List of stylist IDs


class ServiceCreate(ServiceBase):
    """Service creation model"""
    tenant_id: str


class ServiceUpdate(BaseModel):
    """Service update model"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    duration_minutes: Optional[int] = Field(None, gt=0)
    category: Optional[str] = None
    photo_url: Optional[str] = None
    is_active: Optional[bool] = None
    assigned_stylists: Optional[List[str]] = None


class ServiceInDB(ServiceBase):
    """Service model as stored in database"""
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    tenant_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class ServiceResponse(ServiceBase):
    """Service response model"""
    id: str
    tenant_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
