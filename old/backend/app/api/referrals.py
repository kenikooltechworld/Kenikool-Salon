"""
Referral program API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional
from bson import ObjectId
from datetime import datetime
import logging
import uuid

from app.api.dependencies import get_current_user, get_tenant_id
from app.database import Database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/referrals", tags=["referrals"])


def get_db():
    """Get database instance"""
    return Database.get_db()


@router.get("", response_model=list)
async def list_referrals(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    referrer_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List referrals"""
    db = get_db()
    
    try:
        filters = {"tenant_id": tenant_id}
        
        if referrer_id:
            filters["referrer_id"] = referrer_id
        
        if status:
            filters["status"] = status
        
        referrals = list(db.referrals.find(filters).sort("created_at", -1).skip(offset).limit(limit))
        
        # Convert ObjectIds to strings
        for ref in referrals:
            ref["id"] = str(ref["_id"])
            del ref["_id"]
        
        return referrals
    except Exception as e:
        logger.error(f"Error listing referrals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=dict)
async def get_referral_stats(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get referral statistics"""
    db = get_db()
    
    try:
        total_referrals = db.referrals.count_documents({"tenant_id": tenant_id})
        
        successful_referrals = db.referrals.count_documents({
            "tenant_id": tenant_id,
            "status": "completed",
        })
        
        pending_referrals = db.referrals.count_documents({
            "tenant_id": tenant_id,
            "status": "pending",
        })
        
        total_rewards = 0
        referrals = list(db.referrals.find({"tenant_id": tenant_id}))
        for ref in referrals:
            total_rewards += ref.get("reward_amount", 0)
        
        return {
            "total_referrals": total_referrals,
            "successful_referrals": successful_referrals,
            "pending_referrals": pending_referrals,
            "total_rewards": total_rewards,
        }
    except Exception as e:
        logger.error(f"Error getting referral stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_referral(
    referrer_id: str = Query(...),
    referred_id: str = Query(...),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Create a referral"""
    db = get_db()
    
    try:
        # Verify both clients exist
        referrer = db.clients.find_one({
            "_id": ObjectId(referrer_id),
            "tenant_id": tenant_id,
        })
        
        referred = db.clients.find_one({
            "_id": ObjectId(referred_id),
            "tenant_id": tenant_id,
        })
        
        if not referrer or not referred:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Create referral
        referral = {
            "tenant_id": tenant_id,
            "referrer_id": referrer_id,
            "referred_id": referred_id,
            "status": "pending",
            "reward_amount": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        result = db.referrals.insert_one(referral)
        referral["id"] = str(result.inserted_id)
        del referral["_id"]
        
        return referral
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating referral: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-link", response_model=dict)
async def generate_referral_link(
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Generate a referral link for a client"""
    db = get_db()
    
    try:
        client_id = data.get("client_id")
        
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Generate unique referral code
        referral_code = str(uuid.uuid4())[:8].upper()
        
        # Store referral link
        referral_link = {
            "tenant_id": tenant_id,
            "client_id": client_id,
            "code": referral_code,
            "link": f"https://salon.example.com/referral/{referral_code}",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        db.referral_links.insert_one(referral_link)
        
        return {
            "code": referral_code,
            "link": referral_link["link"],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating referral link: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/redeem", response_model=dict)
async def redeem_referral(
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Redeem a referral reward"""
    db = get_db()
    
    try:
        client_id = data.get("client_id")
        amount = data.get("amount", 0)
        
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Create redemption record
        redemption = {
            "tenant_id": tenant_id,
            "client_id": client_id,
            "amount": amount,
            "status": "completed",
            "created_at": datetime.utcnow(),
        }
        
        result = db.referral_redemptions.insert_one(redemption)
        redemption["id"] = str(result.inserted_id)
        del redemption["_id"]
        
        return redemption
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error redeeming referral: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/{client_id}", response_model=dict)
async def get_referral_dashboard(
    client_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get referral dashboard for a client"""
    db = get_db()
    
    try:
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Get referral link
        referral_link = db.referral_links.find_one({
            "client_id": client_id,
            "tenant_id": tenant_id,
        })
        
        referral_code = referral_link.get("code", "") if referral_link else ""
        referral_link_url = referral_link.get("link", "") if referral_link else ""
        
        # Get referral stats for this client
        total_referrals = db.referrals.count_documents({
            "referrer_id": client_id,
            "tenant_id": tenant_id,
        })
        
        successful_referrals = db.referrals.count_documents({
            "referrer_id": client_id,
            "tenant_id": tenant_id,
            "status": "completed",
        })
        
        pending_referrals = db.referrals.count_documents({
            "referrer_id": client_id,
            "tenant_id": tenant_id,
            "status": "pending",
        })
        
        total_earned = 0
        pending_rewards = 0
        redeemed_rewards = 0
        referrals = list(db.referrals.find({
            "referrer_id": client_id,
            "tenant_id": tenant_id,
        }))
        
        for ref in referrals:
            reward = ref.get("reward_amount", 0)
            total_earned += reward
            if ref.get("status") == "pending":
                pending_rewards += reward
            elif ref.get("status") == "completed":
                redeemed_rewards += reward
        
        return {
            "referral_code": referral_code,
            "referral_link": referral_link_url,
            "total_referrals": total_referrals,
            "successful_referrals": successful_referrals,
            "pending_referrals": pending_referrals,
            "total_rewards_earned": total_earned,
            "pending_rewards": pending_rewards,
            "redeemed_rewards": redeemed_rewards,
            "referral_history": [],
            "conversion_rate": (successful_referrals / total_referrals * 100) if total_referrals > 0 else 0,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting referral dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics", response_model=dict)
async def get_referral_analytics(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get referral analytics for tenant"""
    db = get_db()
    
    try:
        total_referrals = db.referrals.count_documents({"tenant_id": tenant_id})
        
        successful_referrals = db.referrals.count_documents({
            "tenant_id": tenant_id,
            "status": "completed",
        })
        
        total_rewards_paid = 0
        total_pending_rewards = 0
        referrals = list(db.referrals.find({"tenant_id": tenant_id}))
        
        for ref in referrals:
            reward = ref.get("reward_amount", 0)
            if ref.get("status") == "completed":
                total_rewards_paid += reward
            else:
                total_pending_rewards += reward
        
        return {
            "total_referrals": total_referrals,
            "successful_referrals": successful_referrals,
            "conversion_rate": (successful_referrals / total_referrals * 100) if total_referrals > 0 else 0,
            "total_rewards_paid": total_rewards_paid,
            "total_pending_rewards": total_pending_rewards,
            "top_referrers": [],
            "referrals_by_period": [],
        }
    except Exception as e:
        logger.error(f"Error getting referral analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
