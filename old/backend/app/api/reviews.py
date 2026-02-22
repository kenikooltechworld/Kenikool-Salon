"""
Review management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse, FileResponse
from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from io import BytesIO

from app.api.dependencies import get_current_user, require_roles, get_database
from app.schemas.review import (
    ReviewCreate,
    ReviewModerate,
    ReviewResponse,
    ReviewListResponse,
    RatingAggregation,
    ReviewResponseCreate,
    ReviewResponseUpdate,
    ResponseTemplate,
    ResponseTemplateCreate,
    ResponseTemplateUpdate
)
from app.services.review_service import ReviewService
from app.services.review_analytics_service import ReviewAnalyticsService

router = APIRouter(prefix="/api/reviews", tags=["reviews"])


@router.get("/aggregation", response_model=RatingAggregation)
async def get_rating_aggregation(
    service_id: Optional[str] = None,
    stylist_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get rating aggregation for tenant, service, or stylist"""
    try:
        tenant_id = current_user.get("tenant_id")
        service = ReviewService(db)
        
        aggregation = await service.get_rating_aggregation(
            tenant_id=tenant_id,
            service_id=service_id,
            stylist_id=stylist_id
        )
        
        return aggregation
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=ReviewListResponse)
async def get_reviews(
    status: Optional[str] = None,
    rating: Optional[List[int]] = Query(None),
    service_id: Optional[str] = None,
    stylist_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    has_response: Optional[bool] = None,
    has_photos: Optional[bool] = None,
    is_flagged: Optional[bool] = None,
    search: Optional[str] = None,
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get reviews with advanced filtering and search"""
    try:
        tenant_id = current_user.get("tenant_id")
        service = ReviewService(db)
        
        result = await service.get_reviews_filtered(
            tenant_id=tenant_id,
            status=status,
            rating=rating,
            service_id=service_id,
            stylist_id=stylist_id,
            start_date=start_date,
            end_date=end_date,
            has_response=has_response,
            has_photos=has_photos,
            is_flagged=is_flagged,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            skip=skip,
            limit=limit
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("", response_model=ReviewResponse)
async def create_review(
    review_data: ReviewCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Create a new review"""
    try:
        tenant_id = current_user.get("tenant_id")
        service = ReviewService(db)
        
        review = await service.create_review(
            tenant_id=tenant_id,
            booking_id=review_data.booking_id,
            client_id=review_data.client_id,
            rating=review_data.rating,
            comment=review_data.comment
        )
        
        return review
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{review_id}", response_model=ReviewResponse)
async def moderate_review(
    review_id: str,
    moderation_data: ReviewModerate,
    current_user: dict = Depends(require_roles(["owner", "admin"])),
    db = Depends(get_database)
):
    """Moderate a review (approve or reject)"""
    try:
        tenant_id = current_user.get("tenant_id")
        service = ReviewService(db)
        
        review = await service.moderate_review(
            review_id=review_id,
            tenant_id=tenant_id,
            status=moderation_data.status
        )
        
        return review
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/aggregation", response_model=RatingAggregation)
async def get_rating_aggregation(
    service_id: Optional[str] = None,
    stylist_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get rating aggregation for tenant, service, or stylist"""
    try:
        tenant_id = current_user.get("tenant_id")
        service = ReviewService(db)
        
        aggregation = await service.get_rating_aggregation(
            tenant_id=tenant_id,
            service_id=service_id,
            stylist_id=stylist_id
        )
        
        return aggregation
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/filter-counts")
async def get_filter_counts(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get filter counts for all filter options"""
    try:
        tenant_id = current_user.get("tenant_id")
        service = ReviewService(db)
        
        counts = await service.get_filter_counts(tenant_id=tenant_id)
        
        return counts
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Response Endpoints
async def add_review_response(
    review_id: str,
    response_data: ReviewResponseCreate,
    current_user: dict = Depends(require_roles(["owner", "admin"])),
    db = Depends(get_database)
):
    """Add owner response to review"""
    try:
        tenant_id = current_user.get("tenant_id")
        user_id = current_user.get("id")
        user_name = current_user.get("name", "Owner")
        
        service = ReviewService(db)
        
        review = await service.add_response(
            review_id=review_id,
            tenant_id=tenant_id,
            responder_id=user_id,
            responder_name=user_name,
            response_text=response_data.text
        )
        
        return review
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{review_id}/response", response_model=ReviewResponse)
async def update_review_response(
    review_id: str,
    response_data: ReviewResponseUpdate,
    current_user: dict = Depends(require_roles(["owner", "admin"])),
    db = Depends(get_database)
):
    """Update existing review response"""
    try:
        tenant_id = current_user.get("tenant_id")
        user_id = current_user.get("id")
        user_name = current_user.get("name", "Owner")
        
        service = ReviewService(db)
        
        review = await service.update_response(
            review_id=review_id,
            tenant_id=tenant_id,
            responder_id=user_id,
            responder_name=user_name,
            response_text=response_data.text
        )
        
        return review
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{review_id}/response", response_model=ReviewResponse)
async def delete_review_response(
    review_id: str,
    current_user: dict = Depends(require_roles(["owner", "admin"])),
    db = Depends(get_database)
):
    """Delete review response"""
    try:
        tenant_id = current_user.get("tenant_id")
        
        service = ReviewService(db)
        
        review = await service.delete_response(
            review_id=review_id,
            tenant_id=tenant_id
        )
        
        return review
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Response Template Endpoints

@router.get("/templates", response_model=list[ResponseTemplate])
async def get_response_templates(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get response templates for tenant"""
    try:
        tenant_id = current_user.get("tenant_id")
        service = ReviewService(db)
        
        templates = await service.get_response_templates(tenant_id=tenant_id)
        
        return templates
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/templates", response_model=ResponseTemplate)
async def create_response_template(
    template_data: ResponseTemplateCreate,
    current_user: dict = Depends(require_roles(["owner", "admin"])),
    db = Depends(get_database)
):
    """Create custom response template"""
    try:
        tenant_id = current_user.get("tenant_id")
        service = ReviewService(db)
        
        template = await service.create_response_template(
            tenant_id=tenant_id,
            name=template_data.name,
            category=template_data.category,
            text=template_data.text
        )
        
        return template
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/templates/{template_id}", response_model=ResponseTemplate)
async def update_response_template(
    template_id: str,
    template_data: ResponseTemplateUpdate,
    current_user: dict = Depends(require_roles(["owner", "admin"])),
    db = Depends(get_database)
):
    """Update response template"""
    try:
        tenant_id = current_user.get("tenant_id")
        service = ReviewService(db)
        
        template = await service.update_response_template(
            template_id=template_id,
            tenant_id=tenant_id,
            name=template_data.name,
            category=template_data.category,
            text=template_data.text
        )
        
        return template
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/templates/{template_id}")
async def delete_response_template(
    template_id: str,
    current_user: dict = Depends(require_roles(["owner", "admin"])),
    db = Depends(get_database)
):
    """Delete response template"""
    try:
        tenant_id = current_user.get("tenant_id")
        service = ReviewService(db)
        
        await service.delete_response_template(
            template_id=template_id,
            tenant_id=tenant_id
        )
        
        return {"message": "Template deleted successfully"}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Bulk Actions Endpoints

@router.post("/bulk/moderate")
async def bulk_moderate_reviews(
    bulk_data: dict,
    current_user: dict = Depends(require_roles(["owner", "admin"])),
    db = Depends(get_database)
):
    """Bulk approve/reject/delete reviews"""
    try:
        tenant_id = current_user.get("tenant_id")
        
        # Validate request data
        review_ids = bulk_data.get("review_ids", [])
        action = bulk_data.get("action")
        
        if not review_ids or not isinstance(review_ids, list):
            raise HTTPException(status_code=400, detail="review_ids must be a non-empty list")
        
        if action not in ["approved", "rejected", "deleted"]:
            raise HTTPException(status_code=400, detail="action must be 'approved', 'rejected', or 'deleted'")
        
        service = ReviewService(db)
        
        result = await service.bulk_moderate_reviews(
            tenant_id=tenant_id,
            review_ids=review_ids,
            action=action
        )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




# Analytics Endpoints

@router.get("/analytics")
async def get_review_analytics(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    service_id: Optional[str] = None,
    stylist_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get review analytics and trends"""
    try:
        tenant_id = current_user.get("tenant_id")
        
        # Validate date range
        if start_date >= end_date:
            raise HTTPException(status_code=400, detail="start_date must be before end_date")
        
        service = ReviewAnalyticsService(db)
        
        analytics = await service.get_complete_analytics(
            tenant_id=tenant_id,
            start_date=start_date,
            end_date=end_date,
            service_id=service_id,
            stylist_id=stylist_id
        )
        
        return analytics
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Export Endpoints

@router.get("/export")
async def export_reviews(
    format: str = Query("csv", regex="^(csv|pdf)$"),
    status: Optional[str] = None,
    rating: Optional[List[int]] = Query(None),
    service_id: Optional[str] = None,
    stylist_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    has_response: Optional[bool] = None,
    has_photos: Optional[bool] = None,
    is_flagged: Optional[bool] = None,
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Export reviews to CSV or PDF format"""
    try:
        tenant_id = current_user.get("tenant_id")
        service = ReviewService(db)
        
        # Generate timestamp for filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        if format == "csv":
            # Export to CSV
            csv_content = await service.export_to_csv(
                tenant_id=tenant_id,
                status=status,
                rating=rating,
                service_id=service_id,
                stylist_id=stylist_id,
                start_date=start_date,
                end_date=end_date,
                has_response=has_response,
                has_photos=has_photos,
                is_flagged=is_flagged,
                search=search
            )
            
            # Return as downloadable file
            return StreamingResponse(
                iter([csv_content]),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=reviews_{timestamp}.csv"}
            )
        
        elif format == "pdf":
            # Export to PDF
            pdf_bytes = await service.export_to_pdf(
                tenant_id=tenant_id,
                status=status,
                rating=rating,
                service_id=service_id,
                stylist_id=stylist_id,
                start_date=start_date,
                end_date=end_date,
                has_response=has_response,
                has_photos=has_photos,
                is_flagged=is_flagged,
                search=search
            )
            
            # Return as downloadable file
            return StreamingResponse(
                iter([pdf_bytes]),
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename=reviews_{timestamp}.pdf"}
            )
        
        else:
            raise HTTPException(status_code=400, detail="Invalid format. Must be 'csv' or 'pdf'")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# Public Endpoints (No Authentication Required)

@router.get("/public/{tenant_id}", response_model=ReviewListResponse)
async def get_public_reviews(
    tenant_id: str,
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db = Depends(get_database)
):
    """Get public approved reviews for tenant (no auth required)"""
    try:
        service = ReviewService(db)
        
        # Only return approved reviews
        result = await service.get_reviews_filtered(
            tenant_id=tenant_id,
            status="approved",
            sort_by=sort_by,
            sort_order=sort_order,
            skip=skip,
            limit=limit
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/public/{tenant_id}/aggregation", response_model=RatingAggregation)
async def get_public_rating_aggregation(
    tenant_id: str,
    db = Depends(get_database)
):
    """Get public rating aggregation for tenant (no auth required)"""
    try:
        service = ReviewService(db)
        
        # Get aggregation for approved reviews only
        aggregation = await service.get_rating_aggregation(
            tenant_id=tenant_id
        )
        
        return aggregation
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/widget/{tenant_id}")
async def get_widget_reviews(
    tenant_id: str,
    limit: int = Query(5, ge=1, le=20),
    db = Depends(get_database)
):
    """Get reviews for embeddable widget (no auth required)"""
    try:
        service = ReviewService(db)
        
        # Get approved reviews for widget
        result = await service.get_reviews_filtered(
            tenant_id=tenant_id,
            status="approved",
            sort_by="created_at",
            sort_order="desc",
            skip=0,
            limit=limit
        )
        
        # Get aggregation stats
        stats = await service.get_rating_aggregation(tenant_id=tenant_id)
        
        return {
            "reviews": result.get("reviews", []),
            "stats": {
                "average_rating": stats.get("average_rating", 0),
                "total_reviews": stats.get("total_reviews", 0)
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Photo Upload Endpoints

@router.post("/{review_id}/photos")
async def upload_review_photo(
    review_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Upload photo to review"""
    try:
        tenant_id = current_user.get("tenant_id")
        user_id = current_user.get("id")
        
        service = ReviewService(db)
        
        # Read file content
        content = await file.read()
        
        # Upload photo
        photo = await service.upload_review_photo(
            review_id=review_id,
            tenant_id=tenant_id,
            file_content=content,
            filename=file.filename,
            content_type=file.content_type
        )
        
        return photo
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{review_id}/photos/{photo_id}")
async def delete_review_photo(
    review_id: str,
    photo_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Delete photo from review"""
    try:
        tenant_id = current_user.get("tenant_id")
        user_id = current_user.get("id")
        
        service = ReviewService(db)
        
        # Delete photo
        review = await service.delete_review_photo(
            review_id=review_id,
            photo_id=photo_id,
            tenant_id=tenant_id,
            user_id=user_id
        )
        
        return review
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Flag Review Endpoints

@router.post("/{review_id}/flag")
async def flag_review(
    review_id: str,
    flag_data: dict,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Flag review as inappropriate"""
    try:
        tenant_id = current_user.get("tenant_id")
        user_id = current_user.get("id")
        
        reason = flag_data.get("reason")
        details = flag_data.get("details", "")
        
        if not reason:
            raise HTTPException(status_code=400, detail="Reason is required")
        
        service = ReviewService(db)
        
        review = await service.flag_review(
            review_id=review_id,
            tenant_id=tenant_id,
            user_id=user_id,
            reason=reason,
            details=details
        )
        
        return review
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{review_id}/flag")
async def unflag_review(
    review_id: str,
    current_user: dict = Depends(require_roles(["owner", "admin"])),
    db = Depends(get_database)
):
    """Unflag review"""
    try:
        tenant_id = current_user.get("tenant_id")
        
        service = ReviewService(db)
        
        review = await service.unflag_review(
            review_id=review_id,
            tenant_id=tenant_id
        )
        
        return review
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Phase 16: Review Incentives Endpoints

@router.post("/{review_id}/award-points")
async def award_review_points(
    review_id: str,
    points: int = Query(50, ge=1, le=1000),
    current_user: dict = Depends(require_roles(["owner", "admin"])),
    db = Depends(get_database)
):
    """Award loyalty points for review submission"""
    try:
        tenant_id = current_user.get("tenant_id")
        
        # Get review to find client
        review = db.reviews.find_one({
            "_id": ObjectId(review_id),
            "tenant_id": tenant_id
        })
        
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        
        service = ReviewService(db)
        
        result = await service.award_review_points(
            review_id=review_id,
            tenant_id=tenant_id,
            client_id=review.get("client_id"),
            points=points
        )
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Phase 17: Helpful Votes Endpoints

@router.post("/{review_id}/helpful")
async def vote_helpful(
    review_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Vote review as helpful"""
    try:
        tenant_id = current_user.get("tenant_id")
        user_id = current_user.get("id")
        
        service = ReviewService(db)
        
        review = await service.vote_helpful(
            review_id=review_id,
            tenant_id=tenant_id,
            user_id=user_id
        )
        
        return review
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{review_id}/helpful")
async def remove_helpful_vote(
    review_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Remove helpful vote from review"""
    try:
        tenant_id = current_user.get("tenant_id")
        user_id = current_user.get("id")
        
        service = ReviewService(db)
        
        review = await service.remove_helpful_vote(
            review_id=review_id,
            tenant_id=tenant_id,
            user_id=user_id
        )
        
        return review
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Phase 19: Review Deletion Endpoints

@router.post("/{review_id}/soft-delete")
async def soft_delete_review(
    review_id: str,
    deletion_reason: str = Query(..., min_length=1),
    current_user: dict = Depends(require_roles(["owner", "admin"])),
    db = Depends(get_database)
):
    """Soft delete a review"""
    try:
        tenant_id = current_user.get("tenant_id")
        user_id = current_user.get("id")
        
        service = ReviewService(db)
        
        review = await service.soft_delete_review(
            review_id=review_id,
            tenant_id=tenant_id,
            deleted_by=user_id,
            deletion_reason=deletion_reason
        )
        
        return review
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{review_id}/restore")
async def restore_review(
    review_id: str,
    current_user: dict = Depends(require_roles(["owner", "admin"])),
    db = Depends(get_database)
):
    """Restore a soft-deleted review"""
    try:
        tenant_id = current_user.get("tenant_id")
        
        service = ReviewService(db)
        
        review = await service.restore_review(
            review_id=review_id,
            tenant_id=tenant_id
        )
        
        return review
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/deleted")
async def get_deleted_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(require_roles(["owner", "admin"])),
    db = Depends(get_database)
):
    """Get soft-deleted reviews"""
    try:
        tenant_id = current_user.get("tenant_id")
        
        service = ReviewService(db)
        
        result = await service.get_deleted_reviews(
            tenant_id=tenant_id,
            skip=skip,
            limit=limit
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Phase 20: Review Editing Endpoints

@router.put("/{review_id}/edit-comment")
async def edit_review_comment(
    review_id: str,
    new_comment: str = Query(..., min_length=1),
    current_user: dict = Depends(require_roles(["owner", "admin"])),
    db = Depends(get_database)
):
    """Edit review comment"""
    try:
        tenant_id = current_user.get("tenant_id")
        user_id = current_user.get("id")
        
        service = ReviewService(db)
        
        review = await service.edit_review_comment(
            review_id=review_id,
            tenant_id=tenant_id,
            new_comment=new_comment,
            edited_by=user_id
        )
        
        return review
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{review_id}/edit-history")
async def get_edit_history(
    review_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get edit history for a review"""
    try:
        tenant_id = current_user.get("tenant_id")
        
        service = ReviewService(db)
        
        history = await service.get_edit_history(
            review_id=review_id,
            tenant_id=tenant_id
        )
        
        return {"edit_history": history}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
