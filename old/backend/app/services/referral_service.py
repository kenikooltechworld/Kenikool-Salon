from datetime import datetime, timedelta
from typing import Dict, List, Optional
from bson import ObjectId
from app.database import Database
import uuid


class ReferralService:
    
    @staticmethod
    def get_tenant_referral_settings(tenant_id: str) -> Dict:
        """Get referral settings for tenant"""
        db = Database.get_db()
        
        tenant = db.tenants.find_one({"_id": ObjectId(tenant_id)})
        
        if not tenant:
            # Return defaults if tenant not found
            return {
                "enabled": True,
                "reward_type": "fixed",
                "reward_amount": 1000,
                "min_booking_amount": 5000,
                "expiration_days": 90,
                "max_referrals_per_client": 50,
                "max_rewards_per_month": 100000
            }
        
        # Return tenant's referral settings or defaults
        return tenant.get("referral_settings", {
            "enabled": True,
            "reward_type": "fixed",
            "reward_amount": 1000,
            "min_booking_amount": 5000,
            "expiration_days": 90,
            "max_referrals_per_client": 50,
            "max_rewards_per_month": 100000
        })
    
    @staticmethod
    def create_referral_code(
        tenant_id: str,
        client_id: str,
        reward_amount: float = 100,
        max_uses: Optional[int] = None
    ) -> Dict:
        """Create referral code for client"""
        db = Database.get_db()
        
        import uuid
        code = str(uuid.uuid4())[:8].upper()
        
        referral = {
            "tenant_id": tenant_id,
            "client_id": ObjectId(client_id),
            "code": code,
            "reward_amount": reward_amount,
            "max_uses": max_uses,
            "current_uses": 0,
            "status": "active",
            "created_at": datetime.utcnow()
        }
        
        result = db.referrals.insert_one(referral)
        referral["_id"] = str(result.inserted_id)
        
        return referral
    
    @staticmethod
    def use_referral_code(
        tenant_id: str,
        code: str,
        new_client_id: str
    ) -> Dict:
        """Use referral code"""
        db = Database.get_db()
        
        referral = db.referrals.find_one({
            "tenant_id": tenant_id,
            "code": code,
            "status": "active"
        })
        
        if not referral:
            raise ValueError("Invalid referral code")
        
        if referral.get("max_uses") and referral["current_uses"] >= referral["max_uses"]:
            raise ValueError("Referral code has reached maximum uses")
        
        # Update referral
        db.referrals.update_one(
            {"_id": referral["_id"]},
            {
                "$inc": {"current_uses": 1},
                "$push": {
                    "used_by": {
                        "client_id": ObjectId(new_client_id),
                        "used_at": datetime.utcnow()
                    }
                }
            }
        )
        
        # Award referrer
        referrer_id = str(referral["client_id"])
        reward_amount = referral.get("reward_amount", 100)
        
        from app.services.rewards_service import RewardsService
        RewardsService.add_points(
            tenant_id=tenant_id,
            client_id=referrer_id,
            points=int(reward_amount),
            reason=f"Referral reward for {new_client_id}"
        )
        
        # Award new client
        RewardsService.add_points(
            tenant_id=tenant_id,
            client_id=new_client_id,
            points=int(reward_amount / 2),
            reason="Referral signup bonus"
        )
        
        return {
            "status": "success",
            "referrer_reward": reward_amount,
            "new_client_reward": reward_amount / 2
        }
    
    @staticmethod
    def get_referral_stats(tenant_id: str, client_id: str) -> Dict:
        """Get referral statistics"""
        db = Database.get_db()
        
        referral = db.referrals.find_one({
            "tenant_id": tenant_id,
            "client_id": ObjectId(client_id)
        })
        
        if not referral:
            return {
                "total_referrals": 0,
                "total_earned": 0
            }
        
        total_referrals = referral.get("current_uses", 0)
        total_earned = total_referrals * referral.get("reward_amount", 0)
        
        return {
            "code": referral.get("code"),
            "total_referrals": total_referrals,
            "total_earned": total_earned,
            "reward_per_referral": referral.get("reward_amount"),
            "max_uses": referral.get("max_uses")
        }
    
    @staticmethod
    def get_top_referrers(tenant_id: str, limit: int = 10) -> List[Dict]:
        """Get top referrers"""
        db = Database.get_db()
        
        pipeline = [
            {
                "$match": {"tenant_id": tenant_id}
            },
            {
                "$project": {
                    "client_id": 1,
                    "code": 1,
                    "reward_amount": 1,
                    "current_uses": 1,
                    "total_earned": {
                        "$multiply": ["$current_uses", "$reward_amount"]
                    }
                }
            },
            {
                "$sort": {"current_uses": -1}
            },
            {
                "$limit": limit
            }
        ]
        
        return list(db.referrals.aggregate(pipeline))
    
    @staticmethod
    def generate_referral_link(tenant_id: str, client_id: str, tenant_subdomain: str) -> Dict:
        """Generate or retrieve referral link for client"""
        db = Database.get_db()
        
        # Check if client already has a referral code
        existing = db.referrals.find_one({
            "tenant_id": tenant_id,
            "client_id": ObjectId(client_id)
        })
        
        if existing:
            referral_link = f"https://{tenant_subdomain}.salon.com/register?ref={existing['code']}"
            return {
                "referral_code": existing["code"],
                "referral_link": referral_link,
                "created_at": existing["created_at"]
            }
        
        # Create new referral code
        code = str(uuid.uuid4())[:8].upper()
        referral_link = f"https://{tenant_subdomain}.salon.com/register?ref={code}"
        
        referral = {
            "tenant_id": tenant_id,
            "client_id": ObjectId(client_id),
            "code": code,
            "referral_link": referral_link,
            "status": "active",
            "created_at": datetime.utcnow(),
            "tracking_records": [],
            "total_tracked": 0,
            "total_completed": 0,
            "total_rewards_earned": 0,
            "pending_rewards": 0,
            "redeemed_rewards": 0
        }
        
        result = db.referrals.insert_one(referral)
        
        return {
            "referral_code": code,
            "referral_link": referral_link,
            "created_at": referral["created_at"]
        }
    
    @staticmethod
    def track_referral(tenant_id: str, referral_code: str, referred_client_id: str) -> Dict:
        """Track referral when new client signs up"""
        db = Database.get_db()
        
        # Find referral by code
        referral = db.referrals.find_one({
            "tenant_id": tenant_id,
            "code": referral_code,
            "status": "active"
        })
        
        if not referral:
            raise ValueError("Invalid or inactive referral code")
        
        # Check for duplicate tracking
        existing_track = db.referrals.find_one({
            "tenant_id": tenant_id,
            "code": referral_code,
            "tracking_records.referred_client_id": ObjectId(referred_client_id)
        })
        
        if existing_track:
            raise ValueError("This client has already been tracked with this referral code")
        
        # Prevent self-referral
        if str(referral["client_id"]) == referred_client_id:
            raise ValueError("Cannot refer yourself")
        
        # Create tracking record
        tracking_record = {
            "referred_client_id": ObjectId(referred_client_id),
            "status": "pending",
            "tracked_at": datetime.utcnow(),
            "completed_at": None,
            "reward_amount": 0
        }
        
        # Update referral with tracking record
        db.referrals.update_one(
            {"_id": referral["_id"]},
            {
                "$push": {"tracking_records": tracking_record},
                "$inc": {"total_tracked": 1}
            }
        )
        
        return {
            "status": "tracked",
            "referrer_id": str(referral["client_id"]),
            "referred_client_id": referred_client_id
        }
    
    @staticmethod
    def complete_referral(tenant_id: str, referred_client_id: str, reward_amount: Optional[float] = None) -> Dict:
        """Mark referral as completed and award reward"""
        db = Database.get_db()
        
        # If reward_amount not provided, get from tenant settings
        if reward_amount is None:
            settings = ReferralService.get_tenant_referral_settings(tenant_id)
            reward_amount = settings.get("reward_amount", 1000)
        
        # Find referral with this referred client
        referral = db.referrals.find_one({
            "tenant_id": tenant_id,
            "tracking_records.referred_client_id": ObjectId(referred_client_id)
        })
        
        if not referral:
            raise ValueError("No referral found for this client")
        
        # Update tracking record status
        db.referrals.update_one(
            {
                "_id": referral["_id"],
                "tracking_records.referred_client_id": ObjectId(referred_client_id)
            },
            {
                "$set": {
                    "tracking_records.$.status": "completed",
                    "tracking_records.$.completed_at": datetime.utcnow(),
                    "tracking_records.$.reward_amount": reward_amount
                },
                "$inc": {
                    "total_completed": 1,
                    "total_rewards_earned": reward_amount,
                    "pending_rewards": reward_amount
                }
            }
        )
        
        return {
            "status": "completed",
            "referrer_id": str(referral["client_id"]),
            "reward_amount": reward_amount
        }
    
    @staticmethod
    def redeem_rewards(tenant_id: str, client_id: str, amount: float) -> Dict:
        """Redeem earned rewards"""
        db = Database.get_db()
        
        # Find referral for client
        referral = db.referrals.find_one({
            "tenant_id": tenant_id,
            "client_id": ObjectId(client_id)
        })
        
        if not referral:
            raise ValueError("No referral record found for this client")
        
        pending_rewards = referral.get("pending_rewards", 0)
        
        if pending_rewards < amount:
            raise ValueError(f"Insufficient rewards. Available: {pending_rewards}, Requested: {amount}")
        
        # Create redemption record
        redemption = {
            "amount": amount,
            "redeemed_at": datetime.utcnow(),
            "status": "completed"
        }
        
        # Update referral
        db.referrals.update_one(
            {"_id": referral["_id"]},
            {
                "$push": {"redemption_records": redemption},
                "$inc": {
                    "pending_rewards": -amount,
                    "redeemed_rewards": amount
                }
            }
        )
        
        return {
            "status": "redeemed",
            "amount": amount,
            "remaining_balance": pending_rewards - amount
        }
    
    @staticmethod
    def get_referral_dashboard(tenant_id: str, client_id: str) -> Dict:
        """Get referral dashboard for client"""
        db = Database.get_db()
        
        referral = db.referrals.find_one({
            "tenant_id": tenant_id,
            "client_id": ObjectId(client_id)
        })
        
        if not referral:
            return {
                "referral_code": None,
                "referral_link": None,
                "total_referrals": 0,
                "successful_referrals": 0,
                "pending_referrals": 0,
                "total_rewards_earned": 0,
                "pending_rewards": 0,
                "redeemed_rewards": 0,
                "referral_history": [],
                "conversion_rate": 0
            }
        
        total_tracked = referral.get("total_tracked", 0)
        total_completed = referral.get("total_completed", 0)
        conversion_rate = (total_completed / total_tracked * 100) if total_tracked > 0 else 0
        
        # Build history
        history = []
        for record in referral.get("tracking_records", []):
            history.append({
                "referred_client_id": str(record["referred_client_id"]),
                "status": record["status"],
                "reward_amount": record.get("reward_amount", 0),
                "referred_at": record["tracked_at"],
                "completed_at": record.get("completed_at")
            })
        
        return {
            "referral_code": referral.get("code"),
            "referral_link": referral.get("referral_link"),
            "total_referrals": total_tracked,
            "successful_referrals": total_completed,
            "pending_referrals": total_tracked - total_completed,
            "total_rewards_earned": referral.get("total_rewards_earned", 0),
            "pending_rewards": referral.get("pending_rewards", 0),
            "redeemed_rewards": referral.get("redeemed_rewards", 0),
            "referral_history": history,
            "conversion_rate": round(conversion_rate, 2)
        }
    
    @staticmethod
    def get_referral_analytics(tenant_id: str) -> Dict:
        """Get tenant-level referral analytics"""
        db = Database.get_db()
        
        referrals = list(db.referrals.find({"tenant_id": tenant_id}))
        
        total_referrals = sum(r.get("total_tracked", 0) for r in referrals)
        total_completed = sum(r.get("total_completed", 0) for r in referrals)
        total_rewards_paid = sum(r.get("redeemed_rewards", 0) for r in referrals)
        total_pending = sum(r.get("pending_rewards", 0) for r in referrals)
        
        conversion_rate = (total_completed / total_referrals * 100) if total_referrals > 0 else 0
        
        # Get top referrers
        top_referrers = sorted(
            referrals,
            key=lambda x: x.get("total_completed", 0),
            reverse=True
        )[:10]
        
        top_referrers_data = [
            {
                "client_id": str(r["client_id"]),
                "total_referrals": r.get("total_tracked", 0),
                "successful_referrals": r.get("total_completed", 0),
                "total_earned": r.get("total_rewards_earned", 0)
            }
            for r in top_referrers
        ]
        
        return {
            "total_referrals": total_referrals,
            "successful_referrals": total_completed,
            "conversion_rate": round(conversion_rate, 2),
            "total_rewards_paid": total_rewards_paid,
            "total_pending_rewards": total_pending,
            "top_referrers": top_referrers_data
        }
