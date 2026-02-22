"""Time-off request management routes."""

import logging
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from bson import ObjectId
from app.models.time_off_request import TimeOffRequest
from app.models.staff import Staff
from app.models.user import User
from app.context import get_tenant_id
from app.decorators.tenant_isolated import tenant_isolated
from app.schemas.time_off_request import (
    TimeOffRequestCreate,
    TimeOffRequestUpdate,
    TimeOffRequestApprove,
    TimeOffRequestDeny,
    TimeOffRequestResponse,
    TimeOffRequestListResponse,
)
from app.tasks import queue_notification

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/time-off-requests", tags=["time-off-requests"])


def get_tenant_id_from_context() -> ObjectId:
    """Get tenant_id from context."""
    tenant_id = get_tenant_id()
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    return tenant_id


def time_off_request_to_response(request: TimeOffRequest) -> dict:
    """Convert TimeOffRequest model to response."""
    return {
        "id": str(request.id),
        "staff_id": str(request.staff_id),
        "start_date": request.start_date.isoformat(),
        "end_date": request.end_date.isoformat(),
        "reason": request.reason,
        "status": request.status,
        "requested_at": request.requested_at.isoformat(),
        "reviewed_at": request.reviewed_at.isoformat() if request.reviewed_at else None,
        "reviewed_by": str(request.reviewed_by) if request.reviewed_by else None,
        "created_at": request.created_at.isoformat(),
        "updated_at": request.updated_at.isoformat(),
    }


