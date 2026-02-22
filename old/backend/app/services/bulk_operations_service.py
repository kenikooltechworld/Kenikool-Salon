from datetime import datetime
from typing import List, Dict, Any, Optional
from bson import ObjectId
from app.database import db


class BulkOperationsService:
    """Service for bulk staff operations."""

    BATCH_SIZE = 50

    @staticmethod
    async def bulk_update_schedules(
        salon_id: str,
        staff_ids: List[str],
        schedule_template_id: str,
    ) -> Dict[str, Any]:
        """Bulk update schedules for multiple staff members."""
        staff_object_ids = [ObjectId(sid) for sid in staff_ids]
        
        # Process in batches
        total_updated = 0
        for i in range(0, len(staff_object_ids), BulkOperationsService.BATCH_SIZE):
            batch = staff_object_ids[i:i + BulkOperationsService.BATCH_SIZE]
            result = await db.stylists.update_many(
                {
                    "_id": {"$in": batch},
                    "salon_id": ObjectId(salon_id),
                },
                {
                    "$set": {
                        "schedule_template_id": ObjectId(schedule_template_id),
                        "updated_at": datetime.utcnow(),
                    }
                },
            )
            total_updated += result.modified_count

        return {
            "operation": "bulk_update_schedules",
            "total_staff": len(staff_ids),
            "updated": total_updated,
            "schedule_template_id": schedule_template_id,
        }

    @staticmethod
    async def bulk_update_commissions(
        salon_id: str,
        staff_ids: List[str],
        commission_type: str,
        commission_value: float,
    ) -> Dict[str, Any]:
        """Bulk update commission rates for multiple staff members."""
        staff_object_ids = [ObjectId(sid) for sid in staff_ids]
        
        total_updated = 0
        for i in range(0, len(staff_object_ids), BulkOperationsService.BATCH_SIZE):
            batch = staff_object_ids[i:i + BulkOperationsService.BATCH_SIZE]
            result = await db.stylists.update_many(
                {
                    "_id": {"$in": batch},
                    "salon_id": ObjectId(salon_id),
                },
                {
                    "$set": {
                        "commission_type": commission_type,
                        "commission_value": commission_value,
                        "updated_at": datetime.utcnow(),
                    }
                },
            )
            total_updated += result.modified_count

        return {
            "operation": "bulk_update_commissions",
            "total_staff": len(staff_ids),
            "updated": total_updated,
            "commission_type": commission_type,
            "commission_value": commission_value,
        }

    @staticmethod
    async def bulk_assign_services(
        salon_id: str,
        staff_ids: List[str],
        service_ids: List[str],
    ) -> Dict[str, Any]:
        """Bulk assign services to multiple staff members."""
        staff_object_ids = [ObjectId(sid) for sid in staff_ids]
        service_object_ids = [ObjectId(sid) for sid in service_ids]
        
        total_updated = 0
        for i in range(0, len(staff_object_ids), BulkOperationsService.BATCH_SIZE):
            batch = staff_object_ids[i:i + BulkOperationsService.BATCH_SIZE]
            result = await db.stylists.update_many(
                {
                    "_id": {"$in": batch},
                    "salon_id": ObjectId(salon_id),
                },
                {
                    "$addToSet": {
                        "services": {"$each": service_object_ids},
                    }
                },
            )
            total_updated += result.modified_count

        return {
            "operation": "bulk_assign_services",
            "total_staff": len(staff_ids),
            "updated": total_updated,
            "services_assigned": len(service_ids),
        }

    @staticmethod
    async def bulk_update_status(
        salon_id: str,
        staff_ids: List[str],
        is_active: bool,
    ) -> Dict[str, Any]:
        """Bulk update active status for multiple staff members."""
        staff_object_ids = [ObjectId(sid) for sid in staff_ids]
        
        total_updated = 0
        for i in range(0, len(staff_object_ids), BulkOperationsService.BATCH_SIZE):
            batch = staff_object_ids[i:i + BulkOperationsService.BATCH_SIZE]
            result = await db.stylists.update_many(
                {
                    "_id": {"$in": batch},
                    "salon_id": ObjectId(salon_id),
                },
                {
                    "$set": {
                        "is_active": is_active,
                        "updated_at": datetime.utcnow(),
                    }
                },
            )
            total_updated += result.modified_count

        return {
            "operation": "bulk_update_status",
            "total_staff": len(staff_ids),
            "updated": total_updated,
            "is_active": is_active,
        }

    @staticmethod
    async def bulk_assign_locations(
        salon_id: str,
        staff_ids: List[str],
        location_ids: List[str],
    ) -> Dict[str, Any]:
        """Bulk assign locations to multiple staff members."""
        staff_object_ids = [ObjectId(sid) for sid in staff_ids]
        location_object_ids = [ObjectId(lid) for lid in location_ids]
        
        total_updated = 0
        for i in range(0, len(staff_object_ids), BulkOperationsService.BATCH_SIZE):
            batch = staff_object_ids[i:i + BulkOperationsService.BATCH_SIZE]
            result = await db.stylists.update_many(
                {
                    "_id": {"$in": batch},
                    "salon_id": ObjectId(salon_id),
                },
                {
                    "$set": {
                        "locations": location_object_ids,
                        "updated_at": datetime.utcnow(),
                    }
                },
            )
            total_updated += result.modified_count

        return {
            "operation": "bulk_assign_locations",
            "total_staff": len(staff_ids),
            "updated": total_updated,
            "locations_assigned": len(location_ids),
        }

    @staticmethod
    async def bulk_export_staff(
        salon_id: str,
        staff_ids: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Export staff data for bulk operations."""
        match_query = {"salon_id": ObjectId(salon_id)}
        if staff_ids:
            match_query["_id"] = {"$in": [ObjectId(sid) for sid in staff_ids]}

        staff_list = await db.stylists.find(
            match_query,
            {
                "_id": 1,
                "name": 1,
                "email": 1,
                "phone": 1,
                "commission_type": 1,
                "commission_value": 1,
                "is_active": 1,
                "locations": 1,
                "services": 1,
            },
        ).to_list(None)

        return [
            {
                "id": str(staff["_id"]),
                "name": staff.get("name"),
                "email": staff.get("email"),
                "phone": staff.get("phone"),
                "commission_type": staff.get("commission_type"),
                "commission_value": staff.get("commission_value"),
                "is_active": staff.get("is_active"),
                "locations": [str(lid) for lid in staff.get("locations", [])],
                "services": [str(sid) for sid in staff.get("services", [])],
            }
            for staff in staff_list
        ]
