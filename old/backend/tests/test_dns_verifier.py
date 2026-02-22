"""Tests for DNS Verifier Service"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import dns.resolver
import dns.exception

from app.services.dns_verifier_service import (
    DNSVerifierService,
    DNSRecord,
    DNSVerificationResult,
)


@pytest.fixture
def dns_verifier():
    """Create DNS Verifier Service instance"""
    return DNSVerifierService()


class TestDNSRecordModel:
    """Test DNSRecord model"""

    def test_dns_record_creation(self):
        """Test creating a DNS record"""
        record = DNSRecord(
            record_type="CNAME",
            host="example.com",
            value="target.com",
            ttl=3600,
        )
        assert record.record_type == "CNAME"
        assert record.host == "example.com"
        assert record.value == "target.com"
        assert record.ttl == 3600

    def test_dns_record_to_dict(self):
        """Test converting DNS record to dict"""
        record = DNSRecord(
            record_type="A",
            host="example.com",
            value="192.0.2.1",
            ttl=3600,
        )
        result = record.to_dict()
        assert result["record_type"] == "A"
        assert result["host"] == "example.com"
        assert result["value"] == "192.0.2.1"
        assert result["ttl"] == 3600


class TestDNSVerificationResult:
    """Test DNSVerificationResult model"""

    def test_verification_result_success(self):
        """Test successful verification result"""
        records = [
            DNSRecord("CNAME", "example.com", "target.com", 3600),
        ]
        result = DNSVerificationResult(
            verified=True,
            message="Domain verified successfully",
            records_found=records,
            issues=[],
        )
        assert result.verified is True
        assert result.message == "Domain verified successfully"
        assert len(result.records_found) == 1
        assert len(result.issues) == 0

    def test_verification_result_failure(self):
        """Test failed verification result"""
        result = DNSVerificationResult(
            verified=False,
            message="Domain verification failed",
            records_found=[],
            issues=["CNAME record not found"],
        )
        assert result.verified is False
        assert len(result.issues) == 1

    def test_verification_result_to_dict(self):
        """Test converting verification result to dict"""
        records = [
            DNSRecord("CNAME", "example.com", "target.com", 3600),
        ]
        result = DNSVerificationResult(
            verified=True,
            message="Success",
            records_found=records,
            issues=[],
        )
        result_dict = result.to_dict()
        assert result_dict["verified"] is True
        assert result_dict["message"] == "Success"
        assert len(result_dict["records_found"]) == 1


class TestDomainValidation:
    """Test domain format validation"""

    def test_validate_valid_domain(self, dns_verifier):
        """Test validating a valid domain"""
        assert dns_verifier._validate_domain_format("example.com") is True
        assert dns_verifier._validate_domain_format("sub.example.com") is True
        assert dns_verifier._validate_domain_format("my-domain.co.uk") is True

    def test_validate_invalid_domain(self, dns_verifier):
        """Test validating invalid domains"""
        assert dns_verifier._validate_domain_format("invalid..com") is False
        assert dns_verifier._validate_domain_format("-invalid.com") is False
        assert dns_verifier._validate_domain_format("invalid-.com") is False
        assert dns_verifier._validate_domain_format("") is False
        assert dns_verifier._validate_domain_format("not a domain") is False


class TestDNSLookup:
    """Test DNS lookup functionality"""

    @pytest.mark.asyncio
    async def test_check_cname_record_valid(self, dns_verifier):
        """Test checking valid CNAME record"""
        with patch.object(dns_verifier._resolver, "resolve") as mock_resolve:
            # Mock DNS response
            mock_rdata = MagicMock()
            mock_rdata.target = "app.yoursalonplatform.com."
            mock_answers = MagicMock()
            mock_answers.__iter__ = MagicMock(return_value=iter([mock_rdata]))
            mock_resolve.return_value = mock_answers

            result = await dns_verifier.check_cname_record("example.com")
            assert result is True

    @pytest.mark.asyncio
    async def test_check_cname_record_invalid(self, dns_verifier):
        """Test checking invalid CNAME record"""
        with patch.object(dns_verifier._resolver, "resolve") as mock_resolve:
            # Mock DNS response with wrong target
            mock_rdata = MagicMock()
            mock_rdata.target = "wrong-target.com."
            mock_answers = MagicMock()
            mock_answers.__iter__ = MagicMock(return_value=iter([mock_rdata]))
            mock_resolve.return_value = mock_answers

            result = await dns_verifier.check_cname_record("example.com")
            assert result is False

    @pytest.mark.asyncio
    async def test_check_cname_record_not_found(self, dns_verifier):
        """Test checking CNAME record when not found"""
        with patch.object(dns_verifier._resolver, "resolve") as mock_resolve:
            mock_resolve.side_effect = dns.resolver.NXDOMAIN()

            result = await dns_verifier.check_cname_record("example.com")
            assert result is False

    @pytest.mark.asyncio
    async def test_check_a_record_valid(self, dns_verifier):
        """Test checking valid A record"""
        with patch.object(dns_verifier._resolver, "resolve") as mock_resolve:
            # Mock DNS response
            mock_rdata = MagicMock()
            mock_rdata.__str__ = MagicMock(return_value="203.0.113.1")
            mock_answers = MagicMock()
            mock_answers.__iter__ = MagicMock(return_value=iter([mock_rdata]))
            mock_resolve.return_value = mock_answers

            result = await dns_verifier.check_a_record("example.com")
            assert result is True

    @pytest.mark.asyncio
    async def test_check_a_record_invalid(self, dns_verifier):
        """Test checking invalid A record"""
        with patch.object(dns_verifier._resolver, "resolve") as mock_resolve:
            # Mock DNS response with wrong IP
            mock_rdata = MagicMock()
            mock_rdata.__str__ = MagicMock(return_value="192.0.2.1")
            mock_answers = MagicMock()
            mock_answers.__iter__ = MagicMock(return_value=iter([mock_rdata]))
            mock_resolve.return_value = mock_answers

            result = await dns_verifier.check_a_record("example.com")
            assert result is False


class TestVerifyDomain:
    """Test domain verification"""

    @pytest.mark.asyncio
    async def test_verify_domain_invalid_format(self, dns_verifier):
        """Test verifying domain with invalid format"""
        result = await dns_verifier.verify_domain("tenant_123", "invalid..domain")
        assert result.verified is False
        assert "Invalid domain format" in result.message

    @pytest.mark.asyncio
    async def test_verify_domain_cname_valid(self, dns_verifier):
        """Test verifying domain with valid CNAME"""
        with patch.object(dns_verifier, "check_cname_record") as mock_cname:
            with patch.object(dns_verifier, "check_a_record") as mock_a:
                with patch.object(dns_verifier, "get_dns_records") as mock_records:
                    mock_cname.return_value = True
                    mock_a.return_value = False
                    mock_records.return_value = [
                        DNSRecord("CNAME", "example.com", "app.yoursalonplatform.com", 3600)
                    ]

                    result = await dns_verifier.verify_domain("tenant_123", "example.com")
                    assert result.verified is True
                    assert "successfully" in result.message.lower()

    @pytest.mark.asyncio
    async def test_verify_domain_no_records(self, dns_verifier):
        """Test verifying domain with no valid records"""
        with patch.object(dns_verifier, "check_cname_record") as mock_cname:
            with patch.object(dns_verifier, "check_a_record") as mock_a:
                with patch.object(dns_verifier, "get_dns_records") as mock_records:
                    mock_cname.return_value = False
                    mock_a.return_value = False
                    mock_records.return_value = []

                    result = await dns_verifier.verify_domain("tenant_123", "example.com")
                    assert result.verified is False
                    assert len(result.issues) > 0


class TestVerificationToken:
    """Test verification token generation"""

    @pytest.mark.asyncio
    async def test_generate_verification_token(self, dns_verifier):
        """Test generating verification token"""
        token = await dns_verifier.generate_verification_token("tenant_123", "example.com")
        assert token is not None
        assert len(token) == 64  # SHA256 hex digest length
        assert isinstance(token, str)

    @pytest.mark.asyncio
    async def test_generate_different_tokens(self, dns_verifier):
        """Test that different calls generate different tokens"""
        token1 = await dns_verifier.generate_verification_token("tenant_123", "example.com")
        token2 = await dns_verifier.generate_verification_token("tenant_123", "example.com")
        # Tokens should be different due to random component
        assert token1 != token2
