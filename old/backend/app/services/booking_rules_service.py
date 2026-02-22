"""
Booking Rules Service
Handles validation and enforcement of service booking rules
"""
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class BookingRulesService:
    """Service for validating and enforcing booking rules"""

    def __init__(self, db):
        self.db = db

    def validate_booking_rules(
        self,
        service_id: str,
        booking_date: datetime,
        tenant_id: str,
        stylist_id: Optional[str] = None,
        allow_override: bool = False
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate booking against service rules
        
        Args:
            service_id: Service ID
            booking_date: Requested booking date/time
            tenant_id: Tenant ID
            stylist_id: Optional stylist ID
            allow_override: Whether to allow manager override
            
        Returns:
            Tuple of (is_valid, error_message)
            
        Requirements: 6.5, 6.6, 6.7
        """
        # Get service
        service = self.db.services.find_one({"_id": service_id, "tenant_id": tenant_id})
        if not service:
            return False, "Service not found"

        booking_rules = service.get("booking_rules")
        if not booking_rules:
            return True, None  # No rules to validate

        # Check if override is allowed
        if allow_override and booking_rules.get("allow_override", True):
            logger.info(f"Booking rules overridden for service {service_id}")
            return True, None

        # Check advance booking window
        days_in_advance = (booking_date - datetime.now()).days
        min_advance = booking_rules.get("advance_booking_min", 0)
        max_advance = booking_rules.get("advance_booking_max", 365)

        if days_in_advance < min_advance:
            return False, f"Booking must be at least {min_advance} days in advance"
        if days_in_advance > max_advance:
            return False, f"Booking cannot be more than {max_advance} days in advance"

        # Check max bookings per day
        max_per_day = booking_rules.get("max_bookings_per_day", 0)
        if max_per_day > 0:
            booking_date_str = booking_date.strftime("%Y-%m-%d")
            existing_count = self.db.bookings.count_documents({
                "service_id": service_id,
                "tenant_id": tenant_id,
                "booking_date": {"$regex": f"^{booking_date_str}"},
                "status": {"$in": ["confirmed", "pending"]}
            })
            if existing_count >= max_per_day:
                return False, f"Maximum {max_per_day} bookings per day reached"

        # Check buffer time
        buffer_before = booking_rules.get("buffer_time_before", 0)
        buffer_after = booking_rules.get("buffer_time_after", 0)
        
        if buffer_before > 0 or buffer_after > 0:
            has_conflict = self._check_buffer_conflicts(
                service_id, booking_date, buffer_before, buffer_after, tenant_id, stylist_id
            )
            if has_conflict:
                return False, f"Booking conflicts with buffer time requirements (before: {buffer_before}min, after: {buffer_after}min)"

        return True, None

    def _check_buffer_conflicts(
        self,
        service_id: str,
        booking_date: datetime,
        buffer_before: int,
        buffer_after: int,
        tenant_id: str,
        stylist_id: Optional[str] = None
    ) -> bool:
        """
        Check if booking conflicts with buffer time requirements
        
        Requirements: 6.1
        """
        # Calculate buffer window
        buffer_start = booking_date - timedelta(minutes=buffer_before)
        buffer_end = booking_date + timedelta(minutes=buffer_after)

        # Build query
        query = {
            "service_id": service_id,
            "tenant_id": tenant_id,
            "status": {"$in": ["confirmed", "pending"]},
        }

        # If stylist specified, only check their bookings
        if stylist_id:
            query["stylist_id"] = stylist_id

        # Find conflicting bookings
        existing_bookings = list(self.db.bookings.find(query))

        for booking in existing_bookings:
            booking_time_str = booking.get("booking_date")
            if not booking_time_str:
                continue

            try:
                if isinstance(booking_time_str, str):
                    existing_time = datetime.fromisoformat(booking_time_str.replace('Z', '+00:00'))
                else:
                    existing_time = booking_time_str

                # Check if existing booking falls within buffer window
                if buffer_start <= existing_time <= buffer_end:
                    return True
            except Exception as e:
                logger.error(f"Error parsing booking date: {e}")
                continue

        return False

    def check_cancellation_policy(
        self,
        service_id: str,
        booking_date: datetime,
        tenant_id: str
    ) -> Tuple[bool, float, str]:
        """
        Check cancellation policy for a booking
        
        Args:
            service_id: Service ID
            booking_date: Booking date/time
            tenant_id: Tenant ID
            
        Returns:
            Tuple of (can_cancel, penalty_percentage, message)
            
        Requirements: 6.4
        """
        service = self.db.services.find_one({"_id": service_id, "tenant_id": tenant_id})
        if not service:
            return False, 0.0, "Service not found"

        booking_rules = service.get("booking_rules")
        if not booking_rules:
            return True, 0.0, "No cancellation policy"

        cancellation_deadline = booking_rules.get("cancellation_deadline", 24)
        cancellation_penalty = booking_rules.get("cancellation_penalty", 0.0)

        # Calculate hours until booking
        hours_until = (booking_date - datetime.now()).total_seconds() / 3600

        if hours_until < cancellation_deadline:
            return True, cancellation_penalty, f"Cancellation within {cancellation_deadline} hours incurs {cancellation_penalty}% penalty"
        else:
            return True, 0.0, "Free cancellation"

    def check_service_availability(
        self,
        service_id: str,
        booking_date: datetime,
        tenant_id: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if service is available at the requested time
        
        Args:
            service_id: Service ID
            booking_date: Requested booking date/time
            tenant_id: Tenant ID
            
        Returns:
            Tuple of (is_available, error_message)
            
        Requirements: 7.1, 7.2, 7.3, 7.4, 7.5
        """
        service = self.db.services.find_one({"_id": service_id, "tenant_id": tenant_id})
        if not service:
            return False, "Service not found"

        availability = service.get("availability")
        if not availability:
            return True, None  # No availability restrictions

        # Check limited time offer
        if availability.get("is_limited_time"):
            limited_time_end = availability.get("limited_time_end")
            if limited_time_end:
                if isinstance(limited_time_end, str):
                    limited_time_end = datetime.fromisoformat(limited_time_end.replace('Z', '+00:00'))
                if datetime.now() > limited_time_end:
                    return False, "Limited time offer has expired"

        # Check day of week
        days_of_week = availability.get("days_of_week", [0, 1, 2, 3, 4, 5, 6])
        booking_day = booking_date.weekday()
        # Convert Python weekday (0=Monday) to our format (0=Sunday)
        booking_day = (booking_day + 1) % 7
        
        if booking_day not in days_of_week:
            day_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
            return False, f"Service not available on {day_names[booking_day]}"

        # Check time ranges
        time_ranges = availability.get("time_ranges", [])
        if time_ranges:
            booking_time = booking_date.strftime("%H:%M")
            is_in_range = False
            
            for time_range in time_ranges:
                start_time = time_range.get("start", "00:00")
                end_time = time_range.get("end", "23:59")
                
                if start_time <= booking_time <= end_time:
                    is_in_range = True
                    break
            
            if not is_in_range:
                return False, f"Service not available at {booking_time}"

        # Check seasonal ranges
        seasonal_ranges = availability.get("seasonal_ranges", [])
        if seasonal_ranges:
            booking_date_str = booking_date.strftime("%Y-%m-%d")
            is_in_season = False
            
            for season in seasonal_ranges:
                start_date = season.get("start")
                end_date = season.get("end")
                
                if start_date <= booking_date_str <= end_date:
                    is_in_season = True
                    break
            
            if not is_in_season:
                return False, "Service not available during this period"

        return True, None

    def check_capacity(
        self,
        service_id: str,
        booking_date: datetime,
        tenant_id: str
    ) -> Tuple[bool, int]:
        """
        Check if service has capacity for booking
        
        Args:
            service_id: Service ID
            booking_date: Requested booking date/time
            tenant_id: Tenant ID
            
        Returns:
            Tuple of (has_capacity, available_slots)
            
        Requirements: 15.1, 15.2, 15.3
        """
        service = self.db.services.find_one({"_id": service_id, "tenant_id": tenant_id})
        if not service:
            return False, 0

        max_concurrent = service.get("max_concurrent_bookings", 0)
        if max_concurrent == 0:  # Unlimited
            return True, -1

        # Count bookings at same time
        booking_time_str = booking_date.strftime("%Y-%m-%d %H:%M")
        concurrent_count = self.db.bookings.count_documents({
            "service_id": service_id,
            "tenant_id": tenant_id,
            "booking_date": {"$regex": f"^{booking_time_str}"},
            "status": {"$in": ["confirmed", "pending"]}
        })

        available_slots = max_concurrent - concurrent_count
        return available_slots > 0, available_slots


# Singleton instance
booking_rules_service = None


def get_booking_rules_service(db):
    """Get or create booking rules service instance"""
    global booking_rules_service
    if booking_rules_service is None:
        booking_rules_service = BookingRulesService(db)
    return booking_rules_service

