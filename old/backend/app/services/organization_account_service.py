"""
Organization Account Service - Business logic for organization accounts
"""
from datetime import datetime
from typing import Dict, List, Optional
from bson import ObjectId
import logging

from app.database import Database
from app.api.exceptions import BadRequestException, NotFoundException

logger = logging.getLogger(__name__)


class OrganizationAccountService:
    """Service for managing organization accounts"""
    
    @staticmethod
    async def create_organization_account(
        account_data: Dict,
        admin_id: str,
        salon_id: str
    ) -> Dict:
        """
        Create a new organization account
        
        Requirements: 20
        """
        db = Database.get_db()
        
        org_account = {
            "company_name": account_data.get("company_name"),
            "company_email": account_data.get("company_email"),
            "company_phone": account_data.get("company_phone"),
            "industry": account_data.get("industry"),
            "employee_count": account_data.get("employee_count", 0),
            "admin_id": ObjectId(admin_id),
            "tenant_id": salon_id,
            "employees": [],
            "contract_terms": account_data.get("contract_terms", {}),
            "credit_limit": account_data.get("credit_limit", 0),
            "current_balance": 0,
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.organization_accounts.insert_one(org_account)
        org_account["_id"] = result.inserted_id
        
        logger.info(f"Created organization account: {result.inserted_id}")
        return org_account
    
    @staticmethod
    async def get_organization_accounts(
        salon_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[Dict]:
        """Get all organization accounts for a salon"""
        db = Database.get_db()
        
        accounts = list(db.organization_accounts.find(
            {"tenant_id": salon_id}
        ).skip(skip).limit(limit))
        
        return accounts
    
    @staticmethod
    async def get_organization_account(
        org_id: str,
        salon_id: str
    ) -> Optional[Dict]:
        """Get a specific organization account"""
        db = Database.get_db()
        
        account = db.organization_accounts.find_one({
            "_id": ObjectId(org_id),
            "tenant_id": salon_id
        })
        
        return account
    
    @staticmethod
    async def add_employee(
        org_id: str,
        employee_data: Dict,
        salon_id: str
    ) -> Dict:
        """Add an employee to organization account"""
        db = Database.get_db()
        
        org_account = db.organization_accounts.find_one({
            "_id": ObjectId(org_id),
            "tenant_id": salon_id
        })
        
        if not org_account:
            raise NotFoundException("Organization account not found")
        
        employee = {
            "_id": ObjectId(),
            "name": employee_data.get("name"),
            "email": employee_data.get("email"),
            "phone": employee_data.get("phone"),
            "department": employee_data.get("department"),
            "position": employee_data.get("position"),
            "added_at": datetime.utcnow()
        }
        
        db.organization_accounts.update_one(
            {"_id": ObjectId(org_id)},
            {
                "$push": {"employees": employee},
                "$inc": {"employee_count": 1},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        logger.info(f"Added employee {employee['_id']} to organization {org_id}")
        return employee
    
    @staticmethod
    async def get_organization_employees(
        org_id: str,
        salon_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict]:
        """Get all employees in organization account"""
        db = Database.get_db()
        
        org_account = db.organization_accounts.find_one({
            "_id": ObjectId(org_id),
            "tenant_id": salon_id
        })
        
        if not org_account:
            raise NotFoundException("Organization account not found")
        
        employees = org_account.get("employees", [])[skip:skip+limit]
        return employees
    
    @staticmethod
    async def remove_employee(
        org_id: str,
        employee_id: str,
        salon_id: str
    ) -> bool:
        """Remove an employee from organization account"""
        db = Database.get_db()
        
        result = db.organization_accounts.update_one(
            {
                "_id": ObjectId(org_id),
                "tenant_id": salon_id
            },
            {
                "$pull": {"employees": {"_id": ObjectId(employee_id)}},
                "$inc": {"employee_count": -1},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        return result.modified_count > 0
    
    @staticmethod
    async def create_organization_booking(
        org_id: str,
        booking_data: Dict,
        salon_id: str
    ) -> Dict:
        """
        Create bulk booking for organization employees
        
        Requirements: 20
        """
        db = Database.get_db()
        
        org_account = db.organization_accounts.find_one({
            "_id": ObjectId(org_id),
            "tenant_id": salon_id
        })
        
        if not org_account:
            raise NotFoundException("Organization account not found")
        
        # Create individual bookings for each employee-service combination
        bookings = []
        total_amount = 0
        
        for employee_booking in booking_data.get("employee_bookings", []):
            employee_id = employee_booking.get("employee_id")
            services = employee_booking.get("services", [])
            
            for service_id in services:
                service = db.services.find_one({"_id": ObjectId(service_id)})
                if not service:
                    continue
                
                booking = {
                    "org_id": ObjectId(org_id),
                    "employee_id": employee_id,
                    "service_id": ObjectId(service_id),
                    "stylist_id": ObjectId(employee_booking.get("stylist_id")),
                    "booking_date": employee_booking.get("booking_date"),
                    "status": "pending",
                    "price": service.get("price", 0),
                    "payment_status": "deferred" if booking_data.get("deferred_payment") else "pending",
                    "tenant_id": salon_id,
                    "created_at": datetime.utcnow()
                }
                
                result = db.bookings.insert_one(booking)
                booking["_id"] = result.inserted_id
                bookings.append(booking)
                total_amount += booking["price"]
        
        # Update organization balance if deferred payment
        if booking_data.get("deferred_payment"):
            db.organization_accounts.update_one(
                {"_id": ObjectId(org_id)},
                {
                    "$inc": {"current_balance": total_amount},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
        
        logger.info(f"Created {len(bookings)} bookings for organization {org_id}")
        
        return {
            "org_id": org_id,
            "booking_count": len(bookings),
            "total_amount": total_amount,
            "bookings": bookings,
            "deferred_payment": booking_data.get("deferred_payment", False)
        }
    
    @staticmethod
    async def get_organization_bookings(
        org_id: str,
        salon_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[Dict]:
        """Get all bookings for organization"""
        db = Database.get_db()
        
        bookings = list(db.bookings.find({
            "org_id": ObjectId(org_id),
            "tenant_id": salon_id
        }).skip(skip).limit(limit))
        
        return bookings
    
    @staticmethod
    async def update_organization_account(
        org_id: str,
        update_data: Dict,
        salon_id: str
    ) -> Optional[Dict]:
        """Update organization account details"""
        db = Database.get_db()
        
        update_data["updated_at"] = datetime.utcnow()
        
        result = db.organization_accounts.find_one_and_update(
            {
                "_id": ObjectId(org_id),
                "tenant_id": salon_id
            },
            {"$set": update_data},
            return_document=True
        )
        
        return result


# Singleton instance
organization_account_service = OrganizationAccountService()
