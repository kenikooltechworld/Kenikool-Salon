"""Owner dashboard routes."""

import logging
from datetime import datetime
from fastapi import APIRouter, Query, HTTPException, Depends
from app.services.owner_dashboard_service import OwnerDashboardService
from app.decorators.tenant_isolated import tenant_isolated
from app.context import get_tenant_id
from app.routes.auth import get_current_user_dependency
from bson import ObjectId

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/owner/dashboard", tags=["owner-dashboard"])
service = OwnerDashboardService()


def _require_owner_or_manager(current_user: dict):
    role_names = current_user.get("role_names", [])
    if "Owner" not in role_names and "Manager" not in role_names:
        raise HTTPException(status_code=403, detail="Owner or Manager access required")


@router.get("/metrics")
@tenant_isolated
async def get_dashboard_metrics(
    use_cache: bool = Query(True, description="Use cached results"),
    tenant_id: ObjectId = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user_dependency),
):
    """
    Get all dashboard metrics in a single request.

    Returns:
        {
            "revenue": {
                "current": 5000.00,
                "previous": 4500.00,
                "trend": "up",
                "trendPercentage": 11.11
            },
            "appointments": {
                "today": 5,
                "thisWeek": 28,
                "thisMonth": 120,
                "trend": "up"
            },
            "satisfaction": {
                "score": 4.7,
                "count": 45,
                "trend": "up"
            },
            "staffUtilization": {
                "percentage": 78.5,
                "bookedHours": 157,
                "availableHours": 200
            },
            "pendingPayments": {
                "count": 3,
                "totalAmount": 450.00,
                "oldestDate": "2026-03-15T10:30:00"
            },
            "inventoryStatus": {
                "lowStockCount": 5,
                "expiringCount": 2
            }
        }
    """
    try:
        _require_owner_or_manager(current_user)
        if not tenant_id:
            raise HTTPException(status_code=401, detail="Tenant context not found")

        metrics = service.get_all_metrics(tenant_id, use_cache)
        logger.info(f"[DashboardAPI][GET /metrics] tenant={tenant_id} metrics={metrics}")
        return {
            "success": True,
            "data": metrics,
            "error": None,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching dashboard metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard metrics")


@router.get("/appointments")
@tenant_isolated
async def get_upcoming_appointments(
    limit: int = Query(10, ge=5, le=50, description="Number of appointments to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    tenant_id: ObjectId = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user_dependency),
):
    """
    Get upcoming appointments for the dashboard.

    Returns next 5-50 appointments (default 10) sorted chronologically.
    Includes both internal and public bookings.

    Query Parameters:
        limit: Number of appointments to return (5-50, default 10)
        offset: Pagination offset (default 0)

    Returns:
        {
            "success": true,
            "data": {
                "appointments": [
                    {
                        "id": "507f1f77bcf86cd799439011",
                        "customerName": "John Doe",
                        "serviceName": "Haircut",
                        "staffName": "Jane Smith",
                        "startTime": "2026-03-20T10:00:00",
                        "endTime": "2026-03-20T10:30:00",
                        "status": "confirmed",
                        "isPublicBooking": false
                    }
                ],
                "total": 45,
                "limit": 10,
                "offset": 0
            },
            "error": null
        }
    """
    try:
        _require_owner_or_manager(current_user)
        if not tenant_id:
            raise HTTPException(status_code=401, detail="Tenant context not found")

        appointments = service.get_upcoming_appointments(tenant_id, limit, offset)
        logger.info(f"[DashboardAPI][GET /appointments] tenant={tenant_id} count={len(appointments['appointments'])} total={appointments['total']}")
        return {
            "success": True,
            "data": appointments,
            "error": None,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching upcoming appointments: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch upcoming appointments")


@router.get("/pending-actions")
@tenant_isolated
async def get_pending_actions(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of actions to return"),
    tenant_id: ObjectId = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user_dependency),
):
    """
    Get pending actions requiring owner attention.

    Returns prioritized actions (payments, staff requests, inventory alerts, customer issues)
    sorted by priority (high, medium, low). Maximum 10 returned with total count.

    Query Parameters:
        limit: Maximum number of actions to return (1-50, default 10)

    Returns:
        {
            "success": true,
            "data": {
                "actions": [
                    {
                        "id": "507f1f77bcf86cd799439011",
                        "description": "Payment from John Doe ($150) pending for 3 days",
                        "dueDate": "2026-03-20T10:00:00",
                        "priority": "high",
                        "type": "payment",
                        "actionUrl": "/payments/507f1f77bcf86cd799439011"
                    }
                ],
                "total": 5
            },
            "error": null
        }
    """
    try:
        _require_owner_or_manager(current_user)
        if not tenant_id:
            raise HTTPException(status_code=401, detail="Tenant context not found")

        actions = service.get_pending_actions(tenant_id, limit)
        logger.info(f"[DashboardAPI][GET /pending-actions] tenant={tenant_id} actions={len(actions['actions'])} total={actions['total']}")
        return {
            "success": True,
            "data": actions,
            "error": None,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching pending actions: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch pending actions")


@router.get("/revenue-analytics")
@tenant_isolated
async def get_revenue_analytics(
    period: str = Query("daily", description="Period: daily, weekly, monthly"),
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    tenant_id: ObjectId = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user_dependency),
):
    """
    Get revenue analytics data for charts and reporting.

    Supports date range filtering and includes daily, weekly, monthly aggregations.
    Includes revenue by service type and top 5 staff members.
    Cached for 1 hour.

    Query Parameters:
        start_date: Start date in YYYY-MM-DD format (optional, defaults to 30 days ago)
        end_date: End date in YYYY-MM-DD format (optional, defaults to today)

    Returns:
        {
            "success": true,
            "data": {
                "dailyRevenue": [{"date": "2026-03-01", "revenue": 150.00}, ...],
                "weeklyRevenue": [{"week": "2026-W09", "revenue": 1050.00}, ...],
                "monthlyRevenue": [{"month": "2026-03", "revenue": 4500.00}, ...],
                "byService": [
                    {
                        "serviceName": "Haircut",
                        "revenue": 2500.00,
                        "percentage": 55.56
                    }
                ],
                "byStaff": [
                    {
                        "staffName": "Jane Smith",
                        "revenue": 3000.00,
                        "percentage": 66.67
                    }
                ],
                "totalRevenue": 5000.00,
                "averageDailyRevenue": 166.67,
                "growthPercentage": 11.11,
                "period": "daily"
            },
            "error": null
        }
    """
    try:
        _require_owner_or_manager(current_user)
        if not tenant_id:
            raise HTTPException(status_code=401, detail="Tenant context not found")

        analytics = service.get_revenue_analytics(tenant_id, period, days)
        logger.info(f"[DashboardAPI][GET /revenue-analytics] tenant={tenant_id} totalRevenue={analytics.get('totalRevenue')} period={analytics.get('period')}")
        return {
            "success": True,
            "data": analytics,
            "error": None,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching revenue analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch revenue analytics")


@router.get("/staff-performance")
@tenant_isolated
async def get_staff_performance(
    tenant_id: ObjectId = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user_dependency),
):
    """
    Get staff performance metrics.

    Returns top 5 staff by revenue with utilization rate, satisfaction score,
    and attendance rate. Includes comparison to previous period.
    Cached for 1 hour.

    Returns:
        {
            "success": true,
            "data": {
                "topStaff": [
                    {
                        "staffId": "507f1f77bcf86cd799439011",
                        "staffName": "Jane Smith",
                        "revenue": 5000.00,
                        "revenueRank": 1,
                        "utilizationRate": 78.5,
                        "satisfactionScore": 4.7,
                        "attendanceRate": 95.0,
                        "previousPeriodRevenue": 4500.00,
                        "revenueGrowth": 11.11
                    }
                ],
                "averageUtilization": 75.0,
                "averageSatisfaction": 4.5,
                "averageAttendance": 95.0
            },
            "error": null
        }
    """
    try:
        _require_owner_or_manager(current_user)
        if not tenant_id:
            raise HTTPException(status_code=401, detail="Tenant context not found")

        performance = service.get_staff_performance(tenant_id)
        logger.info(f"[DashboardAPI][GET /staff-performance] tenant={tenant_id} topStaff={len(performance.get('topStaff', []))}")
        return {
            "success": True,
            "data": performance,
            "error": None,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching staff performance: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch staff performance")


@router.get("/data-status")
@tenant_isolated
async def get_data_status(
    tenant_id: ObjectId = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user_dependency),
):
    """
    Check the status of dashboard data availability.
    
    Returns counts of key entities to help troubleshoot "No data available" issues.
    """
    try:
        _require_owner_or_manager(current_user)
        if not tenant_id:
            raise HTTPException(status_code=401, detail="Tenant context not found")

        # Import models here to avoid circular imports
        from app.models.appointment import Appointment
        from app.models.payment import Payment
        from app.models.staff import Staff
        from app.models.service import Service
        from app.models.customer import Customer
        
        status = {
            "tenantId": str(tenant_id),
            "dataAvailability": {
                "appointments": {
                    "total": Appointment.objects(tenant_id=tenant_id).count(),
                    "completed": Appointment.objects(tenant_id=tenant_id, status="completed").count(),
                    "thisMonth": Appointment.objects(
                        tenant_id=tenant_id,
                        created_at__gte=datetime.utcnow().replace(day=1)
                    ).count()
                },
                "payments": {
                    "total": Payment.objects(tenant_id=tenant_id).count(),
                    "successful": Payment.objects(tenant_id=tenant_id, status="success").count(),
                    "thisMonth": Payment.objects(
                        tenant_id=tenant_id,
                        created_at__gte=datetime.utcnow().replace(day=1)
                    ).count()
                },
                "staff": Staff.objects(tenant_id=tenant_id, status="active").count(),
                "services": Service.objects(tenant_id=tenant_id, is_active=True).count(),
                "customers": Customer.objects(tenant_id=tenant_id).count(),
            },
            "hasData": False,
            "recommendations": []
        }
        
        # Determine if there's enough data for analytics
        has_recent_appointments = status["dataAvailability"]["appointments"]["thisMonth"] > 0
        has_payments = status["dataAvailability"]["payments"]["successful"] > 0
        has_staff = status["dataAvailability"]["staff"] > 0
        
        status["hasData"] = has_recent_appointments and has_payments and has_staff
        
        # Provide recommendations
        if not has_recent_appointments:
            status["recommendations"].append("Create some appointments to see appointment analytics")
        if not has_payments:
            status["recommendations"].append("Process some payments to see revenue analytics")
        if not has_staff:
            status["recommendations"].append("Add staff members to see staff performance data")
        if status["hasData"]:
            status["recommendations"].append("Your dashboard should display analytics data")
        else:
            status["recommendations"].append("Consider running the demo data seeder: python backend/seed_demo_data.py")
        
        return {
            "success": True,
            "data": status,
            "error": None,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking data status: {e}")
        raise HTTPException(status_code=500, detail="Failed to check data status")


@router.post("/pending-actions/{action_id}/complete")
@tenant_isolated
async def mark_action_complete(
    action_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user_dependency),
):
    """
    Mark a pending action as complete.

    Parameters:
        action_id: The ID of the action to mark as complete

    Returns:
        {
            "success": true,
            "message": "Action marked as complete",
            "error": null
        }
    """
    try:
        _require_owner_or_manager(current_user)
        if not tenant_id:
            raise HTTPException(status_code=401, detail="Tenant context not found")

        service.mark_action_complete(tenant_id, action_id)
        return {
            "success": True,
            "message": "Action marked as complete",
            "error": None,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking action complete: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark action as complete")


@router.post("/pending-actions/{action_id}/dismiss")
@tenant_isolated
async def dismiss_action(
    action_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user_dependency),
):
    """
    Dismiss a pending action.

    Parameters:
        action_id: The ID of the action to dismiss

    Returns:
        {
            "success": true,
            "message": "Action dismissed",
            "error": null
        }
    """
    try:
        _require_owner_or_manager(current_user)
        if not tenant_id:
            raise HTTPException(status_code=401, detail="Tenant context not found")

        service.dismiss_action(tenant_id, action_id)
        return {
            "success": True,
            "message": "Action dismissed",
            "error": None,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error dismissing action: {e}")
        raise HTTPException(status_code=500, detail="Failed to dismiss action")
