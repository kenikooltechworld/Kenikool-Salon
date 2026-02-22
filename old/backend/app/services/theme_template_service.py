from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.theme_template import ThemeTemplate


class ThemeTemplateService:
    """Service for managing theme templates"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.theme_templates

    async def create_template(
        self,
        name: str,
        category: str,
        branding: Dict[str, Any],
        description: Optional[str] = None,
        preview_image_url: Optional[str] = None,
        tenant_id: Optional[str] = None,
        is_system: bool = False,
        is_premium: bool = False,
        created_by: Optional[str] = None,
    ) -> ThemeTemplate:
        """Create a new theme template"""
        
        # Validate category
        valid_categories = ["spa", "barber", "salon", "modern", "classic"]
        if category not in valid_categories:
            raise ValueError(f"Invalid category. Must be one of: {', '.join(valid_categories)}")
        
        # Validate branding configuration
        if not isinstance(branding, dict):
            raise ValueError("Branding must be a dictionary")
        
        template_dict = {
            "name": name,
            "category": category,
            "branding": branding,
            "description": description,
            "preview_image_url": preview_image_url,
            "tenant_id": tenant_id,
            "is_system": is_system,
            "is_premium": is_premium,
            "created_by": created_by,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        result = await self.collection.insert_one(template_dict)
        template_dict["_id"] = str(result.inserted_id)
        
        return ThemeTemplate(**template_dict)

    async def get_template(self, template_id: str) -> Optional[ThemeTemplate]:
        """Get a template by ID"""
        try:
            template = await self.collection.find_one({"_id": ObjectId(template_id)})
            if template:
                template["_id"] = str(template["_id"])
                return ThemeTemplate(**template)
        except Exception:
            pass
        return None

    async def get_templates(
        self,
        category: Optional[str] = None,
        tenant_id: Optional[str] = None,
        is_system: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ThemeTemplate]:
        """Get templates with optional filtering"""
        
        query = {}
        
        if category:
            query["category"] = category
        
        if tenant_id:
            # Get both system templates and tenant-specific templates
            query["$or"] = [
                {"tenant_id": tenant_id},
                {"is_system": True}
            ]
        elif is_system is not None:
            query["is_system"] = is_system
        
        templates = []
        cursor = self.collection.find(query).skip(skip).limit(limit)
        
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            templates.append(ThemeTemplate(**doc))
        
        return templates

    async def get_templates_by_category(
        self,
        category: str,
        tenant_id: Optional[str] = None,
    ) -> List[ThemeTemplate]:
        """Get templates by category"""
        
        valid_categories = ["spa", "barber", "salon", "modern", "classic"]
        if category not in valid_categories:
            raise ValueError(f"Invalid category. Must be one of: {', '.join(valid_categories)}")
        
        query = {"category": category}
        
        if tenant_id:
            query["$or"] = [
                {"tenant_id": tenant_id},
                {"is_system": True}
            ]
        else:
            query["is_system"] = True
        
        templates = []
        cursor = self.collection.find(query)
        
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            templates.append(ThemeTemplate(**doc))
        
        return templates

    async def update_template(
        self,
        template_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        branding: Optional[Dict[str, Any]] = None,
        preview_image_url: Optional[str] = None,
        is_premium: Optional[bool] = None,
    ) -> Optional[ThemeTemplate]:
        """Update a template"""
        
        try:
            update_dict = {"updated_at": datetime.utcnow()}
            
            if name is not None:
                update_dict["name"] = name
            if description is not None:
                update_dict["description"] = description
            if branding is not None:
                if not isinstance(branding, dict):
                    raise ValueError("Branding must be a dictionary")
                update_dict["branding"] = branding
            if preview_image_url is not None:
                update_dict["preview_image_url"] = preview_image_url
            if is_premium is not None:
                update_dict["is_premium"] = is_premium
            
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(template_id)},
                {"$set": update_dict},
                return_document=True,
            )
            
            if result:
                result["_id"] = str(result["_id"])
                return ThemeTemplate(**result)
        except Exception:
            pass
        
        return None

    async def delete_template(self, template_id: str) -> bool:
        """Delete a template"""
        
        try:
            result = await self.collection.delete_one({"_id": ObjectId(template_id)})
            return result.deleted_count > 0
        except Exception:
            return False

    async def duplicate_template(
        self,
        template_id: str,
        new_name: str,
        tenant_id: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> Optional[ThemeTemplate]:
        """Duplicate a template"""
        
        original = await self.get_template(template_id)
        if not original:
            return None
        
        # Create new template with copied branding
        return await self.create_template(
            name=new_name,
            category=original.category,
            branding=original.branding.copy(),
            description=original.description,
            preview_image_url=original.preview_image_url,
            tenant_id=tenant_id,
            is_system=False,
            is_premium=original.is_premium,
            created_by=created_by,
        )

    async def get_system_templates(self) -> List[ThemeTemplate]:
        """Get all system templates"""
        return await self.get_templates(is_system=True)

    async def get_tenant_templates(self, tenant_id: str) -> List[ThemeTemplate]:
        """Get all templates for a tenant (including system templates)"""
        return await self.get_templates(tenant_id=tenant_id)

    async def create_default_templates(self) -> List[ThemeTemplate]:
        """Create default system templates"""
        
        templates = []
        
        # Spa template
        spa_template = await self.create_template(
            name="Modern Spa",
            category="spa",
            branding={
                "primary_color": "#8B7355",
                "secondary_color": "#D4A574",
                "accent_color": "#E8D5C4",
                "font_family": "Playfair Display",
                "company_name": "Your Spa",
                "tagline": "Relax and Rejuvenate",
            },
            description="Modern and elegant spa branding template with warm earth tones",
            preview_image_url="/templates/spa-preview.png",
            is_system=True,
            is_premium=False,
        )
        templates.append(spa_template)
        
        # Barber template
        barber_template = await self.create_template(
            name="Classic Barber",
            category="barber",
            branding={
                "primary_color": "#1A1A1A",
                "secondary_color": "#DC143C",
                "accent_color": "#FFFFFF",
                "font_family": "Roboto",
                "company_name": "Your Barber Shop",
                "tagline": "Premium Grooming",
            },
            description="Classic barber shop template with bold red and black colors",
            preview_image_url="/templates/barber-preview.png",
            is_system=True,
            is_premium=False,
        )
        templates.append(barber_template)
        
        # Salon template
        salon_template = await self.create_template(
            name="Chic Salon",
            category="salon",
            branding={
                "primary_color": "#FF69B4",
                "secondary_color": "#FFB6C1",
                "accent_color": "#FFF0F5",
                "font_family": "Montserrat",
                "company_name": "Your Salon",
                "tagline": "Beauty & Style",
            },
            description="Chic salon template with vibrant pink and light colors",
            preview_image_url="/templates/salon-preview.png",
            is_system=True,
            is_premium=False,
        )
        templates.append(salon_template)
        
        # Modern template
        modern_template = await self.create_template(
            name="Modern Minimal",
            category="modern",
            branding={
                "primary_color": "#2C3E50",
                "secondary_color": "#3498DB",
                "accent_color": "#ECF0F1",
                "font_family": "Inter",
                "company_name": "Your Business",
                "tagline": "Modern & Professional",
            },
            description="Modern minimal template with clean lines and professional colors",
            preview_image_url="/templates/modern-preview.png",
            is_system=True,
            is_premium=False,
        )
        templates.append(modern_template)
        
        # Classic template
        classic_template = await self.create_template(
            name="Timeless Classic",
            category="classic",
            branding={
                "primary_color": "#4A4A4A",
                "secondary_color": "#D4AF37",
                "accent_color": "#F5F5F5",
                "font_family": "Georgia",
                "company_name": "Your Business",
                "tagline": "Timeless Elegance",
            },
            description="Classic template with gold accents and timeless design",
            preview_image_url="/templates/classic-preview.png",
            is_system=True,
            is_premium=False,
        )
        templates.append(classic_template)
        
        return templates

    async def count_templates(
        self,
        category: Optional[str] = None,
        tenant_id: Optional[str] = None,
        is_system: Optional[bool] = None,
    ) -> int:
        """Count templates with optional filtering"""
        
        query = {}
        
        if category:
            query["category"] = category
        
        if tenant_id:
            query["$or"] = [
                {"tenant_id": tenant_id},
                {"is_system": True}
            ]
        elif is_system is not None:
            query["is_system"] = is_system
        
        return await self.collection.count_documents(query)
