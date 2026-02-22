"""Pydantic schemas for membership system."""

from datetime import datetime
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field, validator


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


# Request Schemas
class MembershipPlanCreate(BaseModel):
    """Schema for creating a membership plan"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    price: float = Field(..., gt=0)
    billing_cycle: BillingCycle
    benefits: List[str] = Field(default_factory=list)
    discount_percentage: float = Field(default=0.0, ge=0, le=100)
    trial_period_days: Optional[int] = Field(None, ge=1, le=365)

    @validator("price")
    def validate_price(cls, v):
        if v > 1000000:
            raise ValueError("Price exceeds maximum allowed")
        return round(v, 2)


# Alias for backward compatibility
class MembershipPlanCreateRequest(MembershipPlanCreate):
    """Alias for MembershipPlanCreate for backward compatibility"""
    pass


class MembershipPlanUpdate(BaseModel):
    """Schema for updating a membership plan"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    price: Optional[float] = Field(None, gt=0)
    billing_cycle: Optional[BillingCycle] = None
    benefits: Optional[List[str]] = None
    discount_percentage: Optional[float] = Field(None, ge=0, le=100)
    trial_period_days: Optional[int] = Field(None, ge=1, le=365)
    is_active: Optional[bool] = None


# Alias for backward compatibility
class MembershipPlanUpdateRequest(MembershipPlanUpdate):
    """Alias for MembershipPlanUpdate for backward compatibility"""
    pass


class MembershipPlanResponse(BaseModel):
    """Schema for membership plan response"""
    id: str = Field(..., alias="_id")
    tenant_id: str
    name: str
    description: Optional[str] = None
    price: float
    billing_cycle: BillingCycle
    benefits: List[str]
    discount_percentage: float
    trial_period_days: Optional[int] = None
    is_active: bool
    subscriber_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        use_enum_values = True


class MembershipSubscriptionCreate(BaseModel):
    """Schema for creating a subscription"""
    client_id: str = Field(..., min_length=1)
    plan_id: str = Field(..., min_length=1)
    payment_method_id: str = Field(..., min_length=1)
    start_trial: bool = False


# Alias for backward compatibility
class MembershipSubscriptionCreateRequest(MembershipSubscriptionCreate):
    """Alias for MembershipSubscriptionCreate for backward compatibility"""
    pass


class CancelSubscriptionRequest(BaseModel):
    """Schema for cancelling subscription"""
    reason: Optional[str] = Field(None, max_length=500)
    immediate: bool = False


# Alias for backward compatibility
class MembershipSubscriptionCancelRequest(CancelSubscriptionRequest):
    """Alias for CancelSubscriptionRequest for backward compatibility"""
    pass


class ChangeSubscriptionPlanRequest(BaseModel):
    """Schema for changing subscription plan"""
    new_plan_id: str = Field(..., min_length=1)
    apply_immediately: bool = True


# Alias for backward compatibility
class MembershipSubscriptionChangePlanRequest(ChangeSubscriptionPlanRequest):
    """Alias for ChangeSubscriptionPlanRequest for backward compatibility"""
    pass


class UpdatePaymentMethodRequest(BaseModel):
    """Schema for updating payment method"""
    payment_method_id: str = Field(..., min_length=1)


# Alias for backward compatibility
class MembershipSubscriptionPaymentMethodRequest(UpdatePaymentMethodRequest):
    """Alias for UpdatePaymentMethodRequest for backward compatibility"""
    pass


class PaymentRecord(BaseModel):
    """Payment history record"""
    date: datetime
    amount: float
    status: str
    transaction_id: str
    reason: Optional[str] = None


class RenewalRecord(BaseModel):
    """Renewal history record"""
    date: datetime
    from_plan_id: str
    to_plan_id: str
    type: str


class MembershipSubscriptionResponse(BaseModel):
    """Schema for subscription response"""
    id: str = Field(..., alias="_id")
    tenant_id: str
    client_id: str
    plan_id: str
    status: SubscriptionStatus
    start_date: datetime
    end_date: datetime
    trial_end_date: Optional[datetime] = None
    auto_renew: bool
    payment_history: List[PaymentRecord] = []
    renewal_history: List[RenewalRecord] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        use_enum_values = True


class SubscriptionListResponse(BaseModel):
    """List of subscriptions with pagination"""
    subscriptions: List[MembershipSubscriptionResponse]
    total: int
    page: int
    pages: int


class MembershipAnalyticsResponse(BaseModel):
    """Comprehensive membership analytics"""
    mrr: float
    arr: float
    active_subscribers: int
    churn_rate: float
    average_lifetime_days: float
    trial_conversion_rate: float
