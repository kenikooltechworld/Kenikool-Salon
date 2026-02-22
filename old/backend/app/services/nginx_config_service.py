"""
Nginx configuration service - Manages Nginx configuration for custom domains.

This service handles generation, validation, and reloading of Nginx
configurations for custom domains with SSL certificates.
"""
import logging
import os
import subprocess
import tempfile
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class NginxConfigService:
    """Service for managing Nginx configurations"""

    # Nginx configuration paths
    NGINX_SITES_AVAILABLE = "/etc/nginx/sites-available"
    NGINX_SITES_ENABLED = "/etc/nginx/sites-enabled"
    NGINX_CONFIG_TEMPLATE = "backend/infrastructure/nginx-domain.conf.template"

    # Backend configuration
    BACKEND_HOST = os.getenv("BACKEND_HOST", "localhost")
    BACKEND_PORT = os.getenv("BACKEND_PORT", "8000")

    @staticmethod
    async def generate_config(domain: str) -> str:
        """
        Generate Nginx configuration from template.

        Args:
            domain: Domain name

        Returns:
            str: Generated Nginx configuration
        """
        try:
            # Read template
            template_path = Path(NginxConfigService.NGINX_CONFIG_TEMPLATE)

            if not template_path.exists():
                logger.error(f"Nginx template not found: {template_path}")
                return None

            with open(template_path, "r") as f:
                template = f.read()

            # Replace variables
            config = template.replace("{domain}", domain)
            config = config.replace("{backend_host}", NginxConfigService.BACKEND_HOST)
            config = config.replace("{backend_port}", NginxConfigService.BACKEND_PORT)

            logger.info(f"Nginx config generated for {domain}")
            return config

        except Exception as e:
            logger.error(f"Failed to generate Nginx config: {e}")
            return None

    @staticmethod
    async def validate_config(config: str) -> bool:
        """
        Validate Nginx configuration syntax.

        Args:
            config: Nginx configuration content

        Returns:
            bool: True if valid, False otherwise
        """
        try:
            # Write config to temporary file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".conf", delete=False) as f:
                f.write(config)
                temp_path = f.name

            try:
                # Test Nginx configuration
                result = subprocess.run(
                    ["nginx", "-t", "-c", temp_path],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0:
                    logger.info("Nginx configuration is valid")
                    return True
                else:
                    logger.error(f"Nginx configuration validation failed: {result.stderr}")
                    return False

            finally:
                # Clean up temporary file
                os.unlink(temp_path)

        except subprocess.TimeoutExpired:
            logger.error("Nginx validation timed out")
            return False
        except Exception as e:
            logger.error(f"Failed to validate Nginx config: {e}")
            return False

    @staticmethod
    async def write_config(domain: str, config: str) -> bool:
        """
        Write Nginx configuration to file.

        Args:
            domain: Domain name
            config: Nginx configuration content

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            config_path = Path(NginxConfigService.NGINX_SITES_AVAILABLE) / f"{domain}.conf"

            # Create directory if it doesn't exist
            config_path.parent.mkdir(parents=True, exist_ok=True)

            # Write configuration
            with open(config_path, "w") as f:
                f.write(config)

            # Set permissions
            os.chmod(config_path, 0o644)

            logger.info(f"Nginx config written to {config_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to write Nginx config: {e}")
            return False

    @staticmethod
    async def enable_config(domain: str) -> bool:
        """
        Enable Nginx configuration by creating symlink.

        Args:
            domain: Domain name

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            available_path = Path(NginxConfigService.NGINX_SITES_AVAILABLE) / f"{domain}.conf"
            enabled_path = Path(NginxConfigService.NGINX_SITES_ENABLED) / f"{domain}.conf"

            # Create symlink if it doesn't exist
            if not enabled_path.exists():
                enabled_path.symlink_to(available_path)
                logger.info(f"Nginx config enabled for {domain}")

            return True

        except Exception as e:
            logger.error(f"Failed to enable Nginx config: {e}")
            return False

    @staticmethod
    async def reload_nginx() -> bool:
        """
        Reload Nginx with new configuration.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Test configuration first
            result = subprocess.run(
                ["nginx", "-t"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                logger.error(f"Nginx configuration test failed: {result.stderr}")
                return False

            # Reload Nginx
            result = subprocess.run(
                ["nginx", "-s", "reload"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                logger.info("Nginx reloaded successfully")
                return True
            else:
                logger.error(f"Nginx reload failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("Nginx reload timed out")
            return False
        except Exception as e:
            logger.error(f"Failed to reload Nginx: {e}")
            return False

    @staticmethod
    async def remove_config(domain: str) -> bool:
        """
        Remove Nginx configuration for domain.

        Args:
            domain: Domain name

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            available_path = Path(NginxConfigService.NGINX_SITES_AVAILABLE) / f"{domain}.conf"
            enabled_path = Path(NginxConfigService.NGINX_SITES_ENABLED) / f"{domain}.conf"

            # Remove symlink
            if enabled_path.exists():
                enabled_path.unlink()
                logger.info(f"Nginx config disabled for {domain}")

            # Remove configuration file
            if available_path.exists():
                available_path.unlink()
                logger.info(f"Nginx config removed for {domain}")

            # Reload Nginx
            await NginxConfigService.reload_nginx()

            return True

        except Exception as e:
            logger.error(f"Failed to remove Nginx config: {e}")
            return False

    @staticmethod
    async def setup_domain_config(domain: str) -> bool:
        """
        Complete setup of Nginx configuration for a domain.

        Args:
            domain: Domain name

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Generate configuration
            config = await NginxConfigService.generate_config(domain)
            if not config:
                return False

            # Validate configuration
            if not await NginxConfigService.validate_config(config):
                return False

            # Write configuration
            if not await NginxConfigService.write_config(domain, config):
                return False

            # Enable configuration
            if not await NginxConfigService.enable_config(domain):
                return False

            # Reload Nginx
            if not await NginxConfigService.reload_nginx():
                return False

            logger.info(f"Nginx configuration setup completed for {domain}")
            return True

        except Exception as e:
            logger.error(f"Failed to setup Nginx configuration: {e}")
            return False
