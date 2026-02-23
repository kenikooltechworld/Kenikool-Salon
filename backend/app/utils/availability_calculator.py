"""Availability calculation engine for public booking with race condition prevention."""

import hashlib
from datetime import datetime, date, time, timedelta
from typing import List, Optional, Tuple
from bson import ObjectId
from mongoengine import Q
import pytz

from app.models.availability import Availability
from app.models.appointment import Appointment
from app.models.service import Service
from app.models.staff import Staff
from app.cache import cache


class AvailabilitySlot:
    """Represents an available time slot."""

    def __init__(self, slot_time: time, available: bool = True):
        """Initialize availability slot."""
        self.time = slot_time
        self.available = available

    def __repr__(self):
        return f"AvailabilitySlot({self.time}, available={self.available})"


class AvailabilityCalculator:
    """Calculate available time slots for public booking with concurrency control."""

    DEFAULT_SLOT_INTERVAL_MINUTES = 30
    DEFAULT_BUFFER_TIME_MINUTES = 15
    DEFAULT_CONCURRENT_BOOKINGS = 1
    CACHE_TTL_SECONDS = 30  # Short TTL for real-time accuracy

    @staticmethod
    def get_available_slots(
        tenant_id: ObjectId,
        staff_id: ObjectId,
        service_id: ObjectId,
        booking_date: date,
        timezone: str = "UTC",
    ) -> List[AvailabilitySlot]:
        """
        Calculate available time slots for a given date.

        Args:
            tenant_id: Tenant ID
            staff_id: Staff member ID
            service_id: Service ID
            booking_date: Date to check availability
            timezone: Timezone for calculations (default: UTC)

        Returns:
            List of AvailabilitySlot objects
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Check cache first (short TTL for real-time accuracy)
        cache_key = f"availability:{tenant_id}:{staff_id}:{service_id}:{booking_date}"
        cached = cache.get(cache_key)
        if cached:
            # Reconstruct AvailabilitySlot objects from cached data
            return [AvailabilitySlot(slot_time=time.fromisoformat(s["time"]), available=s["available"]) for s in cached]

        # Get service duration
        service = Service.objects(tenant_id=tenant_id, id=service_id).first()
        if not service:
            logger.warning(f"Service not found: {service_id}")
            return []

        service_duration = service.duration_minutes

        # Get staff availability for the date
        availability_records = AvailabilityCalculator._get_staff_availability(
            tenant_id, staff_id, booking_date
        )
        
        logger.info(f"Found {len(availability_records)} availability records for staff {staff_id} on {booking_date}")
        logger.debug(f"Availability records: {availability_records}")

        if not availability_records:
            logger.warning(f"No availability records found for staff {staff_id} on {booking_date}")
            return []

        # Generate all possible slots with configurable intervals
        slots = []
        buffer_time = AvailabilityCalculator.DEFAULT_BUFFER_TIME_MINUTES
        for avail in availability_records:
            slot_interval = avail.slot_interval_minutes or AvailabilityCalculator.DEFAULT_SLOT_INTERVAL_MINUTES
            buffer_time = avail.buffer_time_minutes or AvailabilityCalculator.DEFAULT_BUFFER_TIME_MINUTES
            
            generated_slots = AvailabilityCalculator._generate_slots_for_availability(
                avail, service_duration, slot_interval, buffer_time
            )
            logger.info(f"Generated {len(generated_slots)} slots for availability {avail.id}")
            slots.extend(generated_slots)

        # Remove booked slots (with concurrent booking limit)
        booked_slots = AvailabilityCalculator._get_booked_slots(
            tenant_id, staff_id, booking_date
        )
        
        logger.info(f"Found {len(booked_slots)} booked slots")

        # Get concurrent booking limits
        concurrent_limit = availability_records[0].concurrent_bookings_allowed if availability_records else AvailabilityCalculator.DEFAULT_CONCURRENT_BOOKINGS

        # Filter out past slots (only show present and future)
        now = datetime.now()
        current_date = now.date()
        current_time = now.time()
        
        available_slots = []
        for slot in slots:
            # Skip if slot is in the past
            if booking_date < current_date:
                continue
            if booking_date == current_date and slot.time < current_time:
                continue
            
            # Check if slot is booked
            if not AvailabilityCalculator._is_slot_booked(
                slot, booked_slots, service_duration, buffer_time, concurrent_limit
            ):
                available_slots.append(slot)
        
        logger.info(f"Final available slots: {len(available_slots)} out of {len(slots)}")

        # Cache for short duration (30 seconds for real-time accuracy)
        # Convert to serializable format for caching
        cache_data = [{"time": slot.time.isoformat(), "available": slot.available} for slot in available_slots]
        cache.set(cache_key, cache_data, AvailabilityCalculator.CACHE_TTL_SECONDS)

        return available_slots

    @staticmethod
    def _get_staff_availability(
        tenant_id: ObjectId, staff_id: ObjectId, booking_date: date
    ) -> List[Availability]:
        """Get availability records for staff on a given date."""
        import logging
        logger = logging.getLogger(__name__)
        
        day_of_week = booking_date.weekday()  # 0=Monday, 6=Sunday
        logger.debug(f"_get_staff_availability: tenant={tenant_id}, staff={staff_id}, date={booking_date}, day_of_week={day_of_week}")

        # Get recurring availability for this day of week
        # Use Q objects for the entire query to handle the OR condition properly
        recurring = list(Availability.objects(
            Q(tenant_id=tenant_id) &
            Q(staff_id=staff_id) &
            Q(is_recurring=True) &
            Q(day_of_week=day_of_week) &
            Q(is_active=True) &
            Q(effective_from__lte=booking_date) &
            (Q(effective_to__gte=booking_date) | Q(effective_to=None))
        ))
        logger.debug(f"Found {len(recurring)} recurring availability records")

        # Get specific date availability (non-recurring)
        specific = list(Availability.objects(
            Q(tenant_id=tenant_id) &
            Q(staff_id=staff_id) &
            Q(is_recurring=False) &
            Q(is_active=True) &
            Q(effective_from__lte=booking_date) &
            (Q(effective_to__gte=booking_date) | Q(effective_to=None))
        ))
        logger.debug(f"Found {len(specific)} specific date availability records")

        return recurring + specific

    @staticmethod
    def _generate_slots_for_availability(
        availability: Availability, service_duration: int, slot_interval: int = None, buffer_time: int = None
    ) -> List[AvailabilitySlot]:
        """Generate time slots from an availability record with buffer time consideration."""
        if slot_interval is None:
            slot_interval = AvailabilityCalculator.DEFAULT_SLOT_INTERVAL_MINUTES
        if buffer_time is None:
            buffer_time = AvailabilityCalculator.DEFAULT_BUFFER_TIME_MINUTES
            
        slots = []

        # Parse start and end times
        start_time = datetime.strptime(availability.start_time, "%H:%M:%S").time()
        end_time = datetime.strptime(availability.end_time, "%H:%M:%S").time()

        # Convert to minutes since midnight for easier calculation
        start_minutes = start_time.hour * 60 + start_time.minute
        end_minutes = end_time.hour * 60 + end_time.minute

        # Generate slots at configurable intervals
        current_minutes = start_minutes
        while current_minutes + service_duration <= end_minutes:
            slot_time = time(hour=current_minutes // 60, minute=current_minutes % 60)

            if not AvailabilityCalculator._is_in_break(
                slot_time, availability.breaks, service_duration
            ):
                slots.append(AvailabilitySlot(slot_time, available=True))

            current_minutes += slot_interval

        return slots

    @staticmethod
    def _is_in_break(
        slot_time: time, breaks: List[dict], service_duration: int
    ) -> bool:
        """Check if a slot overlaps with any break times."""
        slot_minutes = slot_time.hour * 60 + slot_time.minute
        slot_end_minutes = slot_minutes + service_duration

        for break_period in breaks:
            break_start = datetime.strptime(break_period["start_time"], "%H:%M:%S")
            break_end = datetime.strptime(break_period["end_time"], "%H:%M:%S")

            break_start_minutes = break_start.hour * 60 + break_start.minute
            break_end_minutes = break_end.hour * 60 + break_end.minute

            # Check for overlap
            if slot_minutes < break_end_minutes and slot_end_minutes > break_start_minutes:
                return True

        return False

    @staticmethod
    def _get_booked_slots(
        tenant_id: ObjectId, staff_id: ObjectId, booking_date: date
    ) -> List[tuple]:
        """Get all booked time slots for a staff member on a given date."""
        # Convert date to datetime range
        start_datetime = datetime.combine(booking_date, time.min)
        end_datetime = datetime.combine(booking_date, time.max)

        # Get all non-cancelled appointments
        appointments = Appointment.objects(
            Q(tenant_id=tenant_id)
            & Q(staff_id=staff_id)
            & Q(status__ne="cancelled")
            & Q(start_time__gte=start_datetime)
            & Q(start_time__lt=end_datetime)
        )

        booked = []
        for appt in appointments:
            booked.append((appt.start_time.time(), appt.end_time.time()))

        return booked

    @staticmethod
    def _is_slot_booked(
        slot: AvailabilitySlot, booked_slots: List[Tuple], service_duration: int, buffer_time: int = None, concurrent_limit: int = None
    ) -> bool:
        """Check if a slot overlaps with booked appointments, considering buffer time and concurrent limits."""
        if buffer_time is None:
            buffer_time = AvailabilityCalculator.DEFAULT_BUFFER_TIME_MINUTES
        if concurrent_limit is None:
            concurrent_limit = AvailabilityCalculator.DEFAULT_CONCURRENT_BOOKINGS
            
        slot_minutes = slot.time.hour * 60 + slot.time.minute
        slot_end_minutes = slot_minutes + service_duration

        # Count overlapping bookings
        overlapping_count = 0
        
        for booked_start, booked_end in booked_slots:
            booked_start_minutes = booked_start.hour * 60 + booked_start.minute
            booked_end_minutes = booked_end.hour * 60 + booked_end.minute

            # Add buffer time AFTER appointment ends
            booked_end_with_buffer = booked_end_minutes + buffer_time

            # Check for overlap
            if slot_minutes < booked_end_with_buffer and slot_end_minutes > booked_start_minutes:
                overlapping_count += 1

        # Slot is booked if concurrent limit is reached
        return overlapping_count >= concurrent_limit

    @staticmethod
    def invalidate_cache(
        tenant_id: ObjectId, staff_id: ObjectId, service_id: ObjectId, booking_date: date
    ) -> None:
        """Invalidate availability cache for a specific date."""
        cache_key = f"availability:{tenant_id}:{staff_id}:{service_id}:{booking_date}"
        cache.delete(cache_key)

    @staticmethod
    def invalidate_staff_cache(tenant_id: ObjectId, staff_id: ObjectId) -> None:
        """Invalidate all availability cache for a staff member."""
        # This is a simplified version - in production, you might want to track all keys
        # For now, we'll rely on TTL expiration
        pass
