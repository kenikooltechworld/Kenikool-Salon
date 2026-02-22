"""Refund routes for refund operations."""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from app.schemas.refund import (
    RefundCreateRequest,
    RefundResponse,
    RefundListResponse,
)
from app.services.refund_service import RefundService
from app.context import get_tenant_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["refunds"])
refund_service = RefundService()


@router.post("/{payment_id}/refund", response_model=RefundResponse)
async def create_refund(payment_id: str, request: RefundCreateRequest):
    """
    Create a refund for a payment.

    This endpoint validates the payment is in success status, validates the refund
    amount does not exceed the original payment amount, calls Paystack to process
    the refund, and creates a Refund record with pending status.

    Args:
        payment_id: Payment ID to refund
        request: RefundCreateRequest with amount and reason

    Returns:
        RefundResponse with refund details

    Raises:
        HTTPException: If validation fails or refund creation fails
    """
    try:
        tenant_id = get_tenant_id()
        if not tenant_id:
            raise HTTPException(status_code=401, detail="Tenant context not found")

        result = refund_service.create_refund(
            payment_id=payment_id,
            amount=request.amount,
            reason=request.reason,
        )

        return RefundResponse(**result)

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating refund: {e}")
        raise HTTPException(status_code=500, detail="Failed to create refund")


@router.get("/refunds/{refund_id}", response_model=RefundResponse)
async def get_refund(refund_id: str):
    """
    Get a refund by ID.

    Args:
        refund_id: Refund ID

    Returns:
        RefundResponse with refund details

    Raises:
        HTTPException: If refund not found
    """
    try:
        tenant_id = get_tenant_id()
        if not tenant_id:
            raise HTTPException(status_code=401, detail="Tenant context not found")

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
            metadata=refund.metadata,
            created_at=refund.created_at,
            updated_at=refund.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving refund: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve refund")


@router.get("/refunds", response_model=RefundListResponse)
async def list_refunds(
    payment_id: Optional[str] = Query(None, description="Filter by payment ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
):
    """
    List refunds with optional filtering.

    Args:
        payment_id: Filter by payment ID
        status: Filter by status (pending, success, failed)
        skip: Number of records to skip
        limit: Number of records to return

    Returns:
        RefundListResponse with total count and list of refunds

    Raises:
        HTTPException: If request fails
    """
    try:
        tenant_id = get_tenant_id()
        if not tenant_id:
            raise HTTPException(status_code=401, detail="Tenant context not found")

        result = refund_service.list_refunds(
            payment_id=payment_id,
            status=status,
            skip=skip,
            limit=limit,
        )

        refunds = [
            RefundResponse(
                id=str(r.id),
                payment_id=str(r.payment_id),
                amount=r.amount,
                reason=r.reason,
                status=r.status,
                reference=r.reference,
                metadata=r.metadata,
                created_at=r.created_at,
                updated_at=r.updated_at,
            )
            for r in result["refunds"]
        ]

        return RefundListResponse(
            total=result["total"],
            page=skip // limit + 1,
            page_size=limit,
            refunds=refunds,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing refunds: {e}")
        raise HTTPException(status_code=500, detail="Failed to list refunds")
