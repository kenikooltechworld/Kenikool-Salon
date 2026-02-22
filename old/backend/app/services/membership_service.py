"""
Membership Service Layer

This module provides the core business logic for the membership system.
It handles plan management, subscription lifecycle, billing, and analytics.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from bson import ObjectId
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError

from app.schemas.membership import (
    MembershipPlanCreateRequest,
    MembershipPlanUpdateRequest,
    MembershipSubscriptionCreateRequest,
    MembershipSubscriptionCancelRequest,
    MembershipSubscriptionChangePlanRequest,
    MembershipSubscriptionPaymentMethodRequest,
)

logger = logging.getLogger(__name__)


class MembershipService:
    """Service for managing membership plans and subscriptions"""
    
    def __init__(self, db: Database):
        """Initialize service with database connection"""
        self.db = db
        self.plans_collection = db["membership_plans"]
        self.subscriptions_collection = db["membership_subscriptions"]
        self.clients_collection = db["clients"]
    
    # ========================================================================
    # PLAN MANAGEMENT
    # ========================================================================
    
    async def create_plan(self, tenant_id: str, plan_data: MembershipPlanCreateRequest, created_by: Optional[str] = None) -> Dict[str, Any]:
        """Create a new membership plan with validation"""
        try:
            existing = self.plans_collection.find_one({"tenant_id": tenant_id, "name": plan_data.name})
            if existing:
                raise ValueError(f"Plan name '{plan_data.name}' already exists")
            if plan_data.price <= 0:
                raise ValueError("Price must be greater than zero")
            valid_cycles = ["monthly", "quarterly", "yearly"]
            if plan_data.billing_cycle not in valid_cycles:
                raise ValueError(f"Billing cycle must be one of {valid_cycles}")
            if not (0 <= plan_data.discount_percentage <= 100):
                raise ValueError("Discount percentage must be between 0 and 100")
            plan_doc = {
                "tenant_id": tenant_id,
                "name": plan_data.name,
                "description": plan_data.description,
                "price": plan_data.price,
                "billing_cycle": plan_data.billing_cycle,
                "benefits": plan_data.benefits or [],
                "discount_percentage": plan_data.discount_percentage,
                "trial_period_days": plan_data.trial_period_days,
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "created_by": created_by
            }
            result = self.plans_collection.insert_one(plan_doc)
            plan_doc["_id"] = result.inserted_id
            logger.info(f"Created membership plan: {result.inserted_id}")
            return plan_doc
        except Exception as e:
            logger.error(f"Error creating membership plan: {e}")
            raise
    
    async def update_plan(self, tenant_id: str, plan_id: str, updates: MembershipPlanUpdateRequest) -> Dict[str, Any]:
        """Update a membership plan"""
        try:
            plan = self.plans_collection.find_one({"_id": ObjectId(plan_id), "tenant_id": tenant_id})
            if not plan:
                raise ValueError(f"Plan {plan_id} not found")
            update_doc = {}
            if updates.name is not None:
                existing = self.plans_collection.find_one({"tenant_id": tenant_id, "name": updates.name, "_id": {"$ne": ObjectId(plan_id)}})
                if existing:
                    raise ValueError(f"Plan name '{updates.name}' already exists")
                update_doc["name"] = updates.name
            if updates.price is not None:
                if updates.price <= 0:
                    raise ValueError("Price must be greater than zero")
                update_doc["price"] = updates.price
            if updates.discount_percentage is not None:
                if not (0 <= updates.discount_percentage <= 100):
                    raise ValueError("Discount percentage must be between 0 and 100")
                update_doc["discount_percentage"] = updates.discount_percentage
            update_doc["updated_at"] = datetime.utcnow()
            result = self.plans_collection.find_one_and_update({"_id": ObjectId(plan_id), "tenant_id": tenant_id}, {"$set": update_doc}, return_document=True)
            logger.info(f"Updated membership plan: {plan_id}")
            return result
        except Exception as e:
            logger.error(f"Error updating membership plan: {e}")
            raise
    
    async def delete_plan(self, tenant_id: str, plan_id: str, force: bool = False) -> Dict[str, Any]:
        """Delete a membership plan"""
        try:
            plan = self.plans_collection.find_one({"_id": ObjectId(plan_id), "tenant_id": tenant_id})
            if not plan:
                raise ValueError(f"Plan {plan_id} not found")
            active_subs = self.subscriptions_collection.count_documents({"plan_id": plan_id, "status": {"$in": ["active", "trial", "paused"]}})
            if active_subs > 0 and not force:
                raise ValueError(f"Cannot delete plan with {active_subs} active subscriptions")
            if force and active_subs > 0:
                self.subscriptions_collection.update_many({"plan_id": plan_id, "status": {"$in": ["active", "trial", "paused"]}}, {"$set": {"status": "cancelled", "auto_renew": False, "cancelled_at": datetime.utcnow(), "cancellation_reason": "Plan deleted", "updated_at": datetime.utcnow()}})
            result = self.plans_collection.delete_one({"_id": ObjectId(plan_id), "tenant_id": tenant_id})
            logger.info(f"Deleted membership plan: {plan_id}")
            return {"deleted_count": result.deleted_count}
        except Exception as e:
            logger.error(f"Error deleting membership plan: {e}")
            raise
    
    async def get_plan(self, tenant_id: str, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get a single membership plan"""
        try:
            plan = self.plans_collection.find_one({"_id": ObjectId(plan_id), "tenant_id": tenant_id})
            return plan
        except Exception as e:
            logger.error(f"Error getting membership plan: {e}")
            raise
    
    async def get_plans(self, tenant_id: str, is_active: Optional[bool] = None, billing_cycle: Optional[str] = None, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """Get membership plans with optional filters"""
        try:
            filter_doc = {"tenant_id": tenant_id}
            if is_active is not None:
                filter_doc["is_active"] = is_active
            if billing_cycle is not None:
                filter_doc["billing_cycle"] = billing_cycle
            total = self.plans_collection.count_documents(filter_doc)
            skip = (page - 1) * limit
            pages = (total + limit - 1) // limit
            plans = list(self.plans_collection.find(filter_doc).skip(skip).limit(limit).sort("created_at", -1))
            return {"plans": plans, "total": total, "page": page, "pages": pages, "limit": limit}
        except Exception as e:
            logger.error(f"Error getting membership plans: {e}")
            raise
    
    async def get_plan_subscribers(self, tenant_id: str, plan_id: str) -> Dict[str, Any]:
        """Get subscribers for a plan with statistics"""
        try:
            plan = self.plans_collection.find_one({"_id": ObjectId(plan_id), "tenant_id": tenant_id})
            if not plan:
                raise ValueError(f"Plan {plan_id} not found")
            subscriptions = list(self.subscriptions_collection.find({"plan_id": plan_id, "status": {"$in": ["active", "trial", "paused"]}}))
            total_revenue = 0
            for sub in subscriptions:
                price = plan.get("price", 0)
                cycle = plan.get("billing_cycle", "monthly")
                if cycle == "monthly":
                    total_revenue += price
                elif cycle == "quarterly":
                    total_revenue += price / 3
                elif cycle == "yearly":
                    total_revenue += price / 12
            durations = []
            for sub in subscriptions:
                if sub.get("start_date"):
                    duration = (datetime.utcnow() - sub["start_date"]).days
                    durations.append(duration)
            avg_duration = sum(durations) / len(durations) if durations else 0
            return {"plan": plan, "subscribers": subscriptions, "total_count": len(subscriptions), "total_revenue": total_revenue, "average_subscription_duration_days": avg_duration}
        except Exception as e:
            logger.error(f"Error getting plan subscribers: {e}")
            raise
    
    async def create_subscription(self, tenant_id: str, client_id: str, plan_id: str, payment_method_id: Optional[str] = None, start_trial: bool = False) -> Dict[str, Any]:
        """Create a new subscription"""
        try:
            client = self.clients_collection.find_one({"_id": ObjectId(client_id), "tenant_id": tenant_id})
            if not client:
                raise ValueError(f"Client {client_id} not found")
            plan = self.plans_collection.find_one({"_id": ObjectId(plan_id), "tenant_id": tenant_id, "is_active": True})
            if not plan:
                raise ValueError(f"Plan {plan_id} not found or is inactive")
            existing = self.subscriptions_collection.find_one({"tenant_id": tenant_id, "client_id": client_id, "status": {"$in": ["active", "trial"]}})
            if existing:
                raise ValueError("Client already has an active subscription")
            start_date = datetime.utcnow()
            if start_trial and plan.get("trial_period_days"):
                trial_end_date = start_date + timedelta(days=plan["trial_period_days"])
                end_date = trial_end_date
                status = "trial"
            else:
                end_date = self._calculate_end_date(start_date, plan["billing_cycle"])
                status = "active"
            sub_doc = {
                "tenant_id": tenant_id,
                "client_id": client_id,
                "plan_id": plan_id,
                "status": status,
                "start_date": start_date,
                "end_date": end_date,
                "trial_end_date": trial_end_date if start_trial else None,
                "auto_renew": True,
                "payment_method_id": payment_method_id,
                "payment_history": [],
                "renewal_history": [],
                "benefit_usage": {"cycle_start": start_date, "usage_count": 0, "limit": -1},
                "grace_period_start": None,
                "retry_count": 0,
                "cancellation_reason": None,
                "cancelled_at": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            result = self.subscriptions_collection.insert_one(sub_doc)
            sub_doc["_id"] = result.inserted_id
            logger.info(f"Created subscription {result.inserted_id}")
            return sub_doc
        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            raise
    
    async def cancel_subscription(self, tenant_id: str, subscription_id: str, reason: Optional[str] = None, immediate: bool = False) -> Dict[str, Any]:
        """Cancel a subscription"""
        try:
            sub = self.subscriptions_collection.find_one({"_id": ObjectId(subscription_id), "tenant_id": tenant_id})
            if not sub:
                raise ValueError(f"Subscription {subscription_id} not found")
            if immediate:
                result = self.subscriptions_collection.find_one_and_update({"_id": ObjectId(subscription_id)}, {"$set": {"status": "cancelled", "auto_renew": False, "cancellation_reason": reason, "cancelled_at": datetime.utcnow(), "updated_at": datetime.utcnow()}}, return_document=True)
            else:
                result = self.subscriptions_collection.find_one_and_update({"_id": ObjectId(subscription_id)}, {"$set": {"auto_renew": False, "cancellation_reason": reason, "updated_at": datetime.utcnow()}}, return_document=True)
            logger.info(f"Cancelled subscription {subscription_id}")
            return result
        except Exception as e:
            logger.error(f"Error cancelling subscription: {e}")
            raise
    
    async def pause_subscription(self, tenant_id: str, subscription_id: str) -> Dict[str, Any]:
        """Pause a subscription"""
        try:
            result = self.subscriptions_collection.find_one_and_update({"_id": ObjectId(subscription_id), "tenant_id": tenant_id}, {"$set": {"status": "paused", "updated_at": datetime.utcnow()}}, return_document=True)
            if not result:
                raise ValueError(f"Subscription {subscription_id} not found")
            logger.info(f"Paused subscription {subscription_id}")
            return result
        except Exception as e:
            logger.error(f"Error pausing subscription: {e}")
            raise
    
    async def resume_subscription(self, tenant_id: str, subscription_id: str) -> Dict[str, Any]:
        """Resume a paused subscription"""
        try:
            sub = self.subscriptions_collection.find_one({"_id": ObjectId(subscription_id), "tenant_id": tenant_id})
            if not sub:
                raise ValueError(f"Subscription {subscription_id} not found")
            plan = self.plans_collection.find_one({"_id": ObjectId(sub["plan_id"])})
            if not plan:
                raise ValueError(f"Plan {sub['plan_id']} not found")
            new_end_date = self._calculate_end_date(datetime.utcnow(), plan["billing_cycle"])
            result = self.subscriptions_collection.find_one_and_update({"_id": ObjectId(subscription_id)}, {"$set": {"status": "active", "end_date": new_end_date, "updated_at": datetime.utcnow()}}, return_document=True)
            logger.info(f"Resumed subscription {subscription_id}")
            return result
        except Exception as e:
            logger.error(f"Error resuming subscription: {e}")
            raise
    
    async def get_subscription(self, tenant_id: str, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get a single subscription"""
        try:
            sub = self.subscriptions_collection.find_one({"_id": ObjectId(subscription_id), "tenant_id": tenant_id})
            return sub
        except Exception as e:
            logger.error(f"Error getting subscription: {e}")
            raise
    
    def get_subscriptions(self, tenant_id: str, status: Optional[str] = None, plan_id: Optional[str] = None, client_id: Optional[str] = None, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """Get subscriptions with optional filters"""
        try:
            filter_doc = {"tenant_id": tenant_id}
            
            # Only add filters if they have actual values (not empty strings)
            if status and status.strip():
                filter_doc["status"] = status.strip()
            if plan_id and plan_id.strip():
                filter_doc["plan_id"] = plan_id.strip()
            if client_id and client_id.strip():
                filter_doc["client_id"] = client_id.strip()
            
            logger.info(f"Querying subscriptions with filter: {filter_doc}")
            
            total = self.subscriptions_collection.count_documents(filter_doc)
            skip = (page - 1) * limit
            pages = (total + limit - 1) // limit
            subs = list(self.subscriptions_collection.find(filter_doc).skip(skip).limit(limit).sort("created_at", -1))
            
            logger.info(f"Found {len(subs)} subscriptions")
            
            return {"subscriptions": subs, "total": total, "page": page, "pages": pages, "limit": limit}
        except Exception as e:
            logger.error(f"Error getting subscriptions: {e}", exc_info=True)
            raise
    
    def _calculate_end_date(self, start_date: datetime, billing_cycle: str) -> datetime:
        """Calculate end date based on billing cycle"""
        if billing_cycle == "monthly":
            return start_date + timedelta(days=30)
        elif billing_cycle == "quarterly":
            return start_date + timedelta(days=90)
        elif billing_cycle == "yearly":
            return start_date + timedelta(days=365)
        else:
            raise ValueError(f"Invalid billing cycle: {billing_cycle}")
    
    async def get_client_discount(self, tenant_id: str, client_id: str) -> float:
        """Get active membership discount for a client"""
        try:
            sub = self.subscriptions_collection.find_one({"tenant_id": tenant_id, "client_id": client_id, "status": "active"})
            if not sub:
                return 0.0
            plan = self.plans_collection.find_one({"_id": ObjectId(sub["plan_id"])})
            if not plan:
                return 0.0
            return plan.get("discount_percentage", 0.0)
        except Exception as e:
            logger.error(f"Error getting client discount: {e}")
            return 0.0
