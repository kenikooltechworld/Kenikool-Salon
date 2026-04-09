"""Membership routes for admin/owner management."""

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from bson import ObjectId

from app.routes.auth import get_current_user_dependency
from app.services.membership_service import MembershipService
from app.schemas.membership import (
    MembershipTierCreate,
    MembershipTierUpdate,
    MembershipTierResponse,
    MembershipCreate,
    MembershipResponse,
    MembershipTransactionResponse,
)


router = APIRouter(prefix="/memberships", tags=["Memberships"])


# Membership Tier Management (Admin)
@router.get("/tiers", response_model=List[MembershipTierResponse])
async def get_membership_tiers(
    current_user: dict = Depends(get_current_user_dependency)
):
    """Get all membership tiers."""
    tenant_id = current_user.get("tenant_id")
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


@router.post("/tiers", response_model=MembershipTierResponse)
async def create_membership_tier(
    tier_data: MembershipTierCreate,
    current_user: dict = Depends(get_current_user_dependency)
):
    """Create a new membership tier."""
    tenant_id = current_user.get("tenant_id")
    
    # Check if user has permission (Owner/Manager only)
    role_names = current_user.get("role_names", [])
    if "Owner" not in role_names and "Manager" not in role_names:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    tier = MembershipService.create_tier(tenant_id, tier_data)
    
    return MembershipTierResponse(
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


@router.put("/tiers/{tier_id}", response_model=MembershipTierResponse)
async def update_membership_tier(
    tier_id: str,
    tier_data: MembershipTierUpdate,
    current_user: dict = Depends(get_current_user_dependency)
):
    """Update a membership tier."""
    role_names = current_user.get("role_names", [])
    if "Owner" not in role_names and "Manager" not in role_names:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        tier = MembershipService.update_tier(ObjectId(tier_id), tier_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return MembershipTierResponse(
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


@router.delete("/tiers/{tier_id}")
async def delete_membership_tier(
    tier_id: str,
    current_user: dict = Depends(get_current_user_dependency)
):
    """Delete (deactivate) a membership tier."""
    role_names = current_user.get("role_names", [])
    if "Owner" not in role_names:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    success = MembershipService.delete_tier(ObjectId(tier_id))
    if not success:
        raise HTTPException(status_code=404, detail="Membership tier not found")
    
    return {"message": "Membership tier deleted successfully"}


# Membership Subscription Management
@router.post("/subscriptions", response_model=MembershipResponse)
async def create_membership_subscription(
    membership_data: MembershipCreate,
    current_user: dict = Depends(get_current_user_dependency)
):
    """Create a new membership subscription for a customer."""
    tenant_id = current_user.get("tenant_id")
    
    try:
        membership = MembershipService.create_membership(
            tenant_id=tenant_id,
            membership_data=membership_data,
            created_by=current_user.get("id")
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


@router.get("/subscriptions/customer/{customer_id}", response_model=MembershipResponse)
async def get_customer_membership(
    customer_id: str,
    current_user: dict = Depends(get_current_user_dependency)
):
    """Get active membership for a customer."""
    tenant_id = current_user.get("tenant_id")
    
    membership = MembershipService.get_customer_membership(
        tenant_id=tenant_id,
        customer_id=ObjectId(customer_id)
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


@router.post("/subscriptions/{membership_id}/pause")
async def pause_membership(
    membership_id: str,
    pause_reason: str,
    current_user: dict = Depends(get_current_user_dependency)
):
    """Pause a membership subscription."""
    try:
        membership = MembershipService.pause_membership(
            membership_id=ObjectId(membership_id),
            pause_reason=pause_reason
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"message": "Membership paused successfully"}


@router.post("/subscriptions/{membership_id}/resume")
async def resume_membership(
    membership_id: str,
    current_user: dict = Depends(get_current_user_dependency)
):
    """Resume a paused membership."""
    try:
        membership = MembershipService.resume_membership(ObjectId(membership_id))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"message": "Membership resumed successfully"}


@router.post("/subscriptions/{membership_id}/cancel")
async def cancel_membership(
    membership_id: str,
    cancellation_reason: str,
    current_user: dict = Depends(get_current_user_dependency)
):
    """Cancel a membership subscription."""
    try:
        membership = MembershipService.cancel_membership(
            membership_id=ObjectId(membership_id),
            cancellation_reason=cancellation_reason,
            cancelled_by=current_user.get("id")
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"message": "Membership cancelled successfully"}


@router.get("/subscriptions/{membership_id}/transactions", response_model=List[MembershipTransactionResponse])
async def get_membership_transactions(
    membership_id: str,
    current_user: dict = Depends(get_current_user_dependency),
    limit: int = 20,
    skip: int = 0
):
    """Get transaction history for a membership."""
    transactions = MembershipService.get_membership_transactions(
        membership_id=ObjectId(membership_id),
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


@router.get("/subscriptions", response_model=List[MembershipResponse])
async def get_all_memberships(
    current_user: dict = Depends(get_current_user_dependency),
    status: str = None,
    tier_id: str = None,
    limit: int = 50,
    skip: int = 0
):
    """Get all memberships for the tenant with optional filters."""
    tenant_id = current_user.get("tenant_id")
    
    memberships = MembershipService.get_all_memberships(
        tenant_id=tenant_id,
        status=status,
        tier_id=ObjectId(tier_id) if tier_id else None,
        limit=limit,
        skip=skip
    )
    
    # Get all tiers for name lookup
    tiers = {str(t.id): t.name for t in MembershipService.get_active_tiers(tenant_id)}
    
    return [
        MembershipResponse(
            id=str(m.id),
            customer_id=str(m.customer_id),
            tier_id=str(m.tier_id),
            tier_name=tiers.get(str(m.tier_id), "Unknown"),
            status=m.status,
            start_date=m.start_date,
            end_date=m.end_date,
            next_billing_date=m.next_billing_date,
            last_payment_date=m.last_payment_date,
            last_payment_amount=m.last_payment_amount.to_decimal() if m.last_payment_amount else None,
            services_used_this_cycle=m.services_used_this_cycle,
            services_remaining_this_cycle=m.services_remaining_this_cycle,
            rollover_services=m.rollover_services,
            created_at=m.created_at,
            updated_at=m.updated_at
        )
        for m in memberships
    ]


@router.get("/stats")
async def get_membership_stats(
    current_user: dict = Depends(get_current_user_dependency)
):
    """Get membership statistics for the tenant."""
    tenant_id = current_user.get("tenant_id")
    
    stats = MembershipService.get_membership_stats(tenant_id)
    
    return stats
