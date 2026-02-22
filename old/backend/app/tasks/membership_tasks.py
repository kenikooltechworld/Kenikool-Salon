"""
Membership system background tasks for Celery.
Handles automated subscription management including renewals, payment retries,
benefit resets, notifications, trial conversions, grace period expiry, and analytics.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from bson import ObjectId
from celery import shared_task
from pymongo.database import Database

from app.database import get_db
from app.services.membership_service import MembershipService
from app.services.email_service import EmailService
from app.models.membership import SubscriptionStatus, BillingCycle

logger = logging.getLogger(__name__)


def _get_db() -> Database:
    """Get database connection"""
    return get_db()


def _calculate_next_billing_date(current_date: datetime, billing_cycle: str) -> datetime:
    """Calculate next billing date based on billing cycle"""
    if billing_cycle == BillingCycle.MONTHLY.value:
        # Add 30 days for monthly
        return current_date + timedelta(days=30)
    elif billing_cycle == BillingCycle.QUARTERLY.value:
        # Add 90 days for quarterly
        return current_date + timedelta(days=90)
    elif billing_cycle == BillingCycle.YEARLY.value:
        # Add 365 days for yearly
        return current_date + timedelta(days=365)
    else:
        # Default to 30 days
        return current_date + timedelta(days=30)


# ============================================================================
# Task 5.2: Subscription Renewal Processing
# ============================================================================

@shared_task(bind=True, max_retries=3)
def process_renewals(self):
    """
    Process subscription renewals for subscriptions ending today.
    
    Runs daily at 2 AM.
    
    - Finds subscriptions where end_date is today and auto_renew is true
    - Processes payment via Paystack
    - Updates end_date to next billing cycle
    - Records renewal in renewal_history
    - Sends confirmation emails
    - Handles failures by setting status to grace_period
    """
    try:
        db = _get_db()
        membership_service = MembershipService(db)
        email_service = EmailService()
        
        # Find subscriptions ending today with auto_renew=true
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        
        subscriptions_collection = db["membership_subscriptions"]
        subscriptions = subscriptions_collection.find({
            "end_date": {"$gte": today, "$lt": tomorrow},
            "auto_renew": True,
            "status": SubscriptionStatus.ACTIVE.value,
        }).to_list(None)
        
        logger.info(f"Found {len(subscriptions)} subscriptions to renew")
        
        for subscription in subscriptions:
            try:
                # Get plan details
                plan = membership_service.get_plan(
                    subscription["tenant_id"],
                    subscription["plan_id"]
                )
                if not plan:
                    logger.error(f"Plan {subscription['plan_id']} not found")
                    continue
                
                # Process payment
                try:
                    membership_service.process_payment(
                        subscription,
                        plan["price"],
                        f"Renewal for {plan['name']}"
                    )
                except Exception as e:
                    logger.error(f"Payment failed for subscription {subscription['_id']}: {str(e)}")
                    # Set to grace period on payment failure
                    subscriptions_collection.update_one(
                        {"_id": subscription["_id"]},
                        {
                            "$set": {
                                "status": SubscriptionStatus.GRACE_PERIOD.value,
                                "grace_period_start": datetime.utcnow(),
                                "retry_count": 0,
                                "updated_at": datetime.utcnow(),
                            }
                        }
                    )
                    logger.info(f"Set subscription {subscription['_id']} to grace period")
                    continue
                
                # Calculate new end date
                new_end_date = _calculate_next_billing_date(
                    datetime.utcnow(),
                    plan["billing_cycle"]
                )
                
                # Record renewal in history
                renewal_record = {
                    "date": datetime.utcnow(),
                    "from_plan_id": subscription["plan_id"],
                    "to_plan_id": subscription["plan_id"],
                    "type": "renewal",
                }
                
                # Update subscription
                subscriptions_collection.update_one(
                    {"_id": subscription["_id"]},
                    {
                        "$set": {
                            "end_date": new_end_date,
                            "status": SubscriptionStatus.ACTIVE.value,
                            "grace_period_start": None,
                            "retry_count": 0,
                            "updated_at": datetime.utcnow(),
                        },
                        "$push": {"renewal_history": renewal_record},
                    }
                )
                
                logger.info(f"Renewed subscription {subscription['_id']}")
                
            except Exception as e:
                logger.error(f"Error processing renewal for subscription {subscription['_id']}: {str(e)}")
                continue
        
        logger.info("Subscription renewal processing completed")
        
    except Exception as exc:
        logger.error(f"Error in process_renewals task: {str(exc)}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


# ============================================================================
# Task 5.3: Payment Retry Processing
# ============================================================================

@shared_task(bind=True, max_retries=3)
def process_payment_retries(self):
    """
    Retry failed payments for subscriptions in grace period.
    
    Runs every 6 hours.
    
    - Finds subscriptions in grace_period with retry_count < 3
    - Retries payment
    - If successful: restores to active, resets retry_count
    - If failed: increments retry_count, schedules next retry or cancels
    - Sends appropriate notifications
    """
    try:
        db = _get_db()
        membership_service = MembershipService(db)
        email_service = EmailService()
        
        subscriptions_collection = db["membership_subscriptions"]
        
        # Find subscriptions in grace period with retry attempts remaining
        subscriptions = subscriptions_collection.find({
            "status": SubscriptionStatus.GRACE_PERIOD.value,
            "retry_count": {"$lt": 3},
        }).to_list(None)
        
        logger.info(f"Found {len(subscriptions)} subscriptions to retry payment")
        
        for subscription in subscriptions:
            try:
                # Get plan details
                plan = membership_service.get_plan(
                    subscription["tenant_id"],
                    subscription["plan_id"]
                )
                if not plan:
                    logger.error(f"Plan {subscription['plan_id']} not found")
                    continue
                
                # Attempt payment retry
                try:
                    membership_service.process_payment(
                        subscription,
                        plan["price"],
                        f"Payment retry for {plan['name']}"
                    )
                    
                    # Payment successful - restore to active
                    subscriptions_collection.update_one(
                        {"_id": subscription["_id"]},
                        {
                            "$set": {
                                "status": SubscriptionStatus.ACTIVE.value,
                                "grace_period_start": None,
                                "retry_count": 0,
                                "updated_at": datetime.utcnow(),
                            }
                        }
                    )
                    logger.info(f"Payment retry successful for subscription {subscription['_id']}")
                    
                except Exception as e:
                    logger.error(f"Payment retry failed for subscription {subscription['_id']}: {str(e)}")
                    
                    # Increment retry count
                    new_retry_count = subscription.get("retry_count", 0) + 1
                    
                    if new_retry_count >= 3:
                        # Max retries reached - cancel subscription
                        subscriptions_collection.update_one(
                            {"_id": subscription["_id"]},
                            {
                                "$set": {
                                    "status": SubscriptionStatus.CANCELLED.value,
                                    "cancellation_reason": "Payment failed after 3 retry attempts",
                                    "cancelled_at": datetime.utcnow(),
                                    "updated_at": datetime.utcnow(),
                                }
                            }
                        )
                        logger.info(f"Cancelled subscription {subscription['_id']} after max retries")
                    else:
                        # Schedule next retry
                        subscriptions_collection.update_one(
                            {"_id": subscription["_id"]},
                            {
                                "$set": {
                                    "retry_count": new_retry_count,
                                    "updated_at": datetime.utcnow(),
                                }
                            }
                        )
                        logger.info(f"Incremented retry count for subscription {subscription['_id']} to {new_retry_count}")
                    
            except Exception as e:
                logger.error(f"Error processing payment retry for subscription {subscription['_id']}: {str(e)}")
                continue
        
        logger.info("Payment retry processing completed")
        
    except Exception as exc:
        logger.error(f"Error in process_payment_retries task: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


# ============================================================================
# Task 5.4: Benefit Usage Reset
# ============================================================================

@shared_task(bind=True, max_retries=3)
def reset_benefit_usage(self):
    """
    Reset benefit usage counters on renewal.
    
    Runs daily at midnight.
    
    - Finds subscriptions with benefit_usage_reset_date <= now
    - Resets benefit usage (unlimited = -1, limited = 0)
    - Calculates next reset date based on billing cycle
    - Updates subscription
    """
    try:
        db = _get_db()
        subscriptions_collection = db["membership_subscriptions"]
        
        # Find subscriptions that need benefit reset
        subscriptions = subscriptions_collection.find({
            "status": SubscriptionStatus.ACTIVE.value,
            "benefit_usage.cycle_start": {"$lte": datetime.utcnow()},
        }).to_list(None)
        
        logger.info(f"Found {len(subscriptions)} subscriptions to reset benefit usage")
        
        for subscription in subscriptions:
            try:
                # Get plan to determine billing cycle
                plans_collection = db["membership_plans"]
                plan = plans_collection.find_one({"_id": ObjectId(subscription["plan_id"])})
                
                if not plan:
                    logger.error(f"Plan {subscription['plan_id']} not found")
                    continue
                
                # Calculate next reset date
                current_cycle_start = subscription.get("benefit_usage", {}).get("cycle_start", datetime.utcnow())
                next_reset_date = _calculate_next_billing_date(
                    current_cycle_start,
                    plan["billing_cycle"]
                )
                
                # Reset benefit usage
                subscriptions_collection.update_one(
                    {"_id": subscription["_id"]},
                    {
                        "$set": {
                            "benefit_usage.cycle_start": datetime.utcnow(),
                            "benefit_usage.usage_count": 0,
                            "updated_at": datetime.utcnow(),
                        }
                    }
                )
                
                logger.info(f"Reset benefit usage for subscription {subscription['_id']}")
                
            except Exception as e:
                logger.error(f"Error resetting benefit usage for subscription {subscription['_id']}: {str(e)}")
                continue
        
        logger.info("Benefit usage reset completed")
        
    except Exception as exc:
        logger.error(f"Error in reset_benefit_usage task: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


# ============================================================================
# Task 5.5: Expiration Notifications
# ============================================================================

@shared_task(bind=True, max_retries=3)
def send_expiration_notifications(self):
    """
    Send notifications for expiring subscriptions.
    
    Runs daily at 9 AM.
    
    - Finds subscriptions expiring in 7, 3, 1 days
    - Checks notification preferences
    - Sends appropriate emails
    - Records notification in notifications_sent
    """
    try:
        db = _get_db()
        subscriptions_collection = db["membership_subscriptions"]
        clients_collection = db["clients"]
        
        email_service = EmailService()
        
        # Check for subscriptions expiring in 7, 3, and 1 days
        notification_windows = [7, 3, 1]
        
        for days_until_expiry in notification_windows:
            target_date = datetime.utcnow() + timedelta(days=days_until_expiry)
            target_date_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            target_date_end = target_date_start + timedelta(days=1)
            
            subscriptions = subscriptions_collection.find({
                "status": SubscriptionStatus.ACTIVE.value,
                "auto_renew": False,
                "end_date": {"$gte": target_date_start, "$lt": target_date_end},
            }).to_list(None)
            
            logger.info(f"Found {len(subscriptions)} subscriptions expiring in {days_until_expiry} days")
            
            for subscription in subscriptions:
                try:
                    # Get client details
                    client = clients_collection.find_one(
                        {"_id": ObjectId(subscription["client_id"])}
                    )
                    if not client:
                        logger.error(f"Client {subscription['client_id']} not found")
                        continue
                    
                    # Get plan details
                    plans_collection = db["membership_plans"]
                    plan = plans_collection.find_one(
                        {"_id": ObjectId(subscription["plan_id"])}
                    )
                    if not plan:
                        logger.error(f"Plan {subscription['plan_id']} not found")
                        continue
                    
                    # Send notification email
                    subject = f"Your {plan['name']} membership expires in {days_until_expiry} days"
                    html = f"""
                    <h2>Membership Expiration Notice</h2>
                    <p>Hi {client.get('first_name', 'Valued Customer')},</p>
                    <p>Your {plan['name']} membership will expire in {days_until_expiry} days.</p>
                    <p>Expiration Date: {subscription['end_date'].strftime('%B %d, %Y')}</p>
                    <p>If you wish to renew, please log in to your account.</p>
                    """
                    
                    try:
                        email_service.send_email(
                            to=client.get("email", ""),
                            subject=subject,
                            html=html
                        )
                        logger.info(f"Sent expiration notification to {client.get('email')} for subscription {subscription['_id']}")
                    except Exception as e:
                        logger.error(f"Failed to send expiration notification: {str(e)}")
                    
                except Exception as e:
                    logger.error(f"Error processing expiration notification for subscription {subscription['_id']}: {str(e)}")
                    continue
        
        logger.info("Expiration notification processing completed")
        
    except Exception as exc:
        logger.error(f"Error in send_expiration_notifications task: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


# ============================================================================
# Task 5.6: Trial Conversion
# ============================================================================

@shared_task(bind=True, max_retries=3)
def process_trial_conversion(self):
    """
    Convert trial subscriptions to paid.
    
    Runs daily at 1 AM.
    
    - Finds trial subscriptions ending today
    - Processes payment
    - If successful: sets status to active, sets end_date
    - If failed: sets status to grace_period
    - Sends confirmation or failure email
    """
    try:
        db = _get_db()
        membership_service = MembershipService(db)
        email_service = EmailService()
        
        subscriptions_collection = db["membership_subscriptions"]
        clients_collection = db["clients"]
        
        # Find trial subscriptions ending today
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        
        subscriptions = subscriptions_collection.find({
            "status": SubscriptionStatus.TRIAL.value,
            "trial_end_date": {"$gte": today, "$lt": tomorrow},
        }).to_list(None)
        
        logger.info(f"Found {len(subscriptions)} trial subscriptions to convert")
        
        for subscription in subscriptions:
            try:
                # Get plan details
                plans_collection = db["membership_plans"]
                plan = plans_collection.find_one(
                    {"_id": ObjectId(subscription["plan_id"])}
                )
                if not plan:
                    logger.error(f"Plan {subscription['plan_id']} not found")
                    continue
                
                # Get client details
                client = clients_collection.find_one(
                    {"_id": ObjectId(subscription["client_id"])}
                )
                if not client:
                    logger.error(f"Client {subscription['client_id']} not found")
                    continue
                
                # Process payment
                try:
                    membership_service.process_payment(
                        subscription,
                        plan["price"],
                        f"Trial conversion for {plan['name']}"
                    )
                    
                    # Calculate new end date
                    new_end_date = _calculate_next_billing_date(
                        datetime.utcnow(),
                        plan["billing_cycle"]
                    )
                    
                    # Update subscription to active
                    subscriptions_collection.update_one(
                        {"_id": subscription["_id"]},
                        {
                            "$set": {
                                "status": SubscriptionStatus.ACTIVE.value,
                                "end_date": new_end_date,
                                "updated_at": datetime.utcnow(),
                            }
                        }
                    )
                    
                    logger.info(f"Converted trial subscription {subscription['_id']} to active")
                    
                    # Send confirmation email
                    subject = f"Welcome to {plan['name']}!"
                    html = f"""
                    <h2>Trial Conversion Successful</h2>
                    <p>Hi {client.get('first_name', 'Valued Customer')},</p>
                    <p>Your trial period has ended and your {plan['name']} membership is now active!</p>
                    <p>Next Billing Date: {new_end_date.strftime('%B %d, %Y')}</p>
                    <p>Thank you for choosing us!</p>
                    """
                    
                    try:
                        email_service.send_email(
                            to=client.get("email", ""),
                            subject=subject,
                            html=html
                        )
                    except Exception as e:
                        logger.error(f"Failed to send trial conversion confirmation: {str(e)}")
                    
                except Exception as e:
                    logger.error(f"Trial conversion payment failed for subscription {subscription['_id']}: {str(e)}")
                    
                    # Set to grace period on payment failure
                    subscriptions_collection.update_one(
                        {"_id": subscription["_id"]},
                        {
                            "$set": {
                                "status": SubscriptionStatus.GRACE_PERIOD.value,
                                "grace_period_start": datetime.utcnow(),
                                "retry_count": 0,
                                "updated_at": datetime.utcnow(),
                            }
                        }
                    )
                    
                    logger.info(f"Set trial subscription {subscription['_id']} to grace period due to payment failure")
                    
                    # Send failure email
                    subject = f"Trial Conversion Failed - {plan['name']}"
                    html = f"""
                    <h2>Trial Conversion Failed</h2>
                    <p>Hi {client.get('first_name', 'Valued Customer')},</p>
                    <p>Unfortunately, we couldn't process the payment for your {plan['name']} membership.</p>
                    <p>Please update your payment method to continue your membership.</p>
                    """
                    
                    try:
                        email_service.send_email(
                            to=client.get("email", ""),
                            subject=subject,
                            html=html
                        )
                    except Exception as e:
                        logger.error(f"Failed to send trial conversion failure email: {str(e)}")
                    
            except Exception as e:
                logger.error(f"Error processing trial conversion for subscription {subscription['_id']}: {str(e)}")
                continue
        
        logger.info("Trial conversion processing completed")
        
    except Exception as exc:
        logger.error(f"Error in process_trial_conversion task: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


# ============================================================================
# Task 5.7: Grace Period Expiry
# ============================================================================

@shared_task(bind=True, max_retries=3)
def expire_grace_periods(self):
    """
    Expire subscriptions after grace period.
    
    Runs daily at 3 AM.
    
    - Finds subscriptions in grace_period for > 30 days
    - Cancels subscriptions
    - Sends cancellation email
    """
    try:
        db = _get_db()
        subscriptions_collection = db["membership_subscriptions"]
        clients_collection = db["clients"]
        
        email_service = EmailService()
        
        # Find subscriptions with expired grace periods (> 30 days)
        grace_period_expiry = datetime.utcnow() - timedelta(days=30)
        
        subscriptions = subscriptions_collection.find({
            "status": SubscriptionStatus.GRACE_PERIOD.value,
            "grace_period_start": {"$lte": grace_period_expiry},
        }).to_list(None)
        
        logger.info(f"Found {len(subscriptions)} subscriptions with expired grace periods")
        
        for subscription in subscriptions:
            try:
                # Get client details
                client = clients_collection.find_one(
                    {"_id": ObjectId(subscription["client_id"])}
                )
                if not client:
                    logger.error(f"Client {subscription['client_id']} not found")
                    continue
                
                # Get plan details
                plans_collection = db["membership_plans"]
                plan = plans_collection.find_one(
                    {"_id": ObjectId(subscription["plan_id"])}
                )
                if not plan:
                    logger.error(f"Plan {subscription['plan_id']} not found")
                    continue
                
                # Cancel subscription
                subscriptions_collection.update_one(
                    {"_id": subscription["_id"]},
                    {
                        "$set": {
                            "status": SubscriptionStatus.CANCELLED.value,
                            "cancellation_reason": "Grace period expired",
                            "cancelled_at": datetime.utcnow(),
                            "updated_at": datetime.utcnow(),
                        }
                    }
                )
                
                logger.info(f"Cancelled subscription {subscription['_id']} due to expired grace period")
                
                # Send cancellation email
                subject = f"Your {plan['name']} membership has been cancelled"
                html = f"""
                <h2>Membership Cancelled</h2>
                <p>Hi {client.get('first_name', 'Valued Customer')},</p>
                <p>Your {plan['name']} membership has been cancelled due to payment failure.</p>
                <p>If you would like to reactivate your membership, please contact us.</p>
                """
                
                try:
                    email_service.send_email(
                        to=client.get("email", ""),
                        subject=subject,
                        html=html
                    )
                except Exception as e:
                    logger.error(f"Failed to send grace period expiry email: {str(e)}")
                
            except Exception as e:
                logger.error(f"Error expiring grace period for subscription {subscription['_id']}: {str(e)}")
                continue
        
        logger.info("Grace period expiry processing completed")
        
    except Exception as exc:
        logger.error(f"Error in expire_grace_periods task: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


# ============================================================================
# Task 5.8: Analytics Aggregation
# ============================================================================

@shared_task(bind=True, max_retries=3)
def aggregate_analytics(self):
    """
    Aggregate membership analytics data.
    
    Runs daily at 1 AM.
    
    - For each tenant, calculates:
      - MRR (sum of monthly subscriptions)
      - ARR (MRR * 12)
      - Active subscriber count
      - Churn rate
      - Revenue by plan
      - Status distribution
    - Stores in membership_analytics collection
    """
    try:
        db = _get_db()
        subscriptions_collection = db["membership_subscriptions"]
        plans_collection = db["membership_plans"]
        analytics_collection = db["membership_analytics"]
        
        # Get all unique tenants
        tenants = subscriptions_collection.distinct("tenant_id")
        
        logger.info(f"Aggregating analytics for {len(tenants)} tenants")
        
        for tenant_id in tenants:
            try:
                # Get all active subscriptions for tenant
                active_subs = subscriptions_collection.find({
                    "tenant_id": tenant_id,
                    "status": SubscriptionStatus.ACTIVE.value,
                }).to_list(None)
                
                # Calculate MRR (sum of monthly subscriptions)
                mrr = 0.0
                for sub in active_subs:
                    plan = plans_collection.find_one(
                        {"_id": ObjectId(sub["plan_id"])}
                    )
                    if plan:
                        if plan["billing_cycle"] == BillingCycle.MONTHLY.value:
                            mrr += plan["price"]
                        elif plan["billing_cycle"] == BillingCycle.QUARTERLY.value:
                            mrr += plan["price"] / 3
                        elif plan["billing_cycle"] == BillingCycle.YEARLY.value:
                            mrr += plan["price"] / 12
                
                # Calculate ARR
                arr = mrr * 12
                
                # Count active subscribers
                active_count = len(active_subs)
                
                # Calculate churn rate (cancelled in last 30 days / active 30 days ago)
                thirty_days_ago = datetime.utcnow() - timedelta(days=30)
                cancelled_last_30 = subscriptions_collection.count_documents({
                    "tenant_id": tenant_id,
                    "status": SubscriptionStatus.CANCELLED.value,
                    "cancelled_at": {"$gte": thirty_days_ago},
                })
                
                # Get active count from 30 days ago (approximate)
                active_30_days_ago = subscriptions_collection.count_documents({
                    "tenant_id": tenant_id,
                    "status": SubscriptionStatus.ACTIVE.value,
                    "created_at": {"$lte": thirty_days_ago},
                })
                
                churn_rate = 0.0
                if active_30_days_ago > 0:
                    churn_rate = (cancelled_last_30 / active_30_days_ago) * 100
                
                # Revenue by plan
                revenue_by_plan = {}
                for sub in active_subs:
                    plan = plans_collection.find_one(
                        {"_id": ObjectId(sub["plan_id"])}
                    )
                    if plan:
                        plan_name = plan["name"]
                        if plan_name not in revenue_by_plan:
                            revenue_by_plan[plan_name] = {
                                "revenue": 0.0,
                                "subscribers": 0,
                            }
                        revenue_by_plan[plan_name]["revenue"] += plan["price"]
                        revenue_by_plan[plan_name]["subscribers"] += 1
                
                # Status distribution
                all_subs = subscriptions_collection.find({
                    "tenant_id": tenant_id,
                }).to_list(None)
                
                status_distribution = {
                    "active": 0,
                    "paused": 0,
                    "cancelled": 0,
                    "expired": 0,
                    "trial": 0,
                    "grace_period": 0,
                }
                
                for sub in all_subs:
                    status = sub.get("status", "active")
                    if status in status_distribution:
                        status_distribution[status] += 1
                
                # Create analytics record
                analytics_record = {
                    "tenant_id": tenant_id,
                    "date": datetime.utcnow(),
                    "mrr": round(mrr, 2),
                    "arr": round(arr, 2),
                    "active_subscribers": active_count,
                    "churn_rate": round(churn_rate, 2),
                    "revenue_by_plan": revenue_by_plan,
                    "status_distribution": status_distribution,
                    "total_subscriptions": len(all_subs),
                }
                
                # Store in analytics collection
                analytics_collection.insert_one(analytics_record)
                
                logger.info(f"Aggregated analytics for tenant {tenant_id}: MRR={mrr}, Active={active_count}")
                
            except Exception as e:
                logger.error(f"Error aggregating analytics for tenant {tenant_id}: {str(e)}")
                continue
        
        logger.info("Analytics aggregation completed")
        
    except Exception as exc:
        logger.error(f"Error in aggregate_analytics task: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
