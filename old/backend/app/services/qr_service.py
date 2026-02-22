"""
QR Code Service for Gift Cards
Generates QR codes for gift card numbers and redemption links
"""

import qrcode
from io import BytesIO
import base64


class QRCodeService:
    """Service for generating QR codes"""

    @staticmethod
    def generate_qr_code(data: str, size: int = 200) -> str:
        """
        Generate QR code and return as base64 data URL
        
        Args:
            data: Data to encode in QR code
            size: Size of QR code in pixels
            
        Returns:
            Base64 encoded data URL for QR code image
        """
        try:
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to bytes
            img_bytes = BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            # Encode to base64
            base64_encoded = base64.b64encode(img_bytes.getvalue()).decode()
            
            # Return as data URL
            return f"data:image/png;base64,{base64_encoded}"
        except Exception as e:
            raise Exception(f"Failed to generate QR code: {str(e)}")

    @staticmethod
    def generate_qr_code_bytes(data: str, size: int = 200) -> bytes:
        """
        Generate QR code and return as bytes
        
        Args:
            data: Data to encode in QR code
            size: Size of QR code in pixels
            
        Returns:
            PNG image bytes
        """
        try:
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to bytes
            img_bytes = BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            return img_bytes.getvalue()
        except Exception as e:
            raise Exception(f"Failed to generate QR code: {str(e)}")
