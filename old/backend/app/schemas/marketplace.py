"""
Marketplace schemas for MongoDB collections
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class MarketplaceBooking(BaseModel):
    """Marketplace booking schema"""
    _id: Optional[str] = None
    tenant_id: str
    guest_id: Optional[str] = None
    guest_email: str
    guest_phone: str
    guest_name: str
    service_id: str
    service_name: str
    stylist_id: Optional[str] = None
    stylist_name: Optional[str] = None
    booking_date: str
    booking_time: str
    duration_minutes: int
    price: float
    discount_percentage: float = 0.0
    final_price: float
    payment_method: str  # "cash", "online"
    payment_status: str  # "pending", "completed", "failed"
    booking_status: str  # "confirmed", "completed", "cancelled", "no-show"
    reference_number: str
    magic_token: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    cancelled_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class GuestAccount(BaseModel):
    """Guest account schema"""
    _id: Optional[str] = None
    email: str
    phone: str
    name: str
    magic_token: Optional[str] = None
    magic_token_expires: Optional[datetime] = None
    is_authenticated: bool = False
    bookings: List[str] = []  # booking IDs
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None


class CommissionTransaction(BaseModel):
    """Commission transaction schema"""
    _id: Optional[str] = None
    tenant_id: str
    booking_id: str
    booking_reference: str
    amount: float
    commission_rate: float
    commission_amount: float
    platform_fee: float
    net_amount: float
    transaction_type: str  # "booking", "refund", "adjustment"
    status: str  # "pending", "completed", "failed"
    payment_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SalonPortfolio(BaseModel):
    """Salon portfolio schema"""
    _id: Optional[str] = None
    tenant_id: str
    title: str
    description: Optional[str] = None
    before_image_url: str
    after_image_url: str
    service_category: str
    stylist_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ReferralTracking(BaseModel):
    """Referral tracking schema"""
    _id: Optional[str] = None
    referral_code: str
    tenant_id: str
    source_page: str  # "landing", "salon_detail", etc.
    visitor_id: Optional[str] = None
    visitor_email: Optional[str] = None
    clicked_at: datetime = Field(default_factory=datetime.utcnow)
    converted: bool = False
    conversion_booking_id: Optional[str] = None
    converted_at: Optional[datetime] = None
    commission_earned: float = 0.0


class MarketplaceSettings(BaseModel):
    """Marketplace settings for tenant"""
    _id: Optional[str] = None
    tenant_id: str
    is_marketplace_enabled: bool = True
    commission_rate: float = 0.15  # 15% default
    online_payment_discount: float = 0.05  # 5% discount
    allow_guest_bookings: bool = True
    magic_link_expiry_hours: int = 24
    auto_confirm_bookings: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
