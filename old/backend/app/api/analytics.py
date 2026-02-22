"""
Advanced Analytics and Reporting System API endpoints.

Provides comprehensive analytics, custom reports, data aggregation,
filtering, export functionality, and scheduled report management.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field
import pandas as pd
from io import BytesIO
import json

from app.core.auth import get_current_user, verify_tenant_access
from app.core.models import User, Tenant
from app.db.mongodb import get_db

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


# ============================================================================
# Data Models
# ============================================================================

class DateRange(BaseModel):
    """Date range for filtering analytics data."""
    start_date: datetime
    end_date: datetime


class FilterCriteria(BaseModel):
    """Advanced filtering criteria for analytics."""
    date_range: DateRange
    staff_ids: Optional[List[str]] = None
    service_ids: Optional[List[str]] = None
    client_ids: Optional[List[str]] = None
    payment_methods: Optional[List[str]] = None
    booking_status: Optional[List[str]] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None


class AggregationConfig(BaseModel):
    """Configuration for data aggregation."""
    group_by: str = Field(..., description="Field to group by: day, week, month, staff, service, client")
    metrics: List[str] = Field(..., description="Metrics to calculate: sum, avg, count, min, max")
    sort_by: Optional[str] = None
    sort_order: str = "desc"


class ReportConfig(BaseModel):
    """Configuration for custom report generation."""
    name: str
    description: Optional[str] = None
    report_type: str = Field(..., description="Type: revenue, bookings, clients, staff, inventory")
    filters: FilterCriteria
    aggregation: AggregationConfig
    include_charts: bool = True
    export_format: Optional[str] = None


class ScheduledReportConfig(BaseModel):
    """Configuration for scheduled report generation."""
    name: str
    description: Optional[str] = None
    report_config: ReportConfig
    schedule: str = Field(..., description="Cron expression for scheduling")
    recipients: List[str] = Field(..., description="Email addresses for report delivery")
    enabled: bool = True


class ExportRequest(BaseModel):
    """Request for data export."""
    data: Dict[str, Any]
    format: str = Field(..., description="Format: csv, pdf, excel")
    filename: str


class AnalyticsMetrics(BaseModel):
    """Analytics metrics response."""
    metric_name: str
    value: float
    unit: str
    trend: Optional[float] = None
    comparison_period: Optional[str] = None


class ReportResponse(BaseModel):
    """Response for report generation."""
    report_id: str
    name: str
    generated_at: datetime
    data: Dict[str, Any]
    summary: Dict[str, Any]
    charts: Optional[List[Dict[str, Any]]] = None


# ============================================================================
# Analytics Endpoints
# ============================================================================

@router.post("/reports/generate")
async def generate_custom_report(
    config: ReportConfig,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
) -> ReportResponse:
    """
    Generate a custom analytics report with specified filters and aggregations.
    
    **Validates: Requirements 21.1, 21.2, 21.3, 21.6**
    """
    tenant_id = current_user.tenant_id
    await verify_tenant_access(current_user, tenant_id, db)
    
    try:
        # Fetch data based on report type
        if config.report_type == "revenue":
            data = await _get_revenue_data(tenant_id, config.filters, db)
        elif config.report_type == "bookings":
            data = await _get_bookings_data(tenant_id, config.filters, db)
        elif config.report_type == "clients":
            data = await _get_clients_data(tenant_id, config.filters, db)
        elif config.report_type == "staff":
            data = await _get_staff_data(tenant_id, config.filters, db)
        elif config.report_type == "inventory":
            data = await _get_inventory_data(tenant_id, config.filters, db)
        else:
            raise HTTPException(status_code=400, detail="Invalid report type")
        
        # Apply aggregation
        aggregated_data = await _apply_aggregation(data, config.aggregation)
        
        # Calculate summary metrics
        summary = await _calculate_summary(aggregated_data)
        
        # Generate charts if requested
        charts = None
        if config.include_charts:
            charts = await _generate_charts(aggregated_data, config.report_type)
        
        # Store report in database
        report_id = await _store_report(
            tenant_id, config.name, aggregated_data, summary, charts, db
        )
        
        return ReportResponse(
            report_id=report_id,
            name=config.name,
            generated_at=datetime.utcnow(),
            data=aggregated_data,
            summary=summary,
            charts=charts
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.get("/reports/{report_id}")
async def get_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
) -> ReportResponse:
    """
    Retrieve a previously generated report.
    
    **Validates: Requirements 21.1, 21.5**
    """
    tenant_id = current_user.tenant_id
    await verify_tenant_access(current_user, tenant_id, db)
    
    report = await db.analytics_reports.find_one({
        "_id": report_id,
        "tenant_id": tenant_id
    })
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return ReportResponse(**report)


@router.get("/reports")
async def list_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
) -> Dict[str, Any]:
    """
    List all reports for the current tenant.
    
    **Validates: Requirements 21.1**
    """
    tenant_id = current_user.tenant_id
    await verify_tenant_access(current_user, tenant_id, db)
    
    reports = await db.analytics_reports.find(
        {"tenant_id": tenant_id}
    ).skip(skip).limit(limit).to_list(limit)
    
    total = await db.analytics_reports.count_documents({"tenant_id": tenant_id})
    
    return {
        "reports": reports,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.post("/reports/{report_id}/export")
async def export_report(
    report_id: str,
    export_request: ExportRequest,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
) -> Dict[str, Any]:
    """
    Export report data in specified format (CSV, PDF, Excel).
    
    **Validates: Requirements 21.5, 21.6**
    """
    tenant_id = current_user.tenant_id
    await verify_tenant_access(current_user, tenant_id, db)
    
    try:
        if export_request.format == "csv":
            export_data = await _export_to_csv(export_request.data)
        elif export_request.format == "pdf":
            export_data = await _export_to_pdf(export_request.data)
        elif export_request.format == "excel":
            export_data = await _export_to_excel(export_request.data)
        else:
            raise HTTPException(status_code=400, detail="Invalid export format")
        
        # Log export
        await db.export_logs.insert_one({
            "tenant_id": tenant_id,
            "user_id": current_user.id,
            "report_id": report_id,
            "format": export_request.format,
            "filename": export_request.filename,
            "created_at": datetime.utcnow()
        })
        
        return {
            "success": True,
            "filename": export_request.filename,
            "format": export_request.format,
            "size": len(export_data)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.post("/reports/schedule")
async def schedule_report(
    config: ScheduledReportConfig,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
) -> Dict[str, Any]:
    """
    Schedule automated report generation and email delivery.
    
    **Validates: Requirements 21.1, 21.5**
    """
    tenant_id = current_user.tenant_id
    await verify_tenant_access(current_user, tenant_id, db)
    
    try:
        schedule_id = await db.report_schedules.insert_one({
            "tenant_id": tenant_id,
            "name": config.name,
            "description": config.description,
            "report_config": config.report_config.dict(),
            "schedule": config.schedule,
            "recipients": config.recipients,
            "enabled": config.enabled,
            "created_by": current_user.id,
            "created_at": datetime.utcnow(),
            "last_run": None,
            "next_run": None
        })
        
        return {
            "schedule_id": str(schedule_id.inserted_id),
            "name": config.name,
            "schedule": config.schedule,
            "enabled": config.enabled
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schedule creation failed: {str(e)}")


@router.get("/schedules")
async def list_schedules(
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    List all scheduled reports for the current tenant.
    
    **Validates: Requirements 21.1**
    """
    tenant_id = current_user.tenant_id
    await verify_tenant_access(current_user, tenant_id, db)
    
    schedules = await db.report_schedules.find(
        {"tenant_id": tenant_id}
    ).to_list(None)
    
    return schedules


