"""
Booking template service - Business logic for booking templates
"""
from bson import ObjectId
from datetime import datetime
from typing import Dict, List, Optional
import logging

from app.database import Database
from app.api.exceptions import NotFoundException, BadRequestException

logger = logging.getLogger(__name__)


class BookingTemplateService:
    """Service for managing booking templates"""
    
    @staticmethod
    async def create_template(
        tenant_id: str,
        name: str,
        client_id: str,
        service_id: str,
        stylist_id: str,
        notes: Optional[str] = None,
        description: Optional[str] = None,
        duration: Optional[int] = None,
        pricing: Optional[float] = None,
        category: Optional[str] = None
    ) -> Dict:
        """
        Create a new booking template
        
        Args:
            tenant_id: Tenant ID
            name: Template name
            client_id: Client ID
            service_id: Service ID
            stylist_id: Stylist ID
            notes: Default notes
            
        Returns:
            Dict with created template data
        """
        db = Database.get_db()
        
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": ObjectId(tenant_id)
        })
        if not client:
            raise NotFoundException("Client not found")
        
        # Verify service exists
        service = db.services.find_one({
            "_id": ObjectId(service_id),
            "tenant_id": ObjectId(tenant_id)
        })
        if not service:
            raise NotFoundException("Service not found")
        
        # Verify stylist exists
        stylist = db.stylists.find_one({
            "_id": ObjectId(stylist_id),
            "tenant_id": ObjectId(tenant_id)
        })
        if not stylist:
            raise NotFoundException("Stylist not found")
        
        # Create template
        template_data = {
            "tenant_id": ObjectId(tenant_id),
            "name": name,
            "description": description or f"Template for {service.get('name', 'Unknown')} with {stylist.get('name', 'Unknown')}",
            "client_id": ObjectId(client_id),
            "client_name": client.get("name", "Unknown"),
            "service_id": ObjectId(service_id),
            "service_name": service.get("name", "Unknown"),
            "stylist_id": ObjectId(stylist_id),
            "stylist_name": stylist.get("name", "Unknown"),
            "services": [{
                "service_id": service_id,
                "service_name": service.get("name", "Unknown"),
                "variant_id": None,
                "add_ons": []
            }],
            "duration": duration or service.get("duration", 60),
            "pricing": pricing or service.get("price", 0.0),
            "category": category or "General",
            "notes": notes,
            "is_active": True,
            "usage_count": 0,
            "last_used_at": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        result = db.booking_templates.insert_one(template_data)
        template_id = str(result.inserted_id)
        
        logger.info(f"Booking template created: {template_id} for client: {client_id}")
        
        # Fetch created template
        template_doc = db.booking_templates.find_one({"_id": ObjectId(template_id)})
        return BookingTemplateService._format_template_response(template_doc)
    
    @staticmethod
    async def create_template_from_booking(
        booking_id: str,
        tenant_id: str,
        template_name: str
    ) -> Dict:
        """
        Create a template from an existing booking
        
        Args:
            booking_id: Booking ID to use as template
            tenant_id: Tenant ID
            template_name: Name for the template
            
        Returns:
            Dict with created template data
        """
        db = Database.get_db()
        
        # Get booking
        booking = db.bookings.find_one({
            "_id": ObjectId(booking_id),
            "tenant_id": ObjectId(tenant_id)
        })
        if not booking:
            raise NotFoundException("Booking not found")
        
        # Create template from booking
        return await BookingTemplateService.create_template(
            tenant_id=tenant_id,
            name=template_name,
            client_id=str(booking["client_id"]),
            service_id=str(booking["service_id"]),
            stylist_id=str(booking["stylist_id"]),
            notes=booking.get("notes")
        )
    
    @staticmethod
    async def get_templates(
        tenant_id: str,
        client_id: Optional[str] = None,
        is_active: Optional[bool] = None,
        offset: int = 0,
        limit: int = 50
    ) -> List[Dict]:
        """
        Get list of booking templates (including default templates)
        
        Args:
            tenant_id: Tenant ID
            client_id: Optional filter by client
            is_active: Optional filter by active status
            offset: Pagination offset
            limit: Pagination limit
            
        Returns:
            List of template dicts
        """
        db = Database.get_db()
        
        # Build query for tenant-specific templates
        tenant_query = {"tenant_id": ObjectId(tenant_id)}
        if client_id:
            tenant_query["client_id"] = ObjectId(client_id)
        if is_active is not None:
            tenant_query["is_active"] = is_active
        
        # Build query for default templates
        default_query = {"is_default": True}
        if is_active is not None:
            default_query["is_active"] = is_active
        
        # Get tenant-specific templates
        tenant_templates = list(
            db.booking_templates.find(tenant_query)
            .sort("last_used_at", -1)
        )
        
        # Get default templates
        default_templates = list(
            db.booking_templates.find(default_query)
            .sort("usage_count", -1)
        )
        
        # Combine and format templates
        all_templates = tenant_templates + default_templates
        
        # Apply pagination
        paginated_templates = all_templates[offset:offset + limit]
        
        return [BookingTemplateService._format_template_response(t) for t in paginated_templates]
    
    @staticmethod
    async def get_template(template_id: str, tenant_id: str) -> Dict:
        """
        Get single template by ID
        
        Args:
            template_id: Template ID
            tenant_id: Tenant ID
            
        Returns:
            Dict with template data
        """
        db = Database.get_db()
        
        template = db.booking_templates.find_one({
            "_id": ObjectId(template_id),
            "tenant_id": ObjectId(tenant_id)
        })
        
        if not template:
            raise NotFoundException("Template not found")
        
        return BookingTemplateService._format_template_response(template)
    
    @staticmethod
    async def update_template(
        template_id: str,
        tenant_id: str,
        updates: Dict
    ) -> Dict:
        """
        Update a booking template
        
        Args:
            template_id: Template ID
            tenant_id: Tenant ID
            updates: Dictionary of fields to update
            
        Returns:
            Dict with updated template data
        """
        db = Database.get_db()
        
        # Get existing template
        template = db.booking_templates.find_one({
            "_id": ObjectId(template_id),
            "tenant_id": ObjectId(tenant_id)
        })
        if not template:
            raise NotFoundException("Template not found")
        
        update_data = {"updated_at": datetime.now()}
        
        # Handle service change
        if "service_id" in updates and updates["service_id"]:
            service = db.services.find_one({
                "_id": ObjectId(updates["service_id"]),
                "tenant_id": ObjectId(tenant_id)
            })
            if not service:
                raise NotFoundException("Service not found")
            
            update_data["service_id"] = ObjectId(updates["service_id"])
            update_data["service_name"] = service.get("name")
        
        # Handle stylist change
        if "stylist_id" in updates and updates["stylist_id"]:
            stylist = db.stylists.find_one({
                "_id": ObjectId(updates["stylist_id"]),
                "tenant_id": ObjectId(tenant_id)
            })
            if not stylist:
                raise NotFoundException("Stylist not found")
            
            update_data["stylist_id"] = ObjectId(updates["stylist_id"])
            update_data["stylist_name"] = stylist.get("name")
        
        # Handle other fields
        for field in ["name", "notes", "is_active"]:
            if field in updates and updates[field] is not None:
                update_data[field] = updates[field]
        
        # Update template
        db.booking_templates.update_one(
            {"_id": ObjectId(template_id)},
            {"$set": update_data}
        )
        
        logger.info(f"Booking template updated: {template_id}")
        
        # Fetch updated template
        template_doc = db.booking_templates.find_one({"_id": ObjectId(template_id)})
        return BookingTemplateService._format_template_response(template_doc)
    
    @staticmethod
    async def delete_template(template_id: str, tenant_id: str) -> bool:
        """
        Delete a booking template
        
        Args:
            template_id: Template ID
            tenant_id: Tenant ID
            
        Returns:
            True if deleted
        """
        db = Database.get_db()
        
        result = db.booking_templates.delete_one({
            "_id": ObjectId(template_id),
            "tenant_id": ObjectId(tenant_id)
        })
        
        if result.deleted_count == 0:
            raise NotFoundException("Template not found")
        
        logger.info(f"Booking template deleted: {template_id}")
        return True
    
    @staticmethod
    async def create_booking_from_template(
        template_id: str,
        tenant_id: str,
        booking_date: datetime,
        override_notes: Optional[str] = None
    ) -> Dict:
        """
        Create a booking from a template
        
        Args:
            template_id: Template ID
            tenant_id: Tenant ID
            booking_date: Booking date/time
            override_notes: Optional notes to override template notes
            
        Returns:
            Dict with created booking data
        """
        db = Database.get_db()
        
        # Get template
        template = db.booking_templates.find_one({
            "_id": ObjectId(template_id),
            "tenant_id": ObjectId(tenant_id)
        })
        if not template:
            raise NotFoundException("Template not found")
        
        if not template.get("is_active"):
            raise BadRequestException("Template is not active")
        
        # Create booking using booking service
        from app.services.booking_service import booking_service
        
        # Get client details
        client = db.clients.find_one({"_id": template["client_id"]})
        if not client:
            raise NotFoundException("Client not found")
        
        booking = await booking_service.create_booking(
            tenant_id=tenant_id,
            client_name=client.get("name", "Unknown"),
            client_phone=client.get("phone", ""),
            service_id=str(template["service_id"]),
            stylist_id=str(template["stylist_id"]),
            booking_date=booking_date.isoformat(),
            client_email=client.get("email"),
            notes=override_notes if override_notes else template.get("notes")
        )
        
        # Update template usage stats
        db.booking_templates.update_one(
            {"_id": ObjectId(template_id)},
            {
                "$inc": {"usage_count": 1},
                "$set": {
                    "last_used_at": datetime.now(),
                    "updated_at": datetime.now()
                }
            }
        )
        
        logger.info(f"Booking created from template: {template_id}")
        
        return booking
    
    @staticmethod
    async def suggest_templates_for_client(
        client_id: str,
        tenant_id: str,
        limit: int = 5
    ) -> List[Dict]:
        """
        Suggest templates for a VIP client based on booking history
        
        Args:
            client_id: Client ID
            tenant_id: Tenant ID
            limit: Maximum number of suggestions
            
        Returns:
            List of suggested template dicts
        """
        db = Database.get_db()
        
        # Get client's most frequent service/stylist combinations
        pipeline = [
            {
                "$match": {
                    "tenant_id": ObjectId(tenant_id),
                    "client_id": ObjectId(client_id),
                    "status": "completed"
                }
            },
            {
                "$group": {
                    "_id": {
                        "service_id": "$service_id",
                        "stylist_id": "$stylist_id"
                    },
                    "count": {"$sum": 1},
                    "service_name": {"$first": "$service_name"},
                    "stylist_name": {"$first": "$stylist_name"}
                }
            },
            {
                "$sort": {"count": -1}
            },
            {
                "$limit": limit
            }
        ]
        
        frequent_combos = list(db.bookings.aggregate(pipeline))
        
        suggestions = []
        for combo in frequent_combos:
            # Check if template already exists
            existing = db.booking_templates.find_one({
                "tenant_id": ObjectId(tenant_id),
                "client_id": ObjectId(client_id),
                "service_id": combo["_id"]["service_id"],
                "stylist_id": combo["_id"]["stylist_id"]
            })
            
            if not existing:
                suggestions.append({
                    "service_id": str(combo["_id"]["service_id"]),
                    "service_name": combo["service_name"],
                    "stylist_id": str(combo["_id"]["stylist_id"]),
                    "stylist_name": combo["stylist_name"],
                    "booking_count": combo["count"],
                    "suggested_name": f"{combo['service_name']} with {combo['stylist_name']}"
                })
        
        return suggestions
    
    @staticmethod
    def _format_template_response(template_doc: Dict) -> Dict:
        """Format template document for response"""
        # Handle default templates that don't have tenant/client specific fields
        is_default = template_doc.get("is_default", False)
        
        return {
            "id": str(template_doc["_id"]),
            "tenant_id": str(template_doc["tenant_id"]) if template_doc.get("tenant_id") else None,
            "name": template_doc["name"],
            "description": template_doc.get("description", ""),
            "client_id": str(template_doc["client_id"]) if template_doc.get("client_id") else None,
            "client_name": template_doc.get("client_name", "Default Template") if not is_default else "Default Template",
            "service_id": str(template_doc["service_id"]) if template_doc.get("service_id") else None,
            "service_name": template_doc.get("service_name", "Service"),
            "stylist_id": str(template_doc["stylist_id"]) if template_doc.get("stylist_id") else None,
            "stylist_name": template_doc.get("stylist_name", "Any Stylist") if not is_default else "Any Stylist",
            "services": template_doc.get("services", [{
                "service_id": str(template_doc["service_id"]) if template_doc.get("service_id") else None,
                "service_name": template_doc.get("service_name", "Service"),
                "variant_id": template_doc.get("variant_id"),
                "add_ons": template_doc.get("add_ons", [])
            }]),
            "duration": template_doc.get("duration", 60),  # Default 60 minutes
            "pricing": template_doc.get("pricing", 0.0),
            "category": template_doc.get("category", "General"),
            "notes": template_doc.get("notes"),
            "is_active": template_doc.get("is_active", True),
            "is_default": is_default,
            "usage_count": template_doc.get("usage_count", 0),
            "last_used_at": template_doc.get("last_used_at"),
            "created_at": template_doc.get("created_at", datetime.now()),
            "updated_at": template_doc.get("updated_at", datetime.now())
        }


# Singleton instance
booking_template_service = BookingTemplateService()
