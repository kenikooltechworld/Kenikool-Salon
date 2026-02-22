"""
Membership REST service - Business logic for membership management
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class MembershipRestService:
    """Service layer for membership management"""
    
    def __init__(self, db):
        self.db = db
    
    async def get_plans(
        self,
        tenant_id: str,
        is_active: Optional[bool] = None
    ) -> Dict:
        """Get list of membership plans"""
        try:
            query = {"tenant_id": tenant_id}
            
            if is_active is not None:
                query["is_active"] = is_active
            
            total = self.db.membership_plans.count_documents(query)
            cursor = self.db.membership_plans.find(query).sort("created_at", -1)
            plans = list(cursor)
            
            for plan in plans:
                plan["_id"] = str(plan["_id"])
            
            return {"plans": plans, "total": total}
        
        except Exception as e:
            logger.error(f"Error getting membership plans: {e}")
            raise Exception(f"Failed to get membership plans: {str(e)}")
    
    async def create_plan(
        self,
        tenant_id: str,
        name: str,
        description: Optional[str],
        price: float,
        billing_cycle: str,
        discount_percentage: float,
        benefits: List[str],
        max_bookings_per_month: Optional[int],
        priority_booking: bool,
        is_active: bool
    ) -> Dict:
        """Create a new membership plan"""
        try:
            plan_data = {
                "tenant_id": tenant_id,
                "name": name,
                "description": description,
                "price": price,
                "billing_cycle": billing_cycle,
                "discount_percentage": discount_percentage,
                "benefits": benefits,
                "max_bookings_per_month": max_bookings_per_month,
                "priority_booking": priority_booking,
                "is_active": is_active,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = self.db.membership_plans.insert_one(plan_data)
            plan_data["_id"] = str(result.inserted_id)
            
            return plan_data
        
        except Exception as e:
            logger.error(f"Error creating membership plan: {e}")
            raise Exception(f"Failed to create membership plan: {str(e)}")
    
    async def create_subscription(
        self,
        tenant_id: str,
        client_id: str,
        plan_id: str,
        payment_method: str,
        auto_renew: bool
    ) -> Dict:
        """Create a new membership subscription"""
        try:
            # Get plan details
            plan = self.db.membership_plans.find_one({
                "_id": ObjectId(plan_id),
                "tenant_id": tenant_id,
                "is_active": True
            })
            
            if not plan:
                raise ValueError("Membership plan not found or inactive")
            
            # Get client details
            client = self.db.clients.find_one({
                "_id": ObjectId(client_id),
                "tenant_id": tenant_id
            })
            
            if not client:
                raise ValueError("Client not found")
            
            # Calculate next billing date
            start_date = datetime.utcnow()
            if plan["billing_cycle"] == "monthly":
                next_billing = start_date + timedelta(days=30)
            elif plan["billing_cycle"] == "quarterly":
                next_billing = start_date + timedelta(days=90)
            elif plan["billing_cycle"] == "yearly":
                next_billing = start_date + timedelta(days=365)
            else:
                next_billing = start_date + timedelta(days=30)
            
            subscription_data = {
                "tenant_id": tenant_id,
                "client_id": client_id,
                "plan_id": plan_id,
                "plan_name": plan["name"],
                "plan_price": plan["price"],
                "billing_cycle": plan["billing_cycle"],
                "discount_percentage": plan["discount_percentage"],
                "client_name": client.get("name", ""),
                "client_phone": client.get("phone", ""),
                "payment_method": payment_method,
                "auto_renew": auto_renew,
                "status": "active",
                "start_date": start_date,
                "next_billing_date": next_billing,
                "last_billing_date": None,
                "bookings_used_this_month": 0,
                "total_payments": plan["price"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "cancelled_at": None
            }
            
            result = self.db.membership_subscriptions.insert_one(subscription_data)
            subscription_data["_id"] = str(result.inserted_id)
            
            return subscription_data
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            raise Exception(f"Failed to create subscription: {str(e)}")
    
    async def cancel_subscription(
        self,
        subscription_id: str,
        tenant_id: str,
        immediate: bool
    ) -> Dict:
        """Cancel a membership subscription"""
        try:
            subscription = self.db.membership_subscriptions.find_one({
                "_id": ObjectId(subscription_id),
                "tenant_id": tenant_id
            })
            
            if not subscription:
                raise ValueError("Subscription not found")
            
            if immediate:
                self.db.membership_subscriptions.update_one(
                    {"_id": ObjectId(subscription_id)},
                    {
                        "$set": {
                            "status": "cancelled",
                            "auto_renew": False,
                            "cancelled_at": datetime.utcnow(),
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
                return {
                    "success": True,
                    "message": "Subscription cancelled immediately",
                    "end_date": None
                }
            else:
                self.db.membership_subscriptions.update_one(
                    {"_id": ObjectId(subscription_id)},
                    {
                        "$set": {
                            "auto_renew": False,
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
                return {
                    "success": True,
                    "message": "Subscription will cancel at end of billing period",
                    "end_date": subscription.get("next_billing_date")
                }
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error cancelling subscription: {e}")
            raise Exception(f"Failed to cancel subscription: {str(e)}")
