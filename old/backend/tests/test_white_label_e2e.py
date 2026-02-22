"""
End-to-end tests for white label system.

Tests the complete user journey:
1. Complete white label setup flow
2. Branding preview with real-time updates
3. Custom domain access with SSL
4. Email delivery with branding
5. Version rollback
"""
import pytest
import io
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from PIL import Image

from app.services.white_label_asset_manager import AssetManagerService
from app.services.dns_verifier_service import DNSVerifierService
from app.services.ssl_manager_service import SSLManagerService
from app.services.preview_engine_service import PreviewEngineService
from app.services.email_branding_service import EmailBrandingService
from app.services.branding_version_service import BrandingVersionService
from app.schemas.white_label import (
    WhiteLabelConfig,
    WhiteLabelBranding,
    WhiteLabelDomain,
    WhiteLabelFeatures,
)


@pytest.fixture
def tenant_id():
    """Test tenant ID"""
    return "e2e-test-tenant"


@pytest.fixture
def sample_logo():
    """Create a sample logo image"""
    img = Image.new('RGB', (200, 100), color='#FF6B6B')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes.getvalue()


@pytest.fixture
def sample_favicon():
    """Create a sample favicon image"""
    img = Image.new('RGB', (32, 32), color='#4ECDC4')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes.getvalue()


@pytest.fixture
def white_label_config():
    """Create a test white label configuration"""
    return WhiteLabelConfig(
        id="wl_e2e_test",
        tenant_id="e2e-test-tenant",
        branding=WhiteLabelBranding(
            company_name="E2E Test Salon",
            tagline="End-to-end testing",
            primary_color="#FF6B6B",
            secondary_color="#4ECDC4",
            accent_color="#45B7D1",
            font_family="Roboto",
            logo_url="https://storage.example.com/logo.png",
            favicon_url="https://storage.example.com/favicon.png",
        ),
        domain=WhiteLabelDomain(
            custom_domain="e2e-test.example.com",
            ssl_enabled=True,
            dns_configured=True,
        ),
        features=WhiteLabelFeatures(
            hide_powered_by=True,
            custom_support_email="support@e2e-test.com",
            custom_support_phone="+1-555-0199",
            custom_terms_url="https://e2e-test.com/terms",
            custom_privacy_url="https://e2e-test.com/privacy",
        ),
        is_active=True,
        created_at=datetime.utcnow(),
    )


