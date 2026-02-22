"""
API endpoints for membership system.
Handles plans and subscriptions management.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional
from bson import ObjectId
from datetime import datetime
import logging

from app.api.dependencies import get_current_user, get_tenant_id, require_owner_or_admin
from app.database import Database
from app.services.membership_service import MembershipService
from app.schemas.membership import (
    MembershipPlanCreate,
    MembershipPlanUpdate,
    MembershipPlanResponse,
    MembershipSubscriptionCreate,
    MembershipSubscriptionResponse,
    SubscriptionListResponse,
    CancelSubscriptionRequest,
    ChangeSubscriptionPlanRequest,
    UpdatePaymentMethodRequest,
    MembershipAnalyticsResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/memberships", tags=["memberships"])


def get_db():
    """Get database instance"""
    return Database.get_db()


# ============================================================================
# Plan Management Endpoints
# ============================================================================


@router.get("/plans", response_model=dict)
async def list_plans(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    is_active: Optional[bool] = Query(None),
    billing_cycle: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """List all membership plans for tenant with search, filter, and sort"""
    db = get_db()
    service = MembershipService(db)

    try:
        result = await service.get_plans(
            tenant_id=tenant_id,
            is_active=is_active,
            billing_cycle=billing_cycle,
            page=page,
            limit=limit,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/plans", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_plan(
    plan_data: MembershipPlanCreate,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(require_owner_or_admin),
):
    """Create a new membership plan"""
    db = get_db()
    service = MembershipService(db)

    try:
        plan = await service.create_plan(tenant_id=tenant_id, plan_data=plan_data)
        return plan
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/plans/{plan_id}", response_model=dict)
async def update_plan(
    plan_id: str,
    updates: MembershipPlanUpdate,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(require_owner_or_admin),
):
    """Update a membership plan"""
    db = get_db()
    service = MembershipService(db)

    try:
        plan = await service.update_plan(
            tenant_id=tenant_id, plan_id=plan_id, updates=updates
        )
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        return plan
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/plans/{plan_id}")
async def delete_plan(
    plan_id: str,
    force: bool = Query(False),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(require_owner_or_admin),
):
    """Delete a membership plan"""
    db = get_db()
    service = MembershipService(db)

    try:
        deleted = await service.delete_plan(
            tenant_id=tenant_id, plan_id=plan_id, force=force
        )
        if not deleted:
            raise HTTPException(status_code=404, detail="Plan not found")
        return {"message": "Plan deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plans/{plan_id}/subscribers", response_model=dict)
async def get_plan_subscribers(
    plan_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(require_owner_or_admin),
):
    """Get subscribers for a plan"""
    db = get_db()
    service = MembershipService(db)

    try:
        result = await service.get_plan_subscribers(
            tenant_id=tenant_id, plan_id=plan_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Subscription Management Endpoints
# ============================================================================


@router.get("/subscriptions", response_model=dict)
async def list_subscriptions(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    status: Optional[str] = Query(None, description="Filter by status"),
    plan_id: Optional[str] = Query(None, description="Filter by plan"),
    client_id: Optional[str] = Query(None, description="Filter by client"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """List subscriptions with search, filter, sort, and pagination"""
    db = get_db()
    service = MembershipService(db)

    try:
        result = service.get_subscriptions(
            tenant_id=tenant_id,
            status=status,
            plan_id=plan_id,
            client_id=client_id,
            page=page,
            limit=limit,
        )
        return result
    except Exception as e:
        import traceback
        logger.error(f"Error in list_subscriptions: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/subscriptions", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    sub_data: MembershipSubscriptionCreate,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Create a new subscription"""
    db = get_db()
    service = MembershipService(db)

    try:
        subscription = await service.create_subscription(
            tenant_id=tenant_id,
            client_id=sub_data.client_id,
            plan_id=sub_data.plan_id,
            payment_method_id=sub_data.payment_method_id,
            start_trial=sub_data.start_trial,
        )
        return subscription
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/subscriptions/{subscription_id}", response_model=dict)
async def get_subscription(
    subscription_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get subscription details"""
    db = get_db()
    service = MembershipService(db)

    try:
        subscription = await service.get_subscription(
            tenant_id=tenant_id, subscription_id=subscription_id
        )
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        return subscription
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/subscriptions/{subscription_id}/cancel", response_model=dict)
async def cancel_subscription(
    subscription_id: str,
    request: CancelSubscriptionRequest,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Cancel a subscription"""
    db = get_db()
    service = MembershipService(db)

    try:
        subscription = await service.cancel_subscription(
            tenant_id=tenant_id,
            subscription_id=subscription_id,
            reason=request.reason,
            immediate=request.immediate,
        )
        return subscription
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/subscriptions/{subscription_id}/pause", response_model=dict)
async def pause_subscription(
    subscription_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Pause a subscription"""
    db = get_db()
    service = MembershipService(db)

    try:
        subscription = await service.pause_subscription(
            tenant_id=tenant_id, subscription_id=subscription_id
        )
        return subscription
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/subscriptions/{subscription_id}/resume", response_model=dict)
async def resume_subscription(
    subscription_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Resume a paused subscription"""
    db = get_db()
    service = MembershipService(db)

    try:
        subscription = await service.resume_subscription(
            tenant_id=tenant_id, subscription_id=subscription_id
        )
        return subscription
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/subscriptions/{subscription_id}/change-plan", response_model=dict)
async def change_subscription_plan(
    subscription_id: str,
    request: ChangeSubscriptionPlanRequest,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Change subscription plan (upgrade/downgrade)"""
    db = get_db()
    service = MembershipService(db)
    
    try:
        subscription = await service.change_plan(
            tenant_id=tenant_id,
            subscription_id=subscription_id,
            new_plan_id=request.new_plan_id,
            apply_immediately=request.apply_immediately,
        )
        return subscription
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/subscriptions/{subscription_id}/payment-method", response_model=dict)
async def update_payment_method(
    subscription_id: str,
    request: UpdatePaymentMethodRequest,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Update payment method for subscription"""
    db = get_db()
    service = MembershipService(db)

    try:
        subscription = await service.get_subscription(
            tenant_id=tenant_id, subscription_id=subscription_id
        )
        if not subscription:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")

        # Update payment method
        updated = await service.subscriptions_collection.find_one_and_update(
            {"_id": ObjectId(subscription_id), "tenant_id": tenant_id},
            {
                "$set": {
                    "payment_method_id": request.payment_method_id,
                    "updated_at": datetime.utcnow(),
                }
            },
            return_document=True,
        )
        return updated
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ============================================================================
# Analytics Endpoint
# ============================================================================


# ============================================================================
# Trial Period Endpoints
# ============================================================================


@router.post("/subscriptions/{subscription_id}/convert-trial-to-paid", response_model=dict)
async def convert_trial_to_paid(
    subscription_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Convert a trial subscription to paid"""
    db = get_db()
    service = MembershipService(db)

    try:
        result = await service.convert_trial_to_paid(
            tenant_id=tenant_id,
            subscription_id=subscription_id,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/subscriptions/{subscription_id}/trial-info", response_model=dict)
async def get_trial_info(
    subscription_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get trial information for a subscription"""
    db = get_db()
    service = MembershipService(db)

    try:
        result = await service.get_trial_info(
            tenant_id=tenant_id,
            subscription_id=subscription_id,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/subscriptions/{subscription_id}/send-trial-reminder", response_model=dict)
async def send_trial_ending_reminder(
    subscription_id: str,
    request: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(require_owner_or_admin),
):
    """Send trial ending reminder"""
    db = get_db()
    service = MembershipService(db)

    try:
        days_before = request.get("days_before", 3)

        result = await service.send_trial_ending_reminder(
            tenant_id=tenant_id,
            subscription_id=subscription_id,
            days_before=days_before,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/trial-conversion-rate", response_model=dict)
async def get_trial_conversion_rate_detailed(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(require_owner_or_admin),
    period_days: int = Query(30),
):
    """Get detailed trial conversion rate statistics"""
    db = get_db()
    service = MembershipService(db)

    try:
        result = await service.get_trial_conversion_rate_detailed(
            tenant_id=tenant_id,
            period_days=period_days,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Benefit Tracking Endpoints
# ============================================================================


@router.post("/subscriptions/{subscription_id}/track-benefit", response_model=dict)
async def track_benefit_usage(
    subscription_id: str,
    request: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(require_owner_or_admin),
):
    """Track benefit usage for a subscription"""
    db = get_db()
    service = MembershipService(db)

    try:
        benefit_type = request.get("benefit_type", "service")

        result = await service.track_benefit_usage(
            tenant_id=tenant_id,
            subscription_id=subscription_id,
            benefit_type=benefit_type,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/subscriptions/{subscription_id}/benefit-usage", response_model=dict)
async def get_benefit_usage(
    subscription_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get benefit usage for a subscription"""
    db = get_db()
    service = MembershipService(db)

    try:
        result = await service.get_benefit_usage(
            tenant_id=tenant_id,
            subscription_id=subscription_id,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/subscriptions/{subscription_id}/reset-benefit-usage", response_model=dict)
async def reset_benefit_usage(
    subscription_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(require_owner_or_admin),
):
    """Reset benefit usage for a subscription"""
    db = get_db()
    service = MembershipService(db)

    try:
        result = await service.reset_benefit_usage(
            tenant_id=tenant_id,
            subscription_id=subscription_id,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/subscriptions/{subscription_id}/benefit-notifications", response_model=dict)
async def check_benefit_limit_notifications(
    subscription_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(require_owner_or_admin),
):
    """Check if benefit limit notifications should be sent"""
    db = get_db()
    service = MembershipService(db)

    try:
        result = await service.check_benefit_limit_notifications(
            tenant_id=tenant_id,
            subscription_id=subscription_id,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Bulk Operations Endpoints
# ============================================================================


@router.post("/subscriptions/bulk/cancel", response_model=dict)
async def bulk_cancel_subscriptions(
    request: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(require_owner_or_admin),
):
    """Bulk cancel subscriptions"""
    db = get_db()
    service = MembershipService(db)

    try:
        subscription_ids = request.get("subscription_ids", [])
        reason = request.get("reason")

        result = await service.bulk_cancel_subscriptions(
            tenant_id=tenant_id,
            subscription_ids=subscription_ids,
            reason=reason,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/subscriptions/bulk/pause", response_model=dict)
async def bulk_pause_subscriptions(
    request: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(require_owner_or_admin),
):
    """Bulk pause subscriptions"""
    db = get_db()
    service = MembershipService(db)

    try:
        subscription_ids = request.get("subscription_ids", [])

        result = await service.bulk_pause_subscriptions(
            tenant_id=tenant_id,
            subscription_ids=subscription_ids,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/subscriptions/bulk/resume", response_model=dict)
async def bulk_resume_subscriptions(
    request: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(require_owner_or_admin),
):
    """Bulk resume subscriptions"""
    db = get_db()
    service = MembershipService(db)

    try:
        subscription_ids = request.get("subscription_ids", [])

        result = await service.bulk_resume_subscriptions(
            tenant_id=tenant_id,
            subscription_ids=subscription_ids,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/subscriptions/bulk/export-csv", response_model=dict)
async def bulk_export_subscriptions_csv(
    request: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(require_owner_or_admin),
):
    """Bulk export subscriptions to CSV"""
    db = get_db()
    service = MembershipService(db)

    try:
        subscription_ids = request.get("subscription_ids")
        filters = request.get("filters")

        csv_content = await service.bulk_export_subscriptions_to_csv(
            tenant_id=tenant_id,
            subscription_ids=subscription_ids,
            filters=filters,
        )
        
        return {
            "csv": csv_content,
            "filename": f"subscriptions_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Analytics Endpoint
# ============================================================================


@router.get("/analytics", response_model=dict)
async def get_analytics(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(require_owner_or_admin),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
):
    """Get membership analytics"""
    db = get_db()
    service = MembershipService(db)

    try:
        mrr = await service.calculate_mrr(tenant_id=tenant_id)
        arr = await service.calculate_arr(tenant_id=tenant_id)
        active_subscribers = await service.get_active_subscriber_count(
            tenant_id=tenant_id
        )
        churn_rate = await service.calculate_churn_rate(tenant_id=tenant_id)
        average_lifetime = await service.get_average_lifetime_days(tenant_id=tenant_id)
        trial_conversion = await service.get_trial_conversion_rate(tenant_id=tenant_id)
        revenue_by_plan = await service.get_revenue_by_plan(tenant_id=tenant_id)
        status_distribution = await service.get_status_distribution(tenant_id=tenant_id)
        subscriber_growth = await service.get_subscriber_growth(tenant_id=tenant_id)

        return {
            "mrr": mrr,
            "arr": arr,
            "active_subscribers": active_subscribers,
            "subscriber_growth": {
                "current_month": active_subscribers,
                "last_month": subscriber_growth[-2]["subscribers"] if len(subscriber_growth) > 1 else 0,
                "growth_rate": (
                    ((active_subscribers - subscriber_growth[-2]["subscribers"]) / max(subscriber_growth[-2]["subscribers"], 1)) * 100
                    if len(subscriber_growth) > 1
                    else 0.0
                ),
            },
            "churn_rate": churn_rate,
            "average_lifetime_days": average_lifetime,
            "trial_conversion_rate": trial_conversion,
            "revenue_by_plan": revenue_by_plan,
            "status_distribution": status_distribution,
            "revenue_trend": subscriber_growth,  # TODO: Calculate actual revenue trend
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
