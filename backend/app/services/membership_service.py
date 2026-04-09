"""Membership service for managing subscriptions."""

from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from bson import ObjectId
from mongoengine import Q

from app.models.membership import MembershipTier, Membership, MembershipTransaction
from app.schemas.membership import (
    MembershipTierCreate,
    MembershipTierUpdate,
    MembershipCreate,
    MembershipUpdate,
)


class MembershipService:
    """Service for membership operations."""
    
    @staticmethod
    def get_active_tiers(tenant_id: ObjectId) -> List[MembershipTier]:
        """Get all active membership tiers for a tenant."""
        return MembershipTier.objects(
            tenant_id=tenant_id,
            is_active=True
        ).order_by('display_order')
    
    @staticmethod
    def get_tier_by_id(tier_id: ObjectId) -> Optional[MembershipTier]:
        """Get membership tier by ID."""
        return MembershipTier.objects(id=tier_id).first()
    
    @staticmethod
    def create_tier(tenant_id: ObjectId, tier_data: MembershipTierCreate) -> MembershipTier:
        """Create a new membership tier."""
        tier = MembershipTier(
            tenant_id=tenant_id,
            **tier_data.dict()
        )
        tier.save()
        return tier
    
    @staticmethod
    def update_tier(tier_id: ObjectId, tier_data: MembershipTierUpdate) -> MembershipTier:
        """Update membership tier."""
        tier = MembershipTier.objects(id=tier_id).first()
        if not tier:
            raise ValueError("Membership tier not found")
        
        update_data = tier_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(tier, key, value)
        
        tier.updated_at = datetime.utcnow()
        tier.save()
        return tier
    
    @staticmethod
    def delete_tier(tier_id: ObjectId) -> bool:
        """Soft delete membership tier."""
        tier = MembershipTier.objects(id=tier_id).first()
        if not tier:
            return False
        
        tier.is_active = False
        tier.save()
        return True
    
    @staticmethod
    def create_membership(
        tenant_id: ObjectId,
        membership_data: MembershipCreate,
        created_by: ObjectId
    ) -> Membership:
        """Create a new membership subscription."""
        tier = MembershipTier.objects(id=ObjectId(membership_data.tier_id)).first()
        if not tier or not tier.is_active:
            raise ValueError("Invalid membership tier")
        
        # Check max members limit
        if tier.max_members:
            active_count = Membership.objects(
                tenant_id=tenant_id,
                tier_id=tier.id,
                status="active"
            ).count()
            if active_count >= tier.max_members:
                raise ValueError("Membership tier is at capacity")
        
        # Calculate start date and next billing date
        start_date = membership_data.start_date or datetime.utcnow()
        if tier.billing_cycle == "monthly":
            next_billing_date = start_date + timedelta(days=30)
        else:  # annual
            next_billing_date = start_date + timedelta(days=365)
        
        membership = Membership(
            tenant_id=tenant_id,
            customer_id=ObjectId(membership_data.customer_id),
            tier_id=tier.id,
            status="active",
            start_date=start_date,
            next_billing_date=next_billing_date,
            payment_method_id=membership_data.payment_method_id,
            services_remaining_this_cycle=tier.free_services_per_month
        )
        membership.save()
        
        return membership
    
    @staticmethod
    def get_customer_membership(
        tenant_id: ObjectId,
        customer_id: ObjectId
    ) -> Optional[Membership]:
        """Get active membership for a customer."""
        return Membership.objects(
            tenant_id=tenant_id,
            customer_id=customer_id,
            status="active"
        ).first()
    
    @staticmethod
    def get_membership_by_id(membership_id: ObjectId) -> Optional[Membership]:
        """Get membership by ID."""
        return Membership.objects(id=membership_id).first()
    
    @staticmethod
    def pause_membership(
        membership_id: ObjectId,
        pause_reason: str,
        resume_date: Optional[datetime] = None
    ) -> Membership:
        """Pause a membership."""
        membership = Membership.objects(id=membership_id).first()
        if not membership:
            raise ValueError("Membership not found")
        
        if membership.status != "active":
            raise ValueError("Can only pause active memberships")
        
        membership.status = "paused"
        membership.paused_at = datetime.utcnow()
        membership.pause_reason = pause_reason
        membership.resume_date = resume_date
        membership.updated_at = datetime.utcnow()
        membership.save()
        
        return membership
    
    @staticmethod
    def resume_membership(membership_id: ObjectId) -> Membership:
        """Resume a paused membership."""
        membership = Membership.objects(id=membership_id).first()
        if not membership:
            raise ValueError("Membership not found")
        
        if membership.status != "paused":
            raise ValueError("Can only resume paused memberships")
        
        membership.status = "active"
        membership.paused_at = None
        membership.pause_reason = None
        membership.resume_date = None
        membership.updated_at = datetime.utcnow()
        membership.save()
        
        return membership
    
    @staticmethod
    def cancel_membership(
        membership_id: ObjectId,
        cancellation_reason: str,
        cancelled_by: ObjectId
    ) -> Membership:
        """Cancel a membership."""
        membership = Membership.objects(id=membership_id).first()
        if not membership:
            raise ValueError("Membership not found")
        
        if membership.status == "cancelled":
            raise ValueError("Membership already cancelled")
        
        membership.status = "cancelled"
        membership.cancelled_at = datetime.utcnow()
        membership.cancellation_reason = cancellation_reason
        membership.cancelled_by = cancelled_by
        membership.updated_at = datetime.utcnow()
        membership.save()
        
        return membership
    
    @staticmethod
    def use_service(membership_id: ObjectId) -> Membership:
        """Track service usage for membership."""
        membership = Membership.objects(id=membership_id).first()
        if not membership:
            raise ValueError("Membership not found")
        
        if membership.status != "active":
            raise ValueError("Membership is not active")
        
        if membership.services_remaining_this_cycle > 0:
            membership.services_used_this_cycle += 1
            membership.services_remaining_this_cycle -= 1
            membership.updated_at = datetime.utcnow()
            membership.save()
        
        return membership
    
    @staticmethod
    def process_billing_cycle(membership_id: ObjectId, payment_amount: Decimal) -> Membership:
        """Process billing cycle and reset usage counters."""
        membership = Membership.objects(id=membership_id).first()
        if not membership:
            raise ValueError("Membership not found")
        
        tier = MembershipTier.objects(id=membership.tier_id).first()
        if not tier:
            raise ValueError("Membership tier not found")
        
        # Record payment
        membership.last_payment_date = datetime.utcnow()
        membership.last_payment_amount = payment_amount
        
        # Calculate next billing date
        if tier.billing_cycle == "monthly":
            membership.next_billing_date = membership.next_billing_date + timedelta(days=30)
        else:  # annual
            membership.next_billing_date = membership.next_billing_date + timedelta(days=365)
        
        # Reset usage counters
        if tier.rollover_unused and membership.services_remaining_this_cycle > 0:
            membership.rollover_services += membership.services_remaining_this_cycle
        
        membership.services_used_this_cycle = 0
        membership.services_remaining_this_cycle = tier.free_services_per_month + membership.rollover_services
        membership.rollover_services = 0
        
        membership.updated_at = datetime.utcnow()
        membership.save()
        
        return membership
    
    @staticmethod
    def create_transaction(
        tenant_id: ObjectId,
        membership_id: ObjectId,
        customer_id: ObjectId,
        transaction_type: str,
        amount: Decimal,
        status: str,
        payment_id: Optional[ObjectId] = None,
        payment_method: Optional[str] = None,
        description: Optional[str] = None
    ) -> MembershipTransaction:
        """Create a membership transaction record."""
        transaction = MembershipTransaction(
            tenant_id=tenant_id,
            membership_id=membership_id,
            customer_id=customer_id,
            transaction_type=transaction_type,
            amount=amount,
            status=status,
            payment_id=payment_id,
            payment_method=payment_method,
            description=description
        )
        transaction.save()
        return transaction
    
    @staticmethod
    def get_membership_transactions(
        membership_id: ObjectId,
        limit: int = 20,
        skip: int = 0
    ) -> List[MembershipTransaction]:
        """Get transaction history for a membership."""
        return MembershipTransaction.objects(
            membership_id=membership_id
        ).order_by('-created_at').skip(skip).limit(limit)
    
    @staticmethod
    def get_memberships_due_for_billing() -> List[Membership]:
        """Get all memberships that are due for billing."""
        today = datetime.utcnow()
        return Membership.objects(
            status="active",
            next_billing_date__lte=today
        )
    
    @staticmethod
    def get_all_memberships(
        tenant_id: ObjectId,
        status: Optional[str] = None,
        tier_id: Optional[ObjectId] = None,
        limit: int = 50,
        skip: int = 0
    ) -> List[Membership]:
        """Get all memberships for a tenant with optional filters."""
        query = {"tenant_id": tenant_id}
        
        if status:
            query["status"] = status
        if tier_id:
            query["tier_id"] = tier_id
        
        return Membership.objects(**query).order_by('-created_at').skip(skip).limit(limit)
    
    @staticmethod
    def get_membership_stats(tenant_id: ObjectId) -> dict:
        """Get membership statistics for a tenant."""
        total_members = Membership.objects(tenant_id=tenant_id, status="active").count()
        paused_members = Membership.objects(tenant_id=tenant_id, status="paused").count()
        cancelled_members = Membership.objects(tenant_id=tenant_id, status="cancelled").count()
        
        # Calculate monthly revenue
        active_memberships = Membership.objects(tenant_id=tenant_id, status="active")
        monthly_revenue = sum(
            float(m.last_payment_amount or 0) for m in active_memberships
        )
        
        return {
            "total_active": total_members,
            "total_paused": paused_members,
            "total_cancelled": cancelled_members,
            "monthly_revenue": monthly_revenue,
            "total_members": total_members + paused_members
        }
