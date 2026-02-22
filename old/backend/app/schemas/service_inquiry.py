"""
Service Inquiry schemas
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum
from app.schemas.base import BaseSchema


class InquiryStatus(str, Enum):
    """Service inquiry status"""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    DECLINED = "declined"
    EXPIRED = "expired"
    CONVERTED = "converted"


class ServiceInquiryCreate(BaseModel):
    """Service inquiry creation request"""
    client_name: str = Field(..., min_length=2, max_length=100)
    client_phone: str = Field(..., min_length=10, max_length=20)
    client_email: Optional[EmailStr] = None
    description: str = Field(..., min_length=10, max_length=1000, description="Service description")
    image_urls: List[str] = Field(default_factory=list, max_items=3, description="Up to 3 reference images")
    preferred_date: Optional[str] = Field(None, description="Preferred date in YYYY-MM-DD format")


class ServiceInquiryResponse(BaseModel):
    """Service inquiry response from salon"""
    can_do_service: bool = Field(..., description="Whether salon can provide the service")
    estimated_price: Optional[float] = Field(None, ge=0, description="Estimated price in Naira")
    estimated_duration: Optional[int] = Field(None, ge=15, description="Estimated duration in minutes")
    suggested_stylist_id: Optional[str] = Field(None, description="Suggested stylist ID")
    response_message: str = Field(..., min_length=10, max_length=500, description="Response message to client")
    custom_service_name: Optional[str] = Field(None, max_length=100, description="Custom service name if approved")


class ServiceInquiry(BaseSchema):
    """Service inquiry model"""
    id: str
    tenant_id: str
    client_name: str
    client_phone: str
    client_email: Optional[str] = None
    description: str
    image_urls: List[str]
    preferred_date: Optional[str] = None
    status: InquiryStatus
    salon_response: Optional[ServiceInquiryResponse] = None
    booking_id: Optional[str] = Field(None, description="Linked booking ID if converted")
    created_at: datetime
    updated_at: datetime
    responded_at: Optional[datetime] = None
    expires_at: datetime


class ServiceInquiryFilter(BaseModel):
    """Service inquiry filter parameters"""
    status: Optional[InquiryStatus] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
