"""
Subscription middleware - Check subscription status and enforce limits
"""
from fastapi import Request, HTTPException
from datetime import datetime
from bson import ObjectId
from app.database import Database


async def check_subscription_status(request: Request, tenant_id: str):
    """
    Check if tenant has active subscription or trial
    Raises HTTPException if subscription expired
    """
    db = Database.get_db()
    
    # Get subscription
    subscription = db.platform_subscriptions.find_one({
        "tenant_id": tenant_id,
        "status": {"$in": ["active", "trial"]}
    })
    
    if not subscription:
        raise HTTPException(
            status_code=403,
            detail="No active subscription. Please subscribe to continue using the platform."
        )
    
    # Check if trial expired
    if subscription["status"] == "trial":
        trial_end = subscription.get("trial_ends_at")
        if trial_end and datetime.utcnow() > trial_end:
            # Update status to expired
            db.platform_subscriptions.update_one(
                {"_id": subscription["_id"]},
                {"$set": {"status": "expired"}}
            )
            db.tenants.update_one(
                {"_id": ObjectId(tenant_id)},
                {"$set": {"is_active": False}}
            )
            raise HTTPException(
                status_code=403,
                detail="Your trial has expired. Please subscribe to continue."
            )
    
    # Check if subscription period ended
    if subscription["status"] == "active":
        period_end = subscription.get("current_period_end")
        if period_end and datetime.utcnow() > period_end:
            if subscription.get("cancel_at_period_end"):
                # Subscription was cancelled, deactivate
                db.platform_subscriptions.update_one(
                    {"_id": subscription["_id"]},
                    {"$set": {"status": "cancelled"}}
                )
                db.tenants.update_one(
                    {"_id": ObjectId(tenant_id)},
                    {"$set": {"is_active": False}}
                )
                raise HTTPException(
                    status_code=403,
                    detail="Your subscription has been cancelled. Please resubscribe to continue."
                )
    
    return subscription


async def check_feature_access(tenant_id: str, feature: str) -> bool:
    """
    Check if tenant's plan has access to specific feature
    
    Features:
    - offline_pos: Offline POS functionality
    - inventory: Inventory management
    - loyalty: Loyalty program
    - campaigns: Marketing campaigns
    - accounting: Accounting features
    - packages: Packages & memberships
    - custom_branding: Custom branding
    - custom_domain: Custom domain
    - api_access: API access
    - white_label: White-label platform
    - reseller_rights: Reseller rights
    - sms_notifications: SMS notifications
    """
    db = Database.get_db()
    
    subscription = db.platform_subscriptions.find_one({
        "tenant_id": tenant_id,
        "status": {"$in": ["active", "trial"]}
    })
    
    if not subscription:
        return False
    
    plan_id = subscription.get("plan_id")
    
    # Trial has all features
    if plan_id == "trial":
        return True
    
    # Feature access by plan (6 tiers)
    feature_access = {
        "free": {
            "offline_pos": False,
            "inventory": False,
            "loyalty": False,
            "campaigns": False,
            "accounting": False,
            "packages": False,
            "custom_branding": False,
            "custom_domain": False,
            "api_access": False,
            "white_label": False,
            "reseller_rights": False,
            "sms_notifications": False
        },
        "starter": {
            "offline_pos": True,
            "inventory": False,
            "loyalty": False,
            "campaigns": False,
            "accounting": False,
            "packages": False,
            "custom_branding": True,
            "custom_domain": False,
            "api_access": False,
            "white_label": False,
            "reseller_rights": False,
            "sms_notifications": True
        },
        "professional": {
            "offline_pos": True,
            "inventory": True,
            "loyalty": True,
            "campaigns": True,
            "accounting": False,
            "packages": False,
            "custom_branding": True,
            "custom_domain": False,
            "api_access": False,
            "white_label": False,
            "reseller_rights": False,
            "sms_notifications": True
        },
        "business": {
            "offline_pos": True,
            "inventory": True,
            "loyalty": True,
            "campaigns": True,
            "accounting": True,
            "packages": True,
            "custom_branding": True,
            "custom_domain": True,
            "api_access": False,
            "white_label": False,
            "reseller_rights": False,
            "sms_notifications": True
        },
        "enterprise": {
            "offline_pos": True,
            "inventory": True,
            "loyalty": True,
            "campaigns": True,
            "accounting": True,
            "packages": True,
            "custom_branding": True,
            "custom_domain": True,
            "api_access": True,
            "white_label": True,
            "reseller_rights": False,
            "sms_notifications": True
        },
        "unlimited": {
            "offline_pos": True,
            "inventory": True,
            "loyalty": True,
            "campaigns": True,
            "accounting": True,
            "packages": True,
            "custom_branding": True,
            "custom_domain": True,
            "api_access": True,
            "white_label": True,
            "reseller_rights": True,
            "sms_notifications": True
        }
    }
    
    return feature_access.get(plan_id, {}).get(feature, False)


