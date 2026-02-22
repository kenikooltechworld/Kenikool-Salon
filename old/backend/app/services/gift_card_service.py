"""
Gift card service for managing gift cards
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from pymongo.database import Database as PyMongoDatabase
from bson import ObjectId


class GiftCardService:
    """Service for managing gift cards"""
    
    def __init__(self, db: PyMongoDatabase):
        self.db = db
        self.gift_cards = db.gift_cards
        self.gift_card_transactions = db.gift_card_transactions
        self.clients = db.clients
    
    async def validate_gift_card(
        self,
        tenant_id: str,
        code: str,
        amount_to_use: Optional[float] = None
    ) -> Dict:
        """Validate gift card for redemption"""
        # Find gift card
        gift_card = await self.gift_cards.find_one({
            "tenant_id": tenant_id,
            "code": code.upper().replace(" ", "")
        })
        
        if not gift_card:
            return {
                "valid": False,
                "error": "Gift card not found"
            }
        
        # Check status
        if gift_card["status"] != "active":
            return {
                "valid": False,
                "error": f"Gift card is {gift_card['status']}"
            }
        
        # Check expiry
        if gift_card.get("expiry_date"):
            if datetime.utcnow() > gift_card["expiry_date"]:
                # Mark as expired
                await self.gift_cards.update_one(
                    {"_id": gift_card["_id"]},
                    {"$set": {"status": "expired", "updated_at": datetime.utcnow()}}
                )
                return {
                    "valid": False,
                    "error": "Gift card has expired"
                }
        
        # Check balance
        current_balance = gift_card["current_balance"]
        if current_balance <= 0:
            # Mark as redeemed
            await self.gift_cards.update_one(
                {"_id": gift_card["_id"]},
                {"$set": {"status": "redeemed", "updated_at": datetime.utcnow()}}
            )
            return {
                "valid": False,
                "error": "Gift card has no remaining balance"
            }
        
        # Check if amount exceeds balance
        if amount_to_use and amount_to_use > current_balance:
            return {
                "valid": False,
                "error": f"Insufficient balance. Available: ₦{current_balance:,.2f}"
            }
        
        return {
            "valid": True,
            "gift_card_id": str(gift_card["_id"]),
            "current_balance": current_balance,
            "recipient_name": gift_card["recipient_name"]
        }
    
    async def redeem_gift_card(
        self,
        tenant_id: str,
        code: str,
        amount_to_use: float,
        booking_id: Optional[str] = None,
        redeemed_by_client_id: Optional[str] = None
    ) -> Dict:
        """Redeem gift card for a booking or service"""
        # Validate first
        validation = await self.validate_gift_card(tenant_id, code, amount_to_use)
        
        if not validation["valid"]:
            return {
                "success": False,
                "error": validation["error"]
            }
        
        gift_card_id = validation["gift_card_id"]
        gift_card = await self.gift_cards.find_one({"_id": ObjectId(gift_card_id)})
        
        balance_before = gift_card["current_balance"]
        balance_after = balance_before - amount_to_use
        
        # Get redeemer details
        redeemed_by_name = None
        if redeemed_by_client_id:
            client = await self.clients.find_one({"_id": ObjectId(redeemed_by_client_id)})
            if client is not None:
                redeemed_by_name = client["name"]
        
        # Create transaction record
        transaction_data = {
            "tenant_id": tenant_id,
            "gift_card_id": gift_card_id,
            "booking_id": booking_id,
            "amount_used": amount_to_use,
            "balance_before": balance_before,
            "balance_after": balance_after,
            "redeemed_by_client_id": redeemed_by_client_id,
            "redeemed_by_name": redeemed_by_name,
            "transaction_date": datetime.utcnow()
        }
        
        transaction_result = await self.gift_card_transactions.insert_one(transaction_data)
        
        # Update gift card
        update_data = {
            "current_balance": balance_after,
            "last_redemption_date": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Set first redemption date if this is the first use
        if gift_card.get("redemption_count", 0) == 0:
            update_data["first_redemption_date"] = datetime.utcnow()
        
        # Mark as redeemed if balance is zero
        if balance_after <= 0:
            update_data["status"] = "redeemed"
        
        await self.gift_cards.update_one(
            {"_id": ObjectId(gift_card_id)},
            {
                "$set": update_data,
                "$inc": {"redemption_count": 1}
            }
        )
        
        return {
            "success": True,
            "transaction_id": str(transaction_result.inserted_id),
            "amount_used": amount_to_use,
            "remaining_balance": balance_after
        }
    
    async def get_gift_card_balance(
        self,
        tenant_id: str,
        code: str
    ) -> Dict:
        """Get gift card balance"""
        gift_card = await self.gift_cards.find_one({
            "tenant_id": tenant_id,
            "code": code.upper().replace(" ", "")
        })
        
        if not gift_card:
            return {
                "found": False,
                "error": "Gift card not found"
            }
        
        return {
            "found": True,
            "code": gift_card["code"],
            "current_balance": gift_card["current_balance"],
            "initial_amount": gift_card["initial_amount"],
            "status": gift_card["status"],
            "recipient_name": gift_card["recipient_name"],
            "expiry_date": gift_card.get("expiry_date"),
            "redemption_count": gift_card.get("redemption_count", 0)
        }
    
    async def get_gift_card_transactions(
        self,
        tenant_id: str,
        gift_card_id: str
    ) -> List[Dict]:
        """Get transaction history for a gift card"""
        transactions = await self.gift_card_transactions.find({
            "tenant_id": tenant_id,
            "gift_card_id": gift_card_id
        }).sort("transaction_date", -1).to_list(length=None)
        
        return transactions
    
    async def cancel_gift_card(
        self,
        tenant_id: str,
        gift_card_id: str,
        refund: bool = False
    ) -> Dict:
        """Cancel a gift card"""
        gift_card = await self.gift_cards.find_one({
            "_id": ObjectId(gift_card_id),
            "tenant_id": tenant_id
        })
        
        if not gift_card:
            return {"success": False, "error": "Gift card not found"}
        
        if gift_card["status"] == "cancelled":
            return {"success": False, "error": "Gift card already cancelled"}
        
        update_data = {
            "status": "cancelled",
            "updated_at": datetime.utcnow()
        }
        
        if refund:
            # Set balance to 0 if refunding
            update_data["current_balance"] = 0
        
        await self.gift_cards.update_one(
            {"_id": ObjectId(gift_card_id)},
            {"$set": update_data}
        )
        
        return {
            "success": True,
            "message": "Gift card cancelled successfully",
            "refunded": refund
        }
    
    async def get_gift_card_analytics(self, tenant_id: str) -> Dict:
        """Get gift card analytics for tenant"""
        pipeline = [
            {"$match": {"tenant_id": tenant_id}},
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1},
                    "total_initial_amount": {"$sum": "$initial_amount"},
                    "total_current_balance": {"$sum": "$current_balance"}
                }
            }
        ]
        
        results = await self.gift_cards.aggregate(pipeline).to_list(length=None)
        
        analytics = {
            "total_gift_cards": 0,
            "total_sold": 0,
            "total_redeemed_value": 0,
            "total_outstanding_balance": 0,
            "by_status": {}
        }
        
        for result in results:
            status = result["_id"]
            count = result["count"]
            initial = result.get("total_initial_amount", 0)
            balance = result.get("total_current_balance", 0)
            
            analytics["total_gift_cards"] += count
            analytics["total_sold"] += initial
            analytics["total_outstanding_balance"] += balance
            
            analytics["by_status"][status] = {
                "count": count,
                "total_initial": initial,
                "total_balance": balance
            }
        
        analytics["total_redeemed_value"] = analytics["total_sold"] - analytics["total_outstanding_balance"]
        
        return analytics
