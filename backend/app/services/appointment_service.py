"""Service for managing appointments."""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from bson import ObjectId
from mongoengine import Q
from app.models.appointment import Appointment
from app.models.availability import Availability
from app.models.service import Service
from app.models.time_slot import TimeSlot
from app.models.customer import Customer
from app.models.payment import Payment
from app.tasks import queue_notification

logger = logging.getLogger(__name__)


class AppointmentService:
    """Service for appointment management and availability calculations."""

    @staticmethod
    def create_appointment(
        tenant_id: ObjectId,
        staff_id: ObjectId,
        service_id: ObjectId,
        start_time: datetime,
        end_time: datetime,
        customer_id: Optional[ObjectId] = None,
        location_id: Optional[ObjectId] = None,
        notes: Optional[str] = None,
        payment_option: Optional[str] = None,
        payment_id: Optional[ObjectId] = None,
        idempotency_key: Optional[str] = None,
        guest_name: Optional[str] = None,
        guest_email: Optional[str] = None,
        guest_phone: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Appointment:
        """
        Create a new appointment - handles both internal and public bookings.
        
        For internal bookings: customer_id must be provided
        For public bookings: guest_* fields must be provided
        
        Args:
            tenant_id: Tenant ID
            staff_id: Staff member ID
            service_id: Service ID
            start_time: Appointment start time (UTC)
            end_time: Appointment end time (UTC)
            customer_id: Optional customer ID (for internal bookings)
            location_id: Optional location ID
            notes: Optional appointment notes
            payment_option: Optional payment option ('now' or 'later')
            payment_id: Optional payment ID
            idempotency_key: Optional idempotency key (prevents duplicate bookings)
            guest_name: Optional guest name (for public bookings)
            guest_email: Optional guest email (for public bookings)
            guest_phone: Optional guest phone (for public bookings)
            ip_address: Optional IP address (for public bookings)
            user_agent: Optional user agent (for public bookings)
            
        Returns:
            Created Appointment document
            
        Raises:
            ValueError: If appointment overlaps or customer has outstanding balance
        """
        # Handle idempotency - check if this booking already exists
        if idempotency_key:
            existing = Appointment.objects(
                tenant_id=tenant_id,
                idempotency_key=idempotency_key
            ).first()
            if existing:
                return existing
        
        # Check for double-booking
        AppointmentService._check_double_booking(tenant_id, staff_id, start_time, end_time)
        
        # Determine if this is a guest booking
        is_guest = bool(guest_name)
        
        # For internal bookings, check customer balance
        if not is_guest and customer_id:
            AppointmentService._check_customer_balance(tenant_id, customer_id)
        
        # For guest bookings, get or create guest customer
        if is_guest and guest_email:
            customer_id = AppointmentService._get_or_create_guest_customer(
                tenant_id, guest_name, guest_email, guest_phone
            )
        
        # Get service to capture price
        service = Service.objects(tenant_id=tenant_id, id=service_id).first()
        price = service.price if service else None
        
        # Create appointment
        appointment = Appointment(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=staff_id,
            service_id=service_id,
            location_id=location_id,
            start_time=start_time,
            end_time=end_time,
            notes=notes,
            price=price,
            payment_id=payment_id,
            payment_option=payment_option,
            idempotency_key=idempotency_key,
            is_guest=is_guest,
            guest_name=guest_name,
            guest_email=guest_email,
            guest_phone=guest_phone,
            ip_address=ip_address,
            user_agent=user_agent,
            status="scheduled",
        )
        appointment.save()
        
        # Send confirmation notification
        try:
            customer = Customer.objects(tenant_id=tenant_id, id=customer_id).first()
            if customer:
                AppointmentService._send_appointment_confirmation(
                    tenant_id, appointment, customer, service, payment_option
                )
        except Exception as e:
            logger.error(f"Error sending appointment confirmation: {str(e)}")
        
        # Schedule appointment reminders
        try:
            from app.services.appointment_reminder_service import AppointmentReminderService
            customer = Customer.objects(tenant_id=tenant_id, id=customer_id).first()
            if customer:
                reminder_name = guest_name if is_guest else f"{customer.first_name} {customer.last_name}"
                reminder_email = guest_email if is_guest else customer.email
                reminder_phone = guest_phone if is_guest else customer.phone
                
                AppointmentReminderService.schedule_reminders_for_appointment(
                    tenant_id,
                    appointment.id,
                    reminder_email,
                    reminder_phone,
                    reminder_name,
                )
        except Exception as e:
            logger.error(f"Error scheduling reminders: {str(e)}")
        
        return appointment

    @staticmethod
    @staticmethod
    def _check_double_booking(
        tenant_id: ObjectId,
        staff_id: ObjectId,
        start_time: datetime,
        end_time: datetime,
    ) -> None:
        """
        Check if appointment overlaps with existing appointments.
        
        Args:
            tenant_id: Tenant ID
            staff_id: Staff member ID
            start_time: Appointment start time
            end_time: Appointment end time
            
        Raises:
            ValueError: If appointment overlaps with existing appointment
        """
        logger.info(f"[DoubleBookingCheck] Checking for overlaps:")
        logger.info(f"  staff_id={staff_id}")
        logger.info(f"  start_time={start_time} (type: {type(start_time).__name__})")
        logger.info(f"  end_time={end_time} (type: {type(end_time).__name__})")
        
        # Find overlapping appointments (excluding cancelled)
        overlapping = Appointment.objects(
            tenant_id=tenant_id,
            staff_id=staff_id,
            status__ne="cancelled",
            start_time__lt=end_time,
            end_time__gt=start_time,
        ).count()
        
        logger.info(f"[DoubleBookingCheck] Found {overlapping} overlapping appointments")
        
        if overlapping > 0:
            # Log existing appointments for this staff
            existing = Appointment.objects(
                tenant_id=tenant_id,
                staff_id=staff_id,
                status__ne="cancelled",
            )
            logger.warning(f"[DoubleBookingCheck] Existing non-cancelled appointments for staff {staff_id}:")
            for apt in existing:
                logger.warning(f"  - ID: {apt.id}, Start: {apt.start_time}, End: {apt.end_time}, Status: {apt.status}")
            
            raise ValueError(
                f"Staff member {staff_id} has overlapping appointment "
                f"between {start_time} and {end_time}"
            )

    @staticmethod
    def _check_customer_balance(
        tenant_id: ObjectId,
        customer_id: ObjectId,
    ) -> None:
        """
        Check if customer has outstanding balance.
        
        Args:
            tenant_id: Tenant ID
            customer_id: Customer ID
            
        Raises:
            ValueError: If customer has outstanding balance
        """
        from app.models.invoice import Invoice
        from app.models.staff import Staff
        from decimal import Decimal
        
        # Get customer
        customer = Customer.objects(
            tenant_id=tenant_id,
            id=customer_id
        ).first()
        
        # If customer doesn't exist, check if they're a staff member
        # (staff members can book for themselves without a customer record)
        if not customer:
            staff = Staff.objects(
                tenant_id=tenant_id,
                id=customer_id
            ).first()
            
            if not staff:
                raise ValueError(f"Customer {customer_id} not found")
            
            # Staff members can book without balance check
            logger.info(f"[BalanceCheck] Staff member {customer_id} booking for themselves - skipping balance check")
            return
        
        # Get unpaid invoices
        unpaid_invoices = Invoice.objects(
            tenant_id=tenant_id,
            customer_id=customer_id,
            status__in=["issued", "overdue"],
        )
        
        # Calculate outstanding balance
        outstanding_balance = Decimal("0")
        for invoice in unpaid_invoices:
            outstanding_balance += invoice.total
        
        if outstanding_balance > 0:
            raise ValueError(
                f"Customer has outstanding balance of {outstanding_balance}. "
                f"Please settle outstanding invoices before booking."
            )

    @staticmethod
    def _get_or_create_guest_customer(
        tenant_id: ObjectId,
        guest_name: str,
        guest_email: str,
        guest_phone: Optional[str] = None,
    ) -> ObjectId:
        """
        Get or create a guest customer for public bookings.
        
        Args:
            tenant_id: Tenant ID
            guest_name: Guest name
            guest_email: Guest email
            guest_phone: Optional guest phone
            
        Returns:
            Customer ID
        """
        # Check if customer with this email already exists
        existing_customer = Customer.objects(
            tenant_id=tenant_id,
            email=guest_email
        ).first()
        
        if existing_customer:
            return existing_customer.id
        
        # Create new guest customer
        # Parse name into first and last name
        name_parts = guest_name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        customer = Customer(
            tenant_id=tenant_id,
            first_name=first_name,
            last_name=last_name,
            email=guest_email,
            phone=guest_phone,
            is_guest=True,  # Mark as guest customer
        )
        customer.save()
        
        logger.info(f"[GuestBooking] Created guest customer {customer.id} for {guest_email}")
        return customer.id

    @staticmethod
    def get_available_slots(
        tenant_id: ObjectId,
        staff_id: ObjectId,
        service_id: ObjectId,
        date: datetime,
        slot_duration_minutes: int = 30,
    ) -> List[Tuple[datetime, datetime]]:
        """
        Calculate available time slots for a staff member on a given date.
        
        Args:
            tenant_id: Tenant ID
            staff_id: Staff member ID
            service_id: Service ID
            date: Date to get slots for (date only, time ignored)
            slot_duration_minutes: Duration of each slot in minutes (default 30)
            
        Returns:
            List of (start_time, end_time) tuples for available slots
        """
        # Get service duration
        service = Service.objects(tenant_id=tenant_id, id=service_id).first()
        if not service:
            return []
        
        service_duration = service.duration_minutes
        
        # Get staff availability for this day of week
        day_of_week = date.weekday()
        availabilities = Availability.objects(
            Q(tenant_id=tenant_id) &
            Q(staff_id=staff_id) &
            Q(is_active=True) &
            Q(is_recurring=True) &
            Q(day_of_week=day_of_week) &
            Q(effective_from__lte=date.date()) &
            (Q(effective_to__gte=date.date()) | Q(effective_to__exists=False))
        )
        
        if not availabilities:
            return []
        
        available_slots = []
        
        # Process each availability window
        for availability in availabilities:
            # Parse availability times
            start_hour, start_min, start_sec = map(int, availability.start_time.split(":"))
            end_hour, end_min, end_sec = map(int, availability.end_time.split(":"))
            
            # Create datetime objects for the availability window
            window_start = date.replace(hour=start_hour, minute=start_min, second=start_sec)
            window_end = date.replace(hour=end_hour, minute=end_min, second=end_sec)
            
            # Subtract breaks from availability window
            breaks = availability.breaks or []
            break_periods = []
            for break_item in breaks:
                break_start_hour, break_start_min, break_start_sec = map(
                    int, break_item.get("start_time", "00:00:00").split(":")
                )
                break_end_hour, break_end_min, break_end_sec = map(
                    int, break_item.get("end_time", "00:00:00").split(":")
                )
                break_start = date.replace(
                    hour=break_start_hour, minute=break_start_min, second=break_start_sec
                )
                break_end = date.replace(
                    hour=break_end_hour, minute=break_end_min, second=break_end_sec
                )
                break_periods.append((break_start, break_end))
            
            # Generate slots for this availability window
            current_time = window_start
            while current_time + timedelta(minutes=service_duration) <= window_end:
                slot_end = current_time + timedelta(minutes=service_duration)
                
                # Check if slot overlaps with any breaks
                slot_in_break = False
                for break_start, break_end in break_periods:
                    if current_time < break_end and slot_end > break_start:
                        slot_in_break = True
                        break
                
                if not slot_in_break:
                    # Check if slot is already booked
                    booked = Appointment.objects(
                        tenant_id=tenant_id,
                        staff_id=staff_id,
                        status__ne="cancelled",
                        start_time__lt=slot_end,
                        end_time__gt=current_time,
                    ).count()
                    
                    if booked == 0:
                        available_slots.append((current_time, slot_end))
                
                # Move to next slot
                current_time += timedelta(minutes=slot_duration_minutes)
        
        return available_slots

    @staticmethod
    def confirm_appointment(
        tenant_id: ObjectId,
        appointment_id: ObjectId,
        time_slot_id: Optional[ObjectId] = None,
    ) -> Appointment:
        """
        Confirm an appointment.
        
        Args:
            tenant_id: Tenant ID
            appointment_id: Appointment ID
            time_slot_id: Optional TimeSlot ID to confirm reservation
            
        Returns:
            Updated Appointment document
            
        Raises:
            ValueError: If appointment not found
        """
        appointment = Appointment.objects(
            tenant_id=tenant_id, id=appointment_id
        ).first()
        
        if not appointment:
            raise ValueError(f"Appointment {appointment_id} not found")
        
        appointment.status = "confirmed"
        appointment.confirmed_at = datetime.utcnow()
        appointment.save()
        
        # Confirm time slot reservation if provided
        if time_slot_id:
            from app.services.time_slot_service import TimeSlotService
            try:
                TimeSlotService.confirm_reservation(tenant_id, time_slot_id, appointment_id)
            except ValueError:
                pass  # Time slot may have already expired
        
        # Queue confirmation notification
        queue_notification(
            tenant_id=str(tenant_id),
            notification_type="appointment_confirmed",
            recipient_id=str(appointment.customer_id),
            data={
                "appointment_id": str(appointment_id),
                "start_time": appointment.start_time.isoformat(),
                "end_time": appointment.end_time.isoformat(),
                "staff_id": str(appointment.staff_id),
                "service_id": str(appointment.service_id),
            }
        )
        
        return appointment

    @staticmethod
    def cancel_appointment(
        tenant_id: ObjectId,
        appointment_id: ObjectId,
        reason: Optional[str] = None,
        cancelled_by: Optional[ObjectId] = None,
    ) -> Appointment:
        """
        Cancel an appointment.
        
        Args:
            tenant_id: Tenant ID
            appointment_id: Appointment ID
            reason: Optional cancellation reason
            cancelled_by: Optional user ID who cancelled
            
        Returns:
            Updated Appointment document
            
        Raises:
            ValueError: If appointment not found
        """
        appointment = Appointment.objects(
            tenant_id=tenant_id, id=appointment_id
        ).first()
        
        if not appointment:
            raise ValueError(f"Appointment {appointment_id} not found")
        
        appointment.status = "cancelled"
        appointment.cancellation_reason = reason
        appointment.cancelled_at = datetime.utcnow()
        appointment.cancelled_by = cancelled_by
        appointment.save()
        
        # Release any associated time slot reservations
        time_slots = TimeSlot.objects(
            Q(tenant_id=tenant_id) &
            Q(appointment_id=appointment_id) &
            Q(status__in=["reserved", "confirmed"])
        )
        
        for slot in time_slots:
            slot.status = "released"
            slot.save()
        
        # Process refund if payment exists
        if appointment.payment_id:
            try:
                from app.services.refund_service import RefundService
                from app.context import set_tenant_id
                
                # Set tenant context for refund service
                set_tenant_id(str(tenant_id))
                
                refund_service = RefundService()
                payment = Payment.objects(
                    tenant_id=tenant_id,
                    id=appointment.payment_id
                ).first()
                
                if payment and payment.status == "success":
                    logger.info(f"Processing refund for cancelled appointment {appointment_id}")
                    refund_service.create_refund(
                        payment_id=str(payment.id),
                        amount=payment.amount,
                        reason=f"Appointment cancelled: {reason or 'No reason provided'}"
                    )
                    logger.info(f"Refund created for payment {payment.id}")
            except Exception as e:
                logger.error(f"Error processing refund for cancelled appointment: {e}")
                # Don't raise - cancellation should succeed even if refund fails
        
        # Queue cancellation notification
        queue_notification(
            tenant_id=str(tenant_id),
            notification_type="appointment_cancelled",
            recipient_id=str(appointment.customer_id),
            data={
                "appointment_id": str(appointment_id),
                "start_time": appointment.start_time.isoformat(),
                "end_time": appointment.end_time.isoformat(),
                "cancellation_reason": reason,
            }
        )
        
        return appointment

    @staticmethod
    def mark_no_show(
        tenant_id: ObjectId,
        appointment_id: ObjectId,
        reason: Optional[str] = None,
    ) -> Appointment:
        """
        Mark an appointment as no-show.
        
        Args:
            tenant_id: Tenant ID
            appointment_id: Appointment ID
            reason: Optional no-show reason
            
        Returns:
            Updated Appointment document
            
        Raises:
            ValueError: If appointment not found
        """
        appointment = Appointment.objects(
            tenant_id=tenant_id, id=appointment_id
        ).first()
        
        if not appointment:
            raise ValueError(f"Appointment {appointment_id} not found")
        
        appointment.status = "no_show"
        appointment.no_show_reason = reason
        appointment.marked_no_show_at = datetime.utcnow()
        appointment.save()
        
        # Process refund if payment exists
        if appointment.payment_id:
            try:
                from app.services.refund_service import RefundService
                from app.context import set_tenant_id
                
                # Set tenant context for refund service
                set_tenant_id(str(tenant_id))
                
                refund_service = RefundService()
                payment = Payment.objects(
                    tenant_id=tenant_id,
                    id=appointment.payment_id
                ).first()
                
                if payment and payment.status == "success":
                    logger.info(f"Processing refund for no-show appointment {appointment_id}")
                    refund_service.create_refund(
                        payment_id=str(payment.id),
                        amount=payment.amount,
                        reason=f"Appointment marked as no-show: {reason or 'No reason provided'}"
                    )
                    logger.info(f"Refund created for payment {payment.id}")
            except Exception as e:
                logger.error(f"Error processing refund for no-show appointment: {e}")
                # Don't raise - marking no-show should succeed even if refund fails
        
        return appointment

    @staticmethod
    def get_appointment(tenant_id: ObjectId, appointment_id: ObjectId) -> Optional[Appointment]:
        """
        Get an appointment by ID.
        
        Args:
            tenant_id: Tenant ID
            appointment_id: Appointment ID
            
        Returns:
            Appointment document or None if not found
        """
        return Appointment.objects(tenant_id=tenant_id, id=appointment_id).first()

    @staticmethod
    def list_appointments(
        tenant_id: ObjectId,
        customer_id: Optional[ObjectId] = None,
        staff_id: Optional[ObjectId] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Appointment], int]:
        """
        List appointments with filtering.
        
        Args:
            tenant_id: Tenant ID
            customer_id: Optional customer ID filter
            staff_id: Optional staff ID filter
            status: Optional status filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            page: Page number (1-indexed)
            page_size: Number of results per page
            
        Returns:
            Tuple of (appointments list, total count)
        """
        query = Q(tenant_id=tenant_id)
        
        if customer_id:
            query &= Q(customer_id=customer_id)
        
        if staff_id:
            query &= Q(staff_id=staff_id)
        
        if status:
            query &= Q(status=status)
        
        if start_date:
            query &= Q(start_time__gte=start_date)
        
        if end_date:
            query &= Q(end_time__lte=end_date)
        
        total = Appointment.objects(query).count()
        
        skip = (page - 1) * page_size
        appointments = Appointment.objects(query).skip(skip).limit(page_size).order_by("-start_time")
        
        return list(appointments), total

    @staticmethod
    def get_day_view(
        tenant_id: ObjectId,
        date: datetime,
        staff_id: Optional[ObjectId] = None,
    ) -> List[Appointment]:
        """
        Get appointments for a specific day.
        
        Args:
            tenant_id: Tenant ID
            date: Date to get appointments for
            staff_id: Optional staff ID filter
            
        Returns:
            List of appointments for the day
        """
        # Get start and end of day
        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        query = Q(tenant_id=tenant_id) & Q(start_time__gte=day_start) & Q(start_time__lt=day_end)
        
        if staff_id:
            query &= Q(staff_id=staff_id)
        
        return list(Appointment.objects(query).order_by("start_time"))

    @staticmethod
    def get_week_view(
        tenant_id: ObjectId,
        date: datetime,
        staff_id: Optional[ObjectId] = None,
    ) -> List[Appointment]:
        """
        Get appointments for a specific week.
        
        Args:
            tenant_id: Tenant ID
            date: Any date in the week
            staff_id: Optional staff ID filter
            
        Returns:
            List of appointments for the week
        """
        # Get start of week (Monday)
        week_start = date - timedelta(days=date.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = week_start + timedelta(days=7)
        
        query = Q(tenant_id=tenant_id) & Q(start_time__gte=week_start) & Q(start_time__lt=week_end)
        
        if staff_id:
            query &= Q(staff_id=staff_id)
        
        return list(Appointment.objects(query).order_by("start_time"))

    @staticmethod
    def get_month_view(
        tenant_id: ObjectId,
        date: datetime,
        staff_id: Optional[ObjectId] = None,
    ) -> List[Appointment]:
        """
        Get appointments for a specific month.
        
        Args:
            tenant_id: Tenant ID
            date: Any date in the month
            staff_id: Optional staff ID filter
            
        Returns:
            List of appointments for the month
        """
        # Get start of month
        month_start = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Get start of next month
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1)
        
        query = Q(tenant_id=tenant_id) & Q(start_time__gte=month_start) & Q(start_time__lt=month_end)
        
        if staff_id:
            query &= Q(staff_id=staff_id)
        
        return list(Appointment.objects(query).order_by("start_time"))

    @staticmethod
    def get_calendar_availability(
        tenant_id: ObjectId,
        staff_id: Optional[ObjectId] = None,
        service_id: Optional[ObjectId] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        timezone: str = "UTC",
    ) -> dict:
        """
        Get calendar availability for a date range.
        
        Args:
            tenant_id: Tenant ID
            staff_id: Optional staff ID filter
            service_id: Optional service ID filter
            start_date: Start date for availability (default: today)
            end_date: End date for availability (default: 30 days from start)
            timezone: Customer's timezone for slot conversion
            
        Returns:
            Dictionary with available slots by date
        """
        if not start_date:
            start_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if not end_date:
            end_date = start_date + timedelta(days=30)
        
        availability_by_date = {}
        current_date = start_date
        
        while current_date < end_date:
            # Get available slots for this date
            if staff_id and service_id:
                slots = AppointmentService.get_available_slots(
                    tenant_id=tenant_id,
                    staff_id=staff_id,
                    service_id=service_id,
                    date=current_date,
                )
                
                if slots:
                    date_key = current_date.date().isoformat()
                    availability_by_date[date_key] = [
                        {
                            "start_time": start.isoformat(),
                            "end_time": end.isoformat(),
                        }
                        for start, end in slots
                    ]
            
            current_date += timedelta(days=1)
        
        return availability_by_date


    @staticmethod
    def _send_appointment_confirmation(
        tenant_id: ObjectId,
        appointment: Appointment,
        customer: Customer,
        service: Optional[Service],
        payment_option: Optional[str] = None,
    ) -> None:
        """
        Send appointment confirmation notification to customer.

        Args:
            tenant_id: Tenant ID
            appointment: Appointment document
            customer: Customer document
            service: Service document
            payment_option: Payment option ('now' or 'later')
        """
        from app.services.notification_service import NotificationService
        from app.context import set_tenant_id

        set_tenant_id(tenant_id)

        try:
            # Format appointment details
            appointment_date = appointment.start_time.strftime("%B %d, %Y")
            appointment_time = appointment.start_time.strftime("%I:%M %p")
            service_name = service.name if service else "Service"

            # Send SMS notification
            sms_content = f"Appointment confirmed! {service_name} on {appointment_date} at {appointment_time}. Reply STOP to cancel."
            NotificationService.create_notification(
                recipient_id=str(customer.id),
                recipient_type="customer",
                notification_type="appointment_confirmation",
                channel="sms",
                content=sms_content,
                recipient_email=customer.email,
                recipient_phone=customer.phone,
                appointment_id=str(appointment.id),
                subject="Appointment Confirmation",
            )
            logger.info(f"SMS confirmation sent for appointment {appointment.id}")

            # Send email notification
            NotificationService.create_notification(
                recipient_id=str(customer.id),
                recipient_type="customer",
                notification_type="appointment_confirmation",
                channel="email",
                content=f"Your appointment for {service_name} is confirmed on {appointment_date} at {appointment_time}.",
                recipient_email=customer.email,
                recipient_phone=customer.phone,
                appointment_id=str(appointment.id),
                subject=f"Appointment Confirmation - {service_name}",
            )
            logger.info(f"Email confirmation sent for appointment {appointment.id}")

        except Exception as e:
            logger.error(f"Error sending appointment confirmation: {str(e)}")
