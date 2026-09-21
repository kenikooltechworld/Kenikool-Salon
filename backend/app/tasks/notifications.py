"""Notification tasks for async processing."""

import logging
from app.background import run_in_background
from app.services.notification_service import NotificationService
from app.context import set_tenant_id

logger = logging.getLogger(__name__)


def process_pending_notifications():
    """Process pending notifications for delivery."""
    try:
        notifications = NotificationService.get_pending_notifications(limit=100)

        for notification in notifications:
            set_tenant_id(notification.tenant_id)

            try:
                if notification.channel == "email":
                    run_in_background(send_email_notification, str(notification.id))
                elif notification.channel == "sms":
                    run_in_background(send_sms_notification, str(notification.id))
                elif notification.channel == "push":
                    run_in_background(send_push_notification, str(notification.id))
                elif notification.channel == "in_app":
                    run_in_background(mark_in_app_notification_sent, str(notification.id))

                NotificationService.mark_notification_sent(str(notification.id))

            except Exception as e:
                logger.error(f"Error processing notification {notification.id}: {str(e)}")
                NotificationService.mark_notification_failed(str(notification.id), str(e))

    except Exception as e:
        logger.error(f"Error in process_pending_notifications: {str(e)}")


def retry_failed_notifications():
    """Retry failed notifications."""
    try:
        notifications = NotificationService.get_failed_notifications_for_retry(limit=50)

        for notification in notifications:
            set_tenant_id(notification.tenant_id)

            try:
                NotificationService.retry_notification(str(notification.id))

                if notification.channel == "email":
                    run_in_background(send_email_notification, str(notification.id))
                elif notification.channel == "sms":
                    run_in_background(send_sms_notification, str(notification.id))
                elif notification.channel == "push":
                    run_in_background(send_push_notification, str(notification.id))

            except Exception as e:
                logger.error(f"Error retrying notification {notification.id}: {str(e)}")

    except Exception as e:
        logger.error(f"Error in retry_failed_notifications: {str(e)}")


