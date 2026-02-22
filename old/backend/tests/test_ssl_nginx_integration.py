"""
Tests for SSL Manager Service with Nginx configuration integration.

This test suite verifies that:
1. SSL certificates are provisioned correctly
2. Nginx configurations are generated from templates
3. Nginx configurations are validated before deployment
4. Nginx is reloaded gracefully after configuration changes
5. Certificates are renewed and Nginx is reloaded
6. Certificates are revoked and Nginx configuration is removed
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
from datetime import datetime, timedelta
from pathlib import Path

from app.services.ssl_manager_service import SSLManagerService, SSLCertificate
from app.services.nginx_config_service import NginxConfigService


class TestSSLManagerNginxIntegration:
    """Test SSL Manager with Nginx configuration"""

    @pytest.fixture
    def ssl_manager(self, mock_db):
        """Create SSL manager instance"""
        manager = SSLManagerService()
        manager.db = mock_db
        return manager

    @pytest.fixture
    def mock_ssl_service(self):
        """Mock SSL service"""
        mock = AsyncMock()
        mock.provision_certificate = AsyncMock(return_value=(True, None))
        mock.renew_certificate = AsyncMock(return_value=(True, None))
        mock.revoke_certificate = AsyncMock(return_value=(True, None))
        mock.get_certificate_expiry = AsyncMock(
            return_value=datetime.utcnow() + timedelta(days=90)
        )
        return mock

    @pytest.fixture
    def mock_db(self):
        """Mock database"""
        mock = MagicMock()
        mock.ssl_certificates = MagicMock()
        mock.ssl_certificates.find_one = MagicMock(return_value=None)
        mock.ssl_certificates.update_one = MagicMock()
        return mock

    @pytest.mark.asyncio
    async def test_provision_certificate_with_nginx_config(self, ssl_manager, mock_ssl_service, mock_db):
        """Test that provisioning certificate also configures Nginx"""
        ssl_manager.ssl_service = mock_ssl_service
        ssl_manager.db = mock_db

        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data="cert data")):
                with patch("app.services.ssl_manager_service.NginxConfigService.generate_config", new_callable=AsyncMock) as mock_generate:
                    with patch("app.services.ssl_manager_service.NginxConfigService.validate_config", new_callable=AsyncMock) as mock_validate:
                        with patch("app.services.ssl_manager_service.NginxConfigService.write_config", new_callable=AsyncMock) as mock_write:
                            with patch("app.services.ssl_manager_service.NginxConfigService.enable_config", new_callable=AsyncMock) as mock_enable:
                                with patch("app.services.ssl_manager_service.NginxConfigService.reload_nginx", new_callable=AsyncMock) as mock_reload:
                                    mock_generate.return_value = "server { ... }"
                                    mock_validate.return_value = True
                                    mock_write.return_value = True
                                    mock_enable.return_value = True
                                    mock_reload.return_value = True

                                    success, error, cert = await ssl_manager.provision_certificate(
                                        tenant_id="test-tenant",
                                        domain="example.com",
                                        email="admin@example.com"
                                    )

                                    assert success is True
                                    assert error is None
                                    assert cert is not None
                                    assert cert.domain == "example.com"

                                    # Verify Nginx configuration was called
                                    mock_generate.assert_called_once_with("example.com")
                                    mock_validate.assert_called_once()
                                    mock_write.assert_called_once()
                                    mock_enable.assert_called_once_with("example.com")
                                    mock_reload.assert_called_once()

    @pytest.mark.asyncio
    async def test_provision_certificate_nginx_config_failure_non_blocking(
        self, ssl_manager, mock_ssl_service, mock_db
    ):
        """Test that Nginx config failure doesn't block certificate provisioning"""
        ssl_manager.ssl_service = mock_ssl_service
        ssl_manager.db = mock_db

        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data="cert data")):
                with patch("app.services.ssl_manager_service.NginxConfigService.generate_config", new_callable=AsyncMock) as mock_generate:
                    mock_generate.return_value = None  # Nginx config generation fails

                    success, error, cert = await ssl_manager.provision_certificate(
                        tenant_id="test-tenant",
                        domain="example.com",
                        email="admin@example.com"
                    )

                    # Certificate should still be provisioned
                    assert success is True
                    assert cert is not None

    @pytest.mark.asyncio
    async def test_renew_certificate_reloads_nginx(self, ssl_manager, mock_ssl_service, mock_db):
        """Test that renewing certificate reloads Nginx"""
        ssl_manager.ssl_service = mock_ssl_service
        ssl_manager.db = mock_db

        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data="cert data")):
                with patch("app.services.ssl_manager_service.NginxConfigService.reload_nginx", new_callable=AsyncMock) as mock_reload:
                    mock_reload.return_value = True

                    success, error = await ssl_manager.renew_certificate(
                        tenant_id="test-tenant",
                        domain="example.com"
                    )

                    assert success is True
                    assert error is None

                    # Verify Nginx was reloaded
                    mock_reload.assert_called_once()

    @pytest.mark.asyncio
    async def test_revoke_certificate_removes_nginx_config(
        self, ssl_manager, mock_ssl_service, mock_db
    ):
        """Test that revoking certificate removes Nginx configuration"""
        ssl_manager.ssl_service = mock_ssl_service
        ssl_manager.db = mock_db

        with patch("app.services.ssl_manager_service.NginxConfigService.remove_config", new_callable=AsyncMock) as mock_remove:
            mock_remove.return_value = True

            success, error = await ssl_manager.revoke_certificate(
                tenant_id="test-tenant",
                domain="example.com"
            )

            assert success is True
            assert error is None

            # Verify Nginx config was removed
            mock_remove.assert_called_once_with("example.com")

            # Verify certificate status was updated
            mock_db.ssl_certificates.update_one.assert_called_once()


