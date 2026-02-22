"""Notification tasks for async processing."""

from celery import shared_task
from app.services.notification_service import NotificationService
from app.context import set_tenant_id
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_pending_notifications(self):
    """Process pending notifications for delivery."""
    try:
        # Get pending notifications
        notifications = NotificationService.get_pending_notifications(limit=100)
        
        for notification in notifications:
            # Set tenant context
            set_tenant_id(notification.tenant_id)
            
            try:
                # Route to appropriate delivery method
                if notification.channel == "email":
                    send_email_notification.delay(str(notification.id))
                elif notification.channel == "sms":
                    send_sms_notification.delay(str(notification.id))
                elif notification.channel == "push":
                    send_push_notification.delay(str(notification.id))
                elif notification.channel == "in_app":
                    mark_in_app_notification_sent.delay(str(notification.id))
                    
                # Mark as sent
                NotificationService.mark_notification_sent(str(notification.id))
                
            except Exception as e:
                logger.error(f"Error processing notification {notification.id}: {str(e)}")
                NotificationService.mark_notification_failed(str(notification.id), str(e))
                
    except Exception as e:
        logger.error(f"Error in process_pending_notifications: {str(e)}")
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def retry_failed_notifications(self):
    """Retry failed notifications."""
    try:
        # Get failed notifications that should be retried
        notifications = NotificationService.get_failed_notifications_for_retry(limit=50)
        
        for notification in notifications:
            # Set tenant context
            set_tenant_id(notification.tenant_id)
            
            try:
                # Retry the notification
                NotificationService.retry_notification(str(notification.id))
                
                # Route to appropriate delivery method
                if notification.channel == "email":
                    send_email_notification.delay(str(notification.id))
                elif notification.channel == "sms":
                    send_sms_notification.delay(str(notification.id))
                elif notification.channel == "push":
                    send_push_notification.delay(str(notification.id))
                    
            except Exception as e:
                logger.error(f"Error retrying notification {notification.id}: {str(e)}")
                
    except Exception as e:
        logger.error(f"Error in retry_failed_notifications: {str(e)}")
        raise self.retry(exc=e, countdown=300)


@shared_task(bind=True, max_retries=3)
def send_email_notification(self, notification_id: str):
    """Send email notification."""
    try:
        notification = NotificationService.get_notification(notification_id)
        if not notification:
            logger.error(f"Notification {notification_id} not found")
            return
            
        set_tenant_id(notification.tenant_id)
        
        if not notification.recipient_email:
            logger.error(f"No recipient email for notification {notification_id}")
            NotificationService.mark_notification_failed(notification_id, "No recipient email")
            return
        
        # Queue email task
        from app.tasks import send_email
        send_email.delay(
            to=notification.recipient_email,
            subject=notification.subject or "Notification",
            template="notification",
            context={
                "content": notification.content,
                "subject": notification.subject,
            },
        )
        
        NotificationService.mark_notification_sent(notification_id)
        NotificationService.log_notification(
            notification_id=notification_id,
            status="sent",
        )
        logger.info(f"Email notification {notification_id} queued")
        
    except Exception as e:
        logger.error(f"Error sending email notification {notification_id}: {str(e)}")
        NotificationService.mark_notification_failed(notification_id, str(e))
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def send_sms_notification(self, notification_id: str):
    """Send SMS notification."""
    try:
        notification = NotificationService.get_notification(notification_id)
        if not notification:
            logger.error(f"Notification {notification_id} not found")
            return
            
        set_tenant_id(notification.tenant_id)
        
        if not notification.recipient_phone:
            logger.error(f"No recipient phone for notification {notification_id}")
            NotificationService.mark_notification_failed(notification_id, "No recipient phone")
            return
        
        # Send SMS via Termii
        from app.services.termii_service import TermiiService
        termii_service = TermiiService()
        result = termii_service.send_sms_sync(
            notification.recipient_phone,
            notification.content,
        )
        
        if result:
            NotificationService.mark_notification_sent(notification_id)
            NotificationService.log_notification(
                notification_id=notification_id,
                status="sent",
                external_id=result.get("message_id"),
                external_response=result,
            )
            logger.info(f"SMS notification {notification_id} sent successfully")
        else:
            NotificationService.mark_notification_failed(
                notification_id, "Termii SMS send failed"
            )
            NotificationService.log_notification(
                notification_id=notification_id,
                status="failed",
                error_message="Termii SMS send failed",
            )
            logger.error(f"SMS notification {notification_id} failed to send")
        
    except Exception as e:
        logger.error(f"Error sending SMS notification {notification_id}: {str(e)}")
        NotificationService.mark_notification_failed(notification_id, str(e))
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def send_push_notification(self, notification_id: str):
    """Send push notification."""
    try:
        notification = NotificationService.get_notification(notification_id)
        if not notification:
            logger.error(f"Notification {notification_id} not found")
            return
            
        set_tenant_id(notification.tenant_id)
        
        # TODO: Integrate with push notification service
        # For now, just mark as delivered
        NotificationService.mark_notification_delivered(notification_id)
        logger.info(f"Push notification {notification_id} sent")
        
    except Exception as e:
        logger.error(f"Error sending push notification {notification_id}: {str(e)}")
        NotificationService.mark_notification_failed(notification_id, str(e))
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task
def mark_in_app_notification_sent(notification_id: str):
    """Mark in-app notification as sent."""
    try:
        notification = NotificationService.get_notification(notification_id)
        if not notification:
            logger.error(f"Notification {notification_id} not found")
            return
            
        set_tenant_id(notification.tenant_id)
        NotificationService.mark_notification_delivered(notification_id)
        logger.info(f"In-app notification {notification_id} marked as sent")
        
    except Exception as e:
        logger.error(f"Error marking in-app notification {notification_id}: {str(e)}")


@shared_task(bind=True, max_retries=3)
def send_appointment_reminders(self):
    """Send pending appointment reminders."""
    try:
        from app.services.appointment_reminder_service import AppointmentReminderService
        
        stats = AppointmentReminderService.send_pending_reminders()
        logger.info(f"Appointment reminders sent: {stats}")
        
    except Exception as e:
        logger.error(f"Error in send_appointment_reminders: {str(e)}")
        raise self.retry(exc=e, countdown=300)
