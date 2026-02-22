"""
Pydantic schemas for domain management.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DNSRecord(BaseModel):
    """DNS record schema"""
    type: str = Field(..., description="Record type (A, CNAME, TXT)")
    name: str = Field(..., description="Record name")
    value: str = Field(..., description="Record value")
    ttl: int = Field(default=3600, description="Time to live")
    status: str = Field(default="pending", description="Record status")


class DomainCreate(BaseModel):
    """Schema for creating a domain"""
    domain: str = Field(..., description="Domain name")


class DomainVerify(BaseModel):
    """Schema for verifying a domain"""
    domain: str = Field(..., description="Domain name")


class DomainResponse(BaseModel):
    """Schema for domain response"""
    id: str = Field(..., description="Domain ID")
    tenant_id: str = Field(..., description="Tenant ID")
    domain: str = Field(..., description="Domain name")
    status: str = Field(..., description="Domain status")
    verification_token: Optional[str] = Field(None, description="Verification token")
    ssl_status: str = Field(..., description="SSL status")
    ssl_expires_at: Optional[datetime] = Field(None, description="SSL expiry date")
    verified_at: Optional[datetime] = Field(None, description="Verification date")
    activated_at: Optional[datetime] = Field(None, description="Activation date")
    health_check_at: Optional[datetime] = Field(None, description="Last health check")
    health_issues: Optional[List[str]] = Field(None, description="Health issues")
    created_at: datetime = Field(..., description="Creation date")
    updated_at: datetime = Field(..., description="Update date")


class DomainListResponse(BaseModel):
    """Schema for domain list response"""
    domains: List[DomainResponse]


class VerificationResult(BaseModel):
    """Schema for verification result"""
    domain: str = Field(..., description="Domain name")
    verified: bool = Field(..., description="Verification status")
    dns_records_valid: bool = Field(..., description="DNS records valid")
    ssl_provisioned: bool = Field(..., description="SSL provisioned")
    errors: List[str] = Field(default_factory=list, description="Errors")
    warnings: List[str] = Field(default_factory=list, description="Warnings")


class DNSInstructions(BaseModel):
    """Schema for DNS instructions"""
    dns_records: List[DNSRecord]
