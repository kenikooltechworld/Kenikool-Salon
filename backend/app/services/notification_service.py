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
        customer_id: str = None,
        user_id: str = None,
        recipient_type: str = "customer",
        notification_type: str = None,
        channel: str = None,
        enabled: bool = True,
    ) -> NotificationPreference:
        """Set notification preference for a customer or staff member."""
        tenant_id = get_tenant_id()

        if not customer_id and not user_id:
            raise ValueError("Either customer_id or user_id must be provided")

        query_params = {
            "tenant_id": tenant_id,
            "notification_type": notification_type,
            "channel": channel,
        }
        
        if customer_id:
            query_params["customer_id"] = customer_id
        if user_id:
            query_params["user_id"] = user_id

        preference = NotificationPreference.objects(**query_params).first()

        if preference:
            preference.enabled = enabled
            preference.save()
        else:
            preference = NotificationPreference(
                tenant_id=tenant_id,
                customer_id=customer_id,
                user_id=user_id,
                recipient_type=recipient_type,
                notification_type=notification_type,
                channel=channel,
                enabled=enabled,
            )
            preference.save()

        return preference

    @staticmethod
    def get_preference(
        customer_id: str = None,
        user_id: str = None,
        notification_type: str = None,
        channel: str = None,
    ) -> Optional[NotificationPreference]:
        """Get notification preference for a customer or staff member."""
        tenant_id = get_tenant_id()
        
        query_params = {
            "tenant_id": tenant_id,
            "notification_type": notification_type,
            "channel": channel,
        }
        
        if customer_id:
            query_params["customer_id"] = customer_id
        if user_id:
            query_params["user_id"] = user_id
            
        return NotificationPreference.objects(**query_params).first()

    @staticmethod
    def get_preferences(customer_id: str = None, user_id: str = None) -> List[NotificationPreference]:
        """Get all notification preferences for a customer or staff member."""
        tenant_id = get_tenant_id()
        
        query_params = {"tenant_id": tenant_id}
        if customer_id:
            query_params["customer_id"] = customer_id
        if user_id:
            query_params["user_id"] = user_id
            
        return NotificationPreference.objects(**query_params)

    @staticmethod
    def is_notification_enabled(
        customer_id: str = None,
        user_id: str = None,
        notification_type: str = None,
        channel: str = None,
    ) -> bool:
        """Check if a notification is enabled for a customer or staff member."""
        preference = NotificationService.get_preference(
            customer_id=customer_id,
            user_id=user_id,
            notification_type=notification_type,
            channel=channel,
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
    def create_staff_appointment_reminder(
        staff_id: str,
        appointment_id: str,
        appointment_time: datetime,
        customer_name: str,
        service_name: str,
        staff_email: str = None,
        staff_phone: str = None,
        channels: List[str] = None,
    ) -> List[Notification]:
        """Create appointment reminder notifications for staff."""
        tenant_id = get_tenant_id()
        channels = channels or ["in_app", "email"]
        notifications = []

        content = f"Reminder: You have an appointment with {customer_name} for {service_name} at {appointment_time.strftime('%I:%M %p')}."
        subject = f"Appointment Reminder - {customer_name}"

        for channel in channels:
            notification = Notification(
                tenant_id=tenant_id,
                recipient_id=staff_id,
                recipient_type="staff",
                notification_type="appointment_reminder_24h",
                channel=channel,
                content=content,
                subject=subject,
                appointment_id=appointment_id,
                recipient_email=staff_email if channel == "email" else None,
                recipient_phone=staff_phone if channel == "sms" else None,
                status="pending",
            )
            notification.save()
            notifications.append(notification)

        return notifications

    @staticmethod
    def create_staff_shift_reminder(
        staff_id: str,
        shift_id: str,
        shift_start: datetime,
        shift_end: datetime,
        staff_email: str = None,
        staff_phone: str = None,
        channels: List[str] = None,
    ) -> List[Notification]:
        """Create shift reminder notifications for staff."""
        tenant_id = get_tenant_id()
        channels = channels or ["in_app", "email"]
        notifications = []

        content = f"Reminder: Your shift starts at {shift_start.strftime('%I:%M %p')} and ends at {shift_end.strftime('%I:%M %p')}."
        subject = "Shift Reminder"

        for channel in channels:
            notification = Notification(
                tenant_id=tenant_id,
                recipient_id=staff_id,
                recipient_type="staff",
                notification_type="shift_assigned",
                channel=channel,
                content=content,
                subject=subject,
                shift_id=shift_id,
                recipient_email=staff_email if channel == "email" else None,
                recipient_phone=staff_phone if channel == "sms" else None,
                status="pending",
            )
            notification.save()
            notifications.append(notification)

        return notifications

    @staticmethod
    def create_staff_time_off_notification(
        staff_id: str,
        time_off_request_id: str,
        status: str,
        start_date: datetime,
        end_date: datetime,
        denial_reason: str = None,
        staff_email: str = None,
        staff_phone: str = None,
        channels: List[str] = None,
    ) -> List[Notification]:
        """Create time off approval/denial notifications for staff."""
        tenant_id = get_tenant_id()
        channels = channels or ["in_app", "email"]
        notifications = []

        if status == "approved":
            content = f"Your time off request from {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')} has been approved."
            subject = "Time Off Request Approved"
            notification_type = "time_off_approved"
        else:
            content = f"Your time off request from {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')} has been denied."
            if denial_reason:
                content += f" Reason: {denial_reason}"
            subject = "Time Off Request Denied"
            notification_type = "time_off_rejected"

        for channel in channels:
            notification = Notification(
                tenant_id=tenant_id,
                recipient_id=staff_id,
                recipient_type="staff",
                notification_type=notification_type,
                channel=channel,
                content=content,
                subject=subject,
                time_off_request_id=time_off_request_id,
                recipient_email=staff_email if channel == "email" else None,
                recipient_phone=staff_phone if channel == "sms" else None,
                status="pending",
            )
            notification.save()
            notifications.append(notification)

        return notifications

    @staticmethod
    def create_staff_commission_notification(
        staff_id: str,
        commission_amount: float,
        payment_period: str,
        staff_email: str = None,
        staff_phone: str = None,
        channels: List[str] = None,
    ) -> List[Notification]:
        """Create commission payment notifications for staff."""
        tenant_id = get_tenant_id()
        channels = channels or ["in_app", "email"]
        notifications = []

        content = f"Your commission payment of ${commission_amount:.2f} for {payment_period} has been processed."
        subject = "Commission Payment Notification"

        for channel in channels:
            notification = Notification(
                tenant_id=tenant_id,
                recipient_id=staff_id,
                recipient_type="staff",
                notification_type="custom",
                channel=channel,
                content=content,
                subject=subject,
                recipient_email=staff_email if channel == "email" else None,
                recipient_phone=staff_phone if channel == "sms" else None,
                status="pending",
            )
            notification.save()
            notifications.append(notification)

        return notifications

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

    @staticmethod
    def create_owner_new_booking_notification(
        owner_id: str,
        customer_name: str,
        service_name: str,
        booking_date: datetime,
        appointment_id: str = None,
        owner_email: str = None,
        channels: List[str] = None,
    ) -> List[Notification]:
        """Create notification for owner when new booking is made."""
        from bson import ObjectId
        
        tenant_id = get_tenant_id()
        channels = channels or ["in_app"]
        notifications = []

        content = f"New booking from {customer_name} for {service_name} on {booking_date.strftime('%B %d, %Y at %I:%M %p')}"
        subject = "New Booking Received"

        for channel in channels:
            notification = Notification(
                tenant_id=tenant_id,
                recipient_id=ObjectId(owner_id) if isinstance(owner_id, str) else owner_id,
                recipient_type="owner",
                notification_type="new_appointment",
                channel=channel,
                content=content,
                subject=subject,
                appointment_id=ObjectId(appointment_id) if appointment_id and isinstance(appointment_id, str) else appointment_id,
                recipient_email=owner_email if channel == "email" else None,
                status="pending",
            )
            notification.save()
            notifications.append(notification)

        return notifications

    @staticmethod
    def create_owner_payment_received_notification(
        owner_id: str,
        customer_name: str,
        amount: float,
        payment_id: str = None,
        owner_email: str = None,
        channels: List[str] = None,
    ) -> List[Notification]:
        """Create notification for owner when payment is received."""
        from bson import ObjectId
        
        tenant_id = get_tenant_id()
        channels = channels or ["in_app"]
        notifications = []

        content = f"Payment of ${amount:.2f} received from {customer_name}"
        subject = "Payment Received"

        for channel in channels:
            notification = Notification(
                tenant_id=tenant_id,
                recipient_id=ObjectId(owner_id) if isinstance(owner_id, str) else owner_id,
                recipient_type="owner",
                notification_type="payment_received",
                channel=channel,
                content=content,
                subject=subject,
                payment_id=ObjectId(payment_id) if payment_id and isinstance(payment_id, str) else payment_id,
                recipient_email=owner_email if channel == "email" else None,
                status="pending",
            )
            notification.save()
            notifications.append(notification)

        return notifications

    @staticmethod
    def create_owner_payment_failed_notification(
        owner_id: str,
        customer_name: str,
        amount: float,
        reason: str = None,
        payment_id: str = None,
        owner_email: str = None,
        channels: List[str] = None,
    ) -> List[Notification]:
        """Create notification for owner when payment fails."""
        from bson import ObjectId
        
        tenant_id = get_tenant_id()
        channels = channels or ["in_app"]
        notifications = []

        content = f"Payment of ${amount:.2f} from {customer_name} failed"
        if reason:
            content += f". Reason: {reason}"
        subject = "Payment Failed"

        for channel in channels:
            notification = Notification(
                tenant_id=tenant_id,
                recipient_id=ObjectId(owner_id) if isinstance(owner_id, str) else owner_id,
                recipient_type="owner",
                notification_type="payment_failed",
                channel=channel,
                content=content,
                subject=subject,
                payment_id=ObjectId(payment_id) if payment_id and isinstance(payment_id, str) else payment_id,
                recipient_email=owner_email if channel == "email" else None,
                status="pending",
            )
            notification.save()
            notifications.append(notification)

        return notifications

    @staticmethod
    def create_owner_staff_alert_notification(
        owner_id: str,
        alert_type: str,
        staff_name: str,
        details: str = None,
        owner_email: str = None,
        channels: List[str] = None,
    ) -> List[Notification]:
        """Create notification for owner for staff-related alerts."""
        from bson import ObjectId
        
        tenant_id = get_tenant_id()
        channels = channels or ["in_app"]
        notifications = []

        content = f"Staff Alert: {staff_name} - {alert_type}"
        if details:
            content += f". {details}"
        subject = f"Staff Alert: {alert_type}"

        for channel in channels:
            notification = Notification(
                tenant_id=tenant_id,
                recipient_id=ObjectId(owner_id) if isinstance(owner_id, str) else owner_id,
                recipient_type="owner",
                notification_type="staff_alert",
                channel=channel,
                content=content,
                subject=subject,
                recipient_email=owner_email if channel == "email" else None,
                status="pending",
            )
            notification.save()
            notifications.append(notification)

        return notifications

    @staticmethod
    def create_owner_inventory_alert_notification(
        owner_id: str,
        alert_type: str,
        item_name: str,
        details: str = None,
        owner_email: str = None,
        channels: List[str] = None,
    ) -> List[Notification]:
        """Create notification for owner for inventory-related alerts."""
        from bson import ObjectId
        
        tenant_id = get_tenant_id()
        channels = channels or ["in_app"]
        notifications = []

        content = f"Inventory Alert: {item_name} - {alert_type}"
        if details:
            content += f". {details}"
        subject = f"Inventory Alert: {alert_type}"

        for channel in channels:
            notification = Notification(
                tenant_id=tenant_id,
                recipient_id=ObjectId(owner_id) if isinstance(owner_id, str) else owner_id,
                recipient_type="owner",
                notification_type="inventory_alert",
                channel=channel,
                content=content,
                subject=subject,
                recipient_email=owner_email if channel == "email" else None,
                status="pending",
            )
            notification.save()
            notifications.append(notification)

        return notifications
