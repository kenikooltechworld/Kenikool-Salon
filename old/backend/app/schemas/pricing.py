"""
Pricing schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, time


class PricingRuleCreate(BaseModel):
    """Pricing rule creation request"""
    name: str = Field(..., min_length=2, max_length=100)
    rule_type: str = Field(..., description="demand, time_of_day, day_of_week, seasonal")
    service_ids: List[str] = Field(default_factory=list, description="Service IDs to apply rule to (empty = all)")
    multiplier: float = Field(..., ge=0.1, le=5.0, description="Price multiplier (e.g., 1.5 = 150%)")
    
    # Time-based conditions
    start_time: Optional[str] = Field(None, description="Start time (HH:MM)")
    end_time: Optional[str] = Field(None, description="End time (HH:MM)")
    days_of_week: List[int] = Field(default_factory=list, description="Days of week (0=Monday, 6=Sunday)")
    
    # Demand-based conditions
    min_bookings: Optional[int] = Field(None, description="Minimum bookings threshold")
    max_bookings: Optional[int] = Field(None, description="Maximum bookings threshold")
    
    # Date-based conditions
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    
    enabled: bool = Field(True, description="Whether rule is active")
    priority: int = Field(0, description="Rule priority (higher = applied first)")


class PricingRuleUpdate(BaseModel):
    """Pricing rule update request"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    multiplier: Optional[float] = Field(None, ge=0.1, le=5.0)
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    days_of_week: Optional[List[int]] = None
    min_bookings: Optional[int] = None
    max_bookings: Optional[int] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    enabled: Optional[bool] = None
    priority: Optional[int] = None


class PricingRuleResponse(BaseModel):
    """Pricing rule response"""
    id: str
    tenant_id: str
    name: str
    rule_type: str
    service_ids: List[str]
    multiplier: float
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    days_of_week: List[int]
    min_bookings: Optional[int] = None
    max_bookings: Optional[int] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    enabled: bool
    priority: int
    created_at: datetime
    updated_at: datetime


class PriceCalculationRequest(BaseModel):
    """Price calculation request"""
    service_id: str
    booking_date: str = Field(..., description="Booking date (YYYY-MM-DD)")
    booking_time: str = Field(..., description="Booking time (HH:MM)")


class PriceCalculationResponse(BaseModel):
    """Price calculation response"""
    service_id: str
    base_price: float
    final_price: float
    applied_rules: List[dict]
    total_multiplier: float