async def check_booking_limit(tenant_id: str) -> dict:
    """
    Check booking limits for tenant's plan
    Returns dict with limit info
    """
    db = Database.get_db()
    
    subscription = db.platform_subscriptions.find_one({
        "tenant_id": tenant_id,
        "status": {"$in": ["active", "trial"]}
    })
    
    if not subscription:
        return {"allowed": False, "limit": 0, "used": 0}
    
    plan_id = subscription.get("plan_id")
    
    # Get current month bookings count
    from datetime import datetime
    start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    bookings_count = db.bookings.count_documents({
        "tenant_id": tenant_id,
        "created_at": {"$gte": start_of_month}
    })
    
    # Booking limits by plan (6 tiers)
    limits = {
        "trial": None,  # Unlimited during trial
        "free": 50,
        "starter": None,  # Unlimited
        "professional": None,  # Unlimited
        "business": None,  # Unlimited
        "enterprise": None,  # Unlimited
        "unlimited": None  # Unlimited
    }
    
    limit = limits.get(plan_id)
    
    if limit is None:
        return {"allowed": True, "limit": None, "used": bookings_count, "unlimited": True}
    
    return {
        "allowed": bookings_count < limit,
        "limit": limit,
        "used": bookings_count,
        "unlimited": False
    }


async def check_staff_limit(tenant_id: str) -> dict:
    """
    Check staff limits for tenant's plan
    Returns dict with limit info
    """
    db = Database.get_db()
    
    subscription = db.platform_subscriptions.find_one({
        "tenant_id": tenant_id,
        "status": {"$in": ["active", "trial"]}
    })
    
    if not subscription:
        return {"allowed": False, "limit": 0, "used": 0}
    
    plan_id = subscription.get("plan_id")
    
    # Get current staff count
    staff_count = db.stylists.count_documents({
        "tenant_id": tenant_id,
        "is_active": True
    })
    
    # Staff limits by plan (6 tiers)
    limits = {
        "trial": None,  # Unlimited during trial
        "free": 1,
        "starter": 3,
        "professional": 10,
        "business": 25,
        "enterprise": 50,
        "unlimited": None  # Unlimited
    }
    
    limit = limits.get(plan_id)
    
    if limit is None:
        return {"allowed": True, "limit": None, "used": staff_count, "unlimited": True}
    
    return {
        "allowed": staff_count < limit,
        "limit": limit,
        "used": staff_count,
        "unlimited": False
    }



async def check_client_limit(tenant_id: str) -> dict:
    """
    Check client limits for tenant's plan
    Returns dict with limit info
    """
    db = Database.get_db()
    
    subscription = db.platform_subscriptions.find_one({
        "tenant_id": tenant_id,
        "status": {"$in": ["active", "trial"]}
    })
    
    if not subscription:
        return {"allowed": False, "limit": 0, "used": 0}
    
    plan_id = subscription.get("plan_id")
    
    # Get current client count
    client_count = db.clients.count_documents({
        "tenant_id": tenant_id,
        "is_active": True
    })
    
    # Client limits by plan (6 tiers)
    limits = {
        "trial": None,  # Unlimited during trial
        "free": 100,
        "starter": 500,
        "professional": 2000,
        "business": None,  # Unlimited
        "enterprise": None,  # Unlimited
        "unlimited": None  # Unlimited
    }
    
    limit = limits.get(plan_id)
    
    if limit is None:
        return {"allowed": True, "limit": None, "used": client_count, "unlimited": True}
    
    return {
        "allowed": client_count < limit,
        "limit": limit,
        "used": client_count,
        "unlimited": False
    }