def send_email_notification(notification_id: str):
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

        from app.tasks import send_email
        send_email(
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


def send_sms_notification(notification_id: str):
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


def send_push_notification(notification_id: str):
    """Send push notification."""
    try:
        notification = NotificationService.get_notification(notification_id)
        if not notification:
            logger.error(f"Notification {notification_id} not found")
            return

        set_tenant_id(notification.tenant_id)

        NotificationService.mark_notification_delivered(notification_id)
        try:
            from app.services.termii_service import TermiiService
            recipient_phone = getattr(notification, "recipient_phone", None)
            if recipient_phone and notification.channel in ("push", "sms"):
                TermiiService().send_sms(
                    phone_number=recipient_phone,
                    message=notification.content or notification.subject or "You have a new notification",
                )
        except Exception as termii_err:
            logger.warning(f"Push notification delivery termii fallback failed: {termii_err}")

        logger.info(f"Push notification {notification_id} sent")

    except Exception as e:
        logger.error(f"Error sending push notification {notification_id}: {str(e)}")
        NotificationService.mark_notification_failed(notification_id, str(e))


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


def send_appointment_reminders():
    """Send pending appointment reminders."""
    try:
        from app.services.appointment_reminder_service import AppointmentReminderService

        stats = AppointmentReminderService.send_pending_reminders()
        logger.info(f"Appointment reminders sent: {stats}")

    except Exception as e:
        logger.error(f"Error in send_appointment_reminders: {str(e)}")


def send_booking_reminders():
    """
    Send booking reminders for public bookings.

    Sends:
    - 24-hour reminder emails/SMS for bookings 24 hours away
    - 1-hour reminder emails/SMS for bookings 1 hour away
    """
    try:
        from datetime import datetime, timedelta
        from app.models.public_booking import PublicBooking, PublicBookingStatus
        from app.services.public_booking_service import PublicBookingService

        now = datetime.utcnow()
        tomorrow_start = now + timedelta(hours=23, minutes=30)
        tomorrow_end = now + timedelta(hours=24, minutes=30)

        bookings_24h = PublicBooking.objects(
            status=PublicBookingStatus.CONFIRMED,
            reminder_24h_sent=False,
        )

        for booking in bookings_24h:
            try:
                from datetime import datetime as dt
                booking_time_obj = dt.strptime(booking.booking_time, "%H:%M").time()
                booking_datetime = dt.combine(booking.booking_date, booking_time_obj)

                time_until_booking = booking_datetime - now
                hours_until = time_until_booking.total_seconds() / 3600

                if 23.5 <= hours_until <= 24.5:
                    try:
                        run_in_background(
                            send_booking_reminder_email,
                            str(booking.id),
                            str(booking.tenant_id),
                            "24h"
                        )

                        booking.reminder_24h_sent = True
                        booking.save()

                        logger.info(f"24-hour reminder queued for booking {booking.id}")
                    except Exception as e:
                        logger.error(f"Error sending 24-hour reminder for booking {booking.id}: {str(e)}")

            except Exception as e:
                logger.error(f"Error processing booking {booking.id} for 24-hour reminder: {str(e)}")

        one_hour_start = now + timedelta(minutes=50)
        one_hour_end = now + timedelta(minutes=70)

        bookings_1h = PublicBooking.objects(
            status=PublicBookingStatus.CONFIRMED,
            reminder_1h_sent=False,
        )

        for booking in bookings_1h:
            try:
                from datetime import datetime as dt
                booking_time_obj = dt.strptime(booking.booking_time, "%H:%M").time()
                booking_datetime = dt.combine(booking.booking_date, booking_time_obj)

                time_until_booking = booking_datetime - now
                minutes_until = time_until_booking.total_seconds() / 60

                if 50 <= minutes_until <= 70:
                    try:
                        run_in_background(
                            send_booking_reminder_email,
                            str(booking.id),
                            str(booking.tenant_id),
                            "1h"
                        )

                        booking.reminder_1h_sent = True
                        booking.save()

                        logger.info(f"1-hour reminder queued for booking {booking.id}")
                    except Exception as e:
                        logger.error(f"Error sending 1-hour reminder for booking {booking.id}: {str(e)}")

            except Exception as e:
                logger.error(f"Error processing booking {booking.id} for 1-hour reminder: {str(e)}")

        logger.info("Booking reminders task completed")

    except Exception as e:
        logger.error(f"Error in send_booking_reminders: {str(e)}")


def send_booking_reminder_email(booking_id: str, tenant_id: str, reminder_type: str):
    """
    Send a booking reminder email/SMS.

    Args:
        booking_id: Public booking ID
        tenant_id: Tenant ID
        reminder_type: "24h" or "1h"
    """
    try:
        from bson import ObjectId
        from app.models.public_booking import PublicBooking
        from app.models.tenant import Tenant
        from app.models.service import Service
        from app.models.staff import Staff
        from app.models.user import User
        from app.tasks import send_email
        from app.services.termii_service import TermiiService

        tenant_id_obj = ObjectId(tenant_id)
        booking_id_obj = ObjectId(booking_id)

        booking = PublicBooking.objects(
            tenant_id=tenant_id_obj,
            id=booking_id_obj
        ).first()

        if not booking:
            logger.error(f"Booking {booking_id} not found")
            return

        tenant = Tenant.objects(id=tenant_id_obj).first()
        service = Service.objects(tenant_id=tenant_id_obj, id=booking.service_id).first()
        staff = Staff.objects(tenant_id=tenant_id_obj, id=booking.staff_id).first()

        if not tenant or not service or not staff:
            logger.error(f"Missing tenant, service, or staff for booking {booking_id}")
            return

        booking_date_str = booking.booking_date.strftime("%B %d, %Y")
        booking_time_str = booking.booking_time
        user = User.objects(id=staff.user_id).first()
        staff_name = f"{user.first_name} {user.last_name}".strip() if user else "Staff"

        try:
            email_subject = f"Reminder: Your appointment is {reminder_type} away"
            email_context = {
                "customer_name": booking.customer_name,
                "salon_name": tenant.name,
                "service_name": service.name,
                "staff_name": staff_name,
                "booking_date": booking_date_str,
                "booking_time": booking_time_str,
                "reminder_type": reminder_type,
                "booking_id": str(booking.id),
                "salon_address": tenant.address or "Address not provided",
                "salon_phone": tenant.phone or "Phone not provided",
                "cancellation_link": f"https://{tenant.subdomain}.kenikool.com/cancel/{booking.id}",
                "reschedule_link": f"https://{tenant.subdomain}.kenikool.com/reschedule/{booking.id}",
                "current_year": datetime.utcnow().year,
            }

            send_email(
                to=booking.customer_email,
                subject=email_subject,
                template="booking_reminder",
                context=email_context,
            )

            logger.info(f"{reminder_type} reminder email queued for booking {booking_id}")
        except Exception as e:
            logger.error(f"Error sending {reminder_type} reminder email for booking {booking_id}: {str(e)}")

        try:
            from app.models.notification import NotificationPreference

            sms_enabled = True
            prefs = NotificationPreference.objects(
                tenant_id=tenant_id_obj,
                customer_id=str(booking.customer_id),
                notification_type=f"appointment_reminder_{reminder_type}",
                channel="sms"
            ).first()

            if prefs:
                sms_enabled = prefs.enabled

            if sms_enabled and booking.customer_phone:
                sms_content = f"Reminder: Your appointment at {tenant.name} is {reminder_type} away on {booking_date_str} at {booking_time_str}. Reply STOP to cancel."

                termii_service = TermiiService()
                result = termii_service.send_sms_sync(
                    booking.customer_phone,
                    sms_content,
                )

                if result:
                    logger.info(f"{reminder_type} reminder SMS sent for booking {booking_id}")
                else:
                    logger.error(f"Failed to send {reminder_type} reminder SMS for booking {booking_id}")
        except Exception as e:
            logger.error(f"Error sending {reminder_type} reminder SMS for booking {booking_id}: {str(e)}")

    except Exception as e:
        logger.error(f"Error in send_booking_reminder_email: {str(e)}")


def send_staff_appointment_reminders():
    """
    Send appointment reminders to staff 24 hours before appointments.
    """
    try:
        from datetime import datetime, timedelta
        from app.models.appointment import Appointment
        from app.models.staff import Staff
        from app.services.notification_service import NotificationService
        from app.context import set_tenant_id

        now = datetime.utcnow()
        tomorrow_start = now + timedelta(hours=23, minutes=30)
        tomorrow_end = now + timedelta(hours=24, minutes=30)

        appointments = Appointment.objects(
            status__in=["scheduled", "confirmed"],
            start_time__gte=tomorrow_start,
            start_time__lte=tomorrow_end,
        )

        for appointment in appointments:
            try:
                set_tenant_id(str(appointment.tenant_id))

                staff = Staff.objects(
                    tenant_id=appointment.tenant_id,
                    id=appointment.staff_id
                ).first()

                if not staff or not staff.user_id:
                    continue

                from app.services.notification_service import NotificationService

                staff_email = getattr(staff.user_id, 'email', None)
                staff_phone = getattr(staff.user_id, 'phone', None)

                channels = []
                if NotificationService.is_notification_enabled(
                    user_id=str(staff.user_id.id),
                    notification_type="appointment_reminder_24h",
                    channel="in_app"
                ):
                    channels.append("in_app")
                if NotificationService.is_notification_enabled(
                    user_id=str(staff.user_id.id),
                    notification_type="appointment_reminder_24h",
                    channel="email"
                ) and staff_email:
                    channels.append("email")
                if NotificationService.is_notification_enabled(
                    user_id=str(staff.user_id.id),
                    notification_type="appointment_reminder_24h",
                    channel="sms"
                ) and staff_phone:
                    channels.append("sms")

                if channels:
                    customer_name = "Customer"
                    if appointment.customer_id:
                        from app.models.customer import Customer
                        customer = Customer.objects(
                            tenant_id=appointment.tenant_id,
                            id=appointment.customer_id
                        ).first()
                        if customer:
                            customer_name = customer.name

                    service_name = "Service"
                    if appointment.service_id:
                        from app.models.service import Service
                        service = Service.objects(
                            tenant_id=appointment.tenant_id,
                            id=appointment.service_id
                        ).first()
                        if service:
                            service_name = service.name

                    NotificationService.create_staff_appointment_reminder(
                        staff_id=str(staff.user_id.id),
                        appointment_id=str(appointment.id),
                        appointment_time=appointment.start_time,
                        customer_name=customer_name,
                        service_name=service_name,
                        staff_email=staff_email,
                        staff_phone=staff_phone,
                        channels=channels,
                    )

                    logger.info(f"Staff appointment reminder created for appointment {appointment.id}")

            except Exception as e:
                logger.error(f"Error processing appointment {appointment.id} for staff reminder: {str(e)}")

        logger.info("Staff appointment reminders task completed")

    except Exception as e:
        logger.error(f"Error in send_staff_appointment_reminders: {str(e)}")


def send_staff_shift_reminders():
    """
    Send shift reminders to staff at the start of their shifts.
    """
    try:
        from datetime import datetime, timedelta
        from app.models.shift import Shift
        from app.models.staff import Staff
        from app.services.notification_service import NotificationService
        from app.context import set_tenant_id

        now = datetime.utcnow()
        start_window = now + timedelta(minutes=25)
        end_window = now + timedelta(minutes=35)

        shifts = Shift.objects(
            status="scheduled",
            start_time__gte=start_window,
            start_time__lte=end_window,
        )

        for shift in shifts:
            try:
                set_tenant_id(str(shift.tenant_id))

                staff = Staff.objects(
                    tenant_id=shift.tenant_id,
                    id=shift.staff_id
                ).first()

                if not staff or not staff.user_id:
                    continue

                staff_email = getattr(staff.user_id, 'email', None)
                staff_phone = getattr(staff.user_id, 'phone', None)

                channels = []
                if NotificationService.is_notification_enabled(
                    user_id=str(staff.user_id.id),
                    notification_type="shift_assigned",
                    channel="in_app"
                ):
                    channels.append("in_app")
                if NotificationService.is_notification_enabled(
                    user_id=str(staff.user_id.id),
                    notification_type="shift_assigned",
                    channel="email"
                ) and staff_email:
                    channels.append("email")
                if NotificationService.is_notification_enabled(
                    user_id=str(staff.user_id.id),
                    notification_type="shift_assigned",
                    channel="sms"
                ) and staff_phone:
                    channels.append("sms")

                if channels:
                    NotificationService.create_staff_shift_reminder(
                        staff_id=str(staff.user_id.id),
                        shift_id=str(shift.id),
                        shift_start=shift.start_time,
                        shift_end=shift.end_time,
                        staff_email=staff_email,
                        staff_phone=staff_phone,
                        channels=channels,
                    )

                    logger.info(f"Staff shift reminder created for shift {shift.id}")

            except Exception as e:
                logger.error(f"Error processing shift {shift.id} for staff reminder: {str(e)}")

        logger.info("Staff shift reminders task completed")

    except Exception as e:
        logger.error(f"Error in send_staff_shift_reminders: {str(e)}")
