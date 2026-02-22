"""
Loyalty Points Service - Business logic for loyalty program
"""
from bson import ObjectId
from datetime import datetime, timezone
from typing import Dict, List, Optional
import logging

from app.database import Database
from app.api.exceptions import NotFoundException, BadRequestException

logger = logging.getLogger(__name__)


class LoyaltyService:
    """Service for managing loyalty points and rewards"""
    
    # Tier thresholds
    TIER_THRESHOLDS = {
        "bronze": 0,
        "silver": 500,
        "gold": 1500,
        "platinum": 3000
    }
    
    @staticmethod
    def get_or_create_account(tenant_id: str, client_id: str) -> Dict:
        """
        Get or create loyalty account for a client
        
        Args:
            tenant_id: Tenant ID
            client_id: Client ID
            
        Returns:
            Dict with loyalty account details
        """
        db = Database.get_db()
        
        # Try to find existing account
        account = db.loyalty_accounts.find_one({
            "tenant_id": tenant_id,
            "client_id": client_id
        })
        
        if account:
            account["id"] = str(account["_id"])
            return account
        
        # Create new account
        account_data = {
            "tenant_id": tenant_id,
            "client_id": client_id,
            "points_balance": 0,
            "lifetime_points": 0,
            "tier": "bronze",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        result = db.loyalty_accounts.insert_one(account_data)
        account_data["id"] = str(result.inserted_id)
        account_data["_id"] = result.inserted_id
        
        logger.info(f"Created loyalty account for client: {client_id}")
        
        return account_data
    
    @staticmethod
    def earn_points(
        tenant_id: str,
        client_id: str,
        points: int,
        reference_type: Optional[str] = None,
        reference_id: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict:
        """
        Award points to a client
        
        Args:
            tenant_id: Tenant ID
            client_id: Client ID
            points: Points to award
            reference_type: Type of reference (booking, purchase, etc)
            reference_id: Reference ID
            description: Transaction description
            
        Returns:
            Dict with transaction details
        """
        db = Database.get_db()
        
        if points <= 0:
            raise BadRequestException("Points must be positive")
        
        # Get or create account
        account = LoyaltyService.get_or_create_account(tenant_id, client_id)
        
        # Calculate new balance
        new_balance = account["points_balance"] + points
        new_lifetime = account["lifetime_points"] + points
        
        # Calculate new tier
        new_tier = LoyaltyService._calculate_tier(new_lifetime)
        
        # Create transaction
        transaction_data = {
            "tenant_id": tenant_id,
            "client_id": client_id,
            "points": points,
            "transaction_type": "earn",
            "reference_type": reference_type,
            "reference_id": reference_id,
            "description": description or f"Earned {points} points",
            "balance_after": new_balance,
            "created_at": datetime.now(timezone.utc)
        }
        
        result = db.loyalty_transactions.insert_one(transaction_data)
        transaction_id = str(result.inserted_id)
        
        # Update account
        db.loyalty_accounts.update_one(
            {"_id": account["_id"]},
            {
                "$set": {
                    "points_balance": new_balance,
                    "lifetime_points": new_lifetime,
                    "tier": new_tier,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        logger.info(f"Client {client_id} earned {points} points. New balance: {new_balance}")
        
        transaction_data["id"] = transaction_id
        transaction_data["_id"] = result.inserted_id
        
        return transaction_data
    
    @staticmethod
    def redeem_points(
        tenant_id: str,
        client_id: str,
        points: int,
        reference_type: Optional[str] = None,
        reference_id: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict:
        """
        Redeem points from a client's account
        
        Args:
            tenant_id: Tenant ID
            client_id: Client ID
            points: Points to redeem
            reference_type: Type of reference
            reference_id: Reference ID
            description: Transaction description
            
        Returns:
            Dict with transaction details
        """
        db = Database.get_db()
        
        if points <= 0:
            raise BadRequestException("Points must be positive")
        
        # Get account
        account = LoyaltyService.get_or_create_account(tenant_id, client_id)
        
        # Check if sufficient balance
        if account["points_balance"] < points:
            raise BadRequestException(
                f"Insufficient points. Balance: {account['points_balance']}, Required: {points}"
            )
        
        # Calculate new balance
        new_balance = account["points_balance"] - points
        
        # Create transaction
        transaction_data = {
            "tenant_id": tenant_id,
            "client_id": client_id,
            "points": -points,  # Negative for redemption
            "transaction_type": "redeem",
            "reference_type": reference_type,
            "reference_id": reference_id,
            "description": description or f"Redeemed {points} points",
            "balance_after": new_balance,
            "created_at": datetime.now(timezone.utc)
        }
        
        result = db.loyalty_transactions.insert_one(transaction_data)
        transaction_id = str(result.inserted_id)
        
        # Update account
        db.loyalty_accounts.update_one(
            {"_id": account["_id"]},
            {
                "$set": {
                    "points_balance": new_balance,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        logger.info(f"Client {client_id} redeemed {points} points. New balance: {new_balance}")
        
        transaction_data["id"] = transaction_id
        transaction_data["_id"] = result.inserted_id
        
        return transaction_data
    
    @staticmethod
    def get_balance(tenant_id: str, client_id: str) -> Dict:
        """
        Get loyalty balance for a client
        
        Args:
            tenant_id: Tenant ID
            client_id: Client ID
            
        Returns:
            Dict with balance information
        """
        account = LoyaltyService.get_or_create_account(tenant_id, client_id)
        
        # Calculate tier progress
        current_tier = account["tier"]
        lifetime_points = account["lifetime_points"]
        
        tier_progress = LoyaltyService._calculate_tier_progress(lifetime_points, current_tier)
        
        return {
            "client_id": client_id,
            "points_balance": account["points_balance"],
            "lifetime_points": lifetime_points,
            "tier": current_tier,
            "tier_progress": tier_progress
        }
    
    @staticmethod
    def get_transaction_history(
        tenant_id: str,
        client_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> Dict:
        """
        Get transaction history for a client
        
        Args:
            tenant_id: Tenant ID
            client_id: Client ID
            limit: Number of transactions to return
            offset: Offset for pagination
            
        Returns:
            Dict with transaction history
        """
        db = Database.get_db()
        
        # Get transactions
        transactions = list(
            db.loyalty_transactions.find({
                "tenant_id": tenant_id,
                "client_id": client_id
            })
            .sort("created_at", -1)
            .skip(offset)
            .limit(limit)
        )
        
        for transaction in transactions:
            transaction["id"] = str(transaction["_id"])
        
        # Calculate totals
        all_transactions = list(db.loyalty_transactions.find({
            "tenant_id": tenant_id,
            "client_id": client_id
        }))
        
        total_earned = sum(t["points"] for t in all_transactions if t["points"] > 0)
        total_redeemed = abs(sum(t["points"] for t in all_transactions if t["points"] < 0))
        
        # Get current balance
        account = LoyaltyService.get_or_create_account(tenant_id, client_id)
        
        return {
            "transactions": transactions,
            "total_earned": total_earned,
            "total_redeemed": total_redeemed,
            "current_balance": account["points_balance"]
        }
    
    @staticmethod
    def _calculate_tier(lifetime_points: int) -> str:
        """Calculate tier based on lifetime points"""
        if lifetime_points >= LoyaltyService.TIER_THRESHOLDS["platinum"]:
            return "platinum"
        elif lifetime_points >= LoyaltyService.TIER_THRESHOLDS["gold"]:
            return "gold"
        elif lifetime_points >= LoyaltyService.TIER_THRESHOLDS["silver"]:
            return "silver"
        else:
            return "bronze"
    
    @staticmethod
    def _calculate_tier_progress(lifetime_points: int, current_tier: str) -> Dict:
        """Calculate progress to next tier"""
        tiers = ["bronze", "silver", "gold", "platinum"]
        current_index = tiers.index(current_tier)
        
        if current_index == len(tiers) - 1:
            # Already at highest tier
            return {
                "current_tier": current_tier,
                "next_tier": None,
                "points_to_next": 0,
                "progress_percentage": 100
            }
        
        next_tier = tiers[current_index + 1]
        current_threshold = LoyaltyService.TIER_THRESHOLDS[current_tier]
        next_threshold = LoyaltyService.TIER_THRESHOLDS[next_tier]
        
        points_to_next = next_threshold - lifetime_points
        progress_percentage = int(
            ((lifetime_points - current_threshold) / (next_threshold - current_threshold)) * 100
        )
        
        return {
            "current_tier": current_tier,
            "next_tier": next_tier,
            "points_to_next": max(0, points_to_next),
            "progress_percentage": min(100, max(0, progress_percentage))
        }
    
    @staticmethod
    def create_reward(
        tenant_id: str,
        name: str,
        description: str,
        points_required: int,
        reward_type: str,
        reward_value: float,
        active: bool = True
    ) -> Dict:
        """Create a loyalty reward"""
        db = Database.get_db()
        
        reward_data = {
            "tenant_id": tenant_id,
            "name": name,
            "description": description,
            "points_required": points_required,
            "reward_type": reward_type,
            "reward_value": reward_value,
            "active": active,
            "created_at": datetime.now(timezone.utc)
        }
        
        result = db.loyalty_rewards.insert_one(reward_data)
        reward_data["id"] = str(result.inserted_id)
        reward_data["_id"] = result.inserted_id
        
        logger.info(f"Created loyalty reward: {name}")
        
        return reward_data
    
    @staticmethod
    def get_rewards(tenant_id: str, active_only: bool = True) -> List[Dict]:
        """Get available loyalty rewards"""
        db = Database.get_db()
        
        query = {"tenant_id": tenant_id}
        if active_only:
            query["active"] = True
        
        rewards = list(db.loyalty_rewards.find(query).sort("points_required", 1))
        
        for reward in rewards:
            reward["id"] = str(reward["_id"])
        
        return rewards