class TestNginxConfigService:
    """Test Nginx configuration service"""

    @pytest.mark.asyncio
    async def test_generate_config_from_template(self):
        """Test generating Nginx config from template"""
        template_content = """
server {{
    server_name {domain};
    ssl_certificate /etc/letsencrypt/live/{domain}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{domain}/privkey.pem;
    proxy_pass http://{backend_host}:{backend_port};
}}
"""
        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=template_content)):
                config = await NginxConfigService.generate_config("example.com")

                assert config is not None
                assert "example.com" in config
                assert "fullchain.pem" in config
                assert "privkey.pem" in config

    @pytest.mark.asyncio
    async def test_validate_config_syntax(self):
        """Test validating Nginx configuration syntax"""
        config = "server { server_name example.com; }"

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")

            result = await NginxConfigService.validate_config(config)

            assert result is True
            mock_run.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_config_syntax_error(self):
        """Test validation fails for invalid config"""
        config = "server { invalid syntax"

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1,
                stderr="nginx: [emerg] unexpected end of file"
            )

            result = await NginxConfigService.validate_config(config)

            assert result is False

    @pytest.mark.asyncio
    async def test_write_config_to_file(self):
        """Test writing Nginx config to file"""
        config = "server { server_name example.com; }"

        with patch("pathlib.Path.mkdir"):
            with patch("builtins.open", mock_open()) as mock_file:
                with patch("os.chmod"):
                    result = await NginxConfigService.write_config("example.com", config)

                    assert result is True
                    mock_file.assert_called_once()

    @pytest.mark.asyncio
    async def test_enable_config_creates_symlink(self):
        """Test enabling config creates symlink"""
        with patch("pathlib.Path.exists", return_value=False):
            with patch("pathlib.Path.symlink_to") as mock_symlink:
                result = await NginxConfigService.enable_config("example.com")

                assert result is True
                mock_symlink.assert_called_once()

    @pytest.mark.asyncio
    async def test_reload_nginx_gracefully(self):
        """Test reloading Nginx gracefully"""
        with patch("subprocess.run") as mock_run:
            # First call for test, second for reload
            mock_run.side_effect = [
                MagicMock(returncode=0, stderr=""),
                MagicMock(returncode=0, stderr="")
            ]

            result = await NginxConfigService.reload_nginx()

            assert result is True
            assert mock_run.call_count == 2

    @pytest.mark.asyncio
    async def test_reload_nginx_fails_on_invalid_config(self):
        """Test reload fails if config is invalid"""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1,
                stderr="nginx: [emerg] invalid config"
            )

            result = await NginxConfigService.reload_nginx()

            assert result is False

    @pytest.mark.asyncio
    async def test_remove_config_deletes_files(self):
        """Test removing config deletes files and reloads Nginx"""
        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.unlink") as mock_unlink:
                with patch("app.services.nginx_config_service.NginxConfigService.reload_nginx", new_callable=AsyncMock) as mock_reload:
                    mock_reload.return_value = True

                    result = await NginxConfigService.remove_config("example.com")

                    assert result is True
                    assert mock_unlink.call_count == 2  # symlink and config file
                    mock_reload.assert_called_once()


class TestSSLCertificateDataModel:
    """Test SSL certificate data model"""

    def test_ssl_certificate_creation(self):
        """Test creating SSL certificate object"""
        cert = SSLCertificate(
            domain="example.com",
            certificate_path="/etc/letsencrypt/live/example.com/fullchain.pem",
            private_key_path="/etc/letsencrypt/live/example.com/privkey.pem",
            issued_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=90),
            issuer="Let's Encrypt",
            status="active",
            tenant_id="test-tenant"
        )

        assert cert.domain == "example.com"
        assert cert.status == "active"
        assert cert.issuer == "Let's Encrypt"

    def test_ssl_certificate_expiry_calculation(self):
        """Test certificate expiry calculation"""
        now = datetime.utcnow()
        expires_at = now + timedelta(days=30)

        cert = SSLCertificate(
            domain="example.com",
            certificate_path="/etc/letsencrypt/live/example.com/fullchain.pem",
            private_key_path="/etc/letsencrypt/live/example.com/privkey.pem",
            issued_at=now,
            expires_at=expires_at,
            issuer="Let's Encrypt",
            status="active",
            tenant_id="test-tenant"
        )

        days_remaining = (cert.expires_at - datetime.utcnow()).days
        assert days_remaining >= 29  # Allow for test execution time


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
