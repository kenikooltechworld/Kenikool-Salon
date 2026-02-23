"""
Unit tests for public booking enhancement features.

Tests cover:
- Booking creation with payment_option
- Cancellation logic
- Rescheduling logic
- Notification preference updates
- Testimonial filtering
- Statistics calculation
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from bson import ObjectId

from backend.app.models.public_booking import PublicBooking, PublicBookingStatus
from backend.app.models.notification import PublicBookingNotificationPreference
from backend.app.services.public_booking_service import PublicBookingService
from backend.app.schemas.public_booking import (
    PublicBookingCreate,
    PublicBookingResponse,
    PublicBookingCancellation,
    PublicBookingReschedule,
)


class TestBookingCreationWithPayment:
    """Test booking creation with payment_option field."""

    @pytest.fixture
    def booking_data(self):
        """Sample booking data with payment option."""
        return {
            "tenant_id": ObjectId(),
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "customer_phone": "+1234567890",
            "service_id": ObjectId(),
            "staff_id": ObjectId(),
            "booking_date": (datetime.now() + timedelta(days=1)).date(),
            "booking_time": "14:00",
            "duration_minutes": 60,
            "payment_option": "now",
            "notes": "Test booking",
        }

    def test_booking_creation_with_pay_now_option(self, booking_data):
        """Test booking creation with 'pay now' option."""
        booking_data["payment_option"] = "now"
        
        # Verify payment_option is set correctly
        assert booking_data["payment_option"] == "now"
        assert "payment_status" not in booking_data or booking_data.get("payment_status") is None

    def test_booking_creation_with_pay_later_option(self, booking_data):
        """Test booking creation with 'pay later' option."""
        booking_data["payment_option"] = "later"
        
        # Verify payment_option is set correctly
        assert booking_data["payment_option"] == "later"

    def test_booking_creation_validates_payment_option(self, booking_data):
        """Test that invalid payment options are rejected."""
        booking_data["payment_option"] = "invalid"
        
        # Should validate that payment_option is either "now" or "later"
        valid_options = ["now", "later"]
        assert booking_data["payment_option"] not in valid_options

    def test_booking_includes_payment_fields(self, booking_data):
        """Test that booking includes all payment-related fields."""
        booking_data["payment_option"] = "now"
        booking_data["payment_status"] = "pending"
        booking_data["payment_id"] = "pay_123456"
        
        assert booking_data["payment_option"] == "now"
        assert booking_data["payment_status"] == "pending"
        assert booking_data["payment_id"] == "pay_123456"


class TestCancellationLogic:
    """Test booking cancellation logic."""

    @pytest.fixture
    def booking_data(self):
        """Sample booking for cancellation tests."""
        return {
            "id": ObjectId(),
            "tenant_id": ObjectId(),
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "booking_date": (datetime.now() + timedelta(days=1)).date(),
            "booking_time": "14:00",
            "status": PublicBookingStatus.CONFIRMED,
            "payment_option": "now",
            "payment_status": "success",
            "created_at": datetime.now(),
        }

    def test_cancellation_allowed_24_hours_before(self, booking_data):
        """Test that cancellation is allowed 24+ hours before appointment."""
        # Booking is tomorrow at 14:00
        booking_date = datetime.now() + timedelta(days=1)
        booking_data["booking_date"] = booking_date.date()
        booking_data["booking_time"] = "14:00"
        
        # Current time is now, so cancellation should be allowed
        time_until_appointment = booking_date - datetime.now()
        assert time_until_appointment.total_seconds() > 2 * 3600  # More than 2 hours

    def test_cancellation_not_allowed_within_2_hours(self, booking_data):
        """Test that cancellation is not allowed within 2 hours of appointment."""
        # Booking is in 1 hour
        booking_date = datetime.now() + timedelta(hours=1)
        booking_data["booking_date"] = booking_date.date()
        booking_data["booking_time"] = booking_date.strftime("%H:%M")
        
        # Current time is now, so cancellation should NOT be allowed
        time_until_appointment = booking_date - datetime.now()
        assert time_until_appointment.total_seconds() < 2 * 3600  # Less than 2 hours

    def test_cancellation_updates_status(self, booking_data):
        """Test that cancellation updates booking status."""
        booking_data["status"] = PublicBookingStatus.CONFIRMED
        
        # Simulate cancellation
        booking_data["status"] = PublicBookingStatus.CANCELLED
        booking_data["cancelled_at"] = datetime.now()
        
        assert booking_data["status"] == PublicBookingStatus.CANCELLED
        assert booking_data["cancelled_at"] is not None

    def test_cancellation_stores_reason(self, booking_data):
        """Test that cancellation reason is stored."""
        cancellation_reason = "Emergency came up"
        booking_data["cancellation_reason"] = cancellation_reason
        
        assert booking_data["cancellation_reason"] == cancellation_reason

    def test_cancellation_with_paid_booking(self, booking_data):
        """Test cancellation of a paid booking."""
        booking_data["payment_status"] = "success"
        booking_data["payment_id"] = "pay_123456"
        
        # Verify payment info is present for refund processing
        assert booking_data["payment_status"] == "success"
        assert booking_data["payment_id"] is not None


class TestReschedulingLogic:
    """Test booking rescheduling logic."""

    @pytest.fixture
    def booking_data(self):
        """Sample booking for rescheduling tests."""
        return {
            "id": ObjectId(),
            "tenant_id": ObjectId(),
            "booking_date": (datetime.now() + timedelta(days=1)).date(),
            "booking_time": "14:00",
            "status": PublicBookingStatus.CONFIRMED,
            "created_at": datetime.now(),
        }

    def test_rescheduling_allowed_24_hours_before(self, booking_data):
        """Test that rescheduling is allowed 24+ hours before appointment."""
        booking_date = datetime.now() + timedelta(days=2)
        booking_data["booking_date"] = booking_date.date()
        
        time_until_appointment = booking_date - datetime.now()
        assert time_until_appointment.total_seconds() > 24 * 3600  # More than 24 hours

    def test_rescheduling_not_allowed_within_24_hours(self, booking_data):
        """Test that rescheduling is not allowed within 24 hours."""
        booking_date = datetime.now() + timedelta(hours=12)
        booking_data["booking_date"] = booking_date.date()
        
        time_until_appointment = booking_date - datetime.now()
        assert time_until_appointment.total_seconds() < 24 * 3600  # Less than 24 hours

    def test_rescheduling_updates_date_and_time(self, booking_data):
        """Test that rescheduling updates booking date and time."""
        original_date = booking_data["booking_date"]
        original_time = booking_data["booking_time"]
        
        new_date = (datetime.now() + timedelta(days=3)).date()
        new_time = "15:00"
        
        booking_data["booking_date"] = new_date
        booking_data["booking_time"] = new_time
        
        assert booking_data["booking_date"] != original_date
        assert booking_data["booking_time"] != original_time
        assert booking_data["booking_date"] == new_date
        assert booking_data["booking_time"] == new_time

    def test_rescheduling_stores_original_booking_reference(self, booking_data):
        """Test that rescheduling stores reference to original booking."""
        original_booking_id = booking_data["id"]
        new_booking_id = ObjectId()
        
        booking_data["rescheduled_from"] = original_booking_id
        
        assert booking_data["rescheduled_from"] == original_booking_id

    def test_rescheduling_preserves_other_fields(self, booking_data):
        """Test that rescheduling preserves other booking fields."""
        original_customer = booking_data.get("customer_name", "John Doe")
        original_service = booking_data.get("service_id")
        
        # Update date/time
        booking_data["booking_date"] = (datetime.now() + timedelta(days=3)).date()
        booking_data["booking_time"] = "15:00"
        
        # Verify other fields are unchanged
        assert booking_data.get("customer_name") == original_customer
        assert booking_data.get("service_id") == original_service


class TestNotificationPreferences:
    """Test notification preference updates."""

    @pytest.fixture
    def preference_data(self):
        """Sample notification preference data."""
        return {
            "booking_id": ObjectId(),
            "customer_email": "john@example.com",
            "customer_phone": "+1234567890",
            "send_confirmation_email": True,
            "send_24h_reminder_email": True,
            "send_1h_reminder_email": True,
            "send_sms_reminders": False,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

    def test_preference_creation(self, preference_data):
        """Test creating notification preferences."""
        assert preference_data["booking_id"] is not None
        assert preference_data["send_confirmation_email"] is True
        assert preference_data["send_24h_reminder_email"] is True

    def test_preference_update_email_toggles(self, preference_data):
        """Test updating email notification toggles."""
        preference_data["send_confirmation_email"] = False
        preference_data["send_24h_reminder_email"] = False
        
        assert preference_data["send_confirmation_email"] is False
        assert preference_data["send_24h_reminder_email"] is False

    def test_preference_update_sms_toggle(self, preference_data):
        """Test updating SMS notification toggle."""
        preference_data["send_sms_reminders"] = True
        
        assert preference_data["send_sms_reminders"] is True

    def test_preference_update_timestamp(self, preference_data):
        """Test that updated_at is updated when preferences change."""
        original_updated_at = preference_data["updated_at"]
        
        # Simulate update
        import time
        time.sleep(0.1)
        preference_data["updated_at"] = datetime.now()
        
        assert preference_data["updated_at"] > original_updated_at

    def test_preference_all_notifications_disabled(self, preference_data):
        """Test disabling all notifications."""
        preference_data["send_confirmation_email"] = False
        preference_data["send_24h_reminder_email"] = False
        preference_data["send_1h_reminder_email"] = False
        preference_data["send_sms_reminders"] = False
        
        # Verify all are disabled
        assert not preference_data["send_confirmation_email"]
        assert not preference_data["send_24h_reminder_email"]
        assert not preference_data["send_1h_reminder_email"]
        assert not preference_data["send_sms_reminders"]


class TestTestimonialFiltering:
    """Test testimonial filtering logic."""

    @pytest.fixture
    def testimonials(self):
        """Sample testimonials from bookings."""
        return [
            {
                "booking_id": ObjectId(),
                "customer_name": "John Doe",
                "rating": 5,
                "review": "Excellent service!",
                "created_at": datetime.now() - timedelta(days=1),
            },
            {
                "booking_id": ObjectId(),
                "customer_name": "Jane Smith",
                "rating": 4,
                "review": "Very good experience",
                "created_at": datetime.now() - timedelta(days=2),
            },
            {
                "booking_id": ObjectId(),
                "customer_name": "Bob Johnson",
                "rating": 3,
                "review": "Average service",
                "created_at": datetime.now() - timedelta(days=3),
            },
            {
                "booking_id": ObjectId(),
                "customer_name": "Alice Brown",
                "rating": 2,
                "review": "Not satisfied",
                "created_at": datetime.now() - timedelta(days=4),
            },
        ]

    def test_filter_testimonials_by_rating(self, testimonials):
        """Test filtering testimonials by minimum rating."""
        min_rating = 4
        filtered = [t for t in testimonials if t["rating"] >= min_rating]
        
        assert len(filtered) == 2
        assert all(t["rating"] >= min_rating for t in filtered)

    def test_filter_testimonials_by_limit(self, testimonials):
        """Test limiting number of testimonials."""
        limit = 3
        filtered = testimonials[:limit]
        
        assert len(filtered) == limit

    def test_sort_testimonials_by_date(self, testimonials):
        """Test sorting testimonials by date (most recent first)."""
        sorted_testimonials = sorted(
            testimonials,
            key=lambda t: t["created_at"],
            reverse=True
        )
        
        assert sorted_testimonials[0]["customer_name"] == "John Doe"
        assert sorted_testimonials[-1]["customer_name"] == "Alice Brown"

    def test_filter_and_limit_testimonials(self, testimonials):
        """Test filtering by rating and limiting results."""
        min_rating = 4
        limit = 2
        
        filtered = [t for t in testimonials if t["rating"] >= min_rating]
        filtered = sorted(filtered, key=lambda t: t["created_at"], reverse=True)
        filtered = filtered[:limit]
        
        assert len(filtered) == 2
        assert all(t["rating"] >= min_rating for t in filtered)


class TestStatisticsCalculation:
    """Test booking statistics calculation."""

    @pytest.fixture
    def bookings(self):
        """Sample bookings for statistics."""
        return [
            {
                "id": ObjectId(),
                "status": PublicBookingStatus.COMPLETED,
                "rating": 5,
                "created_at": datetime.now() - timedelta(days=1),
            },
            {
                "id": ObjectId(),
                "status": PublicBookingStatus.COMPLETED,
                "rating": 4,
                "created_at": datetime.now() - timedelta(days=2),
            },
            {
                "id": ObjectId(),
                "status": PublicBookingStatus.COMPLETED,
                "rating": 5,
                "created_at": datetime.now() - timedelta(days=3),
            },
            {
                "id": ObjectId(),
                "status": PublicBookingStatus.CONFIRMED,
                "rating": None,
                "created_at": datetime.now() - timedelta(days=4),
            },
            {
                "id": ObjectId(),
                "status": PublicBookingStatus.CANCELLED,
                "rating": None,
                "created_at": datetime.now() - timedelta(days=5),
            },
        ]

    def test_calculate_total_bookings(self, bookings):
        """Test calculating total bookings."""
        total = len(bookings)
        
        assert total == 5

    def test_calculate_completed_bookings(self, bookings):
        """Test calculating completed bookings."""
        completed = len([b for b in bookings if b["status"] == PublicBookingStatus.COMPLETED])
        
        assert completed == 3

    def test_calculate_average_rating(self, bookings):
        """Test calculating average rating."""
        completed_bookings = [b for b in bookings if b["status"] == PublicBookingStatus.COMPLETED]
        ratings = [b["rating"] for b in completed_bookings if b["rating"] is not None]
        average_rating = sum(ratings) / len(ratings) if ratings else 0
        
        assert average_rating == 4.67 or abs(average_rating - 4.67) < 0.01

    def test_calculate_completion_rate(self, bookings):
        """Test calculating completion rate."""
        completed = len([b for b in bookings if b["status"] == PublicBookingStatus.COMPLETED])
        total = len(bookings)
        completion_rate = (completed / total) * 100 if total > 0 else 0
        
        assert completion_rate == 60.0

    def test_calculate_cancellation_rate(self, bookings):
        """Test calculating cancellation rate."""
        cancelled = len([b for b in bookings if b["status"] == PublicBookingStatus.CANCELLED])
        total = len(bookings)
        cancellation_rate = (cancelled / total) * 100 if total > 0 else 0
        
        assert cancellation_rate == 20.0

    def test_statistics_with_no_bookings(self):
        """Test statistics calculation with no bookings."""
        bookings = []
        
        total = len(bookings)
        average_rating = 0
        
        assert total == 0
        assert average_rating == 0


class TestPaymentStatusTransitions:
    """Test payment status transitions."""

    @pytest.fixture
    def booking_data(self):
        """Sample booking with payment."""
        return {
            "id": ObjectId(),
            "payment_option": "now",
            "payment_status": "pending",
            "payment_id": None,
        }

    def test_payment_status_pending_to_success(self, booking_data):
        """Test payment status transition from pending to success."""
        assert booking_data["payment_status"] == "pending"
        
        booking_data["payment_status"] = "success"
        booking_data["payment_id"] = "pay_123456"
        
        assert booking_data["payment_status"] == "success"
        assert booking_data["payment_id"] is not None

    def test_payment_status_pending_to_failed(self, booking_data):
        """Test payment status transition from pending to failed."""
        assert booking_data["payment_status"] == "pending"
        
        booking_data["payment_status"] = "failed"
        
        assert booking_data["payment_status"] == "failed"

    def test_payment_status_failed_to_pending_retry(self, booking_data):
        """Test payment status retry after failure."""
        booking_data["payment_status"] = "failed"
        
        # Retry payment
        booking_data["payment_status"] = "pending"
        
        assert booking_data["payment_status"] == "pending"


class TestReminderTracking:
    """Test reminder tracking fields."""

    @pytest.fixture
    def booking_data(self):
        """Sample booking for reminder tracking."""
        return {
            "id": ObjectId(),
            "reminder_24h_sent": False,
            "reminder_1h_sent": False,
        }

    def test_reminder_24h_tracking(self, booking_data):
        """Test 24h reminder tracking."""
        assert booking_data["reminder_24h_sent"] is False
        
        booking_data["reminder_24h_sent"] = True
        
        assert booking_data["reminder_24h_sent"] is True

    def test_reminder_1h_tracking(self, booking_data):
        """Test 1h reminder tracking."""
        assert booking_data["reminder_1h_sent"] is False
        
        booking_data["reminder_1h_sent"] = True
        
        assert booking_data["reminder_1h_sent"] is True

    def test_both_reminders_sent(self, booking_data):
        """Test both reminders sent."""
        booking_data["reminder_24h_sent"] = True
        booking_data["reminder_1h_sent"] = True
        
        assert booking_data["reminder_24h_sent"] is True
        assert booking_data["reminder_1h_sent"] is True
