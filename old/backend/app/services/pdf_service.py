"""
PDF Service for Gift Cards
Generates printable PDF certificates for gift cards
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from io import BytesIO
from datetime import datetime
import qrcode


class PDFService:
    """Service for generating PDF gift card certificates"""

    @staticmethod
    def generate_gift_card_certificate(
        card_number: str,
        amount: float,
        recipient_name: str = None,
        message: str = None,
        expires_at: datetime = None,
        qr_code_data: str = None,
        design_theme: str = "default",
        salon_name: str = None,
        salon_logo_url: str = None
    ) -> bytes:
        """
        Generate a printable PDF certificate for a gift card
        
        Args:
            card_number: Gift card number
            amount: Gift card amount
            recipient_name: Name of recipient
            message: Personal message
            expires_at: Expiration date
            qr_code_data: QR code data URL
            design_theme: Design theme (default, christmas, birthday, valentine)
            salon_name: Name of salon
            salon_logo_url: URL to salon logo
            
        Returns:
            PDF file as bytes
        """
        try:
            # Create PDF buffer
            buffer = BytesIO()
            
            # Create canvas
            c = canvas.Canvas(buffer, pagesize=letter)
            width, height = letter
            
            # Apply design theme
            PDFService._apply_design_theme(c, design_theme)
            
            # Add salon name
            if salon_name:
                c.setFont("Helvetica-Bold", 24)
                c.drawCentredString(width / 2, height - 1 * inch, salon_name)
            
            # Add title
            c.setFont("Helvetica-Bold", 20)
            c.drawCentredString(width / 2, height - 1.5 * inch, "GIFT CARD")
            
            # Add recipient name
            if recipient_name:
                c.setFont("Helvetica", 14)
                c.drawCentredString(width / 2, height - 2.2 * inch, f"For: {recipient_name}")
            
            # Add amount
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(width / 2, height - 3 * inch, f"₦{amount:,.2f}")
            
            # Add card number
            c.setFont("Helvetica", 12)
            c.drawCentredString(width / 2, height - 3.7 * inch, f"Card Number: {card_number}")
            
            # Add expiration date
            if expires_at:
                c.setFont("Helvetica", 10)
                exp_date = expires_at.strftime("%B %d, %Y")
                c.drawCentredString(width / 2, height - 4.2 * inch, f"Expires: {exp_date}")
            
            # Add message
            if message:
                c.setFont("Helvetica-Oblique", 11)
                c.drawCentredString(width / 2, height - 4.8 * inch, f'"{message}"')
            
            # Add QR code if provided
            if qr_code_data:
                try:
                    # Extract base64 data from data URL
                    if "base64," in qr_code_data:
                        base64_data = qr_code_data.split("base64,")[1]
                        import base64
                        qr_bytes = base64.b64decode(base64_data)
                        
                        # Save QR code temporarily
                        qr_buffer = BytesIO(qr_bytes)
                        
                        # Draw QR code on PDF
                        qr_x = width / 2 - 0.75 * inch
                        qr_y = height - 6.5 * inch
                        c.drawImage(qr_buffer, qr_x, qr_y, width=1.5 * inch, height=1.5 * inch)
                except Exception as e:
                    pass  # Skip QR code if there's an error
            
            # Add terms
            c.setFont("Helvetica", 8)
            c.drawString(0.5 * inch, 0.5 * inch, "Terms & Conditions apply. See reverse for details.")
            
            # Save PDF
            c.save()
            
            # Get PDF bytes
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            raise Exception(f"Failed to generate PDF certificate: {str(e)}")

    @staticmethod
    def _generate_qr_code(data: str) -> BytesIO:
        """
        Generate QR code image
        
        Args:
            data: Data to encode
            
        Returns:
            QR code image as BytesIO
        """
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            img_bytes = BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            return img_bytes
        except Exception as e:
            raise Exception(f"Failed to generate QR code: {str(e)}")

    @staticmethod
    def _apply_design_theme(c, theme: str):
        """
        Apply design theme to certificate
        
        Args:
            c: Canvas object
            theme: Theme name (default, christmas, birthday, valentine)
        """
        if theme == "christmas":
            # Christmas theme - red and green
            c.setFillColor(HexColor("#C41E3A"))  # Christmas red
        elif theme == "birthday":
            # Birthday theme - colorful
            c.setFillColor(HexColor("#FF6B6B"))  # Bright red
        elif theme == "valentine":
            # Valentine theme - pink and red
            c.setFillColor(HexColor("#FF1493"))  # Deep pink
        else:
            # Default theme
            c.setFillColor(HexColor("#000000"))  # Black
