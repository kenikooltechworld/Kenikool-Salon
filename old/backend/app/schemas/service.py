"""
Service schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.schemas.base import BaseSchema


class BookingRules(BaseModel):
    """Booking rules for a service"""
    buffer_time_before: int = Field(default=0, ge=0, description="Buffer time before booking in minutes")
    buffer_time_after: int = Field(default=0, ge=0, description="Buffer time after booking in minutes")
    max_bookings_per_day: int = Field(default=0, ge=0, description="Maximum bookings per day (0 = unlimited)")
    advance_booking_min: int = Field(default=0, ge=0, description="Minimum days in advance for booking")
    advance_booking_max: int = Field(default=365, ge=1, description="Maximum days in advance for booking")
    cancellation_deadline: int = Field(default=24, ge=0, description="Cancellation deadline in hours")
    cancellation_penalty: float = Field(default=0.0, ge=0, le=100, description="Cancellation penalty percentage")
    allow_override: bool = Field(default=True, description="Allow manager override of rules")

    class Config:
        populate_by_name = True


class ServiceAvailability(BaseModel):
    """Service availability configuration"""
    days_of_week: List[int] = Field(default=[0, 1, 2, 3, 4, 5, 6], description="Available days (0=Sunday, 6=Saturday)")
    time_ranges: List[Dict[str, str]] = Field(default=[], description="Available time ranges [{start: 'HH:MM', end: 'HH:MM'}]")
    seasonal_ranges: List[Dict[str, str]] = Field(default=[], description="Seasonal date ranges [{start: 'YYYY-MM-DD', end: 'YYYY-MM-DD'}]")
    is_limited_time: bool = Field(default=False, description="Is this a limited time offer")
    limited_time_end: Optional[datetime] = Field(default=None, description="Limited time offer end date")

    class Config:
        populate_by_name = True


class CommissionStructure(BaseModel):
    """Commission structure for a service"""
    commission_type: str = Field(default="percentage", description="Type: 'percentage' or 'fixed'")
    default_rate: float = Field(default=0.0, ge=0, description="Default commission rate (percentage or fixed amount)")
    stylist_overrides: Dict[str, float] = Field(default={}, description="Stylist-specific commission overrides {stylist_id: rate}")
    
    class Config:
        populate_by_name = True


class SEOMetadata(BaseModel):
    """SEO metadata for a service"""
    meta_title: Optional[str] = Field(default=None, max_length=60, description="SEO meta title")
    meta_description: Optional[str] = Field(default=None, max_length=160, description="SEO meta description")
    keywords: List[str] = Field(default=[], description="SEO keywords")
    
    class Config:
        populate_by_name = True


class MarketingSettings(BaseModel):
    """Marketing settings for a service"""
    is_featured: bool = Field(default=False, description="Display service prominently")
    promotional_banner: Optional[str] = Field(default=None, description="Promotional banner text")
    visibility: str = Field(default="public", description="Visibility: 'public', 'private', 'members_only'")
    is_new: bool = Field(default=False, description="Show 'New' badge")
    new_until: Optional[datetime] = Field(default=None, description="Show 'New' badge until this date")
    seo_metadata: Optional[SEOMetadata] = None
    
    class Config:
        populate_by_name = True


class LocationPricing(BaseModel):
    """Location-specific pricing for a service"""
    location_id: str = Field(..., description="Location ID")
    price: float = Field(..., ge=0, description="Service price at this location")
    duration_minutes: Optional[int] = Field(None, ge=1, description="Service duration at this location")
    
    class Config:
        populate_by_name = True
        extra = "allow"  # Allow extra fields for flexibility


class ServiceCreate(BaseModel):
    """Service creation request"""
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    duration_minutes: int = Field(..., gt=0)
    category: Optional[str] = None
    assigned_stylists: List[str] = []
    tiered_pricing: Optional[List[Dict[str, Any]]] = None
    booking_rules: Optional[BookingRules] = None
    availability: Optional[ServiceAvailability] = None
    max_concurrent_bookings: int = Field(default=0, ge=0, description="Max concurrent bookings (0 = unlimited)")
    commission_structure: Optional[CommissionStructure] = None
    required_resources: Optional[List[Dict[str, Any]]] = Field(default=[], description="Required resources [{name, quantity, unit}]")
    marketing_settings: Optional[MarketingSettings] = None
    prerequisite_services: Optional[List[str]] = Field(default=[], description="Service IDs that must be completed first")
    mandatory_addons: Optional[List[str]] = Field(default=[], description="Service IDs that are automatically included")
    available_at_locations: List[str] = Field(default_factory=list, description="List of location IDs where service is available")
    location_pricing: Optional[List[LocationPricing]] = Field(
        default_factory=list,
        description="Location-specific pricing"
    )


class ServiceUpdate(BaseModel):
    """Service update request"""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    duration_minutes: Optional[int] = Field(None, gt=0)
    category: Optional[str] = None
    is_active: Optional[bool] = None
    assigned_stylists: Optional[List[str]] = None
    tiered_pricing: Optional[List[Dict[str, Any]]] = None
    booking_rules: Optional[BookingRules] = None
    availability: Optional[ServiceAvailability] = None
    max_concurrent_bookings: Optional[int] = Field(None, ge=0)
    commission_structure: Optional[CommissionStructure] = None
    required_resources: Optional[List[Dict[str, Any]]] = None
    marketing_settings: Optional[MarketingSettings] = None
    prerequisite_services: Optional[List[str]] = None
    mandatory_addons: Optional[List[str]] = None
    available_at_locations: Optional[List[str]] = None
    location_pricing: Optional[List[LocationPricing]] = None


class ServiceResponse(BaseSchema):
    """Service response"""
    id: str
    tenant_id: str
    name: str
    description: Optional[str]
    price: float
    duration_minutes: int
    category: Optional[str]
    photo_url: Optional[str]
    is_active: bool
    assigned_stylists: List[str]
    tiered_pricing: Optional[List[Dict[str, Any]]] = None
    booking_rules: Optional[BookingRules] = None
    availability: Optional[ServiceAvailability] = None
    max_concurrent_bookings: int
    commission_structure: Optional[CommissionStructure] = None
    required_resources: Optional[List[Dict[str, Any]]] = Field(default=[], description="Required resources [{name, quantity, unit}]")
    marketing_settings: Optional[MarketingSettings] = None
    prerequisite_services: Optional[List[str]] = Field(default=[], description="Service IDs that must be completed first")
    mandatory_addons: Optional[List[str]] = Field(default=[], description="Service IDs that are automatically included")
    available_at_locations: List[str] = []
    location_pricing: Optional[List[LocationPricing]] = None
    created_at: datetime
    updated_at: datetime


class ServiceFilter(BaseModel):
    """Service filter parameters"""
    is_active: Optional[bool] = None
    category: Optional[str] = None


class ServiceStatistics(BaseModel):
    """Service statistics response"""
    total_bookings: int = Field(alias="totalBookings")
    completed_bookings: int = Field(alias="completedBookings")
    cancelled_bookings: int = Field(alias="cancelledBookings")
    total_revenue: float = Field(alias="totalRevenue")
    average_booking_value: float = Field(alias="averageBookingValue")
    revenue_trend: Optional[float] = Field(alias="revenueTrend")
    popularity_rank: int = Field(alias="popularityRank")
    average_rating: float = Field(alias="averageRating")
    conversion_rate: float = Field(alias="conversionRate")

    class Config:
        populate_by_name = True
        by_alias = True


class ServiceDetailsResponse(BaseModel):
    """Service details with statistics response"""
    service: ServiceResponse
    statistics: ServiceStatistics

    class Config:
        populate_by_name = True


class RevenueChartData(BaseModel):
    """Revenue chart data point"""
    date: str
    revenue: float


class BookingTrendData(BaseModel):
    """Booking trend data"""
    current_month: int = Field(alias="currentMonth")
    previous_month: int = Field(alias="previousMonth")
    trend: float

    class Config:
        populate_by_name = True
        by_alias = True


class ServiceAnalyticsResponse(BaseModel):
    """Service analytics response"""
    revenue_chart: List[RevenueChartData] = Field(alias="revenueChart")
    booking_trend: BookingTrendData = Field(alias="bookingTrend")
    peak_times: Dict[str, int] = Field(alias="peakTimes")
    popularity_rank: int = Field(alias="popularityRank")
    average_rating: float = Field(alias="averageRating")
    conversion_rate: float = Field(alias="conversionRate")

    class Config:
        populate_by_name = True
        by_alias = True
