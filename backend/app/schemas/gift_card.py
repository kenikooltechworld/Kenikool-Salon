"""Gift card schemas"""
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from decimal import Decimal
from datetime import datetime


class GiftCardPurchaseRequest(BaseModel):
    """Request to purchase a gift card"""
    amount: Decimal = Field(..., gt=0, description="Gift card amount")
    
    # Purchaser info
    purchased_by_name: str
    purchased_by_email: EmailStr
    purchased_by_phone: str
    
    # Recipient info
    recipient_name: Optional[str] = None
    recipient_email: Optional[EmailStr] = None
    recipient_phone: Optional[str] = None
    
    # Delivery
    delivery_method: str = Field(..., pattern="^(email|sms|both)$")
    delivery_date: Optional[datetime] = None  # For scheduled delivery
    
    # Message
    personal_message: Optional[str] = Field(None, max_length=500)
    
    # Validity
    expiry_months: int = Field(12, ge=1, le=60, description="Months until expiry")
    
    # Payment
    payment_method: str = Field(..., pattern="^(paystack|cash|bank_transfer)$")
    
    @validator('delivery_date')
    def validate_delivery_date(cls, v):
        if v and v < datetime.utcnow():
            raise ValueError("Delivery date must be in the future")
        return v


class GiftCardRedemptionRequest(BaseModel):
    """Request to redeem a gift card"""
    code: str = Field(..., min_length=10, max_length=50)
    amount: Decimal = Field(..., gt=0, description="Amount to redeem")
    booking_id: Optional[str] = None


class GiftCardBalanceCheck(BaseModel):
    """Check gift card balance"""
    code: str = Field(..., min_length=10, max_length=50)


class GiftCardResponse(BaseModel):
    """Gift card response"""
    id: str
    code: str
    initial_amount: float
    current_balance: float
    currency: str
    
    purchased_by_name: Optional[str]
    purchased_by_email: Optional[str]
    purchase_date: datetime
    
    recipient_name: Optional[str]
    recipient_email: Optional[str]
    
    status: str
    expiry_date: Optional[datetime]
    is_active: bool
    
    delivery_method: str
    is_delivered: bool
    delivered_at: Optional[datetime]
    
    personal_message: Optional[str]
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class GiftCardBalanceResponse(BaseModel):
    """Gift card balance response"""
    code: str
    current_balance: float
    currency: str
    status: str
    expiry_date: Optional[datetime]
    is_active: bool


class GiftCardTransactionResponse(BaseModel):
    """Gift card transaction response"""
    id: str
    gift_card_code: str
    transaction_type: str
    amount: float
    balance_before: float
    balance_after: float
    description: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class GiftCardListResponse(BaseModel):
    """List of gift cards"""
    gift_cards: List[GiftCardResponse]
    total: int
    page: int
    page_size: int


class GiftCardPurchaseResponse(BaseModel):
    """Response after purchasing a gift card"""
    gift_card: GiftCardResponse
    payment_url: Optional[str] = None  # For online payment
    message: str
