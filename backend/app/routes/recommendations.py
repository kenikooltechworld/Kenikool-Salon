"""Recommendation routes"""
from fastapi import APIRouter, Depends, Request
from typing import List, Optional
from bson import ObjectId

from app.schemas.recommendation import (
    RecommendationResponse,
    RecommendationRequest,
    RecommendationFeedback,
    CustomerPreferenceResponse
)
from app.services.recommendation_service import RecommendationService
from app.middleware.tenant_context import get_tenant_id
from app.middleware.customer_auth import get_current_customer
from app.models.customer import Customer

router = APIRouter(prefix="/public/recommendations", tags=["Recommendations"])


@router.get("/", response_model=List[RecommendationResponse])
async def get_recommendations(
    request: Request,
    limit: int = 5,
    current_customer: Optional[Customer] = Depends(get_current_customer)
):
    """Get personalized service recommendations"""
    tenant_id = get_tenant_id(request)
    customer_id = current_customer.id if current_customer else None
    
    recommendations = await RecommendationService.generate_recommendations(
        tenant_id=tenant_id,
        customer_id=customer_id,
        limit=limit
    )
    
    return recommendations


@router.post("/feedback")
async def track_recommendation_feedback(
    feedback: RecommendationFeedback
):
    """Track user interaction with recommendation"""
    await RecommendationService.track_recommendation_interaction(
        recommendation_id=feedback.recommendation_id,
        action=feedback.action
    )
    
    return {"message": "Feedback recorded"}


@router.get("/preferences", response_model=CustomerPreferenceResponse)
async def get_customer_preferences(
    request: Request,
    current_customer: Customer = Depends(get_current_customer)
):
    """Get customer preferences"""
    tenant_id = get_tenant_id(request)
    
    # Update preferences based on latest bookings
    preference = await RecommendationService.update_customer_preferences(
        tenant_id=tenant_id,
        customer_id=current_customer.id
    )
    
    return CustomerPreferenceResponse(
        id=str(preference.id),
        customer_id=str(preference.customer_id),
        preferred_service_categories=preference.preferred_service_categories,
        preferred_services=[str(sid) for sid in preference.preferred_services],
        preferred_staff=[str(sid) for sid in preference.preferred_staff],
        preferred_time_slots=preference.preferred_time_slots,
        preferred_days=preference.preferred_days,
        average_booking_frequency_days=preference.average_booking_frequency_days,
        average_spend=preference.average_spend,
        last_booking_date=preference.last_booking_date,
        total_bookings=preference.total_bookings
    )
