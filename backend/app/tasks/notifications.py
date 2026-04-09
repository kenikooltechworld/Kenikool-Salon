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



@shared_task(bind=True, max_retries=3)
def send_booking_reminders(self):
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
        
        # Find bookings that need 24-hour reminders
        now = datetime.utcnow()
        tomorrow_start = now + timedelta(hours=23, minutes=30)
        tomorrow_end = now + timedelta(hours=24, minutes=30)
        
        # Get all bookings 24 hours away that haven't been reminded yet
        bookings_24h = PublicBooking.objects(
            status=PublicBookingStatus.CONFIRMED,
            reminder_24h_sent=False,
        )
        
        for booking in bookings_24h:
            try:
                # Parse booking time
                from datetime import datetime as dt
                booking_time_obj = dt.strptime(booking.booking_time, "%H:%M").time()
                booking_datetime = dt.combine(booking.booking_date, booking_time_obj)
                
                # Check if booking is 24 hours away
                time_until_booking = booking_datetime - now
                hours_until = time_until_booking.total_seconds() / 3600
                
                if 23.5 <= hours_until <= 24.5:
                    # Send 24-hour reminder
                    try:
                        send_booking_reminder_email.delay(
                            str(booking.id),
                            str(booking.tenant_id),
                            "24h"
                        )
                        
                        # Mark as sent
                        booking.reminder_24h_sent = True
                        booking.save()
                        
                        logger.info(f"24-hour reminder queued for booking {booking.id}")
                    except Exception as e:
                        logger.error(f"Error sending 24-hour reminder for booking {booking.id}: {str(e)}")
                        
            except Exception as e:
                logger.error(f"Error processing booking {booking.id} for 24-hour reminder: {str(e)}")
        
        # Find bookings that need 1-hour reminders
        one_hour_start = now + timedelta(minutes=50)
        one_hour_end = now + timedelta(minutes=70)
        
        bookings_1h = PublicBooking.objects(
            status=PublicBookingStatus.CONFIRMED,
            reminder_1h_sent=False,
        )
        
        for booking in bookings_1h:
            try:
                # Parse booking time
                from datetime import datetime as dt
                booking_time_obj = dt.strptime(booking.booking_time, "%H:%M").time()
                booking_datetime = dt.combine(booking.booking_date, booking_time_obj)
                
                # Check if booking is 1 hour away
                time_until_booking = booking_datetime - now
                minutes_until = time_until_booking.total_seconds() / 60
                
                if 50 <= minutes_until <= 70:
                    # Send 1-hour reminder
                    try:
                        send_booking_reminder_email.delay(
                            str(booking.id),
                            str(booking.tenant_id),
                            "1h"
                        )
                        
                        # Mark as sent
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
        raise self.retry(exc=e, countdown=300)


