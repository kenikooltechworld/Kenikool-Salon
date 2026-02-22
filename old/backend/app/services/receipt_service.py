"""
Receipt Service - Payment receipt generation and management
Handles PDF receipt generation and email delivery
"""
from bson import ObjectId
from datetime import datetime
from typing import Dict, Optional
import logging
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

from app.database import Database
from app.api.exceptions import NotFoundException, BadRequestException

logger = logging.getLogger(__name__)


class ReceiptService:
    """Service for payment receipt generation and management"""
    
    @staticmethod
    def generate_receipt_number(tenant_id: str) -> str:
        """
        Generate a unique receipt number
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Unique receipt number
        """
        db = Database.get_db()
        
        # Get count of receipts for this tenant
        count = db.payment_receipts.count_documents({"tenant_id": tenant_id})
        receipt_num = count + 1
        
        return f"RCP-{tenant_id[:4].upper()}-{receipt_num:06d}"
    
    @staticmethod
    def format_receipt_data(
        payment: Dict,
        booking: Optional[Dict] = None,
        client: Optional[Dict] = None,
        salon_info: Optional[Dict] = None
    ) -> Dict:
        """
        Format payment and related data for receipt
        
        Args:
            payment: Payment record
            booking: Related booking record
            client: Related client record
            salon_info: Salon information for branding
            
        Returns:
            Formatted receipt data
        """
        return {
            "payment_reference": payment.get("reference"),
            "payment_amount": payment.get("amount"),
            "payment_method": payment.get("payment_method", payment.get("gateway")),
            "payment_date": payment.get("created_at"),
            "payment_status": payment.get("status"),
            "is_manual": payment.get("is_manual", False),
            
            "booking_reference": booking.get("reference") if booking else None,
            "booking_service": booking.get("service") if booking else None,
            "booking_date": booking.get("start_time") if booking else None,
            
            "client_name": client.get("name") if client else None,
            "client_email": client.get("email") if client else None,
            "client_phone": client.get("phone") if client else None,
            
            "salon_name": salon_info.get("name") if salon_info else "Salon",
            "salon_address": salon_info.get("address") if salon_info else "",
            "salon_phone": salon_info.get("phone") if salon_info else "",
            "salon_email": salon_info.get("email") if salon_info else ""
        }
    
    @staticmethod
    def generate_pdf_receipt(
        receipt_data: Dict,
        receipt_number: str
    ) -> bytes:
        """
        Generate PDF receipt
        
        Args:
            receipt_data: Formatted receipt data
            receipt_number: Receipt number
            
        Returns:
            PDF file as bytes
        """
        # Create PDF in memory
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=1  # Center
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#555555'),
            spaceAfter=6
        )
        
        # Build content
        content = []
        
        # Header
        content.append(Paragraph("PAYMENT RECEIPT", title_style))
        content.append(Spacer(1, 0.2 * inch))
        
        # Salon info
        salon_name = receipt_data.get("salon_name", "Salon")
        content.append(Paragraph(f"<b>{salon_name}</b>", heading_style))
        
        if receipt_data.get("salon_address"):
            content.append(Paragraph(receipt_data["salon_address"], normal_style))
        if receipt_data.get("salon_phone"):
            content.append(Paragraph(f"Phone: {receipt_data['salon_phone']}", normal_style))
        if receipt_data.get("salon_email"):
            content.append(Paragraph(f"Email: {receipt_data['salon_email']}", normal_style))
        
        content.append(Spacer(1, 0.3 * inch))
        
        # Receipt details
        receipt_details = [
            ["Receipt Number:", receipt_number],
            ["Date:", receipt_data.get("payment_date", datetime.utcnow()).strftime("%Y-%m-%d %H:%M:%S")],
            ["Status:", receipt_data.get("payment_status", "").upper()]
        ]
        
        receipt_table = Table(receipt_details, colWidths=[2 * inch, 3 * inch])
        receipt_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#333333')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        content.append(receipt_table)
        
        content.append(Spacer(1, 0.2 * inch))
        
        # Customer info
        if receipt_data.get("client_name"):
            content.append(Paragraph("<b>Customer Information</b>", heading_style))
            customer_details = [
                ["Name:", receipt_data.get("client_name", "")],
                ["Email:", receipt_data.get("client_email", "")],
                ["Phone:", receipt_data.get("client_phone", "")]
            ]
            
            customer_table = Table(customer_details, colWidths=[2 * inch, 3 * inch])
            customer_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#333333')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            content.append(customer_table)
            content.append(Spacer(1, 0.2 * inch))
        
        # Booking info
        if receipt_data.get("booking_reference"):
            content.append(Paragraph("<b>Booking Information</b>", heading_style))
            booking_details = [
                ["Booking Reference:", receipt_data.get("booking_reference", "")],
                ["Service:", receipt_data.get("booking_service", "")],
                ["Date:", receipt_data.get("booking_date", "").strftime("%Y-%m-%d %H:%M:%S") if receipt_data.get("booking_date") else ""]
            ]
            
            booking_table = Table(booking_details, colWidths=[2 * inch, 3 * inch])
            booking_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#333333')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            content.append(booking_table)
            content.append(Spacer(1, 0.2 * inch))
        
        # Payment info
        content.append(Paragraph("<b>Payment Information</b>", heading_style))
        payment_details = [
            ["Payment Reference:", receipt_data.get("payment_reference", "")],
            ["Amount:", f"₦{receipt_data.get('payment_amount', 0):,.2f}"],
            ["Method:", receipt_data.get("payment_method", "").upper()],
            ["Type:", "Manual" if receipt_data.get("is_manual") else "Online"]
        ]
        
        payment_table = Table(payment_details, colWidths=[2 * inch, 3 * inch])
        payment_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#333333')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f5f5f5')),
        ]))
        content.append(payment_table)
        
        content.append(Spacer(1, 0.3 * inch))
        
        # Footer
        footer_text = "Thank you for your business!"
        content.append(Paragraph(footer_text, ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#999999'),
            alignment=1
        )))
        
        # Build PDF
        doc.build(content)
        pdf_buffer.seek(0)
        
        return pdf_buffer.getvalue()
    
    @staticmethod
    def generate_receipt(
        tenant_id: str,
        payment_id: str,
        generated_by: str
    ) -> Dict:
        """
        Generate receipt for a payment
        
        Args:
            tenant_id: Tenant ID
            payment_id: Payment ID
            generated_by: User ID who generated receipt
            
        Returns:
            Dict with receipt details
            
        Raises:
            NotFoundException: If payment not found
        """
        db = Database.get_db()
        
        try:
            payment_oid = ObjectId(payment_id)
        except Exception:
            raise BadRequestException("Invalid payment ID format")
        
        # Fetch payment
        payment = db.payments.find_one({
            "_id": payment_oid,
            "tenant_id": tenant_id
        })
        
        if not payment:
            raise NotFoundException("Payment not found")
        
        # Fetch related data
        booking = None
        if payment.get("booking_id"):
            try:
                booking_oid = ObjectId(payment["booking_id"])
                booking = db.bookings.find_one({
                    "_id": booking_oid,
                    "tenant_id": tenant_id
                })
            except Exception as e:
                logger.warning(f"Failed to fetch booking: {str(e)}")
        
        client = None
        client_id = payment.get("client_id") or (booking.get("client_id") if booking else None)
        if client_id:
            try:
                client_oid = ObjectId(client_id)
                client = db.clients.find_one({
                    "_id": client_oid,
                    "tenant_id": tenant_id
                })
            except Exception as e:
                logger.warning(f"Failed to fetch client: {str(e)}")
        
        # Fetch salon info
        salon_info = None
        try:
            tenant = db.tenants.find_one({"_id": ObjectId(tenant_id)})
            if tenant:
                salon_info = {
                    "name": tenant.get("name", "Salon"),
                    "address": tenant.get("address", ""),
                    "phone": tenant.get("phone", ""),
                    "email": tenant.get("email", "")
                }
        except Exception as e:
            logger.warning(f"Failed to fetch tenant info: {str(e)}")
        
        # Format receipt data
        receipt_data = ReceiptService.format_receipt_data(
            payment, booking, client, salon_info
        )
        
        # Generate receipt number
        receipt_number = ReceiptService.generate_receipt_number(tenant_id)
        
        # Generate PDF
        pdf_bytes = ReceiptService.generate_pdf_receipt(receipt_data, receipt_number)
        
        # Store receipt record
        receipt_record = {
            "tenant_id": tenant_id,
            "payment_id": payment_id,
            "receipt_number": receipt_number,
            "receipt_data": receipt_data,
            "generated_at": datetime.utcnow(),
            "generated_by": generated_by,
            "emailed_to": None,
            "emailed_at": None
        }
        
        result = db.payment_receipts.insert_one(receipt_record)
        receipt_id = str(result.inserted_id)
        
        # Update payment record with receipt info
        db.payments.update_one(
            {"_id": payment_oid},
            {
                "$set": {
                    "receipt_generated_at": datetime.utcnow(),
                    "receipt_url": f"/api/payments/{payment_id}/receipt",
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(
            f"Receipt generated: {receipt_id} for payment {payment_id}, "
            f"receipt number: {receipt_number}"
        )
        
        return {
            "receipt_id": receipt_id,
            "receipt_number": receipt_number,
            "payment_id": payment_id,
            "pdf_bytes": pdf_bytes,
            "generated_at": receipt_record["generated_at"],
            "message": f"Receipt {receipt_number} generated successfully"
        }
    
    @staticmethod
    def email_receipt(
        tenant_id: str,
        payment_id: str,
        email_address: Optional[str] = None
    ) -> Dict:
        """
        Email payment receipt to customer
        
        Args:
            tenant_id: Tenant ID
            payment_id: Payment ID
            email_address: Optional email address (uses payment metadata if not provided)
            
        Returns:
            Dict with email delivery status
            
        Raises:
            NotFoundException: If payment not found
            BadRequestException: If no email address available
        """
        db = Database.get_db()
        
        try:
            payment_oid = ObjectId(payment_id)
        except Exception:
            raise BadRequestException("Invalid payment ID format")
        
        # Fetch payment
        payment = db.payments.find_one({
            "_id": payment_oid,
            "tenant_id": tenant_id
        })
        
        if not payment:
            raise NotFoundException("Payment not found")
        
        # Determine email address
        if not email_address:
            # Try to get from client
            if payment.get("client_id"):
                try:
                    client_oid = ObjectId(payment["client_id"])
                    client = db.clients.find_one({
                        "_id": client_oid,
                        "tenant_id": tenant_id
                    })
                    if client:
                        email_address = client.get("email")
                except Exception:
                    pass
            
            # Try to get from metadata
            if not email_address and payment.get("metadata"):
                email_address = payment["metadata"].get("email")
        
        if not email_address:
            raise BadRequestException("No email address available for receipt delivery")
        
        # Generate receipt if not already generated
        receipt = db.payment_receipts.find_one({
            "payment_id": payment_id,
            "tenant_id": tenant_id
        })
        
        if not receipt:
            # Generate new receipt
            receipt_result = ReceiptService.generate_receipt(
                tenant_id, payment_id, "system"
            )
            pdf_bytes = receipt_result["pdf_bytes"]
            receipt_number = receipt_result["receipt_number"]
        else:
            # Regenerate PDF from stored data
            receipt_number = receipt["receipt_number"]
            pdf_bytes = ReceiptService.generate_pdf_receipt(
                receipt["receipt_data"],
                receipt_number
            )
        
        # Send email
        try:
            email_service = EmailService()
            email_service.send_receipt_email(
                to_email=email_address,
                receipt_number=receipt_number,
                payment_amount=payment.get("amount"),
                pdf_bytes=pdf_bytes
            )
            
            # Update receipt record
            db.payment_receipts.update_one(
                {"payment_id": payment_id, "tenant_id": tenant_id},
                {
                    "$set": {
                        "emailed_to": email_address,
                        "emailed_at": datetime.utcnow()
                    }
                }
            )
            
            # Update payment record
            db.payments.update_one(
                {"_id": payment_oid},
                {
                    "$set": {
                        "receipt_emailed_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            logger.info(
                f"Receipt emailed: {receipt_number} to {email_address} "
                f"for payment {payment_id}"
            )
            
            return {
                "success": True,
                "receipt_number": receipt_number,
                "email_address": email_address,
                "emailed_at": datetime.utcnow(),
                "message": f"Receipt {receipt_number} emailed successfully to {email_address}"
            }
        
        except Exception as e:
            logger.error(f"Failed to email receipt: {str(e)}")
            raise BadRequestException(f"Failed to email receipt: {str(e)}")


# Singleton instance
receipt_service = ReceiptService()
