"""Routes for social proof features."""

from fastapi import APIRouter, HTTPException, Request, Depends
from bson import ObjectId
from typing import List, Optional

from app.schemas.social_proof import (
    BookingActivityResponse,
    SocialMediaFeedResponse,
    InstagramFeedSync,
    VideoTestimonialCreate,
    VideoTestimonialUpdate,
    VideoTestimonialResponse
)
from app.services.booking_activity_service import BookingActivityService
from app.services.social_media_service import SocialMediaService
from app.services.video_testimonial_service import VideoTestimonialService
from app.middleware.tenant_context import get_tenant_id

router = APIRouter(prefix="/social-proof", tags=["Social Proof"])


@router.get("/recent-bookings", response_model=List[BookingActivityResponse])
async def get_recent_bookings(
    request: Request,
    limit: int = 10,
    hours: int = 24
):
    """Get recent booking activities for social proof display"""
    tenant_id = get_tenant_id(request)
    
    activities = BookingActivityService.get_recent_activities(
        tenant_id=tenant_id,
        limit=limit,
        hours=hours
    )
    
    return [activity.to_dict() for activity in activities]


@router.get("/social-feed", response_model=List[SocialMediaFeedResponse])
async def get_social_feed(
    request: Request,
    platform: Optional[str] = None,
    limit: int = 12
):
    """Get social media feed posts"""
    tenant_id = get_tenant_id(request)
    
    if platform and platform not in ['instagram', 'facebook', 'twitter']:
        raise HTTPException(status_code=400, detail="Invalid platform")
    
    feeds = SocialMediaService.get_feed_posts(
        tenant_id=tenant_id,
        platform=platform,
        limit=limit
    )
    
    return [feed.to_dict() for feed in feeds]


@router.post("/sync-instagram")
async def sync_instagram_feed(
    request: Request,
    sync_data: InstagramFeedSync
):
    """Sync Instagram feed (Owner only)"""
    tenant_id = get_tenant_id(request)
    
    feeds = SocialMediaService.sync_instagram_feed(
        tenant_id=tenant_id,
        access_token=sync_data.access_token,
        user_id=sync_data.user_id,
        limit=sync_data.limit
    )
    
    return {
        "message": f"Successfully synced {len(feeds)} Instagram posts",
        "count": len(feeds)
    }


@router.patch("/social-feed/{post_id}/toggle")
async def toggle_post_visibility(
    request: Request,
    post_id: str,
    is_active: bool
):
    """Toggle visibility of a social media post (Owner only)"""
    tenant_id = get_tenant_id(request)
    
    feed = SocialMediaService.toggle_post_visibility(
        post_id=ObjectId(post_id),
        is_active=is_active
    )
    
    if not feed:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Verify tenant
    if feed.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return {"message": "Post visibility updated"}


@router.delete("/social-feed/{post_id}")
async def delete_social_post(
    request: Request,
    post_id: str
):
    """Delete a social media post (Owner only)"""
    tenant_id = get_tenant_id(request)
    
    # Verify post belongs to tenant before deleting
    feed = SocialMediaService.get_feed_posts(tenant_id=tenant_id, limit=1000)
    post_exists = any(str(f.id) == post_id for f in feed)
    
    if not post_exists:
        raise HTTPException(status_code=404, detail="Post not found")
    
    success = SocialMediaService.delete_post(ObjectId(post_id))
    
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return {"message": "Post deleted successfully"}


# Video Testimonials Endpoints

@router.get("/video-testimonials", response_model=List[VideoTestimonialResponse])
async def get_video_testimonials(
    request: Request,
    is_active: Optional[bool] = True,
    limit: int = 10
):
    """Get video testimonials for public display"""
    tenant_id = get_tenant_id(request)
    
    testimonials = VideoTestimonialService.get_testimonials(
        tenant_id=tenant_id,
        is_active=is_active,
        limit=limit
    )
    
    return [testimonial.to_dict() for testimonial in testimonials]


@router.post("/video-testimonials", response_model=VideoTestimonialResponse)
async def create_video_testimonial(
    request: Request,
    testimonial_data: VideoTestimonialCreate
):
    """Create a new video testimonial (Owner only)"""
    tenant_id = get_tenant_id(request)
    
    testimonial = VideoTestimonialService.create_testimonial(
        tenant_id=tenant_id,
        customer_name=testimonial_data.customer_name,
        video_url=testimonial_data.video_url,
        thumbnail_url=testimonial_data.thumbnail_url,
        testimonial_text=testimonial_data.testimonial_text,
        rating=testimonial_data.rating,
        display_order=testimonial_data.display_order
    )
    
    return testimonial.to_dict()


@router.patch("/video-testimonials/{testimonial_id}", response_model=VideoTestimonialResponse)
async def update_video_testimonial(
    request: Request,
    testimonial_id: str,
    testimonial_data: VideoTestimonialUpdate
):
    """Update a video testimonial (Owner only)"""
    tenant_id = get_tenant_id(request)
    
    # Verify testimonial belongs to tenant
    testimonial = VideoTestimonialService.get_testimonial(ObjectId(testimonial_id))
    if not testimonial or testimonial.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Testimonial not found")
    
    updated = VideoTestimonialService.update_testimonial(
        testimonial_id=ObjectId(testimonial_id),
        customer_name=testimonial_data.customer_name,
        video_url=testimonial_data.video_url,
        thumbnail_url=testimonial_data.thumbnail_url,
        testimonial_text=testimonial_data.testimonial_text,
        rating=testimonial_data.rating,
        is_active=testimonial_data.is_active,
        display_order=testimonial_data.display_order
    )
    
    if not updated:
        raise HTTPException(status_code=404, detail="Testimonial not found")
    
    return updated.to_dict()


@router.delete("/video-testimonials/{testimonial_id}")
async def delete_video_testimonial(
    request: Request,
    testimonial_id: str
):
    """Delete a video testimonial (Owner only)"""
    tenant_id = get_tenant_id(request)
    
    # Verify testimonial belongs to tenant
    testimonial = VideoTestimonialService.get_testimonial(ObjectId(testimonial_id))
    if not testimonial or testimonial.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Testimonial not found")
    
    success = VideoTestimonialService.delete_testimonial(ObjectId(testimonial_id))
    
    if not success:
        raise HTTPException(status_code=404, detail="Testimonial not found")
    
    return {"message": "Testimonial deleted successfully"}
