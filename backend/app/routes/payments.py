"""Payment routes for payment operations."""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from app.schemas.payment import (
    PaymentInitializeRequest,
    PaymentInitializeResponse,
    PaymentResponse,
    PaymentListResponse,
)
from app.services.payment_service import PaymentService
from app.context import get_tenant_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["payments"])
payment_service = PaymentService()


@router.post("/initialize", response_model=PaymentInitializeResponse)
async def initialize_payment(request: PaymentInitializeRequest):
    """
    Initialize a payment transaction.

    This endpoint accepts payment details, validates them, calls Paystack to
    initialize a transaction, and stores the payment record with pending status.
    Supports idempotency through idempotency_key to prevent duplicate payments.

    Args:
        request: PaymentInitializeRequest with amount, customer_id, invoice_id, email, metadata, idempotency_key

    Returns:
        PaymentInitializeResponse with payment_id, authorization_url, access_code, reference

    Raises:
        HTTPException: If validation fails or payment initialization fails
    """
    try:
        tenant_id = get_tenant_id()
        if not tenant_id:
            raise HTTPException(status_code=401, detail="Tenant context not found")

        # Initialize payment
        result = payment_service.initialize_payment(
            amount=request.amount,
            customer_id=request.customer_id,
            invoice_id=request.invoice_id,
            email=request.email,
            metadata=request.metadata,
            idempotency_key=request.idempotency_key,
        )

        return PaymentInitializeResponse(**result)

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error initializing payment: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize payment")


