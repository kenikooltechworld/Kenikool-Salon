from datetime import datetime, timedelta
from typing import Dict, List, Optional
from bson import ObjectId
from app.database import Database


class SubscriptionManagementService:
    
    @staticmethod
    def create_subscription_plan(
        tenant_id: str,
        name: str,
        description: str,
        price: float,
        billing_cycle: str,
        services_included: List[str],
        max_bookings_per_month: Optional[int] = None,
        discount_percentage: float = 0
    ) -> Dict:
        """Create subscription plan"""
        db = Database.get_db()
        
        plan = {
            "tenant_id": tenant_id,
            "name": name,
            "description": description,
            "price": price,
            "billing_cycle": billing_cycle,
            "services_included": services_included,
            "max_bookings_per_month": max_bookings_per_month,
            "discount_percentage": discount_percentage,
            "is_active": True,
            "created_at": datetime.utcnow()
        }
        
        result = db.subscription_plans.insert_one(plan)
        plan["_id"] = str(result.inserted_id)
        
        return plan
    
    @staticmethod
    def subscribe_client(
        tenant_id: str,
        client_id: str,
        plan_id: str
    ) -> Dict:
        """Subscribe client to plan"""
        db = Database.get_db()
        
        plan = db.subscription_plans.find_one({
            "_id": ObjectId(plan_id),
            "tenant_id": tenant_id
        })
        
        if not plan:
            raise ValueError("Plan not found")
        
        # Calculate next billing date
        if plan["billing_cycle"] == "monthly":
            next_billing = datetime.utcnow() + timedelta(days=30)
        elif plan["billing_cycle"] == "yearly":
            next_billing = datetime.utcnow() + timedelta(days=365)
        else:
            next_billing = datetime.utcnow() + timedelta(days=30)
        
        subscription = {
            "tenant_id": tenant_id,
            "client_id": ObjectId(client_id),
            "plan_id": ObjectId(plan_id),
            "status": "active",
            "start_date": datetime.utcnow(),
            "next_billing_date": next_billing,
            "bookings_used": 0,
            "created_at": datetime.utcnow()
        }
        
        result = db.subscriptions.insert_one(subscription)
        subscription["_id"] = str(result.inserted_id)
        
        return subscription
    
    @staticmethod
    def cancel_subscription(tenant_id: str, subscription_id: str) -> bool:
        """Cancel subscription"""
        db = Database.get_db()
        
        result = db.subscriptions.update_one(
            {
                "_id": ObjectId(subscription_id),
                "tenant_id": tenant_id
            },
            {
                "$set": {
                    "status": "cancelled",
                    "cancelled_at": datetime.utcnow()
                }
            }
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def get_client_subscription(tenant_id: str, client_id: str) -> Optional[Dict]:
        """Get active subscription for client"""
        db = Database.get_db()
        
        subscription = db.subscriptions.find_one({
            "tenant_id": tenant_id,
            "client_id": ObjectId(client_id),
            "status": "active"
        })
        
        if subscription:
            subscription["_id"] = str(subscription["_id"])
            subscription["plan_id"] = str(subscription["plan_id"])
        
        return subscription
    
    @staticmethod
    def use_subscription_booking(tenant_id: str, client_id: str) -> Dict:
        """Use one booking from subscription"""
        db = Database.get_db()
        
        subscription = db.subscriptions.find_one({
            "tenant_id": tenant_id,
            "client_id": ObjectId(client_id),
            "status": "active"
        })
        
        if not subscription:
            raise ValueError("No active subscription")
        
        plan = db.subscription_plans.find_one({
            "_id": subscription["plan_id"]
        })
        
        if plan.get("max_bookings_per_month"):
            if subscription["bookings_used"] >= plan["max_bookings_per_month"]:
                raise ValueError("Monthly booking limit reached")
        
        db.subscriptions.update_one(
            {"_id": subscription["_id"]},
            {"$inc": {"bookings_used": 1}}
        )
        
        return {
            "status": "success",
            "bookings_used": subscription["bookings_used"] + 1,
            "bookings_remaining": plan.get("max_bookings_per_month", float('inf')) - (subscription["bookings_used"] + 1)
        }
    
    @staticmethod
    def get_subscription_plans(tenant_id: str) -> List[Dict]:
        """Get all subscription plans"""
        db = Database.get_db()
        
        plans = list(db.subscription_plans.find({
            "tenant_id": tenant_id,
            "is_active": True
        }))
        
        return plans
