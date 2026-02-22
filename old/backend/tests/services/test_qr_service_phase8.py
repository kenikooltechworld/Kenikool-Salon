"""
Unit tests for QR Code Service - Phase 8
Tests QR code generation with multiple output formats
"""

import pytest
import base64
from io import BytesIO
from unittest.mock import patch, Mock

from app.services.qr_service import QRCodeService


class TestQRCodeGeneration:
    """Test QR code generation"""

    def test_generate_qr_code_base64(self):
        """Test generating QR code as base64 data URL"""
        data = "GC-TEST123456"
        result = QRCodeService.generate_qr_code(data)
        
        assert result is not None
        assert result.startswith("data:image/png;base64,")
        # Verify it's valid base64
        base64_part = result.split(",")[1]
        decoded = base64.b64decode(base64_part)
        assert len(decoded) > 0

    def test_generate_qr_code_bytes(self):
        """Test generating QR code as bytes"""
        data = "GC-TEST123456"
        result = QRCodeService.generate_qr_code_bytes(data)
        
        assert isinstance(result, bytes)
        assert len(result) > 0
        # PNG files start with specific magic bytes
        assert result[:8] == b'\x89PNG\r\n\x1a\n'

    def test_generate_qr_code_different_sizes(self):
        """Test generating QR codes with different sizes"""
        data = "GC-TEST123456"
        
        small = QRCodeService.generate_qr_code_bytes(data, size=100)
        large = QRCodeService.generate_qr_code_bytes(data, size=400)
        
        assert len(small) > 0
        assert len(large) > 0
        # Larger QR codes should generally produce larger files
        assert len(large) >= len(small)

    def test_generate_qr_code_with_special_characters(self):
        """Test generating QR code with special characters"""
        data = "GC-TEST123456!@#$%^&*()"
        result = QRCodeService.generate_qr_code(data)
        
        assert result is not None
        assert result.startswith("data:image/png;base64,")

    def test_generate_qr_code_with_long_data(self):
        """Test generating QR code with long data"""
        data = "GC-" + "X" * 1000
        result = QRCodeService.generate_qr_code(data)
        
        assert result is not None
        assert result.startswith("data:image/png;base64,")

    def test_generate_qr_code_empty_data(self):
        """Test generating QR code with empty data"""
        data = ""
        result = QRCodeService.generate_qr_code(data)
        
        # Should still generate a QR code, even if empty
        assert result is not None
        assert result.startswith("data:image/png;base64,")

    def test_generate_qr_code_unicode_data(self):
        """Test generating QR code with unicode data"""
        data = "GC-TEST-日本語-العربية"
        result = QRCodeService.generate_qr_code(data)
        
        assert result is not None
        assert result.startswith("data:image/png;base64,")

    def test_generate_qr_code_url_format(self):
        """Test generating QR code for URL"""
        url = "https://example.com/gift-cards/GC-TEST123456"
        result = QRCodeService.generate_qr_code(url)
        
        assert result is not None
        assert result.startswith("data:image/png;base64,")

    def test_generate_qr_code_consistency(self):
        """Test that same data generates same QR code"""
        data = "GC-TEST123456"
        result1 = QRCodeService.generate_qr_code_bytes(data)
        result2 = QRCodeService.generate_qr_code_bytes(data)
        
        # Same data should produce identical QR codes
        assert result1 == result2

    def test_generate_qr_code_different_data(self):
        """Test that different data generates different QR codes"""
        result1 = QRCodeService.generate_qr_code_bytes("GC-TEST123456")
        result2 = QRCodeService.generate_qr_code_bytes("GC-TEST654321")
        
        # Different data should produce different QR codes
        assert result1 != result2


class TestQRCodeIntegration:
    """Test QR code integration scenarios"""

    def test_qr_code_for_gift_card_number(self):
        """Test generating QR code for gift card number"""
        card_number = "GC-SALON-2024-001"
        qr_code = QRCodeService.generate_qr_code(card_number)
        
        assert qr_code is not None
        assert "data:image/png;base64," in qr_code

    def test_qr_code_for_redemption_link(self):
        """Test generating QR code for redemption link"""
        redemption_url = "https://salon.example.com/redeem/GC-TEST123456"
        qr_code = QRCodeService.generate_qr_code(redemption_url)
        
        assert qr_code is not None
        assert "data:image/png;base64," in qr_code

    def test_qr_code_for_balance_check(self):
        """Test generating QR code for balance check"""
        balance_url = "https://salon.example.com/balance?card=GC-TEST123456"
        qr_code = QRCodeService.generate_qr_code(balance_url)
        
        assert qr_code is not None
        assert "data:image/png;base64," in qr_code

    def test_qr_code_bytes_to_base64_conversion(self):
        """Test converting QR code bytes to base64"""
        data = "GC-TEST123456"
        qr_bytes = QRCodeService.generate_qr_code_bytes(data)
        
        # Convert to base64
        base64_encoded = base64.b64encode(qr_bytes).decode()
        
        # Should be valid base64
        assert len(base64_encoded) > 0
        # Should be decodable
        decoded = base64.b64decode(base64_encoded)
        assert decoded == qr_bytes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
