"""
Unit tests for QR Code Service
Tests QR code generation with different formats and error handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import base64
from io import BytesIO

from app.services.qr_service import QRCodeService


class TestQRCodeServiceGeneration:
    """Test QR code generation functionality"""

    @patch('app.services.qr_service.qrcode.QRCode')
    def test_generate_qr_code_base64(self, mock_qr_class):
        """Test generating QR code as base64 data URL"""
        mock_qr = MagicMock()
        mock_qr_class.return_value = mock_qr
        
        # Mock the image generation
        mock_img = MagicMock()
        mock_qr.make_image.return_value = mock_img
        
        result = QRCodeService.generate_qr_code("GC-TEST123456")
        
        assert result.startswith("data:image/png;base64,")
        assert len(result) > 50
        mock_qr.add_data.assert_called_once_with("GC-TEST123456")
        mock_qr.make.assert_called_once()

    @patch('app.services.qr_service.qrcode.QRCode')
    def test_generate_qr_code_bytes(self, mock_qr_class):
        """Test generating QR code as bytes"""
        mock_qr = MagicMock()
        mock_qr_class.return_value = mock_qr
        
        mock_img = MagicMock()
        mock_qr.make_image.return_value = mock_img
        
        result = QRCodeService.generate_qr_code_bytes("GC-TEST123456")
        
        assert isinstance(result, bytes)
        assert len(result) > 0
        mock_qr.add_data.assert_called_once_with("GC-TEST123456")

    @patch('app.services.qr_service.qrcode.QRCode')
    def test_generate_qr_code_custom_size(self, mock_qr_class):
        """Test generating QR code with custom size"""
        mock_qr = MagicMock()
        mock_qr_class.return_value = mock_qr
        
        mock_img = MagicMock()
        mock_qr.make_image.return_value = mock_img
        
        result = QRCodeService.generate_qr_code("GC-TEST123456", size=300)
        
        assert result.startswith("data:image/png;base64,")
        mock_qr_class.assert_called_once()

    @patch('app.services.qr_service.qrcode.QRCode')
    def test_generate_qr_code_empty_data(self, mock_qr_class):
        """Test generating QR code with empty data"""
        mock_qr = MagicMock()
        mock_qr_class.return_value = mock_qr
        
        with pytest.raises(ValueError):
            QRCodeService.generate_qr_code("")

    @patch('app.services.qr_service.qrcode.QRCode')
    def test_generate_qr_code_long_data(self, mock_qr_class):
        """Test generating QR code with long data"""
        mock_qr = MagicMock()
        mock_qr_class.return_value = mock_qr
        
        mock_img = MagicMock()
        mock_qr.make_image.return_value = mock_img
        
        long_data = "GC-" + "X" * 1000
        result = QRCodeService.generate_qr_code(long_data)
        
        assert result.startswith("data:image/png;base64,")
        mock_qr.add_data.assert_called_once_with(long_data)

    @patch('app.services.qr_service.qrcode.QRCode')
    def test_generate_qr_code_special_characters(self, mock_qr_class):
        """Test generating QR code with special characters"""
        mock_qr = MagicMock()
        mock_qr_class.return_value = mock_qr
        
        mock_img = MagicMock()
        mock_qr.make_image.return_value = mock_img
        
        special_data = "GC-TEST!@#$%^&*()"
        result = QRCodeService.generate_qr_code(special_data)
        
        assert result.startswith("data:image/png;base64,")
        mock_qr.add_data.assert_called_once_with(special_data)

    @patch('app.services.qr_service.qrcode.QRCode')
    def test_generate_qr_code_unicode_data(self, mock_qr_class):
        """Test generating QR code with unicode data"""
        mock_qr = MagicMock()
        mock_qr_class.return_value = mock_qr
        
        mock_img = MagicMock()
        mock_qr.make_image.return_value = mock_img
        
        unicode_data = "GC-TEST-日本語"
        result = QRCodeService.generate_qr_code(unicode_data)
        
        assert result.startswith("data:image/png;base64,")
        mock_qr.add_data.assert_called_once_with(unicode_data)

    @patch('app.services.qr_service.qrcode.QRCode')
    def test_generate_qr_code_error_handling(self, mock_qr_class):
        """Test QR code generation error handling"""
        mock_qr_class.side_effect = Exception("QR generation failed")
        
        with pytest.raises(Exception):
            QRCodeService.generate_qr_code("GC-TEST123456")

    @patch('app.services.qr_service.qrcode.QRCode')
    def test_generate_qr_code_image_save_error(self, mock_qr_class):
        """Test handling of image save errors"""
        mock_qr = MagicMock()
        mock_qr_class.return_value = mock_qr
        
        mock_img = MagicMock()
        mock_img.save.side_effect = IOError("Cannot save image")
        mock_qr.make_image.return_value = mock_img
        
        with pytest.raises(IOError):
            QRCodeService.generate_qr_code("GC-TEST123456")

    @patch('app.services.qr_service.qrcode.QRCode')
    def test_generate_qr_code_base64_encoding(self, mock_qr_class):
        """Test base64 encoding of QR code"""
        mock_qr = MagicMock()
        mock_qr_class.return_value = mock_qr
        
        mock_img = MagicMock()
        mock_qr.make_image.return_value = mock_img
        
        result = QRCodeService.generate_qr_code("GC-TEST123456")
        
        # Extract base64 part
        base64_part = result.split(",")[1]
        
        # Verify it's valid base64
        try:
            decoded = base64.b64decode(base64_part)
            assert len(decoded) > 0
        except Exception:
            pytest.fail("Invalid base64 encoding")

    @patch('app.services.qr_service.qrcode.QRCode')
    def test_generate_qr_code_multiple_calls(self, mock_qr_class):
        """Test generating multiple QR codes"""
        mock_qr = MagicMock()
        mock_qr_class.return_value = mock_qr
        
        mock_img = MagicMock()
        mock_qr.make_image.return_value = mock_img
        
        result1 = QRCodeService.generate_qr_code("GC-TEST1")
        result2 = QRCodeService.generate_qr_code("GC-TEST2")
        
        assert result1.startswith("data:image/png;base64,")
        assert result2.startswith("data:image/png;base64,")
        assert mock_qr.add_data.call_count == 2


class TestQRCodeServiceIntegration:
    """Test QR code service integration"""

    @patch('app.services.qr_service.qrcode.QRCode')
    def test_qr_code_scannable_format(self, mock_qr_class):
        """Test that generated QR code is in scannable format"""
        mock_qr = MagicMock()
        mock_qr_class.return_value = mock_qr
        
        mock_img = MagicMock()
        mock_qr.make_image.return_value = mock_img
        
        card_number = "GC-SCAN123456"
        result = QRCodeService.generate_qr_code(card_number)
        
        # Verify format
        assert "data:image/png;base64," in result
        assert len(result) > 100

    @patch('app.services.qr_service.qrcode.QRCode')
    def test_qr_code_for_certificate(self, mock_qr_class):
        """Test QR code generation for certificate embedding"""
        mock_qr = MagicMock()
        mock_qr_class.return_value = mock_qr
        
        mock_img = MagicMock()
        mock_qr.make_image.return_value = mock_img
        
        card_number = "GC-CERT123456"
        result = QRCodeService.generate_qr_code(card_number, size=200)
        
        assert result.startswith("data:image/png;base64,")
        mock_qr_class.assert_called_once()

    @patch('app.services.qr_service.qrcode.QRCode')
    def test_qr_code_for_email(self, mock_qr_class):
        """Test QR code generation for email embedding"""
        mock_qr = MagicMock()
        mock_qr_class.return_value = mock_qr
        
        mock_img = MagicMock()
        mock_qr.make_image.return_value = mock_img
        
        card_number = "GC-EMAIL123456"
        result = QRCodeService.generate_qr_code(card_number, size=150)
        
        assert result.startswith("data:image/png;base64,")
        assert len(result) > 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
