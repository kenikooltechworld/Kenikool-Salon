"""
Credits API endpoints - Package credit management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from typing import Optional, List, Dict
from datetime import datetime
import logging
from bson import ObjectId

from app.api.dependencies import get_current_user, get_current_tenant_id
from app.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/credits", tags=["credits"])


@router.get("/balance")
async def get_credit_balance(
    request: Request,
    current_user: Dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get current package credit balance for user"""
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User has no tenant association"
            )
        
        credit = db.package_credits.find_one({
            "user_id": user_id,
            "tenant_id": tenant_id
        })
        
        if not credit:
            return {
                "id": "",
                "client_id": user_id,
                "balance": 0,
                "total_purchased": 0,
                "expiration_date": None,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
        
        credit["id"] = str(credit.get("_id", ""))
        if "_id" in credit:
            del credit["_id"]
        
        return credit
    except Exception as e:
        logger.error(f"Error fetching credit balance: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch credit balance"
        )


@router.post("/redeem")
async def redeem_credits(
    data: Dict,
    current_user: Dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Redeem package credits for a booking"""
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        booking_id = data.get("booking_id")
        amount = data.get("amount", 0)
        
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User has no tenant association"
            )
        
        if amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Redemption amount must be greater than zero"
            )
        
        # Get current balance
        credit = db.package_credits.find_one({
            "user_id": user_id,
            "tenant_id": tenant_id
        })
        
        if not credit or credit.get("balance", 0) < amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient credits"
            )
        
        # Update balance
        new_balance = credit.get("balance", 0) - amount
        db.package_credits.update_one(
            {"_id": credit["_id"]},
            {
                "$set": {
                    "balance": new_balance,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Record transaction
        db.credit_transactions.insert_one({
            "user_id": user_id,
            "tenant_id": tenant_id,
            "type": "redemption",
            "amount": amount,
            "booking_id": booking_id,
            "description": f"Redeemed for booking {booking_id}",
            "created_at": datetime.utcnow()
        })
        
        return {
            "success": True,
            "remaining_balance": new_balance,
            "credits_applied": amount
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error redeeming credits: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to redeem credits"
        )


@router.get("/transactions")
async def get_credit_transactions(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: Dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get credit transaction history"""
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User has no tenant association"
            )
        
        total = db.credit_transactions.count_documents({
            "user_id": user_id,
            "tenant_id": tenant_id
        })
        
        transactions = list(
            db.credit_transactions.find({
                "user_id": user_id,
                "tenant_id": tenant_id
            })
            .sort("created_at", -1)
            .skip(offset)
            .limit(limit)
        )
        
        for txn in transactions:
            txn["id"] = str(txn.get("_id", ""))
            if "_id" in txn:
                del txn["_id"]
        
        return {
            "items": transactions,
            "total": total
        }
    except Exception as e:
        logger.error(f"Error fetching transactions: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch transactions"
        )


@router.get("/expiration-warning")
async def get_expiration_warning(
    current_user: Dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Check for expiring credits"""
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User has no tenant association"
            )
        
        credit = db.package_credits.find_one({
            "user_id": user_id,
            "tenant_id": tenant_id
        })
        
        if not credit or not credit.get("expiration_date"):
            return {
                "has_expiring_credits": False,
                "expiring_amount": 0,
                "expiration_date": None,
                "days_until_expiration": None
            }
        
        expiration = datetime.fromisoformat(credit["expiration_date"])
        now = datetime.utcnow()
        days_until = (expiration - now).days
        
        return {
            "has_expiring_credits": days_until <= 30,
            "expiring_amount": credit.get("balance", 0),
            "expiration_date": credit["expiration_date"],
            "days_until_expiration": max(0, days_until)
        }
    except Exception as e:
        logger.error(f"Error checking expiration: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check expiration"
        )


@router.post("/purchase")
async def purchase_credits(
    data: Dict,
    current_user: Dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Purchase package credits"""
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        amount = data.get("amount", 0)
        payment_method = data.get("payment_method")
        
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User has no tenant association"
            )
        
        if amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Purchase amount must be greater than zero"
            )
        
        # Get or create credit record
        credit = db.package_credits.find_one({
            "user_id": user_id,
            "tenant_id": tenant_id
        })
        
        if credit:
            new_balance = credit.get("balance", 0) + amount
            new_total = credit.get("total_purchased", 0) + amount
            db.package_credits.update_one(
                {"_id": credit["_id"]},
                {
                    "$set": {
                        "balance": new_balance,
                        "total_purchased": new_total,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
        else:
            result = db.package_credits.insert_one({
                "user_id": user_id,
                "tenant_id": tenant_id,
                "balance": amount,
                "total_purchased": amount,
                "expiration_date": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            new_balance = amount
        
        # Record transaction
        txn_result = db.credit_transactions.insert_one({
            "user_id": user_id,
            "tenant_id": tenant_id,
            "type": "purchase",
            "amount": amount,
            "description": f"Purchased {amount} credits via {payment_method}",
            "created_at": datetime.utcnow()
        })
        
        return {
            "success": True,
            "new_balance": new_balance,
            "transaction_id": str(txn_result.inserted_id)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error purchasing credits: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to purchase credits"
        )
