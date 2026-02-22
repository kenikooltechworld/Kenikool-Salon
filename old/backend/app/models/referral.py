"""
Referral Pydantic models
"""
from pydantic import BaseModel, Field
from typing import Optional
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


class ReferralBase(BaseModel):
    """Base referral model"""
    referrer_client_id: str
    referral_code: str
    referral_link: str
    status: str = "active"  # active, inactive
    total_referrals: int = 0
    successful_referrals: int = 0
    total_rewards_earned: float = 0
    pending_rewards: float = 0


class ReferralCreate(ReferralBase):
    """Referral creation model"""
    tenant_id: str


class ReferralInDB(ReferralBase):
    """Referral model as stored in database"""
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    tenant_id: str
    referrer_name: str
    referrer_phone: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class ReferralTrackingBase(BaseModel):
    """Base referral tracking model"""
    referral_id: str
    referrer_client_id: str
    referred_client_id: str
    status: str = "pending"  # pending, completed, expired
    reward_amount: float = 0
    reward_status: str = "pending"  # pending, earned, paid


class ReferralTrackingInDB(ReferralTrackingBase):
    """Referral tracking model as stored in database"""
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    tenant_id: str
    referred_client_name: str
    referred_client_phone: str
    referred_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
