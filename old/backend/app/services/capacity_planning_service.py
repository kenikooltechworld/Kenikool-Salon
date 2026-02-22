from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.database import db


class CapacityPlanningService:
    """Service for staff capacity planning and utilization."""

    @staticmethod
    async def calculate_daily_capacity(
        salon_id: str,
        date: datetime,
        location_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Calculate total staff capacity for a day."""
        match_query = {
            "salon_id": ObjectId(salon_id),
            "date": date.date(),
        }
        if location_id:
            match_query["location_id"] = ObjectId(location_id)

        # Get all schedules for the day
        schedules = await db.schedules.find(match_query).to_list(None)

        total_capacity_hours = 0
        staff_count = 0
        available_slots = 0

        for schedule in schedules:
            if schedule.get("end_time") and schedule.get("start_time"):
                hours = (
                    schedule["end_time"] - schedule["start_time"]
                ).total_seconds() / 3600
                total_capacity_hours += hours
                staff_count += 1

                # Assume 30-min slots per staff member
                available_slots += int(hours * 2)

        return {
            "date": date.date(),
            "location_id": location_id,
            "total_capacity_hours": total_capacity_hours,
            "staff_count": staff_count,
            "available_slots": available_slots,
        }

    @staticmethod
    async def calculate_booked_capacity(
        salon_id: str,
        date: datetime,
        location_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Calculate booked capacity for a day."""
        match_query = {
            "salon_id": ObjectId(salon_id),
            "date": date.date(),
            "status": {"$in": ["confirmed", "completed"]},
        }
        if location_id:
            match_query["location_id"] = ObjectId(location_id)

        bookings = await db.bookings.find(match_query).to_list(None)

        total_booked_hours = 0
        booked_slots = 0

        for booking in bookings:
            if booking.get("end_time") and booking.get("start_time"):
                hours = (
                    booking["end_time"] - booking["start_time"]
                ).total_seconds() / 3600
                total_booked_hours += hours
                booked_slots += 1

        return {
            "date": date.date(),
            "location_id": location_id,
            "total_booked_hours": total_booked_hours,
            "booked_slots": booked_slots,
        }

    @staticmethod
    async def get_capacity_utilization(
        salon_id: str,
        date: datetime,
        location_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get capacity utilization for a day."""
        capacity = await CapacityPlanningService.calculate_daily_capacity(
            salon_id, date, location_id
        )
        booked = await CapacityPlanningService.calculate_booked_capacity(
            salon_id, date, location_id
        )

        total_capacity = capacity["total_capacity_hours"]
        booked_hours = booked["total_booked_hours"]
        utilization_rate = (
            (booked_hours / total_capacity * 100) if total_capacity > 0 else 0
        )

        return {
            "date": date.date(),
            "location_id": location_id,
            "total_capacity_hours": total_capacity,
            "booked_hours": booked_hours,
            "available_hours": total_capacity - booked_hours,
            "utilization_rate": utilization_rate,
            "staff_count": capacity["staff_count"],
            "booked_slots": booked["booked_slots"],
            "available_slots": capacity["available_slots"] - booked["booked_slots"],
        }

    @staticmethod
    async def get_low_staffing_days(
        salon_id: str,
        start_date: datetime,
        end_date: datetime,
        min_staff_threshold: int = 2,
        location_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get days with staffing below threshold."""
        low_staffing_days = []
        current_date = start_date

        while current_date <= end_date:
            capacity = await CapacityPlanningService.calculate_daily_capacity(
                salon_id, current_date, location_id
            )

            if capacity["staff_count"] < min_staff_threshold:
                low_staffing_days.append(
                    {
                        "date": current_date.date(),
                        "staff_count": capacity["staff_count"],
                        "required_staff": min_staff_threshold,
                        "shortage": min_staff_threshold - capacity["staff_count"],
                    }
                )

            current_date += timedelta(days=1)

        return low_staffing_days

    @staticmethod
    async def predict_busy_periods(
        salon_id: str,
        start_date: datetime,
        end_date: datetime,
        location_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Predict busy periods based on historical data."""
        busy_periods = []
        current_date = start_date

        while current_date <= end_date:
            utilization = await CapacityPlanningService.get_capacity_utilization(
                salon_id, current_date, location_id
            )

            # Consider >70% utilization as busy
            if utilization["utilization_rate"] > 70:
                busy_periods.append(
                    {
                        "date": current_date.date(),
                        "utilization_rate": utilization["utilization_rate"],
                        "booked_hours": utilization["booked_hours"],
                        "available_hours": utilization["available_hours"],
                    }
                )

            current_date += timedelta(days=1)

        return busy_periods

    @staticmethod
    async def suggest_additional_shifts(
        salon_id: str,
        start_date: datetime,
        end_date: datetime,
        location_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Suggest additional shifts for busy periods."""
        suggestions = []
        busy_periods = await CapacityPlanningService.predict_busy_periods(
            salon_id, start_date, end_date, location_id
        )

        for period in busy_periods:
            if period["utilization_rate"] > 85:
                # Suggest adding 1-2 shifts
                suggested_shifts = 1 if period["utilization_rate"] < 95 else 2
                suggestions.append(
                    {
                        "date": period["date"],
                        "suggested_shifts": suggested_shifts,
                        "reason": "High utilization rate",
                        "current_utilization": period["utilization_rate"],
                    }
                )

        return suggestions

    @staticmethod
    async def set_minimum_staffing(
        salon_id: str,
        location_id: str,
        min_staff: int,
    ) -> Dict[str, Any]:
        """Set minimum staffing requirement for a location."""
        result = await db.locations.update_one(
            {
                "_id": ObjectId(location_id),
                "salon_id": ObjectId(salon_id),
            },
            {
                "$set": {
                    "min_staff_requirement": min_staff,
                    "updated_at": datetime.utcnow(),
                }
            },
        )

        if result.matched_count == 0:
            raise ValueError("Location not found")

        return {"location_id": location_id, "min_staff": min_staff}

    @staticmethod
    async def get_minimum_staffing(
        salon_id: str,
        location_id: str,
    ) -> Optional[int]:
        """Get minimum staffing requirement for a location."""
        location = await db.locations.find_one(
            {
                "_id": ObjectId(location_id),
                "salon_id": ObjectId(salon_id),
            },
            {"min_staff_requirement": 1},
        )

        if not location:
            raise ValueError("Location not found")

        return location.get("min_staff_requirement", 2)

    @staticmethod
    async def block_availability(
        staff_id: str,
        salon_id: str,
        location_id: str,
        start_time: datetime,
        end_time: datetime,
        reason: str = "Blocked",
    ) -> Dict[str, Any]:
        """Block staff availability for a time slot."""
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
                    "blocked_availability": blocked_slot,
                }
            },
        )

        if result.matched_count == 0:
            raise ValueError("Staff member not found")

        return blocked_slot

    @staticmethod
    async def get_blocked_availability(
        staff_id: str,
        salon_id: str,
    ) -> List[Dict[str, Any]]:
        """Get all blocked availability slots for a staff member."""
        staff = await db.stylists.find_one(
            {
                "_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
            },
            {"blocked_availability": 1},
        )

        if not staff:
            raise ValueError("Staff member not found")

        return staff.get("blocked_availability", [])

    @staticmethod
    async def remove_blocked_availability(
        staff_id: str,
        salon_id: str,
        block_index: int,
    ) -> bool:
        """Remove a blocked availability slot."""
        staff = await db.stylists.find_one(
            {
                "_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
            }
        )

        if not staff:
            raise ValueError("Staff member not found")

        blocked = staff.get("blocked_availability", [])
        if block_index >= len(blocked):
            raise ValueError("Blocked slot not found")

        blocked.pop(block_index)

        await db.stylists.update_one(
            {
                "_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
            },
            {"$set": {"blocked_availability": blocked}},
        )

        return True
