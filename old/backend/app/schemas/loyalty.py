"""
Loyalty Points System schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.base import BaseSchema


class LoyaltyAccountCreate(BaseModel):
    """Create loyalty account request"""
    client_id: str = Field(..., description="Client ID")


class LoyaltyAccount(BaseSchema):
    """Loyalty account response"""
    id: str
    tenant_id: str
    client_id: str
    points_balance: int = Field(default=0, description="Current points balance")
    lifetime_points: int = Field(default=0, description="Total points earned lifetime")
    tier: str = Field(default="bronze", description="Loyalty tier: bronze, silver, gold, platinum")
    created_at: datetime
    updated_at: datetime


class LoyaltyTransactionCreate(BaseModel):
    """Create loyalty transaction request"""
    client_id: str = Field(..., description="Client ID")
    points: int = Field(..., description="Points amount (positive for earn, negative for redeem)")
    transaction_type: str = Field(..., description="Transaction type: earn, redeem, adjustment")
    reference_type: Optional[str] = Field(None, description="Reference type: booking, purchase, manual")
    reference_id: Optional[str] = Field(None, description="Reference ID (booking ID, purchase ID, etc)")
    description: Optional[str] = Field(None, max_length=500, description="Transaction description")


class LoyaltyTransaction(BaseSchema):
    """Loyalty transaction response"""
    id: str
    tenant_id: str
    client_id: str
    points: int
    transaction_type: str
    reference_type: Optional[str] = None
    reference_id: Optional[str] = None
    description: Optional[str] = None
    balance_after: int
    created_at: datetime


class LoyaltyEarnRequest(BaseModel):
    """Earn points request"""
    client_id: str = Field(..., description="Client ID")
    points: int = Field(..., gt=0, description="Points to earn")
    reference_type: Optional[str] = Field(None, description="Reference type: booking, purchase, manual")
    reference_id: Optional[str] = Field(None, description="Reference ID")
    description: Optional[str] = Field(None, max_length=500)


class LoyaltyRedeemRequest(BaseModel):
    """Redeem points request"""
    client_id: str = Field(..., description="Client ID")
    points: int = Field(..., gt=0, description="Points to redeem")
    reference_type: Optional[str] = Field(None, description="Reference type: booking, purchase, manual")
    reference_id: Optional[str] = Field(None, description="Reference ID")
    description: Optional[str] = Field(None, max_length=500)


class LoyaltyBalanceResponse(BaseModel):
    """Loyalty balance response"""
    client_id: str
    points_balance: int
    lifetime_points: int
    tier: str
    tier_progress: dict  # Progress to next tier


class LoyaltyReward(BaseModel):
    """Loyalty reward definition"""
    id: str
    tenant_id: str
    name: str
    description: str
    points_required: int
    reward_type: str  # discount, free_service, gift
    reward_value: float  # Discount amount or service value
    active: bool = True
    created_at: datetime


class LoyaltyRewardCreate(BaseModel):
    """Create loyalty reward request"""
    name: str = Field(..., max_length=200)
    description: str = Field(..., max_length=500)
    points_required: int = Field(..., gt=0)
    reward_type: str = Field(..., description="Reward type: discount, free_service, gift")
    reward_value: float = Field(..., gt=0)
    active: bool = True


class LoyaltyHistoryResponse(BaseModel):
    """Loyalty history response"""
    transactions: List[LoyaltyTransaction]
    total_earned: int
    total_redeemed: int
    current_balance: int
