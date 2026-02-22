"""
Payment Management API Endpoints
Handles payment operations including detail view, refunds, and related operations
"""
from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from typing import Optional, Dict, Any
from datetime import datetime
import io

from app.api.dependencies import get_tenant_id, require_owner_or_admin
from app.schemas.payment import (
    PaymentDetailResponse,
    RefundRequest,
    RefundResponse,
    ManualPaymentRequest,
    PaymentResponse,
    EmailReceiptRequest
)
from app.services.payment_management_service import payment_management_service
from app.services.receipt_service import receipt_service
from app.services.payment_analytics_service import payment_analytics_service
from app.services.reconciliation_service import reconciliation_service
from app.services.customer_payment_portal_service import customer_payment_portal_service
from app.api.exceptions import BadRequestException

router = APIRouter(prefix="/api/payments", tags=["payments"])


@router.get("/{payment_id}", response_model=PaymentDetailResponse)
async def get_payment_detail(
    payment_id: str,
    tenant_id: str = Depends(get_tenant_id),
    user: Dict = Depends(require_owner_or_admin)
):
    """
    Get detailed payment information including related booking and customer data
    
    Args:
        payment_id: Payment ID to retrieve
        tenant_id: Tenant ID (from dependency)
        user: Current user (from dependency)
        
    Returns:
        PaymentDetailResponse with complete payment information
        
    Raises:
        NotFoundException: If payment not found
        BadRequestException: If payment ID format is invalid
    """
    return payment_management_service.get_payment_detail(tenant_id, payment_id)


@router.post("/{payment_id}/refund", response_model=RefundResponse)
async def process_refund(
    payment_id: str,
    request: RefundRequest,
    tenant_id: str = Depends(get_tenant_id),
    user: Dict = Depends(require_owner_or_admin)
):
    """
    Process full or partial refund for a payment
    
    Validates refund amount, updates payment status, and creates refund record
    
    Args:
        payment_id: Payment ID to refund
        request: RefundRequest with refund details
        tenant_id: Tenant ID (from dependency)
        user: Current user (from dependency)
        
    Returns:
        RefundResponse with refund details and status
        
    Raises:
        NotFoundException: If payment not found
        BadRequestException: If refund validation fails
    """
    # Validate request
    if request.refund_amount <= 0:
        raise BadRequestException("Refund amount must be greater than zero")
    
    if request.refund_type not in ["full", "partial"]:
        raise BadRequestException("Refund type must be 'full' or 'partial'")
    
    if len(request.reason) < 10:
        raise BadRequestException("Refund reason must be at least 10 characters")
    
    # Process refund
    result = payment_management_service.process_refund(
        tenant_id=tenant_id,
        payment_id=payment_id,
        refund_amount=request.refund_amount,
        reason=request.reason,
        refund_type=request.refund_type,
        processed_by=user.get("id") or user.get("user_id")
    )
    
    return RefundResponse(
        refund_id=result["refund_id"],
        payment_id=result["payment_id"],
        refund_amount=result["refund_amount"],
        refund_type=result["refund_type"],
        status=result["status"],
        processed_at=result["processed_at"],
        message=result["message"]
    )


@router.get("/{payment_id}/refund-history")
async def get_refund_history(
    payment_id: str,
    tenant_id: str = Depends(get_tenant_id),
    user: Dict = Depends(require_owner_or_admin)
):
    """
    Get refund history for a payment
    
    Args:
        payment_id: Payment ID
        tenant_id: Tenant ID (from dependency)
        user: Current user (from dependency)
        
    Returns:
        List of refund records
    """
    return payment_management_service.get_refund_history(tenant_id, payment_id)


