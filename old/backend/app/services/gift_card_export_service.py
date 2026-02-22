"""
Gift Card Export Service - Export gift cards to CSV and PDF
"""
from typing import Optional, Dict, List
import csv
import io
from datetime import datetime
from app.database import Database


class GiftCardExportService:
    """Service for exporting gift cards"""

    @staticmethod
    def export_csv(
        tenant_id: str,
        status: Optional[str] = None,
        card_type: Optional[str] = None
    ) -> str:
        """Export gift cards to CSV"""
        db = Database.get_db()
        
        # Build query filter
        query_filter = {"tenant_id": tenant_id}
        if status:
            query_filter["status"] = status
        if card_type:
            query_filter["card_type"] = card_type
        
        # Get all matching gift cards
        cards = list(db.gift_cards.find(query_filter))
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "Card Number",
            "Amount",
            "Balance",
            "Status",
            "Type",
            "Recipient Name",
            "Recipient Email",
            "Created Date",
            "Expires Date",
            "Delivery Status"
        ])
        
        # Write data
        for card in cards:
            writer.writerow([
                card.get("card_number", ""),
                card.get("amount", 0),
                card.get("balance", 0),
                card.get("status", ""),
                card.get("card_type", ""),
                card.get("recipient_name", ""),
                card.get("recipient_email", ""),
                card.get("created_at", "").isoformat() if card.get("created_at") else "",
                card.get("expires_at", "").isoformat() if card.get("expires_at") else "",
                card.get("delivery_status", "")
            ])
        
        return output.getvalue()
    
    @staticmethod
    def export_pdf(
        tenant_id: str,
        status: Optional[str] = None,
        card_type: Optional[str] = None
    ) -> bytes:
        """Export gift cards to PDF"""
        try:
            from reportlab.lib.pagesizes import letter, landscape
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            
            db = Database.get_db()
            
            # Build query filter
            query_filter = {"tenant_id": tenant_id}
            if status:
                query_filter["status"] = status
            if card_type:
                query_filter["card_type"] = card_type
            
            # Get all matching gift cards
            cards = list(db.gift_cards.find(query_filter))
            
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
            elements = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1f2937'),
                spaceAfter=30,
            )
            elements.append(Paragraph("Gift Cards Report", title_style))
            elements.append(Spacer(1, 0.2*inch))
            
            # Create table data
            table_data = [[
                "Card Number",
                "Amount",
                "Balance",
                "Status",
                "Type",
                "Recipient",
                "Created",
                "Expires"
            ]]
            
            for card in cards[:100]:  # Limit to 100 rows for PDF
                table_data.append([
                    card.get("card_number", "")[:15],
                    f"₦{card.get('amount', 0):,.0f}",
                    f"₦{card.get('balance', 0):,.0f}",
                    card.get("status", ""),
                    card.get("card_type", ""),
                    card.get("recipient_name", "")[:20],
                    card.get("created_at", "").strftime("%Y-%m-%d") if card.get("created_at") else "",
                    card.get("expires_at", "").strftime("%Y-%m-%d") if card.get("expires_at") else "",
                ])
            
            # Create table
            table = Table(table_data, colWidths=[1.2*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.7*inch, 1.2*inch, 0.9*inch, 0.9*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9333ea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            elements.append(table)
            
            # Build PDF
            doc.build(elements)
            buffer.seek(0)
            return buffer.getvalue()
        except ImportError:
            # Fallback if reportlab not available
            return b"PDF export not available"