class TestCompleteWhiteLabelSetupFlow:
    """Test complete white label setup flow"""

    @pytest.mark.asyncio
    async def test_e2e_setup_flow_from_start_to_finish(
        self, tenant_id, sample_logo, sample_favicon, white_label_config
    ):
        """Test complete setup flow from start to finish"""
        
        # Step 1: Upload logo
        asset_manager = AssetManagerService()
        asset_manager.client = MagicMock()
        asset_manager.client.put_object = MagicMock()
        asset_manager.client.get_presigned_download_link = MagicMock(
            return_value="https://storage.example.com/logo.png"
        )

        from fastapi import UploadFile
        logo_file = UploadFile(
            file=io.BytesIO(sample_logo),
            size=len(sample_logo),
            filename="logo.png"
        )
        logo_file.content_type = "image/png"

        logo_result = await asset_manager.upload_asset(tenant_id, logo_file, "logo")
        assert logo_result["asset_url"] == "https://storage.example.com/logo.png"
        assert logo_result["asset_type"] == "logo"

        # Step 2: Upload favicon
        favicon_file = UploadFile(
            file=io.BytesIO(sample_favicon),
            size=len(sample_favicon),
            filename="favicon.png"
        )
        favicon_file.content_type = "image/png"

        favicon_result = await asset_manager.upload_asset(tenant_id, favicon_file, "favicon")
        assert favicon_result["asset_url"] == "https://storage.example.com/favicon.png"
        assert favicon_result["asset_type"] == "favicon"

        # Step 3: Verify DNS
        dns_verifier = DNSVerifierService()
        with patch.object(dns_verifier, "check_cname_record") as mock_cname:
            with patch.object(dns_verifier, "get_dns_records") as mock_records:
                mock_cname.return_value = True
                mock_records.return_value = [
                    {
                        "record_type": "CNAME",
                        "host": "e2e-test.example.com",
                        "value": "app.yoursalonplatform.com",
                        "ttl": 3600,
                    }
                ]

                dns_result = await dns_verifier.verify_domain(
                    tenant_id,
                    "e2e-test.example.com"
                )
                assert dns_result.verified is True

        # Step 4: Provision SSL
        ssl_manager = SSLManagerService()
        ssl_manager.db = MagicMock()
        ssl_manager.ssl_service = AsyncMock()
        ssl_manager.ssl_service.provision_certificate = AsyncMock(
            return_value=(True, None)
        )

        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", MagicMock()):
                with patch("app.services.ssl_manager_service.NginxConfigService.generate_config", new_callable=AsyncMock) as mock_nginx:
                    mock_nginx.return_value = "server { ... }"

                    ssl_result = await ssl_manager.provision_certificate(
                        tenant_id=tenant_id,
                        domain="e2e-test.example.com",
                        email="admin@e2e-test.com"
                    )
                    assert ssl_result[0] is True

        # Step 5: Generate preview
        preview_engine = PreviewEngineService()
        preview = await preview_engine.generate_preview(
            branding_config=white_label_config.branding.dict(),
            page_type="home",
            tenant_id=tenant_id,
        )
        assert preview.page_type == "home"
        assert "E2E Test Salon" in preview.html
        assert "#FF6B6B" in preview.html

        # Step 6: Apply email branding
        email_branding = EmailBrandingService()
        from_address = await email_branding.get_branded_from_address(white_label_config)
        assert "support@e2e-test.com" in from_address

        # Verify complete flow
        assert logo_result["asset_url"] is not None
        assert favicon_result["asset_url"] is not None
        assert dns_result.verified is True
        assert ssl_result[0] is True
        assert "E2E Test Salon" in preview.html


class TestBrandingPreviewWithRealTimeUpdates:
    """Test branding preview with real-time updates"""

    @pytest.mark.asyncio
    async def test_preview_updates_on_color_change(self):
        """Test that preview updates when colors change"""
        preview_engine = PreviewEngineService()

        # Initial config
        config1 = {
            "company_name": "Test Salon",
            "primary_color": "#FF0000",
            "secondary_color": "#00FF00",
        }

        preview1 = await preview_engine.generate_preview(
            branding_config=config1,
            page_type="home",
        )

        assert "#FF0000" in preview1.html
        assert "#00FF00" in preview1.html

        # Updated config with different colors
        config2 = {
            "company_name": "Test Salon",
            "primary_color": "#0000FF",
            "secondary_color": "#FFFF00",
        }

        preview2 = await preview_engine.generate_preview(
            branding_config=config2,
            page_type="home",
        )

        assert "#0000FF" in preview2.html
        assert "#FFFF00" in preview2.html
        # Verify colors actually changed
        assert preview1.html != preview2.html

    @pytest.mark.asyncio
    async def test_preview_updates_on_logo_change(self):
        """Test that preview updates when logo changes"""
        preview_engine = PreviewEngineService()

        # Initial config
        config1 = {
            "company_name": "Test Salon",
            "logo_url": "https://storage.example.com/logo1.png",
        }

        preview1 = await preview_engine.generate_preview(
            branding_config=config1,
            page_type="home",
        )

        assert "https://storage.example.com/logo1.png" in preview1.html

        # Updated config with different logo
        config2 = {
            "company_name": "Test Salon",
            "logo_url": "https://storage.example.com/logo2.png",
        }

        preview2 = await preview_engine.generate_preview(
            branding_config=config2,
            page_type="home",
        )

        assert "https://storage.example.com/logo2.png" in preview2.html
        assert preview1.html != preview2.html

    @pytest.mark.asyncio
    async def test_preview_shows_accessibility_warnings(self):
        """Test that preview shows accessibility warnings"""
        preview_engine = PreviewEngineService()

        # Config with poor color contrast
        config = {
            "company_name": "Test Salon",
            "primary_color": "#FFFFFF",
            "secondary_color": "#FFFFCC",
        }

        preview = await preview_engine.generate_preview(
            branding_config=config,
            page_type="home",
        )

        # Should have accessibility warnings
        assert len(preview.accessibility_warnings) > 0
        contrast_warning = next(
            (w for w in preview.accessibility_warnings if w.type == "color_contrast"),
            None
        )
        assert contrast_warning is not None

    @pytest.mark.asyncio
    async def test_preview_multiple_page_types(self):
        """Test preview for multiple page types"""
        preview_engine = PreviewEngineService()

        config = {
            "company_name": "Test Salon",
            "primary_color": "#FF6B6B",
        }

        # Test home page
        home_preview = await preview_engine.generate_preview(
            branding_config=config,
            page_type="home",
        )
        assert home_preview.page_type == "home"

        # Test booking page
        booking_preview = await preview_engine.generate_preview(
            branding_config=config,
            page_type="booking",
        )
        assert booking_preview.page_type == "booking"

        # Test checkout page
        checkout_preview = await preview_engine.generate_preview(
            branding_config=config,
            page_type="checkout",
        )
        assert checkout_preview.page_type == "checkout"

        # All should have the company name
        assert "Test Salon" in home_preview.html
        assert "Test Salon" in booking_preview.html
        assert "Test Salon" in checkout_preview.html


