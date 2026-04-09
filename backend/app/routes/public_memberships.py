"""Public membership routes for customers."""

from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List
from bson import ObjectId

from app.middleware.tenant_context import get_tenant_id
from app.middleware.customer_auth import get_current_customer
from app.models.customer import Customer
from app.services.membership_service import MembershipService
from app.schemas.membership import (
    MembershipTierResponse,
    MembershipCreate,
    MembershipResponse,
    MembershipTransactionResponse,
)


router = APIRouter(prefix="/public/memberships", tags=["Public Memberships"])


@router.get("/tiers", response_model=List[MembershipTierResponse])
async def get_public_membership_tiers(request: Request):
    """Get all available membership tiers for public viewing."""
    tenant_id = get_tenant_id(request)
    tiers = MembershipService.get_active_tiers(tenant_id)
    
    return [
        MembershipTierResponse(
            id=str(tier.id),
            name=tier.name,
            description=tier.description,
            monthly_price=tier.monthly_price.to_decimal(),
            annual_price=tier.annual_price.to_decimal() if tier.annual_price else None,
            billing_cycle=tier.billing_cycle,
            discount_percentage=tier.discount_percentage,
            priority_booking=tier.priority_booking,
            exclusive_services=[str(sid) for sid in tier.exclusive_services],
            free_services_per_month=tier.free_services_per_month,
            rollover_unused=tier.rollover_unused,
            benefits=[
                {"benefit_type": b.benefit_type, "description": b.description, "value": b.value}
                for b in tier.benefits
            ],
            max_members=tier.max_members,
            display_order=tier.display_order,
            is_active=tier.is_active,
            created_at=tier.created_at,
            updated_at=tier.updated_at
        )
        for tier in tiers
    ]


@router.post("/subscribe", response_model=MembershipResponse)
async def subscribe_to_membership(
    request: Request,
    membership_data: MembershipCreate,
    current_customer: Customer = Depends(get_current_customer)
):
    """Subscribe to a membership tier (requires customer authentication)."""
    tenant_id = get_tenant_id(request)
    
    # Ensure customer is subscribing for themselves
    if str(current_customer.id) != membership_data.customer_id:
        raise HTTPException(status_code=403, detail="Can only subscribe for yourself")
    
    try:
        membership = MembershipService.create_membership(
            tenant_id=tenant_id,
            membership_data=membership_data,
            created_by=current_customer.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    tier = MembershipService.get_tier_by_id(membership.tier_id)
    
    return MembershipResponse(
        id=str(membership.id),
        customer_id=str(membership.customer_id),
        tier_id=str(membership.tier_id),
        tier_name=tier.name if tier else "Unknown",
        status=membership.status,
        start_date=membership.start_date,
        end_date=membership.end_date,
        next_billing_date=membership.next_billing_date,
        last_payment_date=membership.last_payment_date,
        last_payment_amount=membership.last_payment_amount.to_decimal() if membership.last_payment_amount else None,
        services_used_this_cycle=membership.services_used_this_cycle,
        services_remaining_this_cycle=membership.services_remaining_this_cycle,
        rollover_services=membership.rollover_services,
        created_at=membership.created_at,
        updated_at=membership.updated_at
    )


@router.get("/my-membership", response_model=MembershipResponse)
async def get_my_membership(
    request: Request,
    current_customer: Customer = Depends(get_current_customer)
):
    """Get current customer's active membership."""
    tenant_id = get_tenant_id(request)
    
    membership = MembershipService.get_customer_membership(
        tenant_id=tenant_id,
        customer_id=current_customer.id
    )
    
    if not membership:
        raise HTTPException(status_code=404, detail="No active membership found")
    
    tier = MembershipService.get_tier_by_id(membership.tier_id)
    
    return MembershipResponse(
        id=str(membership.id),
        customer_id=str(membership.customer_id),
        tier_id=str(membership.tier_id),
        tier_name=tier.name if tier else "Unknown",
        status=membership.status,
        start_date=membership.start_date,
        end_date=membership.end_date,
        next_billing_date=membership.next_billing_date,
        last_payment_date=membership.last_payment_date,
        last_payment_amount=membership.last_payment_amount.to_decimal() if membership.last_payment_amount else None,
        services_used_this_cycle=membership.services_used_this_cycle,
        services_remaining_this_cycle=membership.services_remaining_this_cycle,
        rollover_services=membership.rollover_services,
        created_at=membership.created_at,
        updated_at=membership.updated_at
    )


@router.post("/my-membership/pause")
async def pause_my_membership(
    pause_reason: str,
    current_customer: Customer = Depends(get_current_customer)
):
    """Pause current customer's membership."""
    request_obj = Request(scope={"type": "http"})
    tenant_id = get_tenant_id(request_obj)
    
    membership = MembershipService.get_customer_membership(
        tenant_id=tenant_id,
        customer_id=current_customer.id
    )
    
    if not membership:
        raise HTTPException(status_code=404, detail="No active membership found")
    
    try:
        MembershipService.pause_membership(
            membership_id=membership.id,
            pause_reason=pause_reason
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"message": "Membership paused successfully"}


@router.post("/my-membership/cancel")
async def cancel_my_membership(
    request: Request,
    cancellation_reason: str,
    current_customer: Customer = Depends(get_current_customer)
):
    """Cancel current customer's membership."""
    tenant_id = get_tenant_id(request)
    
    membership = MembershipService.get_customer_membership(
        tenant_id=tenant_id,
        customer_id=current_customer.id
    )
    
    if not membership:
        raise HTTPException(status_code=404, detail="No active membership found")
    
    try:
        MembershipService.cancel_membership(
            membership_id=membership.id,
            cancellation_reason=cancellation_reason,
            cancelled_by=current_customer.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"message": "Membership cancelled successfully"}


@router.get("/my-membership/transactions", response_model=List[MembershipTransactionResponse])
async def get_my_membership_transactions(
    request: Request,
    current_customer: Customer = Depends(get_current_customer),
    limit: int = 20,
    skip: int = 0
):
    """Get transaction history for current customer's membership."""
    tenant_id = get_tenant_id(request)
    
    membership = MembershipService.get_customer_membership(
        tenant_id=tenant_id,
        customer_id=current_customer.id
    )
    
    if not membership:
        raise HTTPException(status_code=404, detail="No active membership found")
    
    transactions = MembershipService.get_membership_transactions(
        membership_id=membership.id,
        limit=limit,
        skip=skip
    )
    
    return [
        MembershipTransactionResponse(
            id=str(t.id),
            membership_id=str(t.membership_id),
            customer_id=str(t.customer_id),
            transaction_type=t.transaction_type,
            amount=t.amount.to_decimal(),
            status=t.status,
            payment_method=t.payment_method,
            description=t.description,
            created_at=t.created_at
        )
        for t in transactions
    ]
