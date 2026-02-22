"""Service for managing appointment reminders."""

import logging
from datetime import datetime, timedelta
from typing import List, Optional
from bson import ObjectId

from app.models.appointment import Appointment
from app.models.notification import Notification
from app.services.notification_service import NotificationService
from app.context import set_tenant_id

logger = logging.getLogger(__name__)


class AppointmentReminderService:
    """Service for scheduling and sending appointment reminders."""

    @staticmethod
    def schedule_reminders_for_appointment(
        tenant_id: ObjectId,
        appointment_id: ObjectId,
        customer_email: str,
        customer_phone: str,
        customer_name: str,
    ) -> List[Notification]:
        """
        Schedule reminders for an appointment (24h and 1h before).

        Args:
            tenant_id: Tenant ID
            appointment_id: Appointment ID
            customer_email: Customer email
            customer_phone: Customer phone
            customer_name: Customer name

        Returns:
            List of created notification records
        """
        set_tenant_id(tenant_id)
        notifications = []

        try:
            appointment = Appointment.objects(
                tenant_id=tenant_id, id=appointment_id
            ).first()

            if not appointment:
                logger.error(f"Appointment {appointment_id} not found")
                return notifications

            # Schedule 24-hour reminder
            reminder_24h = NotificationService.create_notification(
                recipient_id=str(appointment.customer_id),
                recipient_type="customer",
                notification_type="appointment_reminder_24h",
                channel="sms",
                content=f"Reminder: Your appointment is scheduled for tomorrow at {appointment.start_time.strftime('%I:%M %p')}",
                recipient_email=customer_email,
                recipient_phone=customer_phone,
                appointment_id=str(appointment_id),
                subject="Appointment Reminder - 24 Hours",
            )
            notifications.append(reminder_24h)
            logger.info(f"Scheduled 24h reminder for appointment {appointment_id}")

            # Schedule 1-hour reminder
            reminder_1h = NotificationService.create_notification(
                recipient_id=str(appointment.customer_id),
                recipient_type="customer",
                notification_type="appointment_reminder_1h",
                channel="sms",
                content=f"Reminder: Your appointment is in 1 hour at {appointment.start_time.strftime('%I:%M %p')}",
                recipient_email=customer_email,
                recipient_phone=customer_phone,
                appointment_id=str(appointment_id),
                subject="Appointment Reminder - 1 Hour",
            )
            notifications.append(reminder_1h)
            logger.info(f"Scheduled 1h reminder for appointment {appointment_id}")

        except Exception as e:
            logger.error(f"Error scheduling reminders for appointment {appointment_id}: {str(e)}")

        return notifications

    @staticmethod
    def get_pending_reminders(limit: int = 100) -> List[Notification]:
        """
        Get pending reminders that should be sent.

        Args:
            limit: Maximum number of reminders to retrieve

        Returns:
            List of pending reminder notifications
        """
        return Notification.objects(
            notification_type__in=[
                "appointment_reminder_24h",
                "appointment_reminder_1h",
            ],
            status="pending",
        ).order_by("created_at")[:limit]

    @staticmethod
    def send_pending_reminders() -> dict:
        """
        Send all pending appointment reminders.

        Returns:
            Dictionary with send statistics
        """
        stats = {
            "total": 0,
            "sent": 0,
            "failed": 0,
        }

        try:
            reminders = AppointmentReminderService.get_pending_reminders()
            stats["total"] = len(reminders)

            for reminder in reminders:
                try:
                    set_tenant_id(reminder.tenant_id)

                    if reminder.channel == "sms" and reminder.recipient_phone:
                        # Send SMS reminder
                        from app.services.notification_service import NotificationService
                        success = AppointmentReminderService._send_sms_reminder(
                            str(reminder.id),
                            reminder.recipient_phone,
                            reminder.content,
                        )
                        if success:
                            stats["sent"] += 1
                        else:
                            stats["failed"] += 1
                    elif reminder.channel == "email" and reminder.recipient_email:
                        # Send email reminder
                        success = AppointmentReminderService._send_email_reminder(
                            str(reminder.id),
                            reminder.recipient_email,
                            reminder.subject,
                            reminder.content,
                        )
                        if success:
                            stats["sent"] += 1
                        else:
                            stats["failed"] += 1

                except Exception as e:
                    logger.error(f"Error sending reminder {reminder.id}: {str(e)}")
                    stats["failed"] += 1

        except Exception as e:
            logger.error(f"Error in send_pending_reminders: {str(e)}")

        return stats

    @staticmethod
    def _send_sms_reminder(
        notification_id: str, phone_number: str, message: str
    ) -> bool:
        """
        Send SMS reminder via Termii.

        Args:
            notification_id: Notification ID
            phone_number: Recipient phone number
            message: Message content

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            from app.services.termii_service import TermiiService

            termii_service = TermiiService()
            result = termii_service.send_sms_sync(phone_number, message)

            if result:
                NotificationService.mark_notification_sent(notification_id)
                NotificationService.log_notification(
                    notification_id=notification_id,
                    status="sent",
                    external_id=result.get("message_id"),
                    external_response=result,
                )
                logger.info(f"SMS reminder {notification_id} sent successfully")
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
                logger.error(f"SMS reminder {notification_id} failed to send")
                return False

        except Exception as e:
            logger.error(f"Error sending SMS reminder {notification_id}: {str(e)}")
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
    def _send_email_reminder(
        notification_id: str, email: str, subject: str, message: str
    ) -> bool:
        """
        Send email reminder.

        Args:
            notification_id: Notification ID
            email: Recipient email
            subject: Email subject
            message: Email message

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            from app.tasks import send_email

            send_email.delay(
                to=email,
                subject=subject,
                template="appointment_reminder",
                context={"message": message},
            )

            NotificationService.mark_notification_sent(notification_id)
            NotificationService.log_notification(
                notification_id=notification_id,
                status="sent",
            )
            logger.info(f"Email reminder {notification_id} queued successfully")
            return True

        except Exception as e:
            logger.error(f"Error sending email reminder {notification_id}: {str(e)}")
            NotificationService.mark_notification_failed(
                notification_id, f"Exception: {str(e)}"
            )
            NotificationService.log_notification(
                notification_id=notification_id,
                status="failed",
                error_message=str(e),
            )
            return False
