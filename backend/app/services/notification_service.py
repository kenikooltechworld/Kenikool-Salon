"""Notification service for managing notifications."""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from app.models.notification import (
    Notification,
    NotificationTemplate,
    NotificationPreference,
    NotificationLog,
)
from app.context import get_tenant_id
from app.services.termii_service import TermiiService

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for managing notifications."""

    @staticmethod
    def create_notification(
        recipient_id: str,
        recipient_type: str,
        notification_type: str,
        channel: str,
        content: str,
        subject: str = None,
        template_id: str = None,
        template_variables: Dict[str, Any] = None,
        appointment_id: str = None,
        payment_id: str = None,
        shift_id: str = None,
        time_off_request_id: str = None,
        recipient_email: str = None,
        recipient_phone: str = None,
    ) -> Notification:
        """Create a new notification."""
        tenant_id = get_tenant_id()

        notification = Notification(
            tenant_id=tenant_id,
            recipient_id=recipient_id,
            recipient_type=recipient_type,
            notification_type=notification_type,
            channel=channel,
            content=content,
            subject=subject,
            template_id=template_id,
            template_variables=template_variables or {},
            appointment_id=appointment_id,
            payment_id=payment_id,
            shift_id=shift_id,
            time_off_request_id=time_off_request_id,
            recipient_email=recipient_email,
            recipient_phone=recipient_phone,
            status="pending",
        )
        notification.save()
        return notification

    @staticmethod
    def get_notification(notification_id: str) -> Optional[Notification]:
        """Get notification by ID."""
        from bson import ObjectId
        
        tenant_id = get_tenant_id()
        if not tenant_id:
            return None
        
        try:
            notification_obj_id = ObjectId(notification_id) if isinstance(notification_id, str) else notification_id
            return Notification.objects(
                id=notification_obj_id, tenant_id=tenant_id
            ).first()
        except Exception:
            # Invalid ObjectId format
            return None

    @staticmethod
    def get_notifications(
        recipient_id: str = None,
        notification_type: str = None,
        channel: str = None,
        status: str = None,
        limit: int = 50,
        skip: int = 0,
    ) -> List[Notification]:
        """Get notifications with optional filtering."""
        from bson import ObjectId
        
        tenant_id = get_tenant_id()
        if not tenant_id:
            return []
            
        query = Notification.objects(tenant_id=tenant_id)

        if recipient_id:
            try:
                recipient_obj_id = ObjectId(recipient_id) if isinstance(recipient_id, str) else recipient_id
                query = query(recipient_id=recipient_obj_id)
            except Exception:
                # Invalid ObjectId format, return empty list
                return []
        if notification_type:
            query = query(notification_type=notification_type)
        if channel:
            query = query(channel=channel)
        if status:
            query = query(status=status)

        return query.order_by("-created_at")[skip : skip + limit]

    @staticmethod
    def get_pending_notifications(limit: int = 100) -> List[Notification]:
        """Get pending notifications for processing."""
        tenant_id = get_tenant_id()
        return Notification.objects(
            tenant_id=tenant_id, status="pending"
        ).order_by("created_at")[:limit]

    @staticmethod
    def get_failed_notifications_for_retry(limit: int = 50) -> List[Notification]:
        """Get failed notifications that should be retried."""
        tenant_id = get_tenant_id()
        return Notification.objects(
            tenant_id=tenant_id,
            status="failed",
            retry_count__lt=3,
        ).order_by("last_retry_at")[:limit]

    @staticmethod
    def mark_notification_sent(notification_id: str) -> Notification:
        """Mark notification as sent."""
        notification = NotificationService.get_notification(notification_id)
        if notification:
            notification.mark_sent()
        return notification

    @staticmethod
    def mark_notification_delivered(notification_id: str) -> Notification:
        """Mark notification as delivered."""
        notification = NotificationService.get_notification(notification_id)
        if notification:
            notification.mark_delivered()
        return notification

    @staticmethod
    def mark_notification_failed(
        notification_id: str, reason: str = None
    ) -> Notification:
        """Mark notification as failed."""
        notification = NotificationService.get_notification(notification_id)
        if notification:
            notification.mark_failed(reason)
        return notification

    @staticmethod
    def retry_notification(notification_id: str) -> Notification:
        """Retry a failed notification."""
        notification = NotificationService.get_notification(notification_id)
        if notification and notification.should_retry():
            notification.increment_retry()
            notification.status = "pending"
            notification.save()
        return notification

    @staticmethod
    def mark_notification_read(notification_id: str) -> Notification:
        """Mark notification as read."""
        notification = NotificationService.get_notification(notification_id)
        if notification:
            notification.mark_read()
        return notification

    @staticmethod
    def get_unread_notifications(recipient_id: str) -> List[Notification]:
        """Get unread notifications for a recipient."""
        from bson import ObjectId
        
        tenant_id = get_tenant_id()
        if not tenant_id:
            return []
        
        try:
            recipient_obj_id = ObjectId(recipient_id) if isinstance(recipient_id, str) else recipient_id
            return Notification.objects(
                tenant_id=tenant_id, recipient_id=recipient_obj_id, is_read=False
            ).order_by("-created_at")
        except Exception:
            # Invalid ObjectId format, return empty list
            return []

    @staticmethod
    def create_template(
        template_type: str,
        channel: str,
        body: str,
        subject: str = None,
        variables: List[str] = None,
        is_default: bool = False,
    ) -> NotificationTemplate:
        """Create a notification template."""
        tenant_id = get_tenant_id()

        template = NotificationTemplate(
            tenant_id=tenant_id,
            template_type=template_type,
            channel=channel,
            subject=subject,
            body=body,
            variables=variables or [],
            is_default=is_default,
        )
        template.save()
        return template

    @staticmethod
    def get_template(
        template_type: str, channel: str
    ) -> Optional[NotificationTemplate]:
        """Get notification template."""
        tenant_id = get_tenant_id()
        return NotificationTemplate.objects(
            tenant_id=tenant_id,
            template_type=template_type,
            channel=channel,
            is_active=True,
        ).first()

    @staticmethod
    def get_templates(
        template_type: str = None, channel: str = None
    ) -> List[NotificationTemplate]:
        """Get notification templates."""
        tenant_id = get_tenant_id()
        query = NotificationTemplate.objects(tenant_id=tenant_id, is_active=True)

        if template_type:
            query = query(template_type=template_type)
        if channel:
            query = query(channel=channel)

        return query.order_by("template_type", "channel")

    @staticmethod
    def update_template(
        template_id: str,
        body: str = None,
        subject: str = None,
        variables: List[str] = None,
    ) -> Optional[NotificationTemplate]:
        """Update a notification template."""
        tenant_id = get_tenant_id()
        template = NotificationTemplate.objects(
            id=template_id, tenant_id=tenant_id
        ).first()

        if template:
            if body:
                template.body = body
            if subject:
                template.subject = subject
            if variables:
                template.variables = variables
            template.save()

        return template

    @staticmethod
    def set_preference(
        customer_id: str,
        notification_type: str,
        channel: str,
        enabled: bool,
    ) -> NotificationPreference:
        """Set notification preference for a customer."""
        tenant_id = get_tenant_id()

        preference = NotificationPreference.objects(
            tenant_id=tenant_id,
            customer_id=customer_id,
            notification_type=notification_type,
            channel=channel,
        ).first()

        if preference:
            preference.enabled = enabled
            preference.save()
        else:
            preference = NotificationPreference(
                tenant_id=tenant_id,
                customer_id=customer_id,
                notification_type=notification_type,
                channel=channel,
                enabled=enabled,
            )
            preference.save()

        return preference

    @staticmethod
    def get_preference(
        customer_id: str, notification_type: str, channel: str
    ) -> Optional[NotificationPreference]:
        """Get notification preference for a customer."""
        tenant_id = get_tenant_id()
        return NotificationPreference.objects(
            tenant_id=tenant_id,
            customer_id=customer_id,
            notification_type=notification_type,
            channel=channel,
        ).first()

    @staticmethod
    def get_preferences(customer_id: str) -> List[NotificationPreference]:
        """Get all notification preferences for a customer."""
        tenant_id = get_tenant_id()
        return NotificationPreference.objects(
            tenant_id=tenant_id, customer_id=customer_id
        )

    @staticmethod
    def is_notification_enabled(
        customer_id: str, notification_type: str, channel: str
    ) -> bool:
        """Check if a notification is enabled for a customer."""
        preference = NotificationService.get_preference(
            customer_id, notification_type, channel
        )
        return preference.enabled if preference else True  # Default to enabled

    @staticmethod
    def log_notification(
        notification_id: str,
        status: str,
        error_message: str = None,
        external_response: Dict[str, Any] = None,
        external_id: str = None,
    ) -> NotificationLog:
        """Log notification delivery."""
        tenant_id = get_tenant_id()

        log = NotificationLog(
            tenant_id=tenant_id,
            notification_id=notification_id,
            status=status,
            error_message=error_message,
            external_response=external_response or {},
            external_id=external_id,
        )
        log.save()
        return log

    @staticmethod
    def get_notification_stats(
        start_date: datetime = None, end_date: datetime = None
    ) -> Dict[str, Any]:
        """Get notification statistics."""
        tenant_id = get_tenant_id()
        query = Notification.objects(tenant_id=tenant_id)

        if start_date:
            query = query(created_at__gte=start_date)
        if end_date:
            query = query(created_at__lte=end_date)

        total = query.count()
        sent = query(status="sent").count()
        delivered = query(status="delivered").count()
        failed = query(status="failed").count()
        pending = query(status="pending").count()

        return {
            "total": total,
            "sent": sent,
            "delivered": delivered,
            "failed": failed,
            "pending": pending,
            "delivery_rate": (delivered / total * 100) if total > 0 else 0,
            "failure_rate": (failed / total * 100) if total > 0 else 0,
        }

    @staticmethod
    async def send_sms_notification(
        notification_id: str, phone_number: str, message: str
    ) -> bool:
        """
        Send SMS notification via Termii.

        Args:
            notification_id: ID of the notification record
            phone_number: Recipient phone number (E.164 format)
            message: SMS message content

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            termii_service = TermiiService()
            result = await termii_service.send_sms(phone_number, message)

            if result:
                NotificationService.mark_notification_sent(notification_id)
                NotificationService.log_notification(
                    notification_id=notification_id,
                    status="sent",
                    external_id=result.get("message_id"),
                    external_response=result,
                )
                logger.info(f"SMS notification {notification_id} sent successfully")
                return True
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
                return False

        except Exception as e:
            logger.error(f"Error sending SMS notification {notification_id}: {str(e)}")
            NotificationService.mark_notification_failed(
                notification_id, f"Exception: {str(e)}"
            )
            NotificationService.log_notification(
                notification_id=notification_id,
                status="failed",
                error_message=str(e),
            )
            return False
