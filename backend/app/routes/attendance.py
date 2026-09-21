"""Routes for attendance management."""
import logging
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from bson import ObjectId
from app.models.attendance import AttendanceRecord
from app.models.shift import Shift
from app.models.staff import Staff
from app.context import get_tenant_id
from app.decorators.tenant_isolated import tenant_isolated

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/attendance", tags=["attendance"])


def get_tenant_id_from_context() -> ObjectId:
    return get_tenant_id()


def _summarise(query_set) -> dict:
    total_hours = 0.0
    late_arrivals = 0
    early_departures = 0
    days = 0
    for r in query_set:
        days += 1
        if r.is_late:
            late_arrivals += 1
        if r.is_early_departure:
            early_departures += 1
        if r.hours_worked:
            total_hours += r.hours_worked
    avg = total_hours / days if days > 0 else 0.0
    return {
        "total_hours": round(total_hours, 2),
        "total_days": days,
        "late_arrivals": late_arrivals,
        "early_departures": early_departures,
        "average_hours_per_day": round(avg, 2),
    }


@router.get("", response_model=list)
@tenant_isolated
async def get_attendance_records(
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
    staff_id: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
):
    """Fetch attendance records, optionally filtered by staff and date range."""
    try:
        q = AttendanceRecord.objects(tenant_id=tenant_id)
        if staff_id:
            q = q.filter(staff_id=ObjectId(staff_id))
        if status:
            q = q.filter(status=status)
        if start_date:
            from_date = datetime.fromisoformat(start_date)
            q = q.filter(date__gte=from_date)
        if end_date:
            to_date = datetime.fromisoformat(end_date)
            q = q.filter(date__lte=to_date)
        records = q.order_by("-date")
        return [
            {
                "id": str(r.id),
                "staff_id": str(r.staff_id),
                "check_in_time": r.check_in_time.isoformat(),
                "check_out_time": r.check_out_time.isoformat() if r.check_out_time else None,
                "hours_worked": r.hours_worked,
                "status": r.status,
                "is_late": r.is_late,
                "is_early_departure": r.is_early_departure,
                "notes": r.notes,
                "created_at": r.created_at.isoformat(),
                "updated_at": r.updated_at.isoformat() if r.updated_at else None,
            }
            for r in records
        ]
    except Exception as e:
        logger.error(f"Failed to get attendance records: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to get attendance records")


@router.get("/current", response_model=dict)
@tenant_isolated
async def get_current_attendance(
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
    staff_id: Optional[str] = Query(None),
):
    """Get the current open attendance record for a staff member."""
    try:
        if not staff_id:
            raise HTTPException(status_code=400, detail="staff_id is required")
        record = AttendanceRecord.objects(
            tenant_id=tenant_id,
            staff_id=ObjectId(staff_id),
            status__in=["checked_in", "on_break"],
        ).first()
        if not record:
            return None
        return {
            "id": str(record.id),
            "staff_id": str(record.staff_id),
            "check_in_time": record.check_in_time.isoformat(),
            "status": record.status,
            "is_late": record.is_late,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get current attendance: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to get current attendance")


@router.post("/clock-in", response_model=dict)
@tenant_isolated
async def clock_in(
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
    staff_id: Optional[str] = Body(None, embed=True),
    notes: Optional[str] = Body(None, embed=True),
):
    """Clock in a staff member."""
    try:
        if not staff_id:
            raise HTTPException(status_code=400, detail="staff_id is required")
        existing = AttendanceRecord.objects(
            tenant_id=tenant_id,
            staff_id=ObjectId(staff_id),
            status__in=["checked_in", "on_break"],
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Already clocked in")

        now = datetime.utcnow()
        shift = Shift.objects(
            tenant_id=tenant_id,
            staff_id=ObjectId(staff_id),
            start_time__lte=now,
            end_time__gte=now,
            status__in=["scheduled", "in_progress"],
        ).first()

        is_late = False
        if shift:
            grace = timedelta(minutes=15)
            is_late = now > shift.start_time + grace

        record = AttendanceRecord(
            tenant_id=tenant_id,
            staff_id=ObjectId(staff_id),
            shift_id=shift.id if shift else None,
            check_in_time=now,
            date=now,
            status="checked_in",
            is_late=is_late,
            notes=notes,
        )
        record.save()
        return {
            "id": str(record.id),
            "staff_id": str(record.staff_id),
            "check_in_time": record.check_in_time.isoformat(),
            "status": record.status,
            "is_late": record.is_late,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to clock in: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to clock in")


@router.post("/clock-out", response_model=dict)
@tenant_isolated
async def clock_out(
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
    staff_id: Optional[str] = Body(None, embed=True),
    notes: Optional[str] = Body(None, embed=True),
):
    """Clock out a staff member."""
    try:
        if not staff_id:
            raise HTTPException(status_code=400, detail="staff_id is required")
        record = AttendanceRecord.objects(
            tenant_id=tenant_id,
            staff_id=ObjectId(staff_id),
            status="checked_in",
        ).first()
        if not record:
            raise HTTPException(status_code=400, detail="Not currently clocked in")

        now = datetime.utcnow()
        record.check_out_time = now
        record.status = "completed"

        if record.check_in_time:
            delta = (now - record.check_in_time).total_seconds() / 3600.0
            record.hours_worked = round(delta, 2)
            shift = Shift.objects(id=record.shift_id).first() if record.shift_id else None
            if shift:
                expected_end = shift.end_time
                record.is_early_departure = now < expected_end - timedelta(minutes=15)

        if notes:
            record.notes = (record.notes or "") + f"\nClock-out: {notes}"
        record.save()
        return {
            "id": str(record.id),
            "staff_id": str(record.staff_id),
            "check_in_time": record.check_in_time.isoformat(),
            "check_out_time": record.check_out_time.isoformat(),
            "hours_worked": record.hours_worked,
            "status": record.status,
            "is_early_departure": record.is_early_departure,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to clock out: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to clock out")


@router.get("/summary", response_model=dict)
@tenant_isolated
async def get_attendance_summary(
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
    staff_id: str = Query(...),
    period: str = Query("month", pattern="^(week|month|year)$"),
):
    """Get attendance summary for a period."""
    try:
        now = datetime.utcnow()
        if period == "week":
            start = now - timedelta(days=7)
        elif period == "year":
            start = now - timedelta(days=365)
        else:
            start = now - timedelta(days=30)
        records = AttendanceRecord.objects(
            tenant_id=tenant_id,
            staff_id=ObjectId(staff_id),
            date__gte=start,
            date__lte=now,
        )
        return _summarise(records)
    except Exception as e:
        logger.error(f"Failed to get attendance summary: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to get attendance summary")
