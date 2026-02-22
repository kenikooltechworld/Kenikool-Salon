"""Unit tests for Multi-Factor Authentication (MFA)."""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from urllib.parse import unquote
from app.services.mfa_service import MFAService


class TestMultiFactorAuthentication:
    """Test MFA functionality."""

    @pytest.fixture
    def mfa_service(self):
        """Create MFA service."""
        return MFAService()

    def test_totp_secret_generation(self, mfa_service):
        """Test TOTP secret generation."""
        secret = mfa_service.generate_totp_secret()

        assert secret is not None
        assert len(secret) > 0
        assert isinstance(secret, str)

    def test_totp_uri_generation(self, mfa_service):
        """Test TOTP URI generation."""
        secret = mfa_service.generate_totp_secret()
        email = "user@example.com"

        uri = mfa_service.get_totp_uri(secret, email)

        assert uri is not None
        # Email is URL-encoded in the URI, so decode it for comparison
        assert unquote(uri).find(email) >= 0 or email in uri
        assert "otpauth://" in uri
        assert secret in uri

    def test_qr_code_generation(self, mfa_service):
        """Test QR code generation."""
        secret = mfa_service.generate_totp_secret()
        email = "user@example.com"
        uri = mfa_service.get_totp_uri(secret, email)

        qr_code = mfa_service.generate_qr_code(uri)

        assert qr_code is not None
        assert "data:image/png;base64," in qr_code

    def test_totp_code_verification(self, mfa_service):
        """Test TOTP code verification."""
        secret = mfa_service.generate_totp_secret()

        # Generate a valid code
        import pyotp
        totp = pyotp.TOTP(secret)
        valid_code = totp.now()

        # Verify valid code
        assert mfa_service.verify_totp_code(secret, valid_code) is True

        # Verify invalid code
        invalid_code = "000000"
        assert mfa_service.verify_totp_code(secret, invalid_code) is False

    def test_backup_code_generation(self, mfa_service):
        """Test backup code generation."""
        codes = mfa_service.generate_backup_codes(count=10)

        assert len(codes) == 10
        assert all(isinstance(code, str) for code in codes)
        assert all(len(code) > 0 for code in codes)
        # All codes should be unique
        assert len(set(codes)) == 10

    def test_backup_code_hashing(self, mfa_service):
        """Test backup code hashing."""
        code = "ABCD1234"

        hashed = mfa_service.hash_backup_code(code)

        assert hashed != code
        assert len(hashed) > 0

    def test_backup_code_verification(self, mfa_service):
        """Test backup code verification."""
        code = "ABCD1234"
        hashed = mfa_service.hash_backup_code(code)

        # Verify correct code
        assert mfa_service.verify_backup_code(code, hashed) is True

        # Verify incorrect code
        wrong_code = "WRONG1234"
        assert mfa_service.verify_backup_code(wrong_code, hashed) is False

    def test_totp_setup(self, mfa_service):
        """Test TOTP setup."""
        email = "user@example.com"

        secret, qr_code, backup_codes = mfa_service.setup_totp(email)

        assert secret is not None
        assert len(secret) > 0
        assert qr_code is not None
        assert "data:image/png;base64," in qr_code
        assert len(backup_codes) == 10

    def test_sms_setup(self, mfa_service):
        """Test SMS OTP setup."""
        phone = "+1234567890"

        otp_code = mfa_service.setup_sms(phone)

        assert otp_code is not None
        assert len(otp_code) == 6
        assert otp_code.isdigit()

    def test_sms_code_verification(self, mfa_service):
        """Test SMS OTP code verification."""
        provided_code = "123456"
        expected_code = "123456"

        # Verify matching codes
        assert mfa_service.verify_sms_code(provided_code, expected_code) is True

        # Verify non-matching codes
        wrong_code = "654321"
        assert mfa_service.verify_sms_code(wrong_code, expected_code) is False

    def test_sms_otp_sending(self, mfa_service):
        """Test SMS OTP sending."""
        phone = "+1234567890"
        code = "123456"

        result = mfa_service.send_sms_otp(phone, code)

        assert result is True

    @given(
        email=st.emails(),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_totp_setup_with_various_emails(self, mfa_service, email):
        """Test TOTP setup with various email addresses."""
        secret, qr_code, backup_codes = mfa_service.setup_totp(email)

        assert secret is not None
        assert qr_code is not None
        assert len(backup_codes) == 10

    @given(
        count=st.integers(min_value=1, max_value=20),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_backup_code_generation_various_counts(self, mfa_service, count):
        """Test backup code generation with various counts."""
        codes = mfa_service.generate_backup_codes(count=count)

        assert len(codes) == count
        assert len(set(codes)) == count  # All unique

    def test_multiple_totp_secrets_unique(self, mfa_service):
        """Test that multiple TOTP secrets are unique."""
        secrets = [mfa_service.generate_totp_secret() for _ in range(10)]

        # All secrets should be unique
        assert len(set(secrets)) == 10

    def test_totp_code_time_window(self, mfa_service):
        """Test TOTP code verification with time window."""
        secret = mfa_service.generate_totp_secret()

        import pyotp
        import time
        totp = pyotp.TOTP(secret)

        # Get current code
        current_code = totp.now()

        # Verify current code works
        assert mfa_service.verify_totp_code(secret, current_code) is True

        # Wait for next time window
        time.sleep(1)

        # Current code should still work (within time window)
        assert mfa_service.verify_totp_code(secret, current_code) is True
