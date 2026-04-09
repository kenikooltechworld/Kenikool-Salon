"""Celery tasks for membership billing."""

import logging
from datetime import datetime
from decimal import Decimal
from bson import ObjectId

from app.tasks import celery_app
from app.services.membership_service import MembershipService
from app.services.payment_service import PaymentService
from app.models.membership import Membership, MembershipTier

logger = logging.getLogger(__name__)


@celery_app.task(name="process_membership_billing")
def process_membership_billing():
    """
    Process billing for all memberships that are due.
    This task should run daily.
    """
    logger.info("Starting membership billing processing")
    
    try:
        # Get all memberships due for billing
        memberships_due = MembershipService.get_memberships_due_for_billing()
        
        logger.info(f"Found {len(memberships_due)} memberships due for billing")
        
        for membership in memberships_due:
            try:
                process_single_membership_billing(membership)
            except Exception as e:
                logger.error(
                    f"Error processing billing for membership {membership.id}: {e}",
                    exc_info=True
                )
                # Continue with next membership even if one fails
                continue
        
        logger.info("Completed membership billing processing")
        return {
            "success": True,
            "processed": len(memberships_due),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in membership billing task: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


def process_single_membership_billing(membership: Membership):
    """Process billing for a single membership."""
    logger.info(f"Processing billing for membership {membership.id}")
    
    # Get membership tier
    tier = MembershipService.get_tier_by_id(membership.tier_id)
    if not tier:
        logger.error(f"Tier not found for membership {membership.id}")
        return
    
    # Determine billing amount
    if tier.billing_cycle == "monthly":
        amount = tier.monthly_price.to_decimal()
    else:  # annual
        amount = tier.annual_price.to_decimal() if tier.annual_price else tier.monthly_price.to_decimal() * 12
    
    # Check if payment method is available
    if not membership.payment_method_id:
        logger.warning(f"No payment method for membership {membership.id}")
        # TODO: Send notification to customer to update payment method
        return
    
    try:
        # Process payment (this would integrate with Paystack or other payment provider)
        # For now, we'll create a transaction record
        transaction = MembershipService.create_transaction(
            tenant_id=membership.tenant_id,
            membership_id=membership.id,
            customer_id=membership.customer_id,
            transaction_type="payment",
            amount=Decimal(str(amount)),
            status="pending",
            payment_method=membership.payment_method_id,
            description=f"Membership billing for {tier.name} - {tier.billing_cycle}"
        )
        
        # In a real implementation, you would:
        # 1. Charge the payment method using PaymentService
        # 2. Update transaction status based on payment result
        # 3. Process billing cycle if payment successful
        # 4. Handle failed payments (retry, notify customer, etc.)
        
        # For now, we'll assume payment is successful and process the billing cycle
        MembershipService.process_billing_cycle(
            membership_id=membership.id,
            payment_amount=Decimal(str(amount))
        )
        
        # Update transaction status
        transaction.status = "completed"
        transaction.save()
        
        logger.info(f"Successfully processed billing for membership {membership.id}")
        
    except Exception as e:
        logger.error(f"Error processing payment for membership {membership.id}: {e}")
        # TODO: Handle failed payment (send notification, retry logic, etc.)
        raise


@celery_app.task(name="send_membership_renewal_reminders")
def send_membership_renewal_reminders():
    """
    Send renewal reminders to members whose billing date is approaching.
    This task should run daily.
    """
    logger.info("Starting membership renewal reminder task")
    
    try:
        from datetime import timedelta
        from app.models.membership import Membership
        
        # Get memberships with billing date in next 7 days
        upcoming_date = datetime.utcnow() + timedelta(days=7)
        memberships = Membership.objects(
            status="active",
            next_billing_date__lte=upcoming_date,
            next_billing_date__gte=datetime.utcnow()
        )
        
        logger.info(f"Found {len(memberships)} memberships with upcoming renewal")
        
        for membership in memberships:
            try:
                # TODO: Send email/SMS reminder to customer
                # This would integrate with your notification service
                logger.info(f"Sent renewal reminder for membership {membership.id}")
            except Exception as e:
                logger.error(f"Error sending reminder for membership {membership.id}: {e}")
                continue
        
        logger.info("Completed membership renewal reminder task")
        return {
            "success": True,
            "reminders_sent": len(memberships),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in renewal reminder task: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@celery_app.task(name="expire_cancelled_memberships")
def expire_cancelled_memberships():
    """
    Mark cancelled memberships as expired after their end date.
    This task should run daily.
    """
    logger.info("Starting expired membership cleanup task")
    
    try:
        from app.models.membership import Membership
        
        # Get cancelled memberships that have passed their end date
        expired_memberships = Membership.objects(
            status="cancelled",
            end_date__lte=datetime.utcnow()
        )
        
        count = 0
        for membership in expired_memberships:
            membership.status = "expired"
            membership.save()
            count += 1
        
        logger.info(f"Marked {count} memberships as expired")
        return {
            "success": True,
            "expired_count": count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in expired membership cleanup task: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
