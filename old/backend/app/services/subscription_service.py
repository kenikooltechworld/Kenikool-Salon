"""
Platform subscription service - Handles salon owner subscriptions to platform plans
"""
from bson import ObjectId
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

from app.database import Database
from app.api.exceptions import NotFoundException, BadRequestException

logger = logging.getLogger(__name__)


class SubscriptionService:
    """Service for managing platform subscriptions"""
    
    # Platform plans configuration - 6 tiers for Nigerian market
    PLANS = {
        "free": {
            "id": "free",
            "name": "FREE",
            "price": 0,
            "yearly_price": 0,
            "billing_cycle": "monthly",
            "features": [
                "1 staff user",
                "50 bookings per month",
                "100 clients maximum",
                "Basic POS (online only)",
                "Cash payments only",
                "Email support (48-72h)"
            ],
            "max_bookings": 50,
            "max_staff": 1,
            "max_clients": 100,
            "max_sms": 0,
            "max_locations": 1,
            "has_offline_pos": False,
            "has_inventory": False,
            "has_loyalty": False,
            "has_campaigns": False,
            "has_accounting": False,
            "has_packages": False,
            "has_custom_branding": False,
            "has_custom_domain": False,
            "has_api_access": False,
            "has_white_label": False,
            "has_reseller_rights": False,
            "has_sms_notifications": False,
            "is_active": True
        },
        "starter": {
            "id": "starter",
            "name": "STARTER",
            "price": 15000,
            "yearly_price": 153000,  # 15% discount (12 months for price of 10.2)
            "billing_cycle": "monthly",
            "features": [
                "1-3 staff users",
                "Unlimited bookings",
                "500 clients",
                "Offline POS (works without internet)",
                "Multiple payment methods",
                "100 SMS per month",
                "Email & chat support (24-48h)"
            ],
            "max_bookings": None,
            "max_staff": 3,
            "max_clients": 500,
            "max_sms": 100,
            "max_locations": 1,
            "has_offline_pos": True,
            "has_inventory": False,
            "has_loyalty": False,
            "has_campaigns": False,
            "has_accounting": False,
            "has_packages": False,
            "has_custom_branding": True,
            "has_custom_domain": False,
            "has_api_access": False,
            "has_white_label": False,
            "has_reseller_rights": False,
            "has_sms_notifications": True,
            "is_active": True
        },
        "professional": {
            "id": "professional",
            "name": "PROFESSIONAL",
            "price": 35000,
            "yearly_price": 357000,  # 15% discount
            "billing_cycle": "monthly",
            "features": [
                "4-10 staff users",
                "Unlimited bookings",
                "2,000 clients",
                "Inventory management",
                "Loyalty program",
                "Marketing campaigns (basic)",
                "500 SMS per month",
                "Email, chat & WhatsApp support (12-24h)"
            ],
            "max_bookings": None,
            "max_staff": 10,
            "max_clients": 2000,
            "max_sms": 500,
            "max_locations": 1,
            "has_offline_pos": True,
            "has_inventory": True,
            "has_loyalty": True,
            "has_campaigns": True,
            "has_accounting": False,
            "has_packages": False,
            "has_custom_branding": True,
            "has_custom_domain": False,
            "has_api_access": False,
            "has_white_label": False,
            "has_reseller_rights": False,
            "has_sms_notifications": True,
            "is_active": True
        },
        "business": {
            "id": "business",
            "name": "BUSINESS",
            "price": 65000,
            "yearly_price": 663000,  # 15% discount
            "billing_cycle": "monthly",
            "features": [
                "11-25 staff users",
                "Unlimited bookings & clients",
                "Advanced accounting",
                "Packages & memberships",
                "Advanced campaigns",
                "2,000 SMS per month",
                "Custom domain support",
                "Priority support (6-12h)"
            ],
            "max_bookings": None,
            "max_staff": 25,
            "max_clients": None,
            "max_sms": 2000,
            "max_locations": 1,
            "has_offline_pos": True,
            "has_inventory": True,
            "has_loyalty": True,
            "has_campaigns": True,
            "has_accounting": True,
            "has_packages": True,
            "has_custom_branding": True,
            "has_custom_domain": True,
            "has_api_access": False,
            "has_white_label": False,
            "has_reseller_rights": False,
            "has_sms_notifications": True,
            "is_active": True
        },
        "enterprise": {
            "id": "enterprise",
            "name": "ENTERPRISE",
            "price": 120000,
            "yearly_price": 1224000,  # 15% discount
            "billing_cycle": "monthly",
            "features": [
                "26-50 staff users",
                "Unlimited bookings & clients",
                "White-label platform",
                "Multi-location (3 locations)",
                "API access",
                "5,000 SMS per month",
                "Dedicated account manager",
                "Priority support (2-6h)"
            ],
            "max_bookings": None,
            "max_staff": 50,
            "max_clients": None,
            "max_sms": 5000,
            "max_locations": 3,
            "has_offline_pos": True,
            "has_inventory": True,
            "has_loyalty": True,
            "has_campaigns": True,
            "has_accounting": True,
            "has_packages": True,
            "has_custom_branding": True,
            "has_custom_domain": True,
            "has_api_access": True,
            "has_white_label": True,
            "has_reseller_rights": False,
            "has_sms_notifications": True,
            "is_active": True
        },
        "unlimited": {
            "id": "unlimited",
            "name": "UNLIMITED",
            "price": 250000,
            "yearly_price": 2550000,  # 15% discount
            "billing_cycle": "monthly",
            "features": [
                "Unlimited staff & locations",
                "Unlimited everything",
                "Reseller rights",
                "Custom development (40 hours/year)",
                "99.9% uptime SLA",
                "Unlimited SMS",
                "24/7 dedicated support (1h response)",
                "On-site training"
            ],
            "max_bookings": None,
            "max_staff": None,
            "max_clients": None,
            "max_sms": None,
            "max_locations": None,
            "has_offline_pos": True,
            "has_inventory": True,
            "has_loyalty": True,
            "has_campaigns": True,
            "has_accounting": True,
            "has_packages": True,
            "has_custom_branding": True,
            "has_custom_domain": True,
            "has_api_access": True,
            "has_white_label": True,
            "has_reseller_rights": True,
            "has_sms_notifications": True,
            "is_active": True
        }
    }
    
    @staticmethod
    async def get_plans() -> List[Dict]:
        """Get all available platform plans"""
        return list(SubscriptionService.PLANS.values())
    
    @staticmethod
    async def get_plan(plan_id: str) -> Dict:
        """Get specific plan details"""
        plan = SubscriptionService.PLANS.get(plan_id)
        if not plan:
            raise NotFoundException(f"Plan {plan_id} not found")
        return plan
    
    @staticmethod
    async def get_current_subscription(tenant_id: str) -> Dict:
        """Get current subscription for tenant"""
        db = Database.get_db()
        
        # Get tenant to check current plan
        tenant = db.tenants.find_one({"_id": ObjectId(tenant_id)})
        if not tenant:
            raise NotFoundException("Tenant not found")
        
        # Get subscription record
        subscription = db.platform_subscriptions.find_one({
            "tenant_id": tenant_id,
            "status": {"$in": ["active", "trial"]}
        })
        
        if not subscription:
            # Create 30-day trial with Enterprise features for new users
            subscription_data = {
                "tenant_id": tenant_id,
                "plan_id": "trial",
                "plan_name": "30-Day Trial",
                "plan_price": 0,
                "status": "trial",
                "trial_ends_at": datetime.utcnow() + timedelta(days=30),
                "current_period_start": datetime.utcnow(),
                "current_period_end": datetime.utcnow() + timedelta(days=30),
                "cancel_at_period_end": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            result = db.platform_subscriptions.insert_one(subscription_data)
            subscription = db.platform_subscriptions.find_one({"_id": result.inserted_id})
            
            # Update tenant to trial status
            db.tenants.update_one(
                {"_id": ObjectId(tenant_id)},
                {"$set": {"subscription_plan": "trial"}}
            )
        
        return SubscriptionService._format_subscription(subscription)
    
    @staticmethod
    async def upgrade_subscription(
        tenant_id: str,
        plan_id: str,
        payment_method: str
    ) -> Dict:
        """Upgrade or downgrade subscription"""
        from app.services import paystack_service, flutterwave_service
        
        db = Database.get_db()
        
        # Validate plan
        plan = await SubscriptionService.get_plan(plan_id)
        
        # Get current subscription
        current_sub = await SubscriptionService.get_current_subscription(tenant_id)
        
        # If upgrading to paid plan, process payment
        if plan["price"] > 0:
            tenant = db.tenants.find_one({"_id": ObjectId(tenant_id)})
            if not tenant:
                raise NotFoundException("Tenant not found")
            
            # Initialize payment
            reference = f"SUB-{tenant_id[:8]}-{int(datetime.utcnow().timestamp())}"
            
            # Get frontend URL from environment or use default
            import os
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
            callback_url = f"{frontend_url}/dashboard/settings/billing/success?reference={reference}"
            
            if payment_method == "paystack":
                result = await paystack_service.initialize_payment(
                    email=tenant["email"],
                    amount=plan["price"],
                    reference=reference,
                    callback_url=callback_url
                )
                authorization_url = result["authorization_url"]
            elif payment_method == "flutterwave":
                result = await flutterwave_service.initialize_payment(
                    email=tenant["email"],
                    amount=plan["price"],
                    tx_ref=reference,
                    redirect_url=callback_url
                )
                authorization_url = result["link"]
            else:
                raise BadRequestException("Invalid payment method")
            
            # Create pending subscription change
            db.platform_subscriptions.update_one(
                {"_id": ObjectId(current_sub["id"])},
                {
                    "$set": {
                        "pending_plan_id": plan_id,
                        "pending_payment_reference": reference,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return {
                "authorization_url": authorization_url,
                "reference": reference
            }
        
        # If downgrading or switching to free, update immediately
        db.platform_subscriptions.update_one(
            {"_id": ObjectId(current_sub["id"])},
            {
                "$set": {
                    "plan_id": plan_id,
                    "plan_name": plan["name"],
                    "plan_price": plan["price"],
                    "status": "active",
                    "updated_at": datetime.utcnow()
                },
                "$unset": {"trial_ends_at": ""}
            }
        )
        
        # Update tenant plan
        db.tenants.update_one(
            {"_id": ObjectId(tenant_id)},
            {"$set": {"subscription_plan": plan_id}}
        )
        
        logger.info(f"Subscription updated for tenant {tenant_id} to {plan_id}")
        
        return await SubscriptionService.get_current_subscription(tenant_id)
    
    @staticmethod
    async def verify_subscription_payment(reference: str) -> Dict:
        """Verify subscription payment and activate"""
        from app.services import paystack_service, flutterwave_service
        
        db = Database.get_db()
        
        # Find subscription with this reference
        subscription = db.platform_subscriptions.find_one({
            "pending_payment_reference": reference
        })
        
        if not subscription:
            raise NotFoundException("Subscription payment not found")
        
        # Verify payment
        if reference.startswith("SUB-"):
            # Try Paystack first
            try:
                result = await paystack_service.verify_payment(reference)
                success = result["status"] == "success"
            except:
                result = await flutterwave_service.verify_payment(reference)
                success = result["status"] == "successful"
        else:
            raise BadRequestException("Invalid payment reference")
        
        if success:
            # Activate new plan
            plan_id = subscription["pending_plan_id"]
            plan = SubscriptionService.PLANS[plan_id]
            
            db.platform_subscriptions.update_one(
                {"_id": subscription["_id"]},
                {
                    "$set": {
                        "plan_id": plan_id,
                        "plan_name": plan["name"],
                        "plan_price": plan["price"],
                        "status": "active",
                        "current_period_start": datetime.utcnow(),
                        "current_period_end": datetime.utcnow() + timedelta(days=30),
                        "updated_at": datetime.utcnow()
                    },
                    "$unset": {
                        "pending_plan_id": "",
                        "pending_payment_reference": ""
                    }
                }
            )
            
            # Update tenant
            db.tenants.update_one(
                {"_id": ObjectId(subscription["tenant_id"])},
                {"$set": {"subscription_plan": plan_id}}
            )
            
            # Record billing history
            db.billing_history.insert_one({
                "tenant_id": subscription["tenant_id"],
                "amount": plan["price"],
                "status": "completed",
                "description": f"Subscription to {plan['name']} plan",
                "reference": reference,
                "created_at": datetime.utcnow()
            })
            
            logger.info(f"Subscription payment verified for tenant {subscription['tenant_id']}")
        
        return await SubscriptionService.get_current_subscription(subscription["tenant_id"])
    
    @staticmethod
    async def cancel_subscription(tenant_id: str, immediate: bool = False) -> Dict:
        """Cancel subscription"""
        db = Database.get_db()
        
        subscription = db.platform_subscriptions.find_one({
            "tenant_id": tenant_id,
            "status": {"$in": ["active", "trial"]}
        })
        
        if not subscription:
            raise NotFoundException("Active subscription not found")
        
        if immediate:
            # Cancel immediately - account becomes inactive
            db.platform_subscriptions.update_one(
                {"_id": subscription["_id"]},
                {
                    "$set": {
                        "status": "cancelled",
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            db.tenants.update_one(
                {"_id": ObjectId(tenant_id)},
                {"$set": {"subscription_plan": "cancelled", "is_active": False}}
            )
            
            return {
                "success": True,
                "message": "Subscription cancelled immediately. Account is now inactive.",
                "end_date": datetime.utcnow()
            }
        else:
            # Cancel at end of period
            db.platform_subscriptions.update_one(
                {"_id": subscription["_id"]},
                {
                    "$set": {
                        "cancel_at_period_end": True,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return {
                "success": True,
                "message": "Subscription will be cancelled at end of billing period",
                "end_date": subscription["current_period_end"]
            }
    
    @staticmethod
    async def add_payment_method(
        tenant_id: str,
        authorization_code: str,
        card_type: str,
        last4: str,
        exp_month: str,
        exp_year: str,
        bank: str
    ) -> Dict:
        """Add payment method"""
        db = Database.get_db()
        
        payment_method = {
            "tenant_id": tenant_id,
            "authorization_code": authorization_code,
            "card_type": card_type,
            "last4": last4,
            "exp_month": exp_month,
            "exp_year": exp_year,
            "bank": bank,
            "is_default": True,
            "created_at": datetime.utcnow()
        }
        
        # Set other methods as non-default
        db.payment_methods.update_many(
            {"tenant_id": tenant_id},
            {"$set": {"is_default": False}}
        )
        
        result = db.payment_methods.insert_one(payment_method)
        payment_method["_id"] = result.inserted_id
        
        return SubscriptionService._format_payment_method(payment_method)
    
    @staticmethod
    async def get_payment_methods(tenant_id: str) -> List[Dict]:
        """Get payment methods"""
        db = Database.get_db()
        
        methods = list(db.payment_methods.find({"tenant_id": tenant_id}))
        return [SubscriptionService._format_payment_method(m) for m in methods]
    
    @staticmethod
    async def get_billing_history(tenant_id: str, limit: int = 50) -> Dict:
        """Get billing history"""
        db = Database.get_db()
        
        history = list(
            db.billing_history.find({"tenant_id": tenant_id})
            .sort("created_at", -1)
            .limit(limit)
        )
        
        return {
            "items": [SubscriptionService._format_billing_item(item) for item in history],
            "total": len(history)
        }
    
    @staticmethod
    def _format_subscription(sub: Dict) -> Dict:
        """Format subscription for response"""
        return {
            "id": str(sub["_id"]),
            "tenant_id": sub["tenant_id"],
            "plan_id": sub["plan_id"],
            "plan_name": sub["plan_name"],
            "plan_price": sub["plan_price"],
            "status": sub["status"],
            "current_period_start": sub["current_period_start"],
            "current_period_end": sub["current_period_end"],
            "cancel_at_period_end": sub.get("cancel_at_period_end", False),
            "created_at": sub["created_at"],
            "updated_at": sub["updated_at"]
        }
    
    @staticmethod
    def _format_payment_method(method: Dict) -> Dict:
        """Format payment method for response"""
        return {
            "id": str(method["_id"]),
            "tenant_id": method["tenant_id"],
            "card_type": method["card_type"],
            "last4": method["last4"],
            "exp_month": method["exp_month"],
            "exp_year": method["exp_year"],
            "bank": method["bank"],
            "is_default": method.get("is_default", False),
            "created_at": method["created_at"]
        }
    
    @staticmethod
    def _format_billing_item(item: Dict) -> Dict:
        """Format billing history item"""
        return {
            "id": str(item["_id"]),
            "tenant_id": item["tenant_id"],
            "amount": item["amount"],
            "status": item["status"],
            "description": item["description"],
            "invoice_url": item.get("invoice_url"),
            "created_at": item["created_at"]
        }

    @staticmethod
    async def get_usage_stats(tenant_id: str) -> Dict:
        """Get usage statistics with limits for current plan"""
        from app.services.usage_tracking_service import UsageTrackingService
        from app.middleware.subscription_check import (
            check_booking_limit, check_staff_limit, 
            check_sms_limit, check_api_limit, check_client_limit
        )
        
        # Get current usage
        usage = await UsageTrackingService.get_usage_stats(tenant_id)
        
        # Get limits
        booking_limit = await check_booking_limit(tenant_id)
        staff_limit = await check_staff_limit(tenant_id)
        sms_limit = await check_sms_limit(tenant_id)
        api_limit = await check_api_limit(tenant_id)
        client_limit = await check_client_limit(tenant_id)
        
        return {
            "bookings": {
                "used": usage["bookings"],
                "limit": booking_limit["limit"],
                "unlimited": booking_limit.get("unlimited", False),
                "percentage": (usage["bookings"] / booking_limit["limit"] * 100) if booking_limit["limit"] else 0
            },
            "staff": {
                "used": usage["staff"],
                "limit": staff_limit["limit"],
                "unlimited": staff_limit.get("unlimited", False),
                "percentage": (usage["staff"] / staff_limit["limit"] * 100) if staff_limit["limit"] else 0
            },
            "clients": {
                "used": usage["clients"],
                "limit": client_limit["limit"],
                "unlimited": client_limit.get("unlimited", False),
                "percentage": (usage["clients"] / client_limit["limit"] * 100) if client_limit["limit"] else 0
            },
            "sms": {
                "used": usage["sms_sent"],
                "limit": sms_limit["limit"],
                "unlimited": sms_limit.get("unlimited", False),
                "percentage": (usage["sms_sent"] / sms_limit["limit"] * 100) if sms_limit["limit"] else 0
            },
            "api_calls": {
                "used": usage["api_calls"],
                "limit": api_limit["limit"],
                "unlimited": api_limit.get("unlimited", False),
                "percentage": (usage["api_calls"] / api_limit["limit"] * 100) if api_limit["limit"] else 0
            },
            "month": usage["month"]
        }
    
    @staticmethod
    async def check_limit(tenant_id: str, resource: str) -> Dict:
        """
        Check if tenant has reached limit for a resource
        
        Args:
            tenant_id: Tenant ID
            resource: Resource type (bookings, staff, clients, sms, api_calls, locations)
            
        Returns:
            Dict with allowed status and details
        """
        from app.middleware.subscription_check import (
            check_booking_limit, check_staff_limit, check_client_limit,
            check_sms_limit, check_api_limit, check_location_limit
        )
        
        if resource == "bookings":
            return await check_booking_limit(tenant_id)
        elif resource == "staff":
            return await check_staff_limit(tenant_id)
        elif resource == "clients":
            return await check_client_limit(tenant_id)
        elif resource == "sms":
            return await check_sms_limit(tenant_id)
        elif resource == "api_calls":
            return await check_api_limit(tenant_id)
        elif resource == "locations":
            return await check_location_limit(tenant_id)
        else:
            return {"allowed": False, "error": "Invalid resource type"}


# Singleton instance
subscription_service = SubscriptionService()
