"""
Celery application configuration
"""
from celery import Celery
from celery.schedules import crontab
from app.config import settings

# Create Celery app with lazy initialization
celery_app = Celery(
    "salon_saas",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    # Don't include tasks on import to avoid circular imports and connection attempts
    # Tasks will be discovered when Celery worker starts
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    # Broker connection settings - fail fast if Redis is unavailable
    broker_connection_retry=False,  # Don't retry connection on startup
    broker_connection_retry_on_startup=False,  # Don't retry on startup
    broker_connection_max_retries=0,  # No retries when sending tasks
    # Result backend connection settings
    result_backend_transport_options={
        'master_name': 'mymaster',
        'socket_connect_timeout': 1,  # 1 second timeout
        'socket_timeout': 1,  # 1 second timeout
        'retry_on_timeout': False,
    },
)

# Celery Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "send-24-hour-reminders": {
        "task": "app.tasks.reminder_tasks.send_24_hour_reminders",
        "schedule": crontab(minute="0", hour="9"),  # Run daily at 9 AM
    },
    "send-2-hour-reminders": {
        "task": "app.tasks.reminder_tasks.send_2_hour_reminders",
        "schedule": crontab(minute="*/30"),  # Run every 30 minutes
    },
    "check-waitlist-availability": {
        "task": "app.tasks.waitlist_tasks.check_waitlist_availability",
        "schedule": crontab(minute="*/15"),  # Run every 15 minutes
    },
    "send-birthday-campaigns": {
        "task": "check_birthday_campaigns",
        "schedule": crontab(minute="0", hour="9"),  # Run daily at 9 AM
    },
    "send-winback-campaigns": {
        "task": "check_winback_campaigns",
        "schedule": crontab(minute="0", hour="10"),  # Run daily at 10 AM
    },
    "send-pending-review-requests": {
        "task": "app.tasks.review_tasks.send_pending_review_requests",
        "schedule": crontab(minute="0", hour="10"),  # Run daily at 10 AM
    },
    "process-subscription-renewals": {
        "task": "process_subscription_renewals",
        "schedule": crontab(minute="0", hour="0"),  # Run daily at midnight
    },
    "reset-monthly-booking-limits": {
        "task": "reset_monthly_booking_limits",
        "schedule": crontab(minute="0", hour="0", day_of_month="1"),  # Run on 1st of each month
    },
    "send-renewal-reminders": {
        "task": "send_renewal_reminders",
        "schedule": crontab(minute="0", hour="9"),  # Run daily at 9 AM
    },
    "check-expired-gift-cards": {
        "task": "check_expired_gift_cards",
        "schedule": crontab(minute="0", hour="0"),  # Run daily at midnight
    },
    "send-gift-card-expiry-reminders": {
        "task": "send_gift_card_expiry_reminders",
        "schedule": crontab(minute="0", hour="9"),  # Run daily at 9 AM
    },
    # AI Learning Tasks - Run during off-peak hours
    "run-daily-ai-learning": {
        "task": "run_daily_ai_learning",
        "schedule": crontab(minute="0", hour="2"),  # Run daily at 2 AM (off-peak)
    },
    "cleanup-old-ai-data": {
        "task": "cleanup_old_ai_data",
        "schedule": crontab(minute="0", hour="3", day_of_week="0"),  # Run weekly on Sunday at 3 AM
    },
    # Client Analytics Tasks
    "update-stale-analytics": {
        "task": "update_stale_analytics",
        "schedule": crontab(minute="0", hour="*/6"),  # Run every 6 hours
    },
    "identify-at-risk-clients": {
        "task": "identify_at_risk_clients",
        "schedule": crontab(minute="0", hour="8"),  # Run daily at 8 AM
    },
    "update-client-segments": {
        "task": "update_client_segments",
        "schedule": crontab(minute="0", hour="2"),  # Run daily at 2 AM
    },
    # Unified Booking Management Tasks (Phase 3)
    "send-booking-reminders": {
        "task": "app.tasks.booking_tasks.send_booking_reminders",
        "schedule": crontab(minute="0", hour="*/1"),  # Run every hour
    },
    "process-recurring-bookings": {
        "task": "app.tasks.booking_tasks.process_recurring_bookings",
        "schedule": crontab(minute="0", hour="1"),  # Run daily at 1 AM
    },
    "expire-old-inquiries": {
        "task": "app.tasks.booking_tasks.expire_old_inquiries",
        "schedule": crontab(minute="0", hour="2"),  # Run daily at 2 AM
    },
    "send-family-payment-reminders": {
        "task": "app.tasks.booking_tasks.send_family_payment_reminders",
        "schedule": crontab(minute="0", hour="9", day_of_week="1"),  # Run weekly on Monday at 9 AM
    },
    # Client Communication Tasks (Phase 4 - Task 4.6)
    "send-feedback-requests": {
        "task": "app.tasks.booking_tasks.send_feedback_requests",
        "schedule": crontab(minute="0", hour="11"),  # Run daily at 11 AM
    },
    "send-birthday-greetings": {
        "task": "app.tasks.booking_tasks.send_birthday_greetings",
        "schedule": crontab(minute="0", hour="8"),  # Run daily at 8 AM
    },
    "send-reengagement-messages": {
        "task": "app.tasks.booking_tasks.send_reengagement_messages",
        "schedule": crontab(minute="0", hour="10", day_of_week="3"),  # Run weekly on Wednesday at 10 AM
    },
    # Waitlist Expiration Task (Task 9)
    "expire-old-waitlist-entries": {
        "task": "app.tasks.waitlist_tasks.expire_old_waitlist_entries",
        "schedule": crontab(minute="0", hour="2"),  # Run daily at 2:00 AM
    },
    # Settings System Tasks
    "cleanup-expired-sessions": {
        "task": "app.tasks.settings_tasks.cleanup_expired_sessions",
        "schedule": crontab(minute="0", hour="3"),  # Run daily at 3:00 AM
    },
    "cleanup-old-exports": {
        "task": "app.tasks.settings_tasks.cleanup_old_exports",
        "schedule": crontab(minute="0", hour="4"),  # Run daily at 4:00 AM
    },
    "execute-account-deletion": {
        "task": "app.tasks.settings_tasks.execute_account_deletion",
        "schedule": crontab(minute="0", hour="5"),  # Run daily at 5:00 AM
    },
    "send-security-alerts": {
        "task": "app.tasks.settings_tasks.send_security_alerts",
        "schedule": crontab(minute="*/30"),  # Run every 30 minutes
    },
    # Gift Card Tasks (Phase 3)
    "check-gift-card-expiration": {
        "task": "app.tasks.gift_card_tasks.check_gift_card_expiration_task",
        "schedule": crontab(minute="0", hour="0"),  # Run daily at midnight
    },
    "process-failed-gift-card-deliveries": {
        "task": "app.tasks.gift_card_tasks.process_failed_deliveries_task",
        "schedule": crontab(minute="0", hour="*/4"),  # Run every 4 hours
    },
    "cleanup-old-gift-cards": {
        "task": "app.tasks.gift_card_tasks.cleanup_old_gift_cards_task",
        "schedule": crontab(minute="0", hour="3", day_of_week="0"),  # Run weekly on Sunday at 3 AM
    },
    # Membership System Tasks (Phase 5)
    "process-membership-renewals": {
        "task": "app.tasks.membership_tasks.process_renewals",
        "schedule": crontab(minute="0", hour="2"),  # Run daily at 2 AM
    },
    "process-membership-payment-retries": {
        "task": "app.tasks.membership_tasks.process_payment_retries",
        "schedule": crontab(minute="0", hour="*/6"),  # Run every 6 hours
    },
    "reset-membership-benefit-usage": {
        "task": "app.tasks.membership_tasks.reset_benefit_usage",
        "schedule": crontab(minute="0", hour="0"),  # Run daily at midnight
    },
    "send-membership-expiration-notifications": {
        "task": "app.tasks.membership_tasks.send_expiration_notifications",
        "schedule": crontab(minute="0", hour="9"),  # Run daily at 9 AM
    },
    "process-membership-trial-conversion": {
        "task": "app.tasks.membership_tasks.process_trial_conversion",
        "schedule": crontab(minute="0", hour="1"),  # Run daily at 1 AM
    },
    "expire-membership-grace-periods": {
        "task": "app.tasks.membership_tasks.expire_grace_periods",
        "schedule": crontab(minute="0", hour="3"),  # Run daily at 3 AM
    },
    "aggregate-membership-analytics": {
        "task": "app.tasks.membership_tasks.aggregate_analytics",
        "schedule": crontab(minute="0", hour="1"),  # Run daily at 1 AM
    },
}

if __name__ == "__main__":
    celery_app.start()
