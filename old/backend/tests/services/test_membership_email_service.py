"""
Tests for membership email service.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.membership_email_service import MembershipEmailService


@pytest.fixture
def email_service():
    """Create email service instance"""
    return MembershipEmailService()


@pytest.fixture
def sample_context():
    """Sample context for email rendering"""
    return {
        "client_name": "John Doe",
        "plan_name": "Gold Membership",
        "plan_price": "99.99",
        "billing_cycle": "monthly",
        "benefits": ["20% off services", "Priority booking"],
        "discount_percentage": 20,
        "start_date": "January 15, 2025",
        "next_billing_date": "February 15, 2025",
        "dashboard_url": "https://example.com/dashboard",
        "salon_name": "Beauty Salon",
        "currency_symbol": "₦",
    }


class TestMembershipEmailService:
    """Test membership email service"""

    @pytest.mark.asyncio
    async def test_send_welcome_email(self, email_service):
        """Test sending welcome email"""
        with patch.object(email_service.email_service, 'send_email', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True

            result = await email_service.send_welcome_email(
                client_email="john@example.com",
                client_name="John Doe",
                plan_name="Gold Membership",
                plan_price=99.99,
                billing_cycle="monthly",
                benefits=["20% off services", "Priority booking"],
                discount_percentage=20,
                start_date=datetime.now(),
                next_billing_date=datetime.now() + timedelta(days=30),
                dashboard_url="https://example.com/dashboard",
                salon_name="Beauty Salon",
                currency_symbol="₦",
            )

            assert result is True
            mock_send.assert_called_once()
            call_args = mock_send.call_args
            assert call_args[1]["to"] == "john@example.com"
            assert "Welcome" in call_args[1]["subject"]

    @pytest.mark.asyncio
    async def test_send_renewal_reminder_7day(self, email_service):
        """Test sending 7-day renewal reminder"""
        with patch.object(email_service.email_service, 'send_email', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True

            result = await email_service.send_renewal_reminder_7day(
                client_email="john@example.com",
                client_name="John Doe",
                plan_name="Gold Membership",
                plan_price=99.99,
                billing_cycle="monthly",
                discount_percentage=20,
                renewal_date=datetime.now() + timedelta(days=7),
                manage_url="https://example.com/manage",
                pause_url="https://example.com/pause",
                salon_name="Beauty Salon",
                currency_symbol="₦",
            )

            assert result is True
            mock_send.assert_called_once()
            call_args = mock_send.call_args
            assert "7 Days" in call_args[1]["subject"]

    @pytest.mark.asyncio
    async def test_send_renewal_reminder_1day(self, email_service):
        """Test sending 1-day renewal reminder"""
        with patch.object(email_service.email_service, 'send_email', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True

            result = await email_service.send_renewal_reminder_1day(
                client_email="john@example.com",
                client_name="John Doe",
                plan_name="Gold Membership",
                plan_price=99.99,
                billing_cycle="monthly",
                discount_percentage=20,
                renewal_date=datetime.now() + timedelta(days=1),
                manage_url="https://example.com/manage",
                cancel_url="https://example.com/cancel",
                salon_name="Beauty Salon",
                currency_symbol="₦",
            )

            assert result is True
            mock_send.assert_called_once()
            call_args = mock_send.call_args
            assert "Tomorrow" in call_args[1]["subject"]

    @pytest.mark.asyncio
    async def test_send_renewal_confirmation(self, email_service):
        """Test sending renewal confirmation"""
        with patch.object(email_service.email_service, 'send_email', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True

            result = await email_service.send_renewal_confirmation(
                client_email="john@example.com",
                client_name="John Doe",
                plan_name="Gold Membership",
                plan_price=99.99,
                billing_cycle="monthly",
                transaction_id="txn_123456",
                renewal_date=datetime.now(),
                next_renewal_date=datetime.now() + timedelta(days=30),
                dashboard_url="https://example.com/dashboard",
                salon_name="Beauty Salon",
                currency_symbol="₦",
            )

            assert result is True
            mock_send.assert_called_once()
            call_args = mock_send.call_args
            assert "Renewed" in call_args[1]["subject"]

    @pytest.mark.asyncio
    async def test_send_payment_failure_notification(self, email_service):
        """Test sending payment failure notification"""
        with patch.object(email_service.email_service, 'send_email', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True

            result = await email_service.send_payment_failure_notification(
                client_email="john@example.com",
                client_name="John Doe",
                plan_name="Gold Membership",
                plan_price=99.99,
                billing_cycle="monthly",
                failure_reason="Insufficient funds",
                failure_date=datetime.now(),
                grace_period_end_date=datetime.now() + timedelta(days=14),
                update_payment_url="https://example.com/update-payment",
                contact_support_url="https://example.com/support",
                salon_name="Beauty Salon",
                currency_symbol="₦",
            )

            assert result is True
            mock_send.assert_called_once()
            call_args = mock_send.call_args
            assert "Failed" in call_args[1]["subject"]

    @pytest.mark.asyncio
    async def test_send_cancellation_confirmation(self, email_service):
        """Test sending cancellation confirmation"""
        with patch.object(email_service.email_service, 'send_email', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True

            result = await email_service.send_cancellation_confirmation(
                client_email="john@example.com",
                client_name="John Doe",
                plan_name="Gold Membership",
                cancellation_reason="Too expensive",
                cancellation_date=datetime.now(),
                access_until_date=datetime.now() + timedelta(days=30),
                total_paid=299.97,
                total_savings=150.00,
                rejoin_url="https://example.com/rejoin",
                feedback_url="https://example.com/feedback",
                salon_name="Beauty Salon",
                currency_symbol="₦",
            )

            assert result is True
            mock_send.assert_called_once()
            call_args = mock_send.call_args
            assert "Cancelled" in call_args[1]["subject"]

    @pytest.mark.asyncio
    async def test_send_pause_confirmation(self, email_service):
        """Test sending pause confirmation"""
        with patch.object(email_service.email_service, 'send_email', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True

            result = await email_service.send_pause_confirmation(
                client_email="john@example.com",
                client_name="John Doe",
                plan_name="Gold Membership",
                pause_date=datetime.now(),
                original_end_date=datetime.now() + timedelta(days=30),
                dashboard_url="https://example.com/dashboard",
                salon_name="Beauty Salon",
            )

            assert result is True
            mock_send.assert_called_once()
            call_args = mock_send.call_args
            assert "Paused" in call_args[1]["subject"]

    @pytest.mark.asyncio
    async def test_send_resume_confirmation(self, email_service):
        """Test sending resume confirmation"""
        with patch.object(email_service.email_service, 'send_email', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True

            result = await email_service.send_resume_confirmation(
                client_email="john@example.com",
                client_name="John Doe",
                plan_name="Gold Membership",
                resume_date=datetime.now(),
                new_end_date=datetime.now() + timedelta(days=30),
                billing_cycle="monthly",
                dashboard_url="https://example.com/dashboard",
                salon_name="Beauty Salon",
            )

            assert result is True
            mock_send.assert_called_once()
            call_args = mock_send.call_args
            assert "Resumed" in call_args[1]["subject"]

    @pytest.mark.asyncio
    async def test_send_grace_period_warning(self, email_service):
        """Test sending grace period warning"""
        with patch.object(email_service.email_service, 'send_email', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True

            now = datetime.now()
            result = await email_service.send_grace_period_warning(
                client_email="john@example.com",
                client_name="John Doe",
                plan_name="Gold Membership",
                plan_price=99.99,
                grace_period_end_date=now + timedelta(days=14),
                retry_date_1=now + timedelta(days=2),
                retry_date_2=now + timedelta(days=4),
                retry_date_3=now + timedelta(days=6),
                cancellation_date=now + timedelta(days=14),
                update_payment_url="https://example.com/update-payment",
                contact_support_url="https://example.com/support",
                salon_name="Beauty Salon",
                currency_symbol="₦",
            )

            assert result is True
            mock_send.assert_called_once()
            call_args = mock_send.call_args
            assert "Urgent" in call_args[1]["subject"]

    def test_render_template_welcome(self, email_service, sample_context):
        """Test rendering welcome email template"""
        html = email_service._render_template("membership_welcome.html", sample_context)
        
        assert "Welcome to Your Membership" in html
        assert "John Doe" in html
        assert "Gold Membership" in html
        assert "99.99" in html
        assert "20% off services" in html

    def test_render_template_renewal_reminder_7day(self, email_service, sample_context):
        """Test rendering 7-day renewal reminder template"""
        html = email_service._render_template("membership_renewal_reminder_7day.html", sample_context)
        
        assert "Renews Soon" in html
        assert "John Doe" in html
        assert "7 Days" in html or "renewal" in html.lower()

    def test_render_template_renewal_confirmation(self, email_service, sample_context):
        """Test rendering renewal confirmation template"""
        sample_context["transaction_id"] = "txn_123456"
        html = email_service._render_template("membership_renewal_confirmation.html", sample_context)
        
        assert "Successfully" in html or "Renewed" in html
        assert "John Doe" in html

    def test_render_template_payment_failure(self, email_service, sample_context):
        """Test rendering payment failure template"""
        sample_context["failure_reason"] = "Insufficient funds"
        sample_context["failure_date"] = "January 15, 2025"
        sample_context["grace_period_end_date"] = "January 29, 2025"
        html = email_service._render_template("membership_payment_failure.html", sample_context)
        
        assert "Failed" in html or "Payment" in html
        assert "John Doe" in html

    def test_render_template_cancellation(self, email_service, sample_context):
        """Test rendering cancellation template"""
        sample_context["cancellation_reason"] = "Too expensive"
        sample_context["cancellation_date"] = "January 15, 2025"
        sample_context["access_until_date"] = "February 15, 2025"
        sample_context["total_paid"] = "299.97"
        sample_context["total_savings"] = "150.00"
        html = email_service._render_template("membership_cancellation_confirmation.html", sample_context)
        
        assert "Cancelled" in html
        assert "John Doe" in html

    def test_render_template_pause_resume(self, email_service, sample_context):
        """Test rendering pause/resume template"""
        sample_context["action"] = "pause"
        sample_context["action_date"] = "January 15, 2025"
        sample_context["original_end_date"] = "February 15, 2025"
        html = email_service._render_template("membership_pause_resume_confirmation.html", sample_context)
        
        assert "Paused" in html or "Status" in html
        assert "John Doe" in html

    def test_render_template_grace_period(self, email_service, sample_context):
        """Test rendering grace period warning template"""
        sample_context["grace_period_end_date"] = "January 29, 2025"
        sample_context["retry_date_1"] = "January 17, 2025"
        sample_context["retry_date_2"] = "January 19, 2025"
        sample_context["retry_date_3"] = "January 21, 2025"
        sample_context["cancellation_date"] = "January 29, 2025"
        html = email_service._render_template("membership_grace_period_warning.html", sample_context)
        
        assert "Urgent" in html or "Payment" in html
        assert "John Doe" in html

    @pytest.mark.asyncio
    async def test_send_email_with_error_handling(self, email_service):
        """Test email service error handling"""
        with patch.object(email_service.email_service, 'send_email', new_callable=AsyncMock) as mock_send:
            mock_send.side_effect = Exception("Email service error")

            result = await email_service.send_welcome_email(
                client_email="john@example.com",
                client_name="John Doe",
                plan_name="Gold Membership",
                plan_price=99.99,
                billing_cycle="monthly",
                benefits=["20% off services"],
                discount_percentage=20,
                start_date=datetime.now(),
                next_billing_date=datetime.now() + timedelta(days=30),
                dashboard_url="https://example.com/dashboard",
                salon_name="Beauty Salon",
                currency_symbol="₦",
            )

            # Should return False on error
            assert result is False

    def test_template_file_exists(self, email_service):
        """Test that all template files exist"""
        templates = [
            "membership_welcome.html",
            "membership_renewal_reminder_7day.html",
            "membership_renewal_reminder_1day.html",
            "membership_renewal_confirmation.html",
            "membership_payment_failure.html",
            "membership_cancellation_confirmation.html",
            "membership_pause_resume_confirmation.html",
            "membership_grace_period_warning.html",
        ]

        for template in templates:
            try:
                email_service.env.get_template(template)
            except Exception as e:
                pytest.fail(f"Template {template} not found: {str(e)}")
