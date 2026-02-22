from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.database import db


class OnlineBookingService:
    """Service for managing staff availability for online booking."""

    @staticmethod
    async def set_online_booking_enabled(
        staff_id: str,
        salon_id: str,
        enabled: bool,
    ) -> Dict[str, Any]:
        """Enable/disable online booking for a staff member."""
        result = await db.stylists.update_one(
            {
                "_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
            },
            {
                "$set": {
                    "online_booking_enabled": enabled,
                    "updated_at": datetime.utcnow(),
                }
            },
        )

        if result.matched_count == 0:
            raise ValueError("Staff member not found")

        return {"staff_id": staff_id, "online_booking_enabled": enabled}

    @staticmethod
    async def set_max_bookings_per_day(
        staff_id: str,
        salon_id: str,
        max_bookings: int,
    ) -> Dict[str, Any]:
        """Set maximum bookings per day for a staff member."""
        result = await db.stylists.update_one(
            {
                "_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
            },
            {
                "$set": {
                    "max_bookings_per_day": max_bookings,
                    "updated_at": datetime.utcnow(),
                }
            },
        )

        if result.matched_count == 0:
            raise ValueError("Staff member not found")

        return {"staff_id": staff_id, "max_bookings_per_day": max_bookings}

    @staticmethod
    async def set_buffer_time(
        staff_id: str,
        salon_id: str,
        buffer_minutes: int,
    ) -> Dict[str, Any]:
        """Set buffer time between bookings."""
        result = await db.stylists.update_one(
            {
                "_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
            },
            {
                "$set": {
                    "buffer_time_minutes": buffer_minutes,
                    "updated_at": datetime.utcnow(),
                }
            },
        )

        if result.matched_count == 0:
            raise ValueError("Staff member not found")

        return {"staff_id": staff_id, "buffer_time_minutes": buffer_minutes}

    @staticmethod
    async def block_time_slot(
        staff_id: str,
        salon_id: str,
        start_time: datetime,
        end_time: datetime,
        reason: str = "Blocked",
    ) -> Dict[str, Any]:
        """Block a time slot from online booking."""
        blocked_slot = {
            "start_time": start_time,
            "end_time": end_time,
            "reason": reason,
            "created_at": datetime.utcnow(),
        }

        result = await db.stylists.update_one(
            {
                "_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
            },
            {
                "$push": {
                    "blocked_booking_slots": blocked_slot,
                }
            },
        )

        if result.matched_count == 0:
            raise ValueError("Staff member not found")

        return blocked_slot

    @staticmethod
    async def get_blocked_slots(
        staff_id: str,
        salon_id: str,
    ) -> List[Dict[str, Any]]:
        """Get all blocked time slots."""
        staff = await db.stylists.find_one(
            {
                "_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
            },
            {"blocked_booking_slots": 1},
        )

        if not staff:
            raise ValueError("Staff member not found")

        return staff.get("blocked_booking_slots", [])

    @staticmethod
    async def remove_blocked_slot(
        staff_id: str,
        salon_id: str,
        slot_index: int,
    ) -> bool:
        """Remove a blocked time slot."""
        staff = await db.stylists.find_one(
            {
                "_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
            }
        )

        if not staff:
            raise ValueError("Staff member not found")

        slots = staff.get("blocked_booking_slots", [])
        if slot_index >= len(slots):
            raise ValueError("Slot not found")

        slots.pop(slot_index)

        await db.stylists.update_one(
            {
                "_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
            },
            {"$set": {"blocked_booking_slots": slots}},
        )

        return True

    @staticmethod
    async def get_available_slots(
        staff_id: str,
        salon_id: str,
        date: datetime,
    ) -> List[Dict[str, Any]]:
        """Get available time slots for online booking."""
        staff = await db.stylists.find_one(
            {
                "_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
            },
            {
                "online_booking_enabled": 1,
                "max_bookings_per_day": 1,
                "buffer_time_minutes": 1,
                "blocked_booking_slots": 1,
            },
        )

        if not staff:
            raise ValueError("Staff member not found")

        if not staff.get("online_booking_enabled", False):
            return []

        # Get schedule for the day
        schedule = await db.schedules.find_one(
            {
                "staff_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
                "date": date.date(),
            }
        )

        if not schedule:
            return []

        # Get existing bookings
        bookings = await db.bookings.find(
            {
                "stylist_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
                "date": date.date(),
                "status": {"$in": ["confirmed", "completed"]},
            }
        ).to_list(None)

        # Get blocked slots
        blocked_slots = staff.get("blocked_booking_slots", [])

        # Calculate available slots
        available_slots = []
        buffer_minutes = staff.get("buffer_time_minutes", 0)
        max_bookings = staff.get("max_bookings_per_day", 999)

        if len(bookings) >= max_bookings:
            return []

        # Generate 30-minute slots
        current_time = schedule["start_time"]
        while current_time < schedule["end_time"]:
            slot_end = current_time + timedelta(minutes=30)

            # Check if slot is blocked
            is_blocked = False
            for blocked in blocked_slots:
                if (
                    current_time >= blocked["start_time"]
                    and slot_end <= blocked["end_time"]
                ):
                    is_blocked = True
                    break

            if is_blocked:
                current_time = slot_end
                continue

            # Check if slot conflicts with bookings
            has_conflict = False
            for booking in bookings:
                booking_start = booking["start_time"]
                booking_end = booking["end_time"]
                buffer_start = booking_start - timedelta(minutes=buffer_minutes)
                buffer_end = booking_end + timedelta(minutes=buffer_minutes)

                if (
                    current_time < buffer_end
                    and slot_end > buffer_start
                ):
                    has_conflict = True
                    break

            if not has_conflict:
                available_slots.append(
                    {
                        "start_time": current_time,
                        "end_time": slot_end,
                    }
                )

            current_time = slot_end

        return available_slots

    @staticmethod
    async def set_service_availability(
        staff_id: str,
        salon_id: str,
        service_id: str,
        available: bool,
    ) -> Dict[str, Any]:
        """Set availability for a specific service."""
        if available:
            await db.stylists.update_one(
                {
                    "_id": ObjectId(staff_id),
                    "salon_id": ObjectId(salon_id),
                },
                {
                    "$addToSet": {
                        "available_services": ObjectId(service_id),
                    }
                },
            )
        else:
            await db.stylists.update_one(
                {
                    "_id": ObjectId(staff_id),
                    "salon_id": ObjectId(salon_id),
                },
                {
                    "$pull": {
                        "available_services": ObjectId(service_id),
                    }
                },
            )

        return {"staff_id": staff_id, "service_id": service_id, "available": available}

    @staticmethod
    async def get_available_services(
        staff_id: str,
        salon_id: str,
    ) -> List[str]:
        """Get available services for online booking."""
        staff = await db.stylists.find_one(
            {
                "_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
            },
            {"available_services": 1},
        )

        if not staff:
            raise ValueError("Staff member not found")

        return [str(sid) for sid in staff.get("available_services", [])]

    @staticmethod
    async def get_booking_preferences(
        staff_id: str,
        salon_id: str,
    ) -> Dict[str, Any]:
        """Get all booking preferences for a staff member."""
        staff = await db.stylists.find_one(
            {
                "_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
            },
            {
                "online_booking_enabled": 1,
                "max_bookings_per_day": 1,
                "buffer_time_minutes": 1,
                "available_services": 1,
            },
        )

        if not staff:
            raise ValueError("Staff member not found")

        return {
            "staff_id": staff_id,
            "online_booking_enabled": staff.get("online_booking_enabled", False),
            "max_bookings_per_day": staff.get("max_bookings_per_day", 999),
            "buffer_time_minutes": staff.get("buffer_time_minutes", 0),
            "available_services": [str(sid) for sid in staff.get("available_services", [])],
        }