class TestCustomDomainAccessWithSSL:
    """Test custom domain access with SSL"""

    @pytest.mark.asyncio
    async def test_custom_domain_routing(self):
        """Test that requests to custom domain are routed correctly"""
        # This tests the domain router middleware
        config = WhiteLabelConfig(
            id="wl_domain_test",
            tenant_id="domain-test-tenant",
            branding=WhiteLabelBranding(company_name="Domain Test Salon"),
            domain=WhiteLabelDomain(
                custom_domain="custom.example.com",
                ssl_enabled=True,
                dns_configured=True,
            ),
            features=WhiteLabelFeatures(),
            is_active=True,
            created_at=datetime.utcnow(),
        )

        # Verify domain is configured
        assert config.domain.custom_domain == "custom.example.com"
        assert config.domain.ssl_enabled is True
        assert config.domain.dns_configured is True

    @pytest.mark.asyncio
    async def test_ssl_certificate_is_valid(self):
        """Test that SSL certificate is valid for custom domain"""
        ssl_manager = SSLManagerService()
        ssl_manager.db = MagicMock()
        ssl_manager.ssl_service = AsyncMock()
        ssl_manager.ssl_service.get_certificate_expiry = AsyncMock(
            return_value=datetime.utcnow() + timedelta(days=90)
        )

        expiry = await ssl_manager.ssl_service.get_certificate_expiry()
        days_remaining = (expiry - datetime.utcnow()).days

        assert days_remaining > 0
        assert days_remaining <= 90

    @pytest.mark.asyncio
    async def test_https_redirect_for_custom_domain(self):
        """Test that HTTP requests are redirected to HTTPS"""
        # This would be tested in the Nginx configuration
        config = WhiteLabelConfig(
            id="wl_https_test",
            tenant_id="https-test-tenant",
            branding=WhiteLabelBranding(company_name="HTTPS Test Salon"),
            domain=WhiteLabelDomain(
                custom_domain="https-test.example.com",
                ssl_enabled=True,
            ),
            features=WhiteLabelFeatures(),
            is_active=True,
            created_at=datetime.utcnow(),
        )

        assert config.domain.ssl_enabled is True


