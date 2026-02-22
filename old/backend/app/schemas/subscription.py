"""
Platform subscription schemas - For salon owner subscriptions to platform plans
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SubscriptionPlanResponse(BaseModel):
    """Platform subscription plan"""
    id: str
    name: str
    price: float
    billing_cycle: str  # monthly, yearly
    features: list[str]
    max_bookings: Optional[int] = None
    max_staff: Optional[int] = None
    has_custom_branding: bool = False
    has_custom_domain: bool = False
    has_api_access: bool = False
    has_sms_notifications: bool = False
    is_active: bool = True


class SubscriptionUpgradeRequest(BaseModel):
    """Request to upgrade/downgrade subscription"""
    plan_id: str = Field(..., description="Target plan ID")
    payment_method: str = Field(..., description="Payment method: paystack or flutterwave")


class SubscriptionResponse(BaseModel):
    """Current subscription status"""
    id: str
    tenant_id: str
    plan_id: str
    plan_name: str
    plan_price: float
    status: str  # active, cancelled, expired, trial
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool = False
    created_at: datetime
    updated_at: datetime


class PaymentMethodCreate(BaseModel):
    """Add payment method"""
    authorization_code: str = Field(..., description="Paystack authorization code")
    card_type: str
    last4: str
    exp_month: str
    exp_year: str
    bank: str


class PaymentMethodResponse(BaseModel):
    """Payment method response"""
    id: str
    tenant_id: str
    card_type: str
    last4: str
    exp_month: str
    exp_year: str
    bank: str
    is_default: bool = True
    created_at: datetime


class BillingHistoryItem(BaseModel):
    """Billing history item"""
    id: str
    tenant_id: str
    amount: float
    status: str  # completed, failed, pending
    description: str
    invoice_url: Optional[str] = None
    created_at: datetime


class BillingHistoryResponse(BaseModel):
    """Billing history response"""
    items: list[BillingHistoryItem]
    total: int