@router.post("/manual", response_model=PaymentResponse)
async def record_manual_payment(
    request: ManualPaymentRequest,
    tenant_id: str = Depends(get_tenant_id),
    user: Dict = Depends(require_owner_or_admin)
):
    """
    Record a manual payment (cash, check, bank transfer, etc.)
    
    Creates payment record and updates booking status
    
    Args:
        request: ManualPaymentRequest with payment details
        tenant_id: Tenant ID (from dependency)
        user: Current user (from dependency)
        
    Returns:
        PaymentResponse with created payment
        
    Raises:
        NotFoundException: If booking not found
        BadRequestException: If validation fails
    """
    result = payment_management_service.record_manual_payment(
        tenant_id=tenant_id,
        booking_id=request.booking_id,
        amount=request.amount,
        payment_method=request.payment_method,
        recorded_by=user.get("id") or user.get("user_id"),
        reference=request.reference,
        notes=request.notes
    )
    
    return PaymentResponse(
        id=result["id"],
        tenant_id=result["tenant_id"],
        booking_id=result["booking_id"],
        amount=result["amount"],
        gateway=result["gateway"],
        reference=result["reference"],
        status=result["status"],
        payment_type=result["payment_type"],
        created_at=result["created_at"],
        updated_at=result["updated_at"],
        verified_at=result["verified_at"],
        is_manual=result["is_manual"],
        recorded_by=result["recorded_by"]
    )


@router.get("/{payment_id}/receipt")
async def generate_receipt(
    payment_id: str,
    tenant_id: str = Depends(get_tenant_id),
    user: Dict = Depends(require_owner_or_admin)
):
    """
    Generate PDF receipt for payment
    
    Args:
        payment_id: Payment ID
        tenant_id: Tenant ID (from dependency)
        user: Current user (from dependency)
        
    Returns:
        PDF file response
        
    Raises:
        NotFoundException: If payment not found
    """
    result = receipt_service.generate_receipt(
        tenant_id=tenant_id,
        payment_id=payment_id,
        generated_by=user.get("id") or user.get("user_id")
    )
    
    # Return PDF as file response
    pdf_bytes = result["pdf_bytes"]
    receipt_number = result["receipt_number"]
    
    return FileResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        filename=f"{receipt_number}.pdf"
    )


@router.post("/{payment_id}/receipt/email")
async def email_receipt(
    payment_id: str,
    request: Optional[EmailReceiptRequest] = None,
    tenant_id: str = Depends(get_tenant_id),
    user: Dict = Depends(require_owner_or_admin)
):
    """
    Email payment receipt to customer
    
    Args:
        payment_id: Payment ID
        request: Optional EmailReceiptRequest with email address
        tenant_id: Tenant ID (from dependency)
        user: Current user (from dependency)
        
    Returns:
        Success confirmation
        
    Raises:
        NotFoundException: If payment not found
        BadRequestException: If no email address available
    """
    email_address = request.email if request else None
    
    result = receipt_service.email_receipt(
        tenant_id=tenant_id,
        payment_id=payment_id,
        email_address=email_address
    )
    
    return result



@router.get("/analytics", response_model=Dict)
async def get_payment_analytics(
    tenant_id: str = Depends(get_tenant_id),
    date_from: Optional[str] = Query(None, description="Start date (ISO format)"),
    date_to: Optional[str] = Query(None, description="End date (ISO format)"),
    user: Dict = Depends(require_owner_or_admin)
):
    """
    Get payment analytics and statistics
    
    Args:
        tenant_id: Tenant ID (from dependency)
        date_from: Start date (ISO format, optional)
        date_to: End date (ISO format, optional)
        user: Current user (from dependency)
        
    Returns:
        PaymentAnalyticsResponse with trends, breakdowns, and metrics
        
    Raises:
        BadRequestException: If date range is invalid
    """
    return payment_analytics_service.get_payment_analytics(
        tenant_id=tenant_id,
        date_from=date_from,
        date_to=date_to
    )


