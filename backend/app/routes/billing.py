"""Billing routes for subscription management."""

import logging
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId

from app.services.subscription_service import SubscriptionService
from app.models.subscription import Subscription
from app.models.pricing_plan import PricingPlan
from app.middleware.tenant_context import get_tenant_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/billing", tags=["billing"])


# Request/Response Models
class SubscriptionResponse(BaseModel):
    """Subscription response model."""

    id: str
    tenant_id: str
    plan_name: str
    plan_tier: int
    billing_cycle: str
    status: str
    subscription_status: str
    current_period_start: str
    current_period_end: str
    next_billing_date: str
    is_trial: bool
    trial_end: Optional[str]
    days_until_expiry: int
    last_payment_date: Optional[str]
    last_payment_amount: Optional[float]
    auto_renew: bool
    trial_expiry_action_required: bool
    transaction_fee_percentage: float


class UpgradeRequest(BaseModel):
    """Upgrade subscription request."""

    plan_id: str = Field(..., description="Pricing plan ID")
    billing_cycle: str = Field(default="monthly", description="monthly or yearly")


class DowngradeRequest(BaseModel):
    """Downgrade subscription request."""

    plan_id: str = Field(..., description="Pricing plan ID")
    billing_cycle: str = Field(default="monthly", description="monthly or yearly")


class PricingPlanResponse(BaseModel):
    """Pricing plan response model."""

    id: str
    name: str
    tier_level: int
    description: Optional[str]
    monthly_price: float
    yearly_price: float
    currency: str
    features: dict
    trial_days: int
    is_featured: bool


def serialize_subscription(sub: Subscription, plan: PricingPlan) -> SubscriptionResponse:
    """Convert subscription to response model."""
    return SubscriptionResponse(
        id=str(sub.id),
        tenant_id=str(sub.tenant_id),
        plan_name=plan.name,
        plan_tier=plan.tier_level,
        billing_cycle=sub.billing_cycle,
        status=sub.status,
        subscription_status=sub.subscription_status,
        current_period_start=sub.current_period_start.isoformat(),
        current_period_end=sub.current_period_end.isoformat(),
        next_billing_date=sub.next_billing_date.isoformat(),
        is_trial=sub.is_trial,
        trial_end=sub.trial_end.isoformat() if sub.trial_end else None,
        days_until_expiry=sub.days_until_expiry(),
        last_payment_date=sub.last_payment_date.isoformat() if sub.last_payment_date else None,
        last_payment_amount=sub.last_payment_amount,
        auto_renew=sub.auto_renew,
        trial_expiry_action_required=sub.trial_expiry_action_required,
        transaction_fee_percentage=sub.transaction_fee_percentage,
    )


def serialize_plan(plan: PricingPlan) -> PricingPlanResponse:
    """Convert pricing plan to response model."""
    return PricingPlanResponse(
        id=str(plan.id),
        name=plan.name,
        tier_level=plan.tier_level,
        description=plan.description,
        monthly_price=plan.monthly_price,
        yearly_price=plan.yearly_price,
        currency=plan.currency,
        features=plan.features,
        trial_days=plan.trial_days,
        is_featured=plan.is_featured,
    )


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(tenant_id: str = Depends(get_tenant_id)):
    """
    Get current subscription for tenant.

    Returns:
        SubscriptionResponse: Current subscription details
    """
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    
    try:
        subscription = SubscriptionService.get_subscription(tenant_id)
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found",
            )

        plan = PricingPlan.objects(id=subscription.pricing_plan_id).first()
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pricing plan not found",
            )

        return serialize_subscription(subscription, plan)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get subscription",
        )


@router.get("/plans", response_model=list[PricingPlanResponse])
async def get_pricing_plans():
    """
    Get all active pricing plans.

    Returns:
        List of pricing plans
    """
    try:
        plans = PricingPlan.objects(is_active=True).order_by("tier_level")
        return [serialize_plan(plan) for plan in plans]
    except Exception as e:
        logger.error(f"Error getting pricing plans: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get pricing plans",
        )


@router.post("/upgrade", response_model=SubscriptionResponse)
async def upgrade_subscription(
    request: UpgradeRequest,
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Upgrade subscription to a new plan.

    Args:
        request: Upgrade request with plan_id and billing_cycle
        tenant_id: Tenant ID from context

    Returns:
        Updated subscription
    """
    try:
        # Validate plan exists
        plan = PricingPlan.objects(id=ObjectId(request.plan_id)).first()
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pricing plan not found",
            )

        # Upgrade subscription
        subscription = SubscriptionService.upgrade_subscription(
            tenant_id=tenant_id,
            new_plan_id=request.plan_id,
            billing_cycle=request.billing_cycle,
        )

        return serialize_subscription(subscription, plan)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error upgrading subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upgrade subscription",
        )


@router.post("/downgrade", response_model=SubscriptionResponse)
async def downgrade_subscription(
    request: DowngradeRequest,
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Downgrade subscription to a lower plan (effective at next renewal).

    Args:
        request: Downgrade request with plan_id and billing_cycle
        tenant_id: Tenant ID from context

    Returns:
        Updated subscription
    """
    try:
        # Validate plan exists
        plan = PricingPlan.objects(id=ObjectId(request.plan_id)).first()
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pricing plan not found",
            )

        # Downgrade subscription
        subscription = SubscriptionService.downgrade_subscription(
            tenant_id=tenant_id,
            new_plan_id=request.plan_id,
            billing_cycle=request.billing_cycle,
        )

        return serialize_subscription(subscription, plan)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downgrading subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to downgrade subscription",
        )


@router.post("/cancel", response_model=SubscriptionResponse)
async def cancel_subscription(tenant_id: str = Depends(get_tenant_id)):
    """
    Cancel subscription.

    Args:
        tenant_id: Tenant ID from context

    Returns:
        Canceled subscription
    """
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    
    try:
        subscription = SubscriptionService.cancel_subscription(tenant_id)
        plan = PricingPlan.objects(id=subscription.pricing_plan_id).first()
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pricing plan not found",
            )

        return serialize_subscription(subscription, plan)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error canceling subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel subscription",
        )



@router.post("/continue-free", response_model=SubscriptionResponse)
async def continue_free_with_fee(tenant_id: str = Depends(get_tenant_id)):
    """
    Continue on Free tier with 10% transaction fee after trial expires.

    Args:
        tenant_id: Tenant ID from context

    Returns:
        Updated subscription
    """
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    
    try:
        subscription = SubscriptionService.continue_free_with_fee(tenant_id)
        plan = PricingPlan.objects(id=subscription.pricing_plan_id).first()
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pricing plan not found",
            )

        return serialize_subscription(subscription, plan)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error continuing free with fee: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to continue free with fee",
        )


@router.post("/upgrade-from-trial", response_model=SubscriptionResponse)
async def upgrade_from_expired_trial(
    request: UpgradeRequest,
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Upgrade from expired trial to a paid plan.

    Args:
        request: Upgrade request with plan_id and billing_cycle
        tenant_id: Tenant ID from context

    Returns:
        Updated subscription
    """
    try:
        # Validate plan exists
        plan = PricingPlan.objects(id=ObjectId(request.plan_id)).first()
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pricing plan not found",
            )

        subscription = SubscriptionService.upgrade_from_expired_trial(
            tenant_id=tenant_id,
            new_plan_id=request.plan_id,
            billing_cycle=request.billing_cycle,
        )

        return serialize_subscription(subscription, plan)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error upgrading from expired trial: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upgrade from expired trial",
        )
