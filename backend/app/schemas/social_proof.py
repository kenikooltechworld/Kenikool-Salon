"""Schemas for social proof features."""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime


class BookingActivityResponse(BaseModel):
    """Response schema for booking activity"""
    id: str
    customer_name: str
    service_name: str
    booking_type: str
    created_at: str


class SocialMediaFeedResponse(BaseModel):
    """Response schema for social media feed"""
    id: str
    platform: str
    post_id: str
    media_url: HttpUrl
    media_type: str
    caption: Optional[str] = None
    permalink: Optional[HttpUrl] = None
    likes_count: int = 0
    comments_count: int = 0
    published_at: str


class VideoTestimonialCreate(BaseModel):
    """Schema for creating video testimonial"""
    customer_name: str = Field(..., max_length=100)
    video_url: HttpUrl
    thumbnail_url: Optional[HttpUrl] = None
    rating: int = Field(..., ge=1, le=5)
    testimonial_text: Optional[str] = Field(None, max_length=500)
    service_name: Optional[str] = Field(None, max_length=200)
    is_featured: bool = False


class VideoTestimonialUpdate(BaseModel):
    """Schema for updating video testimonial"""
    customer_name: Optional[str] = Field(None, max_length=100)
    video_url: Optional[HttpUrl] = None
    thumbnail_url: Optional[HttpUrl] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    testimonial_text: Optional[str] = Field(None, max_length=500)
    service_name: Optional[str] = Field(None, max_length=200)
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None


class VideoTestimonialResponse(BaseModel):
    """Response schema for video testimonial"""
    id: str
    customer_name: str
    video_url: HttpUrl
    thumbnail_url: Optional[HttpUrl] = None
    rating: int
    testimonial_text: Optional[str] = None
    service_name: Optional[str] = None
    is_featured: bool
    is_active: bool
    created_at: str
    views_count: int = 0


class InstagramFeedSync(BaseModel):
    """Schema for syncing Instagram feed"""
    access_token: str
    user_id: str
    limit: int = Field(default=12, ge=1, le=50)
