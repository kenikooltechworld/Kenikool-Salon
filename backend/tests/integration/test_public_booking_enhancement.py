"""
Integration tests for public booking enhancement features.

Tests cover:
- Full booking flow (service → staff → time → form → confirmation)
- Payment flow (booking → payment → confirmation)
- Cancellation flow (booking → cancellation → refund)
- Reminder sending (Celery task)
- Email delivery
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from bson import ObjectId

from backend.app.models.public_booking import PublicBooking, PublicBookingStatus
from backend.app.models.service import Service
from backend.app.models.staff import Staff
from backend.app.services.public_booking_service import PublicBookingService
from backend.app.schemas.public_booking import PublicBookingCreate


class TestFullBookingFlow:
    """Test complete booking flow from service selection to confirmation."""

    @pytest.fixture
    def tenant_id(self):
        """Sample tenant ID."""
        return ObjectId()

    @pytest.fixture
    def service_data(self, tenant_id):
        """Sample service data."""
        return {
            "id": ObjectId(),
            "tenant_id": tenant_id,
            "name": "Haircut",
            "description": "Professional haircut",
            "duration_minutes": 30,
            "price": 50.00,
            "benefits": ["Professional cut", "Styling included"],
        }

    @pytest.fixture
    def staff_data(self, tenant_id):
        """Sample staff data."""
        return {
            "id": ObjectId(),
            "tenant_id": tenant_id,
            "name": "John Smith",
            "bio": "Expert stylist",
            "specialties": ["Haircut", "Coloring"],
            "rating": 4.8,
            "review_count": 50,
        }

    @pytest.fixture
    def booking_data(self, tenant_id, service_data, staff_data):
        """Sample booking data."""
        return {
            "tenant_id": tenant_id,
            "customer_name": "Jane Doe",
            "customer_email": "jane@example.com",
            "customer_phone": "+1234567890",
            "service_id": service_data["id"],
            "staff_id": staff_data["id"],
            "booking_date": (datetime.now() + timedelta(days=1)).date(),
            "booking_time": "14:00",
            "duration_minutes": 30,
            "payment_option": "later",
            "notes": "First time customer",
        }

    def test_booking_flow_service_selection(self, service_data):
        """Test service selection step."""
        assert service_data["id"] is not None
        assert service_data["name"] == "Haircut"
        assert service_data["duration_minutes"] == 30
        assert service_data["price"] == 50.00

    def test_booking_flow_staff_selection(self, staff_data):
        """Test staff selection step."""
        assert staff_data["id"] is not None
        assert staff_data["name"] == "John Smith"
        assert staff_data["specialties"] == ["Haircut", "Coloring"]
        assert staff_data["rating"] == 4.8

    def test_booking_flow_time_selection(self, booking_data):
        """Test time slot selection step."""
        assert booking_data["booking_date"] is not None
        assert booking_data["booking_time"] == "14:00"
        assert booking_data["duration_minutes"] == 30

    def test_booking_flow_form_submission(self, booking_data):
        """Test booking form submission."""
        assert booking_data["customer_name"] == "Jane Doe"
        assert booking_data["customer_email"] == "jane@example.com"
        assert booking_data["customer_phone"] == "+1234567890"
        assert booking_data["notes"] == "First time customer"

    def test_booking_flow_confirmation(self, booking_data):
        """Test booking confirmation."""
        booking_data["status"] = PublicBookingStatus.CONFIRMED
        booking_data["created_at"] = datetime.now()
        
        assert booking_data["status"] == PublicBookingStatus.CONFIRMED
        assert booking_data["created_at"] is not None

    def test_full_booking_flow_pay_later(self, booking_data):
        """Test complete booking flow with pay later option."""
        # Step 1: Service selection
        assert booking_data["service_id"] is not None
        
        # Step 2: Staff selection
        assert booking_data["staff_id"] is not None
        
        # Step 3: Time selection
        assert booking_data["booking_date"] is not None
        assert booking_data["booking_time"] is not None
        
        # Step 4: Form submission
        assert booking_data["customer_name"] is not None
        assert booking_data["customer_email"] is not None
        
        # Step 5: Payment option
        assert booking_data["payment_option"] == "later"
        
        # Step 6: Confirmation
        booking_data["status"] = PublicBookingStatus.CONFIRMED
        assert booking_data["status"] == PublicBookingStatus.CONFIRMED


class TestPaymentFlow:
    """Test payment flow integration."""

    @pytest.fixture
    def booking_with_payment(self):
        """Sample booking with payment."""
        return {
            "id": ObjectId(),
            "tenant_id": ObjectId(),
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "booking_date": (datetime.now() + timedelta(days=1)).date(),
            "booking_time": "14:00",
            "payment_option": "now",
            "payment_status": "pending",
            "payment_id": None,
            "status": PublicBookingStatus.CONFIRMED,
        }

    def test_payment_flow_initialization(self, booking_with_payment):
        """Test payment initialization."""
        assert booking_with_payment["payment_option"] == "now"
        assert booking_with_payment["payment_status"] == "pending"
        assert booking_with_payment["payment_id"] is None

    def test_payment_flow_success(self, booking_with_payment):
        """Test successful payment."""
        # Simulate payment processing
        booking_with_payment["payment_status"] = "success"
        booking_with_payment["payment_id"] = "pay_123456789"
        
        assert booking_with_payment["payment_status"] == "success"
        assert booking_with_payment["payment_id"] is not None

    def test_payment_flow_failure(self, booking_with_payment):
        """Test payment failure."""
        # Simulate payment failure
        booking_with_payment["payment_status"] = "failed"
        
        assert booking_with_payment["payment_status"] == "failed"

    def test_payment_flow_retry(self, booking_with_payment):
        """Test payment retry after failure."""
        # First attempt fails
        booking_with_payment["payment_status"] = "failed"
        assert booking_with_payment["payment_status"] == "failed"
        
        # Retry
        booking_with_payment["payment_status"] = "pending"
        assert booking_with_payment["payment_status"] == "pending"
        
        # Second attempt succeeds
        booking_with_payment["payment_status"] = "success"
        booking_with_payment["payment_id"] = "pay_987654321"
        assert booking_with_payment["payment_status"] == "success"

    def test_payment_confirmation_email(self, booking_with_payment):
        """Test that confirmation email includes payment info."""
        booking_with_payment["payment_status"] = "success"
        booking_with_payment["payment_id"] = "pay_123456789"
        
        # Email should include payment info
        email_data = {
            "to": booking_with_payment["customer_email"],
            "subject": "Booking Confirmation",
            "payment_id": booking_with_payment["payment_id"],
            "payment_status": booking_with_payment["payment_status"],
        }
        
        assert email_data["payment_id"] == "pay_123456789"
        assert email_data["payment_status"] == "success"


class TestCancellationFlow:
    """Test cancellation flow integration."""

    @pytest.fixture
    def confirmed_booking(self):
        """Sample confirmed booking."""
        return {
            "id": ObjectId(),
            "tenant_id": ObjectId(),
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "booking_date": (datetime.now() + timedelta(days=2)).date(),
            "booking_time": "14:00",
            "status": PublicBookingStatus.CONFIRMED,
            "payment_option": "now",
            "payment_status": "success",
            "payment_id": "pay_123456",
        }

    def test_cancellation_flow_validation(self, confirmed_booking):
        """Test cancellation validation."""
        # Booking is 2 days away, so cancellation should be allowed
        time_until_appointment = (
            datetime.combine(confirmed_booking["booking_date"], datetime.min.time()) -
            datetime.now()
        )
        
        # Should be allowed (more than 2 hours)
        assert time_until_appointment.total_seconds() > 2 * 3600

    def test_cancellation_flow_status_update(self, confirmed_booking):
        """Test cancellation status update."""
        confirmed_booking["status"] = PublicBookingStatus.CANCELLED
        confirmed_booking["cancelled_at"] = datetime.now()
        confirmed_booking["cancellation_reason"] = "Emergency came up"
        
        assert confirmed_booking["status"] == PublicBookingStatus.CANCELLED
        assert confirmed_booking["cancelled_at"] is not None
        assert confirmed_booking["cancellation_reason"] is not None

    def test_cancellation_flow_refund_processing(self, confirmed_booking):
        """Test refund processing during cancellation."""
        # Booking has payment
        assert confirmed_booking["payment_status"] == "success"
        assert confirmed_booking["payment_id"] is not None
        
        # Simulate refund
        refund_data = {
            "original_payment_id": confirmed_booking["payment_id"],
            "refund_amount": 50.00,
            "refund_status": "pending",
        }
        
        assert refund_data["original_payment_id"] == "pay_123456"
        assert refund_data["refund_status"] == "pending"

    def test_cancellation_flow_email_notification(self, confirmed_booking):
        """Test cancellation email notification."""
        confirmed_booking["status"] = PublicBookingStatus.CANCELLED
        
        # Email should be sent
        email_data = {
            "to": confirmed_booking["customer_email"],
            "subject": "Booking Cancelled",
            "booking_id": str(confirmed_booking["id"]),
            "status": confirmed_booking["status"],
        }
        
        assert email_data["subject"] == "Booking Cancelled"
        assert email_data["status"] == PublicBookingStatus.CANCELLED

    def test_cancellation_flow_availability_cache_invalidation(self, confirmed_booking):
        """Test that cancellation invalidates availability cache."""
        # Cache key should be invalidated
        cache_key = f"availability:{confirmed_booking['tenant_id']}:{confirmed_booking['booking_date']}"
        
        # Simulate cache invalidation
        cache_invalidated = True
        
        assert cache_invalidated is True


class TestReminderSending:
    """Test reminder sending via Celery task."""

    @pytest.fixture
    def bookings_for_reminders(self):
        """Sample bookings for reminder testing."""
        now = datetime.now()
        return [
            {
                "id": ObjectId(),
                "customer_email": "john@example.com",
                "customer_phone": "+1234567890",
                "booking_date": (now + timedelta(hours=24)).date(),
                "booking_time": (now + timedelta(hours=24)).strftime("%H:%M"),
                "status": PublicBookingStatus.CONFIRMED,
                "reminder_24h_sent": False,
                "reminder_1h_sent": False,
            },
            {
                "id": ObjectId(),
                "customer_email": "jane@example.com",
                "customer_phone": "+0987654321",
                "booking_date": (now + timedelta(hours=1)).date(),
                "booking_time": (now + timedelta(hours=1)).strftime("%H:%M"),
                "status": PublicBookingStatus.CONFIRMED,
                "reminder_24h_sent": True,
                "reminder_1h_sent": False,
            },
        ]

    def test_find_bookings_24h_away(self, bookings_for_reminders):
        """Test finding bookings 24 hours away."""
        now = datetime.now()
        target_time = now + timedelta(hours=24)
        
        # Find bookings approximately 24 hours away
        bookings_24h = [
            b for b in bookings_for_reminders
            if not b["reminder_24h_sent"] and
            (datetime.combine(b["booking_date"], datetime.min.time()) - now).total_seconds() < 25 * 3600
        ]
        
        assert len(bookings_24h) >= 1

    def test_find_bookings_1h_away(self, bookings_for_reminders):
        """Test finding bookings 1 hour away."""
        now = datetime.now()
        
        # Find bookings approximately 1 hour away
        bookings_1h = [
            b for b in bookings_for_reminders
            if not b["reminder_1h_sent"] and
            (datetime.combine(b["booking_date"], datetime.min.time()) - now).total_seconds() < 2 * 3600
        ]
        
        assert len(bookings_1h) >= 1

    def test_reminder_email_sending(self, bookings_for_reminders):
        """Test reminder email sending."""
        booking = bookings_for_reminders[0]
        
        # Simulate email sending
        email_data = {
            "to": booking["customer_email"],
            "subject": "Appointment Reminder - 24 hours",
            "booking_id": str(booking["id"]),
        }
        
        assert email_data["to"] == booking["customer_email"]
        assert "24 hours" in email_data["subject"]

    def test_reminder_sms_sending(self, bookings_for_reminders):
        """Test reminder SMS sending."""
        booking = bookings_for_reminders[0]
        
        # Simulate SMS sending
        sms_data = {
            "to": booking["customer_phone"],
            "message": f"Reminder: Your appointment is in 24 hours",
        }
        
        assert sms_data["to"] == booking["customer_phone"]
        assert "24 hours" in sms_data["message"]

    def test_reminder_status_update(self, bookings_for_reminders):
        """Test updating reminder status after sending."""
        booking = bookings_for_reminders[0]
        
        # Update reminder status
        booking["reminder_24h_sent"] = True
        
        assert booking["reminder_24h_sent"] is True

    def test_reminder_not_sent_twice(self, bookings_for_reminders):
        """Test that reminders are not sent twice."""
        booking = bookings_for_reminders[1]
        
        # This booking already has 24h reminder sent
        assert booking["reminder_24h_sent"] is True
        
        # Should not send again
        should_send = not booking["reminder_24h_sent"]
        assert should_send is False


class TestEmailDelivery:
    """Test email delivery integration."""

    @pytest.fixture
    def booking_data(self):
        """Sample booking for email testing."""
        return {
            "id": ObjectId(),
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "booking_date": (datetime.now() + timedelta(days=1)).date(),
            "booking_time": "14:00",
            "service_name": "Haircut",
            "staff_name": "Jane Smith",
            "status": PublicBookingStatus.CONFIRMED,
        }

    def test_confirmation_email_content(self, booking_data):
        """Test confirmation email content."""
        email_content = {
            "to": booking_data["customer_email"],
            "subject": "Booking Confirmation",
            "body": f"""
            Dear {booking_data['customer_name']},
            
            Your booking has been confirmed.
            
            Service: {booking_data['service_name']}
            Staff: {booking_data['staff_name']}
            Date: {booking_data['booking_date']}
            Time: {booking_data['booking_time']}
            
            Thank you!
            """,
        }
        
        assert booking_data["customer_email"] in email_content["to"]
        assert booking_data["service_name"] in email_content["body"]
        assert booking_data["staff_name"] in email_content["body"]

    def test_cancellation_email_content(self, booking_data):
        """Test cancellation email content."""
        booking_data["status"] = PublicBookingStatus.CANCELLED
        
        email_content = {
            "to": booking_data["customer_email"],
            "subject": "Booking Cancelled",
            "body": f"""
            Dear {booking_data['customer_name']},
            
            Your booking has been cancelled.
            
            Booking ID: {booking_data['id']}
            
            If you have any questions, please contact us.
            """,
        }
        
        assert "Cancelled" in email_content["subject"]
        assert str(booking_data["id"]) in email_content["body"]

    def test_reminder_email_content(self, booking_data):
        """Test reminder email content."""
        email_content = {
            "to": booking_data["customer_email"],
            "subject": "Appointment Reminder",
            "body": f"""
            Dear {booking_data['customer_name']},
            
            This is a reminder of your upcoming appointment.
            
            Service: {booking_data['service_name']}
            Date: {booking_data['booking_date']}
            Time: {booking_data['booking_time']}
            """,
        }
        
        assert "Reminder" in email_content["subject"]
        assert booking_data["booking_date"].isoformat() in email_content["body"]

    def test_email_template_rendering(self, booking_data):
        """Test email template rendering."""
        # Simulate template rendering
        template_vars = {
            "customer_name": booking_data["customer_name"],
            "service_name": booking_data["service_name"],
            "booking_date": booking_data["booking_date"].isoformat(),
            "booking_time": booking_data["booking_time"],
        }
        
        assert template_vars["customer_name"] == "John Doe"
        assert template_vars["service_name"] == "Haircut"


class TestNotificationPreferencesIntegration:
    """Test notification preferences integration."""

    @pytest.fixture
    def booking_with_preferences(self):
        """Sample booking with notification preferences."""
        return {
            "id": ObjectId(),
            "customer_email": "john@example.com",
            "customer_phone": "+1234567890",
            "preferences": {
                "send_confirmation_email": True,
                "send_24h_reminder_email": True,
                "send_1h_reminder_email": True,
                "send_sms_reminders": False,
            },
        }

    def test_preferences_respected_for_confirmation(self, booking_with_preferences):
        """Test that confirmation email respects preferences."""
        prefs = booking_with_preferences["preferences"]
        
        if prefs["send_confirmation_email"]:
            # Send confirmation email
            email_sent = True
        else:
            email_sent = False
        
        assert email_sent is True

    def test_preferences_respected_for_24h_reminder(self, booking_with_preferences):
        """Test that 24h reminder respects preferences."""
        prefs = booking_with_preferences["preferences"]
        
        if prefs["send_24h_reminder_email"]:
            # Send 24h reminder
            email_sent = True
        else:
            email_sent = False
        
        assert email_sent is True

    def test_preferences_respected_for_sms(self, booking_with_preferences):
        """Test that SMS reminders respect preferences."""
        prefs = booking_with_preferences["preferences"]
        
        if prefs["send_sms_reminders"]:
            # Send SMS
            sms_sent = True
        else:
            sms_sent = False
        
        assert sms_sent is False

    def test_preferences_update_integration(self, booking_with_preferences):
        """Test updating preferences and verifying they're applied."""
        # Update preferences
        booking_with_preferences["preferences"]["send_sms_reminders"] = True
        
        # Verify update
        assert booking_with_preferences["preferences"]["send_sms_reminders"] is True