@router.get("/reconciliation", response_model=Dict)
async def get_reconciliation_data(
    tenant_id: str = Depends(get_tenant_id),
    days_back: int = Query(30, description="Number of days to look back"),
    user: Dict = Depends(require_owner_or_admin)
):
    """
    Get payment reconciliation data
    
    Returns unmatched payments, duplicates, and sync status
    
    Args:
        tenant_id: Tenant ID (from dependency)
        days_back: Number of days to look back (default 30)
        user: Current user (from dependency)
        
    Returns:
        ReconciliationResponse with reconciliation data
        
    Raises:
        BadRequestException: If parameters are invalid
    """
    if days_back < 1 or days_back > 365:
        raise BadRequestException("days_back must be between 1 and 365")
    
    return reconciliation_service.get_reconciliation_data(
        tenant_id=tenant_id,
        days_back=days_back
    )


@router.post("/{payment_id}/sync", response_model=Dict)
async def sync_payment_with_gateway(
    payment_id: str,
    tenant_id: str = Depends(get_tenant_id),
    user: Dict = Depends(require_owner_or_admin)
):
    """
    Sync payment status with gateway
    
    Args:
        payment_id: Payment ID to sync
        tenant_id: Tenant ID (from dependency)
        user: Current user (from dependency)
        
    Returns:
        Updated payment data with sync status
        
    Raises:
        NotFoundException: If payment not found
        BadRequestException: If sync fails
    """
    return reconciliation_service.sync_with_gateway(
        tenant_id=tenant_id,
        payment_id=payment_id
    )


@router.post("/{payment_id}/match", response_model=Dict)
async def manual_match_payment(
    payment_id: str,
    booking_id: str = Query(..., description="Booking ID to link to"),
    tenant_id: str = Depends(get_tenant_id),
    user: Dict = Depends(require_owner_or_admin)
):
    """
    Manually link a payment to a booking
    
    Args:
        payment_id: Payment ID to match
        booking_id: Booking ID to link to
        tenant_id: Tenant ID (from dependency)
        user: Current user (from dependency)
        
    Returns:
        Updated payment data
        
    Raises:
        NotFoundException: If payment or booking not found
        BadRequestException: If validation fails
    """
    return reconciliation_service.manual_match_payment(
        tenant_id=tenant_id,
        payment_id=payment_id,
        booking_id=booking_id,
        matched_by=user.get("id") or user.get("user_id")
    )


@router.get("/reconciliation/report", response_model=Dict)
async def get_reconciliation_report(
    tenant_id: str = Depends(get_tenant_id),
    days_back: int = Query(30, description="Number of days to include in report"),
    user: Dict = Depends(require_owner_or_admin)
):
    """
    Generate a reconciliation report
    
    Args:
        tenant_id: Tenant ID (from dependency)
        days_back: Number of days to include (default 30)
        user: Current user (from dependency)
        
    Returns:
        Reconciliation report with metrics and recommendations
    """
    if days_back < 1 or days_back > 365:
        raise BadRequestException("days_back must be between 1 and 365")
    
    return reconciliation_service.get_reconciliation_report(
        tenant_id=tenant_id,
        days_back=days_back
    )


@router.get("/customer/{customer_id}", response_model=Dict)
async def get_customer_payments(
    customer_id: str,
    tenant_id: str = Depends(get_tenant_id),
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    user: Dict = Depends(require_owner_or_admin)
):
    """
    Get payments for a customer's bookings
    
    Args:
        customer_id: Customer ID to fetch payments for
        tenant_id: Tenant ID (from dependency)
        limit: Maximum number of payments to return (1-100)
        skip: Number of payments to skip (for pagination)
        user: Current user (from dependency)
        
    Returns:
        Dict with customer payments and pagination info
        
    Raises:
        NotFoundException: If customer not found
        BadRequestException: If parameters are invalid
    """
    return customer_payment_portal_service.get_customer_payments(
        tenant_id=tenant_id,
        customer_id=customer_id,
        limit=limit,
        skip=skip
    )


