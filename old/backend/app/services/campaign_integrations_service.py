"""
Campaign System Integrations Service
Integrates campaigns with loyalty, promo codes, bookings, and gift cards
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from bson import ObjectId
from pymongo import ASCENDING
from app.database import db
import uuid


class CampaignIntegrationsService:
    """Service for integrating campaigns with other systems"""

    def __init__(self):
        self.campaigns_collection = db.campaigns
        self.campaign_sends_collection = db.campaign_sends
        self._ensure_indexes()

    def _ensure_indexes(self):
        """Create necessary indexes"""
        self.campaigns_collection.create_index([("tenant_id", ASCENDING)])
        self.campaign_sends_collection.create_index([("campaign_id", ASCENDING)])
        self.campaign_sends_collection.create_index([("booking_id", ASCENDING)])
        self.campaign_sends_collection.create_index([("transaction_id", ASCENDING)])

    # Loyalty System Integration
    async def filter_by_loyalty_tier(
        self,
        client_ids: List[str],
        tenant_id: str,
        loyalty_tiers: List[str]
    ) -> List[str]:
        """Filter clients by loyalty tier"""
        try:
            clients_collection = db.clients
            
            matching_clients = await clients_collection.find({
                "_id": {"$in": [ObjectId(cid) if ObjectId.is_valid(cid) else cid for cid in client_ids]},
                "tenant_id": tenant_id,
                "loyalty_tier": {"$in": loyalty_tiers}
            }).to_list(None)
            
            return [str(c["_id"]) for c in matching_clients]
        except:
            return client_ids

    async def get_loyalty_tier_stats(
        self,
        tenant_id: str
    ) -> Dict[str, int]:
        """Get count of clients by loyalty tier"""
        try:
            clients_collection = db.clients
            
            pipeline = [
                {"$match": {"tenant_id": tenant_id}},
                {
                    "$group": {
                        "_id": "$loyalty_tier",
                        "count": {"$sum": 1}
                    }
                }
            ]
            
            result = await clients_collection.aggregate(pipeline).to_list(None)
            return {r["_id"]: r["count"] for r in result}
        except:
            return {}

    # Promo Code Integration
    async def generate_promo_codes(
        self,
        campaign_id: str,
        tenant_id: str,
        client_ids: List[str],
        discount_percentage: float,
        discount_amount: Optional[float] = None,
        expiry_days: int = 30
    ) -> Dict[str, str]:
        """Generate unique promo codes for campaign recipients"""
        try:
            promo_codes_collection = db.promo_codes
            codes_map = {}
            
            for client_id in client_ids:
                # Generate unique code
                code = f"CAMP{campaign_id[:8]}{client_id[:8]}{uuid.uuid4().hex[:6]}".upper()
                
                promo_code = {
                    "code": code,
                    "campaign_id": campaign_id,
                    "client_id": client_id,
                    "tenant_id": tenant_id,
                    "discount_percentage": discount_percentage,
                    "discount_amount": discount_amount,
                    "created_at": datetime.utcnow(),
                    "expires_at": datetime.utcnow() + __import__('datetime').timedelta(days=expiry_days),
                    "used": False,
                    "used_at": None
                }
                
                await promo_codes_collection.insert_one(promo_code)
                codes_map[client_id] = code
            
            return codes_map
        except:
            return {}

    async def track_promo_code_usage(
        self,
        campaign_id: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        """Track promo code usage from campaign"""
        try:
            promo_codes_collection = db.promo_codes
            
            pipeline = [
                {
                    "$match": {
                        "campaign_id": campaign_id,
                        "tenant_id": tenant_id
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_codes": {"$sum": 1},
                        "used_codes": {
                            "$sum": {"$cond": ["$used", 1, 0]}
                        },
                        "total_discount": {
                            "$sum": {"$cond": ["$used", "$discount_percentage", 0]}
                        }
                    }
                }
            ]
            
            result = await promo_codes_collection.aggregate(pipeline).to_list(1)
            if result:
                return result[0]
            return {"total_codes": 0, "used_codes": 0, "total_discount": 0}
        except:
            return {}

    # Booking System Integration
    async def generate_booking_urls(
        self,
        campaign_id: str,
        tenant_id: str,
        client_ids: List[str],
        service_id: Optional[str] = None
    ) -> Dict[str, str]:
        """Generate personalized booking URLs for campaign recipients"""
        try:
            booking_urls = {}
            
            for client_id in client_ids:
                # Generate tracking token
                token = str(uuid.uuid4())
                
                # Store tracking info
                await db.campaign_booking_links.insert_one({
                    "token": token,
                    "campaign_id": campaign_id,
                    "client_id": client_id,
                    "tenant_id": tenant_id,
                    "service_id": service_id,
                    "created_at": datetime.utcnow()
                })
                
                # Build URL (would be actual booking URL in production)
                url = f"/booking?campaign={token}&client={client_id}"
                booking_urls[client_id] = url
            
            return booking_urls
        except:
            return {}

    async def attribute_booking_to_campaign(
        self,
        booking_id: str,
        campaign_id: str,
        client_id: str,
        tenant_id: str
    ) -> bool:
        """Attribute a booking to a campaign"""
        try:
            # Find campaign send record
            send = await self.campaign_sends_collection.find_one({
                "campaign_id": campaign_id,
                "client_id": client_id,
                "tenant_id": tenant_id
            })
            
            if send:
                # Update send record with booking
                await self.campaign_sends_collection.update_one(
                    {"_id": send["_id"]},
                    {
                        "$set": {
                            "booking_id": booking_id,
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
                
                # Update campaign metrics
                await self.campaigns_collection.update_one(
                    {"_id": ObjectId(campaign_id)},
                    {
                        "$inc": {"conversions": 1},
                        "$set": {"updated_at": datetime.utcnow()}
                    }
                )
                
                return True
            return False
        except:
            return False

    async def get_campaign_booking_stats(
        self,
        campaign_id: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        """Get booking statistics for a campaign"""
        try:
            pipeline = [
                {
                    "$match": {
                        "campaign_id": campaign_id,
                        "tenant_id": tenant_id,
                        "booking_id": {"$exists": True, "$ne": None}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_bookings": {"$sum": 1},
                        "total_revenue": {"$sum": "$revenue_attributed"}
                    }
                }
            ]
            
            result = await self.campaign_sends_collection.aggregate(pipeline).to_list(1)
            if result:
                return result[0]
            return {"total_bookings": 0, "total_revenue": 0}
        except:
            return {}

    # Gift Card Integration
    async def include_gift_cards(
        self,
        campaign_id: str,
        tenant_id: str,
        client_ids: List[str],
        gift_card_amount: float
    ) -> Dict[str, str]:
        """Generate gift card codes for campaign recipients"""
        try:
            gift_cards_collection = db.gift_cards
            gift_card_map = {}
            
            for client_id in client_ids:
                # Generate gift card code
                code = f"GC{campaign_id[:6]}{uuid.uuid4().hex[:10]}".upper()
                
                gift_card = {
                    "code": code,
                    "campaign_id": campaign_id,
                    "client_id": client_id,
                    "tenant_id": tenant_id,
                    "amount": gift_card_amount,
                    "balance": gift_card_amount,
                    "created_at": datetime.utcnow(),
                    "expires_at": datetime.utcnow() + __import__('datetime').timedelta(days=365),
                    "redeemed": False,
                    "redeemed_at": None
                }
                
                await gift_cards_collection.insert_one(gift_card)
                gift_card_map[client_id] = code
            
            return gift_card_map
        except:
            return {}

    async def track_gift_card_redemptions(
        self,
        campaign_id: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        """Track gift card redemptions from campaign"""
        try:
            gift_cards_collection = db.gift_cards
            
            pipeline = [
                {
                    "$match": {
                        "campaign_id": campaign_id,
                        "tenant_id": tenant_id
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_cards": {"$sum": 1},
                        "redeemed_cards": {
                            "$sum": {"$cond": ["$redeemed", 1, 0]}
                        },
                        "total_value": {"$sum": "$amount"},
                        "redeemed_value": {
                            "$sum": {"$cond": ["$redeemed", "$amount", 0]}
                        }
                    }
                }
            ]
            
            result = await gift_cards_collection.aggregate(pipeline).to_list(1)
            if result:
                return result[0]
            return {"total_cards": 0, "redeemed_cards": 0, "total_value": 0, "redeemed_value": 0}
        except:
            return {}

    # ROI Calculation
    async def calculate_campaign_roi(
        self,
        campaign_id: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        """Calculate ROI for a campaign including all integrations"""
        try:
            campaign = await self.campaigns_collection.find_one({
                "_id": ObjectId(campaign_id),
                "tenant_id": tenant_id
            })
            
            if not campaign:
                return {}
            
            # Get costs
            total_cost = campaign.get("actual_cost", 0)
            
            # Get booking revenue
            booking_stats = await self.get_campaign_booking_stats(campaign_id, tenant_id)
            booking_revenue = booking_stats.get("total_revenue", 0)
            
            # Get promo code usage
            promo_stats = await self.track_promo_code_usage(campaign_id, tenant_id)
            
            # Get gift card redemptions
            gift_card_stats = await self.track_gift_card_redemptions(campaign_id, tenant_id)
            gift_card_revenue = gift_card_stats.get("redeemed_value", 0)
            
            # Calculate total revenue
            total_revenue = booking_revenue + gift_card_revenue
            
            # Calculate ROI
            roi = ((total_revenue - total_cost) / total_cost * 100) if total_cost > 0 else 0
            
            return {
                "total_cost": total_cost,
                "total_revenue": total_revenue,
                "roi_percentage": roi,
                "booking_revenue": booking_revenue,
                "gift_card_revenue": gift_card_revenue,
                "promo_codes_used": promo_stats.get("used_codes", 0),
                "bookings_attributed": booking_stats.get("total_bookings", 0),
                "gift_cards_redeemed": gift_card_stats.get("redeemed_cards", 0)
            }
        except:
            return {}


# Singleton instance
campaign_integrations_service = CampaignIntegrationsService()
