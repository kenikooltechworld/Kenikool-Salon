"""
Client service - Business logic layer
"""
from bson import ObjectId
from datetime import datetime
from typing import Dict, List, Optional
import logging

from app.database import Database
from app.api.exceptions import NotFoundException, ConflictException

logger = logging.getLogger(__name__)


class ClientService:
    """Client service for handling client business logic"""
    
    @staticmethod
    def get_clients(
        tenant_id: str,
        search: Optional[str] = None,
        segment: Optional[str] = None,
        tags: Optional[List[str]] = None,
        min_spent: Optional[float] = None,
        max_spent: Optional[float] = None,
        last_visit_start: Optional[datetime] = None,
        last_visit_end: Optional[datetime] = None,
        preferred_stylist_id: Optional[str] = None,
        birthday_month: Optional[int] = None,
        offset: int = 0,
        limit: int = 20
    ) -> List[Dict]:
        """
        Get list of clients for tenant with search and pagination
        
        Returns:
            List of client dicts
        """
        db = Database.get_db()
        
        # Build query
        query = {"tenant_id": tenant_id}
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"phone": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}}
            ]
        if segment:
            query["segment"] = segment
        if tags and len(tags) > 0:
            query["tags"] = {"$in": tags}
        
        # Total spent range filter
        if min_spent is not None or max_spent is not None:
            query["total_spent"] = {}
            if min_spent is not None:
                query["total_spent"]["$gte"] = min_spent
            if max_spent is not None:
                query["total_spent"]["$lte"] = max_spent
        
        # Last visit date range filter
        if last_visit_start is not None or last_visit_end is not None:
            query["last_visit_date"] = {}
            if last_visit_start is not None:
                query["last_visit_date"]["$gte"] = last_visit_start
            if last_visit_end is not None:
                query["last_visit_date"]["$lte"] = last_visit_end
        
        # Preferred stylist filter
        if preferred_stylist_id:
            query["preferences.preferred_stylist_id"] = preferred_stylist_id
        
        # Birthday month filter
        if birthday_month is not None:
            # Extract month from birthday field
            query["$expr"] = {
                "$eq": [{"$month": "$birthday"}, birthday_month]
            }
        
        clients = list(db.clients.find(query).sort("created_at", -1).skip(offset).limit(limit))
        
        return [ClientService._format_client_response(c) for c in clients]
    
    @staticmethod
    def get_client(client_id: str, tenant_id: str) -> Dict:
        """
        Get single client by ID with full details
        
        Returns:
            Dict with client data including booking history and photos
        """
        db = Database.get_db()
        
        client_doc = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id
        })
        
        if client_doc is None:
            raise NotFoundException("Client not found")
        
        return ClientService._format_client_response(client_doc)
    
    @staticmethod
    def create_client(
        tenant_id: str,
        name: str,
        phone: str,
        email: Optional[str] = None,
        address: Optional[str] = None,
        notes: Optional[str] = None,
        birthday: Optional[str] = None,
        segment: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict:
        """
        Create a new client
        
        Returns:
            Dict with created client data
        """
        db = Database.get_db()
        
        # Check if phone already exists for this tenant
        existing_client = db.clients.find_one({
            "tenant_id": tenant_id,
            "phone": phone
        })
        
        if existing_client is not None:
            raise ConflictException("A client with this phone number already exists")
        
        client_data = {
            "tenant_id": tenant_id,
            "name": name,
            "phone": phone,
            "email": email,
            "address": address,
            "notes": notes,
            "birthday": birthday,
            "segment": segment or "new",
            "tags": tags or [],
            "total_visits": 0,
            "total_spent": 0.0,
            "last_activity_date": datetime.utcnow(),
            "photos": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.clients.insert_one(client_data)
        client_id = str(result.inserted_id)
        
        logger.info(f"Client created: {client_id} for tenant: {tenant_id}")
        
        # Fetch created client
        client_doc = db.clients.find_one({"_id": ObjectId(client_id)})
        return ClientService._format_client_response(client_doc)
    
    @staticmethod
    def update_client(
        client_id: str,
        tenant_id: str,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[str] = None,
        notes: Optional[str] = None,
        birthday: Optional[str] = None,
        segment: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict:
        """
        Update a client
        
        Returns:
            Dict with updated client data
        """
        db = Database.get_db()
        
        # Check client exists and belongs to tenant
        client_doc = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id
        })
        
        if client_doc is None:
            raise NotFoundException("Client not found")
        
        # If phone is being updated, check uniqueness
        if phone and phone != client_doc.get("phone"):
            existing_client = db.clients.find_one({
                "tenant_id": tenant_id,
                "phone": phone,
                "_id": {"$ne": ObjectId(client_id)}
            })
            
            if existing_client is not None:
                raise ConflictException("A client with this phone number already exists")
        
        # Build update data
        update_data = {
            "updated_at": datetime.utcnow(),
            "last_activity_date": datetime.utcnow()
        }
        
        if name is not None:
            update_data["name"] = name
        if phone is not None:
            update_data["phone"] = phone
        if email is not None:
            update_data["email"] = email
        if address is not None:
            update_data["address"] = address
        if notes is not None:
            update_data["notes"] = notes
        if birthday is not None:
            update_data["birthday"] = birthday
        if segment is not None:
            update_data["segment"] = segment
        if tags is not None:
            update_data["tags"] = tags
        
        # Update client
        db.clients.update_one(
            {"_id": ObjectId(client_id)},
            {"$set": update_data}
        )
        
        logger.info(f"Client updated: {client_id}")
        
        # Fetch updated client
        client_doc = db.clients.find_one({"_id": ObjectId(client_id)})
        return ClientService._format_client_response(client_doc)
    
    @staticmethod
    async def upload_client_photo(
        client_id: str,
        tenant_id: str,
        file_bytes: bytes,
        photo_type: str,
        description: Optional[str] = None
    ) -> Dict:
        """
        Upload client photo (before/after)
        
        Returns:
            Dict with updated client data
        """
        from app.services.cloudinary_service import upload_image
        
        db = Database.get_db()
        
        # Check client exists and belongs to tenant
        client_doc = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id
        })
        
        if client_doc is None:
            raise NotFoundException("Client not found")
        
        # Upload to Cloudinary
        photo_url = await upload_image(
            file_bytes,
            folder=f"salons/{tenant_id}/clients/{client_id}",
            public_id=f"{photo_type}_{datetime.utcnow().timestamp()}"
        )
        
        # Add photo to client
        photo_data = {
            "photo_url": photo_url,
            "photo_type": photo_type,
            "description": description,
            "uploaded_at": datetime.utcnow()
        }
        
        db.clients.update_one(
            {"_id": ObjectId(client_id)},
            {
                "$push": {"photos": photo_data},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        logger.info(f"Photo uploaded for client: {client_id}")
        
        # Fetch updated client
        client_doc = db.clients.find_one({"_id": ObjectId(client_id)})
        return ClientService._format_client_response(client_doc)
    
    @staticmethod
    def update_preferences(
        client_id: str,
        tenant_id: str,
        preferred_stylist_id: Optional[str] = None,
        preferred_services: Optional[List[str]] = None,
        preferred_products: Optional[List[str]] = None,
        communication_channel: Optional[str] = None,
        appointment_reminders: Optional[bool] = None,
        marketing_consent: Optional[bool] = None
    ) -> Dict:
        """
        Update client preferences
        
        Returns:
            Dict with updated client data
        """
        db = Database.get_db()
        
        # Check client exists and belongs to tenant
        client_doc = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id
        })
        
        if client_doc is None:
            raise NotFoundException("Client not found")
        
        # Build preferences update
        preferences = client_doc.get("preferences", {})
        
        if preferred_stylist_id is not None:
            preferences["preferred_stylist_id"] = preferred_stylist_id
        if preferred_services is not None:
            preferences["preferred_services"] = preferred_services
        if preferred_products is not None:
            preferences["preferred_products"] = preferred_products
        if communication_channel is not None:
            preferences["communication_channel"] = communication_channel
        if appointment_reminders is not None:
            preferences["appointment_reminders"] = appointment_reminders
        if marketing_consent is not None:
            preferences["marketing_consent"] = marketing_consent
        
        # Update client
        db.clients.update_one(
            {"_id": ObjectId(client_id)},
            {
                "$set": {
                    "preferences": preferences,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"Client preferences updated: {client_id}")
        
        # Fetch updated client
        client_doc = db.clients.find_one({"_id": ObjectId(client_id)})
        return ClientService._format_client_response(client_doc)
    
    @staticmethod
    def _format_client_response(client_doc: Dict) -> Dict:
        """Format client document for response"""
        photos = []
        for photo in client_doc.get("photos", []):
            photos.append({
                "photo_url": photo["photo_url"],
                "photo_type": photo["photo_type"],
                "description": photo.get("description"),
                "uploaded_at": photo["uploaded_at"]
            })
        
        preferences = client_doc.get("preferences")
        if preferences:
            preferences = {
                "preferred_stylist_id": preferences.get("preferred_stylist_id"),
                "preferred_services": preferences.get("preferred_services", []),
                "preferred_products": preferences.get("preferred_products", []),
                "communication_channel": preferences.get("communication_channel"),
                "appointment_reminders": preferences.get("appointment_reminders", True),
                "marketing_consent": preferences.get("marketing_consent", False)
            }
        
        return {
            "id": str(client_doc["_id"]),
            "tenant_id": client_doc["tenant_id"],
            "name": client_doc["name"],
            "phone": client_doc["phone"],
            "email": client_doc.get("email"),
            "address": client_doc.get("address"),
            "notes": client_doc.get("notes"),
            "birthday": client_doc.get("birthday"),
            "segment": client_doc.get("segment", "new"),
            "tags": client_doc.get("tags", []),
            "total_visits": client_doc.get("total_visits", 0),
            "total_spent": client_doc.get("total_spent", 0.0),
            "last_visit_date": client_doc.get("last_visit_date"),
            "last_activity_date": client_doc.get("last_activity_date"),
            "photos": photos,
            "preferences": preferences,
            "created_at": client_doc["created_at"],
            "updated_at": client_doc["updated_at"]
        }


# Singleton instance
client_service = ClientService()
