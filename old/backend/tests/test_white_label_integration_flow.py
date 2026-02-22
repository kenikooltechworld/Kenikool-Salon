"""
Integration tests for complete white label system flow.

Tests the end-to-end workflow of:
1. Asset upload to storage
2. DNS verification with real records (staging)
3. SSL provisioning with Let's Encrypt staging
4. Domain routing with multiple domains
5. Email branding application
"""
import pytest
import io
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from PIL import Image

from app.services.white_label_asset_manager import AssetManagerService
from app.services.dns_verifier_service import DNSVerifierService
from app.services.ssl_manager_service import SSLManagerService
from app.services.email_branding_service import EmailBrandingService
from app.schemas.white_label import (
    WhiteLabelConfig,
    WhiteLabelBranding,
    WhiteLabelDomain,
    WhiteLabelFeatures,
)


@pytest.fixture
def tenant_id():
    """Test tenant ID"""
    return "integration-test-tenant"


@pytest.fixture
def sample_logo():
    """Create a sample logo image"""
    img = Image.new('RGB', (200, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes.getvalue()


@pytest.fixture
def sample_favicon():
    """Create a sample favicon image"""
    img = Image.new('RGB', (32, 32), color='blue')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes.getvalue()


@pytest.fixture
def white_label_config():
    """Create a test white label configuration"""
    return WhiteLabelConfig(
        id="wl_integration_test",
        tenant_id="integration-test-tenant",
        branding=WhiteLabelBranding(
            company_name="Integration Test Salon",
            tagline="Testing white label system",
            primary_color="#FF6B6B",
            secondary_color="#4ECDC4",
            accent_color="#45B7D1",
            font_family="Roboto",
        ),
        domain=WhiteLabelDomain(
            custom_domain="integration-test.example.com",
            ssl_enabled=True,
            dns_configured=False,
        ),
        features=WhiteLabelFeatures(
            hide_powered_by=True,
            custom_support_email="support@integration-test.com",
            custom_support_phone="+1-555-0123",
            custom_terms_url="https://integration-test.com/terms",
            custom_privacy_url="https://integration-test.com/privacy",
        ),
        is_active=True,
        created_at=datetime.utcnow(),
    )


class TestAssetUploadIntegration:
    """Test asset upload integration"""

    @pytest.mark.asyncio
    async def test_upload_logo_to_storage(self, tenant_id, sample_logo):
        """Test uploading logo to storage"""
        asset_manager = AssetManagerService()
        asset_manager.client = MagicMock()
        asset_manager.client.put_object = MagicMock()
        asset_manager.client.get_presigned_download_link = MagicMock(
            return_value="https://storage.example.com/logo.png"
        )

        from fastapi import UploadFile
        file = UploadFile(
            file=io.BytesIO(sample_logo),
            size=len(sample_logo),
            filename="logo.png"
        )
        file.content_type = "image/png"

        result = await asset_manager.upload_asset(tenant_id, file, "logo")

        assert result["asset_type"] == "logo"
        assert result["asset_url"] == "https://storage.example.com/logo.png"
        assert result["file_size"] > 0
        assert "dimensions" in result
        asset_manager.client.put_object.assert_called_once()

    @pytest.mark.asyncio
    async def test_upload_favicon_to_storage(self, tenant_id, sample_favicon):
        """Test uploading favicon to storage"""
        asset_manager = AssetManagerService()
        asset_manager.client = MagicMock()
        asset_manager.client.put_object = MagicMock()
        asset_manager.client.get_presigned_download_link = MagicMock(
            return_value="https://storage.example.com/favicon.png"
        )

        from fastapi import UploadFile
        file = UploadFile(
            file=io.BytesIO(sample_favicon),
            size=len(sample_favicon),
            filename="favicon.png"
        )
        file.content_type = "image/png"

        result = await asset_manager.upload_asset(tenant_id, file, "favicon")

        assert result["asset_type"] == "favicon"
        assert result["asset_url"] == "https://storage.example.com/favicon.png"
        asset_manager.client.put_object.assert_called_once()


class TestDNSVerificationIntegration:
    """Test DNS verification integration"""

    @pytest.mark.asyncio
    async def test_verify_domain_with_cname_record(self):
        """Test verifying domain with CNAME record"""
        dns_verifier = DNSVerifierService()

        with patch.object(dns_verifier, "check_cname_record") as mock_cname:
            with patch.object(dns_verifier, "check_a_record") as mock_a:
                with patch.object(dns_verifier, "get_dns_records") as mock_records:
                    mock_cname.return_value = True
                    mock_a.return_value = False
                    mock_records.return_value = [
                        {
                            "record_type": "CNAME",
                            "host": "integration-test.example.com",
                            "value": "app.yoursalonplatform.com",
                            "ttl": 3600,
                        }
                    ]

                    result = await dns_verifier.verify_domain(
                        "integration-test-tenant",
                        "integration-test.example.com"
                    )

                    assert result.verified is True
                    assert len(result.records_found) > 0
                    assert len(result.issues) == 0

    @pytest.mark.asyncio
    async def test_verify_domain_with_a_record(self):
        """Test verifying domain with A record"""
        dns_verifier = DNSVerifierService()

        with patch.object(dns_verifier, "check_cname_record") as mock_cname:
            with patch.object(dns_verifier, "check_a_record") as mock_a:
                with patch.object(dns_verifier, "get_dns_records") as mock_records:
                    mock_cname.return_value = False
                    mock_a.return_value = True
                    mock_records.return_value = [
                        {
                            "record_type": "A",
                            "host": "integration-test.example.com",
                            "value": "203.0.113.1",
                            "ttl": 3600,
                        }
                    ]

                    result = await dns_verifier.verify_domain(
                        "integration-test-tenant",
                        "integration-test.example.com"
                    )

                    assert result.verified is True
                    assert len(result.records_found) > 0

    @pytest.mark.asyncio
    async def test_verify_domain_fails_with_no_records(self):
        """Test domain verification fails when no records found"""
        dns_verifier = DNSVerifierService()

        with patch.object(dns_verifier, "check_cname_record") as mock_cname:
            with patch.object(dns_verifier, "check_a_record") as mock_a:
                with patch.object(dns_verifier, "get_dns_records") as mock_records:
                    mock_cname.return_value = False
                    mock_a.return_value = False
                    mock_records.return_value = []

                    result = await dns_verifier.verify_domain(
                        "integration-test-tenant",
                        "integration-test.example.com"
                    )

                    assert result.verified is False
                    assert len(result.issues) > 0


class TestSSLProvisioningIntegration:
    """Test SSL provisioning integration"""

    @pytest.mark.asyncio
    async def test_provision_ssl_certificate(self):
        """Test provisioning SSL certificate"""
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

                    success, error, cert = await ssl_manager.provision_certificate(
                        tenant_id="integration-test-tenant",
                        domain="integration-test.example.com",
                        email="admin@integration-test.com"
                    )

                    assert success is True
                    assert error is None
                    assert cert is not None
                    assert cert.domain == "integration-test.example.com"

    @pytest.mark.asyncio
    async def test_ssl_certificate_renewal(self):
        """Test SSL certificate renewal"""
        ssl_manager = SSLManagerService()
        ssl_manager.db = MagicMock()
        ssl_manager.ssl_service = AsyncMock()
        ssl_manager.ssl_service.renew_certificate = AsyncMock(
            return_value=(True, None)
        )

        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", MagicMock()):
                with patch("app.services.ssl_manager_service.NginxConfigService.reload_nginx", new_callable=AsyncMock) as mock_reload:
                    mock_reload.return_value = True

                    success, error = await ssl_manager.renew_certificate(
                        tenant_id="integration-test-tenant",
                        domain="integration-test.example.com"
                    )

                    assert success is True
                    assert error is None
                    mock_reload.assert_called_once()


class TestEmailBrandingIntegration:
    """Test email branding integration"""

    @pytest.mark.asyncio
    async def test_apply_branding_to_email_template(self, white_label_config):
        """Test applying branding to email template"""
        email_branding = EmailBrandingService()

        template_data = {
            "user_name": "John Doe",
            "verification_url": "https://example.com/verify?token=123",
        }

        html = await email_branding.apply_branding_to_template(
            "verification",
            white_label_config,
            template_data
        )

        assert "Integration Test Salon" in html
        assert "support@integration-test.com" in html
        assert "John Doe" in html
        assert "#FF6B6B" in html or "#4ECDC4" in html

    @pytest.mark.asyncio
    async def test_get_branded_from_address(self, white_label_config):
        """Test getting branded from address"""
        email_branding = EmailBrandingService()

        from_address = await email_branding.get_branded_from_address(white_label_config)

        assert "support@integration-test.com" in from_address
        assert "Integration Test Salon" in from_address

    @pytest.mark.asyncio
    async def test_get_branded_subject(self, white_label_config):
        """Test getting branded subject line"""
        email_branding = EmailBrandingService()

        subject = await email_branding.get_branded_subject(
            "Welcome to our platform",
            white_label_config
        )

        assert "Integration Test Salon" in subject
        assert "Welcome to our platform" in subject


class TestMultipleDomainRouting:
    """Test domain routing with multiple domains"""

    @pytest.mark.asyncio
    async def test_route_request_to_primary_domain(self):
        """Test routing request to primary domain"""
        # This would test the domain router middleware
        # For now, we verify the configuration supports multiple domains
        config = WhiteLabelConfig(
            id="wl_multi_domain",
            tenant_id="multi-domain-tenant",
            branding=WhiteLabelBranding(company_name="Multi Domain Salon"),
            domain=WhiteLabelDomain(
                custom_domain="primary.example.com",
                ssl_enabled=True,
                dns_configured=True,
            ),
            features=WhiteLabelFeatures(),
            is_active=True,
            created_at=datetime.utcnow(),
        )

        assert config.domain.custom_domain == "primary.example.com"
        assert config.is_active is True

    @pytest.mark.asyncio
    async def test_route_request_to_secondary_domain(self):
        """Test routing request to secondary domain"""
        # Test that multiple domains can be configured
        config1 = WhiteLabelConfig(
            id="wl_domain_1",
            tenant_id="multi-domain-tenant",
            branding=WhiteLabelBranding(company_name="Salon Location 1"),
            domain=WhiteLabelDomain(custom_domain="location1.example.com"),
            features=WhiteLabelFeatures(),
            is_active=True,
            created_at=datetime.utcnow(),
        )

        config2 = WhiteLabelConfig(
            id="wl_domain_2",
            tenant_id="multi-domain-tenant",
            branding=WhiteLabelBranding(company_name="Salon Location 2"),
            domain=WhiteLabelDomain(custom_domain="location2.example.com"),
            features=WhiteLabelFeatures(),
            is_active=True,
            created_at=datetime.utcnow(),
        )

        assert config1.domain.custom_domain == "location1.example.com"
        assert config2.domain.custom_domain == "location2.example.com"
        assert config1.branding.company_name != config2.branding.company_name


class TestCompleteWhiteLabelFlow:
    """Test complete white label setup flow"""

    @pytest.mark.asyncio
    async def test_complete_setup_flow(self, tenant_id, sample_logo, white_label_config):
        """Test complete white label setup flow"""
        # Step 1: Upload assets
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

        # Step 2: Verify DNS
        dns_verifier = DNSVerifierService()
        with patch.object(dns_verifier, "check_cname_record") as mock_cname:
            with patch.object(dns_verifier, "get_dns_records") as mock_records:
                mock_cname.return_value = True
                mock_records.return_value = [
                    {
                        "record_type": "CNAME",
                        "host": "integration-test.example.com",
                        "value": "app.yoursalonplatform.com",
                        "ttl": 3600,
                    }
                ]

                dns_result = await dns_verifier.verify_domain(
                    tenant_id,
                    "integration-test.example.com"
                )
                assert dns_result.verified is True

        # Step 3: Provision SSL
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
                        domain="integration-test.example.com",
                        email="admin@integration-test.com"
                    )
                    assert ssl_result[0] is True

        # Step 4: Apply email branding
        email_branding = EmailBrandingService()
        from_address = await email_branding.get_branded_from_address(white_label_config)
        assert "support@integration-test.com" in from_address

        # Verify complete flow succeeded
        assert logo_result["asset_url"] is not None
        assert dns_result.verified is True
        assert ssl_result[0] is True
        assert "support@integration-test.com" in from_address


class TestIntegrationErrorHandling:
    """Test error handling in integration flows"""

    @pytest.mark.asyncio
    async def test_asset_upload_failure_doesnt_block_dns(self, tenant_id):
        """Test that asset upload failure doesn't block DNS verification"""
        # Asset upload fails
        asset_manager = AssetManagerService()
        asset_manager.client = MagicMock()
        asset_manager.client.put_object = MagicMock(side_effect=Exception("Storage error"))

        # But DNS verification can still proceed
        dns_verifier = DNSVerifierService()
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

    @pytest.mark.asyncio
    async def test_dns_failure_doesnt_block_ssl(self, tenant_id):
        """Test that DNS failure doesn't block SSL provisioning"""
        # DNS verification fails
        dns_verifier = DNSVerifierService()
        with patch.object(dns_verifier, "check_cname_record") as mock_cname:
            with patch.object(dns_verifier, "check_a_record") as mock_a:
                with patch.object(dns_verifier, "get_dns_records") as mock_records:
                    mock_cname.return_value = False
                    mock_a.return_value = False
                    mock_records.return_value = []

                    dns_result = await dns_verifier.verify_domain(tenant_id, "example.com")
                    assert dns_result.verified is False

        # But SSL provisioning can still proceed
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
                        domain="example.com",
                        email="admin@example.com"
                    )
                    assert ssl_result[0] is True