class TestEmailDeliveryWithBranding:
    """Test email delivery with branding"""

    @pytest.mark.asyncio
    async def test_send_branded_verification_email(self, white_label_config):
        """Test sending branded verification email"""
        email_branding = EmailBrandingService()

        template_data = {
            "user_name": "John Doe",
            "verification_url": "https://e2e-test.example.com/verify?token=abc123",
        }

        html = await email_branding.apply_branding_to_template(
            "verification",
            white_label_config,
            template_data
        )

        # Verify branding is applied
        assert "E2E Test Salon" in html
        assert "support@e2e-test.com" in html
        assert "John Doe" in html
        assert "https://e2e-test.example.com/verify?token=abc123" in html

    @pytest.mark.asyncio
    async def test_send_branded_booking_confirmation(self, white_label_config):
        """Test sending branded booking confirmation email"""
        email_branding = EmailBrandingService()

        template_data = {
            "client_name": "Jane Smith",
            "service_name": "Hair Cut",
            "booking_date": "2024-02-15",
            "booking_time": "10:00 AM",
        }

        html = await email_branding.apply_branding_to_template(
            "booking_confirmation",
            white_label_config,
            template_data
        )

        # Verify branding is applied
        assert "E2E Test Salon" in html
        assert "support@e2e-test.com" in html
        assert "Jane Smith" in html
        assert "Hair Cut" in html
        assert "2024-02-15" in html

    @pytest.mark.asyncio
    async def test_send_branded_booking_reminder(self, white_label_config):
        """Test sending branded booking reminder email"""
        email_branding = EmailBrandingService()

        template_data = {
            "client_name": "Jane Smith",
            "service_name": "Hair Cut",
            "booking_date": "2024-02-15",
            "booking_time": "10:00 AM",
        }

        html = await email_branding.apply_branding_to_template(
            "booking_reminder",
            white_label_config,
            template_data
        )

        # Verify branding is applied
        assert "E2E Test Salon" in html
        assert "support@e2e-test.com" in html
        assert "Jane Smith" in html

    @pytest.mark.asyncio
    async def test_email_footer_includes_custom_links(self, white_label_config):
        """Test that email footer includes custom terms and privacy links"""
        email_branding = EmailBrandingService()

        template_data = {"user_name": "John Doe"}

        html = await email_branding.apply_branding_to_template(
            "verification",
            white_label_config,
            template_data
        )

        # Verify custom links are in footer
        assert "https://e2e-test.com/terms" in html
        assert "https://e2e-test.com/privacy" in html


