"""Celery tasks configuration."""

from celery import Celery
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Create Celery app with development-friendly defaults
celery_app = Celery(
    "salon_saas",
    broker=settings.rabbitmq_url,
    backend=settings.redis_url,
)

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
    # Retry on startup to wait for broker to be ready
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,
    # Celery Beat schedule for periodic tasks
    beat_schedule={
        "check-trial-expiry": {
            "task": "app.tasks.subscriptions.check_trial_expiry",
            "schedule": 86400.0,  # Run daily (86400 seconds)
        },
        "send-trial-expiry-reminders": {
            "task": "app.tasks.subscriptions.send_trial_expiry_reminders",
            "schedule": 86400.0,  # Run daily
        },
        "check-subscription-expiry": {
            "task": "app.tasks.subscriptions.check_subscription_expiry",
            "schedule": 86400.0,  # Run daily
        },
        "send-renewal-reminders": {
            "task": "app.tasks.subscriptions.send_renewal_reminders",
            "schedule": 86400.0,  # Run daily
        },
        "cleanup-deleted-tenants": {
            "task": "app.tasks.tenant_cleanup.cleanup_deleted_tenants",
            "schedule": 86400.0,  # Run daily
        },
    },
)

logger.info("Celery app initialized (tasks will queue but may not execute without broker)")


@celery_app.task(bind=True, max_retries=3)
def send_email(self, to: str, subject: str, template: str, context: dict):
    """Send email to recipient via Resend API."""
    import logging
    import requests
    
    logger = logging.getLogger(__name__)
    try:
        logger.info(f"Sending email to {to}: {subject}")
        logger.info(f"Template: {template}, Context: {context}")
        
        # Prepare email body based on template
        if template == "registration_verification":
            html_body = f"""
            <h1>Verify Your Salon Registration</h1>
            <p>Hello,</p>
            <p>Thank you for registering <strong>{context.get('salon_name', 'your salon')}</strong> with Kenikool.</p>
            <p>Your verification code is:</p>
            <h2 style="font-size: 32px; font-weight: bold; font-family: monospace;">{context.get('verification_code', '000000')}</h2>
            <p>This code will expire in <strong>{context.get('expires_in_minutes', 15)} minutes</strong>.</p>
            <p>If you didn't request this code, please ignore this email.</p>
            <p>Best regards,<br>Kenikool Team</p>
            """
        elif template == "welcome":
            html_body = f"""
            <h1>Welcome to Kenikool!</h1>
            <p>Hello {context.get('owner_name', 'there')},</p>
            <p>Your salon <strong>{context.get('salon_name', 'your salon')}</strong> has been successfully registered on Kenikool.</p>
            <h3>Your Account Details:</h3>
            <ul>
                <li><strong>Email:</strong> {context.get('email', '')}</li>
                <li><strong>Salon URL:</strong> <a href="{context.get('full_url', '')}">{context.get('full_url', '')}</a></li>
                <li><strong>Subscription Tier:</strong> {context.get('subscription_tier', 'Trial (30 days)')}</li>
            </ul>
            <h3>Next Steps:</h3>
            <ol>
                <li>Log in to your dashboard at <a href="{context.get('full_url', '')}">{context.get('full_url', '')}</a></li>
                <li>Complete your salon profile and settings</li>
                <li>Add your staff members and services</li>
                <li>Set up your booking calendar</li>
            </ol>
            <p>If you have any questions, feel free to reach out to our support team.</p>
            <p>Best regards,<br>Kenikool Team</p>
            """
        elif template == "staff_welcome":
            salon_name = context.get('salon_name', 'your salon')
            html_body = f"""
            <h1>Welcome to {salon_name}!</h1>
            <p>Hello {context.get('first_name', 'there')},</p>
            <p>You have been added as a staff member at <strong>{salon_name}</strong>. Your account is now ready to use.</p>
            <h3>Your Login Credentials:</h3>
            <ul>
                <li><strong>Email:</strong> {context.get('email', '')}</li>
                <li><strong>Temporary Password:</strong> <code style="background-color: #f0f0f0; padding: 5px 10px; border-radius: 3px; font-family: monospace;">{context.get('temp_password', '')}</code></li>
            </ul>
            <h3>Important:</h3>
            <p><strong>Please change your password immediately after logging in.</strong> You can do this in your account settings.</p>
            <h3>Next Steps:</h3>
            <ol>
                <li>Log in to the staff portal with your email and temporary password</li>
                <li>Change your password to something secure</li>
                <li>Complete your profile information</li>
                <li>Start managing your appointments and schedule</li>
            </ol>
            <p>If you have any questions or need assistance, please contact your manager at {salon_name}.</p>
            <p>Best regards,<br>{salon_name} Team</p>
            """
        elif template == "custom":
            # For custom HTML templates, use the html_content directly
            html_body = context.get('html_content', '<p>No content provided</p>')
        else:
            html_body = f"<p>{context}</p>"
        
        # Send via Resend API
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {settings.resend_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "from": settings.email_from,
                "to": to,
                "subject": subject,
                "html": html_body,
            },
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Email sent successfully to {to}. Message ID: {result.get('id')}")
            return {"status": "sent", "to": to, "message_id": result.get("id")}
        else:
            logger.error(f"Failed to send email to {to}. Status: {response.status_code}, Response: {response.text}")
            raise Exception(f"Resend API error: {response.text}")
            
    except Exception as exc:
        logger.error(f"Error sending email: {exc}")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True, max_retries=3)
