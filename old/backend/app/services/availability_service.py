"""
Booking availability calculation service
"""
from datetime import datetime, timedelta, time as dt_time
from typing import List, Dict, Optional
from app.database import Database
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


def parse_time(time_str: str) -> dt_time:
    """Parse time string in HH:MM format"""
    hour, minute = map(int, time_str.split(':'))
    return dt_time(hour, minute)


def generate_time_slots(
    date: datetime,
    start_time: str,
    end_time: str,
    duration_minutes: int,
    break_start: Optional[str] = None,
    break_end: Optional[str] = None
) -> List[datetime]:
    """
    Generate available time slots for a given date and time range
    """
    slots = []
    
    start = parse_time(start_time)
    end = parse_time(end_time)
    
    # Create datetime objects for the given date
    current = datetime.combine(date.date(), start)
    end_datetime = datetime.combine(date.date(), end)
    
    # Parse break times if provided
    break_start_dt = None
    break_end_dt = None
    if break_start and break_end:
        break_start_dt = datetime.combine(date.date(), parse_time(break_start))
        break_end_dt = datetime.combine(date.date(), parse_time(break_end))
    
    while current + timedelta(minutes=duration_minutes) <= end_datetime:
        # Check if slot overlaps with break time
        slot_end = current + timedelta(minutes=duration_minutes)
        
        if break_start_dt and break_end_dt:
            # Skip if slot overlaps with break
            if not (slot_end <= break_start_dt or current >= break_end_dt):
                current += timedelta(minutes=15)  # Move to next 15-min interval
                continue
        
        slots.append(current)
        current += timedelta(minutes=15)  # 15-minute intervals
    
    return slots


async def get_stylist_schedule(stylist_id: str, date: datetime) -> Optional[Dict]:
    """
    Get stylist's working hours for a specific date
    """
    db = Database.get_db()
    stylist = await db.stylists.find_one({"_id": ObjectId(stylist_id)})
    
    if not stylist or not stylist.get("is_active"):
        return None
    
    schedule = stylist.get("schedule")
    if not schedule:
        return None
    
    # Get day of week
    day_name = date.strftime("%A").lower()
    
    # Find working hours for this day
    working_hours = schedule.get("working_hours", [])
    for hours in working_hours:
        if hours.get("day") == day_name and hours.get("is_working"):
            return {
                "start_time": hours.get("start_time"),
                "end_time": hours.get("end_time"),
                "break_start": schedule.get("break_start"),
                "break_end": schedule.get("break_end")
            }
    
    return None


async def get_existing_bookings(stylist_id: str, date: datetime, tenant_id: str) -> List[Dict]:
    """
    Get all existing bookings for a stylist on a specific date
    """
    db = Database.get_db()
    
    # Get start and end of day
    start_of_day = datetime.combine(date.date(), dt_time.min)
    end_of_day = datetime.combine(date.date(), dt_time.max)
    
    cursor = db.bookings.find({
        "tenant_id": tenant_id,
        "stylist_id": stylist_id,
        "booking_date": {
            "$gte": start_of_day,
            "$lte": end_of_day
        },
        "status": {"$in": ["pending", "confirmed"]}
    })
    
    bookings = []
    for booking in cursor:
        bookings.append({
            "start": booking["booking_date"],
            "duration": booking["duration_minutes"]
        })
    
    return bookings


def is_slot_available(slot: datetime, duration_minutes: int, existing_bookings: List[Dict]) -> bool:
    """
    Check if a time slot is available (no conflicts with existing bookings)
    """
    slot_end = slot + timedelta(minutes=duration_minutes)
    
    for booking in existing_bookings:
        booking_start = booking["start"]
        booking_end = booking_start + timedelta(minutes=booking["duration"])
        
        # Check for overlap
        if not (slot_end <= booking_start or slot >= booking_end):
            return False
    
    return True


async def get_available_slots(
    stylist_id: str,
    service_id: str,
    date: datetime,
    tenant_id: str
) -> List[datetime]:
    """
    Get all available time slots for a stylist and service on a specific date
    """
    db = Database.get_db()
    
    # Get service details
    service = await db.services.find_one({
        "_id": ObjectId(service_id),
        "tenant_id": tenant_id
    })
    
    if service is None:
        return []
    
    duration_minutes = service["duration_minutes"]
    
    # Get stylist schedule
    schedule = await get_stylist_schedule(stylist_id, date)
    if schedule is None:
        return []
    
    # Generate all possible slots
    all_slots = generate_time_slots(
        date,
        schedule["start_time"],
        schedule["end_time"],
        duration_minutes,
        schedule.get("break_start"),
        schedule.get("break_end")
    )
    
    # Get existing bookings
    existing_bookings = await get_existing_bookings(stylist_id, date, tenant_id)
    
    # Filter available slots
    available_slots = [
        slot for slot in all_slots
        if is_slot_available(slot, duration_minutes, existing_bookings)
        and slot > datetime.now()  # Only future slots
    ]
    
    return available_slots
