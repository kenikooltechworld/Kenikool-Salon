"""
Vendor management service
"""
from bson import ObjectId
from datetime import datetime
from typing import Dict, List, Optional
import logging

from app.database import Database
from app.api.exceptions import NotFoundException, BadRequestException

logger = logging.getLogger(__name__)


class VendorService:
    """Service for vendor management"""
    
    @staticmethod
    def create_vendor(
        tenant_id: str,
        name: str,
        contact_person: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        tax_id: Optional[str] = None,
        payment_terms: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict:
        """
        Create a new vendor
        
        Returns:
            Dict with created vendor data
        """
        db = Database.get_db()
        
        # Check if vendor name already exists
        existing = db.vendors.find_one({
            "tenant_id": tenant_id,
            "name": {"$regex": f"^{name}$", "$options": "i"}
        })
        
        if existing:
            raise BadRequestException(f"Vendor with name '{name}' already exists")
        
        # Generate vendor number
        last_vendor = db.vendors.find_one(
            {"tenant_id": tenant_id},
            sort=[("created_at", -1)]
        )
        
        if last_vendor and "vendor_number" in last_vendor:
            last_num = int(last_vendor["vendor_number"].split("-")[-1])
            vendor_number = f"VEN-{last_num + 1:05d}"
        else:
            vendor_number = "VEN-00001"
        
        vendor_data = {
            "tenant_id": tenant_id,
            "vendor_number": vendor_number,
            "name": name,
            "contact_person": contact_person,
            "email": email,
            "phone": phone,
            "address": address,
            "tax_id": tax_id,
            "payment_terms": payment_terms,
            "notes": notes,
            "status": "active",
            "total_outstanding": 0.0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.vendors.insert_one(vendor_data)
        vendor_id = str(result.inserted_id)
        
        logger.info(f"Vendor created: {vendor_id} ({vendor_number}) for tenant: {tenant_id}")
        
        vendor_doc = db.vendors.find_one({"_id": ObjectId(vendor_id)})
        return VendorService._format_vendor_response(vendor_doc)
    
    @staticmethod
    def get_vendors(
        tenant_id: str,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Dict]:
        """
        Get vendors for tenant
        
        Returns:
            List of vendor dicts
        """
        db = Database.get_db()
        
        query = {"tenant_id": tenant_id}
        
        if status:
            query["status"] = status
        
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"vendor_number": {"$regex": search, "$options": "i"}},
                {"contact_person": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}}
            ]
        
        vendors = list(db.vendors.find(query).sort("name", 1))
        
        # Calculate outstanding amounts
        for vendor in vendors:
            outstanding = VendorService._calculate_vendor_outstanding(tenant_id, str(vendor["_id"]))
            vendor["total_outstanding"] = outstanding
            
            # Update in database if different
            if vendor.get("total_outstanding", 0) != outstanding:
                db.vendors.update_one(
                    {"_id": vendor["_id"]},
                    {"$set": {"total_outstanding": outstanding}}
                )
        
        return [VendorService._format_vendor_response(v) for v in vendors]
    
    @staticmethod
    def get_vendor(tenant_id: str, vendor_id: str) -> Dict:
        """
        Get a single vendor by ID
        
        Returns:
            Dict with vendor data
        """
        db = Database.get_db()
        
        vendor = db.vendors.find_one({
            "_id": ObjectId(vendor_id),
            "tenant_id": tenant_id
        })
        
        if not vendor:
            raise NotFoundException("Vendor not found")
        
        # Calculate outstanding amount
        outstanding = VendorService._calculate_vendor_outstanding(tenant_id, vendor_id)
        vendor["total_outstanding"] = outstanding
        
        return VendorService._format_vendor_response(vendor)
    
    @staticmethod
    def update_vendor(
        tenant_id: str,
        vendor_id: str,
        name: Optional[str] = None,
        contact_person: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        tax_id: Optional[str] = None,
        payment_terms: Optional[str] = None,
        notes: Optional[str] = None,
        status: Optional[str] = None
    ) -> Dict:
        """
        Update a vendor
        
        Returns:
            Dict with updated vendor data
        """
        db = Database.get_db()
        
        # Get existing vendor
        vendor = db.vendors.find_one({
            "_id": ObjectId(vendor_id),
            "tenant_id": tenant_id
        })
        
        if not vendor:
            raise NotFoundException("Vendor not found")
        
        # Check if name already exists (if changing name)
        if name and name.lower() != vendor["name"].lower():
            existing = db.vendors.find_one({
                "tenant_id": tenant_id,
                "name": {"$regex": f"^{name}$", "$options": "i"},
                "_id": {"$ne": ObjectId(vendor_id)}
            })
            
            if existing:
                raise BadRequestException(f"Vendor with name '{name}' already exists")
        
        update_data = {"updated_at": datetime.utcnow()}
        
        if name is not None:
            update_data["name"] = name
        if contact_person is not None:
            update_data["contact_person"] = contact_person
        if email is not None:
            update_data["email"] = email
        if phone is not None:
            update_data["phone"] = phone
        if address is not None:
            update_data["address"] = address
        if tax_id is not None:
            update_data["tax_id"] = tax_id
        if payment_terms is not None:
            update_data["payment_terms"] = payment_terms
        if notes is not None:
            update_data["notes"] = notes
        if status is not None:
            update_data["status"] = status
        
        # Update the vendor
        db.vendors.update_one(
            {"_id": ObjectId(vendor_id)},
            {"$set": update_data}
        )
        
        # Return updated vendor
        updated_vendor = db.vendors.find_one({"_id": ObjectId(vendor_id)})
        return VendorService._format_vendor_response(updated_vendor)
    
    @staticmethod
    def delete_vendor(tenant_id: str, vendor_id: str) -> Dict:
        """
        Delete a vendor (only if no outstanding bills)
        
        Returns:
            Dict with deletion result
        """
        db = Database.get_db()
        
        # Get existing vendor
        vendor = db.vendors.find_one({
            "_id": ObjectId(vendor_id),
            "tenant_id": tenant_id
        })
        
        if not vendor:
            raise NotFoundException("Vendor not found")
        
        # Check for outstanding bills
        outstanding_bills = db.bills.count_documents({
            "tenant_id": tenant_id,
            "vendor_id": vendor_id,
            "status": {"$nin": ["paid", "cancelled"]},
            "amount_due": {"$gt": 0}
        })
        
        if outstanding_bills > 0:
            raise BadRequestException("Cannot delete vendor with outstanding bills")
        
        # Check for any bills (even paid ones)
        any_bills = db.bills.count_documents({
            "tenant_id": tenant_id,
            "vendor_id": vendor_id
        })
        
        if any_bills > 0:
            # If there are bills, just deactivate the vendor
            db.vendors.update_one(
                {"_id": ObjectId(vendor_id)},
                {"$set": {"status": "inactive", "updated_at": datetime.utcnow()}}
            )
            return {"message": "Vendor deactivated (has bill history)", "deactivated": True}
        else:
            # If no bills, delete completely
            db.vendors.delete_one({"_id": ObjectId(vendor_id)})
            return {"message": "Vendor deleted successfully", "deleted": True}
    
    @staticmethod
    def _calculate_vendor_outstanding(tenant_id: str, vendor_id: str) -> float:
        """Calculate total outstanding amount for a vendor"""
        db = Database.get_db()
        
        pipeline = [
            {
                "$match": {
                    "tenant_id": tenant_id,
                    "vendor_id": vendor_id,
                    "status": {"$nin": ["cancelled"]},
                    "amount_due": {"$gt": 0}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total": {"$sum": "$amount_due"}
                }
            }
        ]
        
        result = list(db.bills.aggregate(pipeline))
        return result[0]["total"] if result else 0.0
    
    @staticmethod
    def _format_vendor_response(vendor_doc: Dict) -> Dict:
        """Format vendor document for response"""
        return {
            "id": str(vendor_doc["_id"]),
            "tenant_id": vendor_doc["tenant_id"],
            "vendor_number": vendor_doc["vendor_number"],
            "name": vendor_doc["name"],
            "contact_person": vendor_doc.get("contact_person"),
            "email": vendor_doc.get("email"),
            "phone": vendor_doc.get("phone"),
            "address": vendor_doc.get("address"),
            "tax_id": vendor_doc.get("tax_id"),
            "payment_terms": vendor_doc.get("payment_terms"),
            "notes": vendor_doc.get("notes"),
            "status": vendor_doc.get("status", "active"),
            "total_outstanding": vendor_doc.get("total_outstanding", 0.0),
            "created_at": vendor_doc["created_at"],
            "updated_at": vendor_doc["updated_at"]
        }


# Singleton instance
vendor_service = VendorService()