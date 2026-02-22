"""
Tenant API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
import logging
from app.models.user import ReferralSettings
from app.api.dependencies import get_current_user, get_tenant_id
from app.database import Database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tenants", tags=["tenants"])


@router.get("/me")
async def get_current_tenant(
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get current tenant information"""
    try:
        db = Database.get_db()
        tenant = db.tenants.find_one({"_id": ObjectId(tenant_id)})
        
        if not tenant:
            # Return a default tenant if not found
            return {
                "id": tenant_id,
                "salon_name": "Salon",
                "created_at": None,
                "updated_at": None
            }
        
        # Convert ObjectId to string for JSON serialization
        tenant["id"] = str(tenant["_id"])
        del tenant["_id"]
        return tenant
    except Exception as e:
        logger.error(f"Error getting current tenant: {e}")
        # Return a default tenant on error
        return {
            "id": tenant_id,
            "salon_name": "Salon",
            "created_at": None,
            "updated_at": None
        }


@router.get("/referral-settings")
async def get_referral_settings(
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get referral settings for tenant"""
    try:
        db = Database.get_db()
        tenant = db.tenants.find_one({"_id": ObjectId(tenant_id)})
        
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        # Return referral settings or defaults
        referral_settings = tenant.get("referral_settings", {
            "enabled": True,
            "reward_type": "fixed",
            "reward_amount": 1000,
            "min_booking_amount": 5000,
            "expiration_days": 90,
            "max_referrals_per_client": 50,
            "max_rewards_per_month": 100000
        })
        
        return referral_settings
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/referral-settings")
async def update_referral_settings(
    settings: ReferralSettings,
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Update referral settings for tenant"""
    try:
        # Verify user is tenant owner
        if current_user.get("role") != "owner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only tenant owners can update referral settings"
            )
        
        db = Database.get_db()
        
        # Update tenant with new referral settings
        result = db.tenants.update_one(
            {"_id": ObjectId(tenant_id)},
            {
                "$set": {
                    "referral_settings": settings.dict(),
                    "updated_at": Database.get_db().command("serverStatus")["localTime"]
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        return {
            "success": True,
            "message": "Referral settings updated successfully",
            "settings": settings.dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/referral-settings/reset")
async def reset_referral_settings(
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Reset referral settings to defaults"""
    try:
        # Verify user is tenant owner
        if current_user.get("role") != "owner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only tenant owners can reset referral settings"
            )
        
        db = Database.get_db()
        
        # Reset to default settings
        default_settings = {
            "enabled": True,
            "reward_type": "fixed",
            "reward_amount": 1000,
            "min_booking_amount": 5000,
            "expiration_days": 90,
            "max_referrals_per_client": 50,
            "max_rewards_per_month": 100000
        }
        
        result = db.tenants.update_one(
            {"_id": ObjectId(tenant_id)},
            {
                "$set": {
                    "referral_settings": default_settings,
                    "updated_at": Database.get_db().command("serverStatus")["localTime"]
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        return {
            "success": True,
            "message": "Referral settings reset to defaults",
            "settings": default_settings
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
