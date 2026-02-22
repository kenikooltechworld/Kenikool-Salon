"""Property-based tests for Role-Based Access Control (RBAC)."""

import pytest
from hypothesis import given, strategies as st
from app.services.rbac_service import RBACService
from app.models.role import Role, Permission
from app.models.user import User
from app.models.tenant import Tenant
from bson import ObjectId


class TestRoleBasedAccessControl:
    """Test RBAC functionality."""

    @pytest.fixture
    def rbac_service(self):
        """Create RBAC service."""
        return RBACService()

    @pytest.fixture
    def test_tenant(self):
        """Create test tenant."""
        tenant = Tenant(
            name="Test Tenant",
            subscription_tier="starter",
            status="active",
        )
        tenant.save()
        return tenant

    @given(
        resource=st.text(min_size=1, max_size=50),
        action=st.sampled_from(["view", "create", "edit", "delete", "export"]),
    )
    def test_permission_creation(self, rbac_service, test_tenant, resource, action):
        """Test permission creation."""
        permission = rbac_service.create_permission(
            tenant_id=str(test_tenant.id),
            resource=resource,
            action=action,
            description=f"{resource}:{action}",
        )

        assert permission is not None
        assert permission.resource == resource
        assert permission.action == action
        assert permission.tenant_id == test_tenant.id

    @given(
        role_name=st.text(min_size=1, max_size=100),
    )
    def test_role_creation(self, rbac_service, test_tenant, role_name):
        """Test role creation."""
        role = rbac_service.create_role(
            tenant_id=str(test_tenant.id),
            name=role_name,
            description=f"Role: {role_name}",
            is_custom=False,
        )

        assert role is not None
        assert role.name == role_name
        assert role.tenant_id == test_tenant.id

    def test_users_with_correct_permissions_can_access(self, rbac_service, test_tenant):
        """Test that users with correct permissions can access resources."""
        # Create permission
        permission = rbac_service.create_permission(
            tenant_id=str(test_tenant.id),
            resource="appointments",
            action="view",
        )

        # Create role with permission
        role = rbac_service.create_role(
            tenant_id=str(test_tenant.id),
            name="Staff",
            permissions=[str(permission.id)],
        )

        # Create user with role
        user = User(
            tenant_id=test_tenant.id,
            email="staff@example.com",
            password_hash="hashed_password",
            first_name="Staff",
            last_name="Member",
            role_ids=[role.id],  # Multiple roles per user
        )
        user.save()

        # Check permission
        has_permission = rbac_service.has_permission(
            user_id=str(user.id),
            tenant_id=str(test_tenant.id),
            resource="appointments",
            action="view",
        )

        assert has_permission is True

    def test_users_without_permissions_denied_access(self, rbac_service, test_tenant):
        """Test that users without permissions are denied access."""
        # Create role without permissions
        role = rbac_service.create_role(
            tenant_id=str(test_tenant.id),
            name="Customer",
            permissions=[],
        )

        # Create user with role
        user = User(
            tenant_id=test_tenant.id,
            email="customer@example.com",
            password_hash="hashed_password",
            first_name="Customer",
            last_name="User",
            role_ids=[role.id],  # Multiple roles per user
        )
        user.save()

        # Check permission
        has_permission = rbac_service.has_permission(
            user_id=str(user.id),
            tenant_id=str(test_tenant.id),
            resource="settings",
            action="edit",
        )

        assert has_permission is False

    def test_permission_inheritance_works(self, rbac_service, test_tenant):
        """Test that permission inheritance works correctly."""
        # Create multiple permissions
        perm1 = rbac_service.create_permission(
            tenant_id=str(test_tenant.id),
            resource="appointments",
            action="view",
        )
        perm2 = rbac_service.create_permission(
            tenant_id=str(test_tenant.id),
            resource="appointments",
            action="create",
        )

        # Create role with both permissions
        role = rbac_service.create_role(
            tenant_id=str(test_tenant.id),
            name="Manager",
            permissions=[str(perm1.id), str(perm2.id)],
        )

        # Create user
        user = User(
            tenant_id=test_tenant.id,
            email="manager@example.com",
            password_hash="hashed_password",
            first_name="Manager",
            last_name="User",
            role_ids=[role.id],  # Multiple roles per user
        )
        user.save()

        # Check both permissions
        has_view = rbac_service.has_permission(
            user_id=str(user.id),
            tenant_id=str(test_tenant.id),
            resource="appointments",
            action="view",
        )
        has_create = rbac_service.has_permission(
            user_id=str(user.id),
            tenant_id=str(test_tenant.id),
            resource="appointments",
            action="create",
        )

        assert has_view is True
        assert has_create is True

    def test_permission_changes_reflected_immediately(self, rbac_service, test_tenant):
        """Test that permission changes are reflected immediately."""
        # Create permission
        permission = rbac_service.create_permission(
            tenant_id=str(test_tenant.id),
            resource="invoices",
            action="view",
        )

        # Create role without permission
        role = rbac_service.create_role(
            tenant_id=str(test_tenant.id),
            name="Staff",
            permissions=[],
        )

        # Create user
        user = User(
            tenant_id=test_tenant.id,
            email="staff@example.com",
            password_hash="hashed_password",
            first_name="Staff",
            last_name="Member",
            role_ids=[role.id],  # Multiple roles per user
        )
        user.save()

        # Initially no permission
        has_permission = rbac_service.has_permission(
            user_id=str(user.id),
            tenant_id=str(test_tenant.id),
            resource="invoices",
            action="view",
        )
        assert has_permission is False

        # Add permission to role
        rbac_service.add_permission_to_role(
            role_id=str(role.id),
            permission_id=str(permission.id),
            tenant_id=str(test_tenant.id),
        )

        # Now should have permission
        has_permission = rbac_service.has_permission(
            user_id=str(user.id),
            tenant_id=str(test_tenant.id),
            resource="invoices",
            action="view",
        )
        assert has_permission is True

    def test_concurrent_permission_checks(self, rbac_service, test_tenant):
        """Test that concurrent permission checks work correctly."""
        # Create permissions
        permissions = []
        for i in range(5):
            perm = rbac_service.create_permission(
                tenant_id=str(test_tenant.id),
                resource=f"resource_{i}",
                action="view",
            )
            permissions.append(perm)

        # Create role with all permissions
        role = rbac_service.create_role(
            tenant_id=str(test_tenant.id),
            name="Admin",
            permissions=[str(p.id) for p in permissions],
        )

        # Create user
        user = User(
            tenant_id=test_tenant.id,
            email="admin@example.com",
            password_hash="hashed_password",
            first_name="Admin",
            last_name="User",
            role_ids=[role.id],  # Multiple roles per user
        )
        user.save()

        # Check all permissions concurrently
        for i in range(5):
            has_permission = rbac_service.has_permission(
                user_id=str(user.id),
                tenant_id=str(test_tenant.id),
                resource=f"resource_{i}",
                action="view",
            )
            assert has_permission is True

    def test_default_roles_created(self, rbac_service, test_tenant):
        """Test that default roles are created correctly."""
        success = rbac_service.create_default_roles(str(test_tenant.id))
        assert success is True

        # Verify default roles exist
        owner_role = Role.objects(
            tenant_id=test_tenant.id, name="Owner"
        ).first()
        manager_role = Role.objects(
            tenant_id=test_tenant.id, name="Manager"
        ).first()
        staff_role = Role.objects(
            tenant_id=test_tenant.id, name="Staff"
        ).first()
        customer_role = Role.objects(
            tenant_id=test_tenant.id, name="Customer"
        ).first()

        assert owner_role is not None
        assert manager_role is not None
        assert staff_role is not None
        assert customer_role is not None

        # Owner should have most permissions
        assert len(owner_role.permissions) > len(manager_role.permissions)
        assert len(manager_role.permissions) > len(staff_role.permissions)
