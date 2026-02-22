"""Refund service for managing refund operations."""

import logging
from decimal import Decimal
from typing import Dict, Any, Optional
from bson import ObjectId
from app.models.refund import Refund
from app.models.payment import Payment
from app.services.paystack_service import PaystackService
from app.context import get_tenant_id

logger = logging.getLogger(__name__)


class RefundService:
    """Service for managing refund operations."""

    def __init__(self):
        """Initialize refund service."""
        self.paystack_service = PaystackService()

    def create_refund(
        self,
        payment_id: str,
        amount: Decimal,
        reason: str,
    ) -> Dict[str, Any]:
        """
        Create a refund for a payment.

        Validates that:
        1. Payment exists and is in success status
        2. Refund amount does not exceed original payment amount
        3. No duplicate refund for same payment

        Args:
            payment_id: Payment ID to refund
            amount: Refund amount
            reason: Reason for refund

        Returns:
            Dictionary with refund details

        Raises:
            ValueError: If validation fails
        """
        tenant_id = get_tenant_id()
        if not tenant_id:
            raise ValueError("Tenant context not found")

        # Validate payment exists and is in success status
        payment = Payment.objects(
            tenant_id=ObjectId(tenant_id),
            id=ObjectId(payment_id)
        ).first()

        if not payment:
            raise ValueError(f"Payment {payment_id} not found")

        if payment.status != "success":
            raise ValueError(f"Payment must be in success status, current status: {payment.status}")

        # Validate refund amount does not exceed original payment amount
        if amount > payment.amount:
            raise ValueError(
                f"Refund amount {amount} exceeds original payment amount {payment.amount}"
            )

        if amount <= 0:
            raise ValueError("Refund amount must be greater than 0")

        # Check for existing refund for this payment
        existing_refund = Refund.objects(
            tenant_id=ObjectId(tenant_id),
            payment_id=ObjectId(payment_id),
            status__in=["pending", "success"]
        ).first()

        if existing_refund:
            raise ValueError(f"Refund already exists for payment {payment_id}")

        # Call Paystack to process refund
        logger.info(f"Processing refund for payment {payment_id}: amount={amount}, reason={reason}")

        try:
            paystack_response = self.paystack_service.refund_transaction(
                reference=payment.reference,
                amount=int(amount * 100),  # Convert to kobo
            )

            # Create refund record with pending status
            refund = Refund(
                tenant_id=ObjectId(tenant_id),
                payment_id=ObjectId(payment_id),
                amount=amount,
                reason=reason,
                status="pending",
                reference=paystack_response.get("reference", ""),
                metadata={
                    "paystack_response": paystack_response,
                }
            )
            refund.save()

            logger.info(f"Refund {refund.id} created with status pending")

            return {
                "refund_id": str(refund.id),
                "payment_id": str(payment.id),
                "amount": refund.amount,
                "reason": refund.reason,
                "status": refund.status,
                "reference": refund.reference,
                "created_at": refund.created_at,
                "updated_at": refund.updated_at,
            }

        except Exception as e:
            logger.error(f"Error processing refund with Paystack: {e}")
            raise ValueError(f"Failed to process refund: {str(e)}")

    def get_refund(self, refund_id: str) -> Optional[Refund]:
        """
        Get a refund by ID.

        Args:
            refund_id: Refund ID

        Returns:
            Refund object or None if not found
        """
        tenant_id = get_tenant_id()
        if not tenant_id:
            return None

        return Refund.objects(
            tenant_id=ObjectId(tenant_id),
            id=ObjectId(refund_id)
        ).first()

    def get_refund_by_reference(self, reference: str) -> Optional[Refund]:
        """
        Get a refund by Paystack reference.

        Args:
            reference: Paystack refund reference

        Returns:
            Refund object or None if not found
        """
        tenant_id = get_tenant_id()
        if not tenant_id:
            return None

        return Refund.objects(
            tenant_id=ObjectId(tenant_id),
            reference=reference
        ).first()

    def update_refund_status(
        self,
        refund_id: str,
        status: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update refund status.

        Args:
            refund_id: Refund ID
            status: New status (pending, success, failed)
            metadata: Additional metadata to update

        Returns:
            Dictionary with updated refund details

        Raises:
            ValueError: If refund not found or invalid status
        """
        tenant_id = get_tenant_id()
        if not tenant_id:
            raise ValueError("Tenant context not found")

        if status not in ["pending", "success", "failed"]:
            raise ValueError(f"Invalid status: {status}")

        refund = Refund.objects(
            tenant_id=ObjectId(tenant_id),
            id=ObjectId(refund_id)
        ).first()

        if not refund:
            raise ValueError(f"Refund {refund_id} not found")

        refund.status = status
        if metadata:
            refund.metadata.update(metadata)
        refund.save()

        logger.info(f"Refund {refund_id} status updated to {status}")

        return {
            "refund_id": str(refund.id),
            "payment_id": str(refund.payment_id),
            "amount": refund.amount,
            "reason": refund.reason,
            "status": refund.status,
            "reference": refund.reference,
            "created_at": refund.created_at,
            "updated_at": refund.updated_at,
        }

    def list_refunds(
        self,
        payment_id: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        List refunds with optional filtering.

        Args:
            payment_id: Filter by payment ID
            status: Filter by status
            skip: Number of records to skip
            limit: Number of records to return

        Returns:
            Dictionary with total count and list of refunds
        """
        tenant_id = get_tenant_id()
        if not tenant_id:
            return {"total": 0, "refunds": []}

        query = {"tenant_id": ObjectId(tenant_id)}

        if payment_id:
            query["payment_id"] = ObjectId(payment_id)

        if status:
            query["status"] = status

        total = Refund.objects(**query).count()
        refunds = Refund.objects(**query).skip(skip).limit(limit).order_by("-created_at")

        return {
            "total": total,
            "refunds": list(refunds),
        }
