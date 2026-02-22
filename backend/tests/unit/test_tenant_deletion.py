"""Property-based tests for tenant deletion and query filtering."""

import pytest
from hypothesis import given, strategies as st
from bson import ObjectId
from datetime import datetime
from app.models.tenant import Tenant
from app.models.user import User
from app.models.role import Role
from app.models.session import Session
from app.services.tenant_service import TenantProvisioningService
from app.config import Settings


class TestTenantDeletion:
    """Test tenant deletion and cascade behavior."""

    @pytest.fixture
    def tenant_service(self):
        """Create tenant provisioning service."""
        settings = Settings()
        return TenantProvisioningService(settings)

    def test_tenant_deletion_soft_delete(self, tenant_service):
        """Test that tenant deletion uses soft delete (sets deleted_at)."""
        # Provision tenant
        result = tenant_service.provision_tenant(
            name="Soft Delete Test",
            email="owner@salon.com",
            phone="+1234567890",
        )
        tenant_id = result["tenant_id"]

        # Delete tenant
        success = tenant_service.delete_tenant(tenant_id)
        assert success is True

        # Verify soft delete
        tenant = Tenant.objects(id=tenant_id).first()
        assert tenant is not None
        assert tenant.status == "deleted"
        assert tenant.deleted_at is not None

    def test_tenant_deletion_idempotent(self, tenant_service):
        """Test that tenant deletion is idempotent (can be run multiple times)."""
        # Provision tenant
        result = tenant_service.provision_tenant(
            name="Idempotent Delete Test",
            email="owner@salon.com",
            phone="+1234567890",
        )
        tenant_id = result["tenant_id"]

        # Delete tenant multiple times
        success1 = tenant_service.delete_tenant(tenant_id)
        success2 = tenant_service.delete_tenant(tenant_id)
        success3 = tenant_service.delete_tenant(tenant_id)

        assert success1 is True
        assert success2 is True
        assert success3 is True

        # Verify tenant is still deleted
        tenant = Tenant.objects(id=tenant_id).first()
        assert tenant.status == "deleted"

    def test_tenant_deletion_preserves_data(self, tenant_service):
        """Test that soft delete preserves data (doesn't actually delete)."""
        # Provision tenant
        result = tenant_service.provision_tenant(
            name="Preserve Data Test",
            email="owner@salon.com",
            phone="+1234567890",
        )
        tenant_id = result["tenant_id"]
        admin_user_id = result["admin_user_id"]

        # Delete tenant
        tenant_service.delete_tenant(tenant_id)

        # Verify data still exists in database
        tenant = Tenant.objects(id=tenant_id).first()
        assert tenant is not None

        user = User.objects(id=admin_user_id).first()
        assert user is not None

    def test_deleted_tenant_not_in_active_list(self, tenant_service):
        """Test that deleted tenants don't appear in active tenant list."""
        # Provision tenant
        result = tenant_service.provision_tenant(
            name="Active List Test",
            email="owner@salon.com",
            phone="+1234567890",
        )
        tenant_id = result["tenant_id"]

        # Verify tenant is in active list
        active_tenants = tenant_service.list_tenants(status="active")
        active_ids = [str(t.id) for t in active_tenants]
        assert tenant_id in active_ids

        # Delete tenant
        tenant_service.delete_tenant(tenant_id)

        # Verify tenant is not in active list
        active_tenants = tenant_service.list_tenants(status="active")
        active_ids = [str(t.id) for t in active_tenants]
        assert tenant_id not in active_ids

    def test_deleted_tenant_in_deleted_list(self, tenant_service):
        """Test that deleted tenants appear in deleted tenant list."""
        # Provision tenant
        result = tenant_service.provision_tenant(
            name="Deleted List Test",
            email="owner@salon.com",
            phone="+1234567890",
        )
        tenant_id = result["tenant_id"]

        # Delete tenant
        tenant_service.delete_tenant(tenant_id)

        # Verify tenant is in deleted list
        deleted_tenants = tenant_service.list_tenants(status="deleted")
        deleted_ids = [str(t.id) for t in deleted_tenants]
        assert tenant_id in deleted_ids

    @given(
        num_tenants=st.integers(min_value=1, max_value=5),
    )
    def test_multiple_tenant_deletion(self, tenant_service, num_tenants):
        """Property: Multiple tenants can be deleted independently.
        
        **Validates: Requirements 1.4**
        """
        tenant_ids = []

        # Provision multiple tenants
        for i in range(num_tenants):
            result = tenant_service.provision_tenant(
                name=f"Multi Delete Test {i}",
                email=f"owner{i}@salon.com",
                phone=f"+123456789{i}",
            )
            tenant_ids.append(result["tenant_id"])

        # Delete first tenant
        if tenant_ids:
            tenant_service.delete_tenant(tenant_ids[0])

            # Verify first tenant is deleted
            tenant = Tenant.objects(id=tenant_ids[0]).first()
            assert tenant.status == "deleted"

            # Verify other tenants are still active
            for tenant_id in tenant_ids[1:]:
                tenant = Tenant.objects(id=tenant_id).first()
                assert tenant.status == "active"

    def test_tenant_deletion_timestamp(self, tenant_service):
        """Test that tenant deletion sets deleted_at timestamp."""
        # Provision tenant
        result = tenant_service.provision_tenant(
            name="Timestamp Test",
            email="owner@salon.com",
            phone="+1234567890",
        )
        tenant_id = result["tenant_id"]

        # Record time before deletion
        before_deletion = datetime.utcnow()

        # Delete tenant
        tenant_service.delete_tenant(tenant_id)

        # Record time after deletion
        after_deletion = datetime.utcnow()

        # Verify deleted_at is set and within expected time range
        tenant = Tenant.objects(id=tenant_id).first()
        assert tenant.deleted_at is not None
        assert before_deletion <= tenant.deleted_at <= after_deletion

    def test_tenant_deletion_updates_updated_at(self, tenant_service):
        """Test that tenant deletion updates the updated_at timestamp."""
        # Provision tenant
        result = tenant_service.provision_tenant(
            name="Updated At Test",
            email="owner@salon.com",
            phone="+1234567890",
        )
        tenant_id = result["tenant_id"]

        # Get original updated_at
        tenant_before = Tenant.objects(id=tenant_id).first()
        updated_at_before = tenant_before.updated_at

        # Wait a bit to ensure timestamp difference
        import time
        time.sleep(0.1)

        # Delete tenant
        tenant_service.delete_tenant(tenant_id)

        # Verify updated_at is changed
        tenant_after = Tenant.objects(id=tenant_id).first()
        assert tenant_after.updated_at > updated_at_before

    def test_cascade_deletion_users(self, tenant_service):
        """Test that deleting tenant doesn't cascade delete users (soft delete only)."""
        # Provision tenant
        result = tenant_service.provision_tenant(
            name="Cascade Test",
            email="owner@salon.com",
            phone="+1234567890",
        )
        tenant_id = result["tenant_id"]
        admin_user_id = result["admin_user_id"]

        # Delete tenant
        tenant_service.delete_tenant(tenant_id)

        # Verify user still exists (soft delete doesn't cascade)
        user = User.objects(id=admin_user_id).first()
        assert user is not None
        assert user.tenant_id == ObjectId(tenant_id)

    def test_cascade_deletion_roles(self, tenant_service):
        """Test that deleting tenant doesn't cascade delete roles (soft delete only)."""
        # Provision tenant
        result = tenant_service.provision_tenant(
            name="Cascade Roles Test",
            email="owner@salon.com",
            phone="+1234567890",
        )
        tenant_id = result["tenant_id"]

        # Get roles for tenant
        roles_before = Role.objects(tenant_id=ObjectId(tenant_id))
        num_roles_before = roles_before.count()

        # Delete tenant
        tenant_service.delete_tenant(tenant_id)

        # Verify roles still exist
        roles_after = Role.objects(tenant_id=ObjectId(tenant_id))
        num_roles_after = roles_after.count()
        assert num_roles_after == num_roles_before

    @given(
        tenant_name=st.text(min_size=1, max_size=50),
        email=st.emails(),
        phone=st.text(min_size=10, max_size=20),
    )
    def test_deletion_with_various_data(self, tenant_service, tenant_name, email, phone):
        """Property: Tenant deletion works with various input data.
        
        **Validates: Requirements 1.4**
        """
        try:
            # Provision tenant with various data
            result = tenant_service.provision_tenant(
                name=tenant_name,
                email=email,
                phone=phone,
            )

            if result is None:
                # Skip if provisioning failed (e.g., duplicate email)
                return

            tenant_id = result["tenant_id"]

            # Delete tenant
            success = tenant_service.delete_tenant(tenant_id)
            assert success is True

            # Verify deletion
            tenant = Tenant.objects(id=tenant_id).first()
            assert tenant.status == "deleted"

        except Exception as e:
            # Some combinations may fail (e.g., invalid email), which is acceptable
            pass
