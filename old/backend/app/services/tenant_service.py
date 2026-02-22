"""
Tenant service - Business logic layer
"""
from bson import ObjectId
from datetime import datetime
from typing import Dict, Optional, Tuple
import logging

from app.database import Database
from app.api.exceptions import NotFoundException, ForbiddenException
from app.schemas.auth import BankAccountInput

logger = logging.getLogger(__name__)


class TenantService:
    """Tenant service for handling tenant business logic"""
    
    @staticmethod
    async def get_tenant(tenant_id: str) -> Dict:
        """
        Get tenant by ID
        
        Returns:
            Dict with tenant data
        """
        db = Database.get_db()
        
        tenant_doc = db.tenants.find_one({"_id": ObjectId(tenant_id)})
        if tenant_doc is None:
            raise NotFoundException("Tenant not found")
        
        return TenantService._format_tenant_response(tenant_doc)
    
    @staticmethod
    async def get_tenant_by_subdomain(subdomain: str) -> Dict:
        """
        Get tenant by subdomain (for public booking page)
        
        Returns:
            Dict with tenant data
        """
        db = Database.get_db()
        
        tenant_doc = db.tenants.find_one({"subdomain": subdomain, "is_active": True})
        if tenant_doc is None:
            raise NotFoundException("Salon not found")
        
        return TenantService._format_tenant_response(tenant_doc)
    
    @staticmethod
    async def update_tenant(
        tenant_id: str,
        salon_name: Optional[str] = None,
        owner_name: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[str] = None,
        description: Optional[str] = None,
        logo: Optional[str] = None,
        brand_color: Optional[str] = None,
        bank_account: Optional[Dict] = None
    ) -> Dict:
        """
        Update tenant profile
        
        Returns:
            Dict with updated tenant data
        """
        db = Database.get_db()
        
        # Build update data
        update_data = {"updated_at": datetime.utcnow()}
        
        if salon_name is not None:
            update_data["salon_name"] = salon_name
        if owner_name is not None:
            update_data["owner_name"] = owner_name
        if phone is not None:
            update_data["phone"] = phone
        if email is not None:
            update_data["email"] = email
        if address is not None:
            update_data["address"] = address
        if description is not None:
            update_data["description"] = description
        if logo is not None:
            update_data["logo_url"] = logo
        if brand_color is not None:
            update_data["brand_color"] = brand_color
        if bank_account is not None:
            update_data["bank_account"] = bank_account
        
        # Update tenant
        db.tenants.update_one(
            {"_id": ObjectId(tenant_id)},
            {"$set": update_data}
        )
        
        logger.info(f"Tenant updated: {tenant_id}")
        
        # Fetch updated tenant
        tenant_doc = db.tenants.find_one({"_id": ObjectId(tenant_id)})
        return TenantService._format_tenant_response(tenant_doc)
    
    @staticmethod
    async def upload_logo(tenant_id: str, file_bytes: bytes) -> Dict:
        """
        Upload salon logo to Cloudinary
        
        Returns:
            Dict with updated tenant data
        """
        from app.services.cloudinary_service import upload_image
        
        db = Database.get_db()
        
        # Upload to Cloudinary
        logo_url = await upload_image(
            file_bytes,
            folder=f"salons/{tenant_id}",
            public_id="logo"
        )
        
        # Update tenant
        db.tenants.update_one(
            {"_id": ObjectId(tenant_id)},
            {"$set": {"logo_url": logo_url, "updated_at": datetime.utcnow()}}
        )
        
        logger.info(f"Logo uploaded for tenant: {tenant_id}")
        
        # Fetch updated tenant
        tenant_doc = db.tenants.find_one({"_id": ObjectId(tenant_id)})
        return TenantService._format_tenant_response(tenant_doc)
    
    @staticmethod
    async def generate_qr_code(tenant_id: str) -> Dict:
        """
        Generate QR code for booking page
        
        Returns:
            Dict with updated tenant data
        """
        from app.services.qr_service import generate_booking_qr
        from app.services.cloudinary_service import upload_image
        
        db = Database.get_db()
        
        # Get tenant
        tenant_doc = db.tenants.find_one({"_id": ObjectId(tenant_id)})
        if tenant_doc is None:
            raise NotFoundException("Tenant not found")
        
        # Generate QR code
        qr_bytes = generate_booking_qr(tenant_doc["subdomain"])
        
        # Upload to Cloudinary
        qr_url = await upload_image(
            qr_bytes,
            folder=f"salons/{tenant_id}",
            public_id="qr_code"
        )
        
        # Update tenant
        db.tenants.update_one(
            {"_id": ObjectId(tenant_id)},
            {"$set": {"qr_code_url": qr_url, "updated_at": datetime.utcnow()}}
        )
        
        logger.info(f"QR code generated for tenant: {tenant_id}")
        
        # Fetch updated tenant
        tenant_doc = db.tenants.find_one({"_id": ObjectId(tenant_id)})
        return TenantService._format_tenant_response(tenant_doc)
    
    @staticmethod
    async def check_salon_name_availability(salon_name: str) -> Tuple[bool, Optional[str]]:
        """
        Check if salon name is available
        
        Returns:
            Tuple of (available, suggestion)
        """
        db = Database.get_db()
        
        # Check for exact match (case-insensitive)
        existing_salon = db.tenants.find_one({
            "salon_name": {"$regex": f"^{salon_name}$", "$options": "i"}
        })
        
        if existing_salon is None:
            return True, None
        
        # Generate suggestion
        suggestion = f"{salon_name} - [Your Location]"
        return False, suggestion
    
    @staticmethod
    def _format_tenant_response(tenant_doc: Dict) -> Dict:
        """Format tenant document for response"""
        bank_account = None
        if tenant_doc.get("bank_account"):
            ba = tenant_doc["bank_account"]
            bank_account = {
                "bank_name": ba["bank_name"],
                "account_number": ba["account_number"],
                "account_name": ba["account_name"],
                "bank_code": ba.get("bank_code")
            }
        
        return {
            "id": str(tenant_doc["_id"]),
            "salon_name": tenant_doc["salon_name"],
            "subdomain": tenant_doc["subdomain"],
            "custom_domain": tenant_doc.get("custom_domain"),
            "owner_name": tenant_doc["owner_name"],
            "phone": tenant_doc["phone"],
            "email": tenant_doc["email"],
            "address": tenant_doc.get("address"),
            "description": tenant_doc.get("description"),
            "logo_url": tenant_doc.get("logo_url"),
            "brand_color": tenant_doc["brand_color"],
            "qr_code_url": tenant_doc.get("qr_code_url"),
            "is_active": tenant_doc["is_active"],
            "subscription_plan": tenant_doc["subscription_plan"],
            "bank_account": bank_account,
            "created_at": tenant_doc["created_at"]
        }


# Singleton instance
tenant_service = TenantService()
