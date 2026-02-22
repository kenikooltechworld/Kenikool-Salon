"""
Usage Tracking Service - Track resource usage for subscription limits
"""
from datetime import datetime, timedelta
from typing import Dict, Optional
from app.database import Database


class UsageTrackingService:
    """Service for tracking and managing resource usage"""

    @staticmethod
    async def track_booking(tenant_id: str) -> None:
        """Track a booking creation"""
        db = Database.get_db()
        now = datetime.utcnow()
        month_key = now.strftime("%Y-%m")
        
        db.usage_tracking.update_one(
            {"tenant_id": tenant_id, "month": month_key},
            {
                "$inc": {"bookings": 1},
                "$set": {"updated_at": now},
                "$setOnInsert": {
                    "tenant_id": tenant_id,
                    "month": month_key,
                    "created_at": now,
                    "staff": 0,
                    "sms_sent": 0,
                    "api_calls": 0
                }
            },
            upsert=True
        )

    @staticmethod
    async def track_sms(tenant_id: str, count: int = 1) -> None:
        """Track SMS sent via Termii"""
        db = Database.get_db()
        now = datetime.utcnow()
        month_key = now.strftime("%Y-%m")
        
        db.usage_tracking.update_one(
            {"tenant_id": tenant_id, "month": month_key},
            {
                "$inc": {"sms_sent": count},
                "$set": {"updated_at": now},
                "$setOnInsert": {
                    "tenant_id": tenant_id,
                    "month": month_key,
                    "created_at": now,
                    "bookings": 0,
                    "staff": 0,
                    "api_calls": 0
                }
            },
            upsert=True
        )

    @staticmethod
    async def track_api_call(tenant_id: str) -> None:
        """Track API call"""
        db = Database.get_db()
        now = datetime.utcnow()
        month_key = now.strftime("%Y-%m")
        
        db.usage_tracking.update_one(
            {"tenant_id": tenant_id, "month": month_key},
            {
                "$inc": {"api_calls": 1},
                "$set": {"updated_at": now},
                "$setOnInsert": {
                    "tenant_id": tenant_id,
                    "month": month_key,
                    "created_at": now,
                    "bookings": 0,
                    "staff": 0,
                    "sms_sent": 0
                }
            },
            upsert=True
        )

    @staticmethod
    async def update_staff_count(tenant_id: str) -> None:
        """Update current staff count"""
        db = Database.get_db()
        staff_count = db.stylists.count_documents({
            "tenant_id": tenant_id,
            "is_active": True
        })
        
        now = datetime.utcnow()
        month_key = now.strftime("%Y-%m")
        
        db.usage_tracking.update_one(
            {"tenant_id": tenant_id, "month": month_key},
            {
                "$set": {"staff": staff_count, "updated_at": now},
                "$setOnInsert": {
                    "tenant_id": tenant_id,
                    "month": month_key,
                    "created_at": now,
                    "bookings": 0,
                    "clients": 0,
                    "sms_sent": 0,
                    "api_calls": 0
                }
            },
            upsert=True
        )

    @staticmethod
    async def update_client_count(tenant_id: str) -> None:
        """Update current client count"""
        db = Database.get_db()
        client_count = db.clients.count_documents({
            "tenant_id": tenant_id,
            "is_active": True
        })
        
        now = datetime.utcnow()
        month_key = now.strftime("%Y-%m")
        
        db.usage_tracking.update_one(
            {"tenant_id": tenant_id, "month": month_key},
            {
                "$set": {"clients": client_count, "updated_at": now},
                "$setOnInsert": {
                    "tenant_id": tenant_id,
                    "month": month_key,
                    "created_at": now,
                    "bookings": 0,
                    "staff": 0,
                    "sms_sent": 0,
                    "api_calls": 0
                }
            },
            upsert=True
        )

    @staticmethod
    async def get_usage_stats(tenant_id: str, month: Optional[str] = None) -> Dict:
        """Get usage statistics for a tenant"""
        db = Database.get_db()
        
        if not month:
            month = datetime.utcnow().strftime("%Y-%m")
        
        usage = db.usage_tracking.find_one({
            "tenant_id": tenant_id,
            "month": month
        })
        
        if not usage:
            return {
                "month": month,
                "bookings": 0,
                "staff": 0,
                "clients": 0,
                "sms_sent": 0,
                "api_calls": 0
            }
        
        return {
            "month": usage.get("month"),
            "bookings": usage.get("bookings", 0),
            "staff": usage.get("staff", 0),
            "clients": usage.get("clients", 0),
            "sms_sent": usage.get("sms_sent", 0),
            "api_calls": usage.get("api_calls", 0),
            "updated_at": usage.get("updated_at")
        }

    @staticmethod
    async def get_usage_history(tenant_id: str, months: int = 6) -> list:
        """Get usage history for multiple months"""
        db = Database.get_db()
        now = datetime.utcnow()
        month_keys = []
        
        for i in range(months):
            date = now - timedelta(days=30 * i)
            month_keys.append(date.strftime("%Y-%m"))
        
        usage_records = db.usage_tracking.find({
            "tenant_id": tenant_id,
            "month": {"$in": month_keys}
        }).sort("month", -1)
        
        return list(usage_records)
