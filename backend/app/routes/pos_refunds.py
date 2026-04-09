"""API routes for POS refunds."""

from fastapi import APIRouter, Depends, HTTPException, Query
from bson import ObjectId
from decimal import Decimal
from app.context import get_tenant_id, get_user_id
from app.schemas.refund import (
    RefundCreateRequest,
    RefundResponse,
    RefundListResponse,
)
from app.services.refund_service import RefundService
from app.services.pos_audit_service import POSAuditService

router = APIRouter(prefix="/pos/refunds", tags=["pos_refunds"])

refund_service = RefundService()


@router.post("", response_model=RefundResponse)
async def create_refund(
    request: RefundCreateRequest,
    tenant_id: ObjectId = Depends(get_tenant_id),
    user_id: ObjectId = Depends(get_user_id),
):
    """Create a refund request."""
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    
    try:
        refund_data = refund_service.create_refund(
            payment_id=request.payment_id,
            amount=request.amount,
            reason=request.reason,
        )

        # Log refund creation
        POSAuditService.log_action(
            tenant_id=tenant_id,
            user_id=user_id,
            action="refund_created",
            resource_type="refund",
            resource_id=refund_data["refund_id"],
            details={"payment_id": request.payment_id, "amount": str(request.amount)},
        )

        return RefundResponse(
            id=refund_data["refund_id"],
            payment_id=refund_data["payment_id"],
            amount=refund_data["amount"],
            reason=refund_data["reason"],
            status=refund_data["status"],
            reference=refund_data["reference"],
            created_at=refund_data["created_at"].isoformat(),
            updated_at=refund_data["updated_at"].isoformat(),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=RefundListResponse)
async def list_refunds(
    payment_id: str = Query(None, alias="paymentId"),
    status: str = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100, alias="pageSize"),
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """List refunds with pagination."""
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    
    try:
        skip = (page - 1) * page_size
        refunds_data = refund_service.list_refunds(
            payment_id=payment_id,
            status=status,
            skip=skip,
            limit=page_size,
        )

        return RefundListResponse(
            refunds=[
                RefundResponse(
                    id=str(r.id),
                    payment_id=str(r.payment_id),
                    amount=r.amount,
                    reason=r.reason,
                    status=r.status,
                    reference=r.reference,
                    created_at=r.created_at.isoformat(),
                    updated_at=r.updated_at.isoformat(),
                )
                for r in refunds_data["refunds"]
            ],
            total=refunds_data["total"],
            page=page,
            page_size=page_size,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{refund_id}", response_model=RefundResponse)
async def get_refund(
    refund_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """Get refund details."""
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    
    try:
        refund = refund_service.get_refund(refund_id)

        if not refund:
            raise HTTPException(status_code=404, detail="Refund not found")

        return RefundResponse(
            id=str(refund.id),
            payment_id=str(refund.payment_id),
            amount=refund.amount,
            reason=refund.reason,
            status=refund.status,
            reference=refund.reference,
            created_at=refund.created_at.isoformat(),
            updated_at=refund.updated_at.isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{refund_id}/approve", response_model=RefundResponse)
async def approve_refund(
    refund_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id),
    user_id: ObjectId = Depends(get_user_id),
):
    """Approve a refund request."""
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    
    try:
        refund_data = refund_service.update_refund_status(
            refund_id=refund_id,
            status="approved",
        )

        # Log refund approval
        POSAuditService.log_action(
            tenant_id=tenant_id,
            user_id=user_id,
            action="refund_approved",
            resource_type="refund",
            resource_id=refund_id,
        )

        return RefundResponse(
            id=refund_data["refund_id"],
            payment_id=refund_data["payment_id"],
            amount=refund_data["amount"],
            reason=refund_data["reason"],
            status=refund_data["status"],
            reference=refund_data["reference"],
            created_at=refund_data["created_at"].isoformat(),
            updated_at=refund_data["updated_at"].isoformat(),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{refund_id}/process", response_model=RefundResponse)
async def process_refund(
    refund_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id),
    user_id: ObjectId = Depends(get_user_id),
):
    """Process a refund (mark as success)."""
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    
    try:
        refund_data = refund_service.update_refund_status(
            refund_id=refund_id,
            status="success",
        )

        # Log refund processing
        POSAuditService.log_action(
            tenant_id=tenant_id,
            user_id=user_id,
            action="refund_processed",
            resource_type="refund",
            resource_id=refund_id,
        )

        return RefundResponse(
            id=refund_data["refund_id"],
            payment_id=refund_data["payment_id"],
            amount=refund_data["amount"],
            reason=refund_data["reason"],
            status=refund_data["status"],
            reference=refund_data["reference"],
            created_at=refund_data["created_at"].isoformat(),
            updated_at=refund_data["updated_at"].isoformat(),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{refund_id}/reverse", response_model=RefundResponse)
async def reverse_refund(
    refund_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id),
    user_id: ObjectId = Depends(get_user_id),
):
    """Reverse a refund (mark as failed)."""
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    
    try:
        refund_data = refund_service.update_refund_status(
            refund_id=refund_id,
            status="failed",
        )

        # Log refund reversal
        POSAuditService.log_action(
            tenant_id=tenant_id,
            user_id=user_id,
            action="refund_reversed",
            resource_type="refund",
            resource_id=refund_id,
        )

        return RefundResponse(
            id=refund_data["refund_id"],
            payment_id=refund_data["payment_id"],
            amount=refund_data["amount"],
            reason=refund_data["reason"],
            status=refund_data["status"],
            reference=refund_data["reference"],
            created_at=refund_data["created_at"].isoformat(),
            updated_at=refund_data["updated_at"].isoformat(),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
