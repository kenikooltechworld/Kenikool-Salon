"""Unit tests for invoice model and service."""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from bson import ObjectId
from app.models.invoice import Invoice, InvoiceLineItem
from app.models.appointment import Appointment
from app.models.service import Service
from app.models.customer import Customer
from app.models.staff import Staff
from app.services.invoice_service import InvoiceService


@pytest.fixture
def tenant_id():
    """Create a test tenant ID."""
    return ObjectId()


@pytest.fixture
def customer_id():
    """Create a test customer ID."""
    return ObjectId()


@pytest.fixture
def staff_id():
    """Create a test staff ID."""
    return ObjectId()


@pytest.fixture
def service_id():
    """Create a test service ID."""
    return ObjectId()


@pytest.fixture
def test_service(tenant_id, service_id):
    """Create a test service."""
    service = Service(
        id=service_id,
        tenant_id=tenant_id,
        name="Haircut",
        description="Professional haircut",
        price=Decimal("50.00"),
        duration_minutes=30,
    )
    service.save()
    return service


@pytest.fixture
def test_customer(tenant_id, customer_id):
    """Create a test customer."""
    customer = Customer(
        id=customer_id,
        tenant_id=tenant_id,
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="+234123456789",
    )
    customer.save()
    return customer


@pytest.fixture
def test_appointment(tenant_id, customer_id, staff_id, service_id):
    """Create a test appointment."""
    now = datetime.utcnow()
    appointment = Appointment(
        tenant_id=tenant_id,
        customer_id=customer_id,
        staff_id=staff_id,
        service_id=service_id,
        start_time=now,
        end_time=now + timedelta(minutes=30),
        price=Decimal("50.00"),
        status="completed",
    )
    appointment.save()
    return appointment


class TestInvoiceModel:
    """Tests for Invoice model."""

    def test_create_invoice_model(self, tenant_id, customer_id):
        """Test creating an invoice model."""
        line_item = InvoiceLineItem(
            service_id=ObjectId(),
            service_name="Haircut",
            quantity=Decimal("1"),
            unit_price=Decimal("50.00"),
            total=Decimal("50.00"),
        )

        invoice = Invoice(
            tenant_id=tenant_id,
            customer_id=customer_id,
            line_items=[line_item],
            subtotal=Decimal("50.00"),
            discount=Decimal("0"),
            tax=Decimal("5.00"),
            total=Decimal("55.00"),
            status="draft",
        )
        invoice.save()

        assert invoice.id is not None
        assert invoice.tenant_id == tenant_id
        assert invoice.customer_id == customer_id
        assert len(invoice.line_items) == 1
        assert invoice.total == Decimal("55.00")

    def test_invoice_total_calculation(self, tenant_id, customer_id):
        """Test invoice total calculation: subtotal - discount + tax."""
        line_item = InvoiceLineItem(
            service_id=ObjectId(),
            service_name="Haircut",
            quantity=Decimal("1"),
            unit_price=Decimal("100.00"),
            total=Decimal("100.00"),
        )

        invoice = Invoice(
            tenant_id=tenant_id,
            customer_id=customer_id,
            line_items=[line_item],
            subtotal=Decimal("100.00"),
            discount=Decimal("10.00"),
            tax=Decimal("9.00"),
            total=Decimal("99.00"),  # 100 - 10 + 9
            status="draft",
        )
        invoice.save()

        assert invoice.total == Decimal("99.00")

    def test_invoice_with_multiple_line_items(self, tenant_id, customer_id):
        """Test invoice with multiple line items."""
        line_items = [
            InvoiceLineItem(
                service_id=ObjectId(),
                service_name="Haircut",
                quantity=Decimal("1"),
                unit_price=Decimal("50.00"),
                total=Decimal("50.00"),
            ),
            InvoiceLineItem(
                service_id=ObjectId(),
                service_name="Shampoo",
                quantity=Decimal("1"),
                unit_price=Decimal("20.00"),
                total=Decimal("20.00"),
            ),
        ]

        invoice = Invoice(
            tenant_id=tenant_id,
            customer_id=customer_id,
            line_items=line_items,
            subtotal=Decimal("70.00"),
            discount=Decimal("0"),
            tax=Decimal("7.00"),
            total=Decimal("77.00"),
            status="draft",
        )
        invoice.save()

        assert len(invoice.line_items) == 2
        assert invoice.subtotal == Decimal("70.00")
        assert invoice.total == Decimal("77.00")

    def test_invoice_status_transitions(self, tenant_id, customer_id):
        """Test invoice status transitions."""
        line_item = InvoiceLineItem(
            service_id=ObjectId(),
            service_name="Haircut",
            quantity=Decimal("1"),
            unit_price=Decimal("50.00"),
            total=Decimal("50.00"),
        )

        invoice = Invoice(
            tenant_id=tenant_id,
            customer_id=customer_id,
            line_items=[line_item],
            subtotal=Decimal("50.00"),
            discount=Decimal("0"),
            tax=Decimal("5.00"),
            total=Decimal("55.00"),
            status="draft",
        )
        invoice.save()

        # Transition to issued
        invoice.status = "issued"
        invoice.save()
        assert invoice.status == "issued"

        # Transition to paid
        invoice.status = "paid"
        invoice.paid_at = datetime.utcnow()
        invoice.save()
        assert invoice.status == "paid"
        assert invoice.paid_at is not None


