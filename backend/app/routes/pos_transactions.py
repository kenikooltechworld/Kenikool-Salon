"""API routes for POS transactions."""

from fastapi import APIRouter, Depends, HTTPException, Query
from bson import ObjectId
from decimal import Decimal
from typing import Optional, Dict, Any
from app.context import get_tenant_id, get_user_id
from app.schemas.transaction import (
    TransactionCreateRequest,
    TransactionUpdateRequest,
    TransactionResponse,
    TransactionListResponse,
)
from app.services.transaction_service import TransactionService
from app.services.receipt_service import ReceiptService
from app.services.pos_audit_service import POSAuditService
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/transactions", tags=["transactions"])
payment_service = PaymentService()


@router.post("", response_model=TransactionResponse)
async def create_transaction(
    request: TransactionCreateRequest,
    tenant_id: ObjectId = Depends(get_tenant_id),
    user_id: ObjectId = Depends(get_user_id),
):
    """Create a new transaction."""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"[TransactionCreate] Starting transaction creation for tenant {tenant_id}")
        
        # Validate request
        logger.info(f"[TransactionCreate] Validating request data")
        TransactionService.validate_transaction_data(request.dict())

        # Create transaction
        logger.info(f"[TransactionCreate] Creating transaction with {len(request.items)} items")
        transaction = TransactionService.create_transaction(
            tenant_id=tenant_id,
            customer_id=ObjectId(request.customer_id),
            staff_id=ObjectId(request.staff_id),
            items_data=[item.dict() for item in request.items],
            payment_method=request.payment_method,
            transaction_type=request.transaction_type,
            appointment_id=ObjectId(request.appointment_id) if request.appointment_id else None,
            discount_amount=request.discount_amount,
            notes=request.notes,
        )
        logger.info(f"[TransactionCreate] Transaction created: {transaction.id}")

        # Log transaction creation
        logger.info(f"[TransactionCreate] Logging transaction creation")
        POSAuditService.log_transaction_created(
            tenant_id=tenant_id,
            transaction_id=transaction.id,
            user_id=user_id,
            transaction_data=request.dict(),
        )

        # NOTE: Receipt generation is deferred until payment is verified
        # For cash/check payments, receipt will be generated after payment status is confirmed
        # For card/mobile money, receipt will be generated after webhook verification
        logger.info(f"[TransactionCreate] Receipt generation deferred until payment verification")

        logger.info(f"[TransactionCreate] Transaction creation completed successfully")
        return TransactionResponse(
            id=str(transaction.id),
            customer_id=str(transaction.customer_id),
            staff_id=str(transaction.staff_id),
            appointment_id=str(transaction.appointment_id) if transaction.appointment_id else None,
            transaction_type=transaction.transaction_type,
            items=[
                {
                    "item_type": item.item_type,
                    "item_id": str(item.item_id),
                    "item_name": item.item_name,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "line_total": item.line_total,
                    "tax_rate": item.tax_rate,
                    "tax_amount": item.tax_amount,
                    "discount_rate": item.discount_rate,
                    "discount_amount": item.discount_amount,
                }
                for item in transaction.items
            ],
            subtotal=transaction.subtotal,
            tax_amount=transaction.tax_amount,
            discount_amount=transaction.discount_amount,
            total=transaction.total,
            payment_method=transaction.payment_method,
            payment_status=transaction.payment_status,
            reference_number=transaction.reference_number,
            paystack_reference=transaction.paystack_reference,
            notes=transaction.notes,
            created_at=transaction.created_at.isoformat(),
            updated_at=transaction.updated_at.isoformat(),
        )
    except ValueError as e:
        logger.error(f"[TransactionCreate] Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[TransactionCreate] Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=TransactionListResponse)
async def list_transactions(
    customer_id: str = Query(None, alias="customerId"),
    staff_id: str = Query(None, alias="staffId"),
    payment_status: str = Query(None, alias="paymentStatus"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100, alias="pageSize"),
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """List transactions."""
    try:
        transactions, total = TransactionService.list_transactions(
            tenant_id=tenant_id,
            customer_id=ObjectId(customer_id) if customer_id else None,
            staff_id=ObjectId(staff_id) if staff_id else None,
            payment_status=payment_status,
            page=page,
            page_size=page_size,
        )

        return TransactionListResponse(
            transactions=[
                TransactionResponse(
                    id=str(t.id),
                    customer_id=str(t.customer_id),
                    staff_id=str(t.staff_id),
                    appointment_id=str(t.appointment_id) if t.appointment_id else None,
                    transaction_type=t.transaction_type,
                    items=[
                        {
                            "item_type": item.item_type,
                            "item_id": str(item.item_id),
                            "item_name": item.item_name,
                            "quantity": item.quantity,
                            "unit_price": item.unit_price,
                            "line_total": item.line_total,
                            "tax_rate": item.tax_rate,
                            "tax_amount": item.tax_amount,
                            "discount_rate": item.discount_rate,
                            "discount_amount": item.discount_amount,
                        }
                        for item in t.items
                    ],
                    subtotal=t.subtotal,
                    tax_amount=t.tax_amount,
                    discount_amount=t.discount_amount,
                    total=t.total,
                    payment_method=t.payment_method,
                    payment_status=t.payment_status,
                    reference_number=t.reference_number,
                    paystack_reference=t.paystack_reference,
                    notes=t.notes,
                    created_at=t.created_at.isoformat(),
                    updated_at=t.updated_at.isoformat(),
                )
                for t in transactions
            ],
            total=total,
            page=page,
            page_size=page_size,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """Get transaction details."""
    try:
        transaction = TransactionService.get_transaction(
            tenant_id=tenant_id,
            transaction_id=ObjectId(transaction_id),
        )

        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")

        return TransactionResponse(
            id=str(transaction.id),
            customer_id=str(transaction.customer_id),
            staff_id=str(transaction.staff_id),
            appointment_id=str(transaction.appointment_id) if transaction.appointment_id else None,
            transaction_type=transaction.transaction_type,
            items=[
                {
                    "item_type": item.item_type,
                    "item_id": str(item.item_id),
                    "item_name": item.item_name,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "line_total": item.line_total,
                    "tax_rate": item.tax_rate,
                    "tax_amount": item.tax_amount,
                    "discount_rate": item.discount_rate,
                    "discount_amount": item.discount_amount,
                }
                for item in transaction.items
            ],
            subtotal=transaction.subtotal,
            tax_amount=transaction.tax_amount,
            discount_amount=transaction.discount_amount,
            total=transaction.total,
            payment_method=transaction.payment_method,
            payment_status=transaction.payment_status,
            reference_number=transaction.reference_number,
            paystack_reference=transaction.paystack_reference,
            notes=transaction.notes,
            created_at=transaction.created_at.isoformat(),
            updated_at=transaction.updated_at.isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: str,
    request: TransactionUpdateRequest,
    tenant_id: ObjectId = Depends(get_tenant_id),
    user_id: ObjectId = Depends(get_user_id),
):
    """Update transaction."""
    try:
        transaction = TransactionService.update_transaction_status(
            tenant_id=tenant_id,
            transaction_id=ObjectId(transaction_id),
            payment_status=request.payment_status or "pending",
        )

        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")

        # Log transaction modification
        POSAuditService.log_transaction_modified(
            tenant_id=tenant_id,
            transaction_id=transaction.id,
            old_value={},
            new_value=request.dict(),
            user_id=user_id,
        )

        return TransactionResponse(
            id=str(transaction.id),
            customer_id=str(transaction.customer_id),
            staff_id=str(transaction.staff_id),
            appointment_id=str(transaction.appointment_id) if transaction.appointment_id else None,
            transaction_type=transaction.transaction_type,
            items=[
                {
                    "item_type": item.item_type,
                    "item_id": str(item.item_id),
                    "item_name": item.item_name,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "line_total": item.line_total,
                    "tax_rate": item.tax_rate,
                    "tax_amount": item.tax_amount,
                    "discount_rate": item.discount_rate,
                    "discount_amount": item.discount_amount,
                }
                for item in transaction.items
            ],
            subtotal=transaction.subtotal,
            tax_amount=transaction.tax_amount,
            discount_amount=transaction.discount_amount,
            total=transaction.total,
            payment_method=transaction.payment_method,
            payment_status=transaction.payment_status,
            reference_number=transaction.reference_number,
            paystack_reference=transaction.paystack_reference,
            notes=transaction.notes,
            created_at=transaction.created_at.isoformat(),
            updated_at=transaction.updated_at.isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/{transaction_id}/initialize-payment")
async def initialize_transaction_payment(
    transaction_id: str,
    request: Dict[str, Any],
    tenant_id: ObjectId = Depends(get_tenant_id),
    user_id: ObjectId = Depends(get_user_id),
):
    """
    Initialize payment for a POS transaction using Paystack.
    
    This endpoint is called when a customer chooses to pay via card/online payment
    for a POS transaction. It follows the same pattern as booking payments.
    
    Args:
        transaction_id: Transaction ID to initialize payment for
        request: Dictionary with email and optional callback_url
        tenant_id: Tenant ID (from dependency)
        user_id: User ID (from dependency)
        
    Returns:
        Dictionary with authorization_url, access_code, and reference
        
    Raises:
        HTTPException: If transaction not found or payment initialization fails
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"[TransactionPayment] Initializing payment for transaction {transaction_id}")
        
        # Get transaction
        transaction = TransactionService.get_transaction(
            tenant_id=tenant_id,
            transaction_id=ObjectId(transaction_id),
        )
        
        if not transaction:
            logger.error(f"[TransactionPayment] Transaction not found: {transaction_id}")
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Extract email from request
        email = request.get("email")
        callback_url = request.get("callback_url")
        
        if not email:
            logger.error(f"[TransactionPayment] Email not provided")
            raise HTTPException(status_code=400, detail="Email is required")
        
        logger.info(f"[TransactionPayment] Initializing Paystack payment for amount {transaction.total}")
        
        # Initialize payment with Paystack
        result = payment_service.initialize_pos_payment(
            amount=transaction.total,
            email=email,
            callback_url=callback_url,
            metadata={
                "transaction_id": str(transaction.id),
                "customer_id": str(transaction.customer_id),
                "staff_id": str(transaction.staff_id),
                "transaction_type": transaction.transaction_type,
                "payment_type": "pos",
            },
        )
        
        # Store Paystack reference in transaction
        transaction.paystack_reference = result.get("reference")
        transaction.save()
        
        logger.info(f"[TransactionPayment] Payment initialized with reference {result.get('reference')}")
        
        # Log payment initialization
        POSAuditService.log_payment_processed(
            tenant_id=tenant_id,
            transaction_id=transaction.id,
            user_id=user_id,
            payment_method="paystack",
            amount=transaction.total,
            reference=result.get("reference"),
        )
        
        return {
            "success": True,
            "payment_id": result.get("payment_id"),
            "authorization_url": result.get("authorization_url"),
            "access_code": result.get("access_code"),
            "reference": result.get("reference"),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[TransactionPayment] Error initializing payment: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Payment initialization failed: {str(e)}")


@router.post("/{transaction_id}/verify-payment")
async def verify_transaction_payment(
    transaction_id: str,
    request: Dict[str, Any],
    tenant_id: ObjectId = Depends(get_tenant_id),
    user_id: ObjectId = Depends(get_user_id),
):
    """
    Verify payment for a POS transaction after Paystack redirect.
    
    This endpoint is called after the customer completes payment on Paystack.
    It verifies the payment status and updates the transaction accordingly.
    
    Args:
        transaction_id: Transaction ID to verify payment for
        request: Dictionary with reference (Paystack reference)
        tenant_id: Tenant ID (from dependency)
        user_id: User ID (from dependency)
        
    Returns:
        Dictionary with payment status and transaction details
        
    Raises:
        HTTPException: If transaction not found or verification fails
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"[TransactionPaymentVerify] Verifying payment for transaction {transaction_id}")
        
        # Get transaction
        transaction = TransactionService.get_transaction(
            tenant_id=tenant_id,
            transaction_id=ObjectId(transaction_id),
        )
        
        if not transaction:
            logger.error(f"[TransactionPaymentVerify] Transaction not found: {transaction_id}")
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Extract reference from request
        reference = request.get("reference")
        
        if not reference:
            logger.error(f"[TransactionPaymentVerify] Reference not provided")
            raise HTTPException(status_code=400, detail="Reference is required")
        
        logger.info(f"[TransactionPaymentVerify] Verifying Paystack reference {reference}")
        
        # Verify payment with Paystack
        verification_result = payment_service.verify_payment(reference)
        
        if not verification_result:
            logger.error(f"[TransactionPaymentVerify] Payment verification failed for reference {reference}")
            raise HTTPException(status_code=400, detail="Payment verification failed")
        
        payment_status = verification_result.get("status")
        
        logger.info(f"[TransactionPaymentVerify] Payment status: {payment_status}")
        
        # Update transaction status based on payment verification
        if payment_status == "success":
            logger.info(f"[TransactionPaymentVerify] Payment successful, updating transaction status")
            transaction.payment_status = "completed"
            transaction.paystack_reference = reference
            transaction.save()
            
            # Generate receipt AFTER payment is verified
            logger.info(f"[TransactionPaymentVerify] Generating receipt after payment verification")
            try:
                ReceiptService.generate_receipt(tenant_id, transaction.id)
                logger.info(f"[TransactionPaymentVerify] Receipt generated successfully")
            except Exception as e:
                logger.error(f"[TransactionPaymentVerify] Error generating receipt: {str(e)}", exc_info=True)
            
            # Log payment completion
            POSAuditService.log_payment_processed(
                tenant_id=tenant_id,
                transaction_id=transaction.id,
                user_id=user_id,
                payment_method="paystack",
                amount=transaction.total,
                reference=reference,
            )
            
            return {
                "success": True,
                "payment_status": "completed",
                "transaction_id": str(transaction.id),
                "reference": reference,
                "amount": float(transaction.total),
                "message": "Payment verified successfully",
            }
        else:
            logger.warning(f"[TransactionPaymentVerify] Payment not successful: {payment_status}")
            transaction.payment_status = "failed"
            transaction.save()
            
            return {
                "success": False,
                "payment_status": payment_status,
                "transaction_id": str(transaction.id),
                "reference": reference,
                "message": f"Payment {payment_status}",
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[TransactionPaymentVerify] Error verifying payment: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Payment verification failed: {str(e)}")


@router.post("/{transaction_id}/generate-receipt")
async def generate_receipt_for_transaction(
    transaction_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id),
    user_id: ObjectId = Depends(get_user_id),
):
    """
    Generate receipt for a transaction after payment is confirmed.
    
    This endpoint is called after cash/check payments are confirmed.
    It generates the receipt for the transaction.
    
    Args:
        transaction_id: Transaction ID to generate receipt for
        tenant_id: Tenant ID (from dependency)
        user_id: User ID (from dependency)
        
    Returns:
        Dictionary with receipt generation status
        
    Raises:
        HTTPException: If transaction not found or receipt generation fails
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"[GenerateReceipt] Generating receipt for transaction {transaction_id}")
        
        # Get transaction
        transaction = TransactionService.get_transaction(
            tenant_id=tenant_id,
            transaction_id=ObjectId(transaction_id),
        )
        
        if not transaction:
            logger.error(f"[GenerateReceipt] Transaction not found: {transaction_id}")
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Generate receipt
        logger.info(f"[GenerateReceipt] Generating receipt")
        try:
            ReceiptService.generate_receipt(tenant_id, transaction.id)
            logger.info(f"[GenerateReceipt] Receipt generated successfully")
            
            return {
                "success": True,
                "message": "Receipt generated successfully",
                "transaction_id": str(transaction.id),
            }
        except Exception as e:
            logger.error(f"[GenerateReceipt] Error generating receipt: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Receipt generation failed: {str(e)}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[GenerateReceipt] Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Receipt generation failed: {str(e)}")
