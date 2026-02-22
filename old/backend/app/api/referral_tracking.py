"""
Referral Tracking API

Endpoints for tracking referrals, generating referral codes, and managing referral rewards.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import logging
import secrets
import string

from app.database import Database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/marketplace/referrals", tags=["referrals"])


# ============================================================================
# Pydantic Models
# ============================================================================

class ReferralCreate(BaseModel):
    """Create referral tracking"""
    tenant_id: str
    visitor_ip: str
    visitor_user_agent: str


class ReferralResponse(BaseModel):
    """Referral response"""
    referral_code: str
    tenant_id: str
    created_at: str
    expires_at: str
    salon_url: str


class ReferralConversion(BaseModel):
    """Record referral conversion"""
    referral_code: str
    booking_id: str
    booking_reference: str


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/track", response_model=ReferralResponse)
async def track_referral(request_data: ReferralCreate):
    """
    Create referral tracking record
    
    - Generates unique referral code
    - Stores visitor information
    - Sets 30-day expiration
    - Returns referral code and salon URL
    """
    try:
        db = Database.get_db()
        
        # Generate unique referral code
        referral_code = generate_referral_code()
        
        # Check if code already exists (unlikely but possible)
        while db.referral_tracking.find_one({"referral_code": referral_code}):
            referral_code = generate_referral_code()
        
        # Create referral tracking record
        expires_at = datetime.utcnow() + timedelta(days=30)
        
        referral_data = {
            "referral_code": referral_code,
            "tenant_id": request_data.tenant_id,
            "visitor_ip": request_data.visitor_ip,
            "visitor_user_agent": request_data.visitor_user_agent,
            "clicked_at": datetime.utcnow(),
            "expires_at": expires_at,
            "converted_at": None,
            "booking_id": None,
            "booking_reference": None,
            "commission_earned": 0,
            "status": "active",
            "created_at": datetime.utcnow()
        }
        
        result = db.referral_tracking.insert_one(referral_data)
        
        # Get salon info
        salon = db.tenants.find_one({"_id": request_data.tenant_id})
        if not salon:
            raise HTTPException(status_code=404, detail="Salon not found")
        
        # Build salon URL with referral code
        salon_url = f"{salon.get('website_url', 'https://example.com')}?ref={referral_code}"
        
        return ReferralResponse(
            referral_code=referral_code,
            tenant_id=request_data.tenant_id,
            created_at=referral_data["clicked_at"].isoformat(),
            expires_at=expires_at.isoformat(),
            salon_url=salon_url
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error tracking referral: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{code}")
async def get_referral(code: str):
    """
    Get referral details and redirect to salon site
    
    - Validates referral code
    - Checks expiration
    - Returns salon URL with tracking
    """
    try:
        db = Database.get_db()
        
        # Get referral record
        referral = db.referral_tracking.find_one({"referral_code": code})
        
        if not referral:
            raise HTTPException(status_code=404, detail="Referral code not found")
        
        # Check expiration
        if referral["expires_at"] < datetime.utcnow():
            raise HTTPException(status_code=410, detail="Referral code has expired")
        
        # Get salon info
        salon = db.tenants.find_one({"_id": referral["tenant_id"]})
        if not salon:
            raise HTTPException(status_code=404, detail="Salon not found")
        
        # Update click count
        db.referral_tracking.update_one(
            {"_id": referral["_id"]},
            {
                "$inc": {"click_count": 1},
                "$set": {"last_clicked_at": datetime.utcnow()}
            }
        )
        
        # Return salon URL
        return {
            "salon_id": str(referral["tenant_id"]),
            "salon_name": salon.get("name"),
            "salon_url": salon.get("website_url", "https://example.com"),
            "referral_code": code,
            "discount_percentage": salon.get("referral_discount", 5)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting referral: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/convert")
async def record_referral_conversion(conversion_data: ReferralConversion):
    """
    Record referral conversion (booking made through referral)
    
    - Validates referral code
    - Links booking to referral
    - Calculates commission
    - Updates referral status
    """
    try:
        db = Database.get_db()
        
        # Get referral record
        referral = db.referral_tracking.find_one({"referral_code": conversion_data.referral_code})
        
        if not referral:
            raise HTTPException(status_code=404, detail="Referral code not found")
        
        # Check expiration
        if referral["expires_at"] < datetime.utcnow():
            raise HTTPException(status_code=410, detail="Referral code has expired")
        
        # Get booking
        booking = db.marketplace_bookings.find_one({
            "booking_reference": conversion_data.booking_reference
        })
        
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        # Get salon commission rate
        salon = db.tenants.find_one({"_id": referral["tenant_id"]})
        referral_commission_rate = salon.get("referral_commission_rate", 0.05) if salon else 0.05
        
        # Calculate commission
        commission_earned = booking["final_price"] * referral_commission_rate
        
        # Update referral record
        db.referral_tracking.update_one(
            {"_id": referral["_id"]},
            {
                "$set": {
                    "converted_at": datetime.utcnow(),
                    "booking_id": str(booking["_id"]),
                    "booking_reference": conversion_data.booking_reference,
                    "commission_earned": commission_earned,
                    "status": "converted"
                }
            }
        )
        
        # Record commission transaction
        db.commission_transactions.insert_one({
            "tenant_id": str(referral["tenant_id"]),
            "booking_id": str(booking["_id"]),
            "booking_reference": conversion_data.booking_reference,
            "referral_code": conversion_data.referral_code,
            "transaction_type": "referral",
            "amount": booking["final_price"],
            "commission_rate": referral_commission_rate,
            "commission_amount": commission_earned,
            "platform_fee": commission_earned * 0.02,
            "net_amount": commission_earned * 0.98,
            "status": "pending",
            "created_at": datetime.utcnow()
        })
        
        logger.info(f"Referral conversion recorded: {conversion_data.referral_code} -> {conversion_data.booking_reference}")
        
        return {
            "message": "Referral conversion recorded",
            "referral_code": conversion_data.referral_code,
            "booking_reference": conversion_data.booking_reference,
            "commission_earned": commission_earned
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording referral conversion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/{tenant_id}")
async def get_referral_stats(tenant_id: str):
    """
    Get referral statistics for a salon
    """
    try:
        db = Database.get_db()
        
        # Get all referrals for salon
        referrals = list(db.referral_tracking.find({"tenant_id": tenant_id}))
        
        # Calculate stats
        total_referrals = len(referrals)
        active_referrals = len([r for r in referrals if r["status"] == "active"])
        converted_referrals = len([r for r in referrals if r["status"] == "converted"])
        total_commission = sum(r.get("commission_earned", 0) for r in referrals)
        
        # Get top referral codes
        top_referrals = sorted(
            referrals,
            key=lambda x: x.get("click_count", 0),
            reverse=True
        )[:5]
        
        return {
            "tenant_id": tenant_id,
            "total_referrals": total_referrals,
            "active_referrals": active_referrals,
            "converted_referrals": converted_referrals,
            "conversion_rate": (converted_referrals / total_referrals * 100) if total_referrals > 0 else 0,
            "total_commission": total_commission,
            "top_referrals": [
                {
                    "code": r["referral_code"],
                    "clicks": r.get("click_count", 0),
                    "conversions": 1 if r["status"] == "converted" else 0,
                    "commission": r.get("commission_earned", 0)
                }
                for r in top_referrals
            ]
        }
    
    except Exception as e:
        logger.error(f"Error getting referral stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list/{tenant_id}")
async def list_referrals(
    tenant_id: str,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """
    List referrals for a salon
    """
    try:
        db = Database.get_db()
        
        query = {"tenant_id": tenant_id}
        
        if status:
            query["status"] = status
        
        referrals = list(
            db.referral_tracking.find(query)
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )
        
        # Convert ObjectId to string
        for referral in referrals:
            referral["_id"] = str(referral["_id"])
        
        total = db.referral_tracking.count_documents(query)
        
        return {
            "referrals": referrals,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    except Exception as e:
        logger.error(f"Error listing referrals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Helper Functions
# ============================================================================

def generate_referral_code(length: int = 8) -> str:
    """Generate a unique referral code"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))
