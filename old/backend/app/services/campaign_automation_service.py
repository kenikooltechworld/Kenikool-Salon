"""
Campaign Automation Service - Automated marketing campaigns
"""
from datetime import datetime, timedelta
from typing import List, Dict
import logging

from app.database import Database
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class CampaignAutomationService:
    """Service for automated marketing campaigns"""
    
    @staticmethod
    def check_birthday_campaigns(tenant_id: str) -> List[Dict]:
        """
        Check for clients with birthdays and send birthday campaigns
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            List of sent campaigns
        """
        db = Database.get_db()
        today = datetime.utcnow()
        
        # Get clients with birthdays today
        clients = list(db.clients.find({
            "tenant_id": tenant_id,
            "$expr": {
                "$and": [
                    {"$eq": [{"$dayOfMonth": "$date_of_birth"}, today.day]},
                    {"$eq": [{"$month": "$date_of_birth"}, today.month]}
                ]
            }
        }))
        
        sent_campaigns = []
        
        for client in clients:
            # Check if birthday campaign already sent this year
            existing_campaign = db.campaign_sends.find_one({
                "tenant_id": tenant_id,
                "client_id": str(client["_id"]),
                "campaign_type": "birthday",
                "sent_at": {
                    "$gte": datetime(today.year, 1, 1),
                    "$lte": datetime(today.year, 12, 31)
                }
            })
            
            if existing_campaign:
                continue
            
            # Get tenant info for personalization
            tenant = db.tenants.find_one({"_id": tenant_id})
            
            # Create birthday message
            message = f"Happy Birthday {client['name']}! 🎉 Celebrate with us! Get 20% off your next visit at {tenant.get('salon_name', 'our salon')}. Book now!"
            
            # Send SMS
            try:
                NotificationService.send_sms(
                    tenant_id=tenant_id,
                    phone=client["phone"],
                    message=message
                )
                
                # Record campaign send
                campaign_send = {
                    "tenant_id": tenant_id,
                    "client_id": str(client["_id"]),
                    "campaign_type": "birthday",
                    "message": message,
                    "channel": "sms",
                    "sent_at": datetime.utcnow(),
                    "status": "sent"
                }
                
                db.campaign_sends.insert_one(campaign_send)
                sent_campaigns.append(campaign_send)
                
                logger.info(f"Sent birthday campaign to client: {client['name']}")
                
            except Exception as e:
                logger.error(f"Failed to send birthday campaign: {e}")
        
        return sent_campaigns
    
    @staticmethod
    def check_winback_campaigns(tenant_id: str, days_inactive: int = 90) -> List[Dict]:
        """
        Check for inactive clients and send win-back campaigns
        
        Args:
            tenant_id: Tenant ID
            days_inactive: Number of days of inactivity to trigger campaign
            
        Returns:
            List of sent campaigns
        """
        db = Database.get_db()
        cutoff_date = datetime.utcnow() - timedelta(days=days_inactive)
        
        # Get clients who haven't visited in X days
        clients = list(db.clients.find({
            "tenant_id": tenant_id,
            "last_visit_date": {"$lt": cutoff_date}
        }))
        
        sent_campaigns = []
        
        for client in clients:
            # Check if win-back campaign already sent in last 30 days
            existing_campaign = db.campaign_sends.find_one({
                "tenant_id": tenant_id,
                "client_id": str(client["_id"]),
                "campaign_type": "winback",
                "sent_at": {"$gte": datetime.utcnow() - timedelta(days=30)}
            })
            
            if existing_campaign:
                continue
            
            # Get tenant info
            tenant = db.tenants.find_one({"_id": tenant_id})
            
            # Create win-back message
            message = f"We miss you {client['name']}! 💇 It's been a while since your last visit. Come back and enjoy 15% off at {tenant.get('salon_name', 'our salon')}!"
            
            # Send SMS
            try:
                NotificationService.send_sms(
                    tenant_id=tenant_id,
                    phone=client["phone"],
                    message=message
                )
                
                # Record campaign send
                campaign_send = {
                    "tenant_id": tenant_id,
                    "client_id": str(client["_id"]),
                    "campaign_type": "winback",
                    "message": message,
                    "channel": "sms",
                    "sent_at": datetime.utcnow(),
                    "status": "sent",
                    "days_inactive": days_inactive
                }
                
                db.campaign_sends.insert_one(campaign_send)
                sent_campaigns.append(campaign_send)
                
                logger.info(f"Sent win-back campaign to client: {client['name']}")
                
            except Exception as e:
                logger.error(f"Failed to send win-back campaign: {e}")
        
        return sent_campaigns
    
    @staticmethod
    def get_campaign_stats(tenant_id: str, campaign_type: str = None) -> Dict:
        """
        Get statistics for automated campaigns
        
        Args:
            tenant_id: Tenant ID
            campaign_type: Optional campaign type filter
            
        Returns:
            Dict with campaign statistics
        """
        db = Database.get_db()
        
        query = {"tenant_id": tenant_id}
        if campaign_type:
            query["campaign_type"] = campaign_type
        
        total_sent = db.campaign_sends.count_documents(query)
        
        # Get sent by type
        pipeline = [
            {"$match": {"tenant_id": tenant_id}},
            {"$group": {
                "_id": "$campaign_type",
                "count": {"$sum": 1}
            }}
        ]
        
        by_type = {item["_id"]: item["count"] for item in db.campaign_sends.aggregate(pipeline)}
        
        return {
            "total_sent": total_sent,
            "by_type": by_type,
            "birthday_campaigns": by_type.get("birthday", 0),
            "winback_campaigns": by_type.get("winback", 0)
        }
