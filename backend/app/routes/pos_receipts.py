"""API routes for POS receipts."""

from fastapi import APIRouter, Depends, HTTPException, Query
from bson import ObjectId
from app.context import get_tenant_id
from app.schemas.receipt import (
    ReceiptResponse,
    ReceiptPrintRequest,
    ReceiptEmailRequest,
    ReceiptListResponse,
)
from app.services.receipt_service import ReceiptService
from app.tasks import send_email

router = APIRouter(prefix="/receipts", tags=["receipts"])


@router.get("/{transaction_id}", response_model=ReceiptResponse)
async def get_receipt_by_transaction(
    transaction_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """Get receipt for a transaction."""
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    
    try:
        receipt = ReceiptService.get_receipt_by_transaction(
            tenant_id=tenant_id,
            transaction_id=ObjectId(transaction_id),
        )

        if not receipt:
            raise HTTPException(status_code=404, detail="Receipt not found")

        return ReceiptResponse(
            id=str(receipt.id),
            transaction_id=str(receipt.transaction_id),
            customer_id=str(receipt.customer_id),
            receipt_number=receipt.receipt_number,
            receipt_date=receipt.receipt_date.isoformat(),
            customer_name=receipt.customer_name,
            customer_email=receipt.customer_email,
            customer_phone=receipt.customer_phone,
            items=[
                {
                    "item_type": item.item_type,
                    "item_id": str(item.item_id),
                    "item_name": item.item_name,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "line_total": item.line_total,
                    "tax_amount": item.tax_amount,
                    "discount_amount": item.discount_amount,
                }
                for item in receipt.items
            ],
            subtotal=receipt.subtotal,
            tax_amount=receipt.tax_amount,
            discount_amount=receipt.discount_amount,
            total=receipt.total,
            payment_method=receipt.payment_method,
            payment_reference=receipt.payment_reference,
            receipt_format=receipt.receipt_format,
            printed_at=receipt.printed_at.isoformat() if receipt.printed_at else None,
            emailed_at=receipt.emailed_at.isoformat() if receipt.emailed_at else None,
            created_at=receipt.created_at.isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=ReceiptListResponse)
async def list_receipts(
    customer_id: str = Query(None, alias="customerId"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100, alias="pageSize"),
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """List receipts."""
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    
    try:
        receipts, total = ReceiptService.list_receipts(
            tenant_id=tenant_id,
            customer_id=ObjectId(customer_id) if customer_id else None,
            page=page,
            page_size=page_size,
        )

        return ReceiptListResponse(
            receipts=[
                ReceiptResponse(
                    id=str(r.id),
                    transaction_id=str(r.transaction_id),
                    customer_id=str(r.customer_id),
                    receipt_number=r.receipt_number,
                    receipt_date=r.receipt_date.isoformat(),
                    customer_name=r.customer_name,
                    customer_email=r.customer_email,
                    customer_phone=r.customer_phone,
                    items=[
                        {
                            "item_type": item.item_type,
                            "item_id": str(item.item_id),
                            "item_name": item.item_name,
                            "quantity": item.quantity,
                            "unit_price": item.unit_price,
                            "line_total": item.line_total,
                            "tax_amount": item.tax_amount,
                            "discount_amount": item.discount_amount,
                        }
                        for item in r.items
                    ],
                    subtotal=r.subtotal,
                    tax_amount=r.tax_amount,
                    discount_amount=r.discount_amount,
                    total=r.total,
                    payment_method=r.payment_method,
                    payment_reference=r.payment_reference,
                    receipt_format=r.receipt_format,
                    printed_at=r.printed_at.isoformat() if r.printed_at else None,
                    emailed_at=r.emailed_at.isoformat() if r.emailed_at else None,
                    created_at=r.created_at.isoformat(),
                )
                for r in receipts
            ],
            total=total,
            page=page,
            page_size=page_size,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{receipt_id}/print")
async def print_receipt(
    receipt_id: str,
    request: ReceiptPrintRequest,
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """Print receipt."""
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    
    try:
        receipt = ReceiptService.mark_receipt_printed(
            tenant_id=tenant_id,
            receipt_id=ObjectId(receipt_id),
        )

        if not receipt:
            raise HTTPException(status_code=404, detail="Receipt not found")

        return {"status": "success", "message": "Receipt marked as printed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{receipt_id}/email")
async def email_receipt(
    receipt_id: str,
    request: ReceiptEmailRequest,
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """Email receipt."""
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    
    try:
        receipt = ReceiptService.get_receipt(
            tenant_id=tenant_id,
            receipt_id=ObjectId(receipt_id),
        )

        if not receipt:
            raise HTTPException(status_code=404, detail="Receipt not found")

        recipient_email = request.email or receipt.customer_email
        if not recipient_email:
            raise HTTPException(status_code=400, detail="No email address provided")

        items_html = "".join(
            f"<li>{item.item_name} x {item.quantity} - ₦{float(item.line_total):,.2f}</li>"
            for item in receipt.items
        )

        html_body = f"""
        <h1>Receipt #{receipt.receipt_number}</h1>
        <p>Date: {receipt.receipt_date.strftime('%Y-%m-%d %H:%M')}</p>
        <p>Customer: {receipt.customer_name}</p>
        <h3>Items</h3>
        <ul>{items_html}</ul>
        <p><strong>Total: ₦{float(receipt.total):,.2f}</strong></p>
        <p>Payment Method: {receipt.payment_method}</p>
        """

        send_email(
            to=recipient_email,
            subject=f"Receipt #{receipt.receipt_number}",
            template="custom",
            context={"html_content": html_body},
        )

        ReceiptService.mark_receipt_emailed(tenant_id, ObjectId(receipt_id))

        return {"status": "success", "message": f"Receipt emailed to {recipient_email}"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{receipt_id}/pdf")
async def download_receipt_pdf(
    receipt_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """Download receipt as PDF."""
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")

    try:
        receipt = ReceiptService.get_receipt(
            tenant_id=tenant_id,
            receipt_id=ObjectId(receipt_id),
        )

        if not receipt:
            raise HTTPException(status_code=404, detail="Receipt not found")

        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from io import BytesIO

            output = BytesIO()
            doc = SimpleDocTemplate(output, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                "CustomReceipt",
                parent=styles["Heading1"],
                fontSize=20,
                textColor=colors.HexColor("#1a1a1a"),
                spaceAfter=20,
            )

            elements.append(Paragraph(f"Receipt #{receipt.receipt_number}", title_style))
            elements.append(Paragraph(f"Date: {receipt.receipt_date.strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))
            elements.append(Paragraph(f"Customer: {receipt.customer_name}", styles["Normal"]))
            if receipt.customer_email:
                elements.append(Paragraph(f"Email: {receipt.customer_email}", styles["Normal"]))
            if receipt.customer_phone:
                elements.append(Paragraph(f"Phone: {receipt.customer_phone}", styles["Normal"]))
            elements.append(Spacer(1, 0.2 * inch))

            data_list = [
                ["Item", "Qty", "Unit Price", "Line Total"],
            ]
            for item in receipt.items:
                data_list.append([
                    item.item_name,
                    str(item.quantity),
                    f"₦{float(item.unit_price):,.2f}",
                    f"₦{float(item.line_total):,.2f}",
                ])

            table = Table(data_list, colWidths=[2.5 * inch, 0.8 * inch, 1.2 * inch, 1.2 * inch])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 12),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 0.3 * inch))

            totals = [
                ["Subtotal", f"₦{float(receipt.subtotal):,.2f}"],
                ["Tax", f"₦{float(receipt.tax_amount):,.2f}"],
            ]
            if receipt.discount_amount > 0:
                totals.append(["Discount", f"-₦{float(receipt.discount_amount):,.2f}"])
            totals.append(["Total", f"₦{float(receipt.total):,.2f}"])

            totals_table = Table(totals, colWidths=[3 * inch, 2 * inch])
            totals_table.setStyle(TableStyle([
                ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, -1), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))
            elements.append(totals_table)
            elements.append(Spacer(1, 0.2 * inch))
            elements.append(Paragraph(f"Payment Method: {receipt.payment_method}", styles["Normal"]))
            elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))

            doc.build(elements)
            output.seek(0)

            try:
                ReceiptService.mark_receipt_printed(tenant_id, ObjectId(receipt_id))
            except Exception:
                pass

            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename=receipt-{receipt.receipt_number}.pdf"},
            )
        except ImportError:
            raise HTTPException(status_code=500, detail="PDF generation library not available")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
