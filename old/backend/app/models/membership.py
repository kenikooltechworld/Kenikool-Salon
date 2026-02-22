"""
Membership system models for MongoDB collections.
Defines the schema for membership plans and subscriptions.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class BillingCycle(str, Enum):
    """Billing cycle options"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class SubscriptionStatus(str, Enum):
    """Subscription status options"""
    TRIAL = "trial"
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    GRACE_PERIOD = "grace_period"


class PaymentRecord(BaseModel):
    """Payment history record"""
    date: datetime
    amount: float
    status: str  # "success" | "failed"
    transaction_id: str
    reason: Optional[str] = None


class RenewalRecord(BaseModel):
    """Renewal history record"""
    date: datetime
    from_plan_id: str
    to_plan_id: str
    type: str  # "renewal" | "upgrade" | "downgrade"


class BenefitUsage(BaseModel):
    """Benefit usage tracking"""
    cycle_start: datetime
    usage_count: int = 0
    limit: int = -1  # -1 for unlimited


class MembershipPlan(BaseModel):
    """Membership plan model"""
    id: Optional[str] = Field(None, alias="_id")
    tenant_id: str
    name: str
    description: Optional[str] = None
    price: float
    billing_cycle: BillingCycle
    benefits: List[str] = []
    discount_percentage: float = 0.0
    trial_period_days: Optional[int] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None

    class Config:
        populate_by_name = True
        use_enum_values = True


class MembershipSubscription(BaseModel):
    """Membership subscription model"""
    id: Optional[str] = Field(None, alias="_id")
    tenant_id: str
    client_id: str
    plan_id: str
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    start_date: datetime
    end_date: datetime
    trial_end_date: Optional[datetime] = None
    auto_renew: bool = True
    payment_method_id: Optional[str] = None
    payment_history: List[PaymentRecord] = []
    renewal_history: List[RenewalRecord] = []
    benefit_usage: Optional[BenefitUsage] = None
    grace_period_start: Optional[datetime] = None
    retry_count: int = 0
    cancellation_reason: Optional[str] = None
    cancelled_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        use_enum_values = True


class MembershipPlanCreate(BaseModel):
    """Request schema for creating membership plan"""
    name: str
    description: Optional[str] = None
    price: float
    billing_cycle: BillingCycle
    benefits: List[str] = []
    discount_percentage: float = 0.0
    trial_period_days: Optional[int] = None


class MembershipPlanUpdate(BaseModel):
    """Request schema for updating membership plan"""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    billing_cycle: Optional[BillingCycle] = None
    benefits: Optional[List[str]] = None
    discount_percentage: Optional[float] = None
    trial_period_days: Optional[int] = None
    is_active: Optional[bool] = None


class MembershipSubscriptionCreate(BaseModel):
    """Request schema for creating subscription"""
    client_id: str
    plan_id: str
    payment_method_id: str
    start_trial: bool = False


class MembershipSubscriptionUpdate(BaseModel):
    """Request schema for updating subscription"""
    auto_renew: Optional[bool] = None
    payment_method_id: Optional[str] = None


class ChangeSubscriptionPlan(BaseModel):
    """Request schema for changing subscription plan"""
    new_plan_id: str
    apply_immediately: bool = True


class UpdatePaymentMethod(BaseModel):
    """Request schema for updating payment method"""
    payment_method_id: str


class CancelSubscriptionRequest(BaseModel):
    """Request schema for cancelling subscription"""
    reason: Optional[str] = None
    immediate: bool = False
