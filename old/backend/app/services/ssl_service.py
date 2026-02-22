import asyncio
import logging
import subprocess
from datetime import datetime, timedelta
from typing import Optional, Tuple
import os
import time

logger = logging.getLogger(__name__)


class SSLService:
    """Service for managing SSL certificates via Let's Encrypt and Certbot."""

    # Error messages for common SSL issues
    SSL_ERROR_MESSAGES = {
        "rate_limit": "Let's Encrypt rate limit reached. Try again in 1 hour",
        "dns_not_propagated": "DNS changes not propagated yet. Wait 5-10 minutes",
        "challenge_failed": "ACME challenge failed. Check domain is accessible",
        "invalid_domain": "Domain format invalid or not accessible",
        "cert_not_found": "Certificate not found for domain",
        "timeout": "Operation timed out. Try again later",
    }

    def __init__(self, certbot_path: str = "certbot", webroot_path: str = "/var/www/html"):
        self.certbot_path = certbot_path
        self.webroot_path = webroot_path
        self.cert_dir = "/etc/letsencrypt/live"

    async def provision_certificate(
        self, domain: str, email: str = "admin@platform.com", retry_count: int = 0
    ) -> Tuple[bool, Optional[str]]:
        """
        Request SSL certificate from Let's Encrypt using Certbot.
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            cmd = [
                self.certbot_path,
                "certonly",
                "--webroot",
                "-w", self.webroot_path,
                "-d", domain,
                "--non-interactive",
                "--agree-tos",
                "--email", email,
                "--quiet"
            ]

            stdout, stderr, returncode = await self._run_command(cmd)
            
            if returncode == 0:
                logger.info(f"SSL certificate provisioned for {domain}")
                return True, None
            else:
                error_msg = self._parse_certbot_error(stderr)
                logger.error(f"Failed to provision SSL for {domain}: {error_msg}")
                return False, error_msg
                
        except Exception as e:
            logger.error(f"SSL provisioning error for {domain}: {str(e)}")
            return False, str(e)

    async def renew_certificate(self, domain: str) -> Tuple[bool, Optional[str]]:
        """
        Renew expiring SSL certificate.
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            cmd = [
                self.certbot_path,
                "renew",
                "--cert-name", domain,
                "--quiet"
            ]

            stdout, stderr, returncode = await self._run_command(cmd)
            
            if returncode == 0:
                logger.info(f"SSL certificate renewed for {domain}")
                return True, None
            else:
                error_msg = self._parse_certbot_error(stderr)
                logger.error(f"Failed to renew SSL for {domain}: {error_msg}")
                return False, error_msg
                
        except Exception as e:
            logger.error(f"SSL renewal error for {domain}: {str(e)}")
            return False, str(e)

    async def revoke_certificate(self, domain: str) -> Tuple[bool, Optional[str]]:
        """
        Revoke SSL certificate.
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            cert_path = os.path.join(self.cert_dir, domain, "fullchain.pem")
            if not os.path.exists(cert_path):
                logger.warning(f"Certificate not found for {domain}")
                return False, self.SSL_ERROR_MESSAGES["cert_not_found"]

            cmd = [
                self.certbot_path,
                "revoke",
                "--cert-path", cert_path,
                "--quiet"
            ]

            stdout, stderr, returncode = await self._run_command(cmd)
            
            if returncode == 0:
                logger.info(f"SSL certificate revoked for {domain}")
                return True, None
            else:
                error_msg = self._parse_certbot_error(stderr)
                logger.error(f"Failed to revoke SSL for {domain}: {error_msg}")
                return False, error_msg
                
        except Exception as e:
            logger.error(f"SSL revocation error for {domain}: {str(e)}")
            return False, str(e)

    async def check_certificate_valid(self, domain: str) -> bool:
        """Check if SSL certificate is valid and not expired."""
        try:
            cert_path = os.path.join(self.cert_dir, domain, "fullchain.pem")
            if not os.path.exists(cert_path):
                logger.warning(f"Certificate not found for {domain}")
                return False

            expiry = await self.get_certificate_expiry(domain)
            if expiry is None:
                return False

            return expiry > datetime.utcnow()
        except Exception as e:
            logger.error(f"Certificate validation error for {domain}: {str(e)}")
            return False

    async def get_certificate_expiry(self, domain: str) -> Optional[datetime]:
        """Get SSL certificate expiry date."""
        try:
            cert_path = os.path.join(self.cert_dir, domain, "fullchain.pem")
            if not os.path.exists(cert_path):
                logger.warning(f"Certificate not found for {domain}")
                return None

            cmd = [
                "openssl",
                "x509",
                "-enddate",
                "-noout",
                "-in", cert_path
            ]

            stdout, stderr, returncode = await self._run_command(cmd)
            
            if returncode == 0 and stdout:
                # Parse output: "notAfter=Jan 24 12:34:56 2027 GMT"
                output = stdout.strip()
                if output.startswith("notAfter="):
                    date_str = output.replace("notAfter=", "")
                    expiry = datetime.strptime(date_str, "%b %d %H:%M:%S %Y %Z")
                    logger.info(f"Certificate expiry for {domain}: {expiry}")
                    return expiry
            return None
        except Exception as e:
            logger.error(f"Error getting certificate expiry for {domain}: {str(e)}")
            return None

    def _parse_certbot_error(self, stderr: str) -> str:
        """Parse certbot error output and return user-friendly message."""
        if not stderr:
            return "Unknown error occurred"
        
        stderr_lower = stderr.lower()
        
        if "rate limit" in stderr_lower:
            return self.SSL_ERROR_MESSAGES["rate_limit"]
        elif "dns" in stderr_lower and "propagat" in stderr_lower:
            return self.SSL_ERROR_MESSAGES["dns_not_propagated"]
        elif "challenge" in stderr_lower or "acme" in stderr_lower:
            return self.SSL_ERROR_MESSAGES["challenge_failed"]
        elif "invalid" in stderr_lower or "not found" in stderr_lower:
            return self.SSL_ERROR_MESSAGES["invalid_domain"]
        else:
            return stderr[:200]  # Return first 200 chars of error

    async def _run_command(self, cmd: list) -> Tuple[str, str, int]:
        """
        Run shell command asynchronously.
        
        Returns:
            Tuple of (stdout, stderr, returncode)
        """
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            logger.error(f"Command timeout: {' '.join(cmd)}")
            return "", self.SSL_ERROR_MESSAGES["timeout"], 1
        except Exception as e:
            logger.error(f"Command execution error: {str(e)}")
            return "", str(e), 1