@router.post("/customer/{customer_id}/link", response_model=Dict)
async def generate_payment_link(
    customer_id: str,
    payment_id: str = Query(..., description="Payment ID to generate link for"),
    expires_in_days: int = Query(30, ge=1, le=365),
    tenant_id: str = Depends(get_tenant_id),
    user: Dict = Depends(require_owner_or_admin)
):
    """
    Generate a shareable payment link for a pending payment
    
    Args:
        customer_id: Customer ID
        payment_id: Payment ID to generate link for
        expires_in_days: Number of days until link expires (1-365)
        tenant_id: Tenant ID (from dependency)
        user: Current user (from dependency)
        
    Returns:
        Dict with payment link and token
        
    Raises:
        NotFoundException: If payment not found
        BadRequestException: If payment is not pending
    """
    return customer_payment_portal_service.generate_payment_link(
        tenant_id=tenant_id,
        customer_id=customer_id,
        payment_id=payment_id,
        expires_in_days=expires_in_days
    )


@router.get("/link/{token}", response_model=Dict)
async def validate_payment_link(
    token: str,
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Validate a payment link token and get payment details
    
    This endpoint is public (no authentication required) to allow customers
    to access payment links via email
    
    Args:
        token: Payment link token
        tenant_id: Tenant ID (from dependency)
        
    Returns:
        Dict with payment details and link info
        
    Raises:
        NotFoundException: If link not found or expired
        BadRequestException: If link is invalid
    """
    return customer_payment_portal_service.validate_payment_link(
        tenant_id=tenant_id,
        token=token
    )


@router.get("/customer/{customer_id}/status/{payment_id}", response_model=Dict)
async def get_payment_status(
    customer_id: str,
    payment_id: str,
    tenant_id: str = Depends(get_tenant_id),
    user: Dict = Depends(require_owner_or_admin)
):
    """
    Get real-time payment status for a customer
    
    Args:
        customer_id: Customer ID
        payment_id: Payment ID
        tenant_id: Tenant ID (from dependency)
        user: Current user (from dependency)
        
    Returns:
        Dict with payment status and details
        
    Raises:
        NotFoundException: If payment not found
        UnauthorizedException: If payment doesn't belong to customer
    """
    return customer_payment_portal_service.get_payment_status(
        tenant_id=tenant_id,
        customer_id=customer_id,
        payment_id=payment_id
    )


@router.post("/checkout", response_model=Dict)
async def process_booking_checkout(
    request: Dict[str, Any],
    tenant_id: str = Depends(get_tenant_id),
    user: Dict = Depends(require_owner_or_admin)
):
    """
    Process checkout for a booking with multiple payment methods including gift cards
    
    Supports split payments with cash, card, transfer, and gift cards.
    Gift cards are validated and redeemed as part of the checkout process.
    
    Args:
        request: CheckoutRequest with booking_id and payment_methods
        tenant_id: Tenant ID (from dependency)
        user: Current user (from dependency)
        
    Returns:
        Dict with payment confirmation and gift card redemption details
        
    Raises:
        NotFoundException: If booking not found
        BadRequestException: If payment validation fails or gift card is invalid
    """
    from app.services.pos_service import POSService
    from app.database import Database
    from bson import ObjectId
    from datetime import datetime, timezone
    
    db = Database.get_db()
    
    booking_id = request.get("booking_id")
    payment_methods = request.get("payment_methods", [])
    
    if not booking_id:
        raise BadRequestException("booking_id is required")
    
    if not payment_methods:
        raise BadRequestException("At least one payment method is required")
    
    # Get booking
    booking = db.bookings.find_one({
        "_id": ObjectId(booking_id),
        "tenant_id": tenant_id
    })
    
    if not booking:
        from app.api.exceptions import NotFoundException
        raise NotFoundException("Booking not found")
    
    # Calculate total amount due
    service_price = booking.get("service", {}).get("price", 0)
    deposit_paid = booking.get("deposit_amount", 0)
    remaining_balance = service_price - deposit_paid
    
    # Calculate total payment amount
    total_payment = sum(pm.get("amount", 0) for pm in payment_methods)
    
    # Validate payment amount
    if total_payment < remaining_balance:
        raise BadRequestException(
            f"Insufficient payment. Required: {remaining_balance}, Provided: {total_payment}"
        )
    
    # Process gift card payments
    gift_card_redemptions = []
    for payment in payment_methods:
        if payment.get("method") == "gift_card":
            card_number = payment.get("gift_card_code") or payment.get("reference")
            if not card_number:
                raise BadRequestException("Gift card number is required")
            
            # Redeem gift card
            try:
                redemption = POSService.redeem_gift_card(
                    tenant_id=tenant_id,
                    card_number=card_number,
                    amount=payment.get("amount", 0),
                    transaction_id=booking_id,
                    location="Online Booking"
                )
                gift_card_redemptions.append({
                    "card_number": card_number,
                    "amount": payment.get("amount", 0),
                    "remaining_balance": redemption["remaining_balance"]
                })
            except Exception as e:
                # Rollback any successful gift card redemptions
                for redemption in gift_card_redemptions:
                    try:
                        # Refund the gift card
                        gift_card = db.gift_cards.find_one({
                            "tenant_id": tenant_id,
                            "card_number": redemption["card_number"]
                        })
                        if gift_card:
                            db.gift_cards.update_one(
                                {"_id": gift_card["_id"]},
                                {
                                    "$inc": {"balance": redemption["amount"]},
                                    "$push": {
                                        "transactions": {
                                            "type": "refund",
                                            "transaction_id": booking_id,
                                            "amount": redemption["amount"],
                                            "balance_after": gift_card["balance"] + redemption["amount"],
                                            "timestamp": datetime.now(timezone.utc),
                                            "reason": "payment_failed"
                                        }
                                    }
                                }
                            )
                    except Exception as rollback_error:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.error(f"Failed to rollback gift card redemption: {str(rollback_error)}")
                
                raise BadRequestException(f"Gift card payment failed: {str(e)}")
    
    # Update booking with payment information
    update_data = {
        "$set": {
            "payment_status": "paid",
            "payment_methods": payment_methods,
            "paid_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
    }
    
    # Add gift card redemption details if any
    if gift_card_redemptions:
        update_data["$set"]["gift_card_redemptions"] = gift_card_redemptions
    
    db.bookings.update_one(
        {"_id": ObjectId(booking_id)},
        update_data
    )
    
    # Create payment record
    payment_record = {
        "tenant_id": tenant_id,
        "booking_id": booking_id,
        "amount": total_payment,
        "payment_methods": payment_methods,
        "gift_card_redemptions": gift_card_redemptions,
        "status": "completed",
        "created_at": datetime.now(timezone.utc),
        "created_by": user.get("id") or user.get("user_id")
    }
    
    result = db.payments.insert_one(payment_record)
    payment_id = str(result.inserted_id)
    
    return {
        "status": "success",
        "payment_id": payment_id,
        "booking_id": booking_id,
        "total_paid": total_payment,
        "change": total_payment - remaining_balance if total_payment > remaining_balance else 0,
        "gift_card_redemptions": gift_card_redemptions,
        "message": "Payment processed successfully"
    }


@router.post("/initialize")
async def initialize_payment(
    data: Dict,
    tenant_id: str = Depends(get_tenant_id)
):
    """Initialize payment for external payment gateway (Paystack, Flutterwave, etc.)"""
    try:
        booking_id = data.get("booking_id")
        amount = data.get("amount")
        email = data.get("email")
        payment_gateway = data.get("payment_gateway", "paystack")
        
        if not booking_id or not amount or not email:
            raise BadRequestException("booking_id, amount, and email are required")
        
        result = payment_management_service.initialize_payment(
            tenant_id=tenant_id,
            booking_id=booking_id,
            amount=amount,
            email=email,
            payment_gateway=payment_gateway
        )
        
        return {
            "success": True,
            "authorization_url": result.get("authorization_url"),
            "access_code": result.get("access_code"),
            "reference": result.get("reference")
        }
    except BadRequestException:
        raise
    except Exception as e:
        raise BadRequestException(f"Payment initialization failed: {str(e)}")
