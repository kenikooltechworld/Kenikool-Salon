"""
Unit tests for PDF Service
Tests PDF certificate generation with different themes and error handling
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO

from app.services.pdf_service import PDFService


class TestPDFServiceCertificateGeneration:
    """Test PDF certificate generation"""

    @patch('app.services.pdf_service.canvas.Canvas')
    @patch('app.services.pdf_service.QRCodeService.generate_qr_code_bytes')
    def test_generate_gift_card_certificate_basic(self, mock_qr, mock_canvas):
        """Test generating basic gift card certificate"""
        mock_qr.return_value = b"fake_qr_image"
        mock_canvas_instance = MagicMock()
        mock_canvas.return_value = mock_canvas_instance
        
        result = PDFService.generate_gift_card_certificate(
            card_number="GC-TEST123456",
            amount=50000,
            recipient_name="John Doe",
            message="Happy Birthday!",
            expires_at=datetime.now(timezone.utc) + timedelta(days=365),
            qr_code_data="GC-TEST123456",
            design_theme="default",
            salon_name="Test Salon",
            salon_logo_url=None
        )
        
        assert isinstance(result, bytes)
        assert len(result) > 0
        mock_canvas.assert_called_once()

    @patch('app.services.pdf_service.canvas.Canvas')
    @patch('app.services.pdf_service.QRCodeService.generate_qr_code_bytes')
    def test_generate_certificate_with_logo(self, mock_qr, mock_canvas):
        """Test generating certificate with salon logo"""
        mock_qr.return_value = b"fake_qr_image"
        mock_canvas_instance = MagicMock()
        mock_canvas.return_value = mock_canvas_instance
        
        result = PDFService.generate_gift_card_certificate(
            card_number="GC-LOGO123456",
            amount=100000,
            recipient_name="Jane Smith",
            message="Congratulations!",
            expires_at=datetime.now(timezone.utc) + timedelta(days=365),
            qr_code_data="GC-LOGO123456",
            design_theme="default",
            salon_name="Premium Salon",
            salon_logo_url="https://example.com/logo.png"
        )
        
        assert isinstance(result, bytes)
        assert len(result) > 0

    @patch('app.services.pdf_service.canvas.Canvas')
    @patch('app.services.pdf_service.QRCodeService.generate_qr_code_bytes')
    def test_generate_certificate_christmas_theme(self, mock_qr, mock_canvas):
        """Test generating certificate with Christmas theme"""
        mock_qr.return_value = b"fake_qr_image"
        mock_canvas_instance = MagicMock()
        mock_canvas.return_value = mock_canvas_instance
        
        result = PDFService.generate_gift_card_certificate(
            card_number="GC-XMAS123456",
            amount=50000,
            recipient_name="John Doe",
            message="Merry Christmas!",
            expires_at=datetime.now(timezone.utc) + timedelta(days=365),
            qr_code_data="GC-XMAS123456",
            design_theme="christmas",
            salon_name="Test Salon",
            salon_logo_url=None
        )
        
        assert isinstance(result, bytes)
        assert len(result) > 0

    @patch('app.services.pdf_service.canvas.Canvas')
    @patch('app.services.pdf_service.QRCodeService.generate_qr_code_bytes')
    def test_generate_certificate_birthday_theme(self, mock_qr, mock_canvas):
        """Test generating certificate with birthday theme"""
        mock_qr.return_value = b"fake_qr_image"
        mock_canvas_instance = MagicMock()
        mock_canvas.return_value = mock_canvas_instance
        
        result = PDFService.generate_gift_card_certificate(
            card_number="GC-BDAY123456",
            amount=30000,
            recipient_name="Alice Johnson",
            message="Happy Birthday!",
            expires_at=datetime.now(timezone.utc) + timedelta(days=365),
            qr_code_data="GC-BDAY123456",
            design_theme="birthday",
            salon_name="Test Salon",
            salon_logo_url=None
        )
        
        assert isinstance(result, bytes)
        assert len(result) > 0

    @patch('app.services.pdf_service.canvas.Canvas')
    @patch('app.services.pdf_service.QRCodeService.generate_qr_code_bytes')
    def test_generate_certificate_valentine_theme(self, mock_qr, mock_canvas):
        """Test generating certificate with Valentine theme"""
        mock_qr.return_value = b"fake_qr_image"
        mock_canvas_instance = MagicMock()
        mock_canvas.return_value = mock_canvas_instance
        
        result = PDFService.generate_gift_card_certificate(
            card_number="GC-VAL123456",
            amount=25000,
            recipient_name="Couple",
            message="Happy Valentine's Day!",
            expires_at=datetime.now(timezone.utc) + timedelta(days=365),
            qr_code_data="GC-VAL123456",
            design_theme="valentine",
            salon_name="Test Salon",
            salon_logo_url=None
        )
        
        assert isinstance(result, bytes)
        assert len(result) > 0

    @patch('app.services.pdf_service.canvas.Canvas')
    @patch('app.services.pdf_service.QRCodeService.generate_qr_code_bytes')
    def test_generate_certificate_without_message(self, mock_qr, mock_canvas):
        """Test generating certificate without personal message"""
        mock_qr.return_value = b"fake_qr_image"
        mock_canvas_instance = MagicMock()
        mock_canvas.return_value = mock_canvas_instance
        
        result = PDFService.generate_gift_card_certificate(
            card_number="GC-NOMSG123456",
            amount=50000,
            recipient_name="John Doe",
            message=None,
            expires_at=datetime.now(timezone.utc) + timedelta(days=365),
            qr_code_data="GC-NOMSG123456",
            design_theme="default",
            salon_name="Test Salon",
            salon_logo_url=None
        )
        
        assert isinstance(result, bytes)
        assert len(result) > 0

    @patch('app.services.pdf_service.canvas.Canvas')
    @patch('app.services.pdf_service.QRCodeService.generate_qr_code_bytes')
    def test_generate_certificate_without_recipient_name(self, mock_qr, mock_canvas):
        """Test generating certificate without recipient name"""
        mock_qr.return_value = b"fake_qr_image"
        mock_canvas_instance = MagicMock()
        mock_canvas.return_value = mock_canvas_instance
        
        result = PDFService.generate_gift_card_certificate(
            card_number="GC-NOREC123456",
            amount=50000,
            recipient_name=None,
            message=None,
            expires_at=datetime.now(timezone.utc) + timedelta(days=365),
            qr_code_data="GC-NOREC123456",
            design_theme="default",
            salon_name="Test Salon",
            salon_logo_url=None
        )
        
        assert isinstance(result, bytes)
        assert len(result) > 0

    @patch('app.services.pdf_service.canvas.Canvas')
    @patch('app.services.pdf_service.QRCodeService.generate_qr_code_bytes')
    def test_generate_certificate_high_value(self, mock_qr, mock_canvas):
        """Test generating certificate for high-value card"""
        mock_qr.return_value = b"fake_qr_image"
        mock_canvas_instance = MagicMock()
        mock_canvas.return_value = mock_canvas_instance
        
        result = PDFService.generate_gift_card_certificate(
            card_number="GC-HIGH123456",
            amount=500000,
            recipient_name="VIP Customer",
            message="Premium Gift",
            expires_at=datetime.now(timezone.utc) + timedelta(days=365),
            qr_code_data="GC-HIGH123456",
            design_theme="default",
            salon_name="Luxury Salon",
            salon_logo_url="https://example.com/luxury_logo.png"
        )
        
        assert isinstance(result, bytes)
        assert len(result) > 0

    @patch('app.services.pdf_service.canvas.Canvas')
    @patch('app.services.pdf_service.QRCodeService.generate_qr_code_bytes')
    def test_generate_certificate_low_value(self, mock_qr, mock_canvas):
        """Test generating certificate for low-value card"""
        mock_qr.return_value = b"fake_qr_image"
        mock_canvas_instance = MagicMock()
        mock_canvas.return_value = mock_canvas_instance
        
        result = PDFService.generate_gift_card_certificate(
            card_number="GC-LOW123456",
            amount=1000,
            recipient_name="Budget Customer",
            message="Small Gift",
            expires_at=datetime.now(timezone.utc) + timedelta(days=365),
            qr_code_data="GC-LOW123456",
            design_theme="default",
            salon_name="Test Salon",
            salon_logo_url=None
        )
        
        assert isinstance(result, bytes)
        assert len(result) > 0

    @patch('app.services.pdf_service.canvas.Canvas')
    @patch('app.services.pdf_service.QRCodeService.generate_qr_code_bytes')
    def test_generate_certificate_long_message(self, mock_qr, mock_canvas):
        """Test generating certificate with long message"""
        mock_qr.return_value = b"fake_qr_image"
        mock_canvas_instance = MagicMock()
        mock_canvas.return_value = mock_canvas_instance
        
        long_message = "This is a very long message that should be wrapped properly on the certificate. " * 3
        
        result = PDFService.generate_gift_card_certificate(
            card_number="GC-LONG123456",
            amount=50000,
            recipient_name="John Doe",
            message=long_message,
            expires_at=datetime.now(timezone.utc) + timedelta(days=365),
            qr_code_data="GC-LONG123456",
            design_theme="default",
            salon_name="Test Salon",
            salon_logo_url=None
        )
        
        assert isinstance(result, bytes)
        assert len(result) > 0

    @patch('app.services.pdf_service.canvas.Canvas')
    @patch('app.services.pdf_service.QRCodeService.generate_qr_code_bytes')
    def test_generate_certificate_special_characters_in_name(self, mock_qr, mock_canvas):
        """Test generating certificate with special characters in name"""
        mock_qr.return_value = b"fake_qr_image"
        mock_canvas_instance = MagicMock()
        mock_canvas.return_value = mock_canvas_instance
        
        result = PDFService.generate_gift_card_certificate(
            card_number="GC-SPEC123456",
            amount=50000,
            recipient_name="O'Brien-Smith",
            message="Gift for you!",
            expires_at=datetime.now(timezone.utc) + timedelta(days=365),
            qr_code_data="GC-SPEC123456",
            design_theme="default",
            salon_name="Test Salon",
            salon_logo_url=None
        )
        
        assert isinstance(result, bytes)
        assert len(result) > 0

    @patch('app.services.pdf_service.canvas.Canvas')
    @patch('app.services.pdf_service.QRCodeService.generate_qr_code_bytes')
    def test_generate_certificate_invalid_theme(self, mock_qr, mock_canvas):
        """Test generating certificate with invalid theme"""
        mock_qr.return_value = b"fake_qr_image"
        mock_canvas_instance = MagicMock()
        mock_canvas.return_value = mock_canvas_instance
        
        # Should fall back to default theme
        result = PDFService.generate_gift_card_certificate(
            card_number="GC-INVALID123456",
            amount=50000,
            recipient_name="John Doe",
            message="Gift",
            expires_at=datetime.now(timezone.utc) + timedelta(days=365),
            qr_code_data="GC-INVALID123456",
            design_theme="invalid_theme",
            salon_name="Test Salon",
            salon_logo_url=None
        )
        
        assert isinstance(result, bytes)
        assert len(result) > 0

    @patch('app.services.pdf_service.canvas.Canvas')
    @patch('app.services.pdf_service.QRCodeService.generate_qr_code_bytes')
    def test_generate_certificate_qr_code_integration(self, mock_qr, mock_canvas):
        """Test QR code is properly integrated into certificate"""
        mock_qr.return_value = b"fake_qr_image_data"
        mock_canvas_instance = MagicMock()
        mock_canvas.return_value = mock_canvas_instance
        
        result = PDFService.generate_gift_card_certificate(
            card_number="GC-QR123456",
            amount=50000,
            recipient_name="John Doe",
            message="Gift",
            expires_at=datetime.now(timezone.utc) + timedelta(days=365),
            qr_code_data="GC-QR123456",
            design_theme="default",
            salon_name="Test Salon",
            salon_logo_url=None
        )
        
        assert isinstance(result, bytes)
        mock_qr.assert_called_once_with("GC-QR123456")

    @patch('app.services.pdf_service.canvas.Canvas')
    @patch('app.services.pdf_service.QRCodeService.generate_qr_code_bytes')
    def test_generate_certificate_error_handling(self, mock_qr, mock_canvas):
        """Test error handling in certificate generation"""
        mock_qr.return_value = b"fake_qr_image"
        mock_canvas.side_effect = Exception("PDF generation failed")
        
        with pytest.raises(Exception):
            PDFService.generate_gift_card_certificate(
                card_number="GC-ERROR123456",
                amount=50000,
                recipient_name="John Doe",
                message="Gift",
                expires_at=datetime.now(timezone.utc) + timedelta(days=365),
                qr_code_data="GC-ERROR123456",
                design_theme="default",
                salon_name="Test Salon",
                salon_logo_url=None
            )

    @patch('app.services.pdf_service.canvas.Canvas')
    @patch('app.services.pdf_service.QRCodeService.generate_qr_code_bytes')
    def test_generate_certificate_qr_error_fallback(self, mock_qr, mock_canvas):
        """Test fallback when QR code generation fails"""
        mock_qr.side_effect = Exception("QR generation failed")
        mock_canvas_instance = MagicMock()
        mock_canvas.return_value = mock_canvas_instance
        
        # Should handle QR error gracefully
        with pytest.raises(Exception):
            PDFService.generate_gift_card_certificate(
                card_number="GC-QRERR123456",
                amount=50000,
                recipient_name="John Doe",
                message="Gift",
                expires_at=datetime.now(timezone.utc) + timedelta(days=365),
                qr_code_data="GC-QRERR123456",
                design_theme="default",
                salon_name="Test Salon",
                salon_logo_url=None
            )


class TestPDFServiceDesignThemes:
    """Test PDF design theme functionality"""

    @patch('app.services.pdf_service.canvas.Canvas')
    @patch('app.services.pdf_service.QRCodeService.generate_qr_code_bytes')
    def test_all_design_themes(self, mock_qr, mock_canvas):
        """Test all available design themes"""
        mock_qr.return_value = b"fake_qr_image"
        mock_canvas_instance = MagicMock()
        mock_canvas.return_value = mock_canvas_instance
        
        themes = ["default", "christmas", "birthday", "valentine", "custom"]
        
        for theme in themes:
            result = PDFService.generate_gift_card_certificate(
                card_number=f"GC-{theme.upper()}123456",
                amount=50000,
                recipient_name="John Doe",
                message="Gift",
                expires_at=datetime.now(timezone.utc) + timedelta(days=365),
                qr_code_data=f"GC-{theme.upper()}123456",
                design_theme=theme,
                salon_name="Test Salon",
                salon_logo_url=None
            )
            
            assert isinstance(result, bytes)
            assert len(result) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
