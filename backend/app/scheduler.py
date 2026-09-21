"""APScheduler setup for periodic tasks."""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def start_scheduler() -> None:
    """Start the APScheduler."""
    if not scheduler.running:
        scheduler.start()
        logger.info("APScheduler started")


def shutdown_scheduler() -> None:
    """Shutdown the APScheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("APScheduler shut down")


def register_jobs() -> None:
    """Register periodic jobs."""
    from app.tasks.subscriptions import (
        check_trial_expiry,
        send_trial_expiry_reminders,
        check_subscription_expiry,
        send_renewal_reminders,
    )
    from app.tasks.tenant_cleanup import cleanup_deleted_tenants
    from app.tasks.notifications import (
        process_pending_notifications,
        send_appointment_reminders,
        send_booking_reminders,
        send_staff_appointment_reminders,
        send_staff_shift_reminders,
    )

    scheduler.add_job(
        check_trial_expiry,
        trigger=IntervalTrigger(days=1),
        id="check-trial-expiry",
        name="Check trial expiry",
        replace_existing=True,
    )
    scheduler.add_job(
        send_trial_expiry_reminders,
        trigger=IntervalTrigger(days=1),
        id="send-trial-expiry-reminders",
        name="Send trial expiry reminders",
        replace_existing=True,
    )
    scheduler.add_job(
        check_subscription_expiry,
        trigger=IntervalTrigger(days=1),
        id="check-subscription-expiry",
        name="Check subscription expiry",
        replace_existing=True,
    )
    scheduler.add_job(
        send_renewal_reminders,
        trigger=IntervalTrigger(days=1),
        id="send-renewal-reminders",
        name="Send renewal reminders",
        replace_existing=True,
    )
    scheduler.add_job(
        cleanup_deleted_tenants,
        trigger=IntervalTrigger(days=1),
        id="cleanup-deleted-tenants",
        name="Cleanup deleted tenants",
        replace_existing=True,
    )
    scheduler.add_job(
        process_pending_notifications,
        trigger=IntervalTrigger(minutes=1),
        id="process-pending-notifications",
        name="Process pending notifications",
        replace_existing=True,
    )
    scheduler.add_job(
        send_appointment_reminders,
        trigger=IntervalTrigger(minutes=1),
        id="send-appointment-reminders",
        name="Send appointment reminders",
        replace_existing=True,
    )
    scheduler.add_job(
        send_booking_reminders,
        trigger=IntervalTrigger(minutes=1),
        id="send-booking-reminders",
        name="Send booking reminders",
        replace_existing=True,
    )
    scheduler.add_job(
        send_staff_appointment_reminders,
        trigger=IntervalTrigger(minutes=1),
        id="send-staff-appointment-reminders",
        name="Send staff appointment reminders",
        replace_existing=True,
    )
    scheduler.add_job(
        send_staff_shift_reminders,
        trigger=IntervalTrigger(minutes=1),
        id="send-staff-shift-reminders",
        name="Send staff shift reminders",
        replace_existing=True,
    )

    logger.info("APScheduler jobs registered")
