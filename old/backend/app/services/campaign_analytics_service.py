from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from pymongo.collection import Collection


class CampaignAnalyticsService:
    """Service for campaign analytics and reporting"""

    def __init__(self, db_connection):
        self.db = db_connection
        self.sends_collection: Collection = self.db["campaign_sends"]
        self.campaigns_collection: Collection = self.db["campaigns"]
        self._create_indexes()

    def _create_indexes(self):
        """Create database indexes"""
        self.sends_collection.create_index("campaign_id")
        self.sends_collection.create_index([("campaign_id", 1), ("status", 1)])
        self.sends_collection.create_index([("campaign_id", 1), ("channel", 1)])
        self.sends_collection.create_index([("tenant_id", 1), ("created_at", -1)])

    def record_send(self, campaign_id: str, tenant_id: str, client_id: str,
                   channel: str, message_content: str, cost: float) -> Dict[str, Any]:
        """Record a campaign send"""
        send_record = {
            "campaign_id": campaign_id,
            "tenant_id": tenant_id,
            "client_id": client_id,
            "channel": channel,
            "message_content": message_content,
            "status": "pending",
            "cost": cost,
            "retry_count": 0,
            "created_at": datetime.utcnow()
        }
        result = self.sends_collection.insert_one(send_record)
        send_record["_id"] = str(result.inserted_id)
        return send_record

    def update_send_status(self, send_id: str, status: str, 
                          delivered_at: Optional[datetime] = None,
                          error_code: Optional[str] = None,
                          error_message: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Update send status"""
        update_data = {"status": status}
        if delivered_at:
            update_data["delivered_at"] = delivered_at
        if error_code:
            update_data["error_code"] = error_code
        if error_message:
            update_data["error_message"] = error_message

        result = self.sends_collection.find_one_and_update(
            {"_id": send_id},
            {"$set": update_data},
            return_document=True
        )
        return result

    def get_campaign_analytics(self, campaign_id: str, tenant_id: str) -> Dict[str, Any]:
        """Get comprehensive analytics for a campaign"""
        sends = list(self.sends_collection.find({
            "campaign_id": campaign_id,
            "tenant_id": tenant_id
        }))

        if not sends:
            return {
                "campaign_id": campaign_id,
                "total_recipients": 0,
                "delivered": 0,
                "failed": 0,
                "delivery_rate": 0.0
            }

        total = len(sends)
        delivered = len([s for s in sends if s.get("status") == "delivered"])
        failed = len([s for s in sends if s.get("status") == "failed"])
        opened = len([s for s in sends if s.get("opened_at")])
        clicked = len([s for s in sends if s.get("clicked_at")])
        conversions = len([s for s in sends if s.get("booking_id") or s.get("transaction_id")])

        total_cost = sum(s.get("cost", 0) for s in sends)
        revenue = sum(s.get("revenue_attributed", 0) for s in sends)

        return {
            "campaign_id": campaign_id,
            "total_recipients": total,
            "delivered": delivered,
            "failed": failed,
            "delivery_rate": (delivered / total * 100) if total > 0 else 0,
            "opened": opened,
            "open_rate": (opened / delivered * 100) if delivered > 0 else 0,
            "clicked": clicked,
            "click_rate": (clicked / delivered * 100) if delivered > 0 else 0,
            "conversions": conversions,
            "conversion_rate": (conversions / delivered * 100) if delivered > 0 else 0,
            "revenue_generated": revenue,
            "roi": ((revenue - total_cost) / total_cost * 100) if total_cost > 0 else 0,
            "total_cost": total_cost,
            "cost_per_conversion": (total_cost / conversions) if conversions > 0 else 0
        }

    def get_channel_breakdown(self, campaign_id: str, tenant_id: str) -> Dict[str, Any]:
        """Get analytics broken down by channel"""
        sends = list(self.sends_collection.find({
            "campaign_id": campaign_id,
            "tenant_id": tenant_id
        }))

        channels = {}
        for send in sends:
            channel = send.get("channel", "unknown")
            if channel not in channels:
                channels[channel] = {
                    "sent": 0,
                    "delivered": 0,
                    "failed": 0,
                    "opened": 0,
                    "clicked": 0,
                    "cost": 0.0
                }
            
            channels[channel]["sent"] += 1
            if send.get("status") == "delivered":
                channels[channel]["delivered"] += 1
            elif send.get("status") == "failed":
                channels[channel]["failed"] += 1
            if send.get("opened_at"):
                channels[channel]["opened"] += 1
            if send.get("clicked_at"):
                channels[channel]["clicked"] += 1
            channels[channel]["cost"] += send.get("cost", 0)

        return channels

    def get_daily_stats(self, campaign_id: str, tenant_id: str) -> List[Dict[str, Any]]:
        """Get daily statistics for a campaign"""
        sends = list(self.sends_collection.find({
            "campaign_id": campaign_id,
            "tenant_id": tenant_id
        }).sort("created_at", 1))

        daily_stats = {}
        for send in sends:
            date = send.get("created_at").date()
            date_str = date.isoformat()
            
            if date_str not in daily_stats:
                daily_stats[date_str] = {
                    "date": date_str,
                    "delivered": 0,
                    "failed": 0,
                    "opened": 0,
                    "clicked": 0,
                    "conversions": 0
                }
            
            if send.get("status") == "delivered":
                daily_stats[date_str]["delivered"] += 1
            elif send.get("status") == "failed":
                daily_stats[date_str]["failed"] += 1
            if send.get("opened_at"):
                daily_stats[date_str]["opened"] += 1
            if send.get("clicked_at"):
                daily_stats[date_str]["clicked"] += 1
            if send.get("booking_id") or send.get("transaction_id"):
                daily_stats[date_str]["conversions"] += 1

        return list(daily_stats.values())

    def compare_campaigns(self, campaign_ids: List[str], tenant_id: str) -> List[Dict[str, Any]]:
        """Compare multiple campaigns"""
        comparisons = []
        for campaign_id in campaign_ids:
            analytics = self.get_campaign_analytics(campaign_id, tenant_id)
            comparisons.append(analytics)
        return comparisons

    def get_cost_breakdown(self, campaign_id: str, tenant_id: str) -> Dict[str, Any]:
        """Get cost breakdown by channel"""
        sends = list(self.sends_collection.find({
            "campaign_id": campaign_id,
            "tenant_id": tenant_id
        }))

        breakdown = {}
        total_cost = 0
        for send in sends:
            channel = send.get("channel", "unknown")
            cost = send.get("cost", 0)
            
            if channel not in breakdown:
                breakdown[channel] = 0
            breakdown[channel] += cost
            total_cost += cost

        return {
            "campaign_id": campaign_id,
            "by_channel": breakdown,
            "total_cost": total_cost
        }

    def get_spending_trends(self, tenant_id: str, days: int = 30) -> Dict[str, Any]:
        """Get spending trends over time"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        sends = list(self.sends_collection.find({
            "tenant_id": tenant_id,
            "created_at": {"$gte": cutoff_date}
        }).sort("created_at", 1))

        daily_spending = {}
        for send in sends:
            date = send.get("created_at").date()
            date_str = date.isoformat()
            
            if date_str not in daily_spending:
                daily_spending[date_str] = 0
            daily_spending[date_str] += send.get("cost", 0)

        return {
            "period_days": days,
            "daily_spending": daily_spending,
            "total_spending": sum(daily_spending.values())
        }
