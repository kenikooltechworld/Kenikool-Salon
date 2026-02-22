"""
Campaign Service - Manages campaign creation, sending, and analytics
"""
from datetime import datetime
from typing import Dict, List, Optional
from bson import ObjectId
import logging

from app.database import Database
from app.services.sms_credit_service import SMSCreditService
from app.services.termii_service import send_sms, send_whatsapp
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class CampaignService:
    """Service for managing campaigns"""
    
    SUPPORTED_CHANNELS = ["sms", "whatsapp", "email"]
    CAMPAIGN_TYPES = ["birthday", "seasonal", "custom", "win_back"]
    
    @staticmethod
    def _get_db():
        """Get database instance"""
        return Database.get_db()
    
    @staticmethod
    def create_campaign(
        tenant_id: str,
        name: str,
        campaign_type: str,
        message_template: str,
        channels: List[str],
        target_segment: Optional[Dict] = None,
        discount_code: Optional[str] = None,
        discount_value: Optional[float] = None,
        scheduled_at: Optional[str] = None,
        auto_send: bool = False
    ) -> Dict:
        """
        Create a new campaign
        
        Args:
            tenant_id: Tenant ID
            name: Campaign name
            campaign_type: Type of campaign (birthday, seasonal, custom, win_back)
            message_template: Message template with variables
            channels: List of channels (sms, whatsapp, email)
            target_segment: Optional segment criteria
            discount_code: Optional discount code
            discount_value: Optional discount value
            scheduled_at: Optional scheduled send time
            auto_send: Whether to auto-send
            
        Returns:
            Campaign record
        """
        db = CampaignService._get_db()
        
        # Validate inputs
        if campaign_type not in CampaignService.CAMPAIGN_TYPES:
            raise ValueError(f"Invalid campaign type: {campaign_type}")
        
        for channel in channels:
            if channel not in CampaignService.SUPPORTED_CHANNELS:
                raise ValueError(f"Invalid channel: {channel}")
        
        campaign = {
            "tenant_id": tenant_id,
            "name": name,
            "campaign_type": campaign_type,
            "message_template": message_template,
            "channels": channels,
            "target_segment": target_segment or {},
            "discount_code": discount_code,
            "discount_value": discount_value,
            "scheduled_at": scheduled_at,
            "auto_send": auto_send,
            "status": "draft",
            "sent_at": None,
            "recipients_count": 0,
            "delivered_count": 0,
            "failed_count": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.campaigns.insert_one(campaign)
        campaign["_id"] = str(result.inserted_id)
        
        logger.info(f"Created campaign {name} for tenant {tenant_id}")
        
        return CampaignService._format_campaign(campaign)
    
    @staticmethod
    def get_campaign(campaign_id: str, tenant_id: str) -> Dict:
        """
        Get campaign by ID
        
        Args:
            campaign_id: Campaign ID
            tenant_id: Tenant ID
            
        Returns:
            Campaign record
        """
        db = CampaignService._get_db()
        
        try:
            campaign = db.campaigns.find_one({
                "_id": ObjectId(campaign_id),
                "tenant_id": tenant_id
            })
        except Exception:
            raise ValueError(f"Invalid campaign ID: {campaign_id}")
        
        if not campaign:
            raise ValueError("Campaign not found")
        
        return CampaignService._format_campaign(campaign)
    
    @staticmethod
    def list_campaigns(
        tenant_id: str,
        status: Optional[str] = None,
        campaign_type: Optional[str] = None,
        offset: int = 0,
        limit: int = 20
    ) -> List[Dict]:
        """
        List campaigns for tenant
        
        Args:
            tenant_id: Tenant ID
            status: Optional status filter
            campaign_type: Optional type filter
            offset: Pagination offset
            limit: Pagination limit
            
        Returns:
            List of campaigns
        """
        db = CampaignService._get_db()
        
        query = {"tenant_id": tenant_id}
        
        if status:
            query["status"] = status
        if campaign_type:
            query["campaign_type"] = campaign_type
        
        campaigns = list(
            db.campaigns.find(query)
            .sort("created_at", -1)
            .skip(offset)
            .limit(limit)
        )
        
        return [CampaignService._format_campaign(c) for c in campaigns]
    
    @staticmethod
    async def send_campaign(
        campaign_id: str,
        tenant_id: str,
        send_immediately: bool = True
    ) -> Dict:
        """
        Send campaign to target segment
        
        Args:
            campaign_id: Campaign ID
            tenant_id: Tenant ID
            send_immediately: Whether to send immediately or schedule
            
        Returns:
            Campaign send result
        """
        db = CampaignService._get_db()
        
        # Get campaign
        try:
            campaign = db.campaigns.find_one({
                "_id": ObjectId(campaign_id),
                "tenant_id": tenant_id
            })
        except Exception:
            raise ValueError(f"Invalid campaign ID: {campaign_id}")
        
        if not campaign:
            raise ValueError("Campaign not found")
        
        if campaign["status"] != "draft":
            raise ValueError(f"Cannot send campaign with status: {campaign['status']}")
        
        # Get target clients
        clients = CampaignService._get_target_clients(tenant_id, campaign.get("target_segment", {}))
        
        if not clients:
            raise ValueError("No clients match the target segment")
        
        # Calculate SMS credits needed
        sms_channels = [c for c in campaign["channels"] if c in ["sms", "whatsapp"]]
        sms_credits_needed = len(clients) * len(sms_channels)
        
        # Check SMS credits
        if sms_channels and not SMSCreditService.check_sufficient_credits(tenant_id, sms_credits_needed):
            raise ValueError(
                f"Insufficient SMS credits. Required: {sms_credits_needed}, "
                f"Available: {SMSCreditService.get_balance(tenant_id)['current_balance']}"
            )
        
        # Send campaign
        results = {
            "campaign_id": campaign_id,
            "total_recipients": len(clients),
            "sent": 0,
            "failed": 0,
            "failures": [],
            "sms_credits_used": 0
        }
        
        for client in clients:
            try:
                # Send via each channel
                for channel in campaign["channels"]:
                    if channel == "sms":
                        message = CampaignService._render_template(campaign["message_template"], client, tenant_id)
                        await send_sms(client.get("phone", ""), message)
                    elif channel == "whatsapp":
                        message = CampaignService._render_template(campaign["message_template"], client, tenant_id)
                        await send_whatsapp(client.get("phone", ""), message)
                
                results["sent"] += 1
                
                # Deduct SMS credits for SMS/WhatsApp channels
                if sms_channels:
                    SMSCreditService.deduct_credits(
                        tenant_id,
                        len(sms_channels),
                        "campaign_send",
                        campaign_id=campaign_id,
                        reference_id=str(client.get("_id", ""))
                    )
                    results["sms_credits_used"] += len(sms_channels)
                    
            except Exception as e:
                logger.error(f"Error sending campaign to client {client.get('_id')}: {e}")
                results["failed"] += 1
                results["failures"].append({
                    "client_id": str(client.get("_id", "")),
                    "error": str(e)
                })
        
        # Update campaign status
        db.campaigns.update_one(
            {"_id": ObjectId(campaign_id)},
            {
                "$set": {
                    "status": "sent",
                    "sent_at": datetime.utcnow(),
                    "recipients_count": len(clients),
                    "delivered_count": results["sent"],
                    "failed_count": results["failed"],
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"Campaign {campaign_id} sent to {results['sent']} clients, {results['failed']} failed")
        
        return results
    
    @staticmethod
    def _render_template(template: str, client: Dict, tenant_id: str) -> str:
        """
        Render template with client data
        
        Args:
            template: Message template
            client: Client record
            tenant_id: Tenant ID
            
        Returns:
            Rendered message
        """
        db = CampaignService._get_db()
        
        # Get tenant info
        tenant = db.tenants.find_one({"_id": ObjectId(tenant_id)})
        salon_name = tenant.get("business_name", "Our Salon") if tenant else "Our Salon"
        
        # Build variables
        variables = {
            "client_name": client.get("name", ""),
            "salon_name": salon_name,
            "client_email": client.get("email", ""),
            "client_phone": client.get("phone", "")
        }
        
        # Replace variables
        message = template
        for var_name, var_value in variables.items():
            placeholder = f"{{{{{var_name}}}}}"
            message = message.replace(placeholder, str(var_value))
        
        return message
    
    @staticmethod
    def _get_target_clients(tenant_id: str, segment: Dict) -> List[Dict]:
        """
        Get clients matching target segment
        
        Args:
            tenant_id: Tenant ID
            segment: Segment criteria
            
        Returns:
            List of matching clients
        """
        db = CampaignService._get_db()
        
        query = {"tenant_id": tenant_id}
        
        # Apply segment filters
        if segment.get("location"):
            query["location"] = segment["location"]
        if segment.get("loyalty_tier"):
            query["loyalty_tier"] = segment["loyalty_tier"]
        if segment.get("min_visits"):
            query["total_visits"] = {"$gte": segment["min_visits"]}
        
        clients = list(db.clients.find(query).limit(1000))
        
        return clients
    
    @staticmethod
    def get_campaign_analytics(campaign_id: str, tenant_id: str) -> Dict:
        """
        Get campaign analytics
        
        Args:
            campaign_id: Campaign ID
            tenant_id: Tenant ID
            
        Returns:
            Campaign analytics
        """
        campaign = CampaignService.get_campaign(campaign_id, tenant_id)
        
        # Get SMS credits used
        db = CampaignService._get_db()
        transactions = list(
            db.sms_credit_transactions.find({
                "tenant_id": tenant_id,
                "campaign_id": campaign_id
            })
        )
        
        sms_credits_used = sum(tx.get("amount", 0) for tx in transactions)
        
        return {
            "campaign_id": campaign_id,
            "name": campaign["name"],
            "status": campaign["status"],
            "total_recipients": campaign["recipients_count"],
            "delivered": campaign["delivered_count"],
            "failed": campaign["failed_count"],
            "delivery_rate": (
                campaign["delivered_count"] / campaign["recipients_count"] * 100
                if campaign["recipients_count"] > 0 else 0
            ),
            "sms_credits_used": sms_credits_used,
            "channels": campaign["channels"],
            "sent_at": campaign["sent_at"].isoformat() if campaign["sent_at"] else None
        }
    
    @staticmethod
    def _format_campaign(campaign: Dict) -> Dict:
        """Format campaign for response"""
        return {
            **campaign,
            "_id": str(campaign["_id"]),
            "created_at": campaign["created_at"].isoformat(),
            "updated_at": campaign["updated_at"].isoformat(),
            "sent_at": campaign["sent_at"].isoformat() if campaign.get("sent_at") else None
        }


# Create singleton instance
campaign_service = CampaignService()
