"""Routes for invoice management."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from bson import ObjectId
from decimal import Decimal
from app.schemas.invoice import (
    InvoiceCreateRequest,
    InvoiceUpdateRequest,
    InvoiceMarkPaidRequest,
    InvoiceResponse,
    InvoiceListResponse,
)
from app.services.invoice_service import InvoiceService
from app.middleware.tenant_context import get_tenant_id


router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.post("", response_model=InvoiceResponse)
async def create_invoice(
    request: InvoiceCreateRequest,
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """
    Create a new invoice.

    - **customer_id**: Customer ID
    - **line_items**: List of line items with service_id, service_name, quantity, unit_price
    - **discount**: Discount amount (optional)
    - **tax**: Tax amount (optional)
    - **appointment_id**: Appointment ID (optional)
    - **notes**: Invoice notes (optional)
    """
    try:
        customer_id = ObjectId(request.customer_id)
        appointment_id = ObjectId(request.appointment_id) if request.appointment_id else None

        # Convert line items to dict format
        line_items_data = [
            {
                "service_id": item.service_id,
                "service_name": item.service_name,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
            }
            for item in request.line_items
        ]

        invoice = InvoiceService.create_invoice(
            tenant_id=tenant_id,
            customer_id=customer_id,
            line_items_data=line_items_data,
            discount=request.discount,
            tax=request.tax,
            appointment_id=appointment_id,
            notes=request.notes,
        )

        return _invoice_to_response(invoice)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/from-appointment/{appointment_id}", response_model=InvoiceResponse)
async def create_invoice_from_appointment(
    appointment_id: str,
    discount: Decimal = Query(default=Decimal("0"), ge=0),
    tax: Decimal = Query(default=Decimal("0"), ge=0),
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """
    Create an invoice from a completed appointment.

    - **appointment_id**: Appointment ID
    - **discount**: Discount amount (optional)
    - **tax**: Tax amount (optional)
    """
    try:
        appt_id = ObjectId(appointment_id)
        invoice = InvoiceService.create_invoice_from_appointment(
            tenant_id=tenant_id,
            appointment_id=appt_id,
            discount=discount,
            tax=tax,
        )
        return _invoice_to_response(invoice)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """Get an invoice by ID."""
    try:
        inv_id = ObjectId(invoice_id)
        invoice = InvoiceService.get_invoice(tenant_id, inv_id)

        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")

        return _invoice_to_response(invoice)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=InvoiceListResponse)
async def list_invoices(
    customer_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """
    List invoices with optional filtering.

    - **customer_id**: Filter by customer ID (optional)
    - **status**: Filter by status (optional)
    - **page**: Page number (default 1)
    - **page_size**: Items per page (default 20, max 100)
    """
    try:
        cust_id = ObjectId(customer_id) if customer_id else None
        invoices, total = InvoiceService.list_invoices(
            tenant_id=tenant_id,
            customer_id=cust_id,
            status=status,
            page=page,
            page_size=page_size,
        )

        return InvoiceListResponse(
            invoices=[_invoice_to_response(inv) for inv in invoices],
            total=total,
            page=page,
            page_size=page_size,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: str,
    request: InvoiceUpdateRequest,
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """
    Update an invoice.

    - **invoice_id**: Invoice ID
    - **status**: New status (optional)
    - **discount**: New discount amount (optional)
    - **tax**: New tax amount (optional)
    - **notes**: New notes (optional)
    """
    try:
        inv_id = ObjectId(invoice_id)
        invoice = InvoiceService.update_invoice(
            tenant_id=tenant_id,
            invoice_id=inv_id,
            status=request.status,
            discount=request.discount,
            tax=request.tax,
            notes=request.notes,
        )

        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")

        return _invoice_to_response(invoice)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{invoice_id}/mark-paid", response_model=InvoiceResponse)
async def mark_invoice_paid(
    invoice_id: str,
    request: InvoiceMarkPaidRequest,
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """
    Mark an invoice as paid.

    - **invoice_id**: Invoice ID
    - **paid_at**: Payment date (optional, defaults to now)
    """
    try:
        inv_id = ObjectId(invoice_id)
        invoice = InvoiceService.mark_invoice_paid(
            tenant_id=tenant_id,
            invoice_id=inv_id,
            paid_at=request.paid_at,
        )

        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")

        return _invoice_to_response(invoice)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{invoice_id}/cancel", response_model=InvoiceResponse)
async def cancel_invoice(
    invoice_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """Cancel an invoice."""
    try:
        inv_id = ObjectId(invoice_id)
        invoice = InvoiceService.cancel_invoice(tenant_id, inv_id)

        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")

        return _invoice_to_response(invoice)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{invoice_id}/issue", response_model=InvoiceResponse)
async def issue_invoice(
    invoice_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """Issue an invoice (change status from draft to issued)."""
    try:
        inv_id = ObjectId(invoice_id)
        invoice = InvoiceService.issue_invoice(tenant_id, inv_id)

        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")

        return _invoice_to_response(invoice)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def _invoice_to_response(invoice) -> InvoiceResponse:
    """Convert Invoice model to response schema."""
    return InvoiceResponse(
        id=str(invoice.id),
        appointment_id=str(invoice.appointment_id) if invoice.appointment_id else None,
        customer_id=str(invoice.customer_id),
        line_items=[
            {
                "service_id": str(item.service_id),
                "service_name": item.service_name,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "total": item.total,
            }
            for item in invoice.line_items
        ],
        subtotal=invoice.subtotal,
        discount=invoice.discount,
        tax=invoice.tax,
        total=invoice.total,
        status=invoice.status,
        due_date=invoice.due_date.isoformat() if invoice.due_date else None,
        paid_at=invoice.paid_at.isoformat() if invoice.paid_at else None,
        notes=invoice.notes,
        created_at=invoice.created_at.isoformat(),
        updated_at=invoice.updated_at.isoformat(),
    )
