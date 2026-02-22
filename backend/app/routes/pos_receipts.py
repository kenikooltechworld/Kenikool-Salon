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

router = APIRouter(prefix="/receipts", tags=["receipts"])


@router.get("/{transaction_id}", response_model=ReceiptResponse)
async def get_receipt_by_transaction(
    transaction_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """Get receipt for a transaction."""
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
    try:
        receipt = ReceiptService.mark_receipt_emailed(
            tenant_id=tenant_id,
            receipt_id=ObjectId(receipt_id),
        )

        if not receipt:
            raise HTTPException(status_code=404, detail="Receipt not found")

        return {"status": "success", "message": "Receipt marked as emailed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
