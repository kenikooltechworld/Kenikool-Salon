"""
Promotion Pydantic models
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


class PackageBase(BaseModel):
    """Base package model"""
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    service_ids: List[str] = []
    original_price: float = Field(..., gt=0)
    package_price: float = Field(..., gt=0)
    discount_percentage: float = Field(default=0, ge=0, le=100)
    is_active: bool = True
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    max_redemptions: Optional[int] = None
    current_redemptions: int = 0


class PackageCreate(PackageBase):
    """Package creation model"""
    tenant_id: str


class PackageInDB(PackageBase):
    """Package model as stored in database"""
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    tenant_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class PromoCodeBase(BaseModel):
    """Base promo code model"""
    code: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = None
    discount_type: str = Field(..., pattern="^(percentage|fixed)$")
    discount_value: float = Field(..., gt=0)
    min_purchase_amount: Optional[float] = None
    max_discount_amount: Optional[float] = None
    is_active: bool = True
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    max_uses: Optional[int] = None
    current_uses: int = 0
    max_uses_per_client: Optional[int] = 1
    applicable_services: List[str] = []  # Empty means all services


class PromoCodeCreate(PromoCodeBase):
    """Promo code creation model"""
    tenant_id: str


class PromoCodeInDB(PromoCodeBase):
    """Promo code model as stored in database"""
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    tenant_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