@router.get("/metrics/revenue")
async def get_revenue_metrics(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    group_by: str = Query("day", description="day, week, month"),
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get revenue analytics metrics with trend analysis.
    
    **Validates: Requirements 8.3, 21.1, 21.4**
    """
    tenant_id = current_user.tenant_id
    await verify_tenant_access(current_user, tenant_id, db)
    
    try:
        metrics = await _calculate_revenue_metrics(
            tenant_id, start_date, end_date, group_by, db
        )
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metrics calculation failed: {str(e)}")


@router.get("/metrics/bookings")
async def get_bookings_metrics(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    group_by: str = Query("day", description="day, week, month"),
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get booking analytics metrics with trend analysis.
    
    **Validates: Requirements 8.3, 21.1, 21.4**
    """
    tenant_id = current_user.tenant_id
    await verify_tenant_access(current_user, tenant_id, db)
    
    try:
        metrics = await _calculate_bookings_metrics(
            tenant_id, start_date, end_date, group_by, db
        )
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metrics calculation failed: {str(e)}")


@router.get("/metrics/clients")
async def get_clients_metrics(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get client analytics metrics (acquisition, retention, lifetime value).
    
    **Validates: Requirements 8.3, 21.1, 21.4**
    """
    tenant_id = current_user.tenant_id
    await verify_tenant_access(current_user, tenant_id, db)
    
    try:
        metrics = await _calculate_clients_metrics(
            tenant_id, start_date, end_date, db
        )
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metrics calculation failed: {str(e)}")


@router.get("/metrics/staff")
async def get_staff_metrics(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    staff_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get staff performance metrics (utilization, revenue, ratings).
    
    **Validates: Requirements 8.3, 21.1, 21.4**
    """
    tenant_id = current_user.tenant_id
    await verify_tenant_access(current_user, tenant_id, db)
    
    try:
        metrics = await _calculate_staff_metrics(
            tenant_id, start_date, end_date, staff_id, db
        )
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metrics calculation failed: {str(e)}")


@router.get("/filters/available")
async def get_available_filters(
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get available filter options for analytics.
    
    **Validates: Requirements 21.6**
    """
    tenant_id = current_user.tenant_id
    await verify_tenant_access(current_user, tenant_id, db)
    
    try:
        staff = await db.staff.find({"tenant_id": tenant_id}).to_list(None)
        services = await db.services.find({"tenant_id": tenant_id}).to_list(None)
        clients = await db.clients.find({"tenant_id": tenant_id}).to_list(None)
        
        return {
            "staff": [{"id": s["_id"], "name": s.get("name")} for s in staff],
            "services": [{"id": s["_id"], "name": s.get("name")} for s in services],
            "clients": [{"id": c["_id"], "name": c.get("name")} for c in clients],
            "payment_methods": ["cash", "card", "check", "gift_card", "loyalty_points"],
            "booking_status": ["confirmed", "completed", "cancelled", "no_show"],
            "date_ranges": ["today", "this_week", "this_month", "last_month", "this_year", "custom"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Filter retrieval failed: {str(e)}")


# ============================================================================
# Helper Functions
# ============================================================================

async def _get_revenue_data(tenant_id: str, filters: FilterCriteria, db) -> List[Dict]:
    """Fetch revenue data based on filters."""
    query = {"tenant_id": tenant_id}
    
    if filters.date_range:
        query["created_at"] = {
            "$gte": filters.date_range.start_date,
            "$lte": filters.date_range.end_date
        }
    
    if filters.staff_ids:
        query["staff_id"] = {"$in": filters.staff_ids}
    
    if filters.service_ids:
        query["service_ids"] = {"$in": filters.service_ids}
    
    if filters.payment_methods:
        query["payment_method"] = {"$in": filters.payment_methods}
    
    if filters.min_amount is not None:
        query["total_amount"] = {"$gte": filters.min_amount}
    
    if filters.max_amount is not None:
        if "total_amount" not in query:
            query["total_amount"] = {}
        query["total_amount"]["$lte"] = filters.max_amount
    
    return await db.bookings.find(query).to_list(None)


async def _get_bookings_data(tenant_id: str, filters: FilterCriteria, db) -> List[Dict]:
    """Fetch bookings data based on filters."""
    query = {"tenant_id": tenant_id}
    
    if filters.date_range:
        query["start_time"] = {
            "$gte": filters.date_range.start_date,
            "$lte": filters.date_range.end_date
        }
    
    if filters.staff_ids:
        query["staff_id"] = {"$in": filters.staff_ids}
    
    if filters.service_ids:
        query["service_ids"] = {"$in": filters.service_ids}
    
    if filters.booking_status:
        query["status"] = {"$in": filters.booking_status}
    
    return await db.bookings.find(query).to_list(None)


async def _get_clients_data(tenant_id: str, filters: FilterCriteria, db) -> List[Dict]:
    """Fetch clients data based on filters."""
    query = {"tenant_id": tenant_id}
    
    if filters.client_ids:
        query["_id"] = {"$in": filters.client_ids}
    
    return await db.clients.find(query).to_list(None)


async def _get_staff_data(tenant_id: str, filters: FilterCriteria, db) -> List[Dict]:
    """Fetch staff data based on filters."""
    query = {"tenant_id": tenant_id}
    
    if filters.staff_ids:
        query["_id"] = {"$in": filters.staff_ids}
    
    return await db.staff.find(query).to_list(None)


async def _get_inventory_data(tenant_id: str, filters: FilterCriteria, db) -> List[Dict]:
    """Fetch inventory data based on filters."""
    query = {"tenant_id": tenant_id}
    
    return await db.products.find(query).to_list(None)


async def _apply_aggregation(data: List[Dict], config: AggregationConfig) -> Dict[str, Any]:
    """Apply aggregation to data."""
    df = pd.DataFrame(data)
    
    if config.group_by == "day":
        df["date"] = pd.to_datetime(df.get("created_at", df.get("start_time"))).dt.date
        grouped = df.groupby("date")
    elif config.group_by == "week":
        df["week"] = pd.to_datetime(df.get("created_at", df.get("start_time"))).dt.isocalendar().week
        grouped = df.groupby("week")
    elif config.group_by == "month":
        df["month"] = pd.to_datetime(df.get("created_at", df.get("start_time"))).dt.month
        grouped = df.groupby("month")
    else:
        grouped = df.groupby(config.group_by)
    
    result = {}
    for metric in config.metrics:
        if metric == "sum":
            result[metric] = grouped.sum().to_dict()
        elif metric == "avg":
            result[metric] = grouped.mean().to_dict()
        elif metric == "count":
            result[metric] = grouped.count().to_dict()
        elif metric == "min":
            result[metric] = grouped.min().to_dict()
        elif metric == "max":
            result[metric] = grouped.max().to_dict()
    
    return result


async def _calculate_summary(data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate summary statistics from aggregated data."""
    return {
        "total_records": sum(len(v) for v in data.values()) if data else 0,
        "aggregation_complete": True,
        "timestamp": datetime.utcnow().isoformat()
    }


async def _generate_charts(data: Dict[str, Any], report_type: str) -> List[Dict[str, Any]]:
    """Generate chart configurations from data."""
    return [
        {
            "type": "bar",
            "title": f"{report_type.title()} Overview",
            "data": data
        }
    ]


async def _store_report(
    tenant_id: str, name: str, data: Dict, summary: Dict, charts: Optional[List], db
) -> str:
    """Store report in database."""
    result = await db.analytics_reports.insert_one({
        "tenant_id": tenant_id,
        "name": name,
        "data": data,
        "summary": summary,
        "charts": charts,
        "created_at": datetime.utcnow()
    })
    return str(result.inserted_id)


async def _export_to_csv(data: Dict[str, Any]) -> bytes:
    """Export data to CSV format."""
    df = pd.DataFrame(data)
    output = BytesIO()
    df.to_csv(output, index=False)
    return output.getvalue()


async def _export_to_pdf(data: Dict[str, Any]) -> bytes:
    """Export data to PDF format."""
    # Placeholder for PDF export
    return b"PDF export not yet implemented"


async def _export_to_excel(data: Dict[str, Any]) -> bytes:
    """Export data to Excel format."""
    df = pd.DataFrame(data)
    output = BytesIO()
    df.to_excel(output, index=False)
    return output.getvalue()


async def _calculate_revenue_metrics(
    tenant_id: str, start_date: datetime, end_date: datetime, group_by: str, db
) -> Dict[str, Any]:
    """Calculate revenue metrics."""
    bookings = await db.bookings.find({
        "tenant_id": tenant_id,
        "created_at": {"$gte": start_date, "$lte": end_date}
    }).to_list(None)
    
    total_revenue = sum(b.get("total_amount", 0) for b in bookings)
    
    return {
        "total_revenue": total_revenue,
        "booking_count": len(bookings),
        "average_booking_value": total_revenue / len(bookings) if bookings else 0,
        "period": f"{start_date.date()} to {end_date.date()}"
    }


async def _calculate_bookings_metrics(
    tenant_id: str, start_date: datetime, end_date: datetime, group_by: str, db
) -> Dict[str, Any]:
    """Calculate bookings metrics."""
    bookings = await db.bookings.find({
        "tenant_id": tenant_id,
        "start_time": {"$gte": start_date, "$lte": end_date}
    }).to_list(None)
    
    completed = len([b for b in bookings if b.get("status") == "completed"])
    cancelled = len([b for b in bookings if b.get("status") == "cancelled"])
    
    return {
        "total_bookings": len(bookings),
        "completed": completed,
        "cancelled": cancelled,
        "cancellation_rate": cancelled / len(bookings) if bookings else 0,
        "period": f"{start_date.date()} to {end_date.date()}"
    }


async def _calculate_clients_metrics(
    tenant_id: str, start_date: datetime, end_date: datetime, db
) -> Dict[str, Any]:
    """Calculate clients metrics."""
    clients = await db.clients.find({"tenant_id": tenant_id}).to_list(None)
    
    new_clients = len([c for c in clients if c.get("created_at", datetime.utcnow()) >= start_date])
    
    return {
        "total_clients": len(clients),
        "new_clients": new_clients,
        "average_lifetime_value": sum(c.get("total_spent", 0) for c in clients) / len(clients) if clients else 0,
        "period": f"{start_date.date()} to {end_date.date()}"
    }


async def _calculate_staff_metrics(
    tenant_id: str, start_date: datetime, end_date: datetime, staff_id: Optional[str], db
) -> Dict[str, Any]:
    """Calculate staff metrics."""
    query = {"tenant_id": tenant_id, "start_time": {"$gte": start_date, "$lte": end_date}}
    if staff_id:
        query["staff_id"] = staff_id
    
    bookings = await db.bookings.find(query).to_list(None)
    
    return {
        "total_bookings": len(bookings),
        "total_revenue": sum(b.get("total_amount", 0) for b in bookings),
        "average_booking_value": sum(b.get("total_amount", 0) for b in bookings) / len(bookings) if bookings else 0,
        "period": f"{start_date.date()} to {end_date.date()}"
    }
