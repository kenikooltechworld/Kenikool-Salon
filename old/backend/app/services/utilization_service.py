from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.database import db


class UtilizationService:
    """Service for calculating staff utilization metrics."""

    @staticmethod
    async def calculate_staff_utilization(
        staff_id: str,
        salon_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Any]:
        """Calculate utilization rate for a staff member."""
        # Get all scheduled hours
        schedules = await db.schedules.find(
            {
                "staff_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
                "date": {"$gte": start_date.date(), "$lte": end_date.date()},
            }
        ).to_list(None)

        total_scheduled_hours = 0
        for schedule in schedules:
            if schedule.get("end_time") and schedule.get("start_time"):
                hours = (
                    schedule["end_time"] - schedule["start_time"]
                ).total_seconds() / 3600
                total_scheduled_hours += hours

        # Get all booked hours
        bookings = await db.bookings.find(
            {
                "stylist_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
                "date": {"$gte": start_date.date(), "$lte": end_date.date()},
                "status": {"$in": ["confirmed", "completed"]},
            }
        ).to_list(None)

        total_booked_hours = 0
        for booking in bookings:
            if booking.get("end_time") and booking.get("start_time"):
                hours = (
                    booking["end_time"] - booking["start_time"]
                ).total_seconds() / 3600
                total_booked_hours += hours

        utilization_rate = (
            (total_booked_hours / total_scheduled_hours * 100)
            if total_scheduled_hours > 0
            else 0
        )

        return {
            "staff_id": staff_id,
            "period": {"start": start_date.date(), "end": end_date.date()},
            "total_scheduled_hours": total_scheduled_hours,
            "total_booked_hours": total_booked_hours,
            "idle_hours": total_scheduled_hours - total_booked_hours,
            "utilization_rate": utilization_rate,
            "booking_count": len(bookings),
        }

    @staticmethod
    async def identify_underutilized_staff(
        salon_id: str,
        start_date: datetime,
        end_date: datetime,
        threshold: float = 50.0,
        location_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Identify staff with utilization below threshold."""
        match_query = {"salon_id": ObjectId(salon_id)}
        if location_id:
            match_query["locations"] = ObjectId(location_id)

        staff_list = await db.stylists.find(match_query, {"_id": 1, "name": 1}).to_list(None)

        underutilized = []

        for staff in staff_list:
            util = await UtilizationService.calculate_staff_utilization(
                str(staff["_id"]), salon_id, start_date, end_date
            )

            if util["utilization_rate"] < threshold:
                underutilized.append(
                    {
                        "staff_id": str(staff["_id"]),
                        "staff_name": staff.get("name"),
                        "utilization_rate": util["utilization_rate"],
                        "scheduled_hours": util["total_scheduled_hours"],
                        "booked_hours": util["total_booked_hours"],
                        "idle_hours": util["idle_hours"],
                    }
                )

        return sorted(underutilized, key=lambda x: x["utilization_rate"])

    @staticmethod
    async def identify_overutilized_staff(
        salon_id: str,
        start_date: datetime,
        end_date: datetime,
        threshold: float = 90.0,
        location_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Identify staff with utilization above threshold."""
        match_query = {"salon_id": ObjectId(salon_id)}
        if location_id:
            match_query["locations"] = ObjectId(location_id)

        staff_list = await db.stylists.find(match_query, {"_id": 1, "name": 1}).to_list(None)

        overutilized = []

        for staff in staff_list:
            util = await UtilizationService.calculate_staff_utilization(
                str(staff["_id"]), salon_id, start_date, end_date
            )

            if util["utilization_rate"] > threshold:
                overutilized.append(
                    {
                        "staff_id": str(staff["_id"]),
                        "staff_name": staff.get("name"),
                        "utilization_rate": util["utilization_rate"],
                        "scheduled_hours": util["total_scheduled_hours"],
                        "booked_hours": util["total_booked_hours"],
                    }
                )

        return sorted(overutilized, key=lambda x: x["utilization_rate"], reverse=True)

    @staticmethod
    async def get_salon_average_utilization(
        salon_id: str,
        start_date: datetime,
        end_date: datetime,
        location_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get average utilization across all staff."""
        match_query = {"salon_id": ObjectId(salon_id)}
        if location_id:
            match_query["locations"] = ObjectId(location_id)

        staff_list = await db.stylists.find(match_query, {"_id": 1}).to_list(None)

        total_utilization = 0
        staff_count = 0

        for staff in staff_list:
            util = await UtilizationService.calculate_staff_utilization(
                str(staff["_id"]), salon_id, start_date, end_date
            )
            total_utilization += util["utilization_rate"]
            staff_count += 1

        average_utilization = (
            total_utilization / staff_count if staff_count > 0 else 0
        )

        return {
            "average_utilization": average_utilization,
            "staff_count": staff_count,
            "period": {"start": start_date.date(), "end": end_date.date()},
        }

    @staticmethod
    async def compare_location_utilization(
        salon_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Dict[str, Any]]:
        """Compare utilization across locations."""
        locations = await db.locations.find(
            {"salon_id": ObjectId(salon_id)}, {"_id": 1, "name": 1}
        ).to_list(None)

        location_utilization = []

        for location in locations:
            avg_util = await UtilizationService.get_salon_average_utilization(
                salon_id, start_date, end_date, str(location["_id"])
            )

            location_utilization.append(
                {
                    "location_id": str(location["_id"]),
                    "location_name": location.get("name"),
                    "average_utilization": avg_util["average_utilization"],
                    "staff_count": avg_util["staff_count"],
                }
            )

        return sorted(
            location_utilization,
            key=lambda x: x["average_utilization"],
            reverse=True,
        )

    @staticmethod
    async def get_utilization_trends(
        staff_id: str,
        salon_id: str,
        start_date: datetime,
        end_date: datetime,
        interval_days: int = 7,
    ) -> List[Dict[str, Any]]:
        """Get utilization trends over time."""
        trends = []
        current_date = start_date

        while current_date <= end_date:
            period_end = min(
                current_date + timedelta(days=interval_days - 1), end_date
            )

            util = await UtilizationService.calculate_staff_utilization(
                staff_id, salon_id, current_date, period_end
            )

            trends.append(
                {
                    "period_start": current_date.date(),
                    "period_end": period_end.date(),
                    "utilization_rate": util["utilization_rate"],
                    "booked_hours": util["total_booked_hours"],
                    "scheduled_hours": util["total_scheduled_hours"],
                }
            )

            current_date += timedelta(days=interval_days)

        return trends

    @staticmethod
    async def set_utilization_target(
        salon_id: str,
        target_utilization: float,
    ) -> Dict[str, Any]:
        """Set target utilization for the salon."""
        result = await db.salons.update_one(
            {"_id": ObjectId(salon_id)},
            {
                "$set": {
                    "target_utilization": target_utilization,
                    "updated_at": datetime.utcnow(),
                }
            },
        )

        if result.matched_count == 0:
            raise ValueError("Salon not found")

        return {"salon_id": salon_id, "target_utilization": target_utilization}

    @staticmethod
    async def get_utilization_target(salon_id: str) -> Optional[float]:
        """Get target utilization for the salon."""
        salon = await db.salons.find_one(
            {"_id": ObjectId(salon_id)}, {"target_utilization": 1}
        )

        if not salon:
            raise ValueError("Salon not found")

        return salon.get("target_utilization", 75.0)
