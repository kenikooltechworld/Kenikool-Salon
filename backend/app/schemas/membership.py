"""Membership schemas for API requests and responses."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from decimal import Decimal
from datetime import datetime


class MembershipBenefitSchema(BaseModel):
    """Schema for membership benefit."""
    benefit_type: str
    description: str
    value: Optional[str] = None


class MembershipTierBase(BaseModel):
    """Base schema for membership tier."""
    name: str
    description: Optional[str] = None
    monthly_price: Decimal
    annual_price: Optional[Decimal] = None
    billing_cycle: str  # "monthly" or "annual"
    discount_percentage: int = 0
    priority_booking: bool = False
    exclusive_services: List[str] = []
    free_services_per_month: int = 0
    rollover_unused: bool = False
    benefits: List[MembershipBenefitSchema] = []
    max_members: Optional[int] = None
    display_order: int = 0


class MembershipTierCreate(MembershipTierBase):
    """Schema for creating membership tier."""
    pass


class MembershipTierUpdate(BaseModel):
    """Schema for updating membership tier."""
    name: Optional[str] = None
    description: Optional[str] = None
    monthly_price: Optional[Decimal] = None
    annual_price: Optional[Decimal] = None
    billing_cycle: Optional[str] = None
    discount_percentage: Optional[int] = None
    priority_booking: Optional[bool] = None
    exclusive_services: Optional[List[str]] = None
    free_services_per_month: Optional[int] = None
    rollover_unused: Optional[bool] = None
    benefits: Optional[List[MembershipBenefitSchema]] = None
    is_active: Optional[bool] = None
    max_members: Optional[int] = None
    display_order: Optional[int] = None


class MembershipTierResponse(MembershipTierBase):
    """Schema for membership tier response."""
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MembershipCreate(BaseModel):
    """Schema for creating membership subscription."""
    customer_id: str
    tier_id: str
    payment_method_id: Optional[str] = None
    start_date: Optional[datetime] = None


class MembershipUpdate(BaseModel):
    """Schema for updating membership."""
    status: Optional[str] = None
    payment_method_id: Optional[str] = None
    pause_reason: Optional[str] = None
    resume_date: Optional[datetime] = None
    cancellation_reason: Optional[str] = None


class MembershipResponse(BaseModel):
    """Schema for membership response."""
    id: str
    customer_id: str
    tier_id: str
    tier_name: str
    status: str
    start_date: datetime
    end_date: Optional[datetime] = None
    next_billing_date: datetime
    last_payment_date: Optional[datetime] = None
    last_payment_amount: Optional[Decimal] = None
    services_used_this_cycle: int
    services_remaining_this_cycle: int
    rollover_services: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MembershipTransactionResponse(BaseModel):
    """Schema for membership transaction response."""
    id: str
    membership_id: str
    customer_id: str
    transaction_type: str
    amount: Decimal
    status: str
    payment_method: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
