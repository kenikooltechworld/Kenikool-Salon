"""
Staff Role Management Service - Handles role assignment and permission enforcement
"""
from typing import Dict, List, Optional, Set
from bson import ObjectId
from datetime import datetime
import logging

from app.database import Database
from app.api.exceptions import NotFoundException, BadRequestException, ForbiddenException

logger = logging.getLogger(__name__)


class StaffRoleService:
    """Service for managing staff roles and permissions"""

    # Define permission sets for each role
    ROLE_PERMISSIONS = {
        "owner": {
            "staff.view_all",
            "staff.create",
            "staff.edit_all",
            "staff.delete",
            "staff.view_payroll",
            "staff.edit_payroll",
            "staff.view_performance",
            "staff.edit_performance",
            "staff.view_commissions",
            "staff.edit_commissions",
            "staff.manage_roles",
            "staff.create_user_account",
            "staff.view_documents",
            "staff.manage_documents",
            "staff.view_emergency_contacts",
            "staff.manage_emergency_contacts",
            "staff.view_attendance",
            "staff.edit_attendance",
            "staff.manage_schedules",
            "staff.approve_time_off",
            "staff.approve_shift_swaps",
            "staff.send_announcements",
            "staff.view_all_messages",
            "staff.manage_training",
            "staff.manage_certifications",
            "staff.manage_onboarding",
            "staff.view_referrals",
            "staff.manage_referrals",
            "staff.bulk_operations",
            "reports.view_all",
            "reports.export",
        },
        "manager": {
            "staff.view_all",
            "staff.create",
            "staff.edit_all",
            "staff.view_performance",
            "staff.edit_performance",
            "staff.view_commissions",
            "staff.view_attendance",
            "staff.edit_attendance",
            "staff.manage_schedules",
            "staff.approve_time_off",
            "staff.approve_shift_swaps",
            "staff.send_announcements",
            "staff.view_all_messages",
            "staff.send_messages",
            "staff.manage_training",
            "staff.manage_certifications",
            "staff.manage_onboarding",
            "staff.view_documents",
            "staff.manage_documents",
            "staff.view_emergency_contacts",
            "staff.view_referrals",
            "reports.view_team",
            "reports.export",
        },
        "stylist": {
            "staff.view_own",
            "staff.edit_own",
            "staff.view_own_performance",
            "staff.view_own_commissions",
            "staff.view_own_attendance",
            "staff.request_time_off",
            "staff.request_shift_swap",
            "staff.view_own_schedule",
            "staff.view_messages",
            "staff.send_messages",
            "staff.view_own_documents",
            "staff.update_own_emergency_contacts",
            "staff.view_own_training",
            "staff.view_own_certifications",
            "staff.view_own_referrals",
            "reports.view_own",
        },
        "receptionist": {
            "staff.view_all",
            "staff.view_performance",
            "staff.view_attendance",
            "staff.view_schedules",
            "staff.view_messages",
            "staff.send_messages",
            "staff.view_documents",
            "reports.view_team",
        },
    }

    @staticmethod
    def get_role_permissions(role: str) -> Set[str]:
        """Get all permissions for a given role"""
        return StaffRoleService.ROLE_PERMISSIONS.get(role, set())

    @staticmethod
    def has_permission(user_role: str, permission: str) -> bool:
        """Check if a role has a specific permission"""
        permissions = StaffRoleService.get_role_permissions(user_role)
        return permission in permissions

    @staticmethod
    def check_permission(user_role: str, permission: str) -> None:
        """Raise exception if user doesn't have permission"""
        if not StaffRoleService.has_permission(user_role, permission):
            raise ForbiddenException(f"Permission denied: {permission}")

    @staticmethod
    def update_staff_role(
        tenant_id: str,
        staff_id: str,
        new_role: str,
        updated_by: str
    ) -> Dict:
        """Update a staff member's role"""
        db = Database.get_db()

        # Validate role
        if new_role not in StaffRoleService.ROLE_PERMISSIONS:
            raise BadRequestException(f"Invalid role: {new_role}")

        # Get staff member
        staff = db.stylists.find_one({
            "_id": ObjectId(staff_id),
            "tenant_id": tenant_id
        })

        if not staff:
            raise NotFoundException("Staff member not found")

        # Update role
        db.stylists.update_one(
            {"_id": ObjectId(staff_id)},
            {
                "$set": {
                    "role": new_role,
                    "updated_at": datetime.utcnow()
                }
            }
        )

        # Log role change
        db.staff_role_audit_log.insert_one({
            "tenant_id": tenant_id,
            "staff_id": staff_id,
            "staff_name": staff.get("name"),
            "old_role": staff.get("role"),
            "new_role": new_role,
            "changed_by": updated_by,
            "changed_at": datetime.utcnow()
        })

        updated_staff = db.stylists.find_one({"_id": ObjectId(staff_id)})
        return updated_staff

    @staticmethod
    def create_user_account(
        tenant_id: str,
        staff_id: str,
        email: str,
        password: str,
        role: str
    ) -> Dict:
        """Create a user account linked to a staff profile"""
        db = Database.get_db()

        # Get staff member
        staff = db.stylists.find_one({
            "_id": ObjectId(staff_id),
            "tenant_id": tenant_id
        })

        if not staff:
            raise NotFoundException("Staff member not found")

        # Check if user already exists
        existing_user = db.users.find_one({"email": email})
        if existing_user:
            raise BadRequestException("Email already in use")

        # Create user account
        from app.utils.security import hash_password

        user = {
            "tenant_id": tenant_id,
            "email": email,
            "password_hash": hash_password(password),
            "full_name": staff.get("name"),
            "role": role,
            "is_active": True,
            "staff_id": ObjectId(staff_id),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        result = db.users.insert_one(user)
        user_id = result.inserted_id

        # Link user to staff
        db.stylists.update_one(
            {"_id": ObjectId(staff_id)},
            {
                "$set": {
                    "user_id": user_id,
                    "role": role,
                    "updated_at": datetime.utcnow()
                }
            }
        )

        user["_id"] = user_id
        return {
            "user_id": str(user_id),
            "email": email,
            "full_name": user["full_name"],
            "role": role,
            "staff_id": staff_id
        }

    @staticmethod
    def get_staff_permissions(tenant_id: str, staff_id: str) -> Dict:
        """Get all permissions for a staff member"""
        db = Database.get_db()

        staff = db.stylists.find_one({
            "_id": ObjectId(staff_id),
            "tenant_id": tenant_id
        })

        if not staff:
            raise NotFoundException("Staff member not found")

        role = staff.get("role", "stylist")
        permissions = StaffRoleService.get_role_permissions(role)

        return {
            "staff_id": staff_id,
            "role": role,
            "permissions": list(permissions)
        }

    @staticmethod
    def get_available_roles() -> List[Dict]:
        """Get all available roles with their permissions"""
        roles = []
        for role, permissions in StaffRoleService.ROLE_PERMISSIONS.items():
            roles.append({
                "role": role,
                "permissions": list(permissions),
                "permission_count": len(permissions)
            })
        return roles

    @staticmethod
    def can_access_staff_data(
        user_role: str,
        user_staff_id: Optional[str],
        target_staff_id: str
    ) -> bool:
        """Check if user can access another staff member's data"""
        # Owner and Manager can access all staff data
        if user_role in ["owner", "manager"]:
            return True

        # Stylist can only access their own data
        if user_role == "stylist":
            return user_staff_id == target_staff_id

        # Receptionist cannot access individual staff data
        return False

    @staticmethod
    def can_edit_staff_data(
        user_role: str,
        user_staff_id: Optional[str],
        target_staff_id: str
    ) -> bool:
        """Check if user can edit another staff member's data"""
        # Owner and Manager can edit all staff data
        if user_role in ["owner", "manager"]:
            return True

        # Stylist can only edit their own data
        if user_role == "stylist":
            return user_staff_id == target_staff_id

        # Receptionist cannot edit staff data
        return False

    @staticmethod
    def can_view_payroll(
        user_role: str,
        user_staff_id: Optional[str],
        target_staff_id: str
    ) -> bool:
        """Check if user can view payroll data"""
        # Only owner can view payroll
        if user_role == "owner":
            return True

        # Stylist can view their own payroll
        if user_role == "stylist":
            return user_staff_id == target_staff_id

        return False

    @staticmethod
    def can_manage_roles(user_role: str) -> bool:
        """Check if user can manage staff roles"""
        return user_role == "owner"

    @staticmethod
    def get_dashboard_data_for_role(
        user_role: str,
        user_staff_id: Optional[str],
        tenant_id: str
    ) -> Dict:
        """Get dashboard data appropriate for user's role"""
        db = Database.get_db()

        if user_role == "owner":
            # Owner sees all staff and metrics
            return {
                "view_type": "all_staff",
                "can_manage_roles": True,
                "can_view_payroll": True,
                "can_manage_schedules": True,
                "can_approve_requests": True
            }

        elif user_role == "manager":
            # Manager sees all staff but not payroll
            return {
                "view_type": "all_staff",
                "can_manage_roles": False,
                "can_view_payroll": False,
                "can_manage_schedules": True,
                "can_approve_requests": True
            }

        elif user_role == "stylist":
            # Stylist sees only their own data
            return {
                "view_type": "own_data",
                "can_manage_roles": False,
                "can_view_payroll": True,
                "can_manage_schedules": False,
                "can_approve_requests": False,
                "staff_id": user_staff_id
            }

        elif user_role == "receptionist":
            # Receptionist sees team data but limited
            return {
                "view_type": "team_data",
                "can_manage_roles": False,
                "can_view_payroll": False,
                "can_manage_schedules": False,
                "can_approve_requests": False
            }

        return {}

    @staticmethod
    def get_role_audit_log(
        tenant_id: str,
        staff_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """Get audit log of role changes"""
        db = Database.get_db()

        query = {"tenant_id": tenant_id}
        if staff_id:
            query["staff_id"] = staff_id

        logs = list(db.staff_role_audit_log.find(query)
                   .sort("changed_at", -1)
                   .limit(limit))

        return logs


# Singleton instance
staff_role_service = StaffRoleService()
