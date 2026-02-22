"""Audit logging routes for compliance and security."""

import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query, Request
from pydantic import BaseModel
from app.services.audit_service import AuditService
from app.context import get_tenant_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/audit", tags=["audit"])


class AuditLogResponse(BaseModel):
    """Audit log response schema."""

    id: str
    event_type: str
    resource: str
    user_id: str = None
    ip_address: str
    status_code: int
    user_agent: str = None
    created_at: str


class ComplianceReportResponse(BaseModel):
    """Compliance report response schema."""

    tenant_id: str
    period: dict
    total_events: int
    events_by_type: dict
    events_by_resource: dict
    failed_operations: int
    unique_users: int
    unique_ips: int


def get_audit_service() -> AuditService:
    """Get audit service."""
    return AuditService()


@router.get("/logs", response_model=list[AuditLogResponse])
async def get_audit_logs(
    request: Request,
    user_id: str = Query(None),
    event_type: str = Query(None),
    resource: str = Query(None),
    days: int = Query(7, ge=1, le=90),
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0),
    audit_service: AuditService = Depends(get_audit_service),
):
    """
    Get audit logs with filtering.

    Query parameters:
    - user_id: Filter by user ID
    - event_type: Filter by event type (GET, POST, etc.)
    - resource: Filter by resource path
    - days: Number of days to look back (default: 7)
    - limit: Maximum results (default: 100)
    - skip: Number of results to skip (default: 0)
    """
    # Get tenant_id from cookie
    tenant_id = request.cookies.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Calculate date range
    end_date = datetime.utcnow()
    start_date = datetime.utcnow() - __import__("datetime").timedelta(days=days)

    logs = audit_service.get_audit_logs(
        tenant_id=tenant_id,
        user_id=user_id,
        event_type=event_type,
        resource=resource,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        skip=skip,
    )

    return [
        AuditLogResponse(
            id=str(log.id),
            event_type=log.event_type,
            resource=log.resource,
            user_id=log.user_id,
            ip_address=log.ip_address,
            status_code=log.status_code,
            user_agent=log.user_agent,
            created_at=log.created_at.isoformat(),
        )
        for log in logs
    ]


@router.get("/logs/{log_id}", response_model=AuditLogResponse)
async def get_audit_log(
    request: Request,
    log_id: str,
    audit_service: AuditService = Depends(get_audit_service),
):
    """Get a specific audit log."""
    # Get tenant_id from cookie
    tenant_id = request.cookies.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    log = audit_service.get_audit_log_by_id(tenant_id, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Audit log not found")

    return AuditLogResponse(
        id=str(log.id),
        event_type=log.event_type,
        resource=log.resource,
        user_id=log.user_id,
        ip_address=log.ip_address,
        status_code=log.status_code,
        user_agent=log.user_agent,
        created_at=log.created_at.isoformat(),
    )


@router.get("/reports/compliance", response_model=ComplianceReportResponse)
async def get_compliance_report(
    request: Request,
    days: int = Query(30, ge=1, le=365),
    audit_service: AuditService = Depends(get_audit_service),
):
    """
    Generate compliance report.

    Query parameters:
    - days: Number of days to include in report (default: 30)
    """
    # Get tenant_id from cookie
    tenant_id = request.cookies.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    end_date = datetime.utcnow()
    start_date = datetime.utcnow() - __import__("datetime").timedelta(days=days)

    report = audit_service.generate_compliance_report(
        tenant_id=tenant_id,
        start_date=start_date,
        end_date=end_date,
    )

    if not report:
        raise HTTPException(status_code=500, detail="Failed to generate report")

    return ComplianceReportResponse(**report)


@router.get("/reports/suspicious")
async def get_suspicious_activity(
    request: Request,
    days: int = Query(7, ge=1, le=90),
    audit_service: AuditService = Depends(get_audit_service),
):
    """
    Get suspicious activity report.

    Query parameters:
    - days: Number of days to look back (default: 7)
    """
    # Get tenant_id from cookie
    tenant_id = request.cookies.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    logs = audit_service.get_suspicious_activity(tenant_id=tenant_id, days=days)

    return {
        "total_suspicious_events": len(logs),
        "events": [
            {
                "id": str(log.id),
                "event_type": log.event_type,
                "resource": log.resource,
                "ip_address": log.ip_address,
                "status_code": log.status_code,
                "created_at": log.created_at.isoformat(),
            }
            for log in logs
        ],
    }
