"""Service for managing POS receipts."""

from datetime import datetime
from typing import List, Optional
from decimal import Decimal
from bson import ObjectId
from mongoengine import Q
from app.models.receipt import Receipt, ReceiptItem
from app.models.transaction import Transaction


class ReceiptService:
    """Service for receipt generation and management."""

    @staticmethod
    def generate_receipt_number(tenant_id: ObjectId) -> str:
        """Generate unique receipt number."""
        count = Receipt.objects(tenant_id=tenant_id).count()
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"RCP-{timestamp}-{count + 1:06d}"

    @staticmethod
    def generate_receipt(
        tenant_id: ObjectId,
        transaction_id: ObjectId,
    ) -> Optional[Receipt]:
        """
        Generate receipt for a transaction.

        Args:
            tenant_id: Tenant ID
            transaction_id: Transaction ID

        Returns:
            Generated Receipt document or None if transaction not found
        """
        print(f"[ReceiptService] Generating receipt for transaction {transaction_id}")
        transaction = Transaction.objects(
            tenant_id=tenant_id,
            id=transaction_id
        ).first()

        if not transaction:
            print(f"[ReceiptService] Transaction not found: {transaction_id}")
            return None

        print(f"[ReceiptService] Found transaction, creating receipt items")
        # Create receipt items from transaction items
        receipt_items = []
        for item in transaction.items:
            receipt_item = ReceiptItem(
                item_type=item.item_type,
                item_id=item.item_id,
                item_name=item.item_name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                line_total=item.line_total,
                tax_amount=item.tax_amount,
                discount_amount=item.discount_amount,
            )
            receipt_items.append(receipt_item)

        # Create receipt
        receipt = Receipt(
            tenant_id=tenant_id,
            transaction_id=transaction_id,
            customer_id=transaction.customer_id,
            receipt_number=ReceiptService.generate_receipt_number(tenant_id),
            receipt_date=datetime.utcnow(),
            customer_name=ReceiptService._get_customer_name(tenant_id, transaction.customer_id),
            customer_email=ReceiptService._get_customer_email(tenant_id, transaction.customer_id),
            customer_phone=ReceiptService._get_customer_phone(tenant_id, transaction.customer_id),
            items=receipt_items,
            subtotal=transaction.subtotal,
            tax_amount=transaction.tax_amount,
            discount_amount=transaction.discount_amount,
            total=transaction.total,
            payment_method=transaction.payment_method,
            payment_reference=transaction.paystack_reference,
            receipt_format="thermal",
        )
        receipt.save()
        print(f"[ReceiptService] Receipt created: {receipt.id}")
        return receipt

    @staticmethod
    def get_receipt(
        tenant_id: ObjectId,
        receipt_id: ObjectId,
    ) -> Optional[Receipt]:
        """
        Get a receipt by ID.

        Args:
            tenant_id: Tenant ID
            receipt_id: Receipt ID

        Returns:
            Receipt document or None if not found
        """
        return Receipt.objects(
            tenant_id=tenant_id,
            id=receipt_id
        ).first()

    @staticmethod
    def get_receipt_by_transaction(
        tenant_id: ObjectId,
        transaction_id: ObjectId,
    ) -> Optional[Receipt]:
        """
        Get receipt for a transaction.

        Args:
            tenant_id: Tenant ID
            transaction_id: Transaction ID

        Returns:
            Receipt document or None if not found
        """
        return Receipt.objects(
            tenant_id=tenant_id,
            transaction_id=transaction_id
        ).first()

    @staticmethod
    def list_receipts(
        tenant_id: ObjectId,
        customer_id: Optional[ObjectId] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[Receipt], int]:
        """
        List receipts with optional filtering.

        Args:
            tenant_id: Tenant ID
            customer_id: Optional customer ID filter
            page: Page number (1-indexed)
            page_size: Number of items per page

        Returns:
            Tuple of (receipts list, total count)
        """
        query = Q(tenant_id=tenant_id)

        if customer_id:
            query &= Q(customer_id=customer_id)

        total = Receipt.objects(query).count()

        skip = (page - 1) * page_size
        receipts = Receipt.objects(query).skip(skip).limit(page_size).order_by("-receipt_date")

        return list(receipts), total

    @staticmethod
    def mark_receipt_printed(
        tenant_id: ObjectId,
        receipt_id: ObjectId,
    ) -> Optional[Receipt]:
        """
        Mark receipt as printed.

        Args:
            tenant_id: Tenant ID
            receipt_id: Receipt ID

        Returns:
            Updated Receipt document or None if not found
        """
        receipt = Receipt.objects(
            tenant_id=tenant_id,
            id=receipt_id
        ).first()

        if not receipt:
            return None

        receipt.printed_at = datetime.utcnow()
        receipt.save()
        return receipt

    @staticmethod
    def mark_receipt_emailed(
        tenant_id: ObjectId,
        receipt_id: ObjectId,
    ) -> Optional[Receipt]:
        """
        Mark receipt as emailed.

        Args:
            tenant_id: Tenant ID
            receipt_id: Receipt ID

        Returns:
            Updated Receipt document or None if not found
        """
        receipt = Receipt.objects(
            tenant_id=tenant_id,
            id=receipt_id
        ).first()

        if not receipt:
            return None

        receipt.emailed_at = datetime.utcnow()
        receipt.save()
        return receipt

    @staticmethod
    def _get_customer_name(tenant_id: ObjectId, customer_id: ObjectId) -> str:
        """Get customer name."""
        from app.models.customer import Customer
        customer = Customer.objects(tenant_id=tenant_id, id=customer_id).first()
        return f"{customer.first_name} {customer.last_name}" if customer else "Guest"

    @staticmethod
    def _get_customer_email(tenant_id: ObjectId, customer_id: ObjectId) -> Optional[str]:
        """Get customer email."""
        from app.models.customer import Customer
        customer = Customer.objects(tenant_id=tenant_id, id=customer_id).first()
        return customer.email if customer else None

    @staticmethod
    def _get_customer_phone(tenant_id: ObjectId, customer_id: ObjectId) -> Optional[str]:
        """Get customer phone."""
        from app.models.customer import Customer
        customer = Customer.objects(tenant_id=tenant_id, id=customer_id).first()
        return customer.phone if customer else None
