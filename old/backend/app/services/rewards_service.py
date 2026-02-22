from datetime import datetime
from typing import Dict, List, Optional
from bson import ObjectId
from app.database import Database


class RewardsService:
    
    TIER_THRESHOLDS = {
        "bronze": 0,
        "silver": 500,
        "gold": 1500,
        "platinum": 3000
    }
    
    TIER_BENEFITS = {
        "bronze": {"discount": 0, "points_multiplier": 1},
        "silver": {"discount": 5, "points_multiplier": 1.25},
        "gold": {"discount": 10, "points_multiplier": 1.5},
        "platinum": {"discount": 15, "points_multiplier": 2}
    }
    
    @staticmethod
    def get_or_create_loyalty_account(tenant_id: str, client_id: str) -> Dict:
        """Get or create loyalty account"""
        db = Database.get_db()
        
        account = db.loyalty_accounts.find_one({
            "tenant_id": tenant_id,
            "client_id": ObjectId(client_id)
        })
        
        if account:
            account["_id"] = str(account["_id"])
            return account
        
        # Create new account
        account = {
            "tenant_id": tenant_id,
            "client_id": ObjectId(client_id),
            "points_balance": 0,
            "tier": "bronze",
            "lifetime_points": 0,
            "created_at": datetime.utcnow()
        }
        
        result = db.loyalty_accounts.insert_one(account)
        account["_id"] = str(result.inserted_id)
        
        return account
    
    @staticmethod
    def add_points(tenant_id: str, client_id: str, points: int, reason: str) -> Dict:
        """Add loyalty points"""
        db = Database.get_db()
        
        account = RewardsService.get_or_create_loyalty_account(tenant_id, client_id)
        
        new_balance = account.get("points_balance", 0) + points
        new_lifetime = account.get("lifetime_points", 0) + points
        
        # Determine tier
        tier = "bronze"
        for t, threshold in RewardsService.TIER_THRESHOLDS.items():
            if new_lifetime >= threshold:
                tier = t
        
        db.loyalty_accounts.update_one(
            {
                "tenant_id": tenant_id,
                "client_id": ObjectId(client_id)
            },
            {
                "$set": {
                    "points_balance": new_balance,
                    "lifetime_points": new_lifetime,
                    "tier": tier
                }
            },
            upsert=True
        )
        
        # Log transaction
        db.loyalty_transactions.insert_one({
            "tenant_id": tenant_id,
            "client_id": ObjectId(client_id),
            "points": points,
            "reason": reason,
            "created_at": datetime.utcnow()
        })
        
        return {
            "points_added": points,
            "new_balance": new_balance,
            "tier": tier
        }
    
    @staticmethod
    def redeem_points(tenant_id: str, client_id: str, points: int, reward_id: str) -> Dict:
        """Redeem loyalty points"""
        db = Database.get_db()
        
        account = db.loyalty_accounts.find_one({
            "tenant_id": tenant_id,
            "client_id": ObjectId(client_id)
        })
        
        if not account:
            raise ValueError("Loyalty account not found")
        
        if account.get("points_balance", 0) < points:
            raise ValueError("Insufficient points")
        
        new_balance = account["points_balance"] - points
        
        db.loyalty_accounts.update_one(
            {
                "tenant_id": tenant_id,
                "client_id": ObjectId(client_id)
            },
            {
                "$set": {"points_balance": new_balance}
            }
        )
        
        # Log redemption
        db.loyalty_redemptions.insert_one({
            "tenant_id": tenant_id,
            "client_id": ObjectId(client_id),
            "reward_id": reward_id,
            "points_redeemed": points,
            "created_at": datetime.utcnow()
        })
        
        return {
            "points_redeemed": points,
            "new_balance": new_balance
        }
    
    @staticmethod
    def get_available_rewards(tenant_id: str) -> List[Dict]:
        """Get available rewards"""
        db = Database.get_db()
        
        rewards = list(db.rewards.find({
            "tenant_id": tenant_id,
            "is_active": True
        }))
        
        return rewards
    
    @staticmethod
    def get_tier_benefits(tier: str) -> Dict:
        """Get benefits for tier"""
        return RewardsService.TIER_BENEFITS.get(tier, {})
    
    @staticmethod
    def get_loyalty_history(tenant_id: str, client_id: str) -> Dict:
        """Get loyalty history"""
        db = Database.get_db()
        
        transactions = list(db.loyalty_transactions.find({
            "tenant_id": tenant_id,
            "client_id": ObjectId(client_id)
        }).sort("created_at", -1).limit(50))
        
        redemptions = list(db.loyalty_redemptions.find({
            "tenant_id": tenant_id,
            "client_id": ObjectId(client_id)
        }).sort("created_at", -1).limit(50))
        
        return {
            "transactions": transactions,
            "redemptions": redemptions
        }
