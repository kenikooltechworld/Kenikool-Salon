"""
Advanced Scheduling Service for campaigns
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from bson import ObjectId
from pymongo import ASCENDING
from app.database import Database
import pytz


class AdvancedSchedulingService:
    """Service for managing advanced campaign scheduling"""

    @staticmethod
    def _get_db():
        """Get database instance"""
        return Database.get_db()

    def __init__(self):
        self.collection = AdvancedSchedulingService._get_db().campaigns
        self._ensure_indexes()

    def _ensure_indexes(self):
        """Create necessary indexes"""
        self.collection.create_index([("tenant_id", ASCENDING)])
        self.collection.create_index([("recurrence", ASCENDING)])
        self.collection.create_index([("trigger_event", ASCENDING)])
        self.collection.create_index([("scheduled_at", ASCENDING)])

    async def add_recurrence(
        self,
        campaign_id: str,
        tenant_id: str,
        recurrence_type: str,  # daily, weekly, monthly
        recurrence_config: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Add recurrence to a campaign"""
        try:
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(campaign_id), "tenant_id": tenant_id},
                {
                    "$set": {
                        "recurrence": recurrence_type,
                        "recurrence_config": recurrence_config,
                        "updated_at": datetime.utcnow()
                    }
                },
                return_document=True
            )
            return result
        except:
            return None

    async def add_trigger(
        self,
        campaign_id: str,
        tenant_id: str,
        trigger_event: str,  # post_booking, post_visit, anniversary
        trigger_config: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Add trigger to a campaign"""
        try:
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(campaign_id), "tenant_id": tenant_id},
                {
                    "$set": {
                        "trigger_event": trigger_event,
                        "trigger_config": trigger_config,
                        "updated_at": datetime.utcnow()
                    }
                },
                return_document=True
            )
            return result
        except:
            return None

    async def set_optimal_send_time(
        self,
        campaign_id: str,
        tenant_id: str,
        use_optimal_time: bool,
        optimal_time: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Set optimal send time for a campaign"""
        try:
            update_data = {
                "use_optimal_send_time": use_optimal_time,
                "updated_at": datetime.utcnow()
            }
            if optimal_time:
                update_data["optimal_send_time"] = optimal_time
            
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(campaign_id), "tenant_id": tenant_id},
                {"$set": update_data},
                return_document=True
            )
            return result
        except:
            return None

    def calculate_next_execution(
        self,
        recurrence_type: str,
        recurrence_config: Dict[str, Any],
        last_execution: Optional[datetime] = None
    ) -> datetime:
        """Calculate next execution time for recurring campaign"""
        now = datetime.utcnow()
        
        if recurrence_type == "daily":
            return now + timedelta(days=1)
        
        elif recurrence_type == "weekly":
            days_ahead = recurrence_config.get("day_of_week", 0)
            current_day = now.weekday()
            days_to_add = (days_ahead - current_day) % 7
            if days_to_add == 0:
                days_to_add = 7
            return now + timedelta(days=days_to_add)
        
        elif recurrence_type == "monthly":
            day_of_month = recurrence_config.get("day_of_month", 1)
            if now.day >= day_of_month:
                # Next month
                if now.month == 12:
                    next_date = now.replace(year=now.year + 1, month=1, day=day_of_month)
                else:
                    next_date = now.replace(month=now.month + 1, day=day_of_month)
            else:
                next_date = now.replace(day=day_of_month)
            return next_date
        
        return now + timedelta(days=1)

    async def get_recurring_campaigns(
        self,
        tenant_id: str
    ) -> List[Dict[str, Any]]:
        """Get all recurring campaigns for a tenant"""
        campaigns = await self.collection.find({
            "tenant_id": tenant_id,
            "recurrence": {"$exists": True, "$ne": None}
        }).to_list(None)
        return campaigns

    async def get_triggered_campaigns(
        self,
        tenant_id: str,
        trigger_event: str
    ) -> List[Dict[str, Any]]:
        """Get all campaigns triggered by a specific event"""
        campaigns = await self.collection.find({
            "tenant_id": tenant_id,
            "trigger_event": trigger_event,
            "status": "active"
        }).to_list(None)
        return campaigns

    async def calculate_optimal_send_time(
        self,
        client_id: str,
        tenant_id: str
    ) -> str:
        """Calculate optimal send time for a client based on engagement history"""
        # Get client's engagement data
        sends_collection = db.campaign_sends
        
        pipeline = [
            {
                "$match": {
                    "client_id": client_id,
                    "tenant_id": tenant_id,
                    "opened_at": {"$exists": True}
                }
            },
            {
                "$group": {
                    "_id": {
                        "$hour": "$opened_at"
                    },
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"count": -1}
            },
            {
                "$limit": 1
            }
        ]
        
        result = await sends_collection.aggregate(pipeline).to_list(1)
        
        if result:
            optimal_hour = result[0]["_id"]
            return f"{optimal_hour:02d}:00"
        
        # Default to 9 AM if no data
        return "09:00"

    async def get_next_execution_time(
        self,
        campaign_id: str,
        tenant_id: str
    ) -> Optional[datetime]:
        """Get next execution time for a campaign"""
        try:
            campaign = await self.collection.find_one({
                "_id": ObjectId(campaign_id),
                "tenant_id": tenant_id
            })
            
            if not campaign:
                return None
            
            recurrence = campaign.get("recurrence")
            if not recurrence:
                return None
            
            recurrence_config = campaign.get("recurrence_config", {})
            last_execution = campaign.get("last_execution")
            
            next_time = self.calculate_next_execution(
                recurrence,
                recurrence_config,
                last_execution
            )
            
            return next_time
        except:
            return None

    async def create_recurring_instance(
        self,
        campaign_id: str,
        tenant_id: str
    ) -> Optional[Dict[str, Any]]:
        """Create an instance of a recurring campaign"""
        try:
            campaign = await self.collection.find_one({
                "_id": ObjectId(campaign_id),
                "tenant_id": tenant_id
            })
            
            if not campaign:
                return None
            
            # Create new campaign instance
            instance = {
                "parent_campaign_id": campaign_id,
                "tenant_id": tenant_id,
                "name": f"{campaign['name']} - {datetime.utcnow().isoformat()}",
                "campaign_type": campaign.get("campaign_type"),
                "channels": campaign.get("channels", []),
                "message_templates": campaign.get("message_templates", {}),
                "segment_id": campaign.get("segment_id"),
                "status": "draft",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = await self.collection.insert_one(instance)
            instance["_id"] = result.inserted_id
            
            # Update parent's last execution
            await self.collection.update_one(
                {"_id": ObjectId(campaign_id)},
                {"$set": {"last_execution": datetime.utcnow()}}
            )
            
            return instance
        except:
            return None


# Lazy-loaded singleton instance
_advanced_scheduling_service = None

def get_advanced_scheduling_service():
    """Get or create the advanced scheduling service"""
    global _advanced_scheduling_service
    if _advanced_scheduling_service is None:
        _advanced_scheduling_service = AdvancedSchedulingService()
    return _advanced_scheduling_service

# For backward compatibility - use function instead of direct instantiation
class _LazyAdvancedSchedulingService:
    def __getattr__(self, name):
        return getattr(get_advanced_scheduling_service(), name)

advanced_scheduling_service = _LazyAdvancedSchedulingService()
