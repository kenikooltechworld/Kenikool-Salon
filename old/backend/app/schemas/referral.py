"""
Referral schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

# Request Schemas

class ReferralLinkRequest(BaseModel):
    """Request to generate referral link"""
    client_id: str


class TrackReferralRequest(BaseModel):
    """Request to track referral on signup"""
    referral_code: str
    referred_client_id: str


class CompleteReferralRequest(BaseModel):
    """Request to mark referral as completed"""
    referred_client_id: str
    reward_amount: float


class RedeemRewardsRequest(BaseModel):
    """Request to redeem earned rewards"""
    client_id: str
    amount: float


# Response Schemas

class ReferralLinkResponse(BaseModel):
    """Response with referral link and code"""
    referral_code: str
    referral_link: str
    created_at: datetime


class ReferralHistoryItem(BaseModel):
    """Single referral history item"""
    referred_client_id: str
    referred_client_name: str
    status: str  # pending, completed, expired
    reward_amount: float
    referred_at: datetime
    completed_at: Optional[datetime] = None
    expiration_date: Optional[datetime] = None


class ReferralDashboard(BaseModel):
    """Client referral dashboard"""
    referral_code: str
    referral_link: str
    total_referrals: int
    successful_referrals: int
    pending_referrals: int
    total_rewards_earned: float
    pending_rewards: float
    redeemed_rewards: float
    referral_history: List[ReferralHistoryItem]
    conversion_rate: float


class ReferralAnalytics(BaseModel):
    """Tenant-level referral analytics"""
    total_referrals: int
    successful_referrals: int
    conversion_rate: float
    total_rewards_paid: float
    total_pending_rewards: float
    top_referrers: List[dict]
    referrals_by_period: List[dict]


class RedemptionRecord(BaseModel):
    """Reward redemption record"""
    client_id: str
    amount: float
    redeemed_at: datetime
    status: str  # pending, completed, failed


class ReferralResponse(BaseModel):
    """Basic referral response"""
    id: str = Field(..., alias="_id")
    tenant_id: str
    referrer_id: str
    referred_id: str
    status: str
    created_at: datetime
    
    class Config:
        populate_by_name = True


class ReferralDashboardResponse(BaseModel):
    """Legacy dashboard response"""
    total_referrals: int
    successful_referrals: int
    pending_referrals: int
    total_rewards: float
