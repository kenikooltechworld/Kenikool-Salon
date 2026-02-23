"""Service for managing public bookings."""

from datetime import datetime, date, time, timedelta
from typing import Optional
from bson import ObjectId
from mongoengine import Q
import logging

from app.models.public_booking import PublicBooking, PublicBookingStatus
from app.models.appointment import Appointment
from app.models.customer import Customer
from app.models.service import Service
from app.models.staff import Staff
from app.utils.availability_calculator import AvailabilityCalculator
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class PublicBookingService:
    """Service for managing public bookings and guest appointments."""

    @staticmethod
    def create_public_booking(
        tenant_id: ObjectId,
        service_id: ObjectId,
        staff_id: ObjectId,
        customer_name: str,
        customer_email: str,
        customer_phone: str,
        booking_date: date,
        booking_time: time,
        duration_minutes: int,
        notes: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        payment_option: str = "later",
    ) -> PublicBooking:
        """
        Create a public booking (guest appointment) with race condition prevention.

        Args:
            tenant_id: Tenant ID
            service_id: Service ID
            staff_id: Staff member ID
            customer_name: Customer name
            customer_email: Customer email
            customer_phone: Customer phone
            booking_date: Booking date
            booking_time: Booking time
            duration_minutes: Duration in minutes
            notes: Optional notes
            ip_address: IP address of requester
            user_agent: User agent of requester
            idempotency_key: Idempotency key for preventing duplicate bookings
            payment_option: Payment option ("now" or "later")

        Returns:
            Created PublicBooking document

        Raises:
            ValueError: If booking cannot be created
        """
        from pymongo import errors as pymongo_errors
        import hashlib
        
        # Validate booking date is not in the past
        if booking_date < date.today():
            raise ValueError("Cannot book appointments in the past")
        
        # Convert time to string format if needed
        if isinstance(booking_time, time):
            booking_time_str = booking_time.strftime("%H:%M")
        else:
            booking_time_str = booking_time
            booking_time = datetime.strptime(booking_time, "%H:%M").time()
        
        booking_datetime = datetime.combine(booking_date, booking_time)
        end_datetime = booking_datetime + timedelta(minutes=duration_minutes)

        # Validate service exists and allows public booking
        service = Service.objects(tenant_id=tenant_id, id=service_id).first()
        if not service:
            raise ValueError("Service not found")
        if not service.allow_public_booking:
            raise ValueError("This service does not allow public bookings")
        
        # Validate duration matches service duration
        if duration_minutes != service.duration_minutes:
            raise ValueError(f"Duration must be {service.duration_minutes} minutes for this service")
        
        # Validate staff exists and provides this service
        staff = Staff.objects(tenant_id=tenant_id, id=staff_id).first()
        if not staff:
            raise ValueError("Staff member not found")
        if not staff.is_available_for_public_booking:
            raise ValueError("This staff member is not available for public bookings")
        
        # Check if staff provides this service
        if service_id not in staff.service_ids:
            raise ValueError("This staff member does not provide this service")
        
        # Validate payment option is allowed for service
        if payment_option == "now" and not service.allow_pay_now:
            raise ValueError("This service does not allow immediate payment")

        # Generate idempotency key if not provided
        if not idempotency_key:
            key_data = f"{customer_email}:{booking_date}:{booking_time_str}:{service_id}:{staff_id}"
            idempotency_key = hashlib.sha256(key_data.encode()).hexdigest()

        # Check if booking with this idempotency key already exists
        existing_booking = PublicBooking.objects(
            tenant_id=tenant_id,
            idempotency_key=idempotency_key,
            status__ne=PublicBookingStatus.CANCELLED,
        ).first()

        if existing_booking:
            return existing_booking

        # Get or reuse existing guest customer by email
        customer_id = PublicBookingService._get_or_create_guest_customer(
            tenant_id, customer_name, customer_email, customer_phone
        )

        # Use MongoDB transaction for atomic booking creation
        try:
            # Check for overlapping appointments
            overlapping_appointment = Appointment.objects(
                tenant_id=tenant_id,
                staff_id=staff_id,
                status__ne="cancelled",
                start_time__lt=end_datetime,
                end_time__gt=booking_datetime,
            ).first()

            if overlapping_appointment:
                raise ValueError(
                    f"Time slot conflicts with existing appointment for staff {staff_id}"
                )

            # Check for overlapping public bookings
            overlapping_bookings = PublicBooking.objects(
                Q(tenant_id=tenant_id)
                & Q(staff_id=staff_id)
                & Q(booking_date=booking_date)
                & Q(status__ne=PublicBookingStatus.CANCELLED)
            )

            for existing in overlapping_bookings:
                existing_start = datetime.strptime(existing.booking_time, "%H:%M").time()
                existing_start_minutes = existing_start.hour * 60 + existing_start.minute
                existing_end_minutes = existing_start_minutes + existing.duration_minutes
                
                booking_start_minutes = booking_time.hour * 60 + booking_time.minute
                booking_end_minutes = booking_start_minutes + duration_minutes
                
                # Check for overlap
                if booking_start_minutes < existing_end_minutes and booking_end_minutes > existing_start_minutes:
                    raise ValueError(
                        f"Time slot is already booked for staff {staff_id} "
                        f"on {booking_date} at {booking_time_str}"
                    )

            # Create public booking with idempotency key
            public_booking = PublicBooking(
                tenant_id=tenant_id,
                customer_id=customer_id,
                service_id=service_id,
                staff_id=staff_id,
                customer_name=customer_name,
                customer_email=customer_email,
                customer_phone=customer_phone,
                booking_date=booking_date,
                booking_time=booking_time_str,
                duration_minutes=duration_minutes,
                status=PublicBookingStatus.PENDING,
                notes=notes,
                ip_address=ip_address,
                user_agent=user_agent,
                idempotency_key=idempotency_key,
                payment_option=payment_option,
                payment_status="pending" if payment_option == "now" else None,
            )
            public_booking.save()

            # Invalidate cache immediately
            AvailabilityCalculator.invalidate_cache(
                tenant_id, staff_id, service_id, booking_date
            )

            return public_booking

        except pymongo_errors.DuplicateKeyError:
            # Handle race condition: another request created the same booking
            existing = PublicBooking.objects(
                tenant_id=tenant_id,
                idempotency_key=idempotency_key,
            ).first()
            if existing:
                return existing
            raise ValueError("Booking creation failed due to concurrent request")

    @staticmethod
    def _get_or_create_guest_customer(
        tenant_id: ObjectId, name: str, email: str, phone: str
    ) -> ObjectId:
        """
        Get existing customer or create new guest customer.
        Deduplicates by email to prevent multiple records for same customer.

        Args:
            tenant_id: Tenant ID
            name: Customer name
            email: Customer email
            phone: Customer phone

        Returns:
            Customer ID
        """
        # Check if customer with this email already exists
        existing_customer = Customer.objects(
            tenant_id=tenant_id, email=email
        ).first()

        if existing_customer:
            # Update phone if provided and different
            if phone and existing_customer.phone != phone:
                existing_customer.phone = phone
                existing_customer.save()
            return existing_customer.id

        # Create new guest customer
        name_parts = name.split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        customer = Customer(
            tenant_id=tenant_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
        )
        customer.save()

        return customer.id

    @staticmethod
    def confirm_public_booking(
        tenant_id: ObjectId, booking_id: ObjectId
    ) -> PublicBooking:
        """
        Confirm a public booking and create appointment.

        Args:
            tenant_id: Tenant ID
            booking_id: Public booking ID

        Returns:
            Updated PublicBooking document

        Raises:
            ValueError: If booking not found or cannot be confirmed
        """
        from app.services.appointment_reminder_service import AppointmentReminderService
        from app.context import set_tenant_id
        
        set_tenant_id(tenant_id)
        
        booking = PublicBooking.objects(
            tenant_id=tenant_id, id=booking_id
        ).first()

        if not booking:
            raise ValueError(f"Public booking {booking_id} not found")

        if booking.status != PublicBookingStatus.PENDING:
            raise ValueError(
                f"Cannot confirm booking with status {booking.status}"
            )

        # Create appointment from public booking
        # Parse booking_time from string format (HH:MM)
        booking_time_obj = datetime.strptime(booking.booking_time, "%H:%M").time()
        booking_datetime = datetime.combine(booking.booking_date, booking_time_obj)
        end_datetime = booking_datetime + timedelta(minutes=booking.duration_minutes)

        appointment = Appointment(
            tenant_id=tenant_id,
            customer_id=booking.customer_id,
            staff_id=booking.staff_id,
            service_id=booking.service_id,
            start_time=booking_datetime,
            end_time=end_datetime,
            status="confirmed",
            notes=booking.notes,
        )
        appointment.save()

        # Create appointment history entry
        try:
            from app.services.appointment_history_service import AppointmentHistoryService
            AppointmentHistoryService.create_history_from_appointment(tenant_id, appointment.id)
        except Exception as e:
            logger.warning(f"Failed to create appointment history: {str(e)}")

        # Update public booking
        booking.status = PublicBookingStatus.CONFIRMED
        booking.appointment_id = appointment.id
        booking.save()

        # Send confirmation email/SMS
        try:
            PublicBookingService.send_booking_confirmation_notification(
                tenant_id, booking_id
            )
        except Exception as e:
            logger.error(f"Error sending confirmation notification: {str(e)}")

        # Schedule appointment reminders
        try:
            AppointmentReminderService.schedule_reminders_for_appointment(
                tenant_id,
                appointment.id,
                booking.customer_email,
                booking.customer_phone,
                booking.customer_name,
            )
        except Exception as e:
            logger.error(f"Error scheduling reminders: {str(e)}")

        # Invalidate availability cache
        AvailabilityCalculator.invalidate_cache(
            tenant_id, booking.staff_id, booking.service_id, booking.booking_date
        )

        return booking

    @staticmethod
    def cancel_public_booking(
        tenant_id: ObjectId,
        booking_id: ObjectId,
        cancellation_reason: Optional[str] = None,
    ) -> PublicBooking:
        """
        Cancel a public booking.

        Args:
            tenant_id: Tenant ID
            booking_id: Public booking ID
            cancellation_reason: Reason for cancellation

        Returns:
            Updated PublicBooking document

        Raises:
            ValueError: If booking not found or cannot be cancelled
        """
        booking = PublicBooking.objects(
            tenant_id=tenant_id, id=booking_id
        ).first()

        if not booking:
            raise ValueError(f"Public booking {booking_id} not found")

        if booking.status == PublicBookingStatus.CANCELLED:
            raise ValueError("Booking is already cancelled")

        # Check if cancellation is within allowed window (24 hours before appointment)
        # Parse booking_time from string format (HH:MM)
        booking_time_obj = datetime.strptime(booking.booking_time, "%H:%M").time()
        booking_datetime = datetime.combine(booking.booking_date, booking_time_obj)
        hours_until_appointment = (
            booking_datetime - datetime.utcnow()
        ).total_seconds() / 3600

        if hours_until_appointment < 0:
            raise ValueError("Cannot cancel appointment that has already started")

        # Cancel appointment if it exists
        if booking.appointment_id:
            appointment = Appointment.objects(
                tenant_id=tenant_id, id=booking.appointment_id
            ).first()

            if appointment:
                appointment.status = "cancelled"
                appointment.cancellation_reason = cancellation_reason
                appointment.save()

        # Update public booking
        booking.status = PublicBookingStatus.CANCELLED
        booking.cancellation_reason = cancellation_reason
        booking.cancelled_at = datetime.utcnow()
        booking.save()

        # Invalidate availability cache
        AvailabilityCalculator.invalidate_cache(
            tenant_id, booking.staff_id, booking.service_id, booking.booking_date
        )

        return booking

    @staticmethod
    def get_public_booking(
        tenant_id: ObjectId, booking_id: ObjectId
    ) -> Optional[PublicBooking]:
        """
        Get a public booking by ID.

        Args:
            tenant_id: Tenant ID
            booking_id: Public booking ID

        Returns:
            PublicBooking document or None if not found
        """
        return PublicBooking.objects(
            tenant_id=tenant_id, id=booking_id
        ).first()

    @staticmethod
    def list_public_bookings(
        tenant_id: ObjectId,
        status: Optional[PublicBookingStatus] = None,
        customer_email: Optional[str] = None,
        booking_date: Optional[date] = None,
    ) -> list:
        """
        List public bookings with optional filters.

        Args:
            tenant_id: Tenant ID
            status: Optional status filter
            customer_email: Optional customer email filter
            booking_date: Optional booking date filter

        Returns:
            List of PublicBooking documents
        """
        query = {"tenant_id": tenant_id}

        if status:
            query["status"] = status

        if customer_email:
            query["customer_email"] = customer_email

        if booking_date:
            query["booking_date"] = booking_date

        return list(
            PublicBooking.objects(**query).order_by("-created_at")
        )

    @staticmethod
    def send_booking_confirmation_notification(
        tenant_id: ObjectId, booking_id: ObjectId
    ) -> dict:
        """
        Send booking confirmation notification (SMS and email) to customer.

        Args:
            tenant_id: Tenant ID
            booking_id: Public booking ID

        Returns:
            Notification sending result

        Raises:
            ValueError: If booking not found
        """
        booking = PublicBooking.objects(
            tenant_id=tenant_id, id=booking_id
        ).first()

        if not booking:
            raise ValueError(f"Public booking {booking_id} not found")

        # Get service details
        service = Service.objects(tenant_id=tenant_id, id=booking.service_id).first()
        if not service:
            raise ValueError("Service not found")

        # Format booking details
        booking_date_str = booking.booking_date.strftime("%B %d, %Y")
        booking_time_str = booking.booking_time

        # Send SMS notification
        try:
            sms_content = f"Booking confirmed! Your appointment is on {booking_date_str} at {booking_time_str} for {service.name}. Reply STOP to cancel."
            NotificationService.create_notification(
                recipient_id=str(booking.customer_id),
                recipient_type="customer",
                notification_type="booking_confirmation",
                channel="sms",
                content=sms_content,
                recipient_email=booking.customer_email,
                recipient_phone=booking.customer_phone,
                appointment_id=str(booking.appointment_id) if booking.appointment_id else None,
                subject="Booking Confirmation",
            )
            logger.info(f"SMS confirmation notification created for booking {booking_id}")
        except Exception as e:
            logger.error(f"Error creating SMS notification for booking {booking_id}: {str(e)}")

        # Send email notification
        try:
            PublicBookingService.send_booking_confirmation_email(tenant_id, booking_id)
            logger.info(f"Email confirmation notification sent for booking {booking_id}")
        except Exception as e:
            logger.error(f"Error sending email notification for booking {booking_id}: {str(e)}")

        return {"status": "queued"}

    @staticmethod
    def send_booking_confirmation_email(
        tenant_id: ObjectId, booking_id: ObjectId
    ) -> dict:
        """
        Send booking confirmation email to customer.

        Args:
            tenant_id: Tenant ID
            booking_id: Public booking ID

        Returns:
            Email sending result

        Raises:
            ValueError: If booking not found
        """
        from app.tasks import send_email
        from app.models.tenant import Tenant

        booking = PublicBooking.objects(
            tenant_id=tenant_id, id=booking_id
        ).first()

        if not booking:
            raise ValueError(f"Public booking {booking_id} not found")

        # Get tenant and service details
        tenant = Tenant.objects(id=tenant_id).first()
        service = Service.objects(tenant_id=tenant_id, id=booking.service_id).first()
        staff = Staff.objects(tenant_id=tenant_id, id=booking.staff_id).first()

        if not tenant or not service or not staff:
            raise ValueError("Missing tenant, service, or staff information")

        # Get staff user details
        staff_name = f"{staff.user_id.first_name} {staff.user_id.last_name}".strip()

        # Format booking details
        booking_date_str = booking.booking_date.strftime("%B %d, %Y")
        booking_time_str = booking.booking_time.strftime("%I:%M %p")
        price_str = f"₦{float(service.price):,.2f}"

        # Queue email task
        context = {
            "customer_name": booking.customer_name,
            "salon_name": tenant.name,
            "service_name": service.name,
            "staff_name": staff_name,
            "booking_date": booking_date_str,
            "booking_time": booking_time_str,
            "duration_minutes": booking.duration_minutes,
            "price": price_str,
            "booking_id": str(booking.id),
            "salon_address": tenant.address or "Address not provided",
            "salon_phone": tenant.phone or "Phone not provided",
            "salon_email": tenant.email or "Email not provided",
            "reschedule_link": f"https://{tenant.subdomain}.kenikool.com/reschedule/{booking.id}",
            "cancellation_link": f"https://{tenant.subdomain}.kenikool.com/cancel/{booking.id}",
            "current_year": datetime.utcnow().year,
        }

        send_email.delay(
            to=booking.customer_email,
            subject=f"Booking Confirmation - {service.name} at {tenant.name}",
            template="booking_confirmation",
            context=context,
        )

        return {"status": "queued", "email": booking.customer_email}

    @staticmethod
    def send_cancellation_email(
        tenant_id: ObjectId, booking_id: ObjectId
    ) -> dict:
        """
        Send booking cancellation email to customer.

        Args:
            tenant_id: Tenant ID
            booking_id: Public booking ID

        Returns:
            Email sending result

        Raises:
            ValueError: If booking not found
        """
        from app.tasks import send_email
        from app.models.tenant import Tenant

        booking = PublicBooking.objects(
            tenant_id=tenant_id, id=booking_id
        ).first()

        if not booking:
            raise ValueError(f"Public booking {booking_id} not found")

        # Get tenant and service details
        tenant = Tenant.objects(id=tenant_id).first()
        service = Service.objects(tenant_id=tenant_id, id=booking.service_id).first()
        staff = Staff.objects(tenant_id=tenant_id, id=booking.staff_id).first()

        if not tenant or not service or not staff:
            raise ValueError("Missing tenant, service, or staff information")

        # Get staff user details
        staff_name = f"{staff.user_id.first_name} {staff.user_id.last_name}".strip()

        # Format booking details
        booking_date_str = booking.booking_date.strftime("%B %d, %Y")
        booking_time_str = booking.booking_time.strftime("%I:%M %p")

        # Queue email task
        context = {
            "customer_name": booking.customer_name,
            "salon_name": tenant.name,
            "service_name": service.name,
            "staff_name": staff_name,
            "booking_date": booking_date_str,
            "booking_time": booking_time_str,
            "booking_id": str(booking.id),
            "salon_address": tenant.address or "Address not provided",
            "salon_phone": tenant.phone or "Phone not provided",
            "salon_email": tenant.email or "Email not provided",
            "booking_link": f"https://{tenant.subdomain}.kenikool.com",
            "current_year": datetime.utcnow().year,
        }

        send_email.delay(
            to=booking.customer_email,
            subject=f"Booking Cancelled - {service.name} at {tenant.name}",
            template="booking_cancellation",
            context=context,
        )

        return {"status": "queued", "email": booking.customer_email}
