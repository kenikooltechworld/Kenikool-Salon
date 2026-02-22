"""
Review schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class ReviewBase(BaseModel):
    """Base review schema"""
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    comment: Optional[str] = Field(None, description="Optional review comment")

class ReviewCreate(ReviewBase):
    """Review creation schema"""
    booking_id: str = Field(..., description="ID of the completed booking")
    client_id: str = Field(..., description="ID of the client")

class ReviewModerate(BaseModel):
    """Review moderation schema"""
    status: str = Field(..., description="Review status: pending, approved, or rejected")

class ReviewResponseData(BaseModel):
    """Review response data"""
    text: str = Field(..., description="Response text")
    responder_id: Optional[str] = Field(None, description="ID of responder")
    responder_name: Optional[str] = Field(None, description="Name of responder")
    responded_at: Optional[datetime] = Field(None, description="When response was added")
    edited_at: Optional[datetime] = Field(None, description="When response was last edited")

class PhotoData(BaseModel):
    """Photo data"""
    id: str = Field(..., description="Photo ID")
    url: str = Field(..., description="Photo URL")
    uploaded_at: datetime = Field(..., description="When photo was uploaded")

class FlagData(BaseModel):
    """Flag data"""
    reason: str = Field(..., description="Flag reason: spam, offensive, fake")
    flagged_by: str = Field(..., description="ID of user who flagged")
    flagged_at: datetime = Field(..., description="When review was flagged")

class EditHistoryData(BaseModel):
    """Edit history data"""
    original_text: str = Field(..., description="Original comment text")
    edited_text: str = Field(..., description="Edited comment text")
    edited_by: str = Field(..., description="ID of user who edited")
    edited_at: datetime = Field(..., description="When edit was made")

class ReviewResponse(ReviewBase):
    """Review response schema"""
    id: str = Field(..., alias="_id")
    tenant_id: str
    booking_id: str
    client_id: str
    client_name: str
    service_id: str
    service_name: str
    stylist_id: str
    stylist_name: str
    status: str = Field(..., description="Review status: pending, approved, or rejected")
    response: Optional[ReviewResponseData] = Field(None, description="Owner response to review")
    photos: Optional[List[PhotoData]] = Field(None, description="Review photos")
    flags: Optional[List[FlagData]] = Field(None, description="Review flags")
    helpful_votes: Optional[List[str]] = Field(None, description="User IDs who voted helpful")
    edit_history: Optional[List[EditHistoryData]] = Field(None, description="Edit history")
    is_deleted: Optional[bool] = Field(False, description="Whether review is soft-deleted")
    deleted_by: Optional[str] = Field(None, description="ID of user who deleted")
    deleted_at: Optional[datetime] = Field(None, description="When review was deleted")
    deletion_reason: Optional[str] = Field(None, description="Reason for deletion")
    reminder_sent: Optional[bool] = Field(False, description="Whether reminder was sent")
    reminder_sent_at: Optional[datetime] = Field(None, description="When reminder was sent")
    points_awarded: Optional[bool] = Field(False, description="Whether points were awarded")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True

class ReviewListResponse(BaseModel):
    """Review list response schema"""
    reviews: List[ReviewResponse]
    total: int
    skip: int
    limit: int

class RatingDistribution(BaseModel):
    """Rating distribution schema"""
    rating_1: int = Field(..., alias="1")
    rating_2: int = Field(..., alias="2")
    rating_3: int = Field(..., alias="3")
    rating_4: int = Field(..., alias="4")
    rating_5: int = Field(..., alias="5")
    
    class Config:
        populate_by_name = True

class RatingAggregation(BaseModel):
    """Rating aggregation response schema"""
    average_rating: float = Field(..., description="Average rating (0-5)")
    total_reviews: int = Field(..., description="Total number of approved reviews")
    rating_distribution: Dict[str, int] = Field(..., description="Distribution of ratings by star count")

class FilterCounts(BaseModel):
    """Filter counts response schema"""
    status: Dict[str, int] = Field(..., description="Count by status")
    rating: Dict[str, int] = Field(..., description="Count by rating")
    services: Dict[str, int] = Field(..., description="Count by service")
    stylists: Dict[str, int] = Field(..., description="Count by stylist")
    has_response: int = Field(..., description="Count of reviews with responses")
    has_photos: int = Field(..., description="Count of reviews with photos")
    is_flagged: int = Field(..., description="Count of flagged reviews")
    total: int = Field(..., description="Total review count")

class ReviewResponseCreate(BaseModel):
    """Create review response schema"""
    text: str = Field(..., max_length=500, description="Response text (max 500 characters)")

class ReviewResponseUpdate(BaseModel):
    """Update review response schema"""
    text: str = Field(..., max_length=500, description="Response text (max 500 characters)")

class ResponseTemplate(BaseModel):
    """Response template schema"""
    id: str = Field(..., alias="_id")
    name: str = Field(..., description="Template name")
    category: str = Field(..., description="Template category: positive, negative, neutral")
    text: str = Field(..., description="Template text")
    is_default: bool = Field(False, description="Whether this is a default template")
    
    class Config:
        populate_by_name = True

class ResponseTemplateCreate(BaseModel):
    """Create response template schema"""
    name: str = Field(..., description="Template name")
    category: str = Field(..., description="Template category: positive, negative, neutral")
    text: str = Field(..., description="Template text")

class ResponseTemplateUpdate(BaseModel):
    """Update response template schema"""
    name: Optional[str] = Field(None, description="Template name")
    category: Optional[str] = Field(None, description="Template category")
    text: Optional[str] = Field(None, description="Template text")

