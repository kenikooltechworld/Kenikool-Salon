"""
Database models for custom domains.
"""
from datetime import datetime
from typing import Optional, List


class Domain:
    """Domain model for MongoDB"""

    def __init__(
        self,
        tenant_id: str,
        domain: str,
        status: str = "pending",
        verification_token: Optional[str] = None,
        ssl_status: str = "none",
        ssl_expires_at: Optional[datetime] = None,
        verified_at: Optional[datetime] = None,
        activated_at: Optional[datetime] = None,
        health_check_at: Optional[datetime] = None,
        health_issues: Optional[List[str]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        _id: Optional[str] = None
    ):
        self._id = _id
        self.tenant_id = tenant_id
        self.domain = domain
        self.status = status  # pending, verified, failed, warning, revoked
        self.verification_token = verification_token
        self.ssl_status = ssl_status  # none, pending, active, expired
        self.ssl_expires_at = ssl_expires_at
        self.verified_at = verified_at
        self.activated_at = activated_at
        self.health_check_at = health_check_at
        self.health_issues = health_issues or []
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_dict(self) -> dict:
        """Convert to dictionary for MongoDB"""
        return {
            "tenant_id": self.tenant_id,
            "domain": self.domain,
            "status": self.status,
            "verification_token": self.verification_token,
            "ssl_status": self.ssl_status,
            "ssl_expires_at": self.ssl_expires_at,
            "verified_at": self.verified_at,
            "activated_at": self.activated_at,
            "health_check_at": self.health_check_at,
            "health_issues": self.health_issues,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @staticmethod
    def from_dict(data: dict) -> "Domain":
        """Create from dictionary"""
        return Domain(
            tenant_id=data.get("tenant_id"),
            domain=data.get("domain"),
            status=data.get("status", "pending"),
            verification_token=data.get("verification_token"),
            ssl_status=data.get("ssl_status", "none"),
            ssl_expires_at=data.get("ssl_expires_at"),
            verified_at=data.get("verified_at"),
            activated_at=data.get("activated_at"),
            health_check_at=data.get("health_check_at"),
            health_issues=data.get("health_issues", []),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            _id=str(data.get("_id")) if data.get("_id") else None
        )
