"""Background tasks configuration without Celery."""

import logging
from app.background import run_in_background

logger = logging.getLogger(__name__)


def send_email(to: str, subject: str, template: str, context: dict):
    """Send email to recipient via Resend API."""
    import requests
    from app.config import settings

    logger.info(f"Sending email to {to}: {subject}")
    logger.info(f"Template: {template}, Context: {context}")

    try:
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
            html_body = context.get('html_content', '<p>No content provided</p>')
        else:
            html_body = f"<p>{context}</p>"

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
        raise


def send_bulk_emails(recipients: list, subject: str, template: str, context: dict):
    """Send emails to multiple recipients."""
    import requests
    from app.config import settings

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


def send_notification(
    user_id: str,
    title: str,
    message: str,
    notification_type: str = "info",
    channel: str = "in_app",
    recipient_type: str = "staff",
    recipient_email: str = None,
    recipient_phone: str = None,
):
    """Send notification to user."""
    from app.services.notification_service import NotificationService
    from app.context import get_tenant_id

    tenant_id = get_tenant_id()
    notification = NotificationService.create_notification(
        recipient_id=user_id,
        recipient_type=recipient_type,
        notification_type=notification_type,
        channel=channel,
        content=message,
        subject=title,
        recipient_email=recipient_email,
        recipient_phone=recipient_phone,
    )
    logger.info(f"Notification {notification.id} queued for user {user_id}: {title}")
    return {"status": "sent", "user_id": user_id, "notification_id": str(notification.id)}


def send_bulk_notifications(
    user_ids: list,
    title: str,
    message: str,
    notification_type: str = "info",
    channel: str = "in_app",
    recipient_type: str = "staff",
):
    """Send notifications to multiple users."""
    from app.services.notification_service import NotificationService

    created = []
    for uid in user_ids:
        try:
            n = NotificationService.create_notification(
                recipient_id=uid,
                recipient_type=recipient_type,
                notification_type=notification_type,
                channel=channel,
                content=message,
                subject=title,
            )
            created.append(str(n.id))
        except Exception:
            pass

    logger.info(f"Bulk notifications queued: {len(created)} of {len(user_ids)}")
    return {"status": "sent", "count": len(created)}


def generate_report(report_type: str, filters: dict):
    """Generate report."""
    from app.services.owner_dashboard_service import OwnerDashboardService
    from app.context import get_tenant_id

    tenant_id = get_tenant_id()
    service = OwnerDashboardService()
    result = service.get_all_metrics(tenant_id, use_cache=False)
    logger.info(f"Report {report_type} generated for tenant {tenant_id}")
    return {"status": "generated", "report_type": report_type, "data": result}


def export_data(data_type: str, tenant_id: str, format: str):
    """Export data for tenant."""
    from mongoengine.connection import get_db

    db = get_db()
    allowed = {"appointments", "customers", "invoices", "payments", "staff", "services"}
    if data_type not in allowed:
        raise ValueError(f"Unsupported data type: {data_type}")
    collection = db[data_type]
    records = list(collection.find({"tenant_id": tenant_id}).limit(10000))
    logger.info(f"Exported {len(records)} {data_type} records for tenant {tenant_id}")
    return {"status": "exported", "data_type": data_type, "count": len(records), "format": format}


def deliver_webhook(webhook_url: str, event: str, data: dict):
    """Deliver webhook to external service."""
    import httpx

    payload = {
        "event": event,
        "data": data,
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    }
    headers = {"Content-Type": "application/json"}
    response = httpx.post(webhook_url, json=payload, headers=headers, timeout=10)
    logger.info(f"Webhook delivered to {webhook_url}: {response.status_code}")
    return {"status": "delivered", "event": event, "status_code": response.status_code}


def retry_failed_webhook(webhook_id: str):
    """Retry failed webhook delivery."""
    logger.info(f"Retrying webhook {webhook_id}")
    return {"status": "retried", "webhook_id": webhook_id}


def queue_notification(
    tenant_id: str,
    notification_type: str,
    recipient_id: str,
    data: dict,
    recipient_type: str = "customer",
    recipient_email: str = None,
    recipient_phone: str = None,
):
    """Queue a notification to be sent asynchronously."""
    from app.services.notification_service import NotificationService
    from app.context import set_tenant_id
    from bson import ObjectId

    logger.info(f"Queueing {notification_type} notification for tenant {tenant_id} to recipient {recipient_id}")

    try:
        set_tenant_id(ObjectId(tenant_id))
    except Exception:
        pass

    # Look up recipient contact info if not provided
    if not recipient_email or not recipient_phone:
        try:
            if recipient_type == "customer":
                from app.models.customer import Customer
                customer = Customer.objects(
                    tenant_id=ObjectId(tenant_id), id=ObjectId(recipient_id)
                ).first()
                if customer:
                    recipient_email = recipient_email or getattr(customer, "email", None)
                    recipient_phone = recipient_phone or getattr(customer, "phone", None)
            else:
                from app.models.staff import Staff
                from app.models.user import User
                staff = Staff.objects(
                    tenant_id=ObjectId(tenant_id), id=ObjectId(recipient_id)
                ).first()
                if staff and staff.user_id:
                    user = User.objects(id=staff.user_id).first()
                    if user:
                        recipient_email = recipient_email or getattr(user, "email", None)
                        recipient_phone = recipient_phone or getattr(user, "phone", None)
        except Exception as e:
            logger.warning(f"Could not look up recipient contact info: {e}")

    # Determine channels based on notification type
    channels = []
    if notification_type in [
        "appointment_reminder_24h",
        "appointment_reminder_1h",
    ]:
        channels = ["in_app", "email"]
        if recipient_phone:
            channels.append("sms")
    elif notification_type in [
        "payment_success",
        "payment_failed",
        "payment_cancelled",
        "refund_success",
        "appointment_confirmed",
        "appointment_cancelled",
        "appointment_completed",
        "shift_assigned",
        "time_off_approved",
        "time_off_rejected",
        "new_appointment",
    ]:
        channels = ["in_app", "email"]
    else:
        channels = ["in_app"]

    for channel in channels:
        try:
            NotificationService.create_notification(
                recipient_id=recipient_id,
                recipient_type=recipient_type,
                notification_type=notification_type,
                channel=channel,
                content=str(data),
                subject=notification_type.replace("_", " ").title(),
                template_variables=data if isinstance(data, dict) else {},
                recipient_email=recipient_email if channel == "email" else None,
                recipient_phone=recipient_phone if channel in ("sms", "push") else None,
            )
        except Exception as e:
            logger.error(f"Error creating {channel} notification: {e}")

    return {"status": "queued", "notification_type": notification_type}
