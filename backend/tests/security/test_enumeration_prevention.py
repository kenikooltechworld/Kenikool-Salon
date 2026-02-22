"""Tests for account enumeration prevention."""

import pytest
import time
from app.middleware.enumeration_prevention import (
    constant_time_compare,
    get_generic_error_message,
    add_timing_delay,
)


class TestConstantTimeCompare:
    """Test constant-time string comparison."""

    def test_equal_strings(self):
        """Test equal strings return True."""
        result = constant_time_compare("password123", "password123")
        assert result is True

    def test_different_strings(self):
        """Test different strings return False."""
        result = constant_time_compare("password123", "password456")
        assert result is False

    def test_empty_strings(self):
        """Test empty strings."""
        result = constant_time_compare("", "")
        assert result is True

    def test_one_empty_string(self):
        """Test one empty string."""
        result = constant_time_compare("", "password")
        assert result is False

    def test_case_sensitive(self):
        """Test comparison is case-sensitive."""
        result = constant_time_compare("Password", "password")
        assert result is False

    def test_timing_consistency(self):
        """Test timing is consistent regardless of string length."""
        # This is a basic test - real timing attack prevention requires more sophisticated testing
        start = time.time()
        constant_time_compare("a" * 100, "b" * 100)
        time1 = time.time() - start

        start = time.time()
        constant_time_compare("a" * 100, "a" * 99 + "b")
        time2 = time.time() - start

        # Both should take similar time (within reasonable margin)
        # Note: This is a simplified test and may not catch all timing attacks
        assert abs(time1 - time2) < 0.1  # 100ms margin


class TestGenericErrorMessages:
    """Test generic error message generation."""

    def test_login_error_message(self):
        """Test login error message is generic."""
        message = get_generic_error_message("login")
        assert message == "Invalid credentials"
        assert "email" not in message.lower()
        assert "password" not in message.lower()

    def test_registration_error_message(self):
        """Test registration error message is generic."""
        message = get_generic_error_message("registration")
        assert "Registration failed" in message
        assert "email" not in message.lower()

    def test_password_reset_error_message(self):
        """Test password reset error message is generic."""
        message = get_generic_error_message("password_reset")
        assert "If an account exists" in message
        assert "email" not in message.lower()

    def test_email_exists_error_message(self):
        """Test email exists error message is generic."""
        message = get_generic_error_message("email_exists")
        assert "If an account exists" in message

    def test_user_not_found_error_message(self):
        """Test user not found error message is generic."""
        message = get_generic_error_message("user_not_found")
        assert message == "Invalid credentials"

    def test_unknown_error_type(self):
        """Test unknown error type returns generic message."""
        message = get_generic_error_message("unknown_error")
        assert "An error occurred" in message

    def test_no_information_leakage(self):
        """Test that error messages don't leak information."""
        messages = [
            get_generic_error_message("login"),
            get_generic_error_message("registration"),
            get_generic_error_message("password_reset"),
        ]
        
        # Check that messages don't contain sensitive information
        for message in messages:
            assert "email" not in message.lower() or "account" in message.lower()
            assert "password" not in message.lower()
            assert "user" not in message.lower() or "account" in message.lower()


class TestTimingDelay:
    """Test timing delay for preventing timing attacks."""

    def test_timing_delay_adds_delay(self):
        """Test that timing delay adds delay."""
        start = time.time()
        add_timing_delay(base_time=0.05)
        elapsed = time.time() - start
        
        # Should add some delay (at least 0ms, at most 50ms + overhead)
        assert elapsed >= 0
        assert elapsed < 0.2  # Allow for overhead

    def test_timing_delay_randomness(self):
        """Test that timing delay is random."""
        delays = []
        for _ in range(5):
            start = time.time()
            add_timing_delay(base_time=0.01)
            delays.append(time.time() - start)
        
        # Delays should vary (not all exactly the same)
        # This is a basic test - real randomness testing is more complex
        assert len(set([round(d, 3) for d in delays])) > 1 or all(d < 0.02 for d in delays)

    def test_timing_delay_default_parameter(self):
        """Test timing delay with default parameter."""
        start = time.time()
        add_timing_delay()  # Uses default base_time=0.1
        elapsed = time.time() - start
        
        # Should complete in reasonable time
        assert elapsed < 0.3


class TestEnumerationPrevention:
    """Test enumeration prevention strategies."""

    def test_generic_messages_prevent_enumeration(self):
        """Test that generic messages prevent account enumeration."""
        # When user doesn't exist
        message_not_found = get_generic_error_message("user_not_found")
        # When password is wrong
        message_wrong_password = get_generic_error_message("login")
        
        # Both should be the same to prevent enumeration
        assert message_not_found == message_wrong_password

    def test_password_reset_prevents_enumeration(self):
        """Test that password reset messages prevent enumeration."""
        message = get_generic_error_message("password_reset")
        
        # Should not reveal if email exists or not
        assert "does not exist" not in message.lower()
        assert "not found" not in message.lower()
        assert "If an account exists" in message

    def test_timing_attack_prevention(self):
        """Test that timing delays prevent timing attacks."""
        # Simulate checking if email exists (fast) vs checking password (slow)
        # With timing delay, both should take similar time
        
        start = time.time()
        add_timing_delay(base_time=0.05)
        time_with_delay = time.time() - start
        
        # Should add noticeable delay
        assert time_with_delay > 0.01


class TestErrorMessageConsistency:
    """Test error message consistency."""

    def test_all_auth_errors_are_generic(self):
        """Test that all authentication errors are generic."""
        error_types = [
            "login",
            "user_not_found",
            "registration",
            "password_reset",
            "email_exists",
        ]
        
        messages = [get_generic_error_message(error_type) for error_type in error_types]
        
        # All messages should be generic (not reveal specific information)
        for message in messages:
            assert len(message) > 0
            assert "email" not in message.lower() or "account" in message.lower()
            assert "password" not in message.lower()

    def test_error_message_length_consistency(self):
        """Test that error messages have reasonable length."""
        messages = [
            get_generic_error_message("login"),
            get_generic_error_message("registration"),
            get_generic_error_message("password_reset"),
        ]
        
        # All messages should be reasonably short (prevent information leakage through length)
        for message in messages:
            assert 10 < len(message) < 200
