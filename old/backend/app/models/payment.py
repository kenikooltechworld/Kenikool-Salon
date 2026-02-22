"""
Payment Pydantic models
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


class PaymentBase(BaseModel):
    """Base payment model"""
    booking_id: str
    amount: float
    payment_method: str  # card, cash, transfer, split
    payment_gateway: Optional[str] = None  # paystack, flutterwave
    status: str = "pending"  # pending, processing, completed, failed, refunded


class PaymentCreate(PaymentBase):
    """Payment creation model"""
    tenant_id: str
    client_id: str


class PaymentInDB(PaymentBase):
    """Payment model as stored in database"""
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    tenant_id: str
    client_id: str
    transaction_reference: Optional[str] = None
    gateway_response: Optional[dict] = None
    paid_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class SplitPayment(BaseModel):
    """Split payment model"""
    payment_method: str
    amount: float
    transaction_reference: Optional[str] = None


class DepositPayment(BaseModel):
    """Deposit payment model"""
    booking_id: str
    amount: float
    payment_method: str
    payment_gateway: Optional[str] = None
