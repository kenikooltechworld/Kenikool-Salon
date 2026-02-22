"""
Unit tests for PDF Service - Phase 8
Tests PDF certificate generation for gift cards
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, Mock, MagicMock
from io import BytesIO

from app.services.pdf_service import PDFService


class TestPDFCertificateGeneration:
    """Test PDF certificate generation"""

    def test_generate_gift_card_certificate_basic(self):
        """Test generating basic gift card certificate"""
        pdf_bytes = PDFService.generate_gift_card_certificate(
            card_number="GC-TEST123456",
            amount=50000,
            recipient_name="John Doe",
            message="Happy Birthday!",
            expires_at=datetime.now(timezone.utc) + timedelta(days=365),
            qr_code_data="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
            design_theme="default",
            salon_name="Kenikool Salon",
            salon_logo_url=None
        )
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        # PDF files start with %PDF
        assert pdf_bytes[:4] == b'%PDF'

    def test_generate_gift_card_certificate_with_logo(self):
        """Test generating certificate with salon logo"""
        pdf_bytes = PDFService.generate_gift_card_certificate(
            card_number="GC-TEST123456",
            amount=50000,
            recipient_name="Jane Smith",
            message=None,
            expires_at=datetime.now(timezone.utc) + timedelta(days=365),
            qr_code_data="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
            design_theme="default",
            salon_name="Kenikool Salon",
            salon_logo_url="https://example.com/logo.png"
        )
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes[:4] == b'%PDF'

    def test_generate_gift_card_certificate_different_themes(self):
        """Test generating certificates with different themes"""
        themes = ["default", "christmas", "birthday", "valentine"]
        
        for theme in themes:
            pdf_bytes = PDFService.generate_gift_card_certificate(
                card_number="GC-TEST123456",
                amount=50000,
                recipient_name="John Doe",
                message="Happy Birthday!",
                expires_at=datetime.now(timezone.utc) + timedelta(days=365),
                qr_code_data="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
                design_theme=theme,
                salon_name="Kenikool Salon",
                salon_logo_url=None
            )
            
            assert isinstance(pdf_bytes, bytes)
            assert len(pdf_bytes) > 0
            assert pdf_bytes[:4] == b'%PDF'

    def test_generate_gift_card_certificate_no_message(self):
        """Test generating certificate without message"""
        pdf_bytes = PDFService.generate_gift_card_certificate(
            card_number="GC-TEST123456",
            amount=50000,
            recipient_name="John Doe",
            message=None,
            expires_at=datetime.now(timezone.utc) + timedelta(days=365),
            qr_code_data="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
            design_theme="default",
            salon_name="Kenikool Salon",
            salon_logo_url=None
        )
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0

    def test_generate_gift_card_certificate_no_recipient(self):
        """Test generating certificate without recipient name"""
        pdf_bytes = PDFService.generate_gift_card_certificate(
            card_number="GC-TEST123456",
            amount=50000,
            recipient_name=None,
            message="Gift Card",
            expires_at=datetime.now(timezone.utc) + timedelta(days=365),
            qr_code_data="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
            design_theme="default",
            salon_name="Kenikool Salon",
            salon_logo_url=None
        )
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0

    def test_generate_gift_card_certificate_high_value(self):
        """Test generating certificate for high-value card"""
        pdf_bytes = PDFService.generate_gift_card_certificate(
            card_number="GC-PREMIUM123456",
            amount=500000,
            recipient_name="VIP Customer",
            message="Premium Gift Card",
            expires_at=datetime.now(timezone.utc) + timedelta(days=730),
            qr_code_data="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
            design_theme="default",
            salon_name="Kenikool Salon",
            salon_logo_url=None
        )
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0

    def test_generate_gift_card_certificate_long_message(self):
        """Test generating certificate with long message"""
        long_message = "This is a very long congratulatory message that spans multiple lines and contains lots of text to test the PDF generation with extended content."
        
        pdf_bytes = PDFService.generate_gift_card_certificate(
            card_number="GC-TEST123456",
            amount=50000,
            recipient_name="John Doe",
            message=long_message,
            expires_at=datetime.now(timezone.utc) + timedelta(days=365),
            qr_code_data="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
            design_theme="default",
            salon_name="Kenikool Salon",
            salon_logo_url=None
        )
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0

    def test_generate_gift_card_certificate_special_characters(self):
        """Test generating certificate with special characters"""
        pdf_bytes = PDFService.generate_gift_card_certificate(
            card_number="GC-TEST123456",
            amount=50000,
            recipient_name="José García",
            message="¡Felicidades! 🎉",
            expires_at=datetime.now(timezone.utc) + timedelta(days=365),
            qr_code_data="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
            design_theme="default",
            salon_name="Kenikool Salon",
            salon_logo_url=None
        )
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0


class TestQRCodeIntegration:
    """Test QR code integration in PDF"""

    def test_generate_qr_code_for_pdf(self):
        """Test generating QR code for PDF embedding"""
        data = "GC-TEST123456"
        qr_code = PDFService._generate_qr_code(data)
        
        assert isinstance(qr_code, BytesIO)
        assert qr_code.getbuffer().nbytes > 0

    def test_qr_code_in_certificate(self):
        """Test QR code is properly embedded in certificate"""
        pdf_bytes = PDFService.generate_gift_card_certificate(
            card_number="GC-TEST123456",
            amount=50000,
            recipient_name="John Doe",
            message="Happy Birthday!",
            expires_at=datetime.now(timezone.utc) + timedelta(days=365),
            qr_code_data="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
            design_theme="default",
            salon_name="Kenikool Salon",
            salon_logo_url=None
        )
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0


class TestDesignThemes:
    """Test design theme application"""

    def test_apply_design_theme_default(self):
        """Test applying default theme"""
        from reportlab.pdfgen import canvas
        from io import BytesIO
        
        buffer = BytesIO()
        c = canvas.Canvas(buffer)
        
        # Should not raise an error
        PDFService._apply_design_theme(c, "default")
        c.save()
        
        assert buffer.getbuffer().nbytes > 0

    def test_apply_design_theme_christmas(self):
        """Test applying Christmas theme"""
        from reportlab.pdfgen import canvas
        from io import BytesIO
        
        buffer = BytesIO()
        c = canvas.Canvas(buffer)
        
        PDFService._apply_design_theme(c, "christmas")
        c.save()
        
        assert buffer.getbuffer().nbytes > 0

    def test_apply_design_theme_birthday(self):
        """Test applying birthday theme"""
        from reportlab.pdfgen import canvas
        from io import BytesIO
        
        buffer = BytesIO()
        c = canvas.Canvas(buffer)
        
        PDFService._apply_design_theme(c, "birthday")
        c.save()
        
        assert buffer.getbuffer().nbytes > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
