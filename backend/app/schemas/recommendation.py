"""Recommendation schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CustomerPreferenceResponse(BaseModel):
    """Customer preference response"""
    id: str
    customer_id: str
    preferred_service_categories: List[str]
    preferred_services: List[str]
    preferred_staff: List[str]
    preferred_time_slots: List[str]
    preferred_days: List[str]
    average_booking_frequency_days: Optional[int]
    average_spend: Optional[float]
    last_booking_date: Optional[datetime]
    total_bookings: int
    
    class Config:
        from_attributes = True


class RecommendationResponse(BaseModel):
    """Service recommendation response"""
    id: str
    service_id: str
    service_name: str
    service_description: str
    service_price: float
    service_duration: int
    service_image_url: Optional[str]
    
    staff_id: Optional[str]
    staff_name: Optional[str]
    
    confidence_score: float
    recommendation_type: str
    reasoning: str
    
    class Config:
        from_attributes = True


class RecommendationRequest(BaseModel):
    """Request for recommendations"""
    customer_id: Optional[str] = None
    limit: int = Field(default=5, ge=1, le=20)
    include_staff: bool = True


class RecommendationFeedback(BaseModel):
    """Feedback on recommendation"""
    recommendation_id: str
    action: str  # "clicked", "booked", "dismissed"
