from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.white_label import (
    WhiteLabelConfig,
    WhiteLabelConfigCreate,
    WhiteLabelConfigUpdate,
    DNSInstructions,
    WhiteLabelStatus,
)
from app.services.dns_verifier_service import DNSVerifierService


class WhiteLabelService:
    """Service for managing white-label configurations"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.white_label_configs

    async def get_config(self, tenant_id: str) -> Optional[WhiteLabelConfig]:
        """Get white-label configuration for tenant"""
        config = await self.collection.find_one({"tenant_id": tenant_id})
        if config:
            config["_id"] = str(config["_id"])
            return WhiteLabelConfig(**config)
        return None

    async def create_config(
        self, tenant_id: str, config_data: WhiteLabelConfigCreate
    ) -> WhiteLabelConfig:
        """Create white-label configuration"""
        # Check if config already exists
        existing = await self.get_config(tenant_id)
        if existing:
            raise ValueError("White-label configuration already exists")

        config_dict = config_data.model_dump()
        config_dict["tenant_id"] = tenant_id
        config_dict["created_at"] = datetime.utcnow()
        config_dict["updated_at"] = datetime.utcnow()

        result = await self.collection.insert_one(config_dict)
        config_dict["_id"] = str(result.inserted_id)

        return WhiteLabelConfig(**config_dict)

    async def update_config(
        self, tenant_id: str, update_data: WhiteLabelConfigUpdate
    ) -> Optional[WhiteLabelConfig]:
        """Update white-label configuration"""
        update_dict = {}

        # Handle nested updates
        if update_data.branding is not None:
            for key, value in update_data.branding.model_dump().items():
                if value is not None:
                    update_dict[f"branding.{key}"] = value

        if update_data.domain is not None:
            for key, value in update_data.domain.model_dump().items():
                if value is not None:
                    update_dict[f"domain.{key}"] = value

        if update_data.features is not None:
            for key, value in update_data.features.model_dump().items():
                if value is not None:
                    update_dict[f"features.{key}"] = value

        if update_data.is_active is not None:
            update_dict["is_active"] = update_data.is_active

        if not update_dict:
            return await self.get_config(tenant_id)

        update_dict["updated_at"] = datetime.utcnow()

        result = await self.collection.find_one_and_update(
            {"tenant_id": tenant_id},
            {"$set": update_dict},
            return_document=True,
        )

        if result:
            result["_id"] = str(result["_id"])
            return WhiteLabelConfig(**result)
        return None

    async def delete_config(self, tenant_id: str) -> bool:
        """Delete white-label configuration"""
        result = await self.collection.delete_one({"tenant_id": tenant_id})
        return result.deleted_count > 0

    async def get_dns_instructions(
        self, tenant_id: str
    ) -> List[DNSInstructions]:
        """Get DNS configuration instructions"""
        config = await self.get_config(tenant_id)
        if not config or not config.domain.custom_domain:
            return []

        # Generate DNS instructions
        instructions = []

        # CNAME record for custom domain
        instructions.append(
            DNSInstructions(
                record_type="CNAME",
                host=config.domain.custom_domain.split(".")[0],
                value="app.yoursalonplatform.com",
                ttl=3600,
                instructions=f"Add a CNAME record pointing {config.domain.custom_domain} to app.yoursalonplatform.com",
            )
        )

        # SSL/TLS instructions
        if config.domain.ssl_enabled:
            instructions.append(
                DNSInstructions(
                    record_type="TXT",
                    host="_acme-challenge." + config.domain.custom_domain,
                    value="<verification-token>",
                    ttl=3600,
                    instructions="Add this TXT record for SSL certificate verification (will be provided after domain setup)",
                )
            )

        return instructions

    async def verify_domain(self, tenant_id: str) -> bool:
        """Verify custom domain DNS configuration"""
        config = await self.get_config(tenant_id)
        if not config or not config.domain.custom_domain:
            return False

        # Use DNS Verifier Service for actual DNS verification
        dns_verifier = DNSVerifierService()
        try:
            result = await dns_verifier.verify_domain(tenant_id, config.domain.custom_domain)
            
            # Update configuration status based on verification result
            await self.collection.update_one(
                {"tenant_id": tenant_id},
                {
                    "$set": {
                        "domain.dns_configured": result.verified,
                        "updated_at": datetime.utcnow(),
                    }
                },
            )
            
            return result.verified
        finally:
            await dns_verifier.close()

    async def verify_domain_with_details(self, tenant_id: str) -> dict:
        """
        Verify custom domain DNS configuration with detailed error messages
        
        Returns:
            Dict with verification result and detailed error information
        """
        config = await self.get_config(tenant_id)
        if not config:
            return {
                "verified": False,
                "message": "White-label configuration not found",
                "error": "Configuration not found",
                "records": [],
                "issues": ["White-label configuration does not exist"],
            }
        
        if not config.domain.custom_domain:
            return {
                "verified": False,
                "message": "No custom domain configured",
                "error": "Domain not set",
                "records": [],
                "issues": ["Custom domain has not been set"],
            }
        
        # Use DNS Verifier Service for actual DNS verification
        dns_verifier = DNSVerifierService()
        try:
            result = await dns_verifier.verify_domain(tenant_id, config.domain.custom_domain)
            
            # Update configuration status based on verification result
            await self.collection.update_one(
                {"tenant_id": tenant_id},
                {
                    "$set": {
                        "domain.dns_configured": result.verified,
                        "updated_at": datetime.utcnow(),
                    }
                },
            )
            
            return {
                "verified": result.verified,
                "message": result.message,
                "error": None if result.verified else "DNS verification failed",
                "records": [r.to_dict() for r in result.records_found],
                "issues": result.issues,
            }
        except Exception as e:
            return {
                "verified": False,
                "message": f"DNS verification error: {str(e)}",
                "error": str(e),
                "records": [],
                "issues": [f"DNS lookup failed: {str(e)}"],
            }
        finally:
            await dns_verifier.close()

    async def get_status(self, tenant_id: str) -> WhiteLabelStatus:
        """Get white-label configuration status"""
        config = await self.get_config(tenant_id)

        if not config:
            return WhiteLabelStatus(
                is_configured=False,
                is_active=False,
                has_custom_domain=False,
                domain_verified=False,
                ssl_enabled=False,
                branding_complete=False,
                issues=["White-label not configured"],
            )

        issues = []

        # Check branding completeness
        branding_complete = bool(
            config.branding.logo_url
            and config.branding.primary_color
            and config.branding.company_name
        )
        if not branding_complete:
            issues.append("Branding incomplete - add logo, colors, and company name")

        # Check domain configuration
        has_custom_domain = bool(config.domain.custom_domain)
        if has_custom_domain and not config.domain.dns_configured:
            issues.append("Custom domain DNS not configured")

        # Check SSL
        if has_custom_domain and not config.domain.ssl_enabled:
            issues.append("SSL not enabled for custom domain")

        return WhiteLabelStatus(
            is_configured=True,
            is_active=config.is_active,
            has_custom_domain=has_custom_domain,
            domain_verified=config.domain.dns_configured,
            ssl_enabled=config.domain.ssl_enabled,
            branding_complete=branding_complete,
            issues=issues,
        )

    async def get_config_by_domain(self, domain: str) -> Optional[WhiteLabelConfig]:
        """Get white-label configuration by custom domain"""
        config = await self.collection.find_one(
            {"domain.custom_domain": domain, "is_active": True}
        )
        if config:
            config["_id"] = str(config["_id"])
            return WhiteLabelConfig(**config)
        return None
