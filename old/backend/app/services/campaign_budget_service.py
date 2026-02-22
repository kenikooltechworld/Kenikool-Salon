from datetime import datetime
from typing import Any, Dict, Optional
from pymongo.collection import Collection


class CampaignBudgetService:
    """Service for campaign budget management"""

    def __init__(self, db_connection):
        self.db = db_connection
        self.campaigns_collection: Collection = self.db["campaigns"]
        self.sends_collection: Collection = self.db["campaign_sends"]

    def set_campaign_budget(self, campaign_id: str, tenant_id: str,
                           budget_limit: float) -> Dict[str, Any]:
        """Set budget limit for a campaign"""
        if budget_limit <= 0:
            raise ValueError("Budget must be greater than 0")

        result = self.campaigns_collection.find_one_and_update(
            {"_id": campaign_id, "tenant_id": tenant_id},
            {
                "$set": {
                    "budget_limit": budget_limit,
                    "updated_at": datetime.utcnow()
                }
            },
            return_document=True
        )
        return result

    def estimate_campaign_cost(self, campaign_id: str, tenant_id: str,
                              recipient_count: int, channels: list) -> Dict[str, Any]:
        """Estimate campaign cost"""
        channel_costs = {
            "sms": 0.05,
            "whatsapp": 0.08,
            "email": 0.01
        }

        total_cost = 0
        channel_breakdown = {}

        for channel in channels:
            cost_per_message = channel_costs.get(channel, 0)
            channel_cost = cost_per_message * recipient_count
            channel_breakdown[channel] = channel_cost
            total_cost += channel_cost

        return {
            "campaign_id": campaign_id,
            "recipient_count": recipient_count,
            "channels": channels,
            "estimated_cost": total_cost,
            "channel_breakdown": channel_breakdown
        }

    def validate_budget(self, campaign_id: str, tenant_id: str,
                       estimated_cost: float) -> Dict[str, Any]:
        """Validate if campaign cost is within budget"""
        campaign = self.campaigns_collection.find_one({
            "_id": campaign_id,
            "tenant_id": tenant_id
        })

        if not campaign:
            raise ValueError("Campaign not found")

        budget_limit = campaign.get("budget_limit")
        
        if not budget_limit:
            return {
                "valid": True,
                "message": "No budget limit set",
                "estimated_cost": estimated_cost
            }

        if estimated_cost > budget_limit:
            return {
                "valid": False,
                "message": f"Estimated cost ${estimated_cost:.2f} exceeds budget ${budget_limit:.2f}",
                "estimated_cost": estimated_cost,
                "budget_limit": budget_limit,
                "overage": estimated_cost - budget_limit
            }

        return {
            "valid": True,
            "message": "Within budget",
            "estimated_cost": estimated_cost,
            "budget_limit": budget_limit,
            "remaining": budget_limit - estimated_cost
        }

    def get_budget_summary(self, tenant_id: str) -> Dict[str, Any]:
        """Get budget summary for all campaigns"""
        campaigns = list(self.campaigns_collection.find({
            "tenant_id": tenant_id,
            "budget_limit": {"$exists": True, "$ne": None}
        }))

        total_budget = sum(c.get("budget_limit", 0) for c in campaigns)
        total_spent = sum(c.get("actual_cost", 0) for c in campaigns)
        
        campaigns_by_status = {
            "within_budget": 0,
            "approaching_limit": 0,
            "exceeded": 0
        }

        for campaign in campaigns:
            budget = campaign.get("budget_limit", 0)
            spent = campaign.get("actual_cost", 0)
            
            if spent > budget:
                campaigns_by_status["exceeded"] += 1
            elif spent > budget * 0.8:
                campaigns_by_status["approaching_limit"] += 1
            else:
                campaigns_by_status["within_budget"] += 1

        return {
            "total_budget": total_budget,
            "total_spent": total_spent,
            "remaining": total_budget - total_spent,
            "utilization_percentage": (total_spent / total_budget * 100) if total_budget > 0 else 0,
            "campaigns_by_status": campaigns_by_status,
            "total_campaigns": len(campaigns)
        }

    def check_budget_alert(self, campaign_id: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Check if campaign should trigger budget alert"""
        campaign = self.campaigns_collection.find_one({
            "_id": campaign_id,
            "tenant_id": tenant_id
        })

        if not campaign:
            return None

        budget_limit = campaign.get("budget_limit")
        actual_cost = campaign.get("actual_cost", 0)

        if not budget_limit:
            return None

        utilization = (actual_cost / budget_limit * 100)

        if utilization >= 100:
            return {
                "alert_type": "exceeded",
                "message": f"Campaign has exceeded budget limit",
                "budget_limit": budget_limit,
                "actual_cost": actual_cost,
                "overage": actual_cost - budget_limit
            }
        elif utilization >= 80:
            return {
                "alert_type": "approaching",
                "message": f"Campaign is approaching budget limit ({utilization:.1f}% used)",
                "budget_limit": budget_limit,
                "actual_cost": actual_cost,
                "remaining": budget_limit - actual_cost
            }

        return None

    def get_spending_trends(self, tenant_id: str, days: int = 30) -> Dict[str, Any]:
        """Get spending trends"""
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        campaigns = list(self.campaigns_collection.find({
            "tenant_id": tenant_id,
            "created_at": {"$gte": cutoff_date}
        }))

        total_spent = sum(c.get("actual_cost", 0) for c in campaigns)
        avg_campaign_cost = (total_spent / len(campaigns)) if campaigns else 0

        return {
            "period_days": days,
            "total_campaigns": len(campaigns),
            "total_spent": total_spent,
            "average_campaign_cost": avg_campaign_cost,
            "campaigns": [
                {
                    "id": c.get("_id"),
                    "name": c.get("name"),
                    "cost": c.get("actual_cost", 0),
                    "budget": c.get("budget_limit")
                }
                for c in campaigns
            ]
        }
