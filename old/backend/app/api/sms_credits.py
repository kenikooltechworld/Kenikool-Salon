"""
SMS Credits API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
import logging

from app.api.dependencies import get_tenant_id
from app.services.sms_credit_service import SMSCreditService
from app.models.sms_credit import SMSCreditPurchase

logger = logging.getLogger(__name__)

router = APIRouter(tags=["sms-credits"])


@router.get("/sms-credits/balance")
async def get_sms_balance(tenant_id: str = Depends(get_tenant_id)):
    """Get SMS credit balance"""
    try:
        balance = SMSCreditService.get_balance(tenant_id)
        return balance
    except Exception as e:
        logger.error(f"Error getting SMS balance: {e}")
        raise HTTPException(status_code=500, detail="Error getting SMS balance")


@router.get("/sms-credits/history")
async def get_sms_history(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get SMS credit transaction history"""
    try:
        history = SMSCreditService.get_transaction_history(tenant_id, offset, limit)
        return {"transactions": history}
    except Exception as e:
        logger.error(f"Error getting SMS history: {e}")
        raise HTTPException(status_code=500, detail="Error getting SMS history")


@router.post("/sms-credits/purchase")
async def purchase_sms_credits(
    purchase: SMSCreditPurchase,
    tenant_id: str = Depends(get_tenant_id)
):
    """Purchase SMS credits"""
    try:
        transaction = SMSCreditService.add_credits(
            tenant_id=tenant_id,
            amount=purchase.amount,
            reason="purchase",
            reference_id=purchase.reference_id
        )
        return transaction
    except Exception as e:
        logger.error(f"Error purchasing SMS credits: {e}")
        raise HTTPException(status_code=500, detail="Error purchasing SMS credits")


@router.put("/sms-credits/threshold")
async def set_low_balance_threshold(
    threshold: int,
    tenant_id: str = Depends(get_tenant_id)
):
    """Set low balance alert threshold"""
    try:
        result = SMSCreditService.set_low_balance_threshold(tenant_id, threshold)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error setting threshold: {e}")
        raise HTTPException(status_code=500, detail="Error setting threshold")
