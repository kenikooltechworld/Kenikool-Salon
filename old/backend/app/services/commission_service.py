"""Commission service for marketplace"""
from datetime import datetime
from typing import Dict, List, Optional
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class CommissionService:
    """Service for commission management"""
    
    def __init__(self, db):
        self.db = db
    
    async def record_commission(
        self,
        tenant_id: str,
        booking_id: str,
        booking_reference: str,
        amount: float,
        commission_rate: float
    ) -> Dict:
        """Record a commission transaction"""
        try:
            commission_amount = amount * commission_rate
            platform_fee = amount * 0.02  # 2% platform fee
            net_amount = commission_amount - platform_fee
            
            transaction_data = {
                "tenant_id": tenant_id,
                "booking_id": booking_id,
                "booking_reference": booking_reference,
                "amount": amount,
                "commission_rate": commission_rate,
                "commission_amount": commission_amount,
                "platform_fee": platform_fee,
                "net_amount": net_amount,
                "transaction_type": "booking",
                "status": "pending",
                "payment_date": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = self.db.commission_transactions.insert_one(transaction_data)
            transaction_data["_id"] = str(result.inserted_id)
            
            return transaction_data
        
        except Exception as e:
            logger.error(f"Error recording commission: {e}")
            raise Exception(f"Failed to record commission: {str(e)}")
    
    async def split_payment(
        self,
        booking_id: str,
        total_amount: float,
        commission_rate: float
    ) -> Dict:
        """Calculate payment split"""
        try:
            commission_amount = total_amount * commission_rate
            platform_fee = total_amount * 0.02
            salon_amount = total_amount - commission_amount - platform_fee
            
            return {
                "total_amount": total_amount,
                "commission_amount": commission_amount,
                "platform_fee": platform_fee,
                "salon_amount": salon_amount,
                "commission_rate": commission_rate
            }
        
        except Exception as e:
            logger.error(f"Error splitting payment: {e}")
            raise Exception(f"Failed to split payment: {str(e)}")
    
    async def get_dashboard_metrics(
        self,
        tenant_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict:
        """Get commission dashboard metrics"""
        try:
            query = {"tenant_id": tenant_id}
            
            if start_date and end_date:
                query["created_at"] = {
                    "$gte": datetime.fromisoformat(start_date),
                    "$lte": datetime.fromisoformat(end_date)
                }
            
            transactions = list(self.db.commission_transactions.find(query))
            
            total_commission = sum(t.get("commission_amount", 0) for t in transactions)
            total_platform_fee = sum(t.get("platform_fee", 0) for t in transactions)
            total_net = sum(t.get("net_amount", 0) for t in transactions)
            transaction_count = len(transactions)
            
            pending_transactions = [t for t in transactions if t.get("status") == "pending"]
            completed_transactions = [t for t in transactions if t.get("status") == "completed"]
            
            return {
                "total_commission": total_commission,
                "total_platform_fee": total_platform_fee,
                "total_net": total_net,
                "transaction_count": transaction_count,
                "pending_count": len(pending_transactions),
                "completed_count": len(completed_transactions),
                "average_commission": total_commission / transaction_count if transaction_count > 0 else 0
            }
        
        except Exception as e:
            logger.error(f"Error getting dashboard metrics: {e}")
            raise Exception(f"Failed to get metrics: {str(e)}")
    
    async def get_transactions(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> Dict:
        """Get commission transactions"""
        try:
            query = {"tenant_id": tenant_id}
            
            total = self.db.commission_transactions.count_documents(query)
            transactions = list(
                self.db.commission_transactions.find(query)
                .sort("created_at", -1)
                .skip(skip)
                .limit(limit)
            )
            
            for t in transactions:
                t["_id"] = str(t["_id"])
            
            return {
                "transactions": transactions,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        
        except Exception as e:
            logger.error(f"Error getting transactions: {e}")
            raise Exception(f"Failed to get transactions: {str(e)}")
    
    async def update_commission_rate(
        self,
        tenant_id: str,
        new_rate: float
    ) -> Dict:
        """Update commission rate for tenant"""
        try:
            if new_rate < 0 or new_rate > 1:
                raise ValueError("Commission rate must be between 0 and 1")
            
            settings = self.db.marketplace_settings.find_one({"tenant_id": tenant_id})
            
            if settings:
                self.db.marketplace_settings.update_one(
                    {"_id": settings["_id"]},
                    {
                        "$set": {
                            "commission_rate": new_rate,
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
            else:
                self.db.marketplace_settings.insert_one({
                    "tenant_id": tenant_id,
                    "commission_rate": new_rate,
                    "online_payment_discount": 0.05,
                    "is_marketplace_enabled": True,
                    "allow_guest_bookings": True,
                    "magic_link_expiry_hours": 24,
                    "auto_confirm_bookings": False,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                })
            
            return {"commission_rate": new_rate}
        
        except Exception as e:
            logger.error(f"Error updating commission rate: {e}")
            raise Exception(f"Failed to update commission rate: {str(e)}")
