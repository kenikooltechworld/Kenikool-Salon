"""
Conflict Detection Service - Detects scheduling conflicts and validates availability
"""
from bson import ObjectId
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

from app.database import Database
from app.api.exceptions import BadRequestException

logger = logging.getLogger(__name__)


class ConflictDetectionService:
    """Service for detecting booking conflicts and checking availability"""
    
    @staticmethod
    async def check_conflicts(
        tenant_id: str,
        stylist_id: str,
        booking_date: datetime,
        duration_minutes: int,
        exclude_booking_id: Optional[str] = None
    ) -> Tuple[bool, List[Dict]]:
        """
        Check for scheduling conflicts
        
        Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6
        
        Args:
            tenant_id: Tenant ID
            stylist_id: Stylist ID to check
            booking_date: Start date/time of booking
            duration_minutes: Duration of service in minutes
            exclude_booking_id: Booking ID to exclude from conflict check (for rescheduling)
            
        Returns:
            Tuple of (has_conflicts: bool, conflicts: List[Dict])
        """
        db = Database.get_db()
        
        # Calculate end time
        end_time = booking_date + timedelta(minutes=duration_minutes)
        
        # Build query to find overlapping bookings
        query = {
            "tenant_id": ObjectId(tenant_id),
            "stylist_id": ObjectId(stylist_id),
            "status": {"$in": ["pending", "confirmed"]},  # Only check active bookings
            "$or": [
                # Booking starts during this time slot
                {
                    "booking_date": {
                        "$gte": booking_date,
                        "$lt": end_time
                    }
                },
                # Booking ends during this time slot
                {
                    "$expr": {
                        "$and": [
                            {"$lte": ["$booking_date", booking_date]},
                            {
                                "$gt": [
                                    {"$add": ["$booking_date", {"$multiply": ["$duration_minutes", 60000]}]},
                                    booking_date
                                ]
                            }
                        ]
                    }
                }
            ]
        }
        
        # Exclude current booking if rescheduling
        if exclude_booking_id:
            query["_id"] = {"$ne": ObjectId(exclude_booking_id)}
        
        # Find conflicting bookings
        conflicting_bookings = list(db.bookings.find(query))
        
        # Check stylist breaks
        break_conflicts = await ConflictDetectionService._check_stylist_breaks(
            tenant_id, stylist_id, booking_date, end_time
        )
        
        # Combine conflicts
        all_conflicts = []
        
        for booking in conflicting_bookings:
            all_conflicts.append({
                "type": "booking",
                "booking_id": str(booking["_id"]),
                "client_name": booking.get("client_name"),
                "service_name": booking.get("service_name"),
                "start_time": booking["booking_date"],
                "end_time": booking["booking_date"] + timedelta(minutes=booking.get("duration_minutes", 30))
            })
        
        all_conflicts.extend(break_conflicts)
        
        has_conflicts = len(all_conflicts) > 0
        
        return has_conflicts, all_conflicts
    
    @staticmethod
    async def _check_stylist_breaks(
        tenant_id: str,
        stylist_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[Dict]:
        """
        Check if booking conflicts with stylist breaks
        
        Requirements: 6.5
        
        Args:
            tenant_id: Tenant ID
            stylist_id: Stylist ID
            start_time: Booking start time
            end_time: Booking end time
            
        Returns:
            List of break conflicts
        """
        db = Database.get_db()
        
        # Get stylist schedule for the day
        stylist = db.stylists.find_one({
            "_id": ObjectId(stylist_id),
            "tenant_id": ObjectId(tenant_id)
        })
        
        if not stylist:
            return []
        
        # Check if stylist has breaks configured
        breaks = stylist.get("breaks", [])
        conflicts = []
        
        for break_info in breaks:
            # Parse break times
            break_start_str = break_info.get("start_time")  # e.g., "12:00"
            break_end_str = break_info.get("end_time")  # e.g., "13:00"
            
            if not break_start_str or not break_end_str:
                continue
            
            # Create datetime objects for break times on the booking date
            break_start = start_time.replace(
                hour=int(break_start_str.split(":")[0]),
                minute=int(break_start_str.split(":")[1]),
                second=0,
                microsecond=0
            )
            break_end = start_time.replace(
                hour=int(break_end_str.split(":")[0]),
                minute=int(break_end_str.split(":")[1]),
                second=0,
                microsecond=0
            )
            
            # Check for overlap
            if (start_time < break_end and end_time > break_start):
                conflicts.append({
                    "type": "break",
                    "stylist_name": stylist.get("name"),
                    "start_time": break_start,
                    "end_time": break_end
                })
        
        return conflicts
    
    @staticmethod
    async def get_stylist_availability(
        tenant_id: str,
        stylist_id: str,
        date: str,
        service_duration: int = 30,
        buffer_minutes: int = 0
    ) -> List[Dict]:
        """
        Get available time slots for a stylist on a specific date
        
        Requirements: 6.6
        
        Args:
            tenant_id: Tenant ID
            stylist_id: Stylist ID
            date: Date in YYYY-MM-DD format
            service_duration: Service duration in minutes
            buffer_minutes: Buffer time between bookings
            
        Returns:
            List of available time slots
        """
        db = Database.get_db()
        
        # Parse date
        try:
            target_date = datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            raise BadRequestException("Invalid date format. Use YYYY-MM-DD")
        
        # Get stylist working hours
        stylist = db.stylists.find_one({
            "_id": ObjectId(stylist_id),
            "tenant_id": ObjectId(tenant_id)
        })
        
        if not stylist:
            return []
        
        # Get working hours for the day (default 9 AM to 6 PM)
        working_hours = stylist.get("working_hours", {})
        day_name = target_date.strftime("%A").lower()
        day_schedule = working_hours.get(day_name, {"start": "09:00", "end": "18:00"})
        
        if not day_schedule.get("is_working", True):
            return []  # Stylist doesn't work on this day
        
        # Parse working hours
        start_hour, start_minute = map(int, day_schedule["start"].split(":"))
        end_hour, end_minute = map(int, day_schedule["end"].split(":"))
        
        work_start = target_date.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
        work_end = target_date.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
        
        # Get all bookings for the day
        day_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        bookings = list(db.bookings.find({
            "tenant_id": ObjectId(tenant_id),
            "stylist_id": ObjectId(stylist_id),
            "booking_date": {"$gte": day_start, "$lte": day_end},
            "status": {"$in": ["pending", "confirmed"]}
        }).sort("booking_date", 1))
        
        # Generate time slots
        available_slots = []
        current_time = work_start
        
        while current_time + timedelta(minutes=service_duration) <= work_end:
            slot_end = current_time + timedelta(minutes=service_duration)
            
            # Check if slot conflicts with any booking
            has_conflict = False
            for booking in bookings:
                booking_start = booking["booking_date"]
                booking_end = booking_start + timedelta(minutes=booking.get("duration_minutes", 30) + buffer_minutes)
                
                if (current_time < booking_end and slot_end > booking_start):
                    has_conflict = True
                    break
            
            # Check if slot conflicts with breaks
            break_conflicts = await ConflictDetectionService._check_stylist_breaks(
                tenant_id, stylist_id, current_time, slot_end
            )
            
            if not has_conflict and not break_conflicts:
                available_slots.append({
                    "start_time": current_time.strftime("%H:%M"),
                    "end_time": slot_end.strftime("%H:%M"),
                    "available": True
                })
            
            # Move to next slot (15-minute intervals)
            current_time += timedelta(minutes=15)
        
        return available_slots


# Singleton instance
conflict_detection_service = ConflictDetectionService()