class TestInvoiceService:
    """Tests for InvoiceService."""

    def test_create_invoice(self, tenant_id, customer_id):
        """Test creating an invoice via service."""
        line_items_data = [
            {
                "service_id": str(ObjectId()),
                "service_name": "Haircut",
                "quantity": Decimal("1"),
                "unit_price": Decimal("50.00"),
            }
        ]

        invoice = InvoiceService.create_invoice(
            tenant_id=tenant_id,
            customer_id=customer_id,
            line_items_data=line_items_data,
            discount=Decimal("0"),
            tax=Decimal("5.00"),
        )

        assert invoice.id is not None
        assert invoice.subtotal == Decimal("50.00")
        assert invoice.tax == Decimal("5.00")
        assert invoice.total == Decimal("55.00")
        assert invoice.status == "draft"

    def test_create_invoice_with_discount(self, tenant_id, customer_id):
        """Test creating an invoice with discount."""
        line_items_data = [
            {
                "service_id": str(ObjectId()),
                "service_name": "Haircut",
                "quantity": Decimal("1"),
                "unit_price": Decimal("100.00"),
            }
        ]

        invoice = InvoiceService.create_invoice(
            tenant_id=tenant_id,
            customer_id=customer_id,
            line_items_data=line_items_data,
            discount=Decimal("10.00"),
            tax=Decimal("9.00"),
        )

        assert invoice.subtotal == Decimal("100.00")
        assert invoice.discount == Decimal("10.00")
        assert invoice.tax == Decimal("9.00")
        assert invoice.total == Decimal("99.00")  # 100 - 10 + 9

    def test_create_invoice_with_multiple_items(self, tenant_id, customer_id):
        """Test creating an invoice with multiple line items."""
        line_items_data = [
            {
                "service_id": str(ObjectId()),
                "service_name": "Haircut",
                "quantity": Decimal("1"),
                "unit_price": Decimal("50.00"),
            },
            {
                "service_id": str(ObjectId()),
                "service_name": "Shampoo",
                "quantity": Decimal("2"),
                "unit_price": Decimal("20.00"),
            },
        ]

        invoice = InvoiceService.create_invoice(
            tenant_id=tenant_id,
            customer_id=customer_id,
            line_items_data=line_items_data,
            discount=Decimal("0"),
            tax=Decimal("9.00"),
        )

        assert len(invoice.line_items) == 2
        assert invoice.subtotal == Decimal("90.00")  # 50 + (2 * 20)
        assert invoice.total == Decimal("99.00")  # 90 + 9

    def test_create_invoice_from_appointment(
        self, tenant_id, test_appointment, test_service
    ):
        """Test creating an invoice from an appointment."""
        invoice = InvoiceService.create_invoice_from_appointment(
            tenant_id=tenant_id,
            appointment_id=test_appointment.id,
            discount=Decimal("0"),
            tax=Decimal("5.00"),
        )

        assert invoice.appointment_id == test_appointment.id
        assert invoice.customer_id == test_appointment.customer_id
        assert len(invoice.line_items) == 1
        assert invoice.line_items[0].service_name == "Haircut"
        assert invoice.subtotal == Decimal("50.00")
        assert invoice.total == Decimal("55.00")

    def test_create_invoice_empty_line_items(self, tenant_id, customer_id):
        """Test creating an invoice with empty line items raises error."""
        with pytest.raises(ValueError, match="Invoice must have at least one line item"):
            InvoiceService.create_invoice(
                tenant_id=tenant_id,
                customer_id=customer_id,
                line_items_data=[],
            )

    def test_get_invoice(self, tenant_id, customer_id):
        """Test getting an invoice."""
        line_items_data = [
            {
                "service_id": str(ObjectId()),
                "service_name": "Haircut",
                "quantity": Decimal("1"),
                "unit_price": Decimal("50.00"),
            }
        ]

        created_invoice = InvoiceService.create_invoice(
            tenant_id=tenant_id,
            customer_id=customer_id,
            line_items_data=line_items_data,
        )

        retrieved_invoice = InvoiceService.get_invoice(tenant_id, created_invoice.id)

        assert retrieved_invoice is not None
        assert retrieved_invoice.id == created_invoice.id
        assert retrieved_invoice.customer_id == customer_id

    def test_get_invoice_not_found(self, tenant_id):
        """Test getting a non-existent invoice."""
        invoice = InvoiceService.get_invoice(tenant_id, ObjectId())
        assert invoice is None

    def test_list_invoices(self, tenant_id, customer_id):
        """Test listing invoices."""
        line_items_data = [
            {
                "service_id": str(ObjectId()),
                "service_name": "Haircut",
                "quantity": Decimal("1"),
                "unit_price": Decimal("50.00"),
            }
        ]

        # Create multiple invoices
        for i in range(3):
            InvoiceService.create_invoice(
                tenant_id=tenant_id,
                customer_id=customer_id,
                line_items_data=line_items_data,
            )

        invoices, total = InvoiceService.list_invoices(tenant_id=tenant_id)

        assert len(invoices) == 3
        assert total == 3

    def test_list_invoices_by_customer(self, tenant_id, customer_id):
        """Test listing invoices filtered by customer."""
        line_items_data = [
            {
                "service_id": str(ObjectId()),
                "service_name": "Haircut",
                "quantity": Decimal("1"),
                "unit_price": Decimal("50.00"),
            }
        ]

        other_customer_id = ObjectId()

        # Create invoices for different customers
        InvoiceService.create_invoice(
            tenant_id=tenant_id,
            customer_id=customer_id,
            line_items_data=line_items_data,
        )
        InvoiceService.create_invoice(
            tenant_id=tenant_id,
            customer_id=other_customer_id,
            line_items_data=line_items_data,
        )

        invoices, total = InvoiceService.list_invoices(
            tenant_id=tenant_id,
            customer_id=customer_id,
        )

        assert len(invoices) == 1
        assert total == 1
        assert invoices[0].customer_id == customer_id

    def test_list_invoices_by_status(self, tenant_id, customer_id):
        """Test listing invoices filtered by status."""
        line_items_data = [
            {
                "service_id": str(ObjectId()),
                "service_name": "Haircut",
                "quantity": Decimal("1"),
                "unit_price": Decimal("50.00"),
            }
        ]

        # Create invoices with different statuses
        invoice1 = InvoiceService.create_invoice(
            tenant_id=tenant_id,
            customer_id=customer_id,
            line_items_data=line_items_data,
        )
        invoice1.status = "issued"
        invoice1.save()

        invoice2 = InvoiceService.create_invoice(
            tenant_id=tenant_id,
            customer_id=customer_id,
            line_items_data=line_items_data,
        )
        invoice2.status = "paid"
        invoice2.save()

        invoices, total = InvoiceService.list_invoices(
            tenant_id=tenant_id,
            status="paid",
        )

        assert len(invoices) == 1
        assert total == 1
        assert invoices[0].status == "paid"

    def test_update_invoice(self, tenant_id, customer_id):
        """Test updating an invoice."""
        line_items_data = [
            {
                "service_id": str(ObjectId()),
                "service_name": "Haircut",
                "quantity": Decimal("1"),
                "unit_price": Decimal("50.00"),
            }
        ]

        invoice = InvoiceService.create_invoice(
            tenant_id=tenant_id,
            customer_id=customer_id,
            line_items_data=line_items_data,
        )

        updated_invoice = InvoiceService.update_invoice(
            tenant_id=tenant_id,
            invoice_id=invoice.id,
            status="issued",
            discount=Decimal("5.00"),
            tax=Decimal("4.50"),
        )

        assert updated_invoice.status == "issued"
        assert updated_invoice.discount == Decimal("5.00")
        assert updated_invoice.tax == Decimal("4.50")
        assert updated_invoice.total == Decimal("49.50")  # 50 - 5 + 4.50

    def test_mark_invoice_paid(self, tenant_id, customer_id):
        """Test marking an invoice as paid."""
        line_items_data = [
            {
                "service_id": str(ObjectId()),
                "service_name": "Haircut",
                "quantity": Decimal("1"),
                "unit_price": Decimal("50.00"),
            }
        ]

        invoice = InvoiceService.create_invoice(
            tenant_id=tenant_id,
            customer_id=customer_id,
            line_items_data=line_items_data,
        )

        paid_invoice = InvoiceService.mark_invoice_paid(
            tenant_id=tenant_id,
            invoice_id=invoice.id,
        )

        assert paid_invoice.status == "paid"
        assert paid_invoice.paid_at is not None

    def test_cancel_invoice(self, tenant_id, customer_id):
        """Test cancelling an invoice."""
        line_items_data = [
            {
                "service_id": str(ObjectId()),
                "service_name": "Haircut",
                "quantity": Decimal("1"),
                "unit_price": Decimal("50.00"),
            }
        ]

        invoice = InvoiceService.create_invoice(
            tenant_id=tenant_id,
            customer_id=customer_id,
            line_items_data=line_items_data,
        )

        cancelled_invoice = InvoiceService.cancel_invoice(
            tenant_id=tenant_id,
            invoice_id=invoice.id,
        )

        assert cancelled_invoice.status == "cancelled"

    def test_issue_invoice(self, tenant_id, customer_id):
        """Test issuing an invoice."""
        line_items_data = [
            {
                "service_id": str(ObjectId()),
                "service_name": "Haircut",
                "quantity": Decimal("1"),
                "unit_price": Decimal("50.00"),
            }
        ]

        invoice = InvoiceService.create_invoice(
            tenant_id=tenant_id,
            customer_id=customer_id,
            line_items_data=line_items_data,
        )

        issued_invoice = InvoiceService.issue_invoice(
            tenant_id=tenant_id,
            invoice_id=invoice.id,
        )

        assert issued_invoice.status == "issued"

    def test_issue_invoice_not_draft(self, tenant_id, customer_id):
        """Test issuing an invoice that is not in draft status."""
        line_items_data = [
            {
                "service_id": str(ObjectId()),
                "service_name": "Haircut",
                "quantity": Decimal("1"),
                "unit_price": Decimal("50.00"),
            }
        ]

        invoice = InvoiceService.create_invoice(
            tenant_id=tenant_id,
            customer_id=customer_id,
            line_items_data=line_items_data,
        )
        invoice.status = "issued"
        invoice.save()

        with pytest.raises(ValueError, match="Cannot issue invoice with status"):
            InvoiceService.issue_invoice(
                tenant_id=tenant_id,
                invoice_id=invoice.id,
            )


    def test_list_invoices_pagination(self, tenant_id, customer_id):
        """Test invoice pagination."""
        line_items_data = [
            {
                "service_id": str(ObjectId()),
                "service_name": "Haircut",
                "quantity": Decimal("1"),
                "unit_price": Decimal("50.00"),
            }
        ]

        # Create 25 invoices
        for i in range(25):
            InvoiceService.create_invoice(
                tenant_id=tenant_id,
                customer_id=customer_id,
                line_items_data=line_items_data,
            )

        # Test first page
        invoices_page1, total = InvoiceService.list_invoices(
            tenant_id=tenant_id,
            page=1,
            page_size=10,
        )
        assert len(invoices_page1) == 10
        assert total == 25

        # Test second page
        invoices_page2, total = InvoiceService.list_invoices(
            tenant_id=tenant_id,
            page=2,
            page_size=10,
        )
        assert len(invoices_page2) == 10
        assert total == 25

        # Test third page (partial)
        invoices_page3, total = InvoiceService.list_invoices(
            tenant_id=tenant_id,
            page=3,
            page_size=10,
        )
        assert len(invoices_page3) == 5
        assert total == 25

        # Verify no overlap between pages
        page1_ids = {str(inv.id) for inv in invoices_page1}
        page2_ids = {str(inv.id) for inv in invoices_page2}
        page3_ids = {str(inv.id) for inv in invoices_page3}

        assert len(page1_ids & page2_ids) == 0
        assert len(page2_ids & page3_ids) == 0
        assert len(page1_ids & page3_ids) == 0

    def test_list_invoices_pagination_edge_cases(self, tenant_id, customer_id):
        """Test invoice pagination edge cases."""
        line_items_data = [
            {
                "service_id": str(ObjectId()),
                "service_name": "Haircut",
                "quantity": Decimal("1"),
                "unit_price": Decimal("50.00"),
            }
        ]

        # Create 5 invoices
        for i in range(5):
            InvoiceService.create_invoice(
                tenant_id=tenant_id,
                customer_id=customer_id,
                line_items_data=line_items_data,
            )

        # Test page beyond available data
        invoices, total = InvoiceService.list_invoices(
            tenant_id=tenant_id,
            page=10,
            page_size=10,
        )
        assert len(invoices) == 0
        assert total == 5

        # Test with page_size larger than total
        invoices, total = InvoiceService.list_invoices(
            tenant_id=tenant_id,
            page=1,
            page_size=100,
        )
        assert len(invoices) == 5
        assert total == 5

    def test_list_invoices_sorting_by_date(self, tenant_id, customer_id):
        """Test invoice sorting by creation date."""
        line_items_data = [
            {
                "service_id": str(ObjectId()),
                "service_name": "Haircut",
                "quantity": Decimal("1"),
                "unit_price": Decimal("50.00"),
            }
        ]

        # Create invoices with slight delays to ensure different timestamps
        import time
        invoice_ids = []
        for i in range(3):
            invoice = InvoiceService.create_invoice(
                tenant_id=tenant_id,
                customer_id=customer_id,
                line_items_data=line_items_data,
            )
            invoice_ids.append(invoice.id)
            time.sleep(0.01)  # Small delay to ensure different timestamps

        # List invoices (should be sorted by created_at descending)
        invoices, total = InvoiceService.list_invoices(
            tenant_id=tenant_id,
            page_size=10,
        )

        assert len(invoices) == 3
        # Verify they are sorted by created_at in descending order (newest first)
        for i in range(len(invoices) - 1):
            assert invoices[i].created_at >= invoices[i + 1].created_at

    def test_list_invoices_combined_filters(self, tenant_id, customer_id):
        """Test invoice listing with multiple filters combined."""
        line_items_data = [
            {
                "service_id": str(ObjectId()),
                "service_name": "Haircut",
                "quantity": Decimal("1"),
                "unit_price": Decimal("50.00"),
            }
        ]

        other_customer_id = ObjectId()

        # Create invoices with different statuses and customers
        for i in range(3):
            invoice = InvoiceService.create_invoice(
                tenant_id=tenant_id,
                customer_id=customer_id,
                line_items_data=line_items_data,
            )
            if i == 0:
                invoice.status = "paid"
            elif i == 1:
                invoice.status = "issued"
            else:
                invoice.status = "draft"
            invoice.save()

        # Create invoices for other customer
        for i in range(2):
            invoice = InvoiceService.create_invoice(
                tenant_id=tenant_id,
                customer_id=other_customer_id,
                line_items_data=line_items_data,
            )
            invoice.status = "paid"
            invoice.save()

        # Filter by customer and status
        invoices, total = InvoiceService.list_invoices(
            tenant_id=tenant_id,
            customer_id=customer_id,
            status="paid",
        )

        assert len(invoices) == 1
        assert total == 1
        assert invoices[0].customer_id == customer_id
        assert invoices[0].status == "paid"

    def test_list_invoices_empty_result(self, tenant_id, customer_id):
        """Test listing invoices with no results."""
        # Query with non-existent customer
        non_existent_customer_id = ObjectId()

        invoices, total = InvoiceService.list_invoices(
            tenant_id=tenant_id,
            customer_id=non_existent_customer_id,
        )

        assert len(invoices) == 0
        assert total == 0

    def test_list_invoices_tenant_isolation(self, tenant_id, customer_id):
        """Test that invoices are isolated by tenant."""
        line_items_data = [
            {
                "service_id": str(ObjectId()),
                "service_name": "Haircut",
                "quantity": Decimal("1"),
                "unit_price": Decimal("50.00"),
            }
        ]

        # Create invoice for first tenant
        InvoiceService.create_invoice(
            tenant_id=tenant_id,
            customer_id=customer_id,
            line_items_data=line_items_data,
        )

        # Create invoice for different tenant
        other_tenant_id = ObjectId()
        other_customer_id = ObjectId()
        InvoiceService.create_invoice(
            tenant_id=other_tenant_id,
            customer_id=other_customer_id,
            line_items_data=line_items_data,
        )

        # List invoices for first tenant
        invoices, total = InvoiceService.list_invoices(
            tenant_id=tenant_id,
        )

        assert len(invoices) == 1
        assert total == 1
        assert invoices[0].tenant_id == tenant_id

    def test_list_invoices_status_filter_all_statuses(self, tenant_id, customer_id):
        """Test filtering by each invoice status."""
        line_items_data = [
            {
                "service_id": str(ObjectId()),
                "service_name": "Haircut",
                "quantity": Decimal("1"),
                "unit_price": Decimal("50.00"),
            }
        ]

        statuses = ["draft", "issued", "paid", "cancelled"]

        # Create one invoice for each status
        for status in statuses:
            invoice = InvoiceService.create_invoice(
                tenant_id=tenant_id,
                customer_id=customer_id,
                line_items_data=line_items_data,
            )
            invoice.status = status
            invoice.save()

        # Test filtering by each status
        for status in statuses:
            invoices, total = InvoiceService.list_invoices(
                tenant_id=tenant_id,
                status=status,
            )
            assert len(invoices) == 1
            assert total == 1
            assert invoices[0].status == status