@shared_task(bind=True, max_retries=3)
def send_booking_reminder_email(self, booking_id: str, tenant_id: str, reminder_type: str):
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
        from app.tasks import send_email
        from app.services.termii_service import TermiiService
        
        tenant_id_obj = ObjectId(tenant_id)
        booking_id_obj = ObjectId(booking_id)
        
        # Get booking
        booking = PublicBooking.objects(
            tenant_id=tenant_id_obj,
            id=booking_id_obj
        ).first()
        
        if not booking:
            logger.error(f"Booking {booking_id} not found")
            return
        
        # Get tenant, service, and staff details
        tenant = Tenant.objects(id=tenant_id_obj).first()
        service = Service.objects(tenant_id=tenant_id_obj, id=booking.service_id).first()
        staff = Staff.objects(tenant_id=tenant_id_obj, id=booking.staff_id).first()
        
        if not tenant or not service or not staff:
            logger.error(f"Missing tenant, service, or staff for booking {booking_id}")
            return
        
        # Format booking details
        booking_date_str = booking.booking_date.strftime("%B %d, %Y")
        booking_time_str = booking.booking_time
        staff_name = f"{staff.user_id.first_name} {staff.user_id.last_name}".strip()
        
        # Send email reminder
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
            
            send_email.delay(
                to=booking.customer_email,
                subject=email_subject,
                template="booking_reminder",
                context=email_context,
            )
            
            logger.info(f"{reminder_type} reminder email queued for booking {booking_id}")
        except Exception as e:
            logger.error(f"Error sending {reminder_type} reminder email for booking {booking_id}: {str(e)}")
        
        # Send SMS reminder if customer opted in
        try:
            # Check notification preferences
            from app.models.notification import NotificationPreference
            
            sms_enabled = True  # Default to enabled
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
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def send_staff_appointment_reminders(self):
    """
    Send appointment reminders to staff 24 hours before appointments.
    """
    try:
        from datetime import datetime, timedelta
        from app.models.appointment import Appointment
        from app.models.staff import Staff
        from app.services.notification_service import NotificationService
        from app.context import set_tenant_id
        
        # Find appointments 24 hours away
        now = datetime.utcnow()
        tomorrow_start = now + timedelta(hours=23, minutes=30)
        tomorrow_end = now + timedelta(hours=24, minutes=30)
        
        # Get all confirmed appointments 24 hours away
        appointments = Appointment.objects(
            status__in=["scheduled", "confirmed"],
            start_time__gte=tomorrow_start,
            start_time__lte=tomorrow_end,
        )
        
        for appointment in appointments:
            try:
                set_tenant_id(str(appointment.tenant_id))
                
                # Get staff details
                staff = Staff.objects(
                    tenant_id=appointment.tenant_id,
                    id=appointment.staff_id
                ).first()
                
                if not staff or not staff.user_id:
                    continue
                
                # Check if staff wants appointment reminders
                from app.services.notification_service import NotificationService
                
                # Get staff email and phone
                staff_email = staff.user_id.email if hasattr(staff.user_id, 'email') else None
                staff_phone = staff.user_id.phone if hasattr(staff.user_id, 'phone') else None
                
                # Determine which channels to use based on preferences
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
                    # Get customer name
                    customer_name = "Customer"
                    if appointment.customer_id:
                        from app.models.customer import Customer
                        customer = Customer.objects(
                            tenant_id=appointment.tenant_id,
                            id=appointment.customer_id
                        ).first()
                        if customer:
                            customer_name = customer.name
                    
                    # Get service name
                    service_name = "Service"
                    if appointment.service_id:
                        from app.models.service import Service
                        service = Service.objects(
                            tenant_id=appointment.tenant_id,
                            id=appointment.service_id
                        ).first()
                        if service:
                            service_name = service.name
                    
                    # Create notifications
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
        raise self.retry(exc=e, countdown=300)


@shared_task(bind=True, max_retries=3)
def send_staff_shift_reminders(self):
    """
    Send shift reminders to staff at the start of their shifts.
    """
    try:
        from datetime import datetime, timedelta
        from app.models.shift import Shift
        from app.models.staff import Staff
        from app.services.notification_service import NotificationService
        from app.context import set_tenant_id
        
        # Find shifts starting in the next 30 minutes
        now = datetime.utcnow()
        start_window = now + timedelta(minutes=25)
        end_window = now + timedelta(minutes=35)
        
        # Get all scheduled shifts starting soon
        shifts = Shift.objects(
            status="scheduled",
            start_time__gte=start_window,
            start_time__lte=end_window,
        )
        
        for shift in shifts:
            try:
                set_tenant_id(str(shift.tenant_id))
                
                # Get staff details
                staff = Staff.objects(
                    tenant_id=shift.tenant_id,
                    id=shift.staff_id
                ).first()
                
                if not staff or not staff.user_id:
                    continue
                
                # Get staff email and phone
                staff_email = staff.user_id.email if hasattr(staff.user_id, 'email') else None
                staff_phone = staff.user_id.phone if hasattr(staff.user_id, 'phone') else None
                
                # Determine which channels to use based on preferences
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
                    # Create notifications
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
        raise self.retry(exc=e, countdown=300)
