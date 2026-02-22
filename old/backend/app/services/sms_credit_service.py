"""
SMS Credit Service - Manages SMS credit tracking and balance
"""
from datetime import datetime
from typing import Dict, List, Optional
from bson import ObjectId
import logging

from app.database import Database
from app.models.sms_credit import SMSCreditBalance, SMSCreditTransaction

logger = logging.getLogger(__name__)


class SMSCreditService:
    """Service for managing SMS credits"""
    
    @staticmethod
    def _get_db():
        """Get database instance"""
        return Database.get_db()
    
    @staticmethod
    def initialize_credits(tenant_id: str, initial_balance: int = 0) -> Dict:
        """
        Initialize SMS credits for a new tenant
        
        Args:
            tenant_id: Tenant ID
            initial_balance: Initial SMS credit balance
            
        Returns:
            SMS credit balance record
        """
        db = SMSCreditService._get_db()
        
        # Check if already initialized
        existing = db.sms_credit_balance.find_one({"tenant_id": tenant_id})
        if existing:
            return {
                **existing,
                "_id": str(existing["_id"]),
                "last_updated": existing["last_updated"].isoformat()
            }
        
        # Create new balance record
        balance_record = {
            "tenant_id": tenant_id,
            "current_balance": initial_balance,
            "total_purchased": initial_balance,
            "total_used": 0,
            "low_balance_threshold": 100,
            "last_updated": datetime.utcnow()
        }
        
        result = db.sms_credit_balance.insert_one(balance_record)
        balance_record["_id"] = str(result.inserted_id)
        
        logger.info(f"Initialized SMS credits for tenant {tenant_id} with balance {initial_balance}")
        
        return {
            **balance_record,
            "last_updated": balance_record["last_updated"].isoformat()
        }
    
    @staticmethod
    def get_balance(tenant_id: str) -> Dict:
        """
        Get current SMS credit balance for tenant
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            SMS credit balance
        """
        db = SMSCreditService._get_db()
        
        balance = db.sms_credit_balance.find_one({"tenant_id": tenant_id})
        
        if not balance:
            # Initialize if not exists
            return SMSCreditService.initialize_credits(tenant_id)
        
        return {
            **balance,
            "_id": str(balance["_id"]),
            "last_updated": balance["last_updated"].isoformat()
        }
    
    @staticmethod
    def check_sufficient_credits(tenant_id: str, required_credits: int) -> bool:
        """
        Check if tenant has sufficient SMS credits
        
        Args:
            tenant_id: Tenant ID
            required_credits: Number of credits needed
            
        Returns:
            True if sufficient credits, False otherwise
        """
        balance = SMSCreditService.get_balance(tenant_id)
        return balance["current_balance"] >= required_credits
    
    @staticmethod
    def deduct_credits(
        tenant_id: str,
        amount: int,
        reason: str,
        campaign_id: Optional[str] = None,
        reference_id: Optional[str] = None
    ) -> Dict:
        """
        Deduct SMS credits from tenant balance
        
        Args:
            tenant_id: Tenant ID
            amount: Number of credits to deduct
            reason: Reason for deduction (e.g., "campaign_send")
            campaign_id: Optional campaign ID
            reference_id: Optional reference ID
            
        Returns:
            Transaction record
            
        Raises:
            ValueError: If insufficient credits
        """
        db = SMSCreditService._get_db()
        
        # Get current balance
        balance = db.sms_credit_balance.find_one({"tenant_id": tenant_id})
        
        if not balance:
            raise ValueError(f"SMS credit balance not found for tenant {tenant_id}")
        
        if balance["current_balance"] < amount:
            raise ValueError(
                f"Insufficient SMS credits. Required: {amount}, Available: {balance['current_balance']}"
            )
        
        # Calculate new balance
        new_balance = balance["current_balance"] - amount
        
        # Create transaction record
        transaction = {
            "tenant_id": tenant_id,
            "transaction_type": "deduction",
            "amount": amount,
            "reason": reason,
            "campaign_id": campaign_id,
            "reference_id": reference_id,
            "balance_before": balance["current_balance"],
            "balance_after": new_balance,
            "created_at": datetime.utcnow()
        }
        
        # Insert transaction
        tx_result = db.sms_credit_transactions.insert_one(transaction)
        transaction["_id"] = str(tx_result.inserted_id)
        
        # Update balance
        db.sms_credit_balance.update_one(
            {"_id": balance["_id"]},
            {
                "$set": {
                    "current_balance": new_balance,
                    "total_used": balance["total_used"] + amount,
                    "last_updated": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"Deducted {amount} SMS credits from tenant {tenant_id}. New balance: {new_balance}")
        
        # Check if balance is low
        if new_balance < balance.get("low_balance_threshold", 100):
            logger.warning(f"SMS credit balance low for tenant {tenant_id}: {new_balance}")
        
        return {
            **transaction,
            "created_at": transaction["created_at"].isoformat()
        }
    
    @staticmethod
    def add_credits(
        tenant_id: str,
        amount: int,
        reason: str = "purchase",
        reference_id: Optional[str] = None
    ) -> Dict:
        """
        Add SMS credits to tenant balance
        
        Args:
            tenant_id: Tenant ID
            amount: Number of credits to add
            reason: Reason for addition (e.g., "purchase", "refund")
            reference_id: Optional reference ID (e.g., payment ID)
            
        Returns:
            Transaction record
        """
        db = SMSCreditService._get_db()
        
        # Get current balance
        balance = db.sms_credit_balance.find_one({"tenant_id": tenant_id})
        
        if not balance:
            # Initialize if not exists
            SMSCreditService.initialize_credits(tenant_id)
            balance = db.sms_credit_balance.find_one({"tenant_id": tenant_id})
        
        # Calculate new balance
        new_balance = balance["current_balance"] + amount
        
        # Create transaction record
        transaction = {
            "tenant_id": tenant_id,
            "transaction_type": "purchase",
            "amount": amount,
            "reason": reason,
            "campaign_id": None,
            "reference_id": reference_id,
            "balance_before": balance["current_balance"],
            "balance_after": new_balance,
            "created_at": datetime.utcnow()
        }
        
        # Insert transaction
        tx_result = db.sms_credit_transactions.insert_one(transaction)
        transaction["_id"] = str(tx_result.inserted_id)
        
        # Update balance
        db.sms_credit_balance.update_one(
            {"_id": balance["_id"]},
            {
                "$set": {
                    "current_balance": new_balance,
                    "total_purchased": balance["total_purchased"] + amount,
                    "last_updated": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"Added {amount} SMS credits to tenant {tenant_id}. New balance: {new_balance}")
        
        return {
            **transaction,
            "created_at": transaction["created_at"].isoformat()
        }
    
    @staticmethod
    def get_transaction_history(
        tenant_id: str,
        offset: int = 0,
        limit: int = 50
    ) -> List[Dict]:
        """
        Get SMS credit transaction history
        
        Args:
            tenant_id: Tenant ID
            offset: Pagination offset
            limit: Pagination limit
            
        Returns:
            List of transactions
        """
        db = SMSCreditService._get_db()
        
        transactions = list(
            db.sms_credit_transactions.find({"tenant_id": tenant_id})
            .sort("created_at", -1)
            .skip(offset)
            .limit(limit)
        )
        
        return [
            {
                **tx,
                "_id": str(tx["_id"]),
                "created_at": tx["created_at"].isoformat()
            }
            for tx in transactions
        ]
    
    @staticmethod
    def set_low_balance_threshold(tenant_id: str, threshold: int) -> Dict:
        """
        Set low balance alert threshold
        
        Args:
            tenant_id: Tenant ID
            threshold: Threshold value
            
        Returns:
            Updated balance record
        """
        db = SMSCreditService._get_db()
        
        result = db.sms_credit_balance.find_one_and_update(
            {"tenant_id": tenant_id},
            {
                "$set": {
                    "low_balance_threshold": threshold,
                    "last_updated": datetime.utcnow()
                }
            },
            return_document=True
        )
        
        if not result:
            raise ValueError(f"SMS credit balance not found for tenant {tenant_id}")
        
        return {
            **result,
            "_id": str(result["_id"]),
            "last_updated": result["last_updated"].isoformat()
        }


# Create singleton instance
sms_credit_service = SMSCreditService()
