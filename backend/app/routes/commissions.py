"""API routes for staff commissions and payouts."""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from bson import ObjectId
from decimal import Decimal
from app.context import get_tenant_id
from app.services.service_commission_service import ServiceCommissionService
from app.models.commission_payout import CommissionPayout
from app.models.staff_commission import StaffCommission
from app.decorators.tenant_isolated import tenant_isolated


def get_tenant_id_from_context() -> ObjectId:
    return get_tenant_id()


router = APIRouter(prefix="/commissions", tags=["commissions"])


@router.get("/staff/{staff_id}")
@tenant_isolated
async def get_staff_commissions(
    staff_id: str,
    status: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    try:
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
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
                    "transaction_id": str(c.transaction_id),
                    "commission_amount": float(c.commission_amount),
                    "commission_rate": float(c.commission_rate),
                    "commission_type": c.commission_type,
                    "calculated_at": c.calculated_at.isoformat(),
                    "status": getattr(c, "status", "pending"),
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
@tenant_isolated
async def get_commission_summary(
    staff_id: str,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    try:
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None

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

        this_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        this_week_start = datetime.utcnow() - __import__("datetime").timedelta(days=datetime.utcnow().weekday())

        this_month = StaffCommission.objects(
            tenant_id=tenant_id, staff_id=ObjectId(staff_id), created_at__gte=this_month_start
        )
        this_week = StaffCommission.objects(
            tenant_id=tenant_id, staff_id=ObjectId(staff_id), created_at__gte=this_week_start
        )
        total_month = sum(c.commission_amount for c in this_month)
        total_week = sum(c.commission_amount for c in this_week)

        return {
            "totalEarnings": float(summary.get("total_earned", 0)),
            "thisMonth": float(total_month),
            "thisWeek": float(total_week),
            "summary": summary,
            "breakdown": [
                {
                    "label": b.get("service_name", b.get("service_id", "")),
                    "amount": float(b["total_commission"]),
                    "count": b["count"],
                    "percentage": round((b["total_commission"] / summary.get("total_earned", 0)) * 100,
                                       1) if summary.get("total_earned", 0) > 0 else 0.0,
                }
                for b in breakdown
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/staff/{staff_id}/breakdown")
@tenant_isolated
async def get_commission_breakdown(
    staff_id: str,
    breakdown_type: str = Query("service"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    try:
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        breakdown = ServiceCommissionService.get_commission_by_service(
            tenant_id=tenant_id,
            staff_id=ObjectId(staff_id),
            start_date=start_dt,
            end_date=end_dt,
        )
        total = sum(b["total_commission"] for b in breakdown)
        return {
            "breakdown": [
                {
                    "label": b.get("service_name", b.get("service_id", "")),
                    "amount": float(b["total_commission"]),
                    "count": b["count"],
                    "percentage": round((b["total_commission"] / total) * 100, 1) if total > 0 else 0.0,
                }
                for b in breakdown
            ],
            "total": float(total),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/staff/{staff_id}/by-date")
@tenant_isolated
async def get_commission_by_date(
    staff_id: str,
    startDate: str = Query(...),
    endDate: str = Query(...),
    aggregation: str = Query("daily"),
    serviceType: Optional[str] = Query(None),
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    try:
        start_dt = datetime.fromisoformat(startDate)
        end_dt = datetime.fromisoformat(endDate)
        q = {
            "tenant_id": tenant_id,
            "staff_id": ObjectId(staff_id),
            "created_at__gte": start_dt,
            "created_at__lte": end_dt,
        }
        if serviceType:
            q["service_id"] = ObjectId(serviceType)
        query = __import__("mongoengine").Q(**q)
        commissions = StaffCommission.objects(__import__("mongoengine").Q(**q))
        from collections import defaultdict
        daily = defaultdict(lambda: {"amount": Decimal("0"), "count": 0})
        for c in commissions:
            key = c.created_at.strftime("%Y-%m-%d")
            daily[key]["amount"] += c.commission_amount
            daily[key]["count"] += 1
        data = [
            {"date": k, "amount": float(v["amount"]), "count": v["count"]}
            for k, v in sorted(daily.items())
        ]
        total = sum(d["amount"] for d in data)
        return {"data": data, "total": float(total)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/payouts", response_model=dict)
@tenant_isolated
async def get_commission_payouts(
    staff_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    try:
        q = CommissionPayout.objects(tenant_id=tenant_id)
        if staff_id:
            q = q.filter(staff_id=ObjectId(staff_id))
        total = q.count()
        items = q.order_by("-created_at").skip(skip).limit(limit)
        return {
            "payouts": [
                {
                    "id": str(p.id),
                    "staffId": str(p.staff_id),
                    "payoutAmount": float(p.payout_amount),
                    "period": p.period,
                    "payoutDate": p.processed_at.isoformat() if p.processed_at else None,
                    "status": p.status,
                    "createdAt": p.created_at.isoformat(),
                }
                for p in items
            ],
            "total": total,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/payouts", response_model=dict)
@tenant_isolated
async def create_commission_payout(
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
    staff_id: str = Body(...),
    period: str = Body(...),
):
    try:
        from collections import defaultdict
        from datetime import timedelta
        import datetime as dt

        if "-" in period:
            parts = period.split("-")
            if len(parts) == 2:
                year, month = int(parts[0]), int(parts[1])
                start_dt = dt.datetime(year, month, 1)
                end_dt = (dt.datetime(year + (month // 12), (month % 12) + 1, 1) if month == 12 else dt.datetime(year, month + 1, 1))
            else:
                start_dt = datetime.utcnow() - timedelta(days=30)
                end_dt = datetime.utcnow()
        else:
            start_dt = datetime.utcnow() - timedelta(days=30)
            end_dt = datetime.utcnow()

        commissions = StaffCommission.objects(
            tenant_id=tenant_id,
            staff_id=ObjectId(staff_id),
            created_at__gte=start_dt,
            created_at__lte=end_dt,
            status__ne="paid",
        )
        payout_amount = sum(c.commission_amount for c in commissions)

        payout = CommissionPayout(
            tenant_id=tenant_id,
            staff_id=ObjectId(staff_id),
            period=period,
            payout_amount=payout_amount or Decimal("0"),
            status="pending",
        )
        payout.save()

        commissions.update(set__status="paid", set__updated_at=datetime.utcnow())

        return {
            "id": str(payout.id),
            "staffId": str(payout.staff_id),
            "payoutAmount": float(payout.payout_amount),
            "period": payout.period,
            "payoutDate": None,
            "status": payout.status,
            "createdAt": payout.created_at.isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/staff/user/{user_id}", response_model=dict)
@tenant_isolated
async def get_staff_commissions_by_user(
    user_id: str,
    status: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """Get staff commissions by user ID."""
    try:
        staff = Staff.objects(user_id=ObjectId(user_id), tenant_id=tenant_id).first()
        if not staff:
            raise HTTPException(status_code=404, detail="Staff profile not found for this user")
        
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        commissions, total = ServiceCommissionService.list_staff_commissions(
            tenant_id=tenant_id,
            staff_id=staff.id,
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
                    "transaction_id": str(c.transaction_id),
                    "commission_amount": float(c.commission_amount),
                    "commission_rate": float(c.commission_rate),
                    "commission_type": c.commission_type,
                    "calculated_at": c.calculated_at.isoformat(),
                    "status": getattr(c, "status", "pending"),
                }
                for c in commissions
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/staff/user/{user_id}/summary", response_model=dict)
@tenant_isolated
async def get_commission_summary_by_user(
    user_id: str,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """Get commission summary by user ID."""
    try:
        staff = Staff.objects(user_id=ObjectId(user_id), tenant_id=tenant_id).first()
        if not staff:
            raise HTTPException(status_code=404, detail="Staff profile not found for this user")
        
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None

        summary = ServiceCommissionService.get_commission_summary(
            tenant_id=tenant_id,
            staff_id=staff.id,
            start_date=start_dt,
            end_date=end_dt,
        )
        breakdown = ServiceCommissionService.get_commission_by_service(
            tenant_id=tenant_id,
            staff_id=staff.id,
            start_date=start_dt,
            end_date=end_dt,
        )

        this_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        this_week_start = datetime.utcnow() - __import__("datetime").timedelta(days=datetime.utcnow().weekday())

        this_month = StaffCommission.objects(
            tenant_id=tenant_id, staff_id=staff.id, created_at__gte=this_month_start
        )
        this_week = StaffCommission.objects(
            tenant_id=tenant_id, staff_id=staff.id, created_at__gte=this_week_start
        )
        total_month = sum(c.commission_amount for c in this_month)
        total_week = sum(c.commission_amount for c in this_week)

        return {
            "totalEarnings": float(summary.get("total_earned", 0)),
            "thisMonth": float(total_month),
            "thisWeek": float(total_week),
            "summary": summary,
            "breakdown": [
                {
                    "label": b.get("service_name", b.get("service_id", "")),
                    "amount": float(b["total_commission"]),
                    "count": b["count"],
                    "percentage": round((b["total_commission"] / summary.get("total_earned", 0)) * 100,
                                       1) if summary.get("total_earned", 0) > 0 else 0.0,
                }
                for b in breakdown
            ],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
