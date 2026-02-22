"""
Data Export Service - GDPR data export and management
"""
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from bson import ObjectId

from app.database import Database
from app.services.email_service import email_service
from app.utils.redis_cache import RedisCache

logger = logging.getLogger(__name__)


class DataExportException(Exception):
    """Base exception for data export operations"""
    pass


class BadRequestException(DataExportException):
    """Raised when request is invalid"""
    pass


class NotFoundException(DataExportException):
    """Raised when resource is not found"""
    pass


class DataExportService:
    """Service for GDPR data exports and management"""

    @staticmethod
    async def request_export(
        user_id: str,
        tenant_id: str,
        options: Dict,
        request_info: Dict
    ) -> str:
        """
        Request data export
        
        Requirements: 5.1, 5.5
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            options: Export options (include_bookings, include_clients, etc.)
            request_info: Request metadata
            
        Returns:
            Export ID
        """
        db = Database.get_db()
        
        # Create export record
        export_doc = {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "status": "pending",
            "file_url": None,
            "file_size": None,
            "options": options,
            "expires_at": datetime.utcnow() + timedelta(days=7),
            "requested_at": datetime.utcnow(),
            "completed_at": None
        }
        
        result = db.data_exports.insert_one(export_doc)
        export_id = str(result.inserted_id)
        
        # Log the export request (Requirement 5.5)
        try:
            from app.services.audit_log_service import audit_log_service
            await audit_log_service.log_event(
                user_id=user_id,
                tenant_id=tenant_id,
                event_type="data_export_requested",
                request_info=request_info,
                success=True,
                details={"export_id": export_id, "options": options}
            )
        except Exception as e:
            logger.error(f"Failed to log audit event: {str(e)}")
        
        logger.info(f"Data export requested: {export_id}")
        return export_id

    @staticmethod
    async def generate_export(export_id: str) -> bool:
        """
        Generate export file (background job)
        
        Requirements: 5.1, 5.2, 5.3, 5.4
        
        Args:
            export_id: Export ID
            
        Returns:
            True if export generated successfully
        """
        db = Database.get_db()
        
        # Get export record
        export_doc = db.data_exports.find_one({"_id": ObjectId(export_id)})
        if not export_doc:
            logger.error(f"Export not found: {export_id}")
            return False
        
        user_id = export_doc["user_id"]
        tenant_id = export_doc["tenant_id"]
        
        try:
            # Update status to processing
            db.data_exports.update_one(
                {"_id": ObjectId(export_id)},
                {"$set": {"status": "processing"}}
            )
            
            # Collect user data (Requirement 5.1, 5.2)
            export_data = await DataExportService._collect_user_data(
                user_id, tenant_id, export_doc.get("options", {})
            )
            
            # Generate JSON file
            json_content = json.dumps(export_data, indent=2, default=str)
            file_size = len(json_content.encode('utf-8'))
            
            # Upload to Cloudinary (simplified - in production use actual Cloudinary)
            # For now, we'll store the URL as a placeholder
            file_url = f"https://cdn.example.com/exports/{export_id}.json"
            
            # Update export record with completion info
            db.data_exports.update_one(
                {"_id": ObjectId(export_id)},
                {
                    "$set": {
                        "status": "completed",
                        "file_url": file_url,
                        "file_size": file_size,
                        "completed_at": datetime.utcnow()
                    }
                }
            )
            
            # Send email with download link (Requirement 5.3)
            user = db.users.find_one({"_id": ObjectId(user_id)})
            if user:
                try:
                    await email_service.send_data_export_ready(
                        to=user.get("email"),
                        user_name=user.get("full_name", "User"),
                        download_url=file_url,
                        expires_at=export_doc.get("expires_at")
                    )
                except Exception as e:
                    logger.error(f"Failed to send export email: {str(e)}")
            
            logger.info(f"Data export generated: {export_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate export: {str(e)}")
            
            # Update status to failed
            db.data_exports.update_one(
                {"_id": ObjectId(export_id)},
                {"$set": {"status": "failed"}}
            )
            
            return False

    @staticmethod
    async def _collect_user_data(
        user_id: str,
        tenant_id: str,
        options: Dict
    ) -> Dict:
        """
        Collect all user data for export
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            options: Export options
            
        Returns:
            Dict with all user data
        """
        db = Database.get_db()
        
        export_data = {
            "export_date": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "tenant_id": tenant_id
        }
        
        # Get user profile
        user = db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            # Remove sensitive fields
            user.pop("password_hash", None)
            user.pop("totp_secret", None)
            user.pop("backup_codes", None)
            user["_id"] = str(user["_id"])
            export_data["profile"] = user
        
        # Get bookings if requested
        if options.get("include_bookings", True):
            bookings = list(db.bookings.find(
                {"user_id": user_id, "tenant_id": tenant_id}
            ).limit(1000))
            for booking in bookings:
                booking["_id"] = str(booking["_id"])
            export_data["bookings"] = bookings
        
        # Get clients if requested
        if options.get("include_clients", True):
            clients = list(db.clients.find(
                {"tenant_id": tenant_id}
            ).limit(1000))
            for client in clients:
                client["_id"] = str(client["_id"])
            export_data["clients"] = clients
        
        # Get payments if requested
        if options.get("include_payments", True):
            payments = list(db.payments.find(
                {"tenant_id": tenant_id}
            ).limit(1000))
            for payment in payments:
                payment["_id"] = str(payment["_id"])
            export_data["payments"] = payments
        
        # Get settings if requested
        if options.get("include_settings", True):
            preferences = db.user_preferences.find_one(
                {"user_id": user_id, "tenant_id": tenant_id}
            )
            if preferences:
                preferences["_id"] = str(preferences["_id"])
                export_data["preferences"] = preferences
            
            privacy = db.privacy_settings.find_one(
                {"user_id": user_id, "tenant_id": tenant_id}
            )
            if privacy:
                privacy["_id"] = str(privacy["_id"])
                export_data["privacy_settings"] = privacy
        
        return export_data

    @staticmethod
    async def list_exports(user_id: str, tenant_id: str) -> List[Dict]:
        """
        List export history
        
        Requirements: 5.6
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            
        Returns:
            List of exports
        """
        db = Database.get_db()
        
        exports = list(db.data_exports.find({
            "user_id": user_id,
            "tenant_id": tenant_id
        }).sort("requested_at", -1).limit(50))
        
        # Convert to response format
        result = []
        for export in exports:
            result.append({
                "id": str(export["_id"]),
                "status": export["status"],
                "file_url": export.get("file_url"),
                "file_size": export.get("file_size"),
                "requested_at": export["requested_at"],
                "completed_at": export.get("completed_at"),
                "expires_at": export.get("expires_at")
            })
        
        return result

    @staticmethod
    async def get_export(
        user_id: str,
        tenant_id: str,
        export_id: str
    ) -> Dict:
        """
        Get export details
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            export_id: Export ID
            
        Returns:
            Export details
            
        Raises:
            NotFoundException: If export not found
        """
        db = Database.get_db()
        
        export_doc = db.data_exports.find_one({
            "_id": ObjectId(export_id),
            "user_id": user_id,
            "tenant_id": tenant_id
        })
        
        if not export_doc:
            raise NotFoundException("Export not found")
        
        return {
            "id": str(export_doc["_id"]),
            "status": export_doc["status"],
            "file_url": export_doc.get("file_url"),
            "file_size": export_doc.get("file_size"),
            "requested_at": export_doc["requested_at"],
            "completed_at": export_doc.get("completed_at"),
            "expires_at": export_doc.get("expires_at")
        }

    @staticmethod
    async def cleanup_expired_exports() -> int:
        """
        Delete expired exports (background job)
        
        Requirements: 5.4
        
        Returns:
            Number of exports deleted
        """
        db = Database.get_db()
        
        result = db.data_exports.delete_many({
            "expires_at": {"$lt": datetime.utcnow()},
            "status": "completed"
        })
        
        logger.info(f"Cleaned up {result.deleted_count} expired exports")
        return result.deleted_count


# Create singleton instance
data_export_service = DataExportService()
