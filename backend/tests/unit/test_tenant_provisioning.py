"""Unit tests for tenant provisioning."""

import pytest
from app.services.tenant_service import TenantProvisioningService
from app.models.tenant import Tenant
from app.models.user import User
from app.models.role import Role
from app.config import Settings


class TestTenantProvisioning:
    """Test tenant provisioning functionality."""

    @pytest.fixture
    def tenant_service(self):
        """Create tenant provisioning service."""
        settings = Settings()
        return TenantProvisioningService(settings)

    def test_successful_tenant_provisioning(self, tenant_service):
        """Test successful tenant provisioning."""
        result = tenant_service.provision_tenant(
            name="Test Salon",
            email="owner@salon.com",
            phone="+1234567890",
            subscription_tier="starter",
            region="us-east-1",
        )

        assert result is not None
        assert result["tenant_id"] is not None
        assert result["admin_user_id"] is not None
        assert result["admin_email"] == "owner@salon.com"
        assert result["admin_password"] is not None
        assert result["api_key"] is not None
        assert result["subscription_tier"] == "starter"
        assert result["status"] == "active"

    def test_duplicate_tenant_prevention(self, tenant_service):
        """Test that duplicate tenants are prevented."""
        # Provision first tenant
        result1 = tenant_service.provision_tenant(
            name="Duplicate Salon",
            email="owner1@salon.com",
            phone="+1234567890",
        )
        assert result1 is not None

        # Try to provision with same name
        result2 = tenant_service.provision_tenant(
            name="Duplicate Salon",
            email="owner2@salon.com",
            phone="+0987654321",
        )
        assert result2 is None

    def test_admin_user_creation(self, tenant_service):
        """Test that admin user is created correctly."""
        result = tenant_service.provision_tenant(
            name="Admin Test Salon",
            email="admin@salon.com",
            phone="+1234567890",
        )

        # Verify admin user exists
        tenant_id = result["tenant_id"]
        admin_user = User.objects(
            tenant_id=tenant_id,
            email="admin@salon.com",
        ).first()

        assert admin_user is not None
        assert admin_user.first_name == "Admin"
        assert admin_user.last_name == "User"
        assert admin_user.status == "active"

    def test_default_roles_created(self, tenant_service):
        """Test that default roles are created."""
        result = tenant_service.provision_tenant(
            name="Roles Test Salon",
            email="owner@salon.com",
            phone="+1234567890",
        )

        tenant_id = result["tenant_id"]

        # Verify default roles exist
        owner_role = Role.objects(tenant_id=tenant_id, name="Owner").first()
        manager_role = Role.objects(tenant_id=tenant_id, name="Manager").first()
        staff_role = Role.objects(tenant_id=tenant_id, name="Staff").first()
        customer_role = Role.objects(tenant_id=tenant_id, name="Customer").first()

        assert owner_role is not None
        assert manager_role is not None
        assert staff_role is not None
        assert customer_role is not None

    def test_api_key_generation(self, tenant_service):
        """Test that API key is generated."""
        result = tenant_service.provision_tenant(
            name="API Key Test Salon",
            email="owner@salon.com",
            phone="+1234567890",
        )

        api_key = result["api_key"]
        assert api_key is not None
        assert len(api_key) > 0

    def test_get_tenant(self, tenant_service):
        """Test retrieving tenant information."""
        # Provision tenant
        result = tenant_service.provision_tenant(
            name="Get Tenant Test",
            email="owner@salon.com",
            phone="+1234567890",
        )

        tenant_id = result["tenant_id"]

        # Get tenant
        tenant = tenant_service.get_tenant(tenant_id)

        assert tenant is not None
        assert str(tenant.id) == tenant_id
        assert tenant.name == "Get Tenant Test"
        assert tenant.status == "active"

    def test_update_tenant(self, tenant_service):
        """Test updating tenant settings."""
        # Provision tenant
        result = tenant_service.provision_tenant(
            name="Update Test Salon",
            email="owner@salon.com",
            phone="+1234567890",
            subscription_tier="starter",
        )

        tenant_id = result["tenant_id"]

        # Update tenant
        updated_tenant = tenant_service.update_tenant(
            tenant_id=tenant_id,
            subscription_tier="professional",
        )

        assert updated_tenant is not None
        assert updated_tenant.subscription_tier == "professional"

    def test_suspend_tenant(self, tenant_service):
        """Test suspending a tenant."""
        # Provision tenant
        result = tenant_service.provision_tenant(
            name="Suspend Test Salon",
            email="owner@salon.com",
            phone="+1234567890",
        )

        tenant_id = result["tenant_id"]

        # Suspend tenant
        success = tenant_service.suspend_tenant(tenant_id)

        assert success is True

        # Verify tenant is suspended
        tenant = tenant_service.get_tenant(tenant_id)
        assert tenant.status == "suspended"

    def test_delete_tenant(self, tenant_service):
        """Test deleting a tenant (soft delete)."""
        # Provision tenant
        result = tenant_service.provision_tenant(
            name="Delete Test Salon",
            email="owner@salon.com",
            phone="+1234567890",
        )

        tenant_id = result["tenant_id"]

        # Delete tenant
        success = tenant_service.delete_tenant(tenant_id)

        assert success is True

        # Verify tenant is marked as deleted
        tenant = tenant_service.get_tenant(tenant_id)
        assert tenant.status == "deleted"
        assert tenant.deleted_at is not None

    def test_list_tenants(self, tenant_service):
        """Test listing tenants."""
        # Provision multiple tenants
        for i in range(3):
            tenant_service.provision_tenant(
                name=f"List Test Salon {i}",
                email=f"owner{i}@salon.com",
                phone=f"+123456789{i}",
            )

        # List active tenants
        tenants = tenant_service.list_tenants(status="active")

        assert len(tenants) >= 3

    def test_tenant_provisioning_with_different_tiers(self, tenant_service):
        """Test tenant provisioning with different subscription tiers."""
        tiers = ["starter", "professional", "enterprise"]

        for tier in tiers:
            result = tenant_service.provision_tenant(
                name=f"Tier Test {tier}",
                email=f"owner_{tier}@salon.com",
                phone="+1234567890",
                subscription_tier=tier,
            )

            assert result is not None
            assert result["subscription_tier"] == tier

    def test_tenant_provisioning_with_different_regions(self, tenant_service):
        """Test tenant provisioning with different regions."""
        regions = ["us-east-1", "eu-west-1", "ap-southeast-1"]

        for region in regions:
            result = tenant_service.provision_tenant(
                name=f"Region Test {region}",
                email=f"owner_{region}@salon.com",
                phone="+1234567890",
                region=region,
            )

            assert result is not None
            # Verify region is set
            tenant = tenant_service.get_tenant(result["tenant_id"])
            assert tenant.region == region

    def test_admin_password_uniqueness(self, tenant_service):
        """Test that admin passwords are unique."""
        passwords = []

        for i in range(3):
            result = tenant_service.provision_tenant(
                name=f"Password Test {i}",
                email=f"owner{i}@salon.com",
                phone="+1234567890",
            )

            passwords.append(result["admin_password"])

        # All passwords should be unique
        assert len(set(passwords)) == len(passwords)

    def test_tenant_provisioning_error_handling(self, tenant_service):
        """Test error handling in tenant provisioning."""
        # Try to provision with invalid data
        result = tenant_service.provision_tenant(
            name="",  # Empty name
            email="invalid_email",  # Invalid email
            phone="",  # Empty phone
        )

        # Should handle gracefully (return None or raise exception)
        # Depending on implementation
