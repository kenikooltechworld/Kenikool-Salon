from datetime import datetime
from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.database import db


class MultiLocationService:
    """Service for managing multi-location staff assignments."""

    @staticmethod
    async def assign_locations(
        staff_id: str,
        salon_id: str,
        locations: List[str],
    ) -> Dict[str, Any]:
        """Assign staff to multiple locations."""
        # Validate locations exist
        location_ids = [ObjectId(loc_id) for loc_id in locations]
        existing_locations = await db.locations.find(
            {"_id": {"$in": location_ids}, "salon_id": ObjectId(salon_id)},
            {"_id": 1},
        ).to_list(None)

        if len(existing_locations) != len(locations):
            raise ValueError("One or more locations not found")

        result = await db.stylists.update_one(
            {
                "_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
            },
            {
                "$set": {
                    "locations": location_ids,
                    "updated_at": datetime.utcnow(),
                }
            },
        )

        if result.matched_count == 0:
            raise ValueError("Staff member not found")

        return {"staff_id": staff_id, "locations": locations}

    @staticmethod
    async def get_staff_locations(
        staff_id: str,
        salon_id: str,
    ) -> List[Dict[str, Any]]:
        """Get all locations assigned to a staff member."""
        staff = await db.stylists.find_one(
            {
                "_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
            },
            {"locations": 1},
        )

        if not staff:
            raise ValueError("Staff member not found")

        location_ids = staff.get("locations", [])
        if not location_ids:
            return []

        locations = await db.locations.find(
            {"_id": {"$in": location_ids}},
            {"_id": 1, "name": 1, "address": 1, "phone": 1},
        ).to_list(None)

        return [
            {
                "id": str(loc["_id"]),
                "name": loc.get("name"),
                "address": loc.get("address"),
                "phone": loc.get("phone"),
            }
            for loc in locations
        ]

    @staticmethod
    async def add_location_schedule(
        staff_id: str,
        salon_id: str,
        location_id: str,
        schedule_template_id: Optional[str] = None,
        commission_rate: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Add location-specific schedule and commission rate."""
        staff = await db.stylists.find_one(
            {
                "_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
            }
        )

        if not staff:
            raise ValueError("Staff member not found")

        location_schedules = staff.get("location_schedules", {})
        location_schedules[location_id] = {
            "schedule_template_id": schedule_template_id,
            "commission_rate": commission_rate,
            "updated_at": datetime.utcnow(),
        }

        await db.stylists.update_one(
            {
                "_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
            },
            {"$set": {"location_schedules": location_schedules}},
        )

        return location_schedules[location_id]

    @staticmethod
    async def get_location_schedule(
        staff_id: str,
        salon_id: str,
        location_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Get location-specific schedule and commission rate."""
        staff = await db.stylists.find_one(
            {
                "_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
            },
            {"location_schedules": 1},
        )

        if not staff:
            raise ValueError("Staff member not found")

        location_schedules = staff.get("location_schedules", {})
        return location_schedules.get(location_id)

    @staticmethod
    async def get_location_distribution(
        salon_id: str,
        location_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get staff distribution across locations."""
        match_query = {"salon_id": ObjectId(salon_id)}
        if location_id:
            match_query["locations"] = ObjectId(location_id)

        pipeline = [
            {"$match": match_query},
            {"$unwind": "$locations"},
            {
                "$group": {
                    "_id": "$locations",
                    "staff_count": {"$sum": 1},
                    "staff_ids": {"$push": "$_id"},
                }
            },
            {
                "$lookup": {
                    "from": "locations",
                    "localField": "_id",
                    "foreignField": "_id",
                    "as": "location_info",
                }
            },
            {"$unwind": "$location_info"},
            {
                "$project": {
                    "location_id": "$_id",
                    "location_name": "$location_info.name",
                    "staff_count": 1,
                    "staff_ids": 1,
                }
            },
        ]

        results = await db.stylists.aggregate(pipeline).to_list(None)

        return {
            "total_locations": len(results),
            "distribution": [
                {
                    "location_id": str(r["location_id"]),
                    "location_name": r.get("location_name"),
                    "staff_count": r["staff_count"],
                    "staff_ids": [str(sid) for sid in r["staff_ids"]],
                }
                for r in results
            ],
        }

    @staticmethod
    async def calculate_location_hours(
        staff_id: str,
        salon_id: str,
        location_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Any]:
        """Calculate hours worked at a specific location."""
        attendance_records = await db.attendance_records.find(
            {
                "staff_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
                "location_id": ObjectId(location_id),
                "date": {"$gte": start_date, "$lte": end_date},
            }
        ).to_list(None)

        total_hours = 0
        total_breaks = 0

        for record in attendance_records:
            if record.get("clock_out_time") and record.get("clock_in_time"):
                hours = (
                    record["clock_out_time"] - record["clock_in_time"]
                ).total_seconds() / 3600
                total_hours += hours

                # Subtract break time
                breaks = record.get("breaks", [])
                for break_period in breaks:
                    if break_period.get("end_time") and break_period.get("start_time"):
                        break_hours = (
                            break_period["end_time"] - break_period["start_time"]
                        ).total_seconds() / 3600
                        total_breaks += break_hours

        return {
            "staff_id": staff_id,
            "location_id": location_id,
            "total_hours": total_hours - total_breaks,
            "period": {"start": start_date, "end": end_date},
        }

    @staticmethod
    async def get_location_performance(
        salon_id: str,
        location_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Any]:
        """Get performance metrics for a location."""
        # Get all staff at location
        staff_list = await db.stylists.find(
            {
                "salon_id": ObjectId(salon_id),
                "locations": ObjectId(location_id),
            },
            {"_id": 1, "name": 1},
        ).to_list(None)

        staff_performance = []

        for staff in staff_list:
            # Get bookings at this location
            bookings = await db.bookings.find(
                {
                    "stylist_id": staff["_id"],
                    "location_id": ObjectId(location_id),
                    "date": {"$gte": start_date, "$lte": end_date},
                    "status": "completed",
                }
            ).to_list(None)

            revenue = sum(b.get("total_price", 0) for b in bookings)
            booking_count = len(bookings)

            staff_performance.append(
                {
                    "staff_id": str(staff["_id"]),
                    "staff_name": staff.get("name"),
                    "bookings": booking_count,
                    "revenue": revenue,
                    "average_booking_value": revenue / booking_count if booking_count > 0 else 0,
                }
            )

        return {
            "location_id": location_id,
            "period": {"start": start_date, "end": end_date},
            "staff_performance": staff_performance,
            "total_revenue": sum(s["revenue"] for s in staff_performance),
            "total_bookings": sum(s["bookings"] for s in staff_performance),
        }
