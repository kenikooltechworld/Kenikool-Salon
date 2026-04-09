"""API routes for service-based staff commissions."""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from bson import ObjectId
from app.context import get_tenant_id
from app.services.service_commission_service import ServiceCommissionService
from app.schemas.service_commission import (
    ServiceCommissionResponse,
    CommissionListResponse,
    CommissionSummaryResponse,
    ServiceCommissionUpdate,
)

router = APIRouter(prefix="/service-commissions", tags=["service-commissions"])


@router.post("/calculate/{appointment_id}")
async def calculate_commission(
    appointment_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """Calculate commission for a completed appointment."""
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    
    try:
        commission = ServiceCommissionService.calculate_commission_for_appointment(
            tenant_id=tenant_id,
            appointment_id=ObjectId(appointment_id),
        )

        if not commission:
            raise HTTPException(
                status_code=404,
                detail="Appointment not found or not completed"
            )

        return {
            "id": str(commission.id),
            "staff_id": str(commission.staff_id),
            "appointment_id": str(commission.appointment_id),
            "service_id": str(commission.service_id),
            "service_price": commission.service_price,
            "commission_percentage": commission.commission_percentage,
            "commission_amount": commission.commission_amount,
            "status": commission.status,
            "earned_date": commission.earned_date.isoformat(),
            "created_at": commission.created_at.isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/staff/{staff_id}")
async def get_staff_commissions(
    staff_id: str,
    status: str = Query(None, description="Filter by status (pending/paid)"),
    start_date: str = Query(None, description="Start date (ISO format)"),
    end_date: str = Query(None, description="End date (ISO format)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """Get staff commissions with filtering."""
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    
    try:
        # Parse dates if provided
        start_dt = None
        end_dt = None
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
        if end_date:
            end_dt = datetime.fromisoformat(end_date)

        commissions, total = ServiceCommissionService.list_staff_commissions(
            tenant_id=tenant_id,
            staff_id=ObjectId(staff_id),
            status=status,
            start_date=start_dt,
            end_date=end_dt,
            page=page,
            page_size=page_size,
        )

        return {
            "commissions": [
                {
                    "id": str(c.id),
                    "staff_id": str(c.staff_id),
                    "appointment_id": str(c.appointment_id),
                    "service_id": str(c.service_id),
                    "service_price": c.service_price,
                    "commission_percentage": c.commission_percentage,
                    "commission_amount": c.commission_amount,
                    "status": c.status,
                    "earned_date": c.earned_date.isoformat(),
                    "paid_date": c.paid_date.isoformat() if c.paid_date else None,
                    "created_at": c.created_at.isoformat(),
                    "updated_at": c.updated_at.isoformat(),
                }
                for c in commissions
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/staff/{staff_id}/summary")
async def get_commission_summary(
    staff_id: str,
    start_date: str = Query(None, description="Start date (ISO format)"),
    end_date: str = Query(None, description="End date (ISO format)"),
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """Get commission summary for a staff member."""
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    
    try:
        # Parse dates if provided
        start_dt = None
        end_dt = None
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
        if end_date:
            end_dt = datetime.fromisoformat(end_date)

        summary = ServiceCommissionService.get_commission_summary(
            tenant_id=tenant_id,
            staff_id=ObjectId(staff_id),
            start_date=start_dt,
            end_date=end_dt,
        )

        breakdown = ServiceCommissionService.get_commission_by_service(
            tenant_id=tenant_id,
            staff_id=ObjectId(staff_id),
            start_date=start_dt,
            end_date=end_dt,
        )

        return {
            "summary": {
                "total_earned": summary["total_earned"],
                "total_pending": summary["total_pending"],
                "total_paid": summary["total_paid"],
                "total_services": summary["total_services"],
                "average_commission": summary["average_commission"],
            },
            "breakdown": [
                {
                    "service_id": b["service_id"],
                    "service_name": b["service_name"],
                    "total_commission": b["total_commission"],
                    "count": b["count"],
                }
                for b in breakdown
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/staff/{staff_id}/pending")
async def get_pending_commissions(
    staff_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """Get all pending commissions for a staff member."""
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    
    try:
        commissions, total_pending = ServiceCommissionService.get_pending_commissions(
            tenant_id=tenant_id,
            staff_id=ObjectId(staff_id),
        )

        return {
            "commissions": [
                {
                    "id": str(c.id),
                    "staff_id": str(c.staff_id),
                    "appointment_id": str(c.appointment_id),
                    "service_id": str(c.service_id),
                    "service_price": c.service_price,
                    "commission_percentage": c.commission_percentage,
                    "commission_amount": c.commission_amount,
                    "status": c.status,
                    "earned_date": c.earned_date.isoformat(),
                    "created_at": c.created_at.isoformat(),
                }
                for c in commissions
            ],
            "total_pending": total_pending,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{commission_id}/mark-paid")
async def mark_commission_as_paid(
    commission_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """Mark a commission as paid."""
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    
    try:
        commission = ServiceCommissionService.mark_commission_as_paid(
            tenant_id=tenant_id,
            commission_id=ObjectId(commission_id),
        )

        if not commission:
            raise HTTPException(status_code=404, detail="Commission not found")

        return {
            "id": str(commission.id),
            "status": commission.status,
            "paid_date": commission.paid_date.isoformat() if commission.paid_date else None,
            "updated_at": commission.updated_at.isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/staff/{staff_id}/mark-paid-batch")
async def mark_commissions_as_paid_batch(
    staff_id: str,
    commission_ids: list[str],
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """Mark multiple commissions as paid."""
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    
    try:
        count = ServiceCommissionService.mark_commissions_as_paid(
            tenant_id=tenant_id,
            staff_id=ObjectId(staff_id),
            commission_ids=[ObjectId(cid) for cid in commission_ids],
        )

        return {
            "updated_count": count,
            "message": f"Marked {count} commissions as paid",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
