"""
Service Template Service - Business logic for service templates
"""
from bson import ObjectId
from datetime import datetime
from typing import Dict, List, Optional
import logging

from app.database import Database
from app.api.exceptions import NotFoundException

logger = logging.getLogger(__name__)


class ServiceTemplateService:
    """Service for managing service templates"""
    
    @staticmethod
    def create_template(
        tenant_id: str,
        name: str,
        template_data: Dict,
        description: Optional[str] = None,
        category: Optional[str] = None,
        is_default: bool = False
    ) -> Dict:
        """
        Create a new service template
        
        Requirements: 12.4, 12.5
        """
        db = Database.get_db()
        
        template_doc = {
            "tenant_id": tenant_id,
            "name": name,
            "description": description,
            "category": category,
            "is_default": is_default,
            "is_active": True,
            "template_data": template_data,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.service_templates.insert_one(template_doc)
        template_id = str(result.inserted_id)
        
        logger.info(f"Service template created: {template_id} for tenant: {tenant_id}")
        
        # Fetch created template
        template = db.service_templates.find_one({"_id": ObjectId(template_id)})
        return ServiceTemplateService._format_template_response(template)
    
    @staticmethod
    def get_templates(
        tenant_id: str,
        is_active: Optional[bool] = None,
        category: Optional[str] = None,
        include_defaults: bool = True
    ) -> List[Dict]:
        """
        Get templates for tenant
        
        Requirements: 12.6
        """
        db = Database.get_db()
        
        # Build query - include tenant templates and default templates
        query = {
            "$or": [
                {"tenant_id": tenant_id},
                {"is_default": True} if include_defaults else {}
            ]
        }
        
        if is_active is not None:
            query["is_active"] = is_active
        if category is not None:
            query["category"] = category
        
        templates = list(db.service_templates.find(query))
        return [ServiceTemplateService._format_template_response(t) for t in templates]
    
    @staticmethod
    def get_template(template_id: str, tenant_id: str) -> Dict:
        """
        Get single template by ID
        
        Requirements: 12.6
        """
        db = Database.get_db()
        
        template = db.service_templates.find_one({
            "_id": ObjectId(template_id),
            "$or": [
                {"tenant_id": tenant_id},
                {"is_default": True}
            ]
        })
        
        if template is None:
            raise NotFoundException("Template not found")
        
        return ServiceTemplateService._format_template_response(template)
    
    @staticmethod
    def update_template(
        template_id: str,
        tenant_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
        is_active: Optional[bool] = None,
        template_data: Optional[Dict] = None
    ) -> Dict:
        """
        Update a template
        
        Requirements: 12.5
        """
        db = Database.get_db()
        
        # Check template exists and belongs to tenant (can't update default templates)
        template = db.service_templates.find_one({
            "_id": ObjectId(template_id),
            "tenant_id": tenant_id,
            "is_default": False
        })
        
        if template is None:
            raise NotFoundException("Template not found or cannot be modified")
        
        # Build update data
        update_data = {"updated_at": datetime.utcnow()}
        
        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        if category is not None:
            update_data["category"] = category
        if is_active is not None:
            update_data["is_active"] = is_active
        if template_data is not None:
            update_data["template_data"] = template_data
        
        # Update template
        db.service_templates.update_one(
            {"_id": ObjectId(template_id)},
            {"$set": update_data}
        )
        
        logger.info(f"Template updated: {template_id}")
        
        # Fetch updated template
        template = db.service_templates.find_one({"_id": ObjectId(template_id)})
        return ServiceTemplateService._format_template_response(template)
    
    @staticmethod
    def delete_template(template_id: str, tenant_id: str) -> bool:
        """
        Delete a template (soft delete)
        
        Requirements: 12.5
        """
        db = Database.get_db()
        
        # Check template exists and belongs to tenant (can't delete default templates)
        template = db.service_templates.find_one({
            "_id": ObjectId(template_id),
            "tenant_id": tenant_id,
            "is_default": False
        })
        
        if template is None:
            raise NotFoundException("Template not found or cannot be deleted")
        
        # Soft delete
        db.service_templates.update_one(
            {"_id": ObjectId(template_id)},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )
        
        logger.info(f"Template deleted (soft): {template_id}")
        return True
    
    @staticmethod
    def create_default_templates(tenant_id: str) -> List[Dict]:
        """
        Create default service templates
        
        Requirements: 12.6
        """
        db = Database.get_db()
        
        default_templates = [
            {
                "name": "Basic Haircut",
                "description": "Standard haircut service template",
                "category": "Hair",
                "template_data": {
                    "price": 5000,
                    "duration_minutes": 30,
                    "description": "Professional haircut service",
                    "booking_rules": {
                        "buffer_time_before": 5,
                        "buffer_time_after": 5,
                        "advance_booking_min": 0,
                        "advance_booking_max": 30,
                        "cancellation_deadline": 24
                    }
                }
            },
            {
                "name": "Manicure Service",
                "description": "Standard manicure service template",
                "category": "Nails",
                "template_data": {
                    "price": 3000,
                    "duration_minutes": 45,
                    "description": "Professional manicure service",
                    "booking_rules": {
                        "buffer_time_before": 10,
                        "buffer_time_after": 10,
                        "advance_booking_min": 0,
                        "advance_booking_max": 14,
                        "cancellation_deadline": 12
                    }
                }
            },
            {
                "name": "Makeup Application",
                "description": "Standard makeup service template",
                "category": "Makeup",
                "template_data": {
                    "price": 8000,
                    "duration_minutes": 60,
                    "description": "Professional makeup application",
                    "booking_rules": {
                        "buffer_time_before": 15,
                        "buffer_time_after": 15,
                        "advance_booking_min": 1,
                        "advance_booking_max": 30,
                        "cancellation_deadline": 48
                    }
                }
            },
            {
                "name": "Spa Treatment",
                "description": "Standard spa treatment template",
                "category": "Spa",
                "template_data": {
                    "price": 15000,
                    "duration_minutes": 90,
                    "description": "Relaxing spa treatment",
                    "booking_rules": {
                        "buffer_time_before": 15,
                        "buffer_time_after": 15,
                        "advance_booking_min": 1,
                        "advance_booking_max": 30,
                        "cancellation_deadline": 48
                    }
                }
            }
        ]
        
        created_templates = []
        for template_data in default_templates:
            # Check if default template already exists
            existing = db.service_templates.find_one({
                "name": template_data["name"],
                "is_default": True
            })
            
            if not existing:
                template = ServiceTemplateService.create_template(
                    tenant_id="system",  # System-wide default
                    name=template_data["name"],
                    description=template_data["description"],
                    category=template_data["category"],
                    template_data=template_data["template_data"],
                    is_default=True
                )
                created_templates.append(template)
        
        return created_templates
    
    @staticmethod
    def _format_template_response(template_doc: Dict) -> Dict:
        """Format template document for response"""
        return {
            "id": str(template_doc["_id"]),
            "tenant_id": template_doc["tenant_id"],
            "name": template_doc["name"],
            "description": template_doc.get("description"),
            "category": template_doc.get("category"),
            "is_default": template_doc.get("is_default", False),
            "is_active": template_doc.get("is_active", True),
            "template_data": template_doc.get("template_data", {}),
            "created_at": template_doc.get("created_at", datetime.utcnow()),
            "updated_at": template_doc.get("updated_at", datetime.utcnow())
        }


# Singleton instance
service_template_service = ServiceTemplateService()
