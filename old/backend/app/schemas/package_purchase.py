"""
Package purchase schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class PackagePurchaseCreate(BaseModel):
    """Package purchase creation schema"""
    package_definition_id: str = Field(..., description="Package definition ID")
    payment_method: str = Field(..., description="Payment method used")
    is_gift: bool = Field(default=False, description="Whether this is a gift purchase")
    recipient_id: Optional[str] = Field(None, description="Recipient client ID if gift")
    gift_message: Optional[str] = Field(None, description="Gift message")


class PackagePurchaseResponse(BaseModel):
    """Package purchase response schema"""
    id: str = Field(..., alias="_id")
    tenant_id: str
    package_definition_id: str
    client_id: str
    purchased_by_staff_id: str
    purchase_date: datetime
    expiration_date: Optional[datetime]
    status: str = Field(description="active, expired, fully_redeemed, cancelled")
    original_price: float
    amount_paid: float
    payment_method: str
    payment_transaction_id: str
    is_gift: bool
    gift_from_client_id: Optional[str]
    gift_message: Optional[str]
    is_transferable: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True


class PackagePurchaseListResponse(BaseModel):
    """Package purchase list response"""
    purchases: List[PackagePurchaseResponse]
    total: int
