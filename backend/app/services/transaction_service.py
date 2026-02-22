"""Service for managing POS transactions."""

from datetime import datetime
from typing import List, Optional
from decimal import Decimal
from bson import ObjectId
from mongoengine import Q
from app.models.transaction import Transaction, TransactionItem
from app.models.customer import Customer
from app.models.staff import Staff
from app.services.inventory_deduction_service import InventoryDeductionService
from app.services.discount_service import DiscountService
from app.services.commission_service import CommissionService


class TransactionService:
    """Service for transaction management."""

    @staticmethod
    def generate_reference_number(tenant_id: ObjectId) -> str:
        """Generate unique transaction reference number."""
        count = Transaction.objects(tenant_id=tenant_id).count()
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"TXN-{timestamp}-{count + 1:06d}"

    @staticmethod
    def create_transaction(
        tenant_id: ObjectId,
        customer_id: ObjectId,
        staff_id: ObjectId,
        items_data: List[dict],
        payment_method: str,
        transaction_type: str = "service",
        appointment_id: Optional[ObjectId] = None,
        discount_amount: Decimal = Decimal("0"),
        discount_code: Optional[str] = None,
        notes: Optional[str] = None,
        commission_rate: Optional[Decimal] = None,
        commission_type: str = "percentage",
    ) -> Transaction:
        """
        Create a new transaction with inventory deduction, discount application, and commission calculation.

        Args:
            tenant_id: Tenant ID
            customer_id: Customer ID
            staff_id: Staff ID
            items_data: List of item dictionaries
            payment_method: Payment method
            transaction_type: Transaction type (default: service)
            appointment_id: Optional appointment ID
            discount_amount: Discount amount (default: 0)
            discount_code: Optional discount code to apply
            notes: Optional notes
            commission_rate: Optional commission rate
            commission_type: Commission type (percentage or fixed)

        Returns:
            Created Transaction document

        Raises:
            ValueError: If items are invalid or empty
        """
        if not items_data:
            raise ValueError("Transaction must have at least one item")

        # Create transaction items and calculate totals
        items = []
        subtotal = Decimal("0")
        total_tax = Decimal("0")

        for item_data in items_data:
            quantity = int(item_data.get("quantity", 1))
            unit_price = Decimal(str(item_data.get("unit_price", 0)))
            line_total = quantity * unit_price
            tax_rate = Decimal(str(item_data.get("tax_rate", 0)))
            tax_amount = (line_total * tax_rate) / Decimal("100")
            discount_rate = Decimal(str(item_data.get("discount_rate", 0)))
            discount_item = (line_total * discount_rate) / Decimal("100")

            item = TransactionItem(
                item_type=item_data["item_type"],
                item_id=ObjectId(item_data["item_id"]),
                item_name=item_data["item_name"],
                quantity=quantity,
                unit_price=unit_price,
                line_total=line_total,
                tax_rate=tax_rate,
                tax_amount=tax_amount,
                discount_rate=discount_rate,
                discount_amount=discount_item,
            )
            items.append(item)
            subtotal += line_total
            total_tax += tax_amount

        # Check inventory availability before creating transaction
        for item in items:
            if item.item_type == "product":
                if not InventoryDeductionService.check_inventory_availability(
                    tenant_id, item.item_id, item.quantity
                ):
                    raise ValueError(
                        f"Insufficient inventory for product {item.item_name}"
                    )

        # Apply discount code if provided
        if discount_code:
            is_valid, code_discount, message = DiscountService.apply_discount(
                tenant_id, discount_code, subtotal
            )
            if is_valid:
                discount_amount = code_discount
            else:
                raise ValueError(f"Invalid discount code: {message}")

        # Calculate total
        discount_amount = Decimal(str(discount_amount))
        total = subtotal - discount_amount + total_tax

        # Ensure total is not negative
        if total < 0:
            total = Decimal("0")

        # Link to invoice if appointment has one
        invoice_id = None
        if appointment_id:
            from app.models.invoice import Invoice
            invoice = Invoice.objects(
                tenant_id=tenant_id,
                appointment_id=appointment_id
            ).first()
            if invoice:
                invoice_id = invoice.id

        # Create transaction
        transaction = Transaction(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=staff_id,
            appointment_id=appointment_id,
            invoice_id=invoice_id,
            transaction_type=transaction_type,
            items=items,
            subtotal=subtotal,
            tax_amount=total_tax,
            discount_amount=discount_amount,
            total=total,
            payment_method=payment_method,
            payment_status="pending",
            reference_number=TransactionService.generate_reference_number(tenant_id),
            notes=notes,
        )
        transaction.save()

        # Deduct inventory for product items
        try:
            InventoryDeductionService.deduct_inventory(tenant_id, transaction.id, items)
        except Exception as e:
            # If inventory deduction fails, delete transaction and raise error
            transaction.delete()
            raise ValueError(f"Failed to deduct inventory: {str(e)}")

        # Calculate and record commission
        if commission_rate is None:
            # Get commission rate from staff member
            staff = Staff.objects(tenant_id=tenant_id, id=staff_id).first()
            if staff:
                commission_rate = getattr(staff, "commission_rate", Decimal("0"))
                commission_type = getattr(staff, "commission_type", "percentage")
            else:
                commission_rate = Decimal("0")

        if commission_rate and commission_rate > 0:
            try:
                CommissionService.calculate_commission(
                    tenant_id=tenant_id,
                    transaction_id=transaction.id,
                    staff_id=staff_id,
                    commission_rate=commission_rate,
                    commission_type=commission_type,
                )
            except Exception as e:
                # Log commission calculation error but don't fail transaction
                print(f"Warning: Failed to calculate commission: {str(e)}")

        return transaction

    @staticmethod
    @staticmethod
    def get_transaction(
        tenant_id: ObjectId,
        transaction_id: ObjectId,
    ) -> Optional[Transaction]:
        """
        Get a transaction by ID.

        Args:
            tenant_id: Tenant ID
            transaction_id: Transaction ID

        Returns:
            Transaction document or None if not found
        """
        return Transaction.objects(
            tenant_id=tenant_id,
            id=transaction_id
        ).first()

    @staticmethod
    def list_transactions(
        tenant_id: ObjectId,
        customer_id: Optional[ObjectId] = None,
        staff_id: Optional[ObjectId] = None,
        payment_status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[Transaction], int]:
        """
        List transactions with optional filtering.

        Args:
            tenant_id: Tenant ID
            customer_id: Optional customer ID filter
            staff_id: Optional staff ID filter
            payment_status: Optional payment status filter
            page: Page number (1-indexed)
            page_size: Number of items per page

        Returns:
            Tuple of (transactions list, total count)
        """
        query = Q(tenant_id=tenant_id)

        if customer_id:
            query &= Q(customer_id=customer_id)

        if staff_id:
            query &= Q(staff_id=staff_id)

        if payment_status:
            query &= Q(payment_status=payment_status)

        total = Transaction.objects(query).count()

        skip = (page - 1) * page_size
        transactions = Transaction.objects(query).skip(skip).limit(page_size).order_by("-created_at")

        return list(transactions), total

    @staticmethod
    def update_transaction_status(
        tenant_id: ObjectId,
        transaction_id: ObjectId,
        payment_status: str,
        paystack_reference: Optional[str] = None,
    ) -> Optional[Transaction]:
        """
        Update transaction payment status.

        Args:
            tenant_id: Tenant ID
            transaction_id: Transaction ID
            payment_status: New payment status
            paystack_reference: Optional Paystack reference

        Returns:
            Updated Transaction document or None if not found
        """
        transaction = Transaction.objects(
            tenant_id=tenant_id,
            id=transaction_id
        ).first()

        if not transaction:
            return None

        transaction.payment_status = payment_status
        if paystack_reference:
            transaction.paystack_reference = paystack_reference
        transaction.save()
        return transaction

    @staticmethod
    def cancel_transaction(
        tenant_id: ObjectId,
        transaction_id: ObjectId,
    ) -> Optional[Transaction]:
        """
        Cancel a transaction and restore inventory.

        Args:
            tenant_id: Tenant ID
            transaction_id: Transaction ID

        Returns:
            Updated Transaction document or None if not found

        Raises:
            ValueError: If transaction cannot be cancelled
        """
        transaction = Transaction.objects(
            tenant_id=tenant_id,
            id=transaction_id
        ).first()

        if not transaction:
            return None

        if transaction.payment_status == "completed":
            raise ValueError("Cannot cancel a completed transaction")

        # Restore inventory
        try:
            InventoryDeductionService.restore_inventory(tenant_id, transaction_id)
        except Exception as e:
            raise ValueError(f"Failed to restore inventory: {str(e)}")

        # Update transaction status
        transaction.payment_status = "cancelled"
        transaction.save()

        return transaction

    @staticmethod
    @staticmethod
    def validate_transaction_data(data: dict) -> bool:
        """
        Validate transaction data.

        Args:
            data: Transaction data dictionary

        Returns:
            True if valid, raises ValueError otherwise
        """
        if not data.get("items"):
            raise ValueError("Transaction must have at least one item")

        if not data.get("payment_method"):
            raise ValueError("Payment method is required")

        if not data.get("customer_id"):
            raise ValueError("Customer ID is required")

        if not data.get("staff_id"):
            raise ValueError("Staff ID is required")

        return True

    @staticmethod
    @staticmethod
    def calculate_totals(
        items_data: List[dict],
        discount_amount: Decimal = Decimal("0"),
        tax_rate: Decimal = Decimal("0"),
    ) -> dict:
        """
        Calculate transaction totals.

        Args:
            items_data: List of item dictionaries
            discount_amount: Discount amount
            tax_rate: Tax rate percentage

        Returns:
            Dictionary with subtotal, tax_amount, discount_amount, total
        """
        subtotal = Decimal("0")

        for item_data in items_data:
            quantity = int(item_data.get("quantity", 1))
            unit_price = Decimal(str(item_data.get("unit_price", 0)))
            subtotal += quantity * unit_price

        # Apply discount
        discount_amount = Decimal(str(discount_amount))
        discounted_subtotal = subtotal - discount_amount

        # Calculate tax on discounted amount
        tax_amount = (discounted_subtotal * Decimal(str(tax_rate))) / Decimal("100")

        # Calculate total
        total = discounted_subtotal + tax_amount

        return {
            "subtotal": subtotal,
            "tax_amount": tax_amount,
            "discount_amount": discount_amount,
            "total": total,
        }
