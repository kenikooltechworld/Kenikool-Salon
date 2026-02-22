"""
Loyalty program API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional
from bson import ObjectId
from datetime import datetime
import logging

from app.api.dependencies import get_current_user, get_tenant_id
from app.database import Database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/loyalty", tags=["loyalty"])


def get_db():
    """Get database instance"""
    return Database.get_db()


def calculate_tier_and_progress(lifetime_points: int) -> tuple:
    """Calculate tier and progress based on lifetime points"""
    # Tier thresholds
    tiers = {
        "bronze": {"min": 0, "max": 999},
        "silver": {"min": 1000, "max": 4999},
        "gold": {"min": 5000, "max": 9999},
        "platinum": {"min": 10000, "max": float("inf")},
    }
    
    current_tier = "bronze"
    tier_progress = 0
    
    for tier_name, tier_range in tiers.items():
        if tier_range["min"] <= lifetime_points < tier_range["max"]:
            current_tier = tier_name
            # Calculate progress to next tier
            if tier_name != "platinum":
                next_tier_min = tier_range["max"]
                progress_in_tier = lifetime_points - tier_range["min"]
                tier_size = tier_range["max"] - tier_range["min"]
                tier_progress = round((progress_in_tier / tier_size) * 100, 2)
            else:
                tier_progress = 100
            break
    
    return current_tier, tier_progress


@router.get("/balance/{client_id}", response_model=dict)
async def get_loyalty_balance(
    client_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get loyalty balance for a client"""
    db = get_db()
    
    try:
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Get loyalty balance
        loyalty_account = db.loyalty_accounts.find_one({
            "client_id": client_id,
            "tenant_id": tenant_id,
        })
        
        if not loyalty_account:
            # Create default loyalty account if it doesn't exist
            loyalty_account = {
                "client_id": client_id,
                "tenant_id": tenant_id,
                "points_balance": 0,
                "tier": "bronze",
                "total_points_earned": 0,
                "total_points_redeemed": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            db.loyalty_accounts.insert_one(loyalty_account)
        
        lifetime_points = loyalty_account.get("total_points_earned", 0)
        tier, tier_progress = calculate_tier_and_progress(lifetime_points)
        
        return {
            "client_id": client_id,
            "points_balance": loyalty_account.get("points_balance", 0),
            "lifetime_points": lifetime_points,
            "tier": tier,
            "tier_progress": {
                "current_tier": tier,
                "progress_percentage": tier_progress,
                "points_to_next_tier": max(0, (
                    1000 if tier == "bronze" else
                    5000 if tier == "silver" else
                    10000 if tier == "gold" else
                    float("inf")
                ) - lifetime_points),
                "tier_benefits": {
                    "bronze": {"discount": 0, "points_multiplier": 1.0},
                    "silver": {"discount": 5, "points_multiplier": 1.25},
                    "gold": {"discount": 10, "points_multiplier": 1.5},
                    "platinum": {"discount": 15, "points_multiplier": 2.0},
                }.get(tier, {}),
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting loyalty balance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{client_id}", response_model=dict)
async def get_loyalty_history(
    client_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get loyalty transaction history for a client"""
    db = get_db()
    
    try:
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Get loyalty transactions
        total = db.loyalty_transactions.count_documents({
            "client_id": client_id,
            "tenant_id": tenant_id,
        })
        
        transactions = list(db.loyalty_transactions.find({
            "client_id": client_id,
            "tenant_id": tenant_id,
        }).sort("created_at", -1).skip(offset).limit(limit))
        
        # Convert ObjectIds to strings
        for tx in transactions:
            tx["id"] = str(tx["_id"])
            del tx["_id"]
        
        # Calculate totals
        total_earned = sum(tx.get("points", 0) for tx in transactions if tx.get("type") == "earn")
        total_redeemed = sum(tx.get("points", 0) for tx in transactions if tx.get("type") == "redeem")
        
        # Get current balance
        loyalty_account = db.loyalty_accounts.find_one({
            "client_id": client_id,
            "tenant_id": tenant_id,
        })
        current_balance = loyalty_account.get("points_balance", 0) if loyalty_account else 0
        
        return {
            "transactions": transactions,
            "total_earned": total_earned,
            "total_redeemed": total_redeemed,
            "current_balance": current_balance,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting loyalty history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/earn", response_model=dict)
async def earn_loyalty_points(
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Earn loyalty points"""
    db = get_db()
    
    try:
        client_id = data.get("client_id")
        points = data.get("points", 0)
        reason = data.get("reason", "booking")
        
        if not client_id or points <= 0:
            raise HTTPException(status_code=400, detail="Invalid client_id or points")
        
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Get or create loyalty account
        loyalty_account = db.loyalty_accounts.find_one({
            "client_id": client_id,
            "tenant_id": tenant_id,
        })
        
        if not loyalty_account:
            loyalty_account = {
                "client_id": client_id,
                "tenant_id": tenant_id,
                "points_balance": 0,
                "tier": "bronze",
                "total_points_earned": 0,
                "total_points_redeemed": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            db.loyalty_accounts.insert_one(loyalty_account)
        
        # Update loyalty account
        new_balance = loyalty_account.get("points_balance", 0) + points
        new_earned = loyalty_account.get("total_points_earned", 0) + points
        
        db.loyalty_accounts.update_one(
            {"_id": loyalty_account["_id"]},
            {
                "$set": {
                    "points_balance": new_balance,
                    "total_points_earned": new_earned,
                    "updated_at": datetime.utcnow(),
                }
            }
        )
        
        # Record transaction
        transaction = {
            "client_id": client_id,
            "tenant_id": tenant_id,
            "type": "earn",
            "points": points,
            "reason": reason,
            "balance_after": new_balance,
            "created_at": datetime.utcnow(),
        }
        result = db.loyalty_transactions.insert_one(transaction)
        transaction["id"] = str(result.inserted_id)
        
        return transaction
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error earning loyalty points: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/redeem", response_model=dict)
async def redeem_loyalty_points(
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Redeem loyalty points"""
    db = get_db()
    
    try:
        client_id = data.get("client_id")
        points = data.get("points", 0)
        reason = data.get("reason", "reward")
        
        if not client_id or points <= 0:
            raise HTTPException(status_code=400, detail="Invalid client_id or points")
        
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Get loyalty account
        loyalty_account = db.loyalty_accounts.find_one({
            "client_id": client_id,
            "tenant_id": tenant_id,
        })
        
        if not loyalty_account:
            raise HTTPException(status_code=400, detail="No loyalty account found")
        
        current_balance = loyalty_account.get("points_balance", 0)
        if current_balance < points:
            raise HTTPException(status_code=400, detail="Insufficient loyalty points")
        
        # Update loyalty account
        new_balance = current_balance - points
        new_redeemed = loyalty_account.get("total_points_redeemed", 0) + points
        
        db.loyalty_accounts.update_one(
            {"_id": loyalty_account["_id"]},
            {
                "$set": {
                    "points_balance": new_balance,
                    "total_points_redeemed": new_redeemed,
                    "updated_at": datetime.utcnow(),
                }
            }
        )
        
        # Record transaction
        transaction = {
            "client_id": client_id,
            "tenant_id": tenant_id,
            "type": "redeem",
            "points": points,
            "reason": reason,
            "balance_after": new_balance,
            "created_at": datetime.utcnow(),
        }
        result = db.loyalty_transactions.insert_one(transaction)
        transaction["id"] = str(result.inserted_id)
        
        return transaction
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error redeeming loyalty points: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rewards", response_model=list)
async def list_loyalty_rewards(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    active_only: bool = Query(True),
):
    """List loyalty rewards"""
    db = get_db()
    
    try:
        filters = {"tenant_id": tenant_id}
        if active_only:
            filters["is_active"] = True
        
        rewards = list(db.loyalty_rewards.find(filters))
        
        # Convert ObjectIds to strings
        for reward in rewards:
            reward["id"] = str(reward["_id"])
            del reward["_id"]
        
        return rewards
    except Exception as e:
        logger.error(f"Error listing loyalty rewards: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rewards", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_loyalty_reward(
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Create a loyalty reward"""
    db = get_db()
    
    try:
        reward = {
            "tenant_id": tenant_id,
            "name": data.get("name"),
            "description": data.get("description"),
            "points_required": data.get("points_required", 0),
            "discount_amount": data.get("discount_amount", 0),
            "discount_percentage": data.get("discount_percentage", 0),
            "is_active": data.get("is_active", True),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        result = db.loyalty_rewards.insert_one(reward)
        reward["id"] = str(result.inserted_id)
        del reward["_id"]
        
        return reward
    except Exception as e:
        logger.error(f"Error creating loyalty reward: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/account", response_model=dict)
async def get_loyalty_account(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get current user's loyalty account"""
    db = get_db()
    
    try:
        user_id = current_user.get("id")
        
        # Get or create loyalty account
        loyalty_account = db.loyalty_accounts.find_one({
            "user_id": user_id,
            "tenant_id": tenant_id,
        })
        
        if not loyalty_account:
            loyalty_account = {
                "user_id": user_id,
                "tenant_id": tenant_id,
                "points_balance": 0,
                "tier": "bronze",
                "total_points_earned": 0,
                "total_points_redeemed": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            db.loyalty_accounts.insert_one(loyalty_account)
        
        lifetime_points = loyalty_account.get("total_points_earned", 0)
        tier, tier_progress = calculate_tier_and_progress(lifetime_points)
        
        return {
            "id": str(loyalty_account.get("_id", "")),
            "points_balance": loyalty_account.get("points_balance", 0),
            "lifetime_points": lifetime_points,
            "tier": tier,
            "tier_progress": tier_progress,
        }
    except Exception as e:
        logger.error(f"Error getting loyalty account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/points/balance", response_model=dict)
async def get_points_balance(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get current user's points balance"""
    db = get_db()
    
    try:
        user_id = current_user.get("id")
        
        loyalty_account = db.loyalty_accounts.find_one({
            "user_id": user_id,
            "tenant_id": tenant_id,
        })
        
        if not loyalty_account:
            return {
                "currentPoints": 0,
                "pointsToNextTier": 1000,
            }
        
        current_points = loyalty_account.get("current_points", 0)
        tier = loyalty_account.get("current_tier", "bronze")
        tier_thresholds = {
            "bronze": 0,
            "silver": 1000,
            "gold": 5000,
            "platinum": 10000,
        }
        next_tier_threshold = tier_thresholds.get(tier, 0)
        points_to_next = max(0, next_tier_threshold - current_points)
        
        return {
            "currentPoints": current_points,
            "pointsToNextTier": points_to_next,
        }
    except Exception as e:
        logger.error(f"Error getting points balance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tier", response_model=dict)
async def get_loyalty_tier(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get current user's loyalty tier information"""
    db = get_db()
    
    try:
        user_id = current_user.get("id")
        
        loyalty_account = db.loyalty_accounts.find_one({
            "user_id": user_id,
            "tenant_id": tenant_id,
        })
        
        if not loyalty_account:
            tier = "bronze"
        else:
            tier = loyalty_account.get("current_tier", "bronze")
        
        tier_benefits = {
            "bronze": {
                "minPoints": 0,
                "discountPercentage": 5,
                "priorityBooking": False,
                "exclusiveRewards": False,
                "birthdayBonus": 50,
                "anniversaryBonus": 50,
                "freeServicePerYear": 0,
            },
            "silver": {
                "minPoints": 1000,
                "discountPercentage": 10,
                "priorityBooking": True,
                "exclusiveRewards": False,
                "birthdayBonus": 100,
                "anniversaryBonus": 100,
                "freeServicePerYear": 1,
            },
            "gold": {
                "minPoints": 5000,
                "discountPercentage": 15,
                "priorityBooking": True,
                "exclusiveRewards": True,
                "birthdayBonus": 200,
                "anniversaryBonus": 200,
                "freeServicePerYear": 2,
            },
            "platinum": {
                "minPoints": 10000,
                "discountPercentage": 20,
                "priorityBooking": True,
                "exclusiveRewards": True,
                "birthdayBonus": 500,
                "anniversaryBonus": 500,
                "freeServicePerYear": 4,
            },
        }
        
        return {
            "tier": tier,
            "minPoints": tier_benefits[tier]["minPoints"],
            "benefits": tier_benefits[tier],
        }
    except Exception as e:
        logger.error(f"Error getting loyalty tier: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tiers/{tier}/benefits", response_model=dict)
async def get_tier_benefits(tier: str):
    """Get benefits for a specific tier"""
    tier_benefits = {
        "bronze": {
            "minPoints": 0,
            "discountPercentage": 5,
            "priorityBooking": False,
            "exclusiveRewards": False,
            "birthdayBonus": 50,
            "anniversaryBonus": 50,
            "freeServicePerYear": 0,
        },
        "silver": {
            "minPoints": 1000,
            "discountPercentage": 10,
            "priorityBooking": True,
            "exclusiveRewards": False,
            "birthdayBonus": 100,
            "anniversaryBonus": 100,
            "freeServicePerYear": 1,
        },
        "gold": {
            "minPoints": 5000,
            "discountPercentage": 15,
            "priorityBooking": True,
            "exclusiveRewards": True,
            "birthdayBonus": 200,
            "anniversaryBonus": 200,
            "freeServicePerYear": 2,
        },
        "platinum": {
            "minPoints": 10000,
            "discountPercentage": 20,
            "priorityBooking": True,
            "exclusiveRewards": True,
            "birthdayBonus": 500,
            "anniversaryBonus": 500,
            "freeServicePerYear": 4,
        },
    }
    
    if tier not in tier_benefits:
        raise HTTPException(status_code=404, detail="Tier not found")
    
    return tier_benefits[tier]


@router.get("/points/history", response_model=list)
async def get_points_history(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """Get user's points earning history"""
    db = get_db()
    
    try:
        user_id = current_user.get("id")
        
        transactions = list(db.loyalty_transactions.find({
            "user_id": user_id,
            "tenant_id": tenant_id,
        }).sort("created_at", -1).skip(offset).limit(limit))
        
        for tx in transactions:
            tx["id"] = str(tx.get("_id", ""))
        
        return transactions
    except Exception as e:
        logger.error(f"Error getting points history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/points/calculate", response_model=dict)
async def calculate_booking_points(
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Calculate points for a booking"""
    db = get_db()
    
    try:
        amount = data.get("amount", 0)
        
        # Base calculation: 1 point per dollar
        points = int(amount)
        bonus_points = 0
        
        # Get user's tier for bonus multiplier
        user_id = current_user.get("id")
        loyalty_account = db.loyalty_accounts.find_one({
            "user_id": user_id,
            "tenant_id": tenant_id,
        })
        
        if loyalty_account:
            tier_multipliers = {
                "bronze": 1.0,
                "silver": 1.1,
                "gold": 1.25,
                "platinum": 1.5,
            }
            multiplier = tier_multipliers.get(loyalty_account.get("current_tier", "bronze"), 1.0)
            bonus_points = int((points * multiplier) - points)
        
        return {
            "points": points,
            "bonusPoints": bonus_points,
        }
    except Exception as e:
        logger.error(f"Error calculating booking points: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/points/expiration", response_model=dict)
async def get_points_expiration(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get points expiration information"""
    return {
        "expiringPoints": 0,
        "expirationDate": datetime.utcnow(),
    }


@router.get("/transactions", response_model=list)
async def get_transactions(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """Get user's loyalty transactions"""
    db = get_db()
    
    try:
        user_id = current_user.get("id")
        
        transactions = list(db.loyalty_transactions.find({
            "user_id": user_id,
            "tenant_id": tenant_id,
        }).sort("created_at", -1).skip(offset).limit(limit))
        
        for tx in transactions:
            tx["id"] = str(tx.get("_id", ""))
        
        return transactions
    except Exception as e:
        logger.error(f"Error getting transactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transactions/{transaction_id}", response_model=dict)
async def get_transaction(
    transaction_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get transaction details"""
    db = get_db()
    
    try:
        user_id = current_user.get("id")
        
        transaction = db.loyalty_transactions.find_one({
            "_id": ObjectId(transaction_id),
            "user_id": user_id,
            "tenant_id": tenant_id,
        })
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        transaction["id"] = str(transaction.get("_id", ""))
        return transaction
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting transaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics", response_model=dict)
async def get_loyalty_analytics(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get loyalty analytics for user"""
    db = get_db()
    
    try:
        user_id = current_user.get("id")
        
        loyalty_account = db.loyalty_accounts.find_one({
            "user_id": user_id,
            "tenant_id": tenant_id,
        })
        
        if not loyalty_account:
            return {
                "totalPointsEarned": 0,
                "totalPointsRedeemed": 0,
                "currentPoints": 0,
                "currentTier": "bronze",
            }
        
        return {
            "totalPointsEarned": loyalty_account.get("total_points_earned", 0),
            "totalPointsRedeemed": loyalty_account.get("total_points_redeemed", 0),
            "currentPoints": loyalty_account.get("points_balance", 0),
            "currentTier": loyalty_account.get("current_tier", "bronze"),
        }
    except Exception as e:
        logger.error(f"Error getting loyalty analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/points-trends", response_model=dict)
async def get_points_trends(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    days: int = Query(30, ge=1, le=365),
):
    """Get points earning trends"""
    db = get_db()
    
    try:
        from datetime import timedelta
        user_id = current_user.get("id")
        start_date = datetime.utcnow() - timedelta(days=days)
        
        transactions = list(db.loyalty_transactions.find({
            "user_id": user_id,
            "tenant_id": tenant_id,
            "created_at": {"$gte": start_date},
        }).sort("created_at", -1))
        
        for tx in transactions:
            tx["id"] = str(tx.get("_id", ""))
        
        return {"transactions": transactions}
    except Exception as e:
        logger.error(f"Error getting points trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/redemption-trends", response_model=dict)
async def get_redemption_trends(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    days: int = Query(30, ge=1, le=365),
):
    """Get reward redemption trends"""
    db = get_db()
    
    try:
        from datetime import timedelta
        user_id = current_user.get("id")
        start_date = datetime.utcnow() - timedelta(days=days)
        
        transactions = list(db.loyalty_transactions.find({
            "user_id": user_id,
            "tenant_id": tenant_id,
            "type": "redemption",
            "created_at": {"$gte": start_date},
        }).sort("created_at", -1))
        
        for tx in transactions:
            tx["id"] = str(tx.get("_id", ""))
        
        return {"transactions": transactions}
    except Exception as e:
        logger.error(f"Error getting redemption trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/tier-progression", response_model=dict)
async def get_tier_progression_analytics(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get tier progression analytics"""
    db = get_db()
    
    try:
        user_id = current_user.get("id")
        
        loyalty_account = db.loyalty_accounts.find_one({
            "user_id": user_id,
            "tenant_id": tenant_id,
        })
        
        if not loyalty_account:
            return {
                "currentTier": "bronze",
                "currentPoints": 0,
                "tierHistory": [],
            }
        
        return {
            "currentTier": loyalty_account.get("current_tier", "bronze"),
            "currentPoints": loyalty_account.get("points_balance", 0),
            "tierHistory": loyalty_account.get("tier_history", []),
        }
    except Exception as e:
        logger.error(f"Error getting tier progression analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
