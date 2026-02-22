from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from pymongo.collection import Collection


class AutomationService:
    """Service for managing campaign automation"""

    def __init__(self, db_connection):
        self.db = db_connection
        self.settings_collection: Collection = self.db["automation_settings"]
        self.history_collection: Collection = self.db["automation_history"]
        self._create_indexes()

    def _create_indexes(self):
        """Create database indexes"""
        self.settings_collection.create_index("tenant_id", unique=True)
        self.history_collection.create_index("tenant_id")
        self.history_collection.create_index([("tenant_id", 1), ("executed_at", -1)])

    def get_settings(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Get automation settings for tenant"""
        return self.settings_collection.find_one({"tenant_id": tenant_id})

    def update_settings(self, tenant_id: str, settings: Dict[str, Any], 
                       updated_by: str) -> Dict[str, Any]:
        """Update automation settings"""
        settings["updated_at"] = datetime.utcnow()
        settings["updated_by"] = updated_by
        settings["tenant_id"] = tenant_id

        result = self.settings_collection.find_one_and_update(
            {"tenant_id": tenant_id},
            {"$set": settings},
            upsert=True,
            return_document=True
        )
        return result

    def get_history(self, tenant_id: str, skip: int = 0, 
                   limit: int = 50) -> List[Dict[str, Any]]:
        """Get automation execution history"""
        return list(self.history_collection.find(
            {"tenant_id": tenant_id}
        ).sort("executed_at", -1).skip(skip).limit(limit))

    def record_execution(self, tenant_id: str, automation_type: str,
                        campaign_id: str, recipients_count: int,
                        sent_count: int, failed_count: int,
                        status: str, error_message: Optional[str] = None) -> Dict[str, Any]:
        """Record automation execution"""
        record = {
            "tenant_id": tenant_id,
            "automation_type": automation_type,
            "campaign_id": campaign_id,
            "executed_at": datetime.utcnow(),
            "recipients_count": recipients_count,
            "sent_count": sent_count,
            "failed_count": failed_count,
            "status": status,
            "error_message": error_message
        }
        result = self.history_collection.insert_one(record)
        record["_id"] = str(result.inserted_id)
        return record

    def get_next_run_time(self, tenant_id: str, automation_type: str) -> Optional[datetime]:
        """Calculate next run time for automation"""
        settings = self.get_settings(tenant_id)
        if not settings:
            return None

        automation_config = settings.get(f"{automation_type}_campaigns", {})
        if not automation_config.get("enabled"):
            return None

        # For daily automations, next run is tomorrow at configured time
        send_time = automation_config.get("send_time", "09:00")
        hour, minute = map(int, send_time.split(":"))
        
        now = datetime.utcnow()
        next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        if next_run <= now:
            next_run += timedelta(days=1)
        
        return next_run

    def should_run_automation(self, tenant_id: str, automation_type: str) -> bool:
        """Check if automation should run now"""
        settings = self.get_settings(tenant_id)
        if not settings or not settings.get("enabled"):
            return False

        automation_config = settings.get(f"{automation_type}_campaigns", {})
        if not automation_config.get("enabled"):
            return False

        # Check if we've already run today
        today = datetime.utcnow().date()
        last_run = self.history_collection.find_one(
            {
                "tenant_id": tenant_id,
                "automation_type": automation_type,
                "executed_at": {
                    "$gte": datetime.combine(today, datetime.min.time()),
                    "$lte": datetime.combine(today, datetime.max.time())
                }
            },
            sort=[("executed_at", -1)]
        )

        return last_run is None

    def check_frequency_limit(self, tenant_id: str, client_id: str,
                             automation_type: str, limit_days: int) -> bool:
        """Check if client has reached frequency limit for automation"""
        cutoff_date = datetime.utcnow() - timedelta(days=limit_days)
        
        recent_send = self.history_collection.find_one(
            {
                "tenant_id": tenant_id,
                "automation_type": automation_type,
                "executed_at": {"$gte": cutoff_date}
            }
        )
        
        return recent_send is None

    def get_statistics(self, tenant_id: str, days: int = 30) -> Dict[str, Any]:
        """Get automation statistics"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        history = list(self.history_collection.find(
            {
                "tenant_id": tenant_id,
                "executed_at": {"$gte": cutoff_date}
            }
        ))

        total_sent = sum(h.get("sent_count", 0) for h in history)
        total_failed = sum(h.get("failed_count", 0) for h in history)
        total_recipients = sum(h.get("recipients_count", 0) for h in history)

        by_type = {}
        for record in history:
            auto_type = record.get("automation_type")
            if auto_type not in by_type:
                by_type[auto_type] = {
                    "count": 0,
                    "sent": 0,
                    "failed": 0
                }
            by_type[auto_type]["count"] += 1
            by_type[auto_type]["sent"] += record.get("sent_count", 0)
            by_type[auto_type]["failed"] += record.get("failed_count", 0)

        return {
            "total_executions": len(history),
            "total_recipients": total_recipients,
            "total_sent": total_sent,
            "total_failed": total_failed,
            "success_rate": (total_sent / total_recipients * 100) if total_recipients > 0 else 0,
            "by_type": by_type
        }
