"""Celery tasks for subscription management."""

import logging
from celery import shared_task
from datetime import datetime, timedelta
from app.services.subscription_service import SubscriptionService
from app.models.subscription import Subscription

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def check_trial_expiry(self):
    """
    Check for expired trials and set trial_expiry_action_required flag.
    Should be called daily via Celery Beat.
    """
    try:
        now = datetime.utcnow()
        
        # Find subscriptions where trial has just expired
        expired_trials = Subscription.objects(
            is_trial=True,
            trial_end__lt=now,
            trial_expiry_action_required=False
        )
        
        count = 0
        for subscription in expired_trials:
            try:
                SubscriptionService.handle_trial_expiry(str(subscription.tenant_id))
                count += 1
            except Exception as e:
                logger.error(f"Error handling trial expiry for tenant {subscription.tenant_id}: {str(e)}")
        
        logger.info(f"Trial expiry check completed: {count} trials marked as expired")
        return {"expired_trials": count}
    except Exception as exc:
        logger.error(f"Error in check_trial_expiry task: {str(exc)}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_trial_expiry_reminders(self):
    """
    Send email reminders for trials expiring soon.
    Should be called daily via Celery Beat.
    """
    try:
        now = datetime.utcnow()
        
        # Find trials expiring in 3 days
        three_days_later = now + timedelta(days=3)
        expiring_soon = Subscription.objects(
            is_trial=True,
            trial_end__gte=now,
            trial_end__lte=three_days_later,
            trial_expiry_action_required=False
        )
        
        count = 0
        for subscription in expiring_soon:
            try:
                days_remaining = (subscription.trial_end - now).days
                # TODO: Send email reminder
                # EmailService.send_trial_expiry_reminder(subscription.tenant_id, days_remaining)
                logger.info(f"Trial expiry reminder sent to tenant {subscription.tenant_id} ({days_remaining} days remaining)")
                count += 1
            except Exception as e:
                logger.error(f"Error sending reminder for tenant {subscription.tenant_id}: {str(e)}")
        
        logger.info(f"Trial expiry reminders completed: {count} reminders sent")
        return {"reminders_sent": count}
    except Exception as exc:
        logger.error(f"Error in send_trial_expiry_reminders task: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def check_subscription_expiry(self):
    """
    Check for expired subscriptions and handle grace period transitions.
    Should be called daily via Celery Beat.
    """
    try:
        result = SubscriptionService.check_and_expire_subscriptions()
        logger.info(f"Subscription expiry check completed: {result}")
        return result
    except Exception as exc:
        logger.error(f"Error in check_subscription_expiry task: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_renewal_reminders(self):
    """
    Send renewal reminders for subscriptions expiring soon.
    Should be called daily via Celery Beat.
    """
    try:
        result = SubscriptionService.send_renewal_reminders()
        logger.info(f"Renewal reminders sent: {result}")
        return result
    except Exception as exc:
        logger.error(f"Error in send_renewal_reminders task: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)
