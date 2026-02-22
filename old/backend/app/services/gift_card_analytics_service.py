"""
Gift Card Analytics Service - Comprehensive analytics for gift cards
"""
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from bson import ObjectId
import logging
import csv
import io
from app.database import Database

logger = logging.getLogger(__name__)


class GiftCardAnalyticsService:
    """Service for gift card analytics and reporting"""

    @staticmethod
    def get_analytics(
        tenant_id: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        card_type: Optional[str] = None
    ) -> Dict:
        """
        Get comprehensive gift card analytics
        
        Args:
            tenant_id: Tenant ID
            date_from: Start date for analytics
            date_to: End date for analytics
            card_type: Filter by card type (physical/digital)
            
        Returns:
            Dict with analytics data
        """
        db = Database.get_db()
        
        # Default date range: last 30 days
        if not date_to:
            date_to = datetime.now(timezone.utc)
        if not date_from:
            date_from = date_to - timedelta(days=30)
        
        # Build query filter
        query_filter = {
            "tenant_id": tenant_id,
            "created_at": {
                "$gte": date_from,
                "$lte": date_to
            }
        }
        
        if card_type:
            query_filter["card_type"] = card_type
        
        # Get all gift cards in date range
        cards = list(db.gift_cards.find(query_filter))
        
        # Calculate metrics
        total_sold = sum(card.get("amount", 0) for card in cards)
        total_redeemed = sum(
            sum(t.get("amount", 0) for t in card.get("transactions", []) if t.get("type") == "redeem")
            for card in cards
        )
        outstanding_liability = sum(card.get("balance", 0) for card in cards)
        
        total_cards_created = len(cards)
        total_cards_redeemed = len([c for c in cards if c.get("status") == "redeemed"])
        total_cards_expired = len([c for c in cards if c.get("status") == "expired"])
        
        redemption_rate = (total_redeemed / total_sold * 100) if total_sold > 0 else 0
        expiration_rate = (total_cards_expired / total_cards_created * 100) if total_cards_created > 0 else 0
        average_card_value = (total_sold / total_cards_created) if total_cards_created > 0 else 0
        
        # Card type breakdown
        digital_count = len([c for c in cards if c.get("card_type") == "digital"])
        physical_count = len([c for c in cards if c.get("card_type") == "physical"])
        
        # Top purchasers
        purchaser_map: Dict[str, Dict] = {}
        for card in cards:
            purchaser = card.get("purchaser_name", "Unknown")
            if purchaser not in purchaser_map:
                purchaser_map[purchaser] = {"count": 0, "amount": 0}
            purchaser_map[purchaser]["count"] += 1
            purchaser_map[purchaser]["amount"] += card.get("amount", 0)
        
        top_purchasers = sorted(
            [{"name": k, **v} for k, v in purchaser_map.items()],
            key=lambda x: x["amount"],
            reverse=True
        )[:5]
        
        # Top recipients
        recipient_map: Dict[str, Dict] = {}
        for card in cards:
            recipient = card.get("recipient_name", "Unknown")
            if recipient not in recipient_map:
                recipient_map[recipient] = {"count": 0, "amount": 0}
            recipient_map[recipient]["count"] += 1
            recipient_map[recipient]["amount"] += card.get("amount", 0)
        
        top_recipients = sorted(
            [{"name": k, **v} for k, v in recipient_map.items()],
            key=lambda x: x["amount"],
            reverse=True
        )[:5]
        
        return {
            "total_sold": total_sold,
            "total_redeemed": total_redeemed,
            "outstanding_liability": outstanding_liability,
            "redemption_rate": redemption_rate,
            "expiration_rate": expiration_rate,
            "average_card_value": average_card_value,
            "total_cards_created": total_cards_created,
            "total_cards_redeemed": total_cards_redeemed,
            "total_cards_expired": total_cards_expired,
            "card_type_breakdown": {
                "digital": digital_count,
                "physical": physical_count
            },
            "top_purchasers": top_purchasers,
            "top_recipients": top_recipients
        }
    
    @staticmethod
    def export_csv(
        tenant_id: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> str:
        """Export analytics to CSV"""
        analytics = GiftCardAnalyticsService.get_analytics(
            tenant_id=tenant_id,
            date_from=date_from,
            date_to=date_to
        )
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(["Gift Card Analytics Report"])
        writer.writerow([])
        
        # Write metrics
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Total Sold", f"₦{analytics['total_sold']:,.2f}"])
        writer.writerow(["Total Redeemed", f"₦{analytics['total_redeemed']:,.2f}"])
        writer.writerow(["Outstanding Liability", f"₦{analytics['outstanding_liability']:,.2f}"])
        writer.writerow(["Redemption Rate", f"{analytics['redemption_rate']:.1f}%"])
        writer.writerow(["Expiration Rate", f"{analytics['expiration_rate']:.1f}%"])
        writer.writerow(["Average Card Value", f"₦{analytics['average_card_value']:,.2f}"])
        writer.writerow(["Total Cards Created", analytics['total_cards_created']])
        writer.writerow(["Total Cards Redeemed", analytics['total_cards_redeemed']])
        writer.writerow(["Total Cards Expired", analytics['total_cards_expired']])
        writer.writerow([])
        
        # Write card type breakdown
        writer.writerow(["Card Type", "Count"])
        writer.writerow(["Digital", analytics['card_type_breakdown']['digital']])
        writer.writerow(["Physical", analytics['card_type_breakdown']['physical']])
        writer.writerow([])
        
        # Write top purchasers
        writer.writerow(["Top Purchasers"])
        writer.writerow(["Name", "Count", "Amount"])
        for purchaser in analytics['top_purchasers']:
            writer.writerow([purchaser['name'], purchaser['count'], f"₦{purchaser['amount']:,.2f}"])
        writer.writerow([])
        
        # Write top recipients
        writer.writerow(["Top Recipients"])
        writer.writerow(["Name", "Count", "Amount"])
        for recipient in analytics['top_recipients']:
            writer.writerow([recipient['name'], recipient['count'], f"₦{recipient['amount']:,.2f}"])
        
        return output.getvalue()
    
    @staticmethod
    def export_pdf(
        tenant_id: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> bytes:
        """Export analytics to PDF"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            
            analytics = GiftCardAnalyticsService.get_analytics(
                tenant_id=tenant_id,
                date_from=date_from,
                date_to=date_to
            )
            
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
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
            elements.append(Paragraph("Gift Card Analytics Report", title_style))
            elements.append(Spacer(1, 0.2*inch))
            
            # Metrics table
            metrics_data = [
                ["Metric", "Value"],
                ["Total Sold", f"₦{analytics['total_sold']:,.2f}"],
                ["Total Redeemed", f"₦{analytics['total_redeemed']:,.2f}"],
                ["Outstanding Liability", f"₦{analytics['outstanding_liability']:,.2f}"],
                ["Redemption Rate", f"{analytics['redemption_rate']:.1f}%"],
                ["Expiration Rate", f"{analytics['expiration_rate']:.1f}%"],
                ["Average Card Value", f"₦{analytics['average_card_value']:,.2f}"],
                ["Total Cards Created", str(analytics['total_cards_created'])],
                ["Total Cards Redeemed", str(analytics['total_cards_redeemed'])],
                ["Total Cards Expired", str(analytics['total_cards_expired'])],
            ]
            
            metrics_table = Table(metrics_data, colWidths=[3*inch, 2*inch])
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9333ea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(metrics_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Build PDF
            doc.build(elements)
            buffer.seek(0)
            return buffer.getvalue()
        except ImportError:
            # Fallback if reportlab not available
            return b"PDF export not available"