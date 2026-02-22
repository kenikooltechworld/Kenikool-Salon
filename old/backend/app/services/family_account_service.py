"""
Family Account Service

Handles family account registration, management, and deferred payment.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from bson import ObjectId
import uuid

from app.database import get_database
from app.schemas.family_account import (
    FamilyAccountCreate,
    FamilyAccount,
    FamilyMember,
    FamilyBookingCreate
)


class FamilyAccountService:
    """Service for managing family accounts"""
    
    def __init__(self):
        self._db = None
        self._family_accounts_collection = None
        self._bookings_collection = None
        self._clients_collection = None
    
    @property
    def db(self):
        if self._db is None:
            self._db = get_database()
        return self._db
    
    @property
    def family_accounts_collection(self):
        if self._family_accounts_collection is None:
            self._family_accounts_collection = self.db.family_accounts
        return self._family_accounts_collection
    
    @property
    def bookings_collection(self):
        if self._bookings_collection is None:
            self._bookings_collection = self.db.bookings
        return self._bookings_collection
    
    @property
    def clients_collection(self):
        if self._clients_collection is None:
            self._clients_collection = self.db.clients
        return self._clients_collection
    
    async def create_family_account(
        self,
        account_data: FamilyAccountCreate,
        primary_client_id: str,
        salon_id: str
    ) -> FamilyAccount:
        """
        Create a new family account
        
        Args:
            account_data: Family account creation data
            primary_client_id: ID of the primary account holder
            salon_id: ID of the salon
            
        Returns:
            Created family account
        """
        # Generate unique family account ID
        family_account_id = f"FAM-{uuid.uuid4().hex[:8].upper()}"
        
        account_dict = {
            "family_account_id": family_account_id,
            "primary_client_id": primary_client_id,
            "salon_id": salon_id,
            "account_name": account_data.account_name,
            "members": [member.dict() for member in account_data.members],
            "credit_limit": account_data.credit_limit,
            "outstanding_balance": 0.0,
            "total_loyalty_points": 0,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = self.family_accounts_collection.insert_one(account_dict)
        account_dict["_id"] = result.inserted_id
        
        # TODO: Send notification to primary account holder (Task 2.5)
        
        return FamilyAccount(**account_dict)
    
    async def get_family_account(self, account_id: str) -> Optional[FamilyAccount]:
        """Get family account by ID"""
        account = self.family_accounts_collection.find_one({"_id": ObjectId(account_id)})
        return FamilyAccount(**account) if account else None
    
    async def get_family_account_by_family_id(self, family_account_id: str) -> Optional[FamilyAccount]:
        """Get family account by family_account_id"""
        account = self.family_accounts_collection.find_one({"family_account_id": family_account_id})
        return FamilyAccount(**account) if account else None
    
    async def get_family_accounts(
        self,
        salon_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[FamilyAccount]:
        """
        Get all family accounts for a salon
        
        Args:
            salon_id: ID of the salon
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of family accounts
        """
        cursor = self.family_accounts_collection.find(
            {"salon_id": salon_id}
        ).skip(skip).limit(limit).sort("created_at", -1)
        
        accounts = list(cursor)
        return [FamilyAccount(**account) for account in accounts]
    
    async def add_family_member(
        self,
        account_id: str,
        member: FamilyMember
    ) -> FamilyAccount:
        """
        Add a member to family account
        
        Args:
            account_id: ID of the family account
            member: Family member to add
            
        Returns:
            Updated family account
        """
        account = await self.get_family_account(account_id)
        if not account:
            raise ValueError(f"Family account {account_id} not found")
        
        # Check if member already exists
        existing_member_ids = [m.client_id for m in account.members]
        if member.client_id in existing_member_ids:
            raise ValueError(f"Client {member.client_id} is already a member of this family account")
        
        self.family_accounts_collection.update_one(
            {"_id": ObjectId(account_id)},
            {
                "$push": {"members": member.dict()},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        return await self.get_family_account(account_id)
    
    async def remove_family_member(
        self,
        account_id: str,
        client_id: str
    ) -> FamilyAccount:
        """
        Remove a member from family account
        
        Args:
            account_id: ID of the family account
            client_id: ID of the client to remove
            
        Returns:
            Updated family account
        """
        account = await self.get_family_account(account_id)
        if not account:
            raise ValueError(f"Family account {account_id} not found")
        
        # Cannot remove primary account holder
        if client_id == account.primary_client_id:
            raise ValueError("Cannot remove primary account holder")
        
        self.family_accounts_collection.update_one(
            {"_id": ObjectId(account_id)},
            {
                "$pull": {"members": {"client_id": client_id}},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        return await self.get_family_account(account_id)
    
    async def get_family_bookings(
        self,
        account_id: str,
        include_paid: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get all bookings for a family account
        
        Args:
            account_id: ID of the family account
            include_paid: Whether to include paid bookings
            
        Returns:
            List of bookings
        """
        account = await self.get_family_account(account_id)
        if not account:
            raise ValueError(f"Family account {account_id} not found")
        
        query = {"family_account_id": account.family_account_id}
        
        if not include_paid:
            query["payment_status"] = {"$ne": "paid"}
        
        cursor = self.bookings_collection.find(query).sort("booking_date", -1)
        bookings = list(cursor)
        
        return bookings
    
    async def get_outstanding_balance(self, account_id: str) -> Dict[str, Any]:
        """
        Get outstanding balance for family account
        
        Args:
            account_id: ID of the family account
            
        Returns:
            Dictionary with balance details
        """
        account = await self.get_family_account(account_id)
        if not account:
            raise ValueError(f"Family account {account_id} not found")
        
        # Get unpaid bookings
        unpaid_bookings = await self.get_family_bookings(account_id, include_paid=False)
        
        total_outstanding = sum(booking.get("total_price", 0) for booking in unpaid_bookings)
        
        return {
            "family_account_id": account.family_account_id,
            "outstanding_balance": round(total_outstanding, 2),
            "credit_limit": account.credit_limit,
            "available_credit": round(account.credit_limit - total_outstanding, 2),
            "unpaid_booking_count": len(unpaid_bookings),
            "unpaid_bookings": unpaid_bookings
        }
    
    async def check_credit_limit(
        self,
        account_id: str,
        booking_amount: float
    ) -> Dict[str, Any]:
        """
        Check if booking amount is within credit limit
        
        Args:
            account_id: ID of the family account
            booking_amount: Amount of the booking
            
        Returns:
            Dictionary with approval status
        """
        balance_info = await self.get_outstanding_balance(account_id)
        
        new_balance = balance_info["outstanding_balance"] + booking_amount
        within_limit = new_balance <= balance_info["credit_limit"]
        
        return {
            "approved": within_limit,
            "current_balance": balance_info["outstanding_balance"],
            "booking_amount": booking_amount,
            "new_balance": round(new_balance, 2),
            "credit_limit": balance_info["credit_limit"],
            "available_credit": balance_info["available_credit"]
        }
    
    async def create_family_booking(
        self,
        booking_data: FamilyBookingCreate,
        family_account_id: str,
        salon_id: str
    ) -> str:
        """
        Create a booking with deferred payment for family member
        
        Args:
            booking_data: Family booking creation data
            family_account_id: Family account ID
            salon_id: ID of the salon
            
        Returns:
            ID of created booking
        """
        # Get family account
        account = await self.get_family_account_by_family_id(family_account_id)
        if not account:
            raise ValueError(f"Family account {family_account_id} not found")
        
        # Check credit limit
        credit_check = await self.check_credit_limit(str(account.id), booking_data.total_price)
        if not credit_check["approved"]:
            raise ValueError(f"Booking exceeds credit limit. Available credit: {credit_check['available_credit']}")
        
        # Create booking with deferred payment
        booking_dict = {
            "client_id": booking_data.client_id,
            "salon_id": salon_id,
            "stylist_id": booking_data.stylist_id,
            "service_id": booking_data.service_id,
            "booking_date": booking_data.booking_date,
            "status": "confirmed",
            "payment_status": "deferred",
            "family_account_id": family_account_id,
            "total_price": booking_data.total_price,
            "notes": booking_data.notes,
            "created_at": datetime.utcnow()
        }
        
        result = self.bookings_collection.insert_one(booking_dict)
        
        # Update family account outstanding balance
        self.family_accounts_collection.update_one(
            {"family_account_id": family_account_id},
            {
                "$inc": {"outstanding_balance": booking_data.total_price},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        return str(result.inserted_id)
    
    async def pay_family_bookings(
        self,
        account_id: str,
        booking_ids: Optional[List[str]] = None,
        payment_amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Pay for family bookings (individual or bulk)
        
        Args:
            account_id: ID of the family account
            booking_ids: Optional list of specific booking IDs to pay
            payment_amount: Optional specific amount to pay
            
        Returns:
            Dictionary with payment details
        """
        account = await self.get_family_account(account_id)
        if not account:
            raise ValueError(f"Family account {account_id} not found")
        
        if booking_ids:
            # Pay specific bookings
            bookings_to_pay = []
            for booking_id in booking_ids:
                booking = self.bookings_collection.find_one({"_id": ObjectId(booking_id)})
                if booking and booking.get("family_account_id") == account.family_account_id:
                    bookings_to_pay.append(booking)
            
            total_paid = sum(booking.get("total_price", 0) for booking in bookings_to_pay)
            
            # Update bookings
            self.bookings_collection.update_many(
                {"_id": {"$in": [ObjectId(bid) for bid in booking_ids]}},
                {"$set": {"payment_status": "paid", "paid_at": datetime.utcnow()}}
            )
        else:
            # Pay all outstanding or specific amount
            unpaid_bookings = await self.get_family_bookings(account_id, include_paid=False)
            
            if payment_amount:
                # Pay specific amount across bookings
                remaining_amount = payment_amount
                bookings_to_pay = []
                
                for booking in unpaid_bookings:
                    if remaining_amount <= 0:
                        break
                    
                    booking_price = booking.get("total_price", 0)
                    if booking_price <= remaining_amount:
                        bookings_to_pay.append(booking["_id"])
                        remaining_amount -= booking_price
                
                total_paid = payment_amount - remaining_amount
                
                self.bookings_collection.update_many(
                    {"_id": {"$in": bookings_to_pay}},
                    {"$set": {"payment_status": "paid", "paid_at": datetime.utcnow()}}
                )
            else:
                # Pay all outstanding
                total_paid = sum(booking.get("total_price", 0) for booking in unpaid_bookings)
                
                self.bookings_collection.update_many(
                    {"family_account_id": account.family_account_id, "payment_status": "deferred"},
                    {"$set": {"payment_status": "paid", "paid_at": datetime.utcnow()}}
                )
        
        # Update family account balance
        self.family_accounts_collection.update_one(
            {"_id": ObjectId(account_id)},
            {
                "$inc": {"outstanding_balance": -total_paid},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        # TODO: Send payment confirmation notification (Task 2.5)
        
        return {
            "amount_paid": round(total_paid, 2),
            "remaining_balance": round(account.outstanding_balance - total_paid, 2)
        }
    
    async def update_loyalty_points(
        self,
        account_id: str,
        points: int
    ) -> FamilyAccount:
        """
        Update family loyalty points
        
        Args:
            account_id: ID of the family account
            points: Points to add (can be negative)
            
        Returns:
            Updated family account
        """
        self.family_accounts_collection.update_one(
            {"_id": ObjectId(account_id)},
            {
                "$inc": {"total_loyalty_points": points},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        return await self.get_family_account(account_id)


# Singleton instance
family_account_service = FamilyAccountService()