def send_bulk_emails(self, recipients: list, subject: str, template: str, context: dict):
    """Send emails to multiple recipients."""
    import logging
    import requests
    
    logger = logging.getLogger(__name__)
    try:
        logger.info(f"Sending bulk emails to {len(recipients)} recipients")
        
        results = []
        for recipient in recipients:
            try:
                response = requests.post(
                    "https://api.resend.com/emails",
                    headers={
                        "Authorization": f"Bearer {settings.resend_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "from": settings.email_from,
                        "to": recipient,
                        "subject": subject,
                        "html": f"<p>{context}</p>",
                    },
                )
                
                if response.status_code == 200:
                    results.append({"recipient": recipient, "status": "sent"})
                else:
                    results.append({"recipient": recipient, "status": "failed"})
                    
            except Exception as e:
                logger.error(f"Error sending email to {recipient}: {e}")
                results.append({"recipient": recipient, "status": "failed"})
        
        logger.info(f"Bulk email sending completed. Results: {results}")
        return {"status": "completed", "count": len(recipients), "results": results}
        
    except Exception as exc:
        logger.error(f"Error sending bulk emails: {exc}")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True, max_retries=3)
def send_notification(self, user_id: str, title: str, message: str):
    """Send notification to user."""
    import logging
    logger = logging.getLogger(__name__)
    try:
        logger.info(f"Sending notification to user {user_id}: {title}")
        # TODO: Implement notification sending logic
        return {"status": "sent", "user_id": user_id}
    except Exception as exc:
        logger.error(f"Error sending notification: {exc}")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True, max_retries=3)
def send_bulk_notifications(self, user_ids: list, title: str, message: str):
    """Send notifications to multiple users."""
    import logging
    logger = logging.getLogger(__name__)
    try:
        logger.info(f"Sending bulk notifications to {len(user_ids)} users")
        # TODO: Implement bulk notification sending logic
        return {"status": "sent", "count": len(user_ids)}
    except Exception as exc:
        logger.error(f"Error sending bulk notifications: {exc}")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True, max_retries=3)
def generate_report(self, report_type: str, filters: dict):
    """Generate report."""
    import logging
    logger = logging.getLogger(__name__)
    try:
        logger.info(f"Generating {report_type} report with filters: {filters}")
        # TODO: Implement report generation logic
        return {"status": "generated", "report_type": report_type}
    except Exception as exc:
        logger.error(f"Error generating report: {exc}")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True, max_retries=3)
def export_data(self, data_type: str, tenant_id: str, format: str):
    """Export data for tenant."""
    import logging
    logger = logging.getLogger(__name__)
    try:
        logger.info(f"Exporting {data_type} data for tenant {tenant_id} in {format} format")
        # TODO: Implement data export logic
        return {"status": "exported", "data_type": data_type}
    except Exception as exc:
        logger.error(f"Error exporting data: {exc}")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True, max_retries=3)
def deliver_webhook(self, webhook_url: str, event: str, data: dict):
    """Deliver webhook to external service."""
    import logging
    logger = logging.getLogger(__name__)
    try:
        logger.info(f"Delivering webhook to {webhook_url} for event {event}")
        # TODO: Implement webhook delivery logic
        return {"status": "delivered", "event": event}
    except Exception as exc:
        logger.error(f"Error delivering webhook: {exc}")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True, max_retries=3)
def retry_failed_webhook(self, webhook_id: str):
    """Retry failed webhook delivery."""
    import logging
    logger = logging.getLogger(__name__)
    try:
        logger.info(f"Retrying webhook {webhook_id}")
        # TODO: Implement webhook retry logic
        return {"status": "retried", "webhook_id": webhook_id}
    except Exception as exc:
        logger.error(f"Error retrying webhook: {exc}")
        raise self.retry(exc=exc, countdown=60)


def queue_notification(tenant_id: str, notification_type: str, recipient_id: str, data: dict):
    """Queue a notification to be sent asynchronously."""
    import logging
    logger = logging.getLogger(__name__)
    try:
        logger.info(f"Queueing {notification_type} notification for tenant {tenant_id} to recipient {recipient_id}")
        # Queue the notification task
        send_notification.delay(recipient_id, notification_type, str(data))
        return {"status": "queued", "notification_type": notification_type}
    except Exception as exc:
        logger.error(f"Error queueing notification: {exc}")
        return {"status": "failed", "error": str(exc)}