@router.post("/booking/initialize", response_model=PaymentInitializeResponse)
async def initialize_booking_payment(request: dict):
    """
    Initialize a payment transaction for a booking (without invoice).

    This endpoint is specifically for booking payments where no invoice exists yet.
    After successful payment, the booking will be created.

    Args:
        request: Dictionary with amount, email, callback_url, metadata (containing booking_data)

    Returns:
        PaymentInitializeResponse with payment_id, authorization_url, access_code, reference

    Raises:
        HTTPException: If validation fails or payment initialization fails
    """
    try:
        amount = request.get("amount")
        email = request.get("email")
        callback_url = request.get("callback_url")
        metadata = request.get("metadata", {})

        # Convert amount to float for validation
        try:
            amount_float = float(amount) if amount else 0
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Amount must be a valid number")

        if not amount_float or amount_float <= 0:
            raise HTTPException(status_code=400, detail="Valid amount is required")
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")

        # Initialize payment without invoice
        # Note: This endpoint works with or without tenant context (for public bookings)
        result = payment_service.initialize_booking_payment(
            amount=Decimal(str(amount_float)),
            email=email,
            callback_url=callback_url,
            metadata=metadata,
        )

        return PaymentInitializeResponse(**result)

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error initializing booking payment: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize payment")


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: str):
    """
    Get a payment by ID.

    Args:
        payment_id: Payment ID

    Returns:
        PaymentResponse with payment details

    Raises:
        HTTPException: If payment not found
    """
    try:
        tenant_id = get_tenant_id()
        if not tenant_id:
            raise HTTPException(status_code=401, detail="Tenant context not found")

        payment = payment_service.get_payment(payment_id)
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")

        return PaymentResponse(
            id=str(payment.id),
            amount=payment.amount,
            customer_id=str(payment.customer_id),
            invoice_id=str(payment.invoice_id),
            reference=payment.reference,
            status=payment.status,
            gateway=payment.gateway,
            metadata=payment.metadata,
            created_at=payment.created_at,
            updated_at=payment.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving payment: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve payment")


@router.get("/{reference}/verify", response_model=PaymentResponse)
async def verify_payment(reference: str):
    """
    Verify a payment transaction with Paystack and update local record.

    This endpoint calls Paystack to verify the transaction status and updates
    the local payment record if the status has changed. If payment succeeded,
    the associated invoice is marked as paid.

    Args:
        reference: Paystack transaction reference

    Returns:
        PaymentResponse with current payment status

    Raises:
        HTTPException: If verification fails or payment not found
    """
    try:
        tenant_id = get_tenant_id()
        if not tenant_id:
            raise HTTPException(status_code=401, detail="Tenant context not found")

        result = payment_service.verify_payment(reference)

        return PaymentResponse(
            id=result["payment_id"],
            amount=result["amount"],
            customer_id=result["customer_id"],
            invoice_id=result["invoice_id"],
            reference=result["reference"],
            status=result["status"],
            gateway=result["gateway"],
            metadata={},
            created_at=result["created_at"],
            updated_at=result["updated_at"],
        )

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error verifying payment: {e}")
        raise HTTPException(status_code=500, detail="Failed to verify payment")


@router.post("/{payment_id}/retry", response_model=PaymentResponse)
async def retry_payment(payment_id: str):
    """
    Retry a failed payment with exponential backoff.

    This endpoint allows customers to retry a failed payment up to 3 times.
    Exponential backoff is applied between retries (1s, 2s, 4s, 8s).
    On final failure, a notification is queued for the customer.

    Args:
        payment_id: Payment ID to retry

    Returns:
        PaymentResponse with updated payment status

    Raises:
        HTTPException: If payment cannot be retried or retry fails
    """
    try:
        tenant_id = get_tenant_id()
        if not tenant_id:
            raise HTTPException(status_code=401, detail="Tenant context not found")

        result = payment_service.retry_payment(payment_id)

        return PaymentResponse(
            id=result["payment_id"],
            amount=result["amount"],
            customer_id="",  # Not included in retry response
            invoice_id="",  # Not included in retry response
            reference=result["reference"],
            status=result["status"],
            gateway="paystack",
            metadata={
                "retry_count": result["retry_count"],
                "max_retries": result["max_retries"],
                "next_retry_at": str(result["next_retry_at"]) if result["next_retry_at"] else None,
            },
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrying payment: {e}")
        raise HTTPException(status_code=500, detail="Failed to retry payment")


@router.get("", response_model=PaymentListResponse)
async def list_payments(
    customer_id: Optional[str] = Query(None, description="Filter by customer ID"),
    invoice_id: Optional[str] = Query(None, description="Filter by invoice ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
):
    """
    List payments with optional filtering.

    Args:
        customer_id: Filter by customer ID
        invoice_id: Filter by invoice ID
        status: Filter by status (pending, success, failed, cancelled)
        skip: Number of records to skip
        limit: Number of records to return

    Returns:
        PaymentListResponse with total count and list of payments

    Raises:
        HTTPException: If request fails
    """
    try:
        tenant_id = get_tenant_id()
        if not tenant_id:
            raise HTTPException(status_code=401, detail="Tenant context not found")

        result = payment_service.list_payments(
            customer_id=customer_id,
            invoice_id=invoice_id,
            status=status,
            skip=skip,
            limit=limit,
        )

        payments = [
            PaymentResponse(
                id=str(p.id),
                amount=p.amount,
                customer_id=str(p.customer_id),
                invoice_id=str(p.invoice_id),
                reference=p.reference,
                status=p.status,
                gateway=p.gateway,
                metadata=p.metadata,
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
            for p in result["payments"]
        ]

        return PaymentListResponse(
            total=result["total"],
            page=skip // limit + 1,
            page_size=limit,
            payments=payments,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing payments: {e}")
        raise HTTPException(status_code=500, detail="Failed to list payments")


@router.get("/{reference}/booking-status")
async def get_booking_status(reference: str):
    """
    Check if a booking was created from a payment.
    
    This endpoint is used by the frontend to poll for booking creation after payment.
    It returns the appointment ID if the booking was created, or null if still pending.
    
    Args:
        reference: Paystack payment reference
        
    Returns:
        Dictionary with appointment_id if booking exists, or null if not yet created
        
    Raises:
        HTTPException: If payment not found or request fails
    """
    try:
        # Get payment by reference (works without tenant context for public bookings)
        from app.models.payment import Payment as PaymentModel
        payment = PaymentModel.objects(reference=reference).first()
        
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        # Check if appointment was created
        appointment_id = payment.metadata.get("appointment_id")
        
        return {
            "payment_id": str(payment.id),
            "reference": payment.reference,
            "status": payment.status,
            "appointment_id": appointment_id,
            "booking_created": appointment_id is not None,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking booking status: {e}")
        raise HTTPException(status_code=500, detail="Failed to check booking status")


@router.post("/pos/initialize", response_model=PaymentInitializeResponse)
async def initialize_pos_payment(request: dict):
    """
    Initialize a payment transaction for POS (without invoice).

    This endpoint is specifically for POS transactions where payment is processed
    at point of sale. After successful payment, the transaction is marked as completed.

    Args:
        request: Dictionary with amount, email, callback_url, metadata (containing transaction_id)

    Returns:
        PaymentInitializeResponse with payment_id, authorization_url, access_code, reference

    Raises:
        HTTPException: If validation fails or payment initialization fails
    """
    try:
        tenant_id = get_tenant_id()
        if not tenant_id:
            raise HTTPException(status_code=401, detail="Tenant context not found")

        amount = request.get("amount")
        email = request.get("email")
        callback_url = request.get("callback_url")
        metadata = request.get("metadata", {})

        # Convert amount to float for validation
        try:
            amount_float = float(amount) if amount else 0
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Amount must be a valid number")

        if not amount_float or amount_float <= 0:
            raise HTTPException(status_code=400, detail="Valid amount is required")
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")

        # Initialize payment for POS transaction
        result = payment_service.initialize_pos_payment(
            amount=Decimal(str(amount_float)),
            email=email,
            callback_url=callback_url,
            metadata=metadata,
        )

        return PaymentInitializeResponse(**result)

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error initializing POS payment: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize payment")
