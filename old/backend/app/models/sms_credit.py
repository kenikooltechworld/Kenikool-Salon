"""
SMS Credit models for tracking SMS usage and balance
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId


class SMSCreditTransaction(BaseModel):
    """SMS credit transaction model"""
    id: Optional[str] = Field(None, alias="_id")
    tenant_id: str
    transaction_type: str  # "purchase" or "deduction"
    amount: int  # Number of SMS credits
    reason: str  # e.g., "campaign_send", "purchase", "refund"
    campaign_id: Optional[str] = None
    reference_id: Optional[str] = None  # Payment ID, campaign ID, etc.
    balance_before: int
    balance_after: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True


class SMSCreditBalance(BaseModel):
    """SMS credit balance model"""
    id: Optional[str] = Field(None, alias="_id")
    tenant_id: str
    current_balance: int = 0
    total_purchased: int = 0
    total_used: int = 0
    low_balance_threshold: int = 100  # Alert when balance falls below this
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True


class SMSCreditPurchase(BaseModel):
    """SMS credit purchase request"""
    amount: int = Field(..., gt=0, description="Number of SMS credits to purchase")
    payment_method: str = Field(..., description="Payment method (e.g., 'card', 'bank_transfer')")
    reference_id: Optional[str] = None


class SMSCreditResponse(BaseModel):
    """SMS credit response"""
    current_balance: int
    total_purchased: int
    total_used: int
    low_balance_threshold: int
    last_updated: str
