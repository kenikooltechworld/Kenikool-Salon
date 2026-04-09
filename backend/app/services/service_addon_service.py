"""Service Add-on Service"""
from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from decimal import Decimal

from app.models.service_addon import ServiceAddon
from app.schemas.service_addon import ServiceAddonCreate, ServiceAddonUpdate


class ServiceAddonService:
    """Service for managing service add-ons"""
    
    @staticmethod
    def get_addons_for_service(tenant_id: ObjectId, service_id: ObjectId) -> List[ServiceAddon]:
        """Get all active addons applicable to a service"""
        return list(ServiceAddon.objects(
            tenant_id=tenant_id,
            is_active=True,
            applicable_services=service_id
        ).order_by("display_order"))
    
    @staticmethod
    def get_addon_by_id(tenant_id: ObjectId, addon_id: ObjectId) -> Optional[ServiceAddon]:
        """Get addon by ID"""
        return ServiceAddon.objects(
            id=addon_id,
            tenant_id=tenant_id
        ).first()
    
    @staticmethod
    def get_all_addons(tenant_id: ObjectId, is_active: Optional[bool] = None) -> List[ServiceAddon]:
        """Get all addons for a tenant"""
        query = {"tenant_id": tenant_id}
        if is_active is not None:
            query["is_active"] = is_active
        
        return list(ServiceAddon.objects(**query).order_by("display_order"))
    
    @staticmethod
    def create_addon(tenant_id: ObjectId, addon_data: ServiceAddonCreate) -> ServiceAddon:
        """Create a new service addon"""
        # Convert service IDs to ObjectId
        applicable_services = [ObjectId(sid) for sid in addon_data.applicable_services]
        
        addon = ServiceAddon(
            tenant_id=tenant_id,
            name=addon_data.name,
            description=addon_data.description,
            price=addon_data.price,
            duration_minutes=addon_data.duration_minutes,
            image_url=addon_data.image_url,
            applicable_services=applicable_services,
            category=addon_data.category,
            display_order=addon_data.display_order,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        addon.save()
        return addon
    
    @staticmethod
    def update_addon(addon_id: ObjectId, addon_data: ServiceAddonUpdate) -> Optional[ServiceAddon]:
        """Update service addon"""
        addon = ServiceAddon.objects(id=addon_id).first()
        if not addon:
            return None
        
        update_data = addon_data.dict(exclude_unset=True)
        
        # Convert service IDs to ObjectId if provided
        if "applicable_services" in update_data:
            update_data["applicable_services"] = [
                ObjectId(sid) for sid in update_data["applicable_services"]
            ]
        
        for key, value in update_data.items():
            setattr(addon, key, value)
        
        addon.updated_at = datetime.utcnow()
        addon.save()
        return addon
    
    @staticmethod
    def delete_addon(addon_id: ObjectId) -> bool:
        """Delete service addon (soft delete by setting is_active=False)"""
        addon = ServiceAddon.objects(id=addon_id).first()
        if not addon:
            return False
        
        addon.is_active = False
        addon.updated_at = datetime.utcnow()
        addon.save()
        return True
    
    @staticmethod
    def calculate_addons_total(tenant_id: ObjectId, selected_addons: List[dict]) -> tuple[Decimal, List[dict]]:
        """
        Calculate total price and duration for selected addons
        
        Args:
            tenant_id: Tenant ID
            selected_addons: List of dicts with addon_id and quantity
            
        Returns:
            Tuple of (total_price, addon_details)
        """
        total_price = Decimal("0")
        addon_details = []
        
        for addon_data in selected_addons:
            addon = ServiceAddon.objects(
                id=ObjectId(addon_data["addon_id"]),
                tenant_id=tenant_id
            ).first()
            
            if addon and addon.is_active:
                quantity = addon_data.get("quantity", 1)
                addon_price = Decimal(str(addon.price))
                
                addon_details.append({
                    "addon_id": str(addon.id),
                    "name": addon.name,
                    "price": float(addon_price),
                    "duration_minutes": addon.duration_minutes,
                    "quantity": quantity,
                    "subtotal": float(addon_price * quantity)
                })
                total_price += addon_price * quantity
        
        return total_price, addon_details
