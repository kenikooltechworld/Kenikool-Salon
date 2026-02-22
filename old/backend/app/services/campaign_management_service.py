from datetime import datetime
from typing import Dict, List, Optional
from bson import ObjectId
from app.database import Database


class CampaignManagementService:
    
    @staticmethod
    def create_campaign(
        tenant_id: str,
        name: str,
        description: str,
        campaign_type: str,
        start_date: str,
        end_date: str,
        target_audience: List[str],
        message: str,
        budget: Optional[float] = None
    ) -> Dict:
        """Create marketing campaign"""
        db = Database.get_db()
        
        campaign = {
            "tenant_id": tenant_id,
            "name": name,
            "description": description,
            "campaign_type": campaign_type,
            "start_date": datetime.fromisoformat(start_date.replace('Z', '+00:00')),
            "end_date": datetime.fromisoformat(end_date.replace('Z', '+00:00')),
            "target_audience": target_audience,
            "message": message,
            "budget": budget,
            "status": "draft",
            "created_at": datetime.utcnow()
        }
        
        result = db.campaigns.insert_one(campaign)
        campaign["_id"] = str(result.inserted_id)
        
        return campaign
    
    @staticmethod
    def launch_campaign(tenant_id: str, campaign_id: str) -> Dict:
        """Launch campaign"""
        db = Database.get_db()
        
        campaign = db.campaigns.find_one({
            "_id": ObjectId(campaign_id),
            "tenant_id": tenant_id
        })
        
        if not campaign:
            raise ValueError("Campaign not found")
        
        db.campaigns.update_one(
            {"_id": ObjectId(campaign_id)},
            {
                "$set": {
                    "status": "active",
                    "launched_at": datetime.utcnow()
                }
            }
        )
        
        # Send campaign messages
        try:
            from app.tasks.campaign_tasks import send_campaign_messages
            send_campaign_messages.delay(campaign_id)
        except Exception as e:
            pass
        
        return {"status": "launched"}
    
    @staticmethod
    def get_campaign_performance(tenant_id: str, campaign_id: str) -> Dict:
        """Get campaign performance metrics"""
        db = Database.get_db()
        
        campaign = db.campaigns.find_one({
            "_id": ObjectId(campaign_id),
            "tenant_id": tenant_id
        })
        
        if not campaign:
            raise ValueError("Campaign not found")
        
        # Get campaign interactions
        interactions = list(db.campaign_interactions.find({
            "campaign_id": ObjectId(campaign_id)
        }))
        
        # Get conversions
        conversions = len([i for i in interactions if i.get("type") == "conversion"])
        clicks = len([i for i in interactions if i.get("type") == "click"])
        views = len([i for i in interactions if i.get("type") == "view"])
        
        return {
            "campaign_id": campaign_id,
            "name": campaign.get("name"),
            "views": views,
            "clicks": clicks,
            "conversions": conversions,
            "ctr": (clicks / views * 100) if views > 0 else 0,
            "conversion_rate": (conversions / clicks * 100) if clicks > 0 else 0
        }
    
    @staticmethod
    def get_active_campaigns(tenant_id: str) -> List[Dict]:
        """Get active campaigns"""
        db = Database.get_db()
        
        now = datetime.utcnow()
        
        campaigns = list(db.campaigns.find({
            "tenant_id": tenant_id,
            "status": "active",
            "start_date": {"$lte": now},
            "end_date": {"$gte": now}
        }))
        
        return campaigns
    
    @staticmethod
    def end_campaign(tenant_id: str, campaign_id: str) -> Dict:
        """End campaign"""
        db = Database.get_db()
        
        result = db.campaigns.update_one(
            {
                "_id": ObjectId(campaign_id),
                "tenant_id": tenant_id
            },
            {
                "$set": {
                    "status": "ended",
                    "ended_at": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            raise ValueError("Campaign not found")
        
        return {"status": "ended"}