@router.get("", response_model=dict)
@tenant_isolated
async def list_time_off_requests(
    staff_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    List time-off requests for the tenant.

    Returns a paginated list of time-off requests with optional filtering by staff and status.
    """
    try:
        # Query time-off requests
        query = TimeOffRequest.objects(tenant_id=tenant_id)

        # Apply filters
        if staff_id:
            query = query(staff_id=ObjectId(staff_id))
        
        if status:
            query = query(status=status)

        # Get total count
        total = query.count()

        # Apply pagination
        skip = (page - 1) * page_size
        requests = query.skip(skip).limit(page_size).order_by("-created_at")

        # Convert to response format
        request_list = [time_off_request_to_response(req) for req in requests]

        return {
            "requests": request_list,
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    except Exception as e:
        logger.error(f"Failed to list time-off requests: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to list time-off requests")


@router.get("/{request_id}", response_model=dict)
@tenant_isolated
async def get_time_off_request(
    request_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    Get a specific time-off request.

    Returns the time-off request details for the given request ID.
    """
    try:
        request = TimeOffRequest.objects(id=ObjectId(request_id), tenant_id=tenant_id).first()
        if not request:
            raise HTTPException(status_code=404, detail="Time-off request not found")
        
        return time_off_request_to_response(request)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.error(f"Failed to get time-off request: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to get time-off request")


@router.post("", response_model=dict)
@tenant_isolated
async def create_time_off_request(
    request_data: dict = Body(...),
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    Create a new time-off request.

    Creates a new time-off request and queues notification for manager.
    """
    try:
        logger.info(f"Creating time-off request with data: {request_data}")
        
        # Validate staff_id exists
        staff_id = request_data.get("staff_id")
        if not staff_id:
            raise HTTPException(status_code=400, detail="staff_id is required")
        
        staff = Staff.objects(id=ObjectId(staff_id), tenant_id=tenant_id).first()
        if not staff:
            raise HTTPException(status_code=400, detail="Staff member not found")

        # Validate dates
        start_date = request_data.get("start_date")
        end_date = request_data.get("end_date")
        reason = request_data.get("reason")

        if not start_date or not end_date or not reason:
            raise HTTPException(status_code=400, detail="start_date, end_date, and reason are required")

        if start_date > end_date:
            raise HTTPException(status_code=400, detail="start_date must be before end_date")

        # Create new time-off request
        new_request = TimeOffRequest(
            tenant_id=tenant_id,
            staff_id=ObjectId(staff_id),
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            status="pending",
        )
        
        new_request.save()
        logger.info(f"Created time-off request: {new_request.id}")

        # Queue notification for manager
        try:
            staff_user = User.objects(id=staff.user_id).first()
            staff_name = f"{staff_user.first_name} {staff_user.last_name}" if staff_user else "Staff Member"
            
            queue_notification(
                tenant_id=str(tenant_id),
                notification_type="time_off_request_created",
                recipient_id="manager",  # Will be handled by notification system
                data={
                    "request_id": str(new_request.id),
                    "staff_name": staff_name,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "reason": reason,
                }
            )
            logger.info(f"Queued notification for time-off request: {new_request.id}")
        except Exception as e:
            logger.error(f"Failed to queue notification: {str(e)}")
            # Don't fail the request creation if notification fails

        return time_off_request_to_response(new_request)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create time-off request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to create time-off request")


@router.put("/{request_id}/approve", response_model=dict)
@tenant_isolated
async def approve_time_off_request(
    request_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    Approve a time-off request.

    Approves the time-off request and queues notification for staff member.
    """
    try:
        request = TimeOffRequest.objects(id=ObjectId(request_id), tenant_id=tenant_id).first()
        if not request:
            raise HTTPException(status_code=404, detail="Time-off request not found")

        if request.status != "pending":
            raise HTTPException(status_code=400, detail="Only pending requests can be approved")

        # Update request
        request.status = "approved"
        request.reviewed_at = datetime.utcnow()
        request.save()
        logger.info(f"Approved time-off request: {request.id}")

        # Queue notification for staff member
        try:
            staff = Staff.objects(id=request.staff_id).first()
            if staff:
                staff_user = User.objects(id=staff.user_id).first()
                staff_name = f"{staff_user.first_name} {staff_user.last_name}" if staff_user else "Staff Member"
                
                queue_notification(
                    tenant_id=str(tenant_id),
                    notification_type="time_off_request_approved",
                    recipient_id=str(staff.user_id),
                    data={
                        "request_id": str(request.id),
                        "staff_name": staff_name,
                        "start_date": request.start_date.isoformat(),
                        "end_date": request.end_date.isoformat(),
                    }
                )
                logger.info(f"Queued approval notification for time-off request: {request.id}")
        except Exception as e:
            logger.error(f"Failed to queue notification: {str(e)}")
            # Don't fail the approval if notification fails

        return time_off_request_to_response(request)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to approve time-off request: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to approve time-off request")


@router.put("/{request_id}/deny", response_model=dict)
@tenant_isolated
async def deny_time_off_request(
    request_id: str,
    denial_data: dict = Body(...),
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    Deny a time-off request.

    Denies the time-off request and queues notification for staff member.
    """
    try:
        request = TimeOffRequest.objects(id=ObjectId(request_id), tenant_id=tenant_id).first()
        if not request:
            raise HTTPException(status_code=404, detail="Time-off request not found")

        if request.status != "pending":
            raise HTTPException(status_code=400, detail="Only pending requests can be denied")

        # Update request
        request.status = "denied"
        request.reviewed_at = datetime.utcnow()
        request.save()
        logger.info(f"Denied time-off request: {request.id}")

        # Queue notification for staff member
        try:
            staff = Staff.objects(id=request.staff_id).first()
            if staff:
                staff_user = User.objects(id=staff.user_id).first()
                staff_name = f"{staff_user.first_name} {staff_user.last_name}" if staff_user else "Staff Member"
                
                queue_notification(
                    tenant_id=str(tenant_id),
                    notification_type="time_off_request_denied",
                    recipient_id=str(staff.user_id),
                    data={
                        "request_id": str(request.id),
                        "staff_name": staff_name,
                        "start_date": request.start_date.isoformat(),
                        "end_date": request.end_date.isoformat(),
                        "denial_reason": denial_data.get("denial_reason", ""),
                    }
                )
                logger.info(f"Queued denial notification for time-off request: {request.id}")
        except Exception as e:
            logger.error(f"Failed to queue notification: {str(e)}")
            # Don't fail the denial if notification fails

        return time_off_request_to_response(request)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to deny time-off request: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to deny time-off request")