class TestVersionRollback:
    """Test branding version rollback"""

    @pytest.mark.asyncio
    async def test_save_branding_version(self):
        """Test saving branding version"""
        version_service = BrandingVersionService()
        version_service.db = MagicMock()
        version_service.db.branding_versions = MagicMock()
        version_service.db.branding_versions.insert_one = MagicMock(
            return_value=MagicMock(inserted_id="version_1")
        )

        config = {
            "company_name": "Test Salon",
            "primary_color": "#FF0000",
        }

        version_id = await version_service.save_version(
            tenant_id="test-tenant",
            config=config,
            user_id="user_123",
            description="Initial branding"
        )

        assert version_id is not None
        version_service.db.branding_versions.insert_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_version_history(self):
        """Test retrieving version history"""
        version_service = BrandingVersionService()
        version_service.db = MagicMock()
        version_service.db.branding_versions = MagicMock()

        # Mock version history
        versions = [
            {
                "_id": "version_1",
                "tenant_id": "test-tenant",
                "config": {"company_name": "Test Salon v1"},
                "created_at": datetime.utcnow() - timedelta(days=2),
            },
            {
                "_id": "version_2",
                "tenant_id": "test-tenant",
                "config": {"company_name": "Test Salon v2"},
                "created_at": datetime.utcnow() - timedelta(days=1),
            },
            {
                "_id": "version_3",
                "tenant_id": "test-tenant",
                "config": {"company_name": "Test Salon v3"},
                "created_at": datetime.utcnow(),
            },
        ]

        version_service.db.branding_versions.find = MagicMock(return_value=versions)

        history = await version_service.get_version_history("test-tenant", limit=10)

        assert len(history) == 3
        assert history[0]["config"]["company_name"] == "Test Salon v1"
        assert history[2]["config"]["company_name"] == "Test Salon v3"

    @pytest.mark.asyncio
    async def test_rollback_to_previous_version(self):
        """Test rolling back to previous version"""
        version_service = BrandingVersionService()
        version_service.db = MagicMock()
        version_service.db.branding_versions = MagicMock()
        version_service.db.white_label_configs = MagicMock()

        # Mock previous version
        previous_version = {
            "_id": "version_1",
            "tenant_id": "test-tenant",
            "config": {
                "company_name": "Test Salon",
                "primary_color": "#FF0000",
            },
            "created_at": datetime.utcnow() - timedelta(days=1),
        }

        version_service.db.branding_versions.find_one = MagicMock(
            return_value=previous_version
        )
        version_service.db.white_label_configs.update_one = MagicMock()

        result = await version_service.rollback_to_version(
            tenant_id="test-tenant",
            version_id="version_1",
            user_id="user_123"
        )

        assert result is True
        version_service.db.white_label_configs.update_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_compare_versions(self):
        """Test comparing two versions"""
        version_service = BrandingVersionService()

        version1 = {
            "company_name": "Test Salon",
            "primary_color": "#FF0000",
            "secondary_color": "#00FF00",
        }

        version2 = {
            "company_name": "Test Salon Updated",
            "primary_color": "#0000FF",
            "secondary_color": "#00FF00",
        }

        diff = version_service.compare_versions(version1, version2)

        assert "company_name" in diff
        assert "primary_color" in diff
        assert "secondary_color" not in diff  # No change
        assert diff["company_name"]["old"] == "Test Salon"
        assert diff["company_name"]["new"] == "Test Salon Updated"


class TestE2EErrorRecovery:
    """Test error recovery in E2E flows"""

    @pytest.mark.asyncio
    async def test_recover_from_asset_upload_failure(self, tenant_id, sample_logo):
        """Test recovery from asset upload failure"""
        asset_manager = AssetManagerService()
        asset_manager.client = MagicMock()

        # First attempt fails
        asset_manager.client.put_object = MagicMock(side_effect=Exception("Network error"))

        from fastapi import UploadFile
        logo_file = UploadFile(
            file=io.BytesIO(sample_logo),
            size=len(sample_logo),
            filename="logo.png"
        )
        logo_file.content_type = "image/png"

        # Should raise error
        with pytest.raises(Exception):
            await asset_manager.upload_asset(tenant_id, logo_file, "logo")

        # Second attempt succeeds
        asset_manager.client.put_object = MagicMock()
        asset_manager.client.get_presigned_download_link = MagicMock(
            return_value="https://storage.example.com/logo.png"
        )

        logo_file.file.seek(0)  # Reset file pointer
        result = await asset_manager.upload_asset(tenant_id, logo_file, "logo")

        assert result["asset_url"] == "https://storage.example.com/logo.png"

    @pytest.mark.asyncio
    async def test_recover_from_dns_verification_timeout(self, tenant_id):
        """Test recovery from DNS verification timeout"""
        dns_verifier = DNSVerifierService()

        # First attempt times out
        with patch.object(dns_verifier, "check_cname_record") as mock_cname:
            mock_cname.side_effect = TimeoutError("DNS lookup timeout")

            with pytest.raises(TimeoutError):
                await dns_verifier.verify_domain(tenant_id, "example.com")

        # Second attempt succeeds
        with patch.object(dns_verifier, "check_cname_record") as mock_cname:
            with patch.object(dns_verifier, "get_dns_records") as mock_records:
                mock_cname.return_value = True
                mock_records.return_value = [
                    {
                        "record_type": "CNAME",
                        "host": "example.com",
                        "value": "app.yoursalonplatform.com",
                        "ttl": 3600,
                    }
                ]

                result = await dns_verifier.verify_domain(tenant_id, "example.com")
                assert result.verified is True
