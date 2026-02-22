"""Payment service for managing payment operations."""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Optional
from bson import ObjectId
from app.models.payment import Payment
from app.models.invoice import Invoice
from app.models.customer import Customer
from app.services.paystack_service import PaystackService
from app.context import get_tenant_id

logger = logging.getLogger(__name__)


class PaymentService:
    """Service for managing payment operations."""

    def __init__(self):
        """Initialize payment service."""
        self.paystack_service = PaystackService()

    def _calculate_retry_delay(self, retry_count: int) -> int:
        """
        Calculate exponential backoff delay in seconds.

        Args:
            retry_count: Current retry count (0-based)

        Returns:
            Delay in seconds (2^retry_count)
        """
        # Exponential backoff: 1s, 2s, 4s, 8s, etc.
        return 2 ** retry_count

    def initialize_payment(
        self,
        amount: Decimal,
        customer_id: str,
        invoice_id: str,
        email: str,
        metadata: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Initialize a payment transaction with Paystack.

        Args:
            amount: Payment amount
            customer_id: Customer ID
            invoice_id: Invoice ID
            email: Customer email for payment
            metadata: Additional metadata
            idempotency_key: Unique key for idempotency (prevents duplicate payments)

        Returns:
            Dictionary with payment_id, authorization_url, access_code, reference

        Raises:
            ValueError: If validation fails
            Exception: If Paystack API call fails
        """
        tenant_id = get_tenant_id()
        
        # Check for duplicate payment using idempotency key
        if idempotency_key:
            existing_payment = Payment.objects(
                tenant_id=ObjectId(tenant_id),
                idempotency_key=idempotency_key
            ).first()
            if existing_payment:
                logger.info(
                    f"Duplicate payment detected with idempotency_key {idempotency_key}. "
                    f"Returning existing payment {existing_payment.id}"
                )
                return {
                    "payment_id": str(existing_payment.id),
                    "authorization_url": existing_payment.metadata.get("authorization_url", ""),
                    "access_code": existing_payment.metadata.get("access_code", ""),
                    "reference": existing_payment.reference,
                    "is_duplicate": True,
                }
        
        # Validate inputs
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")
        
        if not customer_id:
            raise ValueError("Customer ID is required")
        
        if not invoice_id:
            raise ValueError("Invoice ID is required")
        
        if not email:
            raise ValueError("Email is required")

        # Verify customer exists
        try:
            customer = Customer.objects(
                id=ObjectId(customer_id),
                tenant_id=ObjectId(tenant_id)
            ).first()
            if not customer:
                raise ValueError(f"Customer {customer_id} not found")
        except Exception as e:
            logger.error(f"Error verifying customer: {e}")
            raise ValueError(f"Invalid customer ID: {customer_id}")

        # Verify invoice exists
        try:
            invoice = Invoice.objects(
                id=ObjectId(invoice_id),
                tenant_id=ObjectId(tenant_id)
            ).first()
            if not invoice:
                raise ValueError(f"Invoice {invoice_id} not found")
        except Exception as e:
            logger.error(f"Error verifying invoice: {e}")
            raise ValueError(f"Invalid invoice ID: {invoice_id}")

        # Verify invoice amount matches payment amount
        if invoice.total != amount:
            logger.warning(
                f"Payment amount {amount} does not match invoice total {invoice.total}"
            )

        # Prepare metadata
        if metadata is None:
            metadata = {}
        
        metadata.update({
            "customer_id": str(customer_id),
            "invoice_id": str(invoice_id),
            "customer_name": f"{customer.first_name} {customer.last_name}",
        })

        # Call Paystack to initialize transaction
        try:
            paystack_response = self.paystack_service.initialize_transaction(
                amount=float(amount),
                email=email,
                metadata=metadata,
            )
        except Exception as e:
            logger.error(f"Paystack initialization failed: {e}")
            raise Exception(f"Failed to initialize payment: {str(e)}")

        # Extract Paystack response data
        reference = paystack_response.get("reference")
        authorization_url = paystack_response.get("authorization_url")
        access_code = paystack_response.get("access_code")

        if not reference or not authorization_url:
            raise Exception("Invalid Paystack response: missing reference or authorization_url")

        # Create payment record
        try:
            payment = Payment(
                tenant_id=ObjectId(tenant_id),
                customer_id=ObjectId(customer_id),
                invoice_id=ObjectId(invoice_id),
                amount=amount,
                reference=reference,
                gateway="paystack",
                status="pending",
                idempotency_key=idempotency_key,
                metadata=metadata,
            )
            # Store authorization details in metadata for duplicate detection
            payment.metadata["authorization_url"] = authorization_url
            payment.metadata["access_code"] = access_code
            payment.save()
            logger.info(f"Payment created: {payment.id} with reference {reference}")
        except Exception as e:
            logger.error(f"Error creating payment record: {e}")
            raise Exception(f"Failed to create payment record: {str(e)}")

        return {
            "payment_id": str(payment.id),
            "authorization_url": authorization_url,
            "access_code": access_code,
            "reference": reference,
        }

    def initialize_booking_payment(
        self,
        amount: Decimal,
        email: str,
        callback_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Initialize a payment transaction for a booking (without invoice).

        This is used when a customer wants to pay for a booking before it's created.
        After successful payment, the booking will be created.

        Args:
            amount: Payment amount
            email: Customer email for payment
            callback_url: URL to redirect to after payment
            metadata: Additional metadata (should contain booking_data)

        Returns:
            Dictionary with payment_id, authorization_url, access_code, reference

        Raises:
            ValueError: If validation fails
            Exception: If Paystack API call fails
        """
        import uuid
        
        tenant_id = get_tenant_id()
        
        # Convert amount to float if it's a string
        try:
            amount_float = float(amount)
        except (ValueError, TypeError):
            raise ValueError("Amount must be a valid number")
        
        # Validate inputs
        if amount_float <= 0:
            raise ValueError("Amount must be greater than 0")
        
        if not email:
            raise ValueError("Email is required")

        # Prepare metadata
        if metadata is None:
            metadata = {}
        
        metadata.update({
            "payment_type": "booking",
            "created_at": datetime.utcnow().isoformat(),
        })
        
        # Generate unique idempotency key for booking payments
        # This prevents duplicate key errors when retrying payment initialization
        idempotency_key = str(uuid.uuid4())

        # Call Paystack to initialize transaction
        try:
            paystack_response = self.paystack_service.initialize_transaction(
                amount=float(amount),
                email=email,
                callback_url=callback_url,
                metadata=metadata,
            )
        except Exception as e:
            logger.error(f"Paystack initialization failed: {e}")
            raise Exception(f"Failed to initialize payment: {str(e)}")

        # Extract Paystack response data
        reference = paystack_response.get("reference")
        authorization_url = paystack_response.get("authorization_url")
        access_code = paystack_response.get("access_code")

        if not reference or not authorization_url:
            raise Exception("Invalid Paystack response: missing reference or authorization_url")

        # Create payment record (without customer_id and invoice_id for booking payments)
        try:
            payment = Payment(
                tenant_id=ObjectId(tenant_id) if tenant_id else None,
                amount=amount,
                reference=reference,
                gateway="paystack",
                status="pending",
                idempotency_key=idempotency_key,
                metadata=metadata,
            )
            # Store authorization details in metadata
            payment.metadata["authorization_url"] = authorization_url
            payment.metadata["access_code"] = access_code
            payment.save()
            logger.info(f"Booking payment created: {payment.id} with reference {reference}")
        except Exception as e:
            logger.error(f"Error creating payment record: {e}")
            raise Exception(f"Failed to create payment record: {str(e)}")

        return {
            "payment_id": str(payment.id),
            "authorization_url": authorization_url,
            "access_code": access_code,
            "reference": reference,
        }

    def get_payment(self, payment_id: str) -> Optional[Payment]:
        """
        Get a payment by ID.

        Args:
            payment_id: Payment ID

        Returns:
            Payment object or None if not found
        """
        tenant_id = get_tenant_id()
        
        try:
            payment = Payment.objects(
                id=ObjectId(payment_id),
                tenant_id=ObjectId(tenant_id)
            ).first()
            return payment
        except Exception as e:
            logger.error(f"Error retrieving payment: {e}")
            return None

    def get_payment_by_reference(self, reference: str) -> Optional[Payment]:
        """
        Get a payment by Paystack reference.

        Args:
            reference: Paystack reference

        Returns:
            Payment object or None if not found
        """
        tenant_id = get_tenant_id()
        
        try:
            payment = Payment.objects(
                reference=reference,
                tenant_id=ObjectId(tenant_id)
            ).first()
            return payment
        except Exception as e:
            logger.error(f"Error retrieving payment by reference: {e}")
            return None

    def verify_payment(self, reference: str) -> Dict[str, Any]:
        """
        Verify a payment transaction with Paystack and update local record.

        Args:
            reference: Paystack transaction reference

        Returns:
            Dictionary with payment status and details

        Raises:
            ValueError: If reference is invalid or payment not found
            Exception: If Paystack verification fails
        """
        tenant_id = get_tenant_id()
        
        if not reference:
            raise ValueError("Reference is required")

        # Get local payment record
        payment = self.get_payment_by_reference(reference)
        if not payment:
            raise ValueError(f"Payment with reference {reference} not found")

        # Verify with Paystack
        try:
            paystack_data = self.paystack_service.verify_transaction(reference)
        except Exception as e:
            logger.error(f"Paystack verification failed for {reference}: {e}")
            raise Exception(f"Failed to verify payment with Paystack: {str(e)}")

        # Extract status from Paystack response
        paystack_status = paystack_data.get("status", "").lower()
        
        # Map Paystack status to local status
        status_mapping = {
            "success": "success",
            "pending": "pending",
            "failed": "failed",
            "abandoned": "failed",
        }
        
        new_status = status_mapping.get(paystack_status, "failed")

        # Update payment record if status changed
        old_status = payment.status
        if old_status != new_status:
            payment.status = new_status
            payment.metadata["paystack_data"] = paystack_data
            payment.save()
            logger.info(
                f"Payment {reference} status updated from {old_status} to {new_status}"
            )

            # If payment succeeded, update invoice status
            if new_status == "success" and old_status != "success":
                try:
                    invoice = Invoice.objects(
                        id=payment.invoice_id,
                        tenant_id=ObjectId(tenant_id)
                    ).first()
                    if invoice:
                        invoice.status = "paid"
                        invoice.paid_at = datetime.utcnow()
                        invoice.save()
                        logger.info(f"Invoice {invoice.id} marked as paid")
                except Exception as e:
                    logger.error(f"Error updating invoice status: {e}")

        return {
            "payment_id": str(payment.id),
            "reference": payment.reference,
            "status": payment.status,
            "amount": float(payment.amount),
            "customer_id": str(payment.customer_id),
            "invoice_id": str(payment.invoice_id),
            "gateway": payment.gateway,
            "created_at": payment.created_at,
            "updated_at": payment.updated_at,
        }

    def list_payments(
        self,
        customer_id: Optional[str] = None,
        invoice_id: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        List payments with optional filtering.

        Args:
            customer_id: Filter by customer ID
            invoice_id: Filter by invoice ID
            status: Filter by status
            skip: Number of records to skip
            limit: Number of records to return

        Returns:
            Dictionary with total count and list of payments
        """
        tenant_id = get_tenant_id()
        
        query = Payment.objects(tenant_id=ObjectId(tenant_id))

        if customer_id:
            try:
                query = query.filter(customer_id=ObjectId(customer_id))
            except Exception:
                pass

        if invoice_id:
            try:
                query = query.filter(invoice_id=ObjectId(invoice_id))
            except Exception:
                pass

        if status:
            query = query.filter(status=status)

        total = query.count()
        payments = query.skip(skip).limit(limit).order_by("-created_at")

        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "payments": list(payments),
        }

    def retry_payment(self, payment_id: str) -> Dict[str, Any]:
        """
        Retry a failed payment with exponential backoff.

        Args:
            payment_id: Payment ID to retry

        Returns:
            Dictionary with new payment status and retry information

        Raises:
            ValueError: If payment cannot be retried
            Exception: If retry fails
        """
        tenant_id = get_tenant_id()
        
        # Get payment record
        try:
            payment = Payment.objects(
                id=ObjectId(payment_id),
                tenant_id=ObjectId(tenant_id)
            ).first()
            if not payment:
                raise ValueError(f"Payment {payment_id} not found")
        except Exception as e:
            logger.error(f"Error retrieving payment: {e}")
            raise ValueError(f"Invalid payment ID: {payment_id}")

        # Validate payment can be retried
        if payment.status == "success":
            raise ValueError("Cannot retry a successful payment")
        
        if payment.status == "cancelled":
            raise ValueError("Cannot retry a cancelled payment")
        
        if payment.retry_count >= payment.max_retries:
            raise ValueError(
                f"Maximum retries ({payment.max_retries}) exceeded for payment {payment_id}"
            )

        # Check if enough time has passed since last retry (exponential backoff)
        if payment.next_retry_at and datetime.utcnow() < payment.next_retry_at:
            raise ValueError(
                f"Payment retry not yet available. Next retry at {payment.next_retry_at}"
            )

        # Increment retry count
        payment.retry_count += 1
        payment.last_retry_at = datetime.utcnow()
        
        # Calculate next retry time
        if payment.retry_count < payment.max_retries:
            delay_seconds = self._calculate_retry_delay(payment.retry_count)
            payment.next_retry_at = datetime.utcnow() + __import__('datetime').timedelta(seconds=delay_seconds)
        
        payment.save()
        logger.info(
            f"Payment {payment_id} retry initiated. Retry count: {payment.retry_count}/{payment.max_retries}"
        )

        # If this is the final retry and it fails, queue notification
        if payment.retry_count >= payment.max_retries:
            logger.warning(
                f"Payment {payment_id} has reached maximum retries. Final failure notification queued."
            )
            # Queue notification task (to be implemented in notification service)
            # For now, just log it
            payment.metadata["final_failure_notified"] = True
            payment.save()

        return {
            "payment_id": str(payment.id),
            "reference": payment.reference,
            "status": payment.status,
            "retry_count": payment.retry_count,
            "max_retries": payment.max_retries,
            "next_retry_at": payment.next_retry_at,
            "amount": float(payment.amount),
        }

    def initialize_pos_payment(
        self,
        amount: Decimal,
        email: str,
        callback_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Initialize a payment transaction for POS (without invoice).

        This is used when processing payments at point of sale.
        After successful payment, the transaction is marked as completed.

        Args:
            amount: Payment amount
            email: Staff/customer email for payment
            callback_url: URL to redirect to after payment
            metadata: Additional metadata (should contain transaction_id)

        Returns:
            Dictionary with payment_id, authorization_url, access_code, reference

        Raises:
            ValueError: If validation fails
            Exception: If Paystack API call fails
        """
        import uuid
        
        tenant_id = get_tenant_id()
        
        # Convert amount to float if it's a string
        try:
            amount_float = float(amount)
        except (ValueError, TypeError):
            raise ValueError("Amount must be a valid number")
        
        # Validate inputs
        if amount_float <= 0:
            raise ValueError("Amount must be greater than 0")
        
        if not email:
            raise ValueError("Email is required")

        # Prepare metadata
        if metadata is None:
            metadata = {}
        
        metadata.update({
            "payment_type": "pos",
            "created_at": datetime.utcnow().isoformat(),
        })
        
        # Generate unique idempotency key for POS payments
        idempotency_key = str(uuid.uuid4())

        # Call Paystack to initialize transaction
        try:
            paystack_response = self.paystack_service.initialize_transaction(
                amount=float(amount),
                email=email,
                callback_url=callback_url,
                metadata=metadata,
            )
        except Exception as e:
            logger.error(f"Paystack initialization failed: {e}")
            raise Exception(f"Failed to initialize payment: {str(e)}")

        # Extract Paystack response data
        reference = paystack_response.get("reference")
        authorization_url = paystack_response.get("authorization_url")
        access_code = paystack_response.get("access_code")

        if not reference or not authorization_url:
            raise Exception("Invalid Paystack response: missing reference or authorization_url")

        # Create payment record (without customer_id and invoice_id for POS payments)
        try:
            payment = Payment(
                tenant_id=ObjectId(tenant_id) if tenant_id else None,
                amount=amount,
                reference=reference,
                gateway="paystack",
                status="pending",
                idempotency_key=idempotency_key,
                metadata=metadata,
            )
            # Store authorization details in metadata
            payment.metadata["authorization_url"] = authorization_url
            payment.metadata["access_code"] = access_code
            payment.save()
            logger.info(f"POS payment created: {payment.id} with reference {reference}")
        except Exception as e:
            logger.error(f"Error creating payment record: {e}")
            raise Exception(f"Failed to create payment record: {str(e)}")

        return {
            "payment_id": str(payment.id),
            "authorization_url": authorization_url,
            "access_code": access_code,
            "reference": reference,
        }
