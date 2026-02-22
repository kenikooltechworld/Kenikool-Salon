"""
Gift card schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class GiftCardCreate(BaseModel):
    amount: float = Field(..., gt=0)
    recipient_name: str
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None
    message: Optional[str] = None

class GiftCardResponse(BaseModel):
    id: str = Field(..., alias="_id")
    tenant_id: str
    code: str
    amount: float
    balance: float
    status: str
    created_at: datetime
    
    class Config:
        populate_by_name = True

class GiftCardValidationResponse(BaseModel):
    valid: bool
    balance: Optional[float] = None
    error: Optional[str] = None

class GiftCardRedemptionResponse(BaseModel):
    success: bool
    new_balance: float
    message: str

class GiftCardBalanceResponse(BaseModel):
    balance: float
    status: str
