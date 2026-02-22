"""
Tests for review reminder functionality
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, AsyncMock
from bson import ObjectId

from app.tasks.review_reminder_task import (
    send_review_reminders,
    process_booking_reminder,
    send_email_reminder,
    send_sms_reminder,
    calculate_review_analytics,
    batch_review_notifications
)


@pytest.fixture
def mock_db():
    """Mock database"""
    db = MagicMock()
    db.review_settings = MagicMock()
    db.bookings = MagicMock()
    db.reviews = MagicMock()
    db.review_reminders = MagicMock()
    db.clients = MagicMock()
    db.tenants = MagicMock()
    db.review_analytics = MagicMock()
    return db


@pytest.fixture
def sample_tenant():
    """Sample tenant data"""
    return {
        "_id": ObjectId(),
        "tenant_id": "tenant-123",
        "name": "Test Salon",
        "owner_email": "owner@example.com"
    }


@pytest.fixture
def sample_booking():
    """Sample booking data"""
    return {
        "_id": ObjectId(),
        "tenant_id": "tenant-123",
        "client_id": "client-123",
        "client_email": "client@example.com",
        "client_phone": "+1234567890",
        "status": "completed",
        "completed_at": datetime.utcnow() - timedelta(hours=24),
        "service_id": "service-123",
        "service_name": "Haircut",
        "stylist_id": "stylist-123",
        "stylist_name": "John Doe"
    }


@pytest.fixture
def sample_client():
    """Sample client data"""
    return {
        "_id": ObjectId(),
        "tenant_id": "tenant-123",
        "name": "John Client",
        "email": "client@example.com",
        "phone": "+1234567890"
    }


@pytest.fixture
def sample_review_settings():
    """Sample review settings"""
    return {
        "_id": ObjectId(),
        "tenant_id": "tenant-123",
        "reminder_enabled": True,
        "reminder_delay_hours": 24,
        "incentive_enabled": False,
        "notification_enabled": True,
        "reminder_email_template": "default",
        "reminder_sms_template": "default"
    }


class TestSendReviewReminders:
    """Tests for send_review_reminders task"""

    def test_send_review_reminders_success(self, mock_db, sample_tenant, sample_booking, sample_review_settings):
        """Test successful review reminder sending"""
        # Setup mocks
        mock_db.review_settings.find.return_value = [sample_review_settings]
        mock_db.bookings.find.return_value = [sample_booking]
        mock_db.reviews.find_one.return_value = None  # No existing review
        mock_db.review_reminders.find_one.return_value = None  # No existing reminder
        mock_db.clients.find_one.return_value = None

        with patch('app.tasks.review_reminder_task.get_db', return_value=mock_db):
            with patch('app.tasks.review_reminder_task.process_booking_reminder'):
                result = send_review_reminders()

        assert result["status"] == "success"
        assert "Review reminders processed" in result["message"]

    def test_send_review_reminders_disabled(self, mock_db):
        """Test that reminders are not sent when disabled"""
        settings = {
            "tenant_id": "tenant-123",
            "reminder_enabled": False
        }
        mock_db.review_settings.find.return_value = [settings]

        with patch('app.tasks.review_reminder_task.get_db', return_value=mock_db):
            result = send_review_reminders()

        assert result["status"] == "success"
        # Bookings should not be queried if reminders are disabled
        mock_db.bookings.find.assert_not_called()

    def test_send_review_reminders_no_settings(self, mock_db):
        """Test handling when no settings exist"""
        mock_db.review_settings.find.return_value = []

        with patch('app.tasks.review_reminder_task.get_db', return_value=mock_db):
            result = send_review_reminders()

        assert result["status"] == "success"

    def test_send_review_reminders_custom_delay(self, mock_db, sample_booking, sample_review_settings):
        """Test custom reminder delay"""
        settings = sample_review_settings.copy()
        settings["reminder_delay_hours"] = 48

        mock_db.review_settings.find.return_value = [settings]
        mock_db.bookings.find.return_value = [sample_booking]

        with patch('app.tasks.review_reminder_task.get_db', return_value=mock_db):
            with patch('app.tasks.review_reminder_task.process_booking_reminder'):
                send_review_reminders()

        # Verify the correct time window was used
        call_args = mock_db.bookings.find.call_args
        query = call_args[0][0]
        assert "completed_at" in query


class TestProcessBookingReminder:
    """Tests for process_booking_reminder function"""

    def test_process_booking_reminder_success(self, mock_db, sample_booking, sample_client, sample_review_settings):
        """Test successful booking reminder processing"""
        mock_db.reviews.find_one.return_value = None
        mock_db.review_reminders.find_one.return_value = None
        mock_db.review_settings.find_one.return_value = sample_review_settings
        mock_db.clients.find_one.return_value = sample_client

        with patch('app.tasks.review_reminder_task.send_email_reminder'):
            with patch('app.tasks.review_reminder_task.send_sms_reminder'):
                process_booking_reminder(mock_db, "tenant-123", sample_booking)

        # Verify reminder was recorded
        mock_db.review_reminders.update_one.assert_called_once()

    def test_process_booking_reminder_existing_review(self, mock_db, sample_booking, sample_review_settings):
        """Test that reminder is not sent if review already exists"""
        existing_review = {"_id": ObjectId(), "booking_id": sample_booking["_id"]}
        mock_db.reviews.find_one.return_value = existing_review

        with patch('app.tasks.review_reminder_task.send_email_reminder') as mock_email:
            with patch('app.tasks.review_reminder_task.send_sms_reminder') as mock_sms:
                process_booking_reminder(mock_db, "tenant-123", sample_booking)

        # Email and SMS should not be sent
        mock_email.assert_not_called()
        mock_sms.assert_not_called()

    def test_process_booking_reminder_already_sent(self, mock_db, sample_booking, sample_review_settings):
        """Test that reminder is not sent if already sent"""
        existing_reminder = {
            "booking_id": str(sample_booking["_id"]),
            "reminder_sent": True
        }
        mock_db.reviews.find_one.return_value = None
        mock_db.review_reminders.find_one.return_value = existing_reminder

        with patch('app.tasks.review_reminder_task.send_email_reminder') as mock_email:
            with patch('app.tasks.review_reminder_task.send_sms_reminder') as mock_sms:
                process_booking_reminder(mock_db, "tenant-123", sample_booking)

        # Email and SMS should not be sent
        mock_email.assert_not_called()
        mock_sms.assert_not_called()

    def test_process_booking_reminder_no_email(self, mock_db, sample_booking, sample_review_settings):
        """Test reminder processing when client has no email"""
        booking = sample_booking.copy()
        booking["client_email"] = None

        mock_db.reviews.find_one.return_value = None
        mock_db.review_reminders.find_one.return_value = None
        mock_db.review_settings.find_one.return_value = sample_review_settings
        mock_db.clients.find_one.return_value = None

        with patch('app.tasks.review_reminder_task.send_email_reminder') as mock_email:
            with patch('app.tasks.review_reminder_task.send_sms_reminder'):
                process_booking_reminder(mock_db, "tenant-123", booking)

        # Email should not be sent
        mock_email.assert_not_called()

    def test_process_booking_reminder_no_phone(self, mock_db, sample_booking, sample_review_settings):
        """Test reminder processing when client has no phone"""
        booking = sample_booking.copy()
        booking["client_phone"] = None

        mock_db.reviews.find_one.return_value = None
        mock_db.review_reminders.find_one.return_value = None
        mock_db.review_settings.find_one.return_value = sample_review_settings
        mock_db.clients.find_one.return_value = None

        with patch('app.tasks.review_reminder_task.send_email_reminder'):
            with patch('app.tasks.review_reminder_task.send_sms_reminder') as mock_sms:
                process_booking_reminder(mock_db, "tenant-123", booking)

        # SMS should not be sent
        mock_sms.assert_not_called()


class TestSendEmailReminder:
    """Tests for send_email_reminder function"""

    def test_send_email_reminder_success(self, mock_db, sample_review_settings):
        """Test successful email reminder sending"""
        with patch('app.tasks.review_reminder_task.EmailService') as mock_email_service:
            mock_service_instance = MagicMock()
            mock_email_service.return_value = mock_service_instance

            send_email_reminder(
                tenant_id="tenant-123",
                client_email="client@example.com",
                client_name="John Doe",
                booking_id="booking-123",
                settings=sample_review_settings
            )

            # Verify email was sent
            mock_service_instance.send_email.assert_called_once()
            call_args = mock_service_instance.send_email.call_args
            assert call_args[1]["to"] == "client@example.com"
            assert "review" in call_args[1]["subject"].lower()

    def test_send_email_reminder_includes_review_link(self, mock_db, sample_review_settings):
        """Test that email reminder includes review link"""
        with patch('app.tasks.review_reminder_task.EmailService') as mock_email_service:
            mock_service_instance = MagicMock()
            mock_email_service.return_value = mock_service_instance

            send_email_reminder(
                tenant_id="tenant-123",
                client_email="client@example.com",
                client_name="John Doe",
                booking_id="booking-123",
                settings=sample_review_settings
            )

            call_args = mock_service_instance.send_email.call_args
            body = call_args[1]["body"]
            assert "booking_id=booking-123" in body or "booking-123" in body


class TestSendSMSReminder:
    """Tests for send_sms_reminder function"""

    def test_send_sms_reminder_success(self, mock_db, sample_review_settings):
        """Test successful SMS reminder sending"""
        with patch('app.tasks.review_reminder_task.SMSService') as mock_sms_service:
            mock_service_instance = MagicMock()
            mock_sms_service.return_value = mock_service_instance

            send_sms_reminder(
                tenant_id="tenant-123",
                client_phone="+1234567890",
                client_name="John Doe",
                booking_id="booking-123",
                settings=sample_review_settings
            )

            # Verify SMS was sent
            mock_service_instance.send_sms.assert_called_once()
            call_args = mock_service_instance.send_sms.call_args
            assert call_args[1]["phone"] == "+1234567890"

    def test_send_sms_reminder_includes_review_link(self, mock_db, sample_review_settings):
        """Test that SMS reminder includes review link"""
        with patch('app.tasks.review_reminder_task.SMSService') as mock_sms_service:
            mock_service_instance = MagicMock()
            mock_sms_service.return_value = mock_service_instance

            send_sms_reminder(
                tenant_id="tenant-123",
                client_phone="+1234567890",
                client_name="John Doe",
                booking_id="booking-123",
                settings=sample_review_settings
            )

            call_args = mock_service_instance.send_sms.call_args
            message = call_args[1]["message"]
            assert "booking-123" in message or "review" in message.lower()


class TestCalculateReviewAnalytics:
    """Tests for calculate_review_analytics task"""

    def test_calculate_review_analytics_success(self, mock_db, sample_tenant):
        """Test successful analytics calculation"""
        mock_db.tenants.find.return_value = [sample_tenant]
        mock_db.reviews.find.return_value = [
            {
                "_id": ObjectId(),
                "tenant_id": "tenant-123",
                "rating": 5,
                "status": "approved",
                "response": {"text": "Thank you"}
            },
            {
                "_id": ObjectId(),
                "tenant_id": "tenant-123",
                "rating": 4,
                "status": "approved"
            }
        ]

        with patch('app.tasks.review_reminder_task.get_db', return_value=mock_db):
            result = calculate_review_analytics()

        assert result["status"] == "success"
        assert "Analytics calculated" in result["message"]

    def test_calculate_review_analytics_no_reviews(self, mock_db, sample_tenant):
        """Test analytics calculation with no reviews"""
        mock_db.tenants.find.return_value = [sample_tenant]
        mock_db.reviews.find.return_value = []

        with patch('app.tasks.review_reminder_task.get_db', return_value=mock_db):
            result = calculate_review_analytics()

        assert result["status"] == "success"

    def test_calculate_review_analytics_stores_data(self, mock_db, sample_tenant):
        """Test that analytics are stored in database"""
        reviews = [
            {
                "_id": ObjectId(),
                "tenant_id": "tenant-123",
                "rating": 5,
                "status": "approved",
                "response": {"text": "Thank you"}
            },
            {
                "_id": ObjectId(),
                "tenant_id": "tenant-123",
                "rating": 4,
                "status": "approved"
            },
            {
                "_id": ObjectId(),
                "tenant_id": "tenant-123",
                "rating": 3,
                "status": "approved"
            }
        ]

        mock_db.tenants.find.return_value = [sample_tenant]
        mock_db.reviews.find.return_value = reviews

        with patch('app.tasks.review_reminder_task.get_db', return_value=mock_db):
            calculate_review_analytics()

        # Verify analytics were stored
        mock_db.review_analytics.update_one.assert_called()


class TestBatchReviewNotifications:
    """Tests for batch_review_notifications task"""

    def test_batch_review_notifications_success(self, mock_db, sample_tenant):
        """Test successful batch notification sending"""
        settings = {
            "tenant_id": "tenant-123",
            "notification_enabled": True,
            "notification_digest": True
        }

        mock_db.review_settings.find.return_value = [settings]
        mock_db.reviews.find.return_value = [
            {
                "_id": ObjectId(),
                "tenant_id": "tenant-123",
                "client_name": "John Doe",
                "rating": 5,
                "comment": "Great service!",
                "status": "pending"
            }
        ]
        mock_db.tenants.find_one.return_value = sample_tenant

        with patch('app.tasks.review_reminder_task.get_db', return_value=mock_db):
            with patch('app.tasks.review_reminder_task.EmailService'):
                result = batch_review_notifications()

        assert result["status"] == "success"

    def test_batch_review_notifications_no_new_reviews(self, mock_db):
        """Test batch notifications when no new reviews"""
        settings = {
            "tenant_id": "tenant-123",
            "notification_enabled": True,
            "notification_digest": True
        }

        mock_db.review_settings.find.return_value = [settings]
        mock_db.reviews.find.return_value = []

        with patch('app.tasks.review_reminder_task.get_db', return_value=mock_db):
            result = batch_review_notifications()

        assert result["status"] == "success"

    def test_batch_review_notifications_disabled(self, mock_db):
        """Test that notifications are not sent when disabled"""
        settings = {
            "tenant_id": "tenant-123",
            "notification_enabled": False,
            "notification_digest": True
        }

        mock_db.review_settings.find.return_value = [settings]

        with patch('app.tasks.review_reminder_task.get_db', return_value=mock_db):
            result = batch_review_notifications()

        assert result["status"] == "success"
        # Reviews should not be queried if notifications are disabled
        mock_db.reviews.find.assert_not_called()


class TestReminderIntegration:
    """Integration tests for reminder system"""

    def test_full_reminder_workflow(self, mock_db, sample_booking, sample_client, sample_review_settings):
        """Test complete reminder workflow"""
        mock_db.review_settings.find.return_value = [sample_review_settings]
        mock_db.bookings.find.return_value = [sample_booking]
        mock_db.reviews.find_one.return_value = None
        mock_db.review_reminders.find_one.return_value = None
        mock_db.review_settings.find_one.return_value = sample_review_settings
        mock_db.clients.find_one.return_value = sample_client

        with patch('app.tasks.review_reminder_task.get_db', return_value=mock_db):
            with patch('app.tasks.review_reminder_task.send_email_reminder'):
                with patch('app.tasks.review_reminder_task.send_sms_reminder'):
                    result = send_review_reminders()

        assert result["status"] == "success"
        # Verify reminder was recorded
        mock_db.review_reminders.update_one.assert_called()

    def test_reminder_prevents_duplicates(self, mock_db, sample_booking, sample_review_settings):
        """Test that duplicate reminders are prevented"""
        existing_reminder = {
            "booking_id": str(sample_booking["_id"]),
            "reminder_sent": True,
            "reminder_sent_at": datetime.utcnow()
        }

        mock_db.review_settings.find.return_value = [sample_review_settings]
        mock_db.bookings.find.return_value = [sample_booking]
        mock_db.reviews.find_one.return_value = None
        mock_db.review_reminders.find_one.return_value = existing_reminder

        with patch('app.tasks.review_reminder_task.get_db', return_value=mock_db):
            with patch('app.tasks.review_reminder_task.send_email_reminder') as mock_email:
                with patch('app.tasks.review_reminder_task.send_sms_reminder') as mock_sms:
                    send_review_reminders()

        # Email and SMS should not be sent
        mock_email.assert_not_called()
        mock_sms.assert_not_called()
