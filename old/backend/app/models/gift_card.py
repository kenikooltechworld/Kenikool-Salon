"""
Gift Card Pydantic models
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from bson import ObjectId
import secrets
import string


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


def generate_gift_card_code() -> str:
    """Generate a unique gift card code"""
    # Format: XXXX-XXXX-XXXX-XXXX
    chars = string.ascii_uppercase + string.digits
    parts = [''.join(secrets.choice(chars) for _ in range(4)) for _ in range(4)]
    return '-'.join(parts)


class GiftCardBase(BaseModel):
    """Base gift card model"""
    code: str = Field(default_factory=generate_gift_card_code)
    initial_amount: float = Field(..., gt=0)
    current_balance: float
    recipient_name: str = Field(..., min_length=2, max_length=100)
    recipient_phone: str = Field(..., min_length=10, max_length=20)
    recipient_email: Optional[EmailStr] = None
    sender_name: Optional[str] = None
    message: Optional[str] = None
    status: str = "active"  # active, redeemed, expired, cancelled
    expiry_date: Optional[datetime] = None


class GiftCardCreate(GiftCardBase):
    """Gift card creation model"""
    tenant_id: str
    purchaser_client_id: Optional[str] = None


class GiftCardInDB(GiftCardBase):
    """Gift card model as stored in database"""
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    tenant_id: str
    purchaser_client_id: Optional[str] = None
    purchaser_name: Optional[str] = None
    purchase_date: datetime = Field(default_factory=datetime.utcnow)
    delivery_method: str = "whatsapp"  # whatsapp, sms, email
    delivery_status: str = "pending"  # pending, sent, failed
    delivered_at: Optional[datetime] = None
    first_redemption_date: Optional[datetime] = None
    last_redemption_date: Optional[datetime] = None
    redemption_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


# Alias for backward compatibility
GiftCard = GiftCardInDB


class GiftCardTransaction(BaseModel):
    """Gift card transaction/redemption record"""
    gift_card_id: str
    booking_id: Optional[str] = None
    amount_used: float
    balance_before: float
    balance_after: float
    redeemed_by_client_id: Optional[str] = None
    redeemed_by_name: Optional[str] = None
    transaction_date: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None


class GiftCardTransactionInDB(GiftCardTransaction):
    """Gift card transaction as stored in database"""
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    tenant_id: str
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
