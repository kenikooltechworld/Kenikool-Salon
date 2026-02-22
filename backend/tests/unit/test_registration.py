"""Unit tests for registration service."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from app.services.registration_service import RegistrationService
from app.models.temp_registration import TempRegistration
from app.models.tenant import Tenant
from app.models.user import User
from app.models.role import Role
from app.config import Settings


@pytest.fixture
def settings():
    """Create test settings."""
    return Settings()


@pytest.fixture
def registration_service(settings):
    """Create registration service instance."""
    return RegistrationService(settings)
    """Tests for registration data validation."""

    def test_valid_registration_data(self, registration_service):
        """Test validation of valid registration data."""
        data = {
            "salon_name": "Acme Salon",
            "owner_name": "John Doe",
            "email": "john@example.com",
            "phone": "+234 123 456 7890",
            "password": "SecurePass123!",
            "address": "123 Main St, Lagos",
        }
        is_valid, error = registration_service.validate_registration_data(data)
        assert is_valid is True
        assert error is None

    def test_invalid_email(self, registration_service):
        """Test validation with invalid email."""
        data = {
            "salon_name": "Acme Salon",
            "owner_name": "John Doe",
            "email": "invalid-email",
            "phone": "+234 123 456 7890",
            "password": "SecurePass123!",
            "address": "123 Main St, Lagos",
        }
        is_valid, error = registration_service.validate_registration_data(data)
        assert is_valid is False
        assert "Invalid email format" in error

    def test_invalid_phone(self, registration_service):
        """Test validation with invalid phone."""
        data = {
            "salon_name": "Acme Salon",
            "owner_name": "John Doe",
            "email": "john@example.com",
            "phone": "123",
            "password": "SecurePass123!",
            "address": "123 Main St, Lagos",
        }
        is_valid, error = registration_service.validate_registration_data(data)
        assert is_valid is False
        assert "Invalid phone format" in error

    def test_short_salon_name(self, registration_service):
        """Test validation with short salon name."""
        data = {
            "salon_name": "AB",
            "owner_name": "John Doe",
            "email": "john@example.com",
            "phone": "+234 123 456 7890",
            "password": "SecurePass123!",
            "address": "123 Main St, Lagos",
        }
        is_valid, error = registration_service.validate_registration_data(data)
        assert is_valid is False
        assert "3-255 characters" in error

    def test_weak_password(self, registration_service):
        """Test validation with weak password."""
        data = {
            "salon_name": "Acme Salon",
            "owner_name": "John Doe",
            "email": "john@example.com",
            "phone": "+234 123 456 7890",
            "password": "weak",
            "address": "123 Main St, Lagos",
        }
        is_valid, error = registration_service.validate_registration_data(data)
        assert is_valid is False
        assert "at least 12 characters" in error

    def test_password_missing_uppercase(self, registration_service):
        """Test validation with password missing uppercase."""
        data = {
            "salon_name": "Acme Salon",
            "owner_name": "John Doe",
            "email": "john@example.com",
            "phone": "+234 123 456 7890",
            "password": "securepass123!",
            "address": "123 Main St, Lagos",
        }
        is_valid, error = registration_service.validate_registration_data(data)
        assert is_valid is False
        assert "uppercase" in error

    def test_password_missing_special_char(self, registration_service):
        """Test validation with password missing special character."""
        data = {
            "salon_name": "Acme Salon",
            "owner_name": "John Doe",
            "email": "john@example.com",
            "phone": "+234 123 456 7890",
            "password": "SecurePass123",
            "address": "123 Main St, Lagos",
        }
        is_valid, error = registration_service.validate_registration_data(data)
        assert is_valid is False
        assert "special character" in error

    def test_short_address(self, registration_service):
        """Test validation with short address."""
        data = {
            "salon_name": "Acme Salon",
            "owner_name": "John Doe",
            "email": "john@example.com",
            "phone": "+234 123 456 7890",
            "password": "SecurePass123!",
            "address": "123",
        }
        is_valid, error = registration_service.validate_registration_data(data)
        assert is_valid is False
        assert "5-500 characters" in error

    def test_invalid_referral_code(self, registration_service):
        """Test validation with invalid referral code."""
        data = {
            "salon_name": "Acme Salon",
            "owner_name": "John Doe",
            "email": "john@example.com",
            "phone": "+234 123 456 7890",
            "password": "SecurePass123!",
            "address": "123 Main St, Lagos",
            "referral_code": "REF@123",
        }
        is_valid, error = registration_service.validate_registration_data(data)
        assert is_valid is False
        assert "alphanumeric" in error


class TestGenerateSubdomain:
    """Tests for subdomain generation."""

    def test_generate_subdomain_from_salon_name(self, registration_service):
        """Test subdomain generation from salon name."""
        subdomain = registration_service.generate_subdomain("Acme Salon")
        assert subdomain == "acme-salon"

    def test_generate_subdomain_with_special_chars(self, registration_service):
        """Test subdomain generation with special characters."""
        subdomain = registration_service.generate_subdomain("Acme's Salon & Spa")
        assert subdomain == "acmes-salon-spa"

    def test_generate_subdomain_with_multiple_spaces(self, registration_service):
        """Test subdomain generation with multiple spaces."""
        subdomain = registration_service.generate_subdomain("Acme   Salon")
        assert subdomain == "acme-salon"

    def test_subdomain_max_length(self, registration_service):
        """Test subdomain respects max length."""
        long_name = "A" * 100
        subdomain = registration_service.generate_subdomain(long_name)
        assert len(subdomain) <= 63


class TestGenerateVerificationCode:
    """Tests for verification code generation."""

    def test_generate_verification_code_length(self, registration_service):
        """Test verification code is 6 digits."""
        code = registration_service.generate_verification_code()
        assert len(code) == 6

    def test_generate_verification_code_is_numeric(self, registration_service):
        """Test verification code is numeric."""
        code = registration_service.generate_verification_code()
        assert code.isdigit()

    def test_generate_verification_code_uniqueness(self, registration_service):
        """Test verification codes are unique."""
        codes = set()
        for _ in range(100):
            code = registration_service.generate_verification_code()
            codes.add(code)
        # Should have at least 95 unique codes out of 100
        assert len(codes) >= 95


class TestPasswordHashing:
    """Tests for password hashing."""

    def test_hash_password(self, registration_service):
        """Test password hashing."""
        password = "SecurePass123!"
        hashed = registration_service.hash_password(password)
        assert hashed != password
        assert len(hashed) > 20

    def test_hash_password_consistency(self, registration_service):
        """Test password hashing is consistent."""
        password = "SecurePass123!"
        hash1 = registration_service.hash_password(password)
        hash2 = registration_service.hash_password(password)
        # Hashes should be different due to salt
        assert hash1 != hash2


class TestEmailValidation:
    """Tests for email validation."""

    def test_valid_email(self, registration_service):
        """Test valid email."""
        assert registration_service._is_valid_email("john@example.com") is True

    def test_invalid_email_no_at(self, registration_service):
        """Test invalid email without @."""
        assert registration_service._is_valid_email("johnexample.com") is False

    def test_invalid_email_no_domain(self, registration_service):
        """Test invalid email without domain."""
        assert registration_service._is_valid_email("john@") is False

    def test_invalid_email_no_tld(self, registration_service):
        """Test invalid email without TLD."""
        assert registration_service._is_valid_email("john@example") is False


class TestPhoneValidation:
    """Tests for phone validation."""

    def test_valid_phone_with_plus(self, registration_service):
        """Test valid phone with plus."""
        assert registration_service._is_valid_phone("+234 123 456 7890") is True

    def test_valid_phone_without_plus(self, registration_service):
        """Test valid phone without plus."""
        assert registration_service._is_valid_phone("234 123 456 7890") is True

    def test_invalid_phone_too_short(self, registration_service):
        """Test invalid phone too short."""
        assert registration_service._is_valid_phone("123") is False

    def test_invalid_phone_too_long(self, registration_service):
        """Test invalid phone too long."""
        assert registration_service._is_valid_phone("+234 123 456 7890 123") is False


class TestPasswordStrength:
    """Tests for password strength validation."""

    def test_strong_password(self, registration_service):
        """Test strong password."""
        is_strong, error = registration_service._is_strong_password("SecurePass123!")
        assert is_strong is True
        assert error is None

    def test_password_too_short(self, registration_service):
        """Test password too short."""
        is_strong, error = registration_service._is_strong_password("Short1!")
        assert is_strong is False
        assert "12 characters" in error

    def test_password_no_uppercase(self, registration_service):
        """Test password without uppercase."""
        is_strong, error = registration_service._is_strong_password("securepass123!")
        assert is_strong is False
        assert "uppercase" in error

    def test_password_no_lowercase(self, registration_service):
        """Test password without lowercase."""
        is_strong, error = registration_service._is_strong_password("SECUREPASS123!")
        assert is_strong is False
        assert "lowercase" in error

    def test_password_no_digit(self, registration_service):
        """Test password without digit."""
        is_strong, error = registration_service._is_strong_password("SecurePass!")
        assert is_strong is False
        assert "digit" in error

    def test_password_no_special_char(self, registration_service):
        """Test password without special character."""
        is_strong, error = registration_service._is_strong_password("SecurePass123")
        assert is_strong is False
        assert "special character" in error
