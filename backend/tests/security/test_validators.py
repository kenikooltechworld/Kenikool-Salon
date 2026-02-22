"""Tests for input validators."""

import pytest
from app.validators import (
    sanitize_string,
    sanitize_email,
    sanitize_phone,
    validate_file_upload,
    prevent_nosql_injection,
    prevent_xss,
    PasswordValidator,
)


class TestSanitizeString:
    """Test string sanitization."""

    def test_sanitize_removes_null_bytes(self):
        """Test null bytes are removed."""
        result = sanitize_string("hello\x00world")
        assert result == "hello world"

    def test_sanitize_trims_whitespace(self):
        """Test whitespace is trimmed."""
        result = sanitize_string("  hello  ")
        assert result == "hello"

    def test_sanitize_respects_max_length(self):
        """Test max length is enforced."""
        with pytest.raises(ValueError):
            sanitize_string("a" * 256, max_length=255)

    def test_sanitize_valid_string(self):
        """Test valid string passes through."""
        result = sanitize_string("hello world")
        assert result == "hello world"


class TestSanitizeEmail:
    """Test email sanitization."""

    def test_valid_email(self):
        """Test valid email is accepted."""
        result = sanitize_email("user@example.com")
        assert result == "user@example.com"

    def test_invalid_email_no_at(self):
        """Test email without @ is rejected."""
        result = sanitize_email("userexample.com")
        assert result == ""

    def test_invalid_email_no_domain(self):
        """Test email without domain is rejected."""
        result = sanitize_email("user@")
        assert result == ""

    def test_email_lowercased(self):
        """Test email is lowercased."""
        result = sanitize_email("User@Example.COM")
        assert result == "user@example.com"


class TestSanitizePhone:
    """Test phone number sanitization."""

    def test_valid_phone(self):
        """Test valid phone number is accepted."""
        result = sanitize_phone("1234567890")
        assert result == "1234567890"

    def test_phone_with_formatting(self):
        """Test phone with formatting is cleaned."""
        result = sanitize_phone("(123) 456-7890")
        assert result == "1234567890"

    def test_invalid_phone_too_short(self):
        """Test phone too short is rejected."""
        result = sanitize_phone("123")
        assert result == ""

    def test_invalid_phone_too_long(self):
        """Test phone too long is rejected."""
        result = sanitize_phone("1" * 20)
        assert result == ""


class TestValidateFileUpload:
    """Test file upload validation."""

    def test_invalid_extension(self):
        """Test invalid file extension is rejected."""
        with pytest.raises(ValueError):
            validate_file_upload("test.exe", {"pdf", "txt"})

    def test_path_traversal_attempt(self):
        """Test path traversal attempt is rejected."""
        with pytest.raises(ValueError):
            validate_file_upload("../../../etc/passwd", {"pdf", "txt"})

    def test_valid_file(self):
        """Test valid file passes validation."""
        result = validate_file_upload("document.pdf", {"pdf", "txt"})
        assert result is True


class TestPreventNoSQLInjection:
    """Test NoSQL injection prevention."""

    def test_mongodb_operator_rejected(self):
        """Test MongoDB operators are rejected."""
        with pytest.raises(ValueError):
            prevent_nosql_injection({"$where": "1==1"})

    def test_nested_operator_rejected(self):
        """Test nested operators are rejected."""
        with pytest.raises(ValueError):
            prevent_nosql_injection({"user": {"$ne": None}})

    def test_valid_data_passes(self):
        """Test valid data passes through."""
        data = {"name": "John", "email": "john@example.com"}
        result = prevent_nosql_injection(data)
        assert result == data


class TestPreventXSS:
    """Test XSS prevention."""

    def test_html_entities_escaped(self):
        """Test HTML entities are escaped."""
        result = prevent_xss("<script>alert('xss')</script>")
        assert "&lt;" in result
        assert "&gt;" in result
        assert "<script>" not in result

    def test_quotes_escaped(self):
        """Test quotes are escaped."""
        result = prevent_xss('onclick="alert(\'xss\')"')
        assert "&quot;" in result or "&#x27;" in result

    def test_valid_text_passes(self):
        """Test valid text passes through."""
        result = prevent_xss("Hello World")
        assert result == "Hello World"


class TestPasswordValidator:
    """Test password validation."""

    def test_password_too_short(self):
        """Test password too short is rejected."""
        with pytest.raises(ValueError):
            PasswordValidator(password="Short1!")

    def test_password_no_uppercase(self):
        """Test password without uppercase is rejected."""
        with pytest.raises(ValueError):
            PasswordValidator(password="lowercase1234!")

    def test_password_no_lowercase(self):
        """Test password without lowercase is rejected."""
        with pytest.raises(ValueError):
            PasswordValidator(password="UPPERCASE1234!")

    def test_password_no_digit(self):
        """Test password without digit is rejected."""
        with pytest.raises(ValueError):
            PasswordValidator(password="NoDigits!@#$")

    def test_password_no_special_char(self):
        """Test password without special character is rejected."""
        with pytest.raises(ValueError):
            PasswordValidator(password="NoSpecial1234")

    def test_valid_password(self):
        """Test valid password is accepted."""
        validator = PasswordValidator(password="ValidPass123!")
        assert validator.password == "ValidPass123!"
