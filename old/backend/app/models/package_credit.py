"""
Package Credit Model
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


class CreditTransaction(BaseModel):
    """Credit transaction record"""
    id: str = Field(default_factory=lambda: str(ObjectId()))
    type: str  # purchase, redemption, expiration
    amount: float
    booking_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PackageCreditBase(BaseModel):
    """Base package credit model"""
    client_id: str
    balance: float
    total_purchased: float = 0.0
    expiration_date: Optional[datetime] = None


class PackageCreditCreate(PackageCreditBase):
    """Package credit creation model"""
    tenant_id: str


class PackageCreditInDB(PackageCreditBase):
    """Package credit model as stored in database"""
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    tenant_id: str
    transactions: List[CreditTransaction] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
