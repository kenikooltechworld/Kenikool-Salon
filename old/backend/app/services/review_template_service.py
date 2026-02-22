"""
Review template service - Business logic for response template management
"""
from datetime import datetime
from typing import Dict, List, Optional
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class ReviewTemplateService:
    """Service layer for review template management"""
    
    def __init__(self, db):
        self.db = db
    
    async def get_templates(
        self,
        tenant_id: str,
        category: Optional[str] = None,
        include_default: bool = True
    ) -> List[Dict]:
        """Get response templates for tenant"""
        try:
            query = {"tenant_id": tenant_id}
            
            if category:
                if category not in ["positive", "negative", "neutral"]:
                    raise ValueError("Invalid category")
                query["category"] = category
            
            # Sort by default status first, then by creation date
            templates = list(
                self.db.review_templates.find(query)
                .sort([("is_default", -1), ("created_at", -1)])
            )
            
            for template in templates:
                template["_id"] = str(template["_id"])
            
            return templates
        
        except Exception as e:
            logger.error(f"Error getting templates: {e}")
            raise Exception(f"Failed to get templates: {str(e)}")
    
    async def get_template_by_id(
        self,
        template_id: str,
        tenant_id: str
    ) -> Dict:
        """Get specific template by ID"""
        try:
            template = self.db.review_templates.find_one({
                "_id": ObjectId(template_id),
                "tenant_id": tenant_id
            })
            
            if not template:
                raise ValueError("Template not found")
            
            template["_id"] = str(template["_id"])
            return template
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error getting template: {e}")
            raise Exception(f"Failed to get template: {str(e)}")
    
    async def create_template(
        self,
        tenant_id: str,
        name: str,
        category: str,
        text: str
    ) -> Dict:
        """Create custom response template"""
        try:
            # Validate category
            if category not in ["positive", "negative", "neutral"]:
                raise ValueError("Invalid category. Must be 'positive', 'negative', or 'neutral'")
            
            # Validate inputs
            if not name or not name.strip():
                raise ValueError("Template name cannot be empty")
            
            if not text or not text.strip():
                raise ValueError("Template text cannot be empty")
            
            if len(text) > 1000:
                raise ValueError("Template text cannot exceed 1000 characters")
            
            template_data = {
                "tenant_id": tenant_id,
                "name": name.strip(),
                "category": category,
                "text": text.strip(),
                "is_default": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = self.db.review_templates.insert_one(template_data)
            template_data["_id"] = str(result.inserted_id)
            
            return template_data
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error creating template: {e}")
            raise Exception(f"Failed to create template: {str(e)}")
    
    async def update_template(
        self,
        template_id: str,
        tenant_id: str,
        name: Optional[str] = None,
        category: Optional[str] = None,
        text: Optional[str] = None
    ) -> Dict:
        """Update response template"""
        try:
            # Find template
            template = self.db.review_templates.find_one({
                "_id": ObjectId(template_id),
                "tenant_id": tenant_id
            })
            
            if not template:
                raise ValueError("Template not found")
            
            # Prevent editing default templates
            if template.get("is_default"):
                raise ValueError("Cannot edit default templates")
            
            # Build update data
            update_data = {"updated_at": datetime.utcnow()}
            
            if name is not None:
                if not name.strip():
                    raise ValueError("Template name cannot be empty")
                update_data["name"] = name.strip()
            
            if category is not None:
                if category not in ["positive", "negative", "neutral"]:
                    raise ValueError("Invalid category")
                update_data["category"] = category
            
            if text is not None:
                if not text.strip():
                    raise ValueError("Template text cannot be empty")
                if len(text) > 1000:
                    raise ValueError("Template text cannot exceed 1000 characters")
                update_data["text"] = text.strip()
            
            # Update template
            self.db.review_templates.update_one(
                {"_id": ObjectId(template_id)},
                {"$set": update_data}
            )
            
            # Get updated template
            updated_template = self.db.review_templates.find_one({"_id": ObjectId(template_id)})
            updated_template["_id"] = str(updated_template["_id"])
            
            return updated_template
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error updating template: {e}")
            raise Exception(f"Failed to update template: {str(e)}")
    
    async def delete_template(
        self,
        template_id: str,
        tenant_id: str
    ) -> None:
        """Delete response template"""
        try:
            # Find template
            template = self.db.review_templates.find_one({
                "_id": ObjectId(template_id),
                "tenant_id": tenant_id
            })
            
            if not template:
                raise ValueError("Template not found")
            
            # Prevent deletion of default templates
            if template.get("is_default"):
                raise ValueError("Cannot delete default templates")
            
            # Delete template
            self.db.review_templates.delete_one({"_id": ObjectId(template_id)})
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error deleting template: {e}")
            raise Exception(f"Failed to delete template: {str(e)}")
    
    async def get_template_stats(self, tenant_id: str) -> Dict:
        """Get template statistics"""
        try:
            total = self.db.review_templates.count_documents({"tenant_id": tenant_id})
            
            # Count by category
            category_counts = {}
            for category in ["positive", "negative", "neutral"]:
                count = self.db.review_templates.count_documents({
                    "tenant_id": tenant_id,
                    "category": category
                })
                category_counts[category] = count
            
            # Count default vs custom
            default_count = self.db.review_templates.count_documents({
                "tenant_id": tenant_id,
                "is_default": True
            })
            custom_count = total - default_count
            
            return {
                "total": total,
                "by_category": category_counts,
                "default": default_count,
                "custom": custom_count
            }
        
        except Exception as e:
            logger.error(f"Error getting template stats: {e}")
            raise Exception(f"Failed to get template stats: {str(e)}")
    
    async def duplicate_template(
        self,
        template_id: str,
        tenant_id: str,
        new_name: Optional[str] = None
    ) -> Dict:
        """Duplicate an existing template"""
        try:
            # Get original template
            template = self.db.review_templates.find_one({
                "_id": ObjectId(template_id),
                "tenant_id": tenant_id
            })
            
            if not template:
                raise ValueError("Template not found")
            
            # Create new template based on original
            new_template_data = {
                "tenant_id": tenant_id,
                "name": new_name or f"{template['name']} (Copy)",
                "category": template["category"],
                "text": template["text"],
                "is_default": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = self.db.review_templates.insert_one(new_template_data)
            new_template_data["_id"] = str(result.inserted_id)
            
            return new_template_data
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error duplicating template: {e}")
            raise Exception(f"Failed to duplicate template: {str(e)}")
    
    async def search_templates(
        self,
        tenant_id: str,
        query: str
    ) -> List[Dict]:
        """Search templates by name or text"""
        try:
            search_query = {
                "tenant_id": tenant_id,
                "$or": [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"text": {"$regex": query, "$options": "i"}}
                ]
            }
            
            templates = list(
                self.db.review_templates.find(search_query)
                .sort([("is_default", -1), ("created_at", -1)])
            )
            
            for template in templates:
                template["_id"] = str(template["_id"])
            
            return templates
        
        except Exception as e:
            logger.error(f"Error searching templates: {e}")
            raise Exception(f"Failed to search templates: {str(e)}")
