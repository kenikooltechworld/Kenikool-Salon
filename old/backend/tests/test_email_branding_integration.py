"""
Tests for Email Branding Service Integration with Email Service
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
from fastapi import HTTPException

from app.services.email_service import EmailService
from app.services.email_branding_service import EmailBrandingService
from app.schemas.white_label import (
    WhiteLabelConfig,
    WhiteLabelBranding,
    WhiteLabelDomain,
    WhiteLabelFeatures,
)


@pytest.fixture
def white_label_config():
    """Create a test white label configuration"""
    return WhiteLabelConfig(
        id="wl_123",
        tenant_id="tenant_123",
        branding=WhiteLabelBranding(
            logo_url="https://example.com/logo.png",
            primary_color="#FF6B6B",
            secondary_color="#4ECDC4",
            company_name="Test Salon",
            tagline="Your Beauty Destination",
        ),
        domain=WhiteLabelDomain(
            custom_domain="booking.testsalon.com",
            ssl_enabled=True,
            dns_configured=True,
        ),
        features=WhiteLabelFeatures(
            hide_powered_by=True,
            custom_support_email="support@testsalon.com",
            custom_support_phone="+1234567890",
            custom_terms_url="https://testsalon.com/terms",
            custom_privacy_url="https://testsalon.com/privacy",
        ),
        is_active=True,
        created_at=datetime.utcnow(),
    )


@pytest.fixture
def email_service():
    """Create email service instance"""
    with patch('app.services.email_service.settings'):
        service = EmailService()
        service.api_key = "test-key"
        service.from_email = "noreply@kenikool.com"
        return service


@pytest.fixture
def email_branding_service():
    """Create email branding service instance"""
    return EmailBrandingService()


class TestEmailBrandingIntegration:
    """Test email branding integration with email service"""

    @pytest.mark.asyncio
    async def test_set_white_label_config(self, email_service, white_label_config):
        """Test setting white label configuration"""
        email_service.set_white_label_config(white_label_config)
        assert email_service.white_label_config == white_label_config

    @pytest.mark.asyncio
    async def test_set_tenant_context(self, email_service, white_label_config):
        """Test setting tenant context"""
        email_service.set_tenant_context("tenant_123", white_label_config)
        assert email_service.tenant_id == "tenant_123"
        assert email_service.white_label_config == white_label_config

    @pytest.mark.asyncio
    async def test_send_verification_email_with_branding(
        self, email_service, white_label_config
    ):
        """Test sending verification email with white label branding"""
        email_service.set_white_label_config(white_label_config)

        with patch.object(email_service, "send_email", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True

            result = await email_service.send_verification_email(
                to="user@example.com",
                user_name="John Doe",
                verification_token="test-token-123",
            )

            assert result is True
            mock_send.assert_called_once()

            # Check that the call includes branded from address
            call_args = mock_send.call_args
            # Check positional or keyword arguments
            if len(call_args[0]) >= 4:
                # Positional: to, subject, html, text, from_email
                assert "support@testsalon.com" in call_args[0][4]
                assert "Test Salon" in call_args[0][1]
            else:
                # Keyword arguments
                assert "support@testsalon.com" in call_args[1].get("from_email", "")
                assert "Test Salon" in call_args[1].get("subject", "")

    @pytest.mark.asyncio
    async def test_send_verification_email_without_branding(self, email_service):
        """Test sending verification email without white label branding"""
        with patch.object(email_service, "send_email", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True

            result = await email_service.send_verification_email(
                to="user@example.com",
                user_name="John Doe",
                verification_token="test-token-123",
            )

            assert result is True
            mock_send.assert_called_once()

            # Check that default branding is used
            call_args = mock_send.call_args
            if len(call_args[0]) >= 2:
                assert "Kenikool Salon" in call_args[0][1]
            else:
                assert "Kenikool Salon" in call_args[1].get("subject", "")

    @pytest.mark.asyncio
    async def test_send_booking_confirmation_with_branding(
        self, email_service, white_label_config
    ):
        """Test sending booking confirmation with white label branding"""
        email_service.set_white_label_config(white_label_config)

        with patch.object(email_service, "send_email", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True

            result = await email_service.send_booking_confirmation_email(
                to="client@example.com",
                client_name="Jane Smith",
                service_name="Hair Cut",
                booking_date="2024-02-15",
                booking_time="10:00 AM",
            )

            assert result is True
            mock_send.assert_called_once()

            # Check that the call includes branded from address
            call_args = mock_send.call_args
            if len(call_args[0]) >= 4:
                assert "support@testsalon.com" in call_args[0][4]
                assert "Test Salon" in call_args[0][1]
            else:
                assert "support@testsalon.com" in call_args[1].get("from_email", "")
                assert "Test Salon" in call_args[1].get("subject", "")

    @pytest.mark.asyncio
    async def test_send_booking_reminder_with_branding(
        self, email_service, white_label_config
    ):
        """Test sending booking reminder with white label branding"""
        email_service.set_white_label_config(white_label_config)

        with patch.object(email_service, "send_email", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True

            result = await email_service.send_booking_reminder_email(
                to="client@example.com",
                client_name="Jane Smith",
                service_name="Hair Cut",
                booking_date="2024-02-15",
                booking_time="10:00 AM",
            )

            assert result is True
            mock_send.assert_called_once()

            # Check that the call includes branded from address
            call_args = mock_send.call_args
            if len(call_args[0]) >= 4:
                assert "support@testsalon.com" in call_args[0][4]
                assert "Reminder" in call_args[0][1]
            else:
                assert "support@testsalon.com" in call_args[1].get("from_email", "")
                assert "Reminder" in call_args[1].get("subject", "")

    @pytest.mark.asyncio
    async def test_send_branded_email(self, email_service, white_label_config):
        """Test sending a generic branded email"""
        email_service.set_white_label_config(white_label_config)

        with patch.object(email_service, "send_email", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True

            result = await email_service.send_branded_email(
                to="user@example.com",
                subject="Important Update",
                html="<p>This is important</p>",
                text="This is important",
            )

            assert result is True
            mock_send.assert_called_once()

            # Check that subject includes company name
            call_args = mock_send.call_args
            if len(call_args[0]) >= 2:
                assert "Test Salon" in call_args[0][1]
            else:
                assert "Test Salon" in call_args[1].get("subject", "")


class TestEmailBrandingService:
    """Test email branding service functionality"""

    @pytest.mark.asyncio
    async def test_get_branded_from_address_with_custom_email(
        self, email_branding_service, white_label_config
    ):
        """Test getting branded from address with custom email"""
        from_address = await email_branding_service.get_branded_from_address(
            white_label_config
        )

        assert "support@testsalon.com" in from_address
        assert "Test Salon" in from_address

    @pytest.mark.asyncio
    async def test_get_branded_from_address_without_custom_email(
        self, email_branding_service
    ):
        """Test getting branded from address without custom email"""
        config = WhiteLabelConfig(
            id="wl_123",
            tenant_id="tenant_123",
            branding=WhiteLabelBranding(company_name="Test Salon"),
            domain=WhiteLabelDomain(),
            features=WhiteLabelFeatures(),
            is_active=True,
            created_at=datetime.utcnow(),
        )

        from_address = await email_branding_service.get_branded_from_address(config)

        assert "noreply@kenikool.com" in from_address

    @pytest.mark.asyncio
    async def test_get_branded_subject(self, email_branding_service, white_label_config):
        """Test getting branded subject line"""
        subject = await email_branding_service.get_branded_subject(
            "Welcome to our platform", white_label_config
        )

        assert "Test Salon" in subject
        assert "Welcome to our platform" in subject

    @pytest.mark.asyncio
    async def test_apply_branding_to_template_verification(
        self, email_branding_service, white_label_config
    ):
        """Test applying branding to verification template"""
        template_data = {
            "user_name": "John Doe",
            "verification_url": "https://example.com/verify?token=123",
        }

        html = await email_branding_service.apply_branding_to_template(
            "verification", white_label_config, template_data
        )

        # Check that branding is applied
        assert "Test Salon" in html
        assert "#FF6B6B" in html or "linear-gradient" in html
        assert "support@testsalon.com" in html
        assert "John Doe" in html

    @pytest.mark.asyncio
    async def test_apply_branding_to_template_booking_confirmation(
        self, email_branding_service, white_label_config
    ):
        """Test applying branding to booking confirmation template"""
        template_data = {
            "client_name": "Jane Smith",
            "service_name": "Hair Cut",
            "booking_date": "2024-02-15",
            "booking_time": "10:00 AM",
        }

        html = await email_branding_service.apply_branding_to_template(
            "booking_confirmation", white_label_config, template_data
        )

        # Check that branding is applied
        assert "Test Salon" in html
        assert "Jane Smith" in html
        assert "Hair Cut" in html
        assert "2024-02-15" in html

    @pytest.mark.asyncio
    async def test_apply_branding_to_html(
        self, email_branding_service, white_label_config
    ):
        """Test applying branding to raw HTML"""
        html = "<p>Default content</p>"

        branded_html = await email_branding_service.apply_branding_to_html(
            html, white_label_config
        )

        # Should return HTML (may or may not be modified depending on content)
        assert isinstance(branded_html, str)

    @pytest.mark.asyncio
    async def test_validate_email_domain_with_spf(
        self, email_branding_service
    ):
        """Test email domain validation with SPF record"""
        with patch("app.services.email_branding_service.dns.resolver.resolve") as mock_resolve:
            # Mock SPF record
            mock_record = MagicMock()
            mock_record.__str__ = MagicMock(return_value="v=spf1 include:_spf.google.com ~all")
            mock_resolve.return_value = [mock_record]

            result = await email_branding_service.validate_email_domain(
                "example.com"
            )

            assert result["domain"] == "example.com"
            assert result["spf_configured"] is True

    @pytest.mark.asyncio
    async def test_validate_email_domain_invalid_format(
        self, email_branding_service
    ):
        """Test email domain validation with invalid format"""
        result = await email_branding_service.validate_email_domain(
            "invalid domain"
        )

        assert result["valid"] is False
        assert len(result["issues"]) > 0

    @pytest.mark.asyncio
    async def test_apply_branding_replaces_company_name(
        self, email_branding_service, white_label_config
    ):
        """Test that branding replaces default company name"""
        html = "<h1>Kenikool Salon</h1>"

        branded_html = email_branding_service._apply_branding(
            html, white_label_config, {}
        )

        assert "Test Salon" in branded_html
        assert "Kenikool Salon" not in branded_html

    @pytest.mark.asyncio
    async def test_apply_branding_replaces_colors(
        self, email_branding_service, white_label_config
    ):
        """Test that branding replaces default colors"""
        html = "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)"

        branded_html = email_branding_service._apply_branding(
            html, white_label_config, {}
        )

        assert "#FF6B6B" in branded_html or "#4ECDC4" in branded_html

    @pytest.mark.asyncio
    async def test_apply_branding_adds_support_info(
        self, email_branding_service, white_label_config
    ):
        """Test that branding adds support information"""
        html = "<p>Lagos, Nigeria</p>"

        branded_html = email_branding_service._apply_branding(
            html, white_label_config, {}
        )

        assert "support@testsalon.com" in branded_html
        assert "+1234567890" in branded_html

    @pytest.mark.asyncio
    async def test_apply_branding_adds_custom_links(
        self, email_branding_service, white_label_config
    ):
        """Test that branding adds custom terms and privacy links"""
        html = "<p>Lagos, Nigeria</p>"

        branded_html = email_branding_service._apply_branding(
            html, white_label_config, {}
        )

        assert "https://testsalon.com/terms" in branded_html
        assert "https://testsalon.com/privacy" in branded_html

    @pytest.mark.asyncio
    async def test_apply_branding_hides_powered_by(
        self, email_branding_service
    ):
        """Test that branding hides powered by text when configured"""
        config = WhiteLabelConfig(
            id="wl_123",
            tenant_id="tenant_123",
            branding=WhiteLabelBranding(company_name="Test Salon"),
            domain=WhiteLabelDomain(),
            features=WhiteLabelFeatures(hide_powered_by=True),
            is_active=True,
            created_at=datetime.utcnow(),
        )

        html = "<p>Powered by Kenikool</p>"

        branded_html = email_branding_service._apply_branding(html, config, {})

        assert "Powered by" not in branded_html


class TestEmailDomainValidation:
    """Test email domain validation functionality"""

    @pytest.mark.asyncio
    async def test_validate_email_domain_with_spf_and_dkim(
        self, email_branding_service
    ):
        """Test email domain validation with both SPF and DKIM records"""
        with patch("app.services.email_branding_service.dns.resolver.resolve") as mock_resolve:
            # Mock SPF record
            spf_record = MagicMock()
            spf_record.__str__ = MagicMock(return_value="v=spf1 include:_spf.google.com ~all")
            
            # Mock DKIM record
            dkim_record = MagicMock()
            dkim_record.__str__ = MagicMock(return_value="v=DKIM1; k=rsa; p=MIGfMA0...")
            
            # Setup mock to return different records based on domain
            def resolve_side_effect(domain, record_type):
                if "v=spf1" in domain or domain == "example.com":
                    return [spf_record]
                elif "_domainkey" in domain:
                    return [dkim_record]
                raise Exception("Not found")
            
            mock_resolve.side_effect = resolve_side_effect

            result = await email_branding_service.validate_email_domain("example.com")

            assert result["domain"] == "example.com"
            assert result["spf_configured"] is True
            assert result["valid"] is True

    @pytest.mark.asyncio
    async def test_validate_email_domain_with_dmarc(
        self, email_branding_service
    ):
        """Test email domain validation with DMARC record"""
        with patch("app.services.email_branding_service.dns.resolver.resolve") as mock_resolve:
            # Mock SPF record
            spf_record = MagicMock()
            spf_record.__str__ = MagicMock(return_value="v=spf1 include:_spf.google.com ~all")
            
            # Mock DMARC record
            dmarc_record = MagicMock()
            dmarc_record.__str__ = MagicMock(return_value="v=DMARC1; p=quarantine; rua=mailto:admin@example.com")
            
            def resolve_side_effect(domain, record_type):
                if domain == "example.com":
                    return [spf_record]
                elif "_dmarc.example.com" in domain:
                    return [dmarc_record]
                raise Exception("Not found")
            
            mock_resolve.side_effect = resolve_side_effect

            result = await email_branding_service.validate_email_domain("example.com")

            assert result["domain"] == "example.com"
            assert result["spf_configured"] is True
            assert result["dmarc_configured"] is True
            assert result["valid"] is True

    @pytest.mark.asyncio
    async def test_validate_email_domain_missing_spf(
        self, email_branding_service
    ):
        """Test email domain validation when SPF is missing"""
        with patch("app.services.email_branding_service.dns.resolver.resolve") as mock_resolve:
            # Mock no SPF record
            mock_resolve.side_effect = Exception("No SPF record found")

            result = await email_branding_service.validate_email_domain("example.com")

            assert result["domain"] == "example.com"
            assert result["spf_configured"] is False
            assert result["valid"] is False
            assert len(result["issues"]) > 0
            assert any("SPF" in issue for issue in result["issues"])

    @pytest.mark.asyncio
    async def test_validate_email_domain_invalid_format(
        self, email_branding_service
    ):
        """Test email domain validation with invalid format"""
        result = await email_branding_service.validate_email_domain("invalid domain")

        assert result["valid"] is False
        assert len(result["issues"]) > 0
        assert any("Invalid domain format" in issue for issue in result["issues"])

    @pytest.mark.asyncio
    async def test_validate_email_domain_empty_domain(
        self, email_branding_service
    ):
        """Test email domain validation with empty domain"""
        result = await email_branding_service.validate_email_domain("")

        assert result["valid"] is False
        assert len(result["issues"]) > 0

    @pytest.mark.asyncio
    async def test_validate_email_domain_with_subdomain(
        self, email_branding_service
    ):
        """Test email domain validation with subdomain"""
        with patch("app.services.email_branding_service.dns.resolver.resolve") as mock_resolve:
            spf_record = MagicMock()
            spf_record.__str__ = MagicMock(return_value="v=spf1 include:_spf.google.com ~all")
            mock_resolve.return_value = [spf_record]

            result = await email_branding_service.validate_email_domain("mail.example.com")

            assert result["domain"] == "mail.example.com"
            assert result["spf_configured"] is True

    @pytest.mark.asyncio
    async def test_validate_email_domain_recommendations(
        self, email_branding_service
    ):
        """Test that recommendations are provided"""
        with patch("app.services.email_branding_service.dns.resolver.resolve") as mock_resolve:
            spf_record = MagicMock()
            spf_record.__str__ = MagicMock(return_value="v=spf1 include:_spf.google.com ~all")
            mock_resolve.return_value = [spf_record]

            result = await email_branding_service.validate_email_domain("example.com")

            assert len(result["recommendations"]) > 0
            assert any("SPF" in rec or "DKIM" in rec or "DMARC" in rec for rec in result["recommendations"])

    @pytest.mark.asyncio
    async def test_validate_email_domain_multiple_selectors(
        self, email_branding_service
    ):
        """Test DKIM validation with multiple selectors"""
        with patch("app.services.email_branding_service.dns.resolver.resolve") as mock_resolve:
            spf_record = MagicMock()
            spf_record.__str__ = MagicMock(return_value="v=spf1 include:_spf.google.com ~all")
            
            dkim_record = MagicMock()
            dkim_record.__str__ = MagicMock(return_value="v=DKIM1; k=rsa; p=MIGfMA0...")
            
            def resolve_side_effect(domain, record_type):
                if domain == "example.com":
                    return [spf_record]
                elif "selector1._domainkey.example.com" in domain:
                    return [dkim_record]
                raise Exception("Not found")
            
            mock_resolve.side_effect = resolve_side_effect

            result = await email_branding_service.validate_email_domain("example.com")

            assert result["dkim_configured"] is True
            assert "selector1._domainkey.example.com" in result["dkim_record"]


class TestEmailDomainValidationAPI:
    """Test email domain validation API endpoint"""

    @pytest.mark.asyncio
    async def test_validate_email_domain_endpoint(self):
        """Test the validate-email-domain API endpoint"""
        from app.api.white_label import validate_email_domain
        from unittest.mock import AsyncMock
        
        # Create mock request and user
        request = MagicMock()
        request.domain = "example.com"
        
        current_user = {"tenant_id": "tenant_123"}
        
        # Mock the email branding service
        with patch("app.api.white_label.email_branding_service.validate_email_domain") as mock_validate:
            mock_validate.return_value = {
                "domain": "example.com",
                "valid": True,
                "spf_configured": True,
                "dkim_configured": True,
                "dmarc_configured": False,
                "issues": [],
                "warnings": [],
                "recommendations": ["Your email domain is properly configured"],
            }
            
            response = await validate_email_domain(request, current_user)
            
            assert response.status_code == 200
            content = response.body.decode()
            assert "example.com" in content
            assert "valid" in content

    @pytest.mark.asyncio
    async def test_validate_email_domain_endpoint_invalid_format(self):
        """Test the validate-email-domain API endpoint with invalid format"""
        from app.api.white_label import validate_email_domain
        
        request = MagicMock()
        request.domain = "invalid domain"
        
        current_user = {"tenant_id": "tenant_123"}
        
        with pytest.raises(HTTPException) as exc_info:
            await validate_email_domain(request, current_user)
        
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_validate_email_domain_endpoint_no_tenant(self):
        """Test the validate-email-domain API endpoint without tenant"""
        from app.api.white_label import validate_email_domain
        
        request = MagicMock()
        request.domain = "example.com"
        
        current_user = {}
        
        with pytest.raises(HTTPException) as exc_info:
            await validate_email_domain(request, current_user)
        
        assert exc_info.value.status_code == 401