async def check_location_limit(tenant_id: str) -> dict:
    """
    Check location limits for tenant's plan
    Returns dict with limit info
    """
    db = Database.get_db()
    
    subscription = db.platform_subscriptions.find_one({
        "tenant_id": tenant_id,
        "status": {"$in": ["active", "trial"]}
    })
    
    if not subscription:
        return {"allowed": False, "limit": 0, "used": 0}
    
    plan_id = subscription.get("plan_id")
    
    # Get current location count
    location_count = db.locations.count_documents({
        "tenant_id": tenant_id,
        "is_active": True
    })
    
    # Location limits by plan (6 tiers)
    limits = {
        "trial": None,  # Unlimited during trial
        "free": 1,
        "starter": 1,
        "professional": 1,
        "business": 1,
        "enterprise": 3,
        "unlimited": None  # Unlimited
    }
    
    limit = limits.get(plan_id)
    
    if limit is None:
        return {"allowed": True, "limit": None, "used": location_count, "unlimited": True}
    
    return {
        "allowed": location_count < limit,
        "limit": limit,
        "used": location_count,
        "unlimited": False
    }


async def check_sms_limit(tenant_id: str) -> dict:
    """
    Check SMS limits for tenant's plan
    Returns dict with limit info
    """
    db = Database.get_db()
    
    subscription = db.platform_subscriptions.find_one({
        "tenant_id": tenant_id,
        "status": {"$in": ["active", "trial"]}
    })
    
    if not subscription:
        return {"allowed": False, "limit": 0, "used": 0}
    
    plan_id = subscription.get("plan_id")
    
    # Get current month SMS count from usage tracking
    from datetime import datetime
    month_key = datetime.utcnow().strftime("%Y-%m")
    
    usage = db.usage_tracking.find_one({
        "tenant_id": tenant_id,
        "month": month_key
    })
    
    sms_count = usage.get("sms_sent", 0) if usage else 0
    
    # SMS limits by plan (6 tiers)
    limits = {
        "trial": None,  # Unlimited during trial
        "free": 0,  # No SMS
        "starter": 100,
        "professional": 500,
        "business": 2000,
        "enterprise": 5000,
        "unlimited": None  # Unlimited
    }
    
    limit = limits.get(plan_id)
    
    if limit is None:
        return {"allowed": True, "limit": None, "used": sms_count, "unlimited": True}
    
    if limit == 0:
        return {"allowed": False, "limit": 0, "used": sms_count, "unlimited": False}
    
    return {
        "allowed": sms_count < limit,
        "limit": limit,
        "used": sms_count,
        "unlimited": False
    }


async def check_api_limit(tenant_id: str) -> dict:
    """
    Check API call limits for tenant's plan
    Returns dict with limit info
    """
    db = Database.get_db()
    
    subscription = db.platform_subscriptions.find_one({
        "tenant_id": tenant_id,
        "status": {"$in": ["active", "trial"]}
    })
    
    if not subscription:
        return {"allowed": False, "limit": 0, "used": 0}
    
    plan_id = subscription.get("plan_id")
    
    # Get current month API calls from usage tracking
    from datetime import datetime
    month_key = datetime.utcnow().strftime("%Y-%m")
    
    usage = db.usage_tracking.find_one({
        "tenant_id": tenant_id,
        "month": month_key
    })
    
    api_count = usage.get("api_calls", 0) if usage else 0
    
    # API limits by plan (6 tiers)
    limits = {
        "trial": None,  # Unlimited during trial
        "free": 0,  # No API access
        "starter": 0,  # No API access
        "professional": 0,  # No API access
        "business": 0,  # No API access
        "enterprise": None,  # Unlimited
        "unlimited": None  # Unlimited
    }
    
    limit = limits.get(plan_id)
    
    if limit is None:
        return {"allowed": True, "limit": None, "used": api_count, "unlimited": True}
    
    if limit == 0:
        return {"allowed": False, "limit": 0, "used": api_count, "unlimited": False}
    
    return {
        "allowed": api_count < limit,
        "limit": limit,
        "used": api_count,
        "unlimited": False
    }
