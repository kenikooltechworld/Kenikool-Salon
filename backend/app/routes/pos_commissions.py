"""API routes for POS staff commissions."""

from fastapi import APIRouter, Depends, HTTPException, Query
from bson import ObjectId
from app.context import get_tenant_id
from app.services.commission_service import CommissionService

router = APIRouter(prefix="/commissions", tags=["commissions"])


@router.get("/staff/{staff_id}")
async def get_staff_commission(
    staff_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """Get staff commissions."""
    try:
        commissions, total = CommissionService.list_staff_commissions(
            tenant_id=tenant_id,
            staff_id=ObjectId(staff_id),
            page=page,
            page_size=page_size,
        )

        return {
            "commissions": [
                {
                    "id": str(c.id),
                    "staff_id": str(c.staff_id),
                    "transaction_id": str(c.transaction_id),
                    "commission_amount": c.commission_amount,
                    "commission_rate": c.commission_rate,
                    "commission_type": c.commission_type,
                    "calculated_at": c.calculated_at.isoformat(),
                }
                for c in commissions
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/payouts")
async def list_commission_payouts(
    staff_id: str = Query(None, alias="staffId"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100, alias="pageSize"),
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """List commission payouts."""
    try:
        # This would typically query a CommissionPayout model
        # For now, return empty list
        return {
            "payouts": [],
            "total": 0,
            "page": page,
            "page_size": page_size,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/payouts")
async def create_commission_payout(
    staff_id: str,
    period: str = Query("monthly"),
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """Create commission payout."""
    try:
        payout_amount = CommissionService.calculate_payout(
            tenant_id=tenant_id,
            staff_id=ObjectId(staff_id),
            period=period,
        )

        payout = CommissionService.process_commission_payout(
            tenant_id=tenant_id,
            staff_id=ObjectId(staff_id),
            payout_amount=payout_amount,
        )

        return payout
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
