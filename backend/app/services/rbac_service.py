"""Role-Based Access Control (RBAC) service."""

import logging
from typing import List, Optional
from app.models.role import Role, Permission
from app.models.user import User

logger = logging.getLogger(__name__)


class RBACService:
    """Service for managing roles and permissions."""

    def __init__(self):
        """Initialize RBAC service."""
        self.permission_cache = {}

    def create_permission(
        self, tenant_id: str, resource: str, action: str, description: str = ""
    ) -> Optional[Permission]:
        """Create a new permission."""
        try:
            permission = Permission(
                tenant_id=tenant_id,
                resource=resource,
                action=action,
                description=description,
            )
            permission.save()
            logger.info(f"Permission created: {resource}:{action}")
            return permission
        except Exception as e:
            logger.error(f"Error creating permission: {e}")
            return None

    def create_role(
        self,
        tenant_id: str,
        name: str,
        description: str = "",
        permissions: List[str] = None,
        is_custom: bool = False,
    ) -> Optional[Role]:
        """Create a new role."""
        try:
            permission_ids = []
            if permissions:
                for perm_id in permissions:
                    permission_ids.append(perm_id)

            role = Role(
                tenant_id=tenant_id,
                name=name,
                description=description,
                permissions=permission_ids,
                is_custom=is_custom,
            )
            role.save()
            logger.info(f"Role created: {name}")
            return role
        except Exception as e:
            logger.error(f"Error creating role: {e}")
            return None

    def assign_role_to_user(
        self, user_id: str, role_id: str, tenant_id: str
    ) -> bool:
        """Assign a role to a user (adds to existing roles)."""
        try:
            user = User.objects(id=user_id, tenant_id=tenant_id).first()
            if not user:
                logger.warning(f"User not found: {user_id}")
                return False

            if role_id not in user.role_ids:
                user.role_ids.append(role_id)
                user.save()
                logger.info(f"Role {role_id} assigned to user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error assigning role: {e}")
            return False

    def get_user_permissions(self, user_id: str, tenant_id: str) -> List[str]:
        """Get all permissions for a user from all their roles."""
        try:
            user = User.objects(id=user_id, tenant_id=tenant_id).first()
            if not user:
                logger.warning(f"User not found: {user_id}")
                return []

            all_permissions = set()
            for role_id in user.role_ids:
                role = Role.objects(id=role_id, tenant_id=tenant_id).first()
                if role:
                    permissions = Permission.objects(
                        id__in=role.permissions, tenant_id=tenant_id
                    )
                    for p in permissions:
                        all_permissions.add(f"{p.resource}:{p.action}")
            
            return list(all_permissions)
        except Exception as e:
            logger.error(f"Error getting user permissions: {e}")
            return []

    def has_permission(
        self, user_id: str, tenant_id: str, resource: str, action: str
    ) -> bool:
        """Check if user has a specific permission."""
        try:
            permissions = self.get_user_permissions(user_id, tenant_id)
            permission_string = f"{resource}:{action}"
            return permission_string in permissions
        except Exception as e:
            logger.error(f"Error checking permission: {e}")
            return False

    def add_permission_to_role(
        self, role_id: str, permission_id: str, tenant_id: str
    ) -> bool:
        """Add a permission to a role."""
        try:
            role = Role.objects(id=role_id, tenant_id=tenant_id).first()
            if not role:
                logger.warning(f"Role not found: {role_id}")
                return False

            if permission_id not in role.permissions:
                role.permissions.append(permission_id)
                role.save()
                logger.info(f"Permission {permission_id} added to role {role_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding permission to role: {e}")
            return False

    def remove_permission_from_role(
        self, role_id: str, permission_id: str, tenant_id: str
    ) -> bool:
        """Remove a permission from a role."""
        try:
            role = Role.objects(id=role_id, tenant_id=tenant_id).first()
            if not role:
                logger.warning(f"Role not found: {role_id}")
                return False

            if permission_id in role.permissions:
                role.permissions.remove(permission_id)
                role.save()
                logger.info(f"Permission {permission_id} removed from role {role_id}")
            return True
        except Exception as e:
            logger.error(f"Error removing permission from role: {e}")
            return False

    def create_default_roles(self, tenant_id: str) -> bool:
        """Create default roles for a tenant."""
        try:
            # Create default permissions
            permissions = {
                "appointments": ["view", "create", "edit", "delete"],
                "customers": ["view", "create", "edit", "delete"],
                "staff": ["view", "create", "edit", "delete"],
                "services": ["view", "create", "edit", "delete"],
                "invoices": ["view", "create", "edit", "delete"],
                "reports": ["view", "export"],
                "settings": ["view", "edit"],
            }

            permission_ids = {}
            for resource, actions in permissions.items():
                for action in actions:
                    perm = self.create_permission(
                        tenant_id, resource, action, f"{resource}:{action}"
                    )
                    if perm:
                        permission_ids[f"{resource}:{action}"] = str(perm.id)

            # Create Owner role (all permissions)
            owner_perms = list(permission_ids.values())
            self.create_role(
                tenant_id,
                "Owner",
                "Full platform access",
                owner_perms,
                is_custom=False,
            )

            # Create Manager role (operational management)
            manager_perms = [
                permission_ids.get("appointments:view"),
                permission_ids.get("appointments:create"),
                permission_ids.get("appointments:edit"),
                permission_ids.get("customers:view"),
                permission_ids.get("customers:create"),
                permission_ids.get("customers:edit"),
                permission_ids.get("staff:view"),
                permission_ids.get("staff:edit"),
                permission_ids.get("services:view"),
                permission_ids.get("invoices:view"),
                permission_ids.get("reports:view"),
            ]
            manager_perms = [p for p in manager_perms if p]
            self.create_role(
                tenant_id,
                "Manager",
                "Staff and operational management",
                manager_perms,
                is_custom=False,
            )

            # Create Staff role (limited access)
            staff_perms = [
                permission_ids.get("appointments:view"),
                permission_ids.get("customers:view"),
            ]
            staff_perms = [p for p in staff_perms if p]
            self.create_role(
                tenant_id,
                "Staff",
                "Limited to assigned services and schedule",
                staff_perms,
                is_custom=False,
            )

            # Create Customer role (self-service)
            customer_perms = [
                permission_ids.get("appointments:view"),
                permission_ids.get("appointments:create"),
            ]
            customer_perms = [p for p in customer_perms if p]
            self.create_role(
                tenant_id,
                "Customer",
                "Self-service appointment booking and profile",
                customer_perms,
                is_custom=False,
            )

            logger.info(f"Default roles created for tenant: {tenant_id}")
            return True
        except Exception as e:
            logger.error(f"Error creating default roles: {e}")
            return False
