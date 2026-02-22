"""
Service Inquiry Service

Handles custom service requests from clients with image upload support.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from bson import ObjectId

from app.database import get_database
from app.schemas.service_inquiry import (
    ServiceInquiryCreate,
    ServiceInquiry,
    InquiryStatus
)


class ServiceInquiryService:
    """Service for managing service inquiries"""
    
    def __init__(self):
        self._db = None
        self._inquiries_collection = None
        self._services_collection = None
        self._bookings_collection = None
    
    @property
    def db(self):
        if self._db is None:
            self._db = get_database()
        return self._db
    
    @property
    def inquiries_collection(self):
        if self._inquiries_collection is None:
            self._inquiries_collection = self.db.service_inquiries
        return self._inquiries_collection
    
    @property
    def services_collection(self):
        if self._services_collection is None:
            self._services_collection = self.db.services
        return self._services_collection
    
    @property
    def bookings_collection(self):
        if self._bookings_collection is None:
            self._bookings_collection = self.db.bookings
        return self._bookings_collection
    
    async def create_inquiry(
        self,
        inquiry_data: ServiceInquiryCreate,
        client_id: str,
        salon_id: str
    ) -> ServiceInquiry:
        """
        Create a new service inquiry
        
        Args:
            inquiry_data: Inquiry creation data
            client_id: ID of the client making the inquiry
            salon_id: ID of the salon
            
        Returns:
            Created service inquiry
        """
        inquiry_dict = {
            "client_id": client_id,
            "salon_id": salon_id,
            "description": inquiry_data.description,
            "image_urls": inquiry_data.image_urls or [],
            "preferred_date": inquiry_data.preferred_date,
            "status": InquiryStatus.PENDING,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await self.inquiries_collection.insert_one(inquiry_dict)
        inquiry_dict["_id"] = result.inserted_id
        
        # TODO: Send notification to salon owner (Task 2.5)
        
        return ServiceInquiry(**inquiry_dict)
    
    async def get_inquiry(self, inquiry_id: str) -> Optional[ServiceInquiry]:
        """Get inquiry by ID"""
        inquiry = await self.inquiries_collection.find_one({"_id": ObjectId(inquiry_id)})
        return ServiceInquiry(**inquiry) if inquiry else None
    
    async def get_inquiries(
        self,
        salon_id: str,
        status: Optional[InquiryStatus] = None,
        client_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[ServiceInquiry]:
        """
        Get inquiries with optional filtering
        
        Args:
            salon_id: ID of the salon
            status: Filter by status
            client_id: Filter by client
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of service inquiries
        """
        query = {"salon_id": salon_id}
        
        if status:
            query["status"] = status
        
        if client_id:
            query["client_id"] = client_id
        
        cursor = self.inquiries_collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
        inquiries = await cursor.to_list(length=limit)
        
        return [ServiceInquiry(**inquiry) for inquiry in inquiries]
    
    async def respond_to_inquiry(
        self,
        inquiry_id: str,
        response: str,
        status: InquiryStatus,
        custom_service_name: Optional[str] = None,
        custom_service_price: Optional[float] = None,
        custom_service_duration: Optional[int] = None
    ) -> ServiceInquiry:
        """
        Respond to a service inquiry
        
        Args:
            inquiry_id: ID of the inquiry
            response: Response message
            status: New status (approved/declined)
            custom_service_name: Name for custom service if approved
            custom_service_price: Price for custom service if approved
            custom_service_duration: Duration in minutes if approved
            
        Returns:
            Updated service inquiry
        """
        inquiry = await self.get_inquiry(inquiry_id)
        if not inquiry:
            raise ValueError(f"Inquiry {inquiry_id} not found")
        
        update_data = {
            "response": response,
            "status": status,
            "responded_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # If approved, create custom service
        if status == InquiryStatus.APPROVED and custom_service_name:
            service_data = {
                "name": custom_service_name,
                "description": f"Custom service for inquiry {inquiry_id}",
                "price": custom_service_price or 0,
                "duration": custom_service_duration or 60,
                "salon_id": inquiry.salon_id,
                "is_custom": True,
                "inquiry_id": inquiry_id,
                "created_at": datetime.utcnow()
            }
            
            service_result = await self.services_collection.insert_one(service_data)
            update_data["custom_service_id"] = str(service_result.inserted_id)
        
        await self.inquiries_collection.update_one(
            {"_id": ObjectId(inquiry_id)},
            {"$set": update_data}
        )
        
        # TODO: Send notification to client (Task 2.5)
        
        return await self.get_inquiry(inquiry_id)
    
    async def convert_to_booking(
        self,
        inquiry_id: str,
        booking_date: datetime,
        stylist_id: str
    ) -> str:
        """
        Convert approved inquiry to booking
        
        Args:
            inquiry_id: ID of the inquiry
            booking_date: Date and time for the booking
            stylist_id: ID of the stylist
            
        Returns:
            ID of created booking
        """
        inquiry = await self.get_inquiry(inquiry_id)
        if not inquiry:
            raise ValueError(f"Inquiry {inquiry_id} not found")
        
        if inquiry.status != InquiryStatus.APPROVED:
            raise ValueError("Can only convert approved inquiries to bookings")
        
        if not inquiry.custom_service_id:
            raise ValueError("Inquiry must have a custom service created")
        
        # Create booking
        booking_data = {
            "client_id": inquiry.client_id,
            "salon_id": inquiry.salon_id,
            "stylist_id": stylist_id,
            "service_id": inquiry.custom_service_id,
            "booking_date": booking_date,
            "status": "confirmed",
            "inquiry_id": inquiry_id,
            "created_at": datetime.utcnow()
        }
        
        result = await self.bookings_collection.insert_one(booking_data)
        
        # Update inquiry status
        await self.inquiries_collection.update_one(
            {"_id": ObjectId(inquiry_id)},
            {"$set": {
                "status": InquiryStatus.CONVERTED,
                "booking_id": str(result.inserted_id),
                "updated_at": datetime.utcnow()
            }}
        )
        
        return str(result.inserted_id)
    
    async def expire_old_inquiries(self, days: int = 7) -> int:
        """
        Expire pending inquiries older than specified days
        
        Args:
            days: Number of days after which to expire inquiries
            
        Returns:
            Number of inquiries expired
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        result = await self.inquiries_collection.update_many(
            {
                "status": InquiryStatus.PENDING,
                "created_at": {"$lt": cutoff_date}
            },
            {"$set": {
                "status": InquiryStatus.EXPIRED,
                "updated_at": datetime.utcnow()
            }}
        )
        
        # TODO: Send notification to clients about expired inquiries (Task 2.5)
        
        return result.modified_count


# Singleton instance
service_inquiry_service = ServiceInquiryService()
