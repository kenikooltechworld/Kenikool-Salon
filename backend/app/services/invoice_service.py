"""Service for managing invoices."""

from datetime import datetime, timedelta
from typing import List, Optional
from decimal import Decimal
from bson import ObjectId
from mongoengine import Q
from app.models.invoice import Invoice, InvoiceLineItem
from app.models.appointment import Appointment
from app.models.service import Service


class InvoiceService:
    """Service for invoice management and generation."""

    @staticmethod
    def create_invoice(
        tenant_id: ObjectId,
        customer_id: ObjectId,
        line_items_data: List[dict],
        discount: Decimal = Decimal("0"),
        tax: Decimal = Decimal("0"),
        appointment_id: Optional[ObjectId] = None,
        notes: Optional[str] = None,
    ) -> Invoice:
        """
        Create a new invoice.

        Args:
            tenant_id: Tenant ID
            customer_id: Customer ID
            line_items_data: List of line item dictionaries with service_id, service_name, quantity, unit_price
            discount: Discount amount (default 0)
            tax: Tax amount (default 0)
            appointment_id: Optional appointment ID
            notes: Optional invoice notes

        Returns:
            Created Invoice document

        Raises:
            ValueError: If line items are invalid or empty
        """
        if not line_items_data:
            raise ValueError("Invoice must have at least one line item")

        # Create line items and calculate subtotal
        line_items = []
        subtotal = Decimal("0")

        for item_data in line_items_data:
            quantity = Decimal(str(item_data.get("quantity", 1)))
            unit_price = Decimal(str(item_data.get("unit_price", 0)))
            total = quantity * unit_price

            line_item = InvoiceLineItem(
                service_id=ObjectId(item_data["service_id"]),
                service_name=item_data["service_name"],
                quantity=quantity,
                unit_price=unit_price,
                total=total,
            )
            line_items.append(line_item)
            subtotal += total

        # Calculate total: subtotal - discount + tax
        discount = Decimal(str(discount))
        tax = Decimal(str(tax))
        total = subtotal - discount + tax

        # Ensure total is not negative
        if total < 0:
            total = Decimal("0")

        # Create invoice
        invoice = Invoice(
            tenant_id=tenant_id,
            customer_id=customer_id,
            appointment_id=appointment_id,
            line_items=line_items,
            subtotal=subtotal,
            discount=discount,
            tax=tax,
            total=total,
            status="draft",
            notes=notes,
            due_date=datetime.utcnow() + timedelta(days=30),
        )
        invoice.save()
        return invoice

    @staticmethod
    def create_invoice_from_appointment(
        tenant_id: ObjectId,
        appointment_id: ObjectId,
        discount: Decimal = Decimal("0"),
        tax: Decimal = Decimal("0"),
    ) -> Invoice:
        """
        Create an invoice from a completed appointment.

        Args:
            tenant_id: Tenant ID
            appointment_id: Appointment ID
            discount: Discount amount (default 0)
            tax: Tax amount (default 0)

        Returns:
            Created Invoice document

        Raises:
            ValueError: If appointment not found or invalid
        """
        # Get appointment
        appointment = Appointment.objects(
            tenant_id=tenant_id,
            id=appointment_id
        ).first()

        if not appointment:
            raise ValueError(f"Appointment {appointment_id} not found")

        # Get service details
        service = Service.objects(
            tenant_id=tenant_id,
            id=appointment.service_id
        ).first()

        if not service:
            raise ValueError(f"Service {appointment.service_id} not found")

        # Create line item from appointment
        line_items_data = [
            {
                "service_id": str(appointment.service_id),
                "service_name": service.name,
                "quantity": 1,
                "unit_price": appointment.price or service.price,
            }
        ]

        # Create invoice
        return InvoiceService.create_invoice(
            tenant_id=tenant_id,
            customer_id=appointment.customer_id,
            line_items_data=line_items_data,
            discount=discount,
            tax=tax,
            appointment_id=appointment_id,
        )

    @staticmethod
    def get_invoice(
        tenant_id: ObjectId,
        invoice_id: ObjectId,
    ) -> Optional[Invoice]:
        """
        Get an invoice by ID.

        Args:
            tenant_id: Tenant ID
            invoice_id: Invoice ID

        Returns:
            Invoice document or None if not found
        """
        return Invoice.objects(
            tenant_id=tenant_id,
            id=invoice_id
        ).first()

    @staticmethod
    def list_invoices(
        tenant_id: ObjectId,
        customer_id: Optional[ObjectId] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[Invoice], int]:
        """
        List invoices with optional filtering.

        Args:
            tenant_id: Tenant ID
            customer_id: Optional customer ID filter
            status: Optional status filter
            page: Page number (1-indexed)
            page_size: Number of items per page

        Returns:
            Tuple of (invoices list, total count)
        """
        query = Q(tenant_id=tenant_id)

        if customer_id:
            query &= Q(customer_id=customer_id)

        if status:
            query &= Q(status=status)

        total = Invoice.objects(query).count()

        skip = (page - 1) * page_size
        invoices = Invoice.objects(query).skip(skip).limit(page_size).order_by("-created_at")

        return list(invoices), total

    @staticmethod
    def update_invoice(
        tenant_id: ObjectId,
        invoice_id: ObjectId,
        status: Optional[str] = None,
        discount: Optional[Decimal] = None,
        tax: Optional[Decimal] = None,
        notes: Optional[str] = None,
    ) -> Optional[Invoice]:
        """
        Update an invoice.

        Args:
            tenant_id: Tenant ID
            invoice_id: Invoice ID
            status: Optional new status
            discount: Optional new discount
            tax: Optional new tax
            notes: Optional new notes

        Returns:
            Updated Invoice document or None if not found
        """
        invoice = Invoice.objects(
            tenant_id=tenant_id,
            id=invoice_id
        ).first()

        if not invoice:
            return None

        if status:
            invoice.status = status

        if discount is not None:
            invoice.discount = Decimal(str(discount))
            # Recalculate total
            invoice.total = invoice.subtotal - invoice.discount + invoice.tax

        if tax is not None:
            invoice.tax = Decimal(str(tax))
            # Recalculate total
            invoice.total = invoice.subtotal - invoice.discount + invoice.tax

        if notes is not None:
            invoice.notes = notes

        invoice.save()
        return invoice

    @staticmethod
    def mark_invoice_paid(
        tenant_id: ObjectId,
        invoice_id: ObjectId,
        paid_at: Optional[datetime] = None,
    ) -> Optional[Invoice]:
        """
        Mark an invoice as paid.

        Args:
            tenant_id: Tenant ID
            invoice_id: Invoice ID
            paid_at: Optional payment date (defaults to now)

        Returns:
            Updated Invoice document or None if not found
        """
        invoice = Invoice.objects(
            tenant_id=tenant_id,
            id=invoice_id
        ).first()

        if not invoice:
            return None

        invoice.status = "paid"
        invoice.paid_at = paid_at or datetime.utcnow()
        invoice.save()
        return invoice

    @staticmethod
    def cancel_invoice(
        tenant_id: ObjectId,
        invoice_id: ObjectId,
    ) -> Optional[Invoice]:
        """
        Cancel an invoice.

        Args:
            tenant_id: Tenant ID
            invoice_id: Invoice ID

        Returns:
            Updated Invoice document or None if not found
        """
        invoice = Invoice.objects(
            tenant_id=tenant_id,
            id=invoice_id
        ).first()

        if not invoice:
            return None

        invoice.status = "cancelled"
        invoice.save()
        return invoice

    @staticmethod
    def issue_invoice(
        tenant_id: ObjectId,
        invoice_id: ObjectId,
    ) -> Optional[Invoice]:
        """
        Issue an invoice (change status from draft to issued).

        Args:
            tenant_id: Tenant ID
            invoice_id: Invoice ID

        Returns:
            Updated Invoice document or None if not found
        """
        invoice = Invoice.objects(
            tenant_id=tenant_id,
            id=invoice_id
        ).first()

        if not invoice:
            return None

        if invoice.status != "draft":
            raise ValueError(f"Cannot issue invoice with status {invoice.status}")

        invoice.status = "issued"
        invoice.save()
        return invoice

    @staticmethod
    def auto_initialize_payment_for_invoice(
        tenant_id: ObjectId,
        invoice: Invoice,
        customer_email: str,
    ) -> Optional[dict]:
        """
        Auto-initialize payment when invoice is issued.
        
        Args:
            tenant_id: Tenant ID
            invoice: Invoice document
            customer_email: Customer email for payment link
            
        Returns:
            Payment initialization response or None if failed
        """
        from app.services.payment_service import PaymentService
        import logging
        
        logger = logging.getLogger(__name__)
        
        try:
            if not customer_email:
                logger.warning(f"Cannot auto-initialize payment: customer email not provided")
                return None
            
            payment_service = PaymentService()
            payment_response = payment_service.initialize_payment(
                amount=float(invoice.total),
                customer_id=str(invoice.customer_id),
                email=customer_email,
                metadata={
                    "invoice_id": str(invoice.id),
                    "appointment_id": str(invoice.appointment_id) if invoice.appointment_id else None,
                    "payment_type": "invoice",
                }
            )
            
            logger.info(f"Auto-initialized payment for invoice {invoice.id}")
            return payment_response
            
        except Exception as e:
            logger.error(f"Failed to auto-initialize payment for invoice {invoice.id}: {e}")
            return None
