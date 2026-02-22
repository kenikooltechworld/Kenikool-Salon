from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SSLCertificateBase(BaseModel):
    """Base SSL certificate configuration"""
    domain: str = Field(..., description="Domain for which certificate is issued")
    certificate_path: str = Field(..., description="Path to certificate file in storage")
    private_key_path: str = Field(..., description="Path to private key file in storage")
    issuer: str = Field(default="Let's Encrypt", description="Certificate issuer")
    status: str = Field(default="active", description="Certificate status: active, expired, revoked, pending")


class SSLCertificateCreate(SSLCertificateBase):
    """Schema for creating SSL certificate"""
    pass


class SSLCertificateUpdate(BaseModel):
    """Schema for updating SSL certificate"""
    certificate_path: Optional[str] = None
    private_key_path: Optional[str] = None
    status: Optional[str] = None


class SSLCertificate(SSLCertificateBase):
    """SSL certificate with metadata"""
    id: str = Field(..., alias="_id", description="Certificate ID")
    tenant_id: str = Field(..., description="Tenant ID")
    issued_at: datetime = Field(..., description="Certificate issue date")
    expires_at: datetime = Field(..., description="Certificate expiration date")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    renewal_attempted_at: Optional[datetime] = Field(None, description="Last renewal attempt timestamp")
    renewal_failed_reason: Optional[str] = Field(None, description="Reason for renewal failure if applicable")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "ssl_123",
                "tenant_id": "tenant_123",
                "domain": "booking.mysalon.com",
                "certificate_path": "white-label/tenant_123/ssl/cert.pem",
                "private_key_path": "white-label/tenant_123/ssl/key.pem",
                "issuer": "Let's Encrypt",
                "status": "active",
                "issued_at": "2024-01-01T00:00:00Z",
                "expires_at": "2025-01-01T00:00:00Z",
                "created_at": "2024-01-01T00:00:00Z"
            }
        }


class SSLCertificateListResponse(BaseModel):
    """Response for listing SSL certificates"""
    certificates: list[SSLCertificate] = Field(..., description="List of certificates")
    total: int = Field(..., description="Total number of certificates")


class ACMEChallenge(BaseModel):
    """ACME challenge for certificate validation"""
    challenge_type: str = Field(..., description="Challenge type: http-01 or dns-01")
    token: str = Field(..., description="Challenge token")
    key_authorization: str = Field(..., description="Key authorization string")
    instructions: str = Field(..., description="Human-readable instructions for completing challenge")
    expires_at: datetime = Field(..., description="Challenge expiration time")


class CertificateRenewalStatus(BaseModel):
    """Status of certificate renewal"""
    domain: str = Field(..., description="Domain")
    current_status: str = Field(..., description="Current certificate status")
    expires_at: datetime = Field(..., description="Current certificate expiration")
    days_until_expiry: int = Field(..., description="Days until expiration")
    renewal_needed: bool = Field(..., description="Whether renewal is needed")
    last_renewal_attempt: Optional[datetime] = Field(None, description="Last renewal attempt")
    last_renewal_error: Optional[str] = Field(None, description="Last renewal error message")
