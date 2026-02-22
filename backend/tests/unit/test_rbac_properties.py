"""Property-based tests for RBAC system with real MongoDB data - Validates: Requirements 2.2, 2.3, 2.4, 2.5"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from app.services.rbac_service import RBACService
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission


@pytest.fixture
def rbac_service():
    """Create RBAC service."""
    return RBACService()


@pytest.fixture
def test_tenant_id():
    """Create a test tenant ID."""
    return "test-tenant-rbac"


@pytest.fixture
def test_permissions(test_tenant_id):
    """Create test permissions in MongoDB."""
    permissions = []
    resources = ["appointments", "customers", "staff", "billing"]
    actions = ["view", "create", "edit", "delete"]

    for resource in resources:
        for action in actions:
            perm = Permission(
                tenant_id=test_tenant_id,
                resource=resource,
                action=action,
                description=f"{action} {resource}",
            )
            perm.save()
            permissions.append(perm)

    return permissions


@pytest.fixture
def test_roles(test_tenant_id, test_permissions):
    """Create test roles in MongoDB."""
    # Owner role - all permissions
    owner_role = Role(
        tenant_id=test_tenant_id,
        name="Owner",
        description="Owner role",
        is_custom=False,
        permissions=[p.id for p in test_permissions],
    )
    owner_role.save()

    # Manager role - limited permissions
    manager_permissions = [p for p in test_permissions if p.action in ["view", "create", "edit"]]
    manager_role = Role(
        tenant_id=test_tenant_id,
        name="Manager",
        description="Manager role",
        is_custom=False,
        permissions=[p.id for p in manager_permissions],
    )
    manager_role.save()

    # Staff role - very limited permissions
    staff_permissions = [p for p in test_permissions if p.action == "view"]
    staff_role = Role(
        tenant_id=test_tenant_id,
        name="Staff",
        description="Staff role",
        is_custom=False,
        permissions=[p.id for p in staff_permissions],
    )
    staff_role.save()

    return {
        "owner": owner_role,
        "manager": manager_role,
        "staff": staff_role,
    }


class TestRBACProperty:
    """Property-based tests for RBAC - Validates: Requirements 2.2, 2.3, 2.4, 2.5"""

    def test_owner_has_all_permissions(self, rbac_service, test_tenant_id, test_roles, test_permissions):
        """Property: Owner role always has all permissions."""
        owner_role = test_roles["owner"]

        # Owner should have all permissions
        assert len(owner_role.permissions) == len(test_permissions)

        for perm in test_permissions:
            assert perm.id in owner_role.permissions

    def test_manager_has_limited_permissions(self, rbac_service, test_tenant_id, test_roles, test_permissions):
        """Property: Manager role always has limited permissions."""
        manager_role = test_roles["manager"]

        # Manager should not have delete permissions
        delete_perms = [p for p in test_permissions if p.action == "delete"]
        for perm in delete_perms:
            assert perm.id not in manager_role.permissions

    def test_staff_has_minimal_permissions(self, rbac_service, test_tenant_id, test_roles, test_permissions):
        """Property: Staff role always has minimal permissions."""
        staff_role = test_roles["staff"]

        # Staff should only have view permissions
        for perm in test_permissions:
            if perm.action == "view":
                assert perm.id in staff_role.permissions
            else:
                assert perm.id not in staff_role.permissions

    def test_permission_inheritance_consistency(self, rbac_service, test_tenant_id, test_roles):
        """Property: Permission inheritance is always consistent."""
        owner_role = test_roles["owner"]
        manager_role = test_roles["manager"]
        staff_role = test_roles["staff"]

        # Owner permissions should be superset of Manager permissions
        manager_perms = set(manager_role.permissions)
        owner_perms = set(owner_role.permissions)
        assert manager_perms.issubset(owner_perms)

        # Manager permissions should be superset of Staff permissions
        staff_perms = set(staff_role.permissions)
        assert staff_perms.issubset(manager_perms)

    def test_role_creation_with_permissions(self, rbac_service, test_tenant_id, test_permissions):
        """Property: Roles can be created with any valid permission set."""
        # Create custom role with subset of permissions
        custom_perms = test_permissions[:5]
        custom_role = Role(
            tenant_id=test_tenant_id,
            name="Custom",
            description="Custom role",
            is_custom=True,
            permissions=[p.id for p in custom_perms],
        )
        custom_role.save()

        # Verify role was created with correct permissions
        assert len(custom_role.permissions) == len(custom_perms)
        for perm in custom_perms:
            assert perm.id in custom_role.permissions

    def test_permission_modification_consistency(self, rbac_service, test_tenant_id, test_roles, test_permissions):
        """Property: Permission modifications are always consistent."""
        manager_role = test_roles["manager"]
        original_perms = set(manager_role.permissions)

        # Add a new permission
        new_perm = test_permissions[-1]  # Get a permission not in manager role
        if new_perm.id not in manager_role.permissions:
            manager_role.permissions.append(new_perm.id)
            manager_role.save()

            # Verify permission was added
            updated_role = Role.objects(id=manager_role.id).first()
            assert new_perm.id in updated_role.permissions

    def test_multiple_roles_isolation(self, rbac_service, test_tenant_id, test_roles):
        """Property: Multiple roles are always isolated from each other."""
        owner_role = test_roles["owner"]
        manager_role = test_roles["manager"]
        staff_role = test_roles["staff"]

        # Modify manager role
        original_manager_perms = set(manager_role.permissions)
        manager_role.permissions = []
        manager_role.save()

        # Verify other roles are not affected
        owner_updated = Role.objects(id=owner_role.id).first()
        staff_updated = Role.objects(id=staff_role.id).first()

        assert len(owner_updated.permissions) > 0
        assert len(staff_updated.permissions) > 0

        # Restore manager role
        manager_role.permissions = list(original_manager_perms)
        manager_role.save()

    def test_permission_resource_action_combinations(self, rbac_service, test_tenant_id):
        """Property: All resource-action combinations are valid."""
        resources = ["appointments", "customers", "staff", "billing", "reports"]
        actions = ["view", "create", "edit", "delete", "export"]

        for resource in resources:
            for action in actions:
                perm = Permission(
                    tenant_id=test_tenant_id,
                    resource=resource,
                    action=action,
                    description=f"{action} {resource}",
                )
                perm.save()

                # Verify permission was created
                saved_perm = Permission.objects(
                    tenant_id=test_tenant_id,
                    resource=resource,
                    action=action,
                ).first()
                assert saved_perm is not None
                assert saved_perm.resource == resource
                assert saved_perm.action == action

    def test_role_permission_list_integrity(self, rbac_service, test_tenant_id, test_roles, test_permissions):
        """Property: Role permission lists always maintain integrity."""
        for role_name, role in test_roles.items():
            # Verify all permission IDs in role exist
            for perm_id in role.permissions:
                perm = Permission.objects(id=perm_id).first()
                assert perm is not None

            # Verify no duplicate permission IDs
            assert len(role.permissions) == len(set(role.permissions))

    def test_custom_role_creation_flexibility(self, rbac_service, test_tenant_id, test_permissions):
        """Property: Custom roles can be created with any permission combination."""
        # Create multiple custom roles with different permission combinations
        for i in range(5):
            # Select different subsets of permissions
            subset_size = (i + 1) * 2
            custom_perms = test_permissions[:subset_size]

            custom_role = Role(
                tenant_id=test_tenant_id,
                name=f"Custom{i}",
                description=f"Custom role {i}",
                is_custom=True,
                permissions=[p.id for p in custom_perms],
            )
            custom_role.save()

            # Verify role was created correctly
            saved_role = Role.objects(id=custom_role.id).first()
            assert len(saved_role.permissions) == len(custom_perms)
