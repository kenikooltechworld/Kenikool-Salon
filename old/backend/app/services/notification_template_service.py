"""
Notification Template Service - Manages notification templates for waitlist system
"""
from typing import Dict, List, Optional
from datetime import datetime
from bson import ObjectId
import logging

from app.database import Database
from app.api.exceptions import NotFoundException, ConflictException

logger = logging.getLogger(__name__)


class NotificationTemplateService:
    """Service for managing notification templates"""
    
    # Required variables that must be present in templates
    REQUIRED_VARIABLES = {"client_name", "salon_name", "service_name", "salon_phone"}
    
    @staticmethod
    def _get_db():
        """Get database instance"""
        return Database.get_db()
    
    @staticmethod
    def create_notification_template(
        tenant_id: str,
        name: str,
        message: str,
        variables: Optional[List[str]] = None,
        is_default: bool = False
    ) -> Dict:
        """
        Create a notification template.
        
        Args:
            tenant_id: Tenant ID
            name: Template name
            message: Template message with variable placeholders
            variables: List of variable names used in template
            is_default: Whether this is the default template
            
        Returns:
            Created template
            
        Requirements: 12.1, 12.4
        """
        db = NotificationTemplateService._get_db()
        
        # Validate template
        NotificationTemplateService._validate_template(message, variables or [])
        
        # Check if template name already exists for this tenant
        existing = db.notification_templates.find_one({
            "tenant_id": tenant_id,
            "name": name
        })
        
        if existing:
            raise ConflictException(f"Template with name '{name}' already exists")
        
        # If this is being set as default, unset other defaults
        if is_default:
            db.notification_templates.update_many(
                {"tenant_id": tenant_id, "is_default": True},
                {"$set": {"is_default": False}}
            )
        
        template = {
            "tenant_id": tenant_id,
            "name": name,
            "message": message,
            "variables": variables or [],
            "is_default": is_default,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.notification_templates.insert_one(template)
        template["_id"] = str(result.inserted_id)
        
        logger.info(f"Created notification template '{name}' for tenant {tenant_id}")
        
        return template
    
    @staticmethod
    def get_notification_templates(
        tenant_id: str,
        is_default_only: bool = False
    ) -> List[Dict]:
        """
        Get notification templates for a tenant.
        
        Args:
            tenant_id: Tenant ID
            is_default_only: Only return default template
            
        Returns:
            List of templates
            
        Requirements: 12.1
        """
        db = NotificationTemplateService._get_db()
        
        query = {"tenant_id": tenant_id}
        
        if is_default_only:
            query["is_default"] = True
        
        templates = list(
            db.notification_templates.find(query).sort("created_at", -1)
        )
        
        return [
            {
                **t,
                "_id": str(t["_id"]),
                "created_at": t["created_at"].isoformat(),
                "updated_at": t["updated_at"].isoformat()
            }
            for t in templates
        ]
    
    @staticmethod
    def get_notification_template(
        template_id: str,
        tenant_id: str
    ) -> Dict:
        """
        Get a specific notification template.
        
        Args:
            template_id: Template ID
            tenant_id: Tenant ID
            
        Returns:
            Template
            
        Raises:
            NotFoundException: If template not found
        """
        db = NotificationTemplateService._get_db()
        
        template = db.notification_templates.find_one({
            "_id": ObjectId(template_id),
            "tenant_id": tenant_id
        })
        
        if not template:
            raise NotFoundException("Notification template not found")
        
        template["_id"] = str(template["_id"])
        template["created_at"] = template["created_at"].isoformat()
        template["updated_at"] = template["updated_at"].isoformat()
        
        return template
    
    @staticmethod
    def update_notification_template(
        template_id: str,
        tenant_id: str,
        name: Optional[str] = None,
        message: Optional[str] = None,
        variables: Optional[List[str]] = None,
        is_default: Optional[bool] = None
    ) -> Dict:
        """
        Update a notification template.
        
        Args:
            template_id: Template ID
            tenant_id: Tenant ID
            name: New template name
            message: New template message
            variables: New list of variables
            is_default: New default status
            
        Returns:
            Updated template
            
        Requirements: 12.1, 12.4
        """
        db = NotificationTemplateService._get_db()
        
        template = db.notification_templates.find_one({
            "_id": ObjectId(template_id),
            "tenant_id": tenant_id
        })
        
        if not template:
            raise NotFoundException("Notification template not found")
        
        # Validate template if message or variables are being updated
        if message is not None or variables is not None:
            msg = message if message is not None else template["message"]
            vars_list = variables if variables is not None else template["variables"]
            NotificationTemplateService._validate_template(msg, vars_list)
        
        # Check if new name conflicts with existing template
        if name is not None and name != template["name"]:
            existing = db.notification_templates.find_one({
                "tenant_id": tenant_id,
                "name": name,
                "_id": {"$ne": ObjectId(template_id)}
            })
            if existing:
                raise ConflictException(f"Template with name '{name}' already exists")
        
        # If this is being set as default, unset other defaults
        if is_default is True:
            db.notification_templates.update_many(
                {"tenant_id": tenant_id, "_id": {"$ne": ObjectId(template_id)}, "is_default": True},
                {"$set": {"is_default": False}}
            )
        
        # Build update data
        update_data = {"updated_at": datetime.utcnow()}
        
        if name is not None:
            update_data["name"] = name
        if message is not None:
            update_data["message"] = message
        if variables is not None:
            update_data["variables"] = variables
        if is_default is not None:
            update_data["is_default"] = is_default
        
        # Update template
        db.notification_templates.update_one(
            {"_id": ObjectId(template_id)},
            {"$set": update_data}
        )
        
        # Get updated template
        updated = db.notification_templates.find_one({"_id": ObjectId(template_id)})
        updated["_id"] = str(updated["_id"])
        updated["created_at"] = updated["created_at"].isoformat()
        updated["updated_at"] = updated["updated_at"].isoformat()
        
        logger.info(f"Updated notification template {template_id}")
        
        return updated
    
    @staticmethod
    def delete_notification_template(
        template_id: str,
        tenant_id: str
    ) -> Dict:
        """
        Delete a notification template.
        
        Args:
            template_id: Template ID
            tenant_id: Tenant ID
            
        Returns:
            Deleted template info
            
        Requirements: 12.1
        """
        db = NotificationTemplateService._get_db()
        
        template = db.notification_templates.find_one({
            "_id": ObjectId(template_id),
            "tenant_id": tenant_id
        })
        
        if not template:
            raise NotFoundException("Notification template not found")
        
        # Don't allow deleting the default template
        if template.get("is_default"):
            raise ConflictException("Cannot delete the default notification template")
        
        db.notification_templates.delete_one({"_id": ObjectId(template_id)})
        
        logger.info(f"Deleted notification template {template_id}")
        
        return {
            "id": str(template["_id"]),
            "name": template["name"],
            "deleted_at": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def _validate_template(message: str, variables: List[str]) -> None:
        """
        Validate that template contains required variables.
        
        Args:
            message: Template message
            variables: List of variables used in template
            
        Raises:
            ValueError: If template is invalid
            
        Requirements: 12.4
        """
        if not message:
            raise ValueError("Template message cannot be empty")
        
        # Check that all required variables are present in the message
        for required_var in NotificationTemplateService.REQUIRED_VARIABLES:
            placeholder = f"{{{required_var}}}"
            if placeholder not in message:
                raise ValueError(
                    f"Template must contain required variable: {placeholder}"
                )
        
        # Verify that variables list matches what's in the message
        # Extract all placeholders from message
        import re
        placeholders = re.findall(r'\{(\w+)\}', message)
        
        if set(placeholders) != set(variables):
            raise ValueError(
                f"Variables list must match placeholders in message. "
                f"Found: {set(placeholders)}, Expected: {set(variables)}"
            )


# Singleton instance
notification_template_service = NotificationTemplateService()
