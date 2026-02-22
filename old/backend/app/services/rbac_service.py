"""
Role-based access control service for analytics
"""
import logging
from typing import List, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class AnalyticsRole(str, Enum):
    """Analytics roles"""
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"
    VIEWER = "viewer"


class AnalyticsPermission(str, Enum):
    """Analytics permissions"""
    VIEW_ANALYTICS = "view_analytics"
    VIEW_FINANCIAL = "view_financial"
    VIEW_CLIENTS = "view_clients"
    VIEW_INVENTORY = "view_inventory"
    VIEW_CAMPAIGNS = "view_campaigns"
    VIEW_PREDICTIONS = "view_predictions"
    CREATE_REPORTS = "create_reports"
    EXPORT_DATA = "export_data"
    MANAGE_GOALS = "manage_goals"
    MANAGE_ALERTS = "manage_alerts"
    MANAGE_USERS = "manage_users"
    VIEW_STAFF_ANALYTICS = "view_staff_analytics"
    VIEW_LOCATION_ANALYTICS = "view_location_analytics"


class RBACService:
    """Service for managing role-based access control"""

    # Define role permissions
    ROLE_PERMISSIONS = {
        AnalyticsRole.ADMIN: [
            AnalyticsPermission.VIEW_ANALYTICS,
            AnalyticsPermission.VIEW_FINANCIAL,
            AnalyticsPermission.VIEW_CLIENTS,
            AnalyticsPermission.VIEW_INVENTORY,
            AnalyticsPermission.VIEW_CAMPAIGNS,
            AnalyticsPermission.VIEW_PREDICTIONS,
            AnalyticsPermission.CREATE_REPORTS,
            AnalyticsPermission.EXPORT_DATA,
            AnalyticsPermission.MANAGE_GOALS,
            AnalyticsPermission.MANAGE_ALERTS,
            AnalyticsPermission.MANAGE_USERS,
            AnalyticsPermission.VIEW_STAFF_ANALYTICS,
            AnalyticsPermission.VIEW_LOCATION_ANALYTICS,
        ],
        AnalyticsRole.MANAGER: [
            AnalyticsPermission.VIEW_ANALYTICS,
            AnalyticsPermission.VIEW_FINANCIAL,
            AnalyticsPermission.VIEW_CLIENTS,
            AnalyticsPermission.VIEW_INVENTORY,
            AnalyticsPermission.VIEW_CAMPAIGNS,
            AnalyticsPermission.VIEW_PREDICTIONS,
            AnalyticsPermission.CREATE_REPORTS,
            AnalyticsPermission.EXPORT_DATA,
            AnalyticsPermission.MANAGE_GOALS,
            AnalyticsPermission.MANAGE_ALERTS,
            AnalyticsPermission.VIEW_STAFF_ANALYTICS,
            AnalyticsPermission.VIEW_LOCATION_ANALYTICS,
        ],
        AnalyticsRole.STAFF: [
            AnalyticsPermission.VIEW_ANALYTICS,
            AnalyticsPermission.VIEW_CLIENTS,
            AnalyticsPermission.VIEW_INVENTORY,
            AnalyticsPermission.VIEW_CAMPAIGNS,
        ],
        AnalyticsRole.VIEWER: [
            AnalyticsPermission.VIEW_ANALYTICS,
            AnalyticsPermission.VIEW_CLIENTS,
        ],
    }

    def __init__(self):
        """Initialize RBAC service"""
        self.user_roles: Dict[str, List[AnalyticsRole]] = {}
        self.user_permissions: Dict[str, List[AnalyticsPermission]] = {}

    def has_permission(
        self,
        user_id: str,
        permission: AnalyticsPermission,
        role: AnalyticsRole = None
    ) -> bool:
        """Check if user has a specific permission"""
        if role:
            return permission in self.ROLE_PERMISSIONS.get(role, [])
        
        # Check user's roles
        user_roles = self.user_roles.get(user_id, [])
        for user_role in user_roles:
            if permission in self.ROLE_PERMISSIONS.get(user_role, []):
                return True
        
        return False

    def has_any_permission(
        self,
        user_id: str,
        permissions: List[AnalyticsPermission]
    ) -> bool:
        """Check if user has any of the specified permissions"""
        for permission in permissions:
            if self.has_permission(user_id, permission):
                return True
        return False

    def has_all_permissions(
        self,
        user_id: str,
        permissions: List[AnalyticsPermission]
    ) -> bool:
        """Check if user has all specified permissions"""
        for permission in permissions:
            if not self.has_permission(user_id, permission):
                return False
        return True

    def get_user_permissions(self, user_id: str) -> List[AnalyticsPermission]:
        """Get all permissions for a user"""
        permissions = set()
        user_roles = self.user_roles.get(user_id, [])
        
        for role in user_roles:
            permissions.update(self.ROLE_PERMISSIONS.get(role, []))
        
        return list(permissions)

    def assign_role(self, user_id: str, role: AnalyticsRole) -> None:
        """Assign a role to a user"""
        if user_id not in self.user_roles:
            self.user_roles[user_id] = []
        
        if role not in self.user_roles[user_id]:
            self.user_roles[user_id].append(role)
            logger.info(f"Assigned role {role} to user {user_id}")

    def remove_role(self, user_id: str, role: AnalyticsRole) -> None:
        """Remove a role from a user"""
        if user_id in self.user_roles and role in self.user_roles[user_id]:
            self.user_roles[user_id].remove(role)
            logger.info(f"Removed role {role} from user {user_id}")

    def get_user_roles(self, user_id: str) -> List[AnalyticsRole]:
        """Get all roles for a user"""
        return self.user_roles.get(user_id, [])

    def can_view_location(self, user_id: str, location_id: str, user_location_id: str = None) -> bool:
        """Check if user can view analytics for a location"""
        # Admins and managers can view all locations
        if self.has_permission(user_id, AnalyticsPermission.VIEW_LOCATION_ANALYTICS):
            return True
        
        # Staff can only view their own location
        if user_location_id:
            return location_id == user_location_id
        
        return False

    def can_view_staff_analytics(self, user_id: str, staff_id: str, user_staff_id: str = None) -> bool:
        """Check if user can view analytics for a staff member"""
        # Admins and managers can view all staff
        if self.has_permission(user_id, AnalyticsPermission.VIEW_STAFF_ANALYTICS):
            return True
        
        # Staff can only view their own analytics
        if user_staff_id:
            return staff_id == user_staff_id
        
        return False

    def filter_data_by_role(
        self,
        user_id: str,
        data: List[Dict[str, Any]],
        location_field: str = "location_id",
        staff_field: str = "staff_id",
        user_location_id: str = None,
        user_staff_id: str = None
    ) -> List[Dict[str, Any]]:
        """Filter data based on user's role and permissions"""
        filtered_data = []
        
        for item in data:
            # Check location access
            if location_field in item:
                if not self.can_view_location(user_id, item[location_field], user_location_id):
                    continue
            
            # Check staff access
            if staff_field in item:
                if not self.can_view_staff_analytics(user_id, item[staff_field], user_staff_id):
                    continue
            
            filtered_data.append(item)
        
        return filtered_data

    def get_role_description(self, role: AnalyticsRole) -> str:
        """Get description of a role"""
        descriptions = {
            AnalyticsRole.ADMIN: "Full access to all analytics features",
            AnalyticsRole.MANAGER: "Access to all analytics and management features",
            AnalyticsRole.STAFF: "Access to basic analytics and client data",
            AnalyticsRole.VIEWER: "Read-only access to basic analytics",
        }
        return descriptions.get(role, "Unknown role")


# Global RBAC service instance
rbac_service = RBACService()
