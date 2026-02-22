"""DNS Verifier Service for White Label System"""
import asyncio
import re
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import dns.resolver
import dns.exception
import redis.asyncio as redis

from app.config import settings


class DNSRecord:
    """Represents a DNS record"""
    def __init__(self, record_type: str, host: str, value: str, ttl: int = 3600):
        self.record_type = record_type
        self.host = host
        self.value = value
        self.ttl = ttl

    def to_dict(self) -> Dict:
        return {
            "record_type": self.record_type,
            "host": self.host,
            "value": self.value,
            "ttl": self.ttl,
        }


class DNSVerificationResult:
    """Result of DNS verification"""
    def __init__(
        self,
        verified: bool,
        message: str,
        records_found: List[DNSRecord] = None,
        issues: List[str] = None,
        verified_at: Optional[datetime] = None,
    ):
        self.verified = verified
        self.message = message
        self.records_found = records_found or []
        self.issues = issues or []
        self.verified_at = verified_at

    def to_dict(self) -> Dict:
        return {
            "verified": self.verified,
            "message": self.message,
            "records_found": [r.to_dict() for r in self.records_found],
            "issues": self.issues,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
        }


class DNSVerifierService:
    """Service for verifying DNS configuration for custom domains"""

    # Platform configuration
    PLATFORM_DOMAIN = "app.yoursalonplatform.com"
    PLATFORM_IP = "203.0.113.1"  # Example IP - should be configured
    DNS_CACHE_TTL = 300  # 5 minutes
    DNS_LOOKUP_TIMEOUT = 10  # seconds
    MAX_RETRIES = 3
    RETRY_BACKOFF = 2  # exponential backoff multiplier

    def __init__(self):
        """Initialize DNS Verifier Service"""
        self.redis_client = None
        self._resolver = dns.resolver.Resolver()
        self._resolver.timeout = self.DNS_LOOKUP_TIMEOUT
        self._resolver.lifetime = self.DNS_LOOKUP_TIMEOUT

    async def _get_redis(self) -> redis.Redis:
        """Get or create Redis connection"""
        if self.redis_client is None:
            self.redis_client = await redis.from_url(settings.REDIS_URL)
        return self.redis_client

    async def _cache_get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        try:
            redis_client = await self._get_redis()
            return await redis_client.get(key)
        except Exception:
            return None

    async def _cache_set(self, key: str, value: str, ttl: int = DNS_CACHE_TTL) -> None:
        """Set value in cache"""
        try:
            redis_client = await self._get_redis()
            await redis_client.setex(key, ttl, value)
        except Exception:
            pass

    def _validate_domain_format(self, domain: str) -> bool:
        """
        Validate domain format

        Args:
            domain: Domain to validate

        Returns:
            True if domain format is valid
        """
        # Domain regex pattern
        domain_pattern = r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$"
        return bool(re.match(domain_pattern, domain.lower()))

    async def check_cname_record(
        self,
        domain: str,
        expected_target: str = PLATFORM_DOMAIN,
    ) -> bool:
        """
        Check if CNAME record points to expected target

        Args:
            domain: Domain to check
            expected_target: Expected CNAME target

        Returns:
            True if CNAME record is correct
        """
        try:
            # Try with retries and exponential backoff
            for attempt in range(self.MAX_RETRIES):
                try:
                    answers = self._resolver.resolve(domain, "CNAME")
                    for rdata in answers:
                        target = str(rdata.target).rstrip(".")
                        if target.lower() == expected_target.lower():
                            return True
                    return False
                except dns.exception.Timeout:
                    if attempt < self.MAX_RETRIES - 1:
                        await asyncio.sleep(self.RETRY_BACKOFF ** attempt)
                    else:
                        raise
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.DNSException):
            return False

    async def check_a_record(
        self,
        domain: str,
        expected_ip: str = PLATFORM_IP,
    ) -> bool:
        """
        Check if A record points to expected IP

        Args:
            domain: Domain to check
            expected_ip: Expected A record IP

        Returns:
            True if A record is correct
        """
        try:
            # Try with retries and exponential backoff
            for attempt in range(self.MAX_RETRIES):
                try:
                    answers = self._resolver.resolve(domain, "A")
                    for rdata in answers:
                        if str(rdata) == expected_ip:
                            return True
                    return False
                except dns.exception.Timeout:
                    if attempt < self.MAX_RETRIES - 1:
                        await asyncio.sleep(self.RETRY_BACKOFF ** attempt)
                    else:
                        raise
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.DNSException):
            return False

    async def get_dns_records(self, domain: str) -> List[DNSRecord]:
        """
        Get DNS records for a domain

        Args:
            domain: Domain to query

        Returns:
            List of DNS records found
        """
        records = []

        # Check CNAME records
        try:
            answers = self._resolver.resolve(domain, "CNAME")
            for rdata in answers:
                records.append(
                    DNSRecord(
                        record_type="CNAME",
                        host=domain,
                        value=str(rdata.target).rstrip("."),
                        ttl=answers.rrset.ttl,
                    )
                )
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.DNSException):
            pass

        # Check A records
        try:
            answers = self._resolver.resolve(domain, "A")
            for rdata in answers:
                records.append(
                    DNSRecord(
                        record_type="A",
                        host=domain,
                        value=str(rdata),
                        ttl=answers.rrset.ttl,
                    )
                )
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.DNSException):
            pass

        # Check TXT records
        try:
            answers = self._resolver.resolve(domain, "TXT")
            for rdata in answers:
                records.append(
                    DNSRecord(
                        record_type="TXT",
                        host=domain,
                        value=str(rdata),
                        ttl=answers.rrset.ttl,
                    )
                )
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.DNSException):
            pass

        return records

    async def verify_domain(
        self,
        tenant_id: str,
        domain: str,
    ) -> DNSVerificationResult:
        """
        Verify DNS configuration for a custom domain

        Args:
            tenant_id: Tenant identifier
            domain: Domain to verify

        Returns:
            DNSVerificationResult with verification status
        """
        # Check cache first
        cache_key = f"dns_verify:{domain}"
        cached_result = await self._cache_get(cache_key)
        if cached_result:
            import json
            result_dict = json.loads(cached_result)
            return DNSVerificationResult(
                verified=result_dict["verified"],
                message=result_dict["message"],
                records_found=[
                    DNSRecord(
                        r["record_type"],
                        r["host"],
                        r["value"],
                        r["ttl"],
                    )
                    for r in result_dict["records_found"]
                ],
                issues=result_dict["issues"],
                verified_at=datetime.fromisoformat(result_dict["verified_at"])
                if result_dict["verified_at"]
                else None,
            )

        # Validate domain format
        if not self._validate_domain_format(domain):
            result = DNSVerificationResult(
                verified=False,
                message=f"Invalid domain format: {domain}",
                issues=["Domain format is invalid"],
            )
            return result

        # Get DNS records
        records = await self.get_dns_records(domain)

        # Check for correct CNAME record
        cname_valid = await self.check_cname_record(domain)

        # Check for correct A record
        a_valid = await self.check_a_record(domain)

        # Check www variant
        www_domain = f"www.{domain}"
        www_cname_valid = await self.check_cname_record(www_domain)
        www_a_valid = await self.check_a_record(www_domain)

        # Determine verification status
        verified = cname_valid or a_valid or www_cname_valid or www_a_valid
        issues = []

        if not cname_valid and not www_cname_valid:
            issues.append(
                f"CNAME record not found or incorrect. Expected: {domain} -> {self.PLATFORM_DOMAIN}"
            )

        if not a_valid and not www_a_valid:
            issues.append(
                f"A record not found or incorrect. Expected: {domain} -> {self.PLATFORM_IP}"
            )

        message = (
            "Domain verified successfully"
            if verified
            else "Domain verification failed. Please check your DNS configuration."
        )

        result = DNSVerificationResult(
            verified=verified,
            message=message,
            records_found=records,
            issues=issues,
            verified_at=datetime.utcnow() if verified else None,
        )

        # Cache the result
        import json
        await self._cache_set(cache_key, json.dumps(result.to_dict()))

        return result

    async def generate_verification_token(
        self,
        tenant_id: str,
        domain: str,
    ) -> str:
        """
        Generate a verification token for DNS TXT record

        Args:
            tenant_id: Tenant identifier
            domain: Domain to verify

        Returns:
            Verification token
        """
        import hashlib
        import secrets

        # Generate random token
        random_part = secrets.token_hex(16)

        # Create hash with tenant_id and domain
        hash_input = f"{tenant_id}:{domain}:{random_part}"
        token = hashlib.sha256(hash_input.encode()).hexdigest()

        # Cache token for 24 hours
        cache_key = f"dns_token:{tenant_id}:{domain}"
        await self._cache_set(cache_key, token, ttl=86400)

        return token

    async def close(self) -> None:
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
