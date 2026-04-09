"""Service for managing video testimonials"""

from typing import List, Optional
from bson import ObjectId
from datetime import datetime

from app.models.video_testimonial import VideoTestimonial


class VideoTestimonialService:
    """Service for video testimonial management"""
    
    @staticmethod
    def create_testimonial(
        tenant_id: ObjectId,
        customer_name: str,
        video_url: str,
        thumbnail_url: Optional[str] = None,
        testimonial_text: Optional[str] = None,
        rating: int = 5,
        display_order: int = 0
    ) -> VideoTestimonial:
        """Create a new video testimonial"""
        testimonial = VideoTestimonial(
            tenant_id=tenant_id,
            customer_name=customer_name,
            video_url=video_url,
            thumbnail_url=thumbnail_url,
            testimonial_text=testimonial_text,
            rating=rating,
            display_order=display_order,
            is_active=True
        )
        testimonial.save()
        return testimonial
    
    @staticmethod
    def get_testimonials(
        tenant_id: ObjectId,
        is_active: Optional[bool] = True,
        limit: int = 10
    ) -> List[VideoTestimonial]:
        """Get video testimonials for a tenant"""
        query = {"tenant_id": tenant_id}
        
        if is_active is not None:
            query["is_active"] = is_active
        
        return VideoTestimonial.objects(**query).order_by("display_order", "-created_at").limit(limit)
    
    @staticmethod
    def get_testimonial(testimonial_id: ObjectId) -> Optional[VideoTestimonial]:
        """Get a single video testimonial by ID"""
        return VideoTestimonial.objects(id=testimonial_id).first()
    
    @staticmethod
    def update_testimonial(
        testimonial_id: ObjectId,
        customer_name: Optional[str] = None,
        video_url: Optional[str] = None,
        thumbnail_url: Optional[str] = None,
        testimonial_text: Optional[str] = None,
        rating: Optional[int] = None,
        is_active: Optional[bool] = None,
        display_order: Optional[int] = None
    ) -> Optional[VideoTestimonial]:
        """Update a video testimonial"""
        testimonial = VideoTestimonial.objects(id=testimonial_id).first()
        
        if not testimonial:
            return None
        
        if customer_name is not None:
            testimonial.customer_name = customer_name
        if video_url is not None:
            testimonial.video_url = video_url
        if thumbnail_url is not None:
            testimonial.thumbnail_url = thumbnail_url
        if testimonial_text is not None:
            testimonial.testimonial_text = testimonial_text
        if rating is not None:
            testimonial.rating = rating
        if is_active is not None:
            testimonial.is_active = is_active
        if display_order is not None:
            testimonial.display_order = display_order
        
        testimonial.updated_at = datetime.utcnow()
        testimonial.save()
        
        return testimonial
    
    @staticmethod
    def delete_testimonial(testimonial_id: ObjectId) -> bool:
        """Delete a video testimonial"""
        testimonial = VideoTestimonial.objects(id=testimonial_id).first()
        
        if not testimonial:
            return False
        
        testimonial.delete()
        return True
