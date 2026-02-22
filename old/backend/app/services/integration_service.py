from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.integration import (
    Integration,
    IntegrationCreate,
    IntegrationInstallation,
    IntegrationInstallationCreate,
    IntegrationInstallationUpdate,
    IntegrationStatus,
    IntegrationWithInstallation,
    IntegrationTestResult,
)


class IntegrationService:
    """Service for managing integrations"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.integrations_collection = db.integrations
        self.installations_collection = db.integration_installations

    async def get_integrations(
        self, category: Optional[str] = None, tenant_id: Optional[str] = None
    ) -> List[IntegrationWithInstallation]:
        """Get all available integrations with installation status"""
        query = {}
        if category:
            query["category"] = category

        integrations = await self.integrations_collection.find(query).to_list(None)

        # If tenant_id provided, check installation status
        result = []
        for integration in integrations:
            integration["_id"] = str(integration["_id"])
            integration_obj = Integration(**integration)

            if tenant_id:
                installation = await self.get_installation(
                    tenant_id, str(integration["_id"])
                )
                result.append(
                    IntegrationWithInstallation(
                        **integration_obj.model_dump(),
                        installation=installation,
                        is_installed=installation is not None,
                    )
                )
            else:
                result.append(
                    IntegrationWithInstallation(
                        **integration_obj.model_dump(),
                        installation=None,
                        is_installed=False,
                    )
                )

        return result

    async def get_integration(self, integration_id: str) -> Optional[Integration]:
        """Get integration by ID"""
        integration = await self.integrations_collection.find_one(
            {"_id": ObjectId(integration_id)}
        )
        if integration:
            integration["_id"] = str(integration["_id"])
            return Integration(**integration)
        return None

    async def create_integration(
        self, integration_data: IntegrationCreate
    ) -> Integration:
        """Create new integration (admin only)"""
        integration_dict = integration_data.model_dump()
        integration_dict["created_at"] = datetime.utcnow()
        integration_dict["updated_at"] = datetime.utcnow()

        result = await self.integrations_collection.insert_one(integration_dict)
        integration_dict["_id"] = str(result.inserted_id)

        return Integration(**integration_dict)

    async def install_integration(
        self, tenant_id: str, installation_data: IntegrationInstallationCreate
    ) -> IntegrationInstallation:
        """Install integration for tenant"""
        # Check if already installed
        existing = await self.installations_collection.find_one(
            {"tenant_id": tenant_id, "integration_id": installation_data.integration_id}
        )
        if existing:
            raise ValueError("Integration already installed")

        # Verify integration exists
        integration = await self.get_integration(installation_data.integration_id)
        if not integration:
            raise ValueError("Integration not found")

        # Create installation
        installation_dict = installation_data.model_dump()
        installation_dict["tenant_id"] = tenant_id
        installation_dict["status"] = IntegrationStatus.INSTALLED
        installation_dict["installed_at"] = datetime.utcnow()

        # Validate required fields
        if integration.required_fields:
            missing_fields = [
                field
                for field in integration.required_fields
                if field not in installation_dict["configuration"]
            ]
            if missing_fields:
                raise ValueError(
                    f"Missing required configuration fields: {', '.join(missing_fields)}"
                )

        result = await self.installations_collection.insert_one(installation_dict)
        installation_dict["_id"] = str(result.inserted_id)

        return IntegrationInstallation(**installation_dict)

    async def get_installation(
        self, tenant_id: str, integration_id: str
    ) -> Optional[IntegrationInstallation]:
        """Get installation for tenant"""
        installation = await self.installations_collection.find_one(
            {"tenant_id": tenant_id, "integration_id": integration_id}
        )
        if installation:
            installation["_id"] = str(installation["_id"])
            return IntegrationInstallation(**installation)
        return None

    async def get_tenant_installations(
        self, tenant_id: str
    ) -> List[IntegrationInstallation]:
        """Get all installations for tenant"""
        installations = await self.installations_collection.find(
            {"tenant_id": tenant_id}
        ).to_list(None)

        result = []
        for installation in installations:
            installation["_id"] = str(installation["_id"])
            result.append(IntegrationInstallation(**installation))

        return result

    async def update_installation(
        self,
        tenant_id: str,
        integration_id: str,
        update_data: IntegrationInstallationUpdate,
    ) -> Optional[IntegrationInstallation]:
        """Update integration installation"""
        update_dict = {
            k: v for k, v in update_data.model_dump().items() if v is not None
        }

        if not update_dict:
            return await self.get_installation(tenant_id, integration_id)

        result = await self.installations_collection.find_one_and_update(
            {"tenant_id": tenant_id, "integration_id": integration_id},
            {"$set": update_dict},
            return_document=True,
        )

        if result:
            result["_id"] = str(result["_id"])
            return IntegrationInstallation(**result)
        return None

    async def uninstall_integration(
        self, tenant_id: str, integration_id: str
    ) -> bool:
        """Uninstall integration"""
        result = await self.installations_collection.delete_one(
            {"tenant_id": tenant_id, "integration_id": integration_id}
        )
        return result.deleted_count > 0

    async def test_integration(
        self, tenant_id: str, integration_id: str
    ) -> IntegrationTestResult:
        """Test integration connection"""
        installation = await self.get_installation(tenant_id, integration_id)
        if not installation:
            return IntegrationTestResult(
                success=False, message="Integration not installed"
            )

        integration = await self.get_integration(integration_id)
        if not integration:
            return IntegrationTestResult(
                success=False, message="Integration not found"
            )

        # Basic validation - check if all required fields are present
        if integration.required_fields:
            missing_fields = [
                field
                for field in integration.required_fields
                if field not in installation.configuration
            ]
            if missing_fields:
                return IntegrationTestResult(
                    success=False,
                    message=f"Missing configuration: {', '.join(missing_fields)}",
                )

        # Update last sync time
        await self.installations_collection.update_one(
            {"tenant_id": tenant_id, "integration_id": integration_id},
            {"$set": {"last_sync": datetime.utcnow(), "status": IntegrationStatus.ACTIVE}},
        )

        return IntegrationTestResult(
            success=True,
            message="Integration test successful",
            details={"integration": integration.name, "status": "active"},
        )

    async def seed_default_integrations(self):
        """Seed default integrations"""
        default_integrations = [
            {
                "name": "Stripe Payment Gateway",
                "description": "Accept credit card payments with Stripe",
                "category": "payment",
                "provider": "Stripe",
                "version": "1.0.0",
                "icon_url": "https://stripe.com/img/v3/home/social.png",
                "documentation_url": "https://stripe.com/docs",
                "support_url": "https://support.stripe.com",
                "pricing": "2.9% + ₦30 per transaction",
                "features": [
                    "Credit card processing",
                    "Subscription billing",
                    "Refunds and disputes",
                    "Mobile payments",
                ],
                "required_fields": ["api_key", "webhook_secret"],
                "is_premium": False,
                "created_at": datetime.utcnow(),
            },
            {
                "name": "Mailchimp Marketing",
                "description": "Email marketing and automation",
                "category": "marketing",
                "provider": "Mailchimp",
                "version": "1.0.0",
                "icon_url": "https://mailchimp.com/favicon.ico",
                "documentation_url": "https://mailchimp.com/developer",
                "support_url": "https://mailchimp.com/contact",
                "pricing": "Free up to 500 contacts",
                "features": [
                    "Email campaigns",
                    "Marketing automation",
                    "Audience segmentation",
                    "Analytics",
                ],
                "required_fields": ["api_key", "list_id"],
                "is_premium": False,
                "created_at": datetime.utcnow(),
            },
            {
                "name": "QuickBooks Online",
                "description": "Sync accounting data with QuickBooks",
                "category": "accounting",
                "provider": "Intuit",
                "version": "1.0.0",
                "icon_url": "https://quickbooks.intuit.com/favicon.ico",
                "documentation_url": "https://developer.intuit.com",
                "support_url": "https://quickbooks.intuit.com/learn-support",
                "pricing": "Requires QuickBooks subscription",
                "features": [
                    "Invoice sync",
                    "Expense tracking",
                    "Financial reports",
                    "Tax preparation",
                ],
                "required_fields": ["client_id", "client_secret", "realm_id"],
                "is_premium": True,
                "created_at": datetime.utcnow(),
            },
            {
                "name": "Google Analytics",
                "description": "Track website and app analytics",
                "category": "analytics",
                "provider": "Google",
                "version": "1.0.0",
                "icon_url": "https://www.google.com/analytics/favicon.ico",
                "documentation_url": "https://developers.google.com/analytics",
                "support_url": "https://support.google.com/analytics",
                "pricing": "Free",
                "features": [
                    "Website traffic analysis",
                    "User behavior tracking",
                    "Conversion tracking",
                    "Custom reports",
                ],
                "required_fields": ["tracking_id", "property_id"],
                "is_premium": False,
                "created_at": datetime.utcnow(),
            },
            {
                "name": "Twilio SMS",
                "description": "Send SMS notifications via Twilio",
                "category": "communication",
                "provider": "Twilio",
                "version": "1.0.0",
                "icon_url": "https://www.twilio.com/favicon.ico",
                "documentation_url": "https://www.twilio.com/docs",
                "support_url": "https://support.twilio.com",
                "pricing": "Pay as you go",
                "features": [
                    "SMS messaging",
                    "Two-way messaging",
                    "Delivery tracking",
                    "International support",
                ],
                "required_fields": ["account_sid", "auth_token", "phone_number"],
                "is_premium": False,
                "created_at": datetime.utcnow(),
            },
            {
                "name": "Zapier Automation",
                "description": "Connect with 5000+ apps via Zapier",
                "category": "other",
                "provider": "Zapier",
                "version": "1.0.0",
                "icon_url": "https://zapier.com/favicon.ico",
                "documentation_url": "https://zapier.com/developer",
                "support_url": "https://zapier.com/help",
                "pricing": "Free tier available",
                "features": [
                    "Multi-app workflows",
                    "Automated tasks",
                    "Custom triggers",
                    "Data transformation",
                ],
                "required_fields": ["api_key"],
                "is_premium": True,
                "created_at": datetime.utcnow(),
            },
        ]

        # Check if integrations already exist
        count = await self.integrations_collection.count_documents({})
        if count == 0:
            await self.integrations_collection.insert_many(default_integrations)
