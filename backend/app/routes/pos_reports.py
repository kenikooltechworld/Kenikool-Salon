"""API routes for POS reporting."""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
from bson import ObjectId
from datetime import datetime, timedelta
from io import BytesIO
import csv
from app.context import get_tenant_id
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/sales")
async def get_sales_report(
    start_date: str = Query(None, alias="startDate"),
    end_date: str = Query(None, alias="endDate"),
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """Get sales report."""
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    
    try:
        transactions, total = TransactionService.list_transactions(
            tenant_id=tenant_id,
            page=1,
            page_size=1000,
        )

        # Calculate sales metrics
        total_sales = sum(t.total for t in transactions)
        total_transactions = len(transactions)
        average_transaction = total_sales / total_transactions if total_transactions > 0 else 0

        return {
            "total_sales": total_sales,
            "total_transactions": total_transactions,
            "average_transaction": average_transaction,
            "period": {
                "start_date": start_date,
                "end_date": end_date,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/revenue")
async def get_revenue_report(
    start_date: str = Query(None, alias="startDate"),
    end_date: str = Query(None, alias="endDate"),
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """Get revenue report."""
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    
    try:
        transactions, total = TransactionService.list_transactions(
            tenant_id=tenant_id,
            page=1,
            page_size=1000,
        )

        # Calculate revenue metrics
        total_revenue = sum(t.total for t in transactions)
        total_tax = sum(t.tax_amount for t in transactions)
        total_discount = sum(t.discount_amount for t in transactions)

        return {
            "total_revenue": total_revenue,
            "total_tax": total_tax,
            "total_discount": total_discount,
            "net_revenue": total_revenue - total_tax,
            "period": {
                "start_date": start_date,
                "end_date": end_date,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/inventory")
async def get_inventory_report(
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """Get inventory report."""
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    
    try:
        from app.models.inventory import Inventory

        inventories = Inventory.objects(tenant_id=tenant_id)

        low_stock_items = [
            {
                "product_id": str(inv.product_id),
                "quantity_on_hand": inv.quantity_on_hand,
                "reorder_point": inv.reorder_point,
            }
            for inv in inventories
            if inv.quantity_on_hand <= inv.reorder_point
        ]

        return {
            "total_items": len(list(inventories)),
            "low_stock_items": low_stock_items,
            "low_stock_count": len(low_stock_items),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/payments")
async def get_payment_report(
    start_date: str = Query(None, alias="startDate"),
    end_date: str = Query(None, alias="endDate"),
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """Get payment report."""
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    
    try:
        transactions, total = TransactionService.list_transactions(
            tenant_id=tenant_id,
            page=1,
            page_size=1000,
        )

        # Group by payment method
        payment_methods = {}
        for t in transactions:
            if t.payment_method not in payment_methods:
                payment_methods[t.payment_method] = {
                    "count": 0,
                    "total": 0,
                }
            payment_methods[t.payment_method]["count"] += 1
            payment_methods[t.payment_method]["total"] += t.total

        return {
            "payment_methods": payment_methods,
            "total_transactions": len(transactions),
            "period": {
                "start_date": start_date,
                "end_date": end_date,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _generate_csv_report(report_type: str, data: dict) -> BytesIO:
    """Generate CSV report."""
    output = BytesIO()
    writer = csv.writer(output)

    if report_type == "sales":
        writer.writerow(["Sales Report"])
        writer.writerow(["Total Sales", data.get("total_sales", 0)])
        writer.writerow(["Total Transactions", data.get("total_transactions", 0)])
        writer.writerow(["Average Transaction", data.get("average_transaction", 0)])
    elif report_type == "revenue":
        writer.writerow(["Revenue Report"])
        writer.writerow(["Total Revenue", data.get("total_revenue", 0)])
        writer.writerow(["Total Tax", data.get("total_tax", 0)])
        writer.writerow(["Total Discount", data.get("total_discount", 0)])
        writer.writerow(["Net Revenue", data.get("net_revenue", 0)])
    elif report_type == "inventory":
        writer.writerow(["Inventory Report"])
        writer.writerow(["Total Items", data.get("total_items", 0)])
        writer.writerow(["Low Stock Count", data.get("low_stock_count", 0)])
        writer.writerow([])
        writer.writerow(["Product ID", "Quantity On Hand", "Reorder Point"])
        for item in data.get("low_stock_items", []):
            writer.writerow([
                item.get("product_id"),
                item.get("quantity_on_hand"),
                item.get("reorder_point"),
            ])
    elif report_type == "payments":
        writer.writerow(["Payments Report"])
        writer.writerow(["Total Transactions", data.get("total_transactions", 0)])
        writer.writerow([])
        writer.writerow(["Payment Method", "Count", "Total"])
        for method, info in data.get("payment_methods", {}).items():
            writer.writerow([method, info.get("count"), info.get("total")])

    output.seek(0)
    return output


def _generate_pdf_report(report_type: str, data: dict) -> BytesIO:
    """Generate PDF report."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch

        output = BytesIO()
        doc = SimpleDocTemplate(output, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
        )

        if report_type == "sales":
            elements.append(Paragraph("Sales Report", title_style))
            data_list = [
                ["Metric", "Value"],
                ["Total Sales", f"₦{data.get('total_sales', 0):,.2f}"],
                ["Total Transactions", str(data.get("total_transactions", 0))],
                ["Average Transaction", f"₦{data.get('average_transaction', 0):,.2f}"],
            ]
        elif report_type == "revenue":
            elements.append(Paragraph("Revenue Report", title_style))
            data_list = [
                ["Metric", "Value"],
                ["Total Revenue", f"₦{data.get('total_revenue', 0):,.2f}"],
                ["Total Tax", f"₦{data.get('total_tax', 0):,.2f}"],
                ["Total Discount", f"₦{data.get('total_discount', 0):,.2f}"],
                ["Net Revenue", f"₦{data.get('net_revenue', 0):,.2f}"],
            ]
        elif report_type == "inventory":
            elements.append(Paragraph("Inventory Report", title_style))
            data_list = [
                ["Metric", "Value"],
                ["Total Items", str(data.get("total_items", 0))],
                ["Low Stock Count", str(data.get("low_stock_count", 0))],
            ]
        elif report_type == "payments":
            elements.append(Paragraph("Payments Report", title_style))
            data_list = [
                ["Payment Method", "Count", "Total"],
            ]
            for method, info in data.get("payment_methods", {}).items():
                data_list.append([
                    method,
                    str(info.get("count")),
                    f"₦{info.get('total', 0):,.2f}",
                ])

        table = Table(data_list)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 0.5 * inch))
        elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))

        doc.build(elements)
        output.seek(0)
        return output
    except ImportError:
        raise HTTPException(status_code=500, detail="PDF generation library not available")


@router.get("/export")
async def export_report(
    report_type: str = Query("sales", alias="reportType"),
    format: str = Query("pdf"),
    start_date: str = Query(None, alias="startDate"),
    end_date: str = Query(None, alias="endDate"),
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """Export report as PDF or CSV."""
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    
    try:
        # Get the report data based on type
        if report_type == "sales":
            transactions, _ = TransactionService.list_transactions(
                tenant_id=tenant_id,
                page=1,
                page_size=1000,
            )
            total_sales = sum(t.total for t in transactions)
            total_transactions = len(transactions)
            average_transaction = total_sales / total_transactions if total_transactions > 0 else 0
            data = {
                "total_sales": total_sales,
                "total_transactions": total_transactions,
                "average_transaction": average_transaction,
            }
        elif report_type == "revenue":
            transactions, _ = TransactionService.list_transactions(
                tenant_id=tenant_id,
                page=1,
                page_size=1000,
            )
            total_revenue = sum(t.total for t in transactions)
            total_tax = sum(t.tax_amount for t in transactions)
            total_discount = sum(t.discount_amount for t in transactions)
            data = {
                "total_revenue": total_revenue,
                "total_tax": total_tax,
                "total_discount": total_discount,
                "net_revenue": total_revenue - total_tax,
            }
        elif report_type == "inventory":
            from app.models.inventory import Inventory
            inventories = Inventory.objects(tenant_id=tenant_id)
            low_stock_items = [
                {
                    "product_id": str(inv.product_id),
                    "quantity_on_hand": inv.quantity_on_hand,
                    "reorder_point": inv.reorder_point,
                }
                for inv in inventories
                if inv.quantity_on_hand <= inv.reorder_point
            ]
            data = {
                "total_items": len(list(inventories)),
                "low_stock_items": low_stock_items,
                "low_stock_count": len(low_stock_items),
            }
        elif report_type == "payments":
            transactions, _ = TransactionService.list_transactions(
                tenant_id=tenant_id,
                page=1,
                page_size=1000,
            )
            payment_methods = {}
            for t in transactions:
                if t.payment_method not in payment_methods:
                    payment_methods[t.payment_method] = {"count": 0, "total": 0}
                payment_methods[t.payment_method]["count"] += 1
                payment_methods[t.payment_method]["total"] += t.total
            data = {
                "payment_methods": payment_methods,
                "total_transactions": len(transactions),
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid report type")

        # Generate file based on format
        if format == "csv":
            output = _generate_csv_report(report_type, data)
            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=report_{report_type}.csv"},
            )
        elif format == "pdf":
            output = _generate_pdf_report(report_type, data)
            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename=report_{report_type}.pdf"},
            )
        elif format == "excel":
            try:
                import pandas as pd
                df = pd.DataFrame([data])
                output = BytesIO()
                df.to_excel(output, index=False)
                output.seek(0)
                return StreamingResponse(
                    iter([output.getvalue()]),
                    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": f"attachment; filename=report_{report_type}.xlsx"},
                )
            except ImportError:
                raise HTTPException(status_code=500, detail="Excel generation library not available")
        else:
            raise HTTPException(status_code=400, detail="Invalid format")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
