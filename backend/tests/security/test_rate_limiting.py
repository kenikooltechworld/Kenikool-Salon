"""Tests for rate limiting and brute force protection."""

import pytest
from app.middleware.rate_limit import (
    get_login_attempts,
    increment_login_attempts,
    reset_login_attempts,
    is_account_locked,
    lock_account,
    unlock_account,
)


class TestLoginAttempts:
    """Test login attempt tracking."""

    def test_get_initial_attempts(self):
        """Test initial login attempts is 0."""
        attempts = get_login_attempts("test@example.com")
        assert attempts == 0

    def test_increment_attempts(self):
        """Test incrementing login attempts."""
        email = "test@example.com"
        reset_login_attempts(email)  # Clean up first

        attempts = increment_login_attempts(email)
        assert attempts >= 1

    def test_reset_attempts(self):
        """Test resetting login attempts."""
        email = "test@example.com"
        increment_login_attempts(email)
        reset_login_attempts(email)

        attempts = get_login_attempts(email)
        assert attempts == 0


class TestAccountLocking:
    """Test account locking mechanism."""

    def test_account_not_locked_initially(self):
        """Test account is not locked initially."""
        email = "test@example.com"
        unlock_account(email)  # Clean up first

        locked = is_account_locked(email)
        assert locked is False

    def test_lock_account(self):
        """Test locking account."""
        email = "test@example.com"
        lock_account(email)

        locked = is_account_locked(email)
        assert locked is True

    def test_unlock_account(self):
        """Test unlocking account."""
        email = "test@example.com"
        lock_account(email)
        unlock_account(email)

        locked = is_account_locked(email)
        assert locked is False
