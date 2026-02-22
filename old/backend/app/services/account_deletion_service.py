"""
Account Deletion Service - Account deletion workflow and management
"""
import logging
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional
from bson import ObjectId

from app.database import Database
from app.utils.security import verify_password
from app.services.email_service import email_service

logger = logging.getLogger(__name__)


class AccountDeletionException(Exception):
    """Base exception for account deletion operations"""
    pass


class UnauthorizedException(AccountDeletionException):
    """Raised when authentication fails"""
    pass


class BadRequestException(AccountDeletionException):
    """Raised when request is invalid"""
    pass


class NotFoundException(AccountDeletionException):
    """Raised when resource is not found"""
    pass


class AccountDeletionService:
    """Service for account deletion workflow"""

    @staticmethod
    async def request_deletion(
        user_id: str,
        tenant_id: str,
        password: str,
        request_info: Dict
    ) -> Dict:
        """
        Request account deletion with password confirmation
        
        Requirements: 6.1, 6.2, 6.3
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            password: Current password for confirmation
            request_info: Request metadata
            
        Returns:
            Deletion request details
            
        Raises:
            UnauthorizedException: If password is incorrect
            BadRequestException: If user is owner without transfer
        """
        db = Database.get_db()
        
        # Get user
        user = db.users.find_one({"_id": ObjectId(user_id), "tenant_id": tenant_id})
        if not user:
            raise NotFoundException("User not found")
        
        # Verify password (Requirement 6.1)
        if not verify_password(password, user.get("password_hash")):
            raise UnauthorizedException("Password is incorrect")
        
        # Check if user is owner (Requirement 6.7)
        if user.get("role") == "owner":
            # Check if ownership has been transferred
            other_owner = db.users.find_one({
                "tenant_id": tenant_id,
                "role": "owner",
                "_id": {"$ne": ObjectId(user_id)}
            })
            
            if not other_owner:
                raise BadRequestException(
                    "Cannot delete account as owner. Please transfer ownership to another user first."
                )
        
        # Generate cancellation token
        cancellation_token = secrets.token_urlsafe(32)
        
        # Create deletion record
        scheduled_for = datetime.utcnow() + timedelta(days=30)
        
        deletion_doc = {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "status": "pending",
            "scheduled_for": scheduled_for,
            "requested_at": datetime.utcnow(),
            "completed_at": None,
            "cancellation_token": cancellation_token
        }
        
        result = db.account_deletions.insert_one(deletion_doc)
        deletion_id = str(result.inserted_id)
        
        # Soft delete account (Requirement 6.3)
        db.users.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "account_deleted": True,
                    "account_deletion_scheduled_for": scheduled_for,
                    "account_deletion_id": deletion_id
                }
            }
        )
        
        # Send confirmation email (Requirement 6.6)
        try:
            await email_service.send_account_deletion_scheduled(
                to=user.get("email"),
                user_name=user.get("full_name", "User"),
                scheduled_for=scheduled_for,
                cancellation_url=f"https://app.example.com/cancel-deletion/{cancellation_token}"
            )
        except Exception as e:
            logger.error(f"Failed to send deletion confirmation email: {str(e)}")
        
        # Log security event
        try:
            from app.services.audit_log_service import audit_log_service
            await audit_log_service.log_event(
                user_id=user_id,
                tenant_id=tenant_id,
                event_type="account_deletion_requested",
                request_info=request_info,
                success=True,
                details={"scheduled_for": scheduled_for.isoformat()}
            )
        except Exception as e:
            logger.error(f"Failed to log audit event: {str(e)}")
        
        logger.info(f"Account deletion requested: {deletion_id}")
        
        return {
            "id": deletion_id,
            "status": "pending",
            "scheduled_for": scheduled_for,
            "requested_at": deletion_doc["requested_at"],
            "cancellation_token": cancellation_token
        }

    @staticmethod
    async def cancel_deletion(
        user_id: str,
        tenant_id: str,
        cancellation_token: str,
        request_info: Dict
    ) -> bool:
        """
        Cancel pending account deletion
        
        Requirements: 6.3
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            cancellation_token: Token to verify cancellation request
            request_info: Request metadata
            
        Returns:
            True if deletion cancelled
            
        Raises:
            NotFoundException: If deletion not found
            BadRequestException: If token is invalid
        """
        db = Database.get_db()
        
        # Find deletion record
        deletion = db.account_deletions.find_one({
            "user_id": user_id,
            "tenant_id": tenant_id,
            "status": "pending"
        })
        
        if not deletion:
            raise NotFoundException("No pending deletion found")
        
        # Verify cancellation token
        if deletion.get("cancellation_token") != cancellation_token:
            raise BadRequestException("Invalid cancellation token")
        
        # Update deletion status
        db.account_deletions.update_one(
            {"_id": deletion["_id"]},
            {"$set": {"status": "cancelled"}}
        )
        
        # Restore account
        db.users.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "account_deleted": False,
                    "account_deletion_scheduled_for": None,
                    "account_deletion_id": None
                }
            }
        )
        
        # Send confirmation email
        user = db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            try:
                await email_service.send_account_deletion_cancelled(
                    to=user.get("email"),
                    user_name=user.get("full_name", "User")
                )
            except Exception as e:
                logger.error(f"Failed to send cancellation email: {str(e)}")
        
        # Log security event
        try:
            from app.services.audit_log_service import audit_log_service
            await audit_log_service.log_event(
                user_id=user_id,
                tenant_id=tenant_id,
                event_type="account_deletion_cancelled",
                request_info=request_info,
                success=True
            )
        except Exception as e:
            logger.error(f"Failed to log audit event: {str(e)}")
        
        logger.info(f"Account deletion cancelled: {user_id}")
        return True

    @staticmethod
    async def get_deletion_status(
        user_id: str,
        tenant_id: str
    ) -> Optional[Dict]:
        """
        Get account deletion status
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            
        Returns:
            Deletion status or None if no pending deletion
        """
        db = Database.get_db()
        
        deletion = db.account_deletions.find_one({
            "user_id": user_id,
            "tenant_id": tenant_id,
            "status": "pending"
        })
        
        if not deletion:
            return None
        
        return {
            "id": str(deletion["_id"]),
            "status": deletion["status"],
            "scheduled_for": deletion["scheduled_for"],
            "requested_at": deletion["requested_at"]
        }

    @staticmethod
    async def execute_hard_delete(user_id: str, tenant_id: str) -> bool:
        """
        Execute hard delete for account (background job)
        
        Requirements: 6.5
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            
        Returns:
            True if deletion completed
        """
        db = Database.get_db()
        
        try:
            # Get deletion record
            deletion = db.account_deletions.find_one({
                "user_id": user_id,
                "tenant_id": tenant_id,
                "status": "pending"
            })
            
            if not deletion:
                logger.warning(f"No pending deletion found for user {user_id}")
                return False
            
            # Check if 30 days have passed
            if deletion["scheduled_for"] > datetime.utcnow():
                logger.info(f"Deletion not yet scheduled for user {user_id}")
                return False
            
            # Delete all user data across collections
            collections_to_clean = [
                "users",
                "sessions",
                "api_keys",
                "user_preferences",
                "privacy_settings",
                "security_logs",
                "data_exports",
                "bookings",
                "clients",
                "payments"
            ]
            
            for collection_name in collections_to_clean:
                try:
                    collection = db[collection_name]
                    collection.delete_many({
                        "user_id": user_id,
                        "tenant_id": tenant_id
                    })
                except Exception as e:
                    logger.error(f"Failed to delete from {collection_name}: {str(e)}")
            
            # Update deletion record
            db.account_deletions.update_one(
                {"_id": deletion["_id"]},
                {
                    "$set": {
                        "status": "completed",
                        "completed_at": datetime.utcnow()
                    }
                }
            )
            
            logger.info(f"Account hard deleted: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to execute hard delete: {str(e)}")
            return False

    @staticmethod
    async def cleanup_old_deletions() -> int:
        """
        Clean up old deletion records (background job)
        
        Returns:
            Number of records deleted
        """
        db = Database.get_db()
        
        # Delete completed deletions older than 90 days
        result = db.account_deletions.delete_many({
            "status": "completed",
            "completed_at": {"$lt": datetime.utcnow() - timedelta(days=90)}
        })
        
        logger.info(f"Cleaned up {result.deleted_count} old deletion records")
        return result.deleted_count

    @staticmethod
    async def check_soft_deleted_login(user_id: str, tenant_id: str) -> bool:
        """
        Check if account is soft-deleted and prevent login
        
        Requirements: 6.4
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            
        Returns:
            True if account is soft-deleted
        """
        db = Database.get_db()
        
        user = db.users.find_one({"_id": ObjectId(user_id), "tenant_id": tenant_id})
        if not user:
            return False
        
        return user.get("account_deleted", False)


# Create singleton instance
account_deletion_service = AccountDeletionService()
