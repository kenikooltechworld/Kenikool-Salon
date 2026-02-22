import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from bson import ObjectId
from pymongo import ASCENDING
from app.database import db


class TemplateService:
    """Service for managing campaign templates"""

    def __init__(self):
        self.collection = db.campaign_templates
        self._ensure_indexes()

    def _ensure_indexes(self):
        """Create necessary indexes"""
        self.collection.create_index([("tenant_id", ASCENDING)])
        self.collection.create_index([("category", ASCENDING)])
        self.collection.create_index([("is_system", ASCENDING)])
        self.collection.create_index([("created_at", ASCENDING)])

    async def create_template(
        self,
        tenant_id: str,
        name: str,
        category: str,
        channels: List[str],
        message_templates: Dict[str, str],
        variables: List[str],
        email_subject: Optional[str] = None,
        description: Optional[str] = None,
        created_by: str = "system",
        is_system: bool = False
    ) -> Dict[str, Any]:
        """Create a new campaign template"""
        template = {
            "tenant_id": tenant_id,
            "name": name,
            "category": category,
            "channels": channels,
            "message_templates": message_templates,
            "email_subject": email_subject,
            "variables": variables,
            "description": description,
            "is_system": is_system,
            "created_by": created_by,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await self.collection.insert_one(template)
        template["_id"] = result.inserted_id
        return template

    async def get_template(self, template_id: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Get a template by ID"""
        try:
            template = await self.collection.find_one({
                "_id": ObjectId(template_id),
                "tenant_id": tenant_id
            })
            return template
        except:
            return None

    async def get_templates(
        self,
        tenant_id: str,
        category: Optional[str] = None,
        offset: int = 0,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get templates with optional filtering"""
        query = {"tenant_id": tenant_id}
        if category:
            query["category"] = category
        
        templates = await self.collection.find(query).skip(offset).limit(limit).to_list(None)
        return templates

    async def get_categories(self, tenant_id: str) -> List[str]:
        """Get all template categories"""
        categories = await self.collection.distinct("category", {"tenant_id": tenant_id})
        return sorted(categories)

    async def update_template(
        self,
        template_id: str,
        tenant_id: str,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Update a template"""
        try:
            kwargs["updated_at"] = datetime.utcnow()
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(template_id), "tenant_id": tenant_id},
                {"$set": kwargs},
                return_document=True
            )
            return result
        except:
            return None

    async def delete_template(self, template_id: str, tenant_id: str) -> bool:
        """Delete a template (only custom templates)"""
        try:
            template = await self.get_template(template_id, tenant_id)
            if template and template.get("is_system"):
                return False  # Cannot delete system templates
            
            result = await self.collection.delete_one({
                "_id": ObjectId(template_id),
                "tenant_id": tenant_id
            })
            return result.deleted_count > 0
        except:
            return False

    def extract_variables(self, content: str) -> List[str]:
        """Extract personalization variables from template content"""
        pattern = r'\{\{(\w+)\}\}'
        variables = re.findall(pattern, content)
        return list(set(variables))

    def render_template(self, content: str, variables: Dict[str, str]) -> str:
        """Render template with variable substitution"""
        result = content
        for key, value in variables.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))
        return result

    async def seed_system_templates(self, tenant_id: str) -> None:
        """Seed system templates for a tenant"""
        system_templates = [
            {
                "name": "Birthday Special",
                "category": "birthday",
                "channels": ["sms", "email"],
                "message_templates": {
                    "sms": "Happy Birthday {{client_name}}! Enjoy {{discount_percentage}}% off your next visit. Use code: {{promo_code}}",
                    "email": "Special Birthday Offer for {{client_name}}"
                },
                "email_subject": "Happy Birthday! {{discount_percentage}}% Off",
                "variables": ["client_name", "discount_percentage", "promo_code"],
                "description": "Birthday greeting with discount offer"
            },
            {
                "name": "Win-Back Campaign",
                "category": "retention",
                "channels": ["sms", "email"],
                "message_templates": {
                    "sms": "We miss you {{client_name}}! Come back and get {{discount_percentage}}% off. {{booking_link}}",
                    "email": "We Miss You! {{discount_percentage}}% Off Your Next Visit"
                },
                "email_subject": "We Miss You - {{discount_percentage}}% Off",
                "variables": ["client_name", "discount_percentage", "booking_link"],
                "description": "Re-engagement campaign for inactive clients"
            },
            {
                "name": "Post-Visit Follow-up",
                "category": "retention",
                "channels": ["sms", "email"],
                "message_templates": {
                    "sms": "Thanks for visiting {{salon_name}}, {{client_name}}! How was your experience? {{feedback_link}}",
                    "email": "Thank You for Your Visit to {{salon_name}}"
                },
                "email_subject": "Thank You for Your Visit",
                "variables": ["client_name", "salon_name", "feedback_link"],
                "description": "Post-visit feedback and follow-up"
            },
            {
                "name": "Seasonal Promotion",
                "category": "seasonal",
                "channels": ["sms", "email"],
                "message_templates": {
                    "sms": "{{season}} Special! {{discount_percentage}}% off {{service_name}}. Book now: {{booking_link}}",
                    "email": "{{season}} Special Offer - {{discount_percentage}}% Off"
                },
                "email_subject": "{{season}} Special - {{discount_percentage}}% Off",
                "variables": ["season", "discount_percentage", "service_name", "booking_link"],
                "description": "Seasonal promotional campaign"
            },
            {
                "name": "New Service Launch",
                "category": "promotional",
                "channels": ["sms", "email"],
                "message_templates": {
                    "sms": "New! {{service_name}} now available at {{salon_name}}. Book your appointment: {{booking_link}}",
                    "email": "Introducing {{service_name}} - Exclusive Offer Inside"
                },
                "email_subject": "New Service: {{service_name}}",
                "variables": ["service_name", "salon_name", "booking_link"],
                "description": "Announce new services to clients"
            },
            {
                "name": "Loyalty Reward",
                "category": "promotional",
                "channels": ["sms", "email"],
                "message_templates": {
                    "sms": "{{client_name}}, you've earned {{reward_points}} loyalty points! Redeem now: {{reward_link}}",
                    "email": "You've Earned {{reward_points}} Loyalty Points!"
                },
                "email_subject": "Loyalty Reward - {{reward_points}} Points",
                "variables": ["client_name", "reward_points", "reward_link"],
                "description": "Loyalty program rewards notification"
            }
        ]

        for template_data in system_templates:
            existing = await self.collection.find_one({
                "tenant_id": tenant_id,
                "name": template_data["name"],
                "is_system": True
            })
            if not existing:
                await self.create_template(
                    tenant_id=tenant_id,
                    is_system=True,
                    created_by="system",
                    **template_data
                )


# Singleton instance
template_service = TemplateService()