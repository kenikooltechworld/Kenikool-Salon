"""Routes for staff goals and achievements."""
import logging
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from bson import ObjectId
from app.models.goal import Goal, GoalAchievement
from app.models.staff_commission import StaffCommission
from app.models.service_commission import ServiceCommission
from app.models.appointment import Appointment
from app.models.staff import Staff
from app.context import get_tenant_id
from app.decorators.tenant_isolated import tenant_isolated


def get_tenant_id_from_context() -> ObjectId:
    return get_tenant_id()


router = APIRouter(prefix="/goals", tags=["goals"])


@router.get("/staff/{staff_id}", response_model=dict)
@tenant_isolated
async def get_staff_goals(
    staff_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    try:
        Staff.objects(id=ObjectId(staff_id), tenant_id=tenant_id).first_or_404(detail="Staff not found")
        now = datetime.utcnow()
        active = Goal.objects(
            tenant_id=tenant_id,
            staff_id=ObjectId(staff_id),
            status="active",
            period_start__lte=now,
            period_end__gte=now,
        )
        completed = Goal.objects(tenant_id=tenant_id, staff_id=ObjectId(staff_id), status="completed").limit(10)
        total_goals_count = Goal.objects(tenant_id=tenant_id, staff_id=ObjectId(staff_id)).count()
        completed_goals_count = Goal.objects(tenant_id=tenant_id, staff_id=ObjectId(staff_id), status="completed").count()
        goals = []
        for g in list(active) + list(completed):
            progress = 0.0
            if g.target_value > 0:
                progress = min(100.0, (g.current_value / g.target_value) * 100)
            goals.append({
                "id": str(g.id),
                "goal_type": g.goal_type,
                "target_value": g.target_value,
                "current_value": g.current_value,
                "period_start": g.period_start.isoformat(),
                "period_end": g.period_end.isoformat(),
                "status": g.status,
                "progress_percentage": round(progress, 1),
                "created_at": g.created_at.isoformat(),
                "updated_at": g.updated_at.isoformat() if g.updated_at else None,
            })
        return {
            "goals": goals,
            "total_goals": total_goals_count,
            "completed_goals": completed_goals_count,
            "active_goals": active.count(),
            "overall_progress": round(sum(g["progress_percentage"] for g in goals) / len(goals), 1) if goals else 0,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get goals: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to get goals")


@router.get("/achievements", response_model=dict)
@tenant_isolated
async def get_achievements(
    staff_id: str = Query(...),
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
    limit: int = Query(25, ge=1, le=100),
):
    try:
        Staff.objects(id=ObjectId(staff_id), tenant_id=tenant_id).first_or_404(detail="Staff not found")
        items = GoalAchievement.objects(tenant_id=tenant_id, staff_id=ObjectId(staff_id)).order_by("-achieved_at").limit(limit)
        return {
            "achievements": [
                {
                    "id": str(i.id),
                    "goal_id": str(i.goal_id),
                    "staff_id": str(i.staff_id),
                    "achieved_at": i.achieved_at.isoformat(),
                    "target_value": i.target_value,
                    "achieved_value": i.achieved_value,
                    "bonus_earned": i.bonus_earned,
                    "incentive_details": i.incentive_details,
                }
                for i in items
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get achievements: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to get achievements")


@router.get("/bonuses", response_model=list)
@tenant_isolated
async def get_bonuses(
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """Fetch bonus/incentive configurations from goals as a list."""
    try:
        goals = Goal.objects(tenant_id=tenant_id, status="active").distinct(field="bonus_earned")
        return [
            {
                "id": str(g.id),
                "name": f"{g.goal_type.title()} Target",
                "description": f"Target of {g.target_value} for {g.goal_type}",
                "bonus_amount": g.bonus_earned or 0.0,
                "criteria": g.goal_type,
                "active": g.status == "active",
            }
            for g in Goal.objects(tenant_id=tenant_id).limit(50)
        ]
    except Exception as e:
        logger.error(f"Failed to get bonuses: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to get bonuses")


@router.get("/performance-vs-targets", response_model=dict)
@tenant_isolated
async def get_performance_vs_targets(
    staff_id: str = Query(...),
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    try:
        now = datetime.utcnow()
        targets = Goal.objects(
            tenant_id=tenant_id,
            staff_id=ObjectId(staff_id),
            status="active",
            period_start__lte=now,
            period_end__gte=now,
        )
        sales_target = commission_target = appointments_target = 0
        commission_current = sales_current = appointments_current = 0.0
        for g in targets:
            if g.goal_type == "sales":
                sales_target = g.target_value
                sales_current = g.current_value
            elif g.goal_type == "commission":
                commission_target = g.target_value
                commission_current = g.current_value
            elif g.goal_type == "appointments":
                appointments_target = g.target_value
                appointments_current = g.current_value
            elif g.goal_type == "customer_satisfaction":
                pass

        def pct(actual, target):
            return round((actual / target) * 100, 1) if target > 0 else 0.0

        return {
            "sales_vs_target": {"target": sales_target, "actual": round(sales_current, 2), "percentage": pct(sales_current, sales_target)},
            "commission_vs_target": {"target": commission_target, "actual": round(commission_current, 2), "percentage": pct(commission_current, commission_target)},
            "appointments_vs_target": {"target": appointments_target, "actual": round(appointments_current, 2), "percentage": pct(appointments_current, appointments_target)},
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get performance vs targets: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to get performance vs targets")


@router.post("/staff/{staff_id}/goals", response_model=dict)
@tenant_isolated
async def create_staff_goal(
    staff_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
    goal_type: str = Body(...),
    target_value: float = Body(...),
    period_start: str = Body(...),
    period_end: str = Body(...),
):
    try:
        from app.models.staff import Staff
        Staff.objects(id=ObjectId(staff_id), tenant_id=tenant_id).first_or_404(detail="Staff not found")
        goal = Goal(
            tenant_id=tenant_id,
            staff_id=ObjectId(staff_id),
            goal_type=goal_type,
            target_value=target_value,
            current_value=0,
            period_start=datetime.fromisoformat(period_start),
            period_end=datetime.fromisoformat(period_end),
            status="active",
        )
        goal.save()
        return {"id": str(goal.id), "status": goal.status}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create goal: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to create goal")
