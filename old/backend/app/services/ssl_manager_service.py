"""
SSL Manager Service for Let's Encrypt certificate provisioning and management.

This service handles:
- Certificate provisioning via Let's Encrypt
- ACME challenge generation (HTTP-01 and DNS-01)
- Certificate storage and retrieval
- Certificate renewal and revocation
- Nginx configuration management for SSL
"""
import logging
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple, List
from dataclasses import dataclass, asdict
import os

from app.database import Database
from app.services.ssl_service import SSLService
from app.services.nginx_config_service import NginxConfigService

logger = logging.getLogger(__name__)


@dataclass
class ACMEChallenge:
    """ACME challenge data"""
    challenge_type: str  # "http-01" or "dns-01"
    token: str
    key_authorization: str
    instructions: str
    domain: str
    created_at: datetime


@dataclass
class SSLCertificate:
    """SSL certificate data"""
    domain: str
    certificate_path: str
    private_key_path: str
    issued_at: datetime
    expires_at: datetime
    issuer: str
    status: str  # "active", "expired", "revoked"
    tenant_id: str


class SSLManagerService:
    """Service for managing SSL certificates via Let's Encrypt"""

    def __init__(self):
        self.ssl_service = SSLService()
        self._db = None  # Lazy-loaded database
        self.cert_dir = "/etc/letsencrypt/live"
        self.challenge_dir = "/var/www/html/.well-known/acme-challenge"

    @property
    def db(self):
        """Lazy-load database connection"""
        if self._db is None:
            self._db = Database.get_db()
        return self._db

    async def provision_certificate(
        self,
        tenant_id: str,
        domain: str,
        email: str = "admin@platform.com"
    ) -> Tuple[bool, Optional[str], Optional[SSLCertificate]]:
        """
        Provision SSL certificate from Let's Encrypt and configure Nginx.

        Args:
            tenant_id: Tenant ID
            domain: Domain to provision certificate for
            email: Email for Let's Encrypt account

        Returns:
            Tuple of (success, error_message, certificate)
        """
        try:
            logger.info(f"Provisioning SSL certificate for {domain} (tenant: {tenant_id})")

            # Provision certificate using certbot
            success, error = await self.ssl_service.provision_certificate(domain, email)

            if not success:
                logger.error(f"Failed to provision certificate for {domain}: {error}")
                return False, error, None

            # Get certificate details
            cert = await self._get_certificate_details(domain, tenant_id)
            if not cert:
                logger.error(f"Failed to retrieve certificate details for {domain}")
                return False, "Failed to retrieve certificate details", None

            # Store certificate in database
            await self._store_certificate(cert)

            # Configure Nginx for the domain with SSL
            nginx_success = await self._configure_nginx_for_domain(domain)
            if not nginx_success:
                logger.warning(f"Failed to configure Nginx for {domain}, but certificate was provisioned")
                # Don't fail the entire operation if Nginx config fails
                # The certificate is still valid, just not yet served

            logger.info(f"SSL certificate provisioned successfully for {domain}")
            return True, None, cert

        except Exception as e:
            error_msg = f"SSL provisioning error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg, None

    async def renew_certificate(
        self,
        tenant_id: str,
        domain: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Renew expiring SSL certificate and reload Nginx.

        Args:
            tenant_id: Tenant ID
            domain: Domain to renew certificate for

        Returns:
            Tuple of (success, error_message)
        """
        try:
            logger.info(f"Renewing SSL certificate for {domain} (tenant: {tenant_id})")

            # Renew certificate using certbot
            success, error = await self.ssl_service.renew_certificate(domain)

            if not success:
                logger.error(f"Failed to renew certificate for {domain}: {error}")
                return False, error

            # Update certificate in database
            cert = await self._get_certificate_details(domain, tenant_id)
            if cert:
                await self._store_certificate(cert)

            # Reload Nginx to use renewed certificate
            nginx_success = await NginxConfigService.reload_nginx()
            if not nginx_success:
                logger.warning(f"Failed to reload Nginx after certificate renewal for {domain}")
                # Don't fail the operation - certificate is renewed, just Nginx reload failed

            logger.info(f"SSL certificate renewed successfully for {domain}")
            return True, None

        except Exception as e:
            error_msg = f"SSL renewal error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg

    async def revoke_certificate(
        self,
        tenant_id: str,
        domain: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Revoke SSL certificate and remove Nginx configuration.

        Args:
            tenant_id: Tenant ID
            domain: Domain to revoke certificate for

        Returns:
            Tuple of (success, error_message)
        """
        try:
            logger.info(f"Revoking SSL certificate for {domain} (tenant: {tenant_id})")

            # Revoke certificate using certbot
            success, error = await self.ssl_service.revoke_certificate(domain)

            if not success:
                logger.error(f"Failed to revoke certificate for {domain}: {error}")
                return False, error

            # Update certificate status in database
            self.db.ssl_certificates.update_one(
                {"domain": domain, "tenant_id": tenant_id},
                {"$set": {
                    "status": "revoked",
                    "updated_at": datetime.utcnow()
                }}
            )

            # Remove Nginx configuration for the domain
            nginx_success = await NginxConfigService.remove_config(domain)
            if not nginx_success:
                logger.warning(f"Failed to remove Nginx config for {domain}, but certificate was revoked")
                # Don't fail the operation - certificate is revoked, just Nginx removal failed

            logger.info(f"SSL certificate revoked successfully for {domain}")
            return True, None

        except Exception as e:
            error_msg = f"SSL revocation error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg

    async def get_acme_challenge(
        self,
        domain: str,
        challenge_type: str = "dns-01"
    ) -> Tuple[bool, Optional[str], Optional[ACMEChallenge]]:
        """
        Generate ACME challenge for domain verification.

        Args:
            domain: Domain to generate challenge for
            challenge_type: Type of challenge ("http-01" or "dns-01")

        Returns:
            Tuple of (success, error_message, challenge)
        """
        try:
            logger.info(f"Generating ACME {challenge_type} challenge for {domain}")

            # For now, we'll use a simplified approach
            # In production, this would integrate with acme library
            import secrets
            import hashlib

            # Generate random token
            token = secrets.token_urlsafe(32)

            # Generate key authorization (token.key_thumbprint)
            # Simplified: using hash of token
            key_authorization = hashlib.sha256(token.encode()).hexdigest()

            if challenge_type == "dns-01":
                # For DNS-01, create TXT record value
                txt_value = hashlib.sha256(key_authorization.encode()).hexdigest()
                instructions = (
                    f"Create a DNS TXT record:\n"
                    f"Name: _acme-challenge.{domain}\n"
                    f"Value: {txt_value}\n"
                    f"TTL: 300"
                )
            elif challenge_type == "http-01":
                # For HTTP-01, create file path
                instructions = (
                    f"Create a file at:\n"
                    f"Path: /.well-known/acme-challenge/{token}\n"
                    f"Content: {key_authorization}"
                )
            else:
                return False, f"Unsupported challenge type: {challenge_type}", None

            challenge = ACMEChallenge(
                challenge_type=challenge_type,
                token=token,
                key_authorization=key_authorization,
                instructions=instructions,
                domain=domain,
                created_at=datetime.utcnow()
            )

            logger.info(f"ACME challenge generated for {domain}")
            return True, None, challenge

        except Exception as e:
            error_msg = f"ACME challenge generation error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg, None

    async def validate_acme_challenge(
        self,
        domain: str,
        challenge_type: str,
        token: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate ACME challenge response.

        Args:
            domain: Domain being validated
            challenge_type: Type of challenge
            token: Challenge token

        Returns:
            Tuple of (success, error_message)
        """
        try:
            logger.info(f"Validating ACME {challenge_type} challenge for {domain}")

            if challenge_type == "dns-01":
                # Verify DNS TXT record
                success = await self._verify_dns_challenge(domain, token)
                if not success:
                    return False, "DNS TXT record not found or incorrect"

            elif challenge_type == "http-01":
                # Verify HTTP challenge file
                success = await self._verify_http_challenge(domain, token)
                if not success:
                    return False, "HTTP challenge file not accessible"

            else:
                return False, f"Unsupported challenge type: {challenge_type}"

            logger.info(f"ACME challenge validated for {domain}")
            return True, None

        except Exception as e:
            error_msg = f"ACME challenge validation error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg

    async def check_certificate_expiry(
        self,
        domain: str
    ) -> Optional[datetime]:
        """
        Check SSL certificate expiry date.

        Args:
            domain: Domain to check

        Returns:
            Expiry datetime or None if not found
        """
        try:
            expiry = await self.ssl_service.get_certificate_expiry(domain)
            return expiry
        except Exception as e:
            logger.error(f"Error checking certificate expiry for {domain}: {str(e)}")
            return None

    async def get_certificate_status(
        self,
        tenant_id: str,
        domain: str
    ) -> Optional[Dict]:
        """
        Get certificate status from database.

        Args:
            tenant_id: Tenant ID
            domain: Domain

        Returns:
            Certificate document or None
        """
        try:
            cert = self.db.ssl_certificates.find_one({
                "domain": domain,
                "tenant_id": tenant_id
            })
            return cert
        except Exception as e:
            logger.error(f"Error getting certificate status: {str(e)}")
            return None

    async def list_certificates(
        self,
        tenant_id: str
    ) -> List[Dict]:
        """
        List all certificates for a tenant.

        Args:
            tenant_id: Tenant ID

        Returns:
            List of certificate documents
        """
        try:
            certs = list(self.db.ssl_certificates.find({
                "tenant_id": tenant_id
            }))
            return certs
        except Exception as e:
            logger.error(f"Error listing certificates: {str(e)}")
            return []

    async def _configure_nginx_for_domain(self, domain: str) -> bool:
        """
        Configure Nginx for a domain with SSL certificate.

        This method generates, validates, and enables Nginx configuration
        for the domain, then reloads Nginx without downtime.

        Args:
            domain: Domain to configure

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Configuring Nginx for domain: {domain}")

            # Generate Nginx configuration from template
            config = await NginxConfigService.generate_config(domain)
            if not config:
                logger.error(f"Failed to generate Nginx config for {domain}")
                return False

            # Validate configuration syntax
            if not await NginxConfigService.validate_config(config):
                logger.error(f"Nginx configuration validation failed for {domain}")
                return False

            # Write configuration to file
            if not await NginxConfigService.write_config(domain, config):
                logger.error(f"Failed to write Nginx config for {domain}")
                return False

            # Enable configuration by creating symlink
            if not await NginxConfigService.enable_config(domain):
                logger.error(f"Failed to enable Nginx config for {domain}")
                return False

            # Reload Nginx with new configuration (graceful reload)
            if not await NginxConfigService.reload_nginx():
                logger.error(f"Failed to reload Nginx for {domain}")
                return False

            logger.info(f"Nginx configured successfully for {domain}")
            return True

        except Exception as e:
            logger.error(f"Error configuring Nginx for {domain}: {str(e)}")
            return False

    async def _get_certificate_details(
        self,
        domain: str,
        tenant_id: str
    ) -> Optional[SSLCertificate]:
        """
        Get certificate details from filesystem.

        Args:
            domain: Domain
            tenant_id: Tenant ID

        Returns:
            SSLCertificate object or None
        """
        try:
            cert_path = os.path.join(self.cert_dir, domain, "fullchain.pem")
            key_path = os.path.join(self.cert_dir, domain, "privkey.pem")

            if not os.path.exists(cert_path) or not os.path.exists(key_path):
                logger.warning(f"Certificate files not found for {domain}")
                return None

            # Get expiry date
            expiry = await self.ssl_service.get_certificate_expiry(domain)
            if not expiry:
                logger.warning(f"Could not determine expiry for {domain}")
                return None

            cert = SSLCertificate(
                domain=domain,
                certificate_path=cert_path,
                private_key_path=key_path,
                issued_at=datetime.utcnow(),
                expires_at=expiry,
                issuer="Let's Encrypt",
                status="active",
                tenant_id=tenant_id
            )

            return cert

        except Exception as e:
            logger.error(f"Error getting certificate details: {str(e)}")
            return None

    async def _store_certificate(self, cert: SSLCertificate) -> bool:
        """
        Store certificate in database.

        Args:
            cert: SSLCertificate object

        Returns:
            Success status
        """
        try:
            cert_doc = {
                "domain": cert.domain,
                "tenant_id": cert.tenant_id,
                "certificate_path": cert.certificate_path,
                "private_key_path": cert.private_key_path,
                "issued_at": cert.issued_at,
                "expires_at": cert.expires_at,
                "issuer": cert.issuer,
                "status": cert.status,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }

            # Upsert certificate
            self.db.ssl_certificates.update_one(
                {"domain": cert.domain, "tenant_id": cert.tenant_id},
                {"$set": cert_doc},
                upsert=True
            )

            logger.info(f"Certificate stored for {cert.domain}")
            return True

        except Exception as e:
            logger.error(f"Error storing certificate: {str(e)}")
            return False

    async def _verify_dns_challenge(
        self,
        domain: str,
        token: str
    ) -> bool:
        """
        Verify DNS challenge TXT record.

        Args:
            domain: Domain
            token: Challenge token

        Returns:
            True if verified, False otherwise
        """
        try:
            import dns.resolver

            # Construct DNS query name
            query_name = f"_acme-challenge.{domain}"

            # Query DNS
            answers = dns.resolver.resolve(query_name, "TXT")

            # Check if token is in answers
            for rdata in answers:
                for txt_data in rdata.strings:
                    if token in txt_data.decode():
                        logger.info(f"DNS challenge verified for {domain}")
                        return True

            logger.warning(f"DNS challenge token not found for {domain}")
            return False

        except Exception as e:
            logger.error(f"DNS challenge verification error: {str(e)}")
            return False

    async def _verify_http_challenge(
        self,
        domain: str,
        token: str
    ) -> bool:
        """
        Verify HTTP challenge file.

        Args:
            domain: Domain
            token: Challenge token

        Returns:
            True if verified, False otherwise
        """
        try:
            import httpx

            # Construct challenge URL
            url = f"http://{domain}/.well-known/acme-challenge/{token}"

            # Make request
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10)

                if response.status_code == 200:
                    logger.info(f"HTTP challenge verified for {domain}")
                    return True

            logger.warning(f"HTTP challenge file not accessible for {domain}")
            return False

        except Exception as e:
            logger.error(f"HTTP challenge verification error: {str(e)}")
            return False
