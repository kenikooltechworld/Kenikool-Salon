"""
Client management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional
from bson import ObjectId
from datetime import datetime
import logging

from app.api.dependencies import get_current_user, get_tenant_id
from app.database import Database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/clients", tags=["clients"])


def get_db():
    """Get database instance"""
    return Database.get_db()


@router.get("", response_model=dict)
async def list_clients(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    search: Optional[str] = Query(None, description="Search by name, phone, or email"),
    segment: Optional[str] = Query(None, description="Filter by segment"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List all clients for tenant with optional filtering"""
    db = get_db()
    
    try:
        filters = {"tenant_id": tenant_id}
        
        if search:
            filters["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"phone": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}},
            ]
        
        if segment:
            filters["segment"] = segment
        
        # Get total count
        total = db.clients.count_documents(filters)
        
        # Get paginated results
        clients = list(
            db.clients.find(filters)
            .skip(offset)
            .limit(limit)
            .sort("created_at", -1)
        )
        
        # Convert ObjectIds to strings
        for client in clients:
            client["id"] = str(client["_id"])
            del client["_id"]
        
        return {
            "items": clients,
            "page_info": {
                "total_count": total,
                "offset": offset,
                "limit": limit,
            }
        }
    except Exception as e:
        logger.error(f"Error listing clients: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Birthday and Photos Endpoints (must come before /{client_id} routes)
# ============================================================================

@router.get("/birthdays/upcoming", response_model=dict)
async def get_upcoming_birthdays(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    days_ahead: int = Query(7, ge=1, le=365),
):
    """Get clients with upcoming birthdays"""
    db = get_db()
    
    try:
        from datetime import timedelta
        
        # Get current date
        today = datetime.utcnow()
        future_date = today + timedelta(days=days_ahead)
        
        # Get all clients for tenant
        clients = list(db.clients.find({
            "tenant_id": tenant_id,
            "birthday": {"$exists": True, "$ne": None}
        }))
        
        upcoming_birthdays = []
        
        for client in clients:
            try:
                birthday_str = client.get("birthday")
                if not birthday_str:
                    continue
                
                # Parse birthday (assuming format YYYY-MM-DD or similar)
                if isinstance(birthday_str, str):
                    birthday_date = datetime.strptime(birthday_str, "%Y-%m-%d")
                else:
                    birthday_date = birthday_str
                
                # Get this year's birthday
                this_year_birthday = birthday_date.replace(year=today.year)
                
                # If birthday has already passed this year, check next year
                if this_year_birthday < today:
                    this_year_birthday = birthday_date.replace(year=today.year + 1)
                
                # Check if birthday is within the range
                if today <= this_year_birthday <= future_date:
                    days_until = (this_year_birthday - today).days
                    upcoming_birthdays.append({
                        "id": str(client["_id"]),
                        "name": client.get("name"),
                        "phone": client.get("phone"),
                        "email": client.get("email"),
                        "birthday": birthday_str,
                        "days_until": days_until,
                        "birthday_date": this_year_birthday.isoformat(),
                    })
            except Exception as e:
                logger.warning(f"Error processing birthday for client {client.get('_id')}: {e}")
                continue
        
        # Sort by days_until
        upcoming_birthdays.sort(key=lambda x: x["days_until"])
        
        return {
            "upcoming_birthdays": upcoming_birthdays,
            "total_count": len(upcoming_birthdays),
            "days_ahead": days_ahead,
        }
    except Exception as e:
        logger.error(f"Error getting upcoming birthdays: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{client_id}", response_model=dict)
async def get_client(
    client_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get a single client by ID"""
    db = get_db()
    
    try:
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        client["id"] = str(client["_id"])
        del client["_id"]
        return client
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting client {client_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{client_id}/photos", response_model=dict)
async def get_client_photos(
    client_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get photos for a client"""
    db = get_db()
    
    try:
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Get photos
        photos = client.get("photos", [])
        
        return {
            "client_id": client_id,
            "photos": photos,
            "total_count": len(photos),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting client photos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{client_id}/photos", response_model=dict, status_code=status.HTTP_201_CREATED)
async def add_client_photo(
    client_id: str,
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Add a photo to a client"""
    db = get_db()
    
    try:
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        photo_url = data.get("photo_url")
        caption = data.get("caption")
        
        if not photo_url:
            raise HTTPException(status_code=400, detail="photo_url is required")
        
        # Create photo record
        photo = {
            "url": photo_url,
            "caption": caption,
            "uploaded_at": datetime.utcnow(),
        }
        
        # Add photo to client
        result = db.clients.find_one_and_update(
            {"_id": ObjectId(client_id), "tenant_id": tenant_id},
            {
                "$push": {"photos": photo},
                "$set": {"updated_at": datetime.utcnow()}
            },
            return_document=True,
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Client not found")
        
        return {
            "success": True,
            "photo": photo,
            "total_photos": len(result.get("photos", [])),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding client photo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{client_id}/photos/{photo_index}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client_photo(
    client_id: str,
    photo_index: int,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Delete a photo from a client"""
    db = get_db()
    
    try:
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        photos = client.get("photos", [])
        
        if photo_index < 0 or photo_index >= len(photos):
            raise HTTPException(status_code=400, detail="Invalid photo index")
        
        # Remove photo
        photos.pop(photo_index)
        
        # Update client
        db.clients.update_one(
            {"_id": ObjectId(client_id), "tenant_id": tenant_id},
            {
                "$set": {
                    "photos": photos,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"Deleted photo {photo_index} from client {client_id}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting client photo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_client(
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Create a new client"""
    db = get_db()
    
    try:
        # Validate required fields
        if not data.get("name") or not data.get("phone"):
            raise HTTPException(status_code=400, detail="Name and phone are required")
        
        # Create client document
        client_doc = {
            "tenant_id": tenant_id,
            "name": data.get("name"),
            "phone": data.get("phone"),
            "email": data.get("email"),
            "address": data.get("address"),
            "notes": data.get("notes"),
            "birthday": data.get("birthday"),
            "segment": data.get("segment", "regular"),
            "tags": data.get("tags", []),
            "total_visits": 0,
            "total_spent": 0,
            "photos": [],
            "preferences": data.get("preferences", {}),
            "created_at": Database.get_db().command("serverStatus")["localTime"],
            "updated_at": Database.get_db().command("serverStatus")["localTime"],
        }
        
        result = db.clients.insert_one(client_doc)
        client_doc["id"] = str(result.inserted_id)
        del client_doc["_id"]
        
        logger.info(f"Created client {result.inserted_id} for tenant {tenant_id}")
        return client_doc
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating client: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{client_id}", response_model=dict)
async def update_client(
    client_id: str,
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Update a client"""
    db = get_db()
    
    try:
        # Build update document
        update_doc = {}
        for field in ["name", "phone", "email", "address", "notes", "birthday", "segment", "tags", "preferences"]:
            if field in data:
                update_doc[field] = data[field]
        
        if not update_doc:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        update_doc["updated_at"] = Database.get_db().command("serverStatus")["localTime"]
        
        result = db.clients.find_one_and_update(
            {"_id": ObjectId(client_id), "tenant_id": tenant_id},
            {"$set": update_doc},
            return_document=True,
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Client not found")
        
        result["id"] = str(result["_id"])
        del result["_id"]
        
        logger.info(f"Updated client {client_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating client {client_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Delete a client"""
    db = get_db()
    
    try:
        result = db.clients.delete_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Client not found")
        
        logger.info(f"Deleted client {client_id}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting client {client_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Client Detail Endpoints
# ============================================================================

@router.get("/{client_id}/referrals", response_model=dict)
async def get_client_referrals(
    client_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get referrals for a client"""
    db = get_db()
    
    try:
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Get referrals made by this client
        referrals = list(db.referrals.find({
            "referrer_id": client_id,
            "tenant_id": tenant_id,
        }))
        
        # Calculate total referral value
        total_referral_value = sum(ref.get("reward_amount", 0) for ref in referrals)
        
        # Get referred clients details
        referred_clients = []
        for ref in referrals:
            referred_id = ref.get("referred_id")
            if referred_id:
                try:
                    referred_client = db.clients.find_one({
                        "_id": ObjectId(referred_id),
                        "tenant_id": tenant_id,
                    })
                    if referred_client:
                        referred_clients.append({
                            "id": str(referred_client["_id"]),
                            "name": referred_client.get("name", "Unknown"),
                            "referral_value": ref.get("reward_amount", 0),
                        })
                except:
                    pass
        
        return {
            "referrer_id": client_id,
            "referrer_name": client.get("name", "Unknown"),
            "referred_clients": referred_clients,
            "total_referral_value": total_referral_value,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting client referrals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{client_id}/history", response_model=dict)
async def get_client_history(
    client_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get booking history for a client"""
    db = get_db()
    
    try:
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Get bookings for this client
        total = db.bookings.count_documents({
            "client_id": client_id,
            "tenant_id": tenant_id,
        })
        
        bookings = list(db.bookings.find({
            "client_id": client_id,
            "tenant_id": tenant_id,
        }).sort("booking_date", -1).skip(offset).limit(limit))
        
        return {
            "bookings": bookings,
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting client history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{client_id}/packages", response_model=dict)
async def get_client_packages(
    client_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get packages purchased by a client"""
    db = get_db()
    
    try:
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Get package purchases for this client
        packages = list(db.package_purchases.find({
            "client_id": client_id,
            "tenant_id": tenant_id,
        }))
        
        return {
            "packages": packages,
            "total": len(packages),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting client packages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{client_id}/analytics", response_model=dict)
async def get_client_analytics(
    client_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get analytics for a client"""
    db = get_db()
    
    try:
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Get booking statistics
        total_bookings = db.bookings.count_documents({
            "client_id": client_id,
            "tenant_id": tenant_id,
        })
        
        completed_bookings = db.bookings.count_documents({
            "client_id": client_id,
            "tenant_id": tenant_id,
            "status": "completed",
        })
        
        # Calculate total spent
        bookings = list(db.bookings.find({
            "client_id": client_id,
            "tenant_id": tenant_id,
        }))
        
        total_spent = sum(b.get("total_amount", 0) for b in bookings)
        
        return {
            "total_bookings": total_bookings,
            "completed_bookings": completed_bookings,
            "total_spent": total_spent,
            "average_booking_value": total_spent / total_bookings if total_bookings > 0 else 0,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting client analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{client_id}/financial", response_model=dict)
async def get_client_financial(
    client_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get financial information for a client"""
    db = get_db()
    
    try:
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Get financial data
        bookings = list(db.bookings.find({
            "client_id": client_id,
            "tenant_id": tenant_id,
        }))
        
        total_spent = sum(b.get("total_amount", 0) for b in bookings)
        total_paid = sum(b.get("amount_paid", 0) for b in bookings)
        outstanding_balance = total_spent - total_paid
        
        # Calculate additional metrics
        transaction_count = len(bookings)
        average_transaction = total_spent / transaction_count if transaction_count > 0 else 0
        tip_total = sum(b.get("tip_amount", 0) for b in bookings)
        tip_average = tip_total / transaction_count if transaction_count > 0 else 0
        
        return {
            "total_spent": total_spent,
            "total_paid": total_paid,
            "outstanding_balance": outstanding_balance,
            "payment_status": "paid" if outstanding_balance == 0 else "outstanding",
            "total_revenue": total_spent,
            "transaction_count": transaction_count,
            "average_transaction": average_transaction,
            "tip_total": tip_total,
            "tip_average": tip_average,
            "revenue_by_month": [],
            "revenue_by_service_category": {},
            "payment_method_preferences": {},
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting client financial info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{client_id}/communications", response_model=dict)
async def get_client_communications(
    client_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get communication history for a client"""
    db = get_db()
    
    try:
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Get communications (emails, SMS, etc.)
        total = db.communications.count_documents({
            "client_id": client_id,
            "tenant_id": tenant_id,
        })
        
        communications = list(db.communications.find({
            "client_id": client_id,
            "tenant_id": tenant_id,
        }).sort("created_at", -1).skip(offset).limit(limit))
        
        # Convert ObjectIds to strings
        for comm in communications:
            if "_id" in comm:
                comm["id"] = str(comm["_id"])
                del comm["_id"]
        
        return {
            "items": communications,
            "total_count": total,
            "has_more": (offset + limit) < total,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting client communications: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{client_id}/communications/stats", response_model=dict)
async def get_client_communications_stats(
    client_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get communication statistics for a client"""
    db = get_db()
    
    try:
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Get communication stats
        total_communications = db.communications.count_documents({
            "client_id": client_id,
            "tenant_id": tenant_id,
        })
        
        # Get by channel
        by_channel = {}
        for channel in ["sms", "email", "whatsapp"]:
            by_channel[channel] = db.communications.count_documents({
                "client_id": client_id,
                "tenant_id": tenant_id,
                "channel": channel,
            })
        
        # Get by status
        by_status = {}
        for status in ["pending", "sent", "delivered", "read", "failed"]:
            by_status[status] = db.communications.count_documents({
                "client_id": client_id,
                "tenant_id": tenant_id,
                "status": status,
            })
        
        # Calculate response rate (read messages / total messages)
        read_count = by_status.get("read", 0)
        response_rate = (read_count / total_communications * 100) if total_communications > 0 else 0
        
        return {
            "total_communications": total_communications,
            "by_channel": by_channel,
            "by_status": by_status,
            "response_rate": round(response_rate, 2),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting client communications stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{client_id}/reviews", response_model=dict)
async def get_client_reviews(
    client_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get reviews for a client"""
    db = get_db()
    
    try:
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Get reviews for this client
        total = db.reviews.count_documents({
            "client_id": client_id,
            "tenant_id": tenant_id,
        })
        
        reviews = list(db.reviews.find({
            "client_id": client_id,
            "tenant_id": tenant_id,
        }).sort("created_at", -1).skip(offset).limit(limit))
        
        return {
            "reviews": reviews,
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting client reviews: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{client_id}/reviews/stats", response_model=dict)
async def get_client_reviews_stats(
    client_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get review statistics for a client"""
    db = get_db()
    
    try:
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Get review stats
        total_reviews = db.reviews.count_documents({
            "client_id": client_id,
            "tenant_id": tenant_id,
        })
        
        reviews = list(db.reviews.find({
            "client_id": client_id,
            "tenant_id": tenant_id,
        }))
        
        average_rating = 0.0
        if reviews:
            total_rating = sum(r.get("rating", 0) for r in reviews)
            average_rating = total_rating / len(reviews)
        
        return {
            "total_reviews": total_reviews,
            "average_rating": average_rating,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting client reviews stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{client_id}/relationships", response_model=dict)
async def get_client_relationships(
    client_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get relationship information for a client"""
    db = get_db()
    
    try:
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Get relationship data
        return {
            "client_id": client_id,
            "total_visits": client.get("total_visits", 0),
            "total_spent": client.get("total_spent", 0),
            "last_visit_date": client.get("last_visit_date"),
            "preferred_stylist": client.get("preferred_stylist"),
            "preferred_service": client.get("preferred_service"),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting client relationships: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{client_id}/send-communication", response_model=dict)
async def send_client_communication(
    client_id: str,
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Send communication to a client"""
    from app.services.termii_service import send_sms, send_whatsapp
    from app.services.sms_credit_service import SMSCreditService
    
    db = get_db()
    
    try:
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        channel = data.get("channel", "sms")
        content = data.get("content")
        subject = data.get("subject")
        
        if not content:
            raise HTTPException(status_code=400, detail="Content is required")
        
        # Check SMS credits for SMS/WhatsApp
        if channel in ["sms", "whatsapp"]:
            if not SMSCreditService.check_sufficient_credits(tenant_id, 1):
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient SMS credits. Available: {SMSCreditService.get_balance(tenant_id)['current_balance']}"
                )
        
        # Get recipient
        recipient = None
        if channel == "sms":
            recipient = client.get("phone")
        elif channel == "whatsapp":
            recipient = client.get("phone")
        elif channel == "email":
            recipient = client.get("email")
        
        if not recipient:
            raise HTTPException(status_code=400, detail=f"Client has no {channel} contact information")
        
        # Send message
        sent_successfully = False
        error_message = None
        
        try:
            if channel == "sms":
                sent_successfully = await send_sms(recipient, content)
            elif channel == "whatsapp":
                sent_successfully = await send_whatsapp(recipient, content)
            elif channel == "email":
                # Email sending would go here
                sent_successfully = True
        except Exception as e:
            error_message = str(e)
            logger.error(f"Error sending {channel} message: {e}")
        
        # Create communication record
        communication = {
            "client_id": client_id,
            "tenant_id": tenant_id,
            "channel": channel,
            "direction": "outbound",
            "message_type": "manual",
            "subject": subject,
            "content": content,
            "recipient": recipient,
            "status": "sent" if sent_successfully else "failed",
            "error_message": error_message,
            "sent_at": datetime.utcnow() if sent_successfully else None,
            "created_at": datetime.utcnow(),
        }
        
        result = db.communications.insert_one(communication)
        communication["id"] = str(result.inserted_id)
        del communication["_id"]
        
        # Deduct SMS credits if sent successfully
        if sent_successfully and channel in ["sms", "whatsapp"]:
            SMSCreditService.deduct_credits(
                tenant_id,
                1,
                "manual_send",
                reference_id=str(result.inserted_id)
            )
        
        if not sent_successfully:
            raise HTTPException(status_code=500, detail=f"Failed to send {channel} message: {error_message}")
        
        return communication
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending communication: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{client_id}/request-review", response_model=dict)
async def request_client_review(
    client_id: str,
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Request a review from a client"""
    db = get_db()
    
    try:
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        channel = data.get("channel", "email")
        
        # Create review request record
        review_request = {
            "client_id": client_id,
            "tenant_id": tenant_id,
            "channel": channel,
            "status": "sent",
            "sent_at": datetime.utcnow(),
            "created_at": datetime.utcnow(),
        }
        
        result = db.review_requests.insert_one(review_request)
        review_request["id"] = str(result.inserted_id)
        del review_request["_id"]
        
        return review_request
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error requesting review: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{client_id}/activity", response_model=dict)
async def get_client_activity(
    client_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get activity timeline for a client"""
    db = get_db()
    
    try:
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Aggregate activity from multiple sources
        activities = []
        
        # Get bookings
        bookings = list(db.bookings.find({
            "client_id": client_id,
            "tenant_id": tenant_id,
        }).sort("booking_date", -1).limit(limit))
        
        for booking in bookings:
            activities.append({
                "id": str(booking["_id"]),
                "type": "booking",
                "title": f"Booking: {booking.get('service_name', 'Service')}",
                "description": f"Status: {booking.get('status', 'pending')}",
                "timestamp": booking.get("booking_date"),
                "metadata": {
                    "booking_id": str(booking["_id"]),
                    "service": booking.get("service_name"),
                    "stylist": booking.get("stylist_name"),
                    "status": booking.get("status"),
                }
            })
        
        # Get communications
        communications = list(db.communications.find({
            "client_id": client_id,
            "tenant_id": tenant_id,
        }).sort("created_at", -1).limit(limit))
        
        for comm in communications:
            activities.append({
                "id": str(comm["_id"]),
                "type": "communication",
                "title": f"Communication: {comm.get('channel', 'unknown').upper()}",
                "description": comm.get("content", "")[:100],
                "timestamp": comm.get("created_at"),
                "metadata": {
                    "channel": comm.get("channel"),
                    "status": comm.get("status"),
                }
            })
        
        # Get reviews
        reviews = list(db.reviews.find({
            "client_id": client_id,
            "tenant_id": tenant_id,
        }).sort("created_at", -1).limit(limit))
        
        for review in reviews:
            activities.append({
                "id": str(review["_id"]),
                "type": "review",
                "title": f"Review: {review.get('rating', 0)} stars",
                "description": review.get("comment", "")[:100],
                "timestamp": review.get("created_at"),
                "metadata": {
                    "rating": review.get("rating"),
                    "service": review.get("service_name"),
                }
            })
        
        # Sort by timestamp descending
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Apply pagination
        total = len(activities)
        activities = activities[offset:offset + limit]
        
        return {
            "activities": activities,
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting client activity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Client Communication Endpoints
# ============================================================================

@router.post("/{client_id}/communications", response_model=dict, status_code=status.HTTP_201_CREATED)
async def send_client_communication(
    client_id: str,
    channel: str = Query(..., description="sms, email, or whatsapp"),
    content: str = Query(..., description="Message content"),
    subject: Optional[str] = Query(None, description="Email subject"),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Send communication to client"""
    db = get_db()
    
    try:
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Validate channel
        if channel not in ["sms", "email", "whatsapp"]:
            raise HTTPException(status_code=400, detail="Invalid channel")
        
        # Get recipient based on channel
        recipient = None
        if channel == "sms":
            recipient = client.get("phone")
        elif channel == "email":
            recipient = client.get("email")
        elif channel == "whatsapp":
            recipient = client.get("phone")
        
        if not recipient:
            raise HTTPException(status_code=400, detail=f"Client has no {channel} contact information")
        
        # Create communication record
        communication = {
            "client_id": client_id,
            "tenant_id": tenant_id,
            "channel": channel,
            "direction": "outbound",
            "message_type": "manual",
            "subject": subject,
            "content": content,
            "recipient": recipient,
            "status": "sent",
            "sent_by": current_user.get("id"),
            "created_at": datetime.utcnow(),
        }
        
        result = db.communications.insert_one(communication)
        communication["id"] = str(result.inserted_id)
        del communication["_id"]
        
        logger.info(f"Sent {channel} communication to client {client_id}")
        return {
            "success": True,
            "communication_id": communication["id"],
            "status": "sent",
            "channel": channel,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending communication: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Client Review Request Endpoints
# ============================================================================

@router.post("/{client_id}/reviews/request", response_model=dict, status_code=status.HTTP_201_CREATED)
async def request_client_review(
    client_id: str,
    channel: str = Query(..., description="sms, email, or whatsapp"),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Request review from client"""
    db = get_db()
    
    try:
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Validate channel
        if channel not in ["sms", "email", "whatsapp"]:
            raise HTTPException(status_code=400, detail="Invalid channel")
        
        # Get recipient
        recipient = None
        if channel == "sms":
            recipient = client.get("phone")
        elif channel == "email":
            recipient = client.get("email")
        elif channel == "whatsapp":
            recipient = client.get("phone")
        
        if not recipient:
            raise HTTPException(status_code=400, detail=f"Client has no {channel} contact information")
        
        # Create review request record
        review_request = {
            "client_id": client_id,
            "tenant_id": tenant_id,
            "channel": channel,
            "recipient": recipient,
            "status": "sent",
            "sent_by": current_user.get("id"),
            "created_at": datetime.utcnow(),
        }
        
        result = db.review_requests.insert_one(review_request)
        
        logger.info(f"Requested review from client {client_id} via {channel}")
        return {
            "success": True,
            "request_id": str(result.inserted_id),
            "status": "sent",
            "channel": channel,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error requesting review: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Client Activity Timeline Endpoints
# ============================================================================

@router.get("/{client_id}/activity", response_model=dict)
async def get_client_activity(
    client_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get client activity timeline"""
    db = get_db()
    
    try:
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Get activity events (bookings, communications, reviews, etc.)
        activities = []
        
        # Get bookings
        bookings = list(db.bookings.find({
            "client_id": client_id,
            "tenant_id": tenant_id,
        }).sort("booking_date", -1).limit(limit))
        
        for booking in bookings:
            activities.append({
                "type": "booking",
                "title": f"Booking: {booking.get('service_name', 'Service')}",
                "description": f"Status: {booking.get('status', 'pending')}",
                "timestamp": booking.get("booking_date"),
                "data": booking,
            })
        
        # Get communications
        communications = list(db.communications.find({
            "client_id": client_id,
            "tenant_id": tenant_id,
        }).sort("created_at", -1).limit(limit))
        
        for comm in communications:
            activities.append({
                "type": "communication",
                "title": f"Communication: {comm.get('channel', 'unknown').upper()}",
                "description": comm.get("content", "")[:100],
                "timestamp": comm.get("created_at"),
                "data": comm,
            })
        
        # Get reviews
        reviews = list(db.reviews.find({
            "client_id": client_id,
            "tenant_id": tenant_id,
        }).sort("created_at", -1).limit(limit))
        
        for review in reviews:
            activities.append({
                "type": "review",
                "title": f"Review: {review.get('rating', 0)} stars",
                "description": review.get("comment", "")[:100],
                "timestamp": review.get("created_at"),
                "data": review,
            })
        
        # Sort by timestamp
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        activities = activities[:limit]
        
        return {
            "client_id": client_id,
            "activities": activities,
            "total_count": len(activities),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting client activity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Client Document Endpoints
# ============================================================================

@router.post("/{client_id}/documents", response_model=dict, status_code=status.HTTP_201_CREATED)
async def upload_client_document(
    client_id: str,
    document_type: str = Query(..., description="Type of document"),
    file_url: str = Query(..., description="URL of uploaded file"),
    description: Optional[str] = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Upload client document"""
    db = get_db()
    
    try:
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Create document record
        document = {
            "client_id": client_id,
            "tenant_id": tenant_id,
            "document_type": document_type,
            "file_url": file_url,
            "description": description,
            "uploaded_by": current_user.get("id"),
            "created_at": datetime.utcnow(),
        }
        
        result = db.client_documents.insert_one(document)
        document["id"] = str(result.inserted_id)
        del document["_id"]
        
        logger.info(f"Uploaded document for client {client_id}")
        return {
            "success": True,
            "document_id": document["id"],
            "document": document,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{client_id}/documents", response_model=dict)
async def list_client_documents(
    client_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    document_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List client documents"""
    db = get_db()
    
    try:
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Build filters
        filters = {
            "client_id": client_id,
            "tenant_id": tenant_id,
        }
        if document_type:
            filters["document_type"] = document_type
        
        # Get total count
        total = db.client_documents.count_documents(filters)
        
        # Get documents
        documents = list(db.client_documents.find(filters)
            .sort("created_at", -1)
            .skip(offset)
            .limit(limit))
        
        # Convert ObjectIds to strings
        for doc in documents:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
        
        return {
            "documents": documents,
            "total_count": total,
            "has_more": (offset + limit) < total,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{client_id}/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client_document(
    client_id: str,
    doc_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Delete client document"""
    db = get_db()
    
    try:
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Delete document
        result = db.client_documents.delete_one({
            "_id": ObjectId(doc_id),
            "client_id": client_id,
            "tenant_id": tenant_id,
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Document not found")
        
        logger.info(f"Deleted document {doc_id} for client {client_id}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Client Privacy/GDPR Endpoints
# ============================================================================

@router.post("/{client_id}/privacy/export", response_model=dict, status_code=status.HTTP_201_CREATED)
async def export_client_data(
    client_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Export client data (GDPR)"""
    db = get_db()
    
    try:
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Collect all client data
        export_data = {
            "client": client,
            "bookings": list(db.bookings.find({"client_id": client_id, "tenant_id": tenant_id})),
            "communications": list(db.communications.find({"client_id": client_id, "tenant_id": tenant_id})),
            "reviews": list(db.reviews.find({"client_id": client_id, "tenant_id": tenant_id})),
            "loyalty": db.loyalty_accounts.find_one({"client_id": client_id, "tenant_id": tenant_id}),
            "documents": list(db.client_documents.find({"client_id": client_id, "tenant_id": tenant_id})),
        }
        
        # Create export record
        export_record = {
            "client_id": client_id,
            "tenant_id": tenant_id,
            "export_type": "full",
            "status": "completed",
            "data_size": len(str(export_data)),
            "requested_by": current_user.get("id"),
            "created_at": datetime.utcnow(),
        }
        
        result = db.data_exports.insert_one(export_record)
        
        logger.info(f"Exported data for client {client_id}")
        return {
            "success": True,
            "export_id": str(result.inserted_id),
            "status": "completed",
            "data_size": export_record["data_size"],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting client data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{client_id}/privacy/delete", response_model=dict, status_code=status.HTTP_200_OK)
async def delete_client_data(
    client_id: str,
    confirm: bool = Query(False, description="Confirmation to delete"),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Delete client data (GDPR)"""
    db = get_db()
    
    try:
        if not confirm:
            raise HTTPException(status_code=400, detail="Deletion must be confirmed")
        
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Delete all client data
        db.clients.delete_one({"_id": ObjectId(client_id), "tenant_id": tenant_id})
        db.bookings.delete_many({"client_id": client_id, "tenant_id": tenant_id})
        db.communications.delete_many({"client_id": client_id, "tenant_id": tenant_id})
        db.reviews.delete_many({"client_id": client_id, "tenant_id": tenant_id})
        db.loyalty_accounts.delete_many({"client_id": client_id, "tenant_id": tenant_id})
        db.client_documents.delete_many({"client_id": client_id, "tenant_id": tenant_id})
        
        # Create deletion record for audit
        deletion_record = {
            "client_id": client_id,
            "tenant_id": tenant_id,
            "deletion_type": "full",
            "status": "completed",
            "deleted_by": current_user.get("id"),
            "created_at": datetime.utcnow(),
        }
        
        db.data_deletions.insert_one(deletion_record)
        
        logger.info(f"Deleted all data for client {client_id}")
        return {
            "success": True,
            "status": "completed",
            "message": "Client data has been permanently deleted",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting client data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Client Notification Preferences Endpoints
# ============================================================================

@router.get("/{client_id}/notifications", response_model=dict)
async def get_notification_preferences(
    client_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get notification preferences for a client"""
    db = get_db()
    
    try:
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Get or create notification preferences
        prefs = db.notification_preferences.find_one({
            "client_id": client_id,
            "tenant_id": tenant_id,
        })
        
        if not prefs:
            prefs = {
                "client_id": client_id,
                "tenant_id": tenant_id,
                "email_notifications": True,
                "sms_notifications": True,
                "whatsapp_notifications": True,
                "appointment_reminders": True,
                "promotional_emails": True,
                "loyalty_updates": True,
                "review_requests": True,
                "marketing_consent": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            db.notification_preferences.insert_one(prefs)
        
        prefs["id"] = str(prefs["_id"])
        del prefs["_id"]
        
        return prefs
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting notification preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{client_id}/notifications", response_model=dict)
async def update_notification_preferences(
    client_id: str,
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Update notification preferences for a client"""
    db = get_db()
    
    try:
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Build update document
        update_doc = {}
        for field in [
            "email_notifications",
            "sms_notifications",
            "whatsapp_notifications",
            "appointment_reminders",
            "promotional_emails",
            "loyalty_updates",
            "review_requests",
            "marketing_consent",
        ]:
            if field in data:
                update_doc[field] = data[field]
        
        if not update_doc:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        update_doc["updated_at"] = datetime.utcnow()
        
        # Update or create preferences
        result = db.notification_preferences.find_one_and_update(
            {"client_id": client_id, "tenant_id": tenant_id},
            {"$set": update_doc},
            upsert=True,
            return_document=True,
        )
        
        result["id"] = str(result["_id"])
        del result["_id"]
        
        logger.info(f"Updated notification preferences for client {client_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating notification preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Client At-Risk and Retention Endpoints
# ============================================================================

@router.get("/at-risk", response_model=dict)
async def get_at_risk_clients(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    days_inactive: int = Query(90, ge=1, le=365),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    """Get clients at risk of churn (inactive for specified days)"""
    db = get_db()
    
    try:
        from datetime import datetime, timedelta
        
        # Calculate cutoff date
        cutoff_date = datetime.utcnow() - timedelta(days=days_inactive)
        
        # Find clients with no recent bookings
        at_risk_clients = list(db.clients.find({
            "tenant_id": tenant_id,
            "$or": [
                {"last_visit_date": {"$lt": cutoff_date}},
                {"last_visit_date": {"$exists": False}},
            ]
        }).skip(offset).limit(limit))
        
        # Convert ObjectIds to strings
        for client in at_risk_clients:
            client["id"] = str(client["_id"])
            del client["_id"]
        
        total = db.clients.count_documents({
            "tenant_id": tenant_id,
            "$or": [
                {"last_visit_date": {"$lt": cutoff_date}},
                {"last_visit_date": {"$exists": False}},
            ]
        })
        
        return {
            "clients": at_risk_clients,
            "total_count": total,
            "days_inactive": days_inactive,
            "has_more": (offset + limit) < total,
        }
    except Exception as e:
        logger.error(f"Error getting at-risk clients: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/winback-campaign", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_winback_campaign(
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Create a winback campaign for at-risk clients"""
    db = get_db()
    
    try:
        client_ids = data.get("client_ids", [])
        channel = data.get("channel", "email")
        message = data.get("message", "")
        offer = data.get("offer")
        
        if not client_ids or not message:
            raise HTTPException(status_code=400, detail="client_ids and message are required")
        
        # Create campaign record
        campaign = {
            "tenant_id": tenant_id,
            "campaign_type": "winback",
            "channel": channel,
            "message": message,
            "offer": offer,
            "client_ids": client_ids,
            "total_clients": len(client_ids),
            "status": "created",
            "created_by": current_user.get("id"),
            "created_at": datetime.utcnow(),
        }
        
        result = db.campaigns.insert_one(campaign)
        campaign["id"] = str(result.inserted_id)
        del campaign["_id"]
        
        logger.info(f"Created winback campaign for {len(client_ids)} clients")
        return {
            "success": True,
            "campaign_id": campaign["id"],
            "campaign": campaign,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating winback campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/retention-metrics", response_model=dict)
async def get_retention_metrics(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get retention metrics for the salon"""
    db = get_db()
    
    try:
        from datetime import datetime, timedelta
        
        # Calculate metrics
        total_clients = db.clients.count_documents({"tenant_id": tenant_id})
        
        # Active clients (visited in last 90 days)
        cutoff_90 = datetime.utcnow() - timedelta(days=90)
        active_clients = db.clients.count_documents({
            "tenant_id": tenant_id,
            "last_visit_date": {"$gte": cutoff_90}
        })
        
        # At-risk clients (no visit in 90 days)
        at_risk_clients = db.clients.count_documents({
            "tenant_id": tenant_id,
            "$or": [
                {"last_visit_date": {"$lt": cutoff_90}},
                {"last_visit_date": {"$exists": False}},
            ]
        })
        
        # Churn rate
        churn_rate = (at_risk_clients / total_clients * 100) if total_clients > 0 else 0
        retention_rate = 100 - churn_rate
        
        # Average visits per client
        bookings = list(db.bookings.find({"tenant_id": tenant_id}))
        avg_visits = len(bookings) / total_clients if total_clients > 0 else 0
        
        return {
            "total_clients": total_clients,
            "active_clients": active_clients,
            "at_risk_clients": at_risk_clients,
            "churn_rate": round(churn_rate, 2),
            "retention_rate": round(retention_rate, 2),
            "average_visits_per_client": round(avg_visits, 2),
        }
    except Exception as e:
        logger.error(f"Error getting retention metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{client_id}/service-history", response_model=dict)
async def get_client_service_history(
    client_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    service_type: Optional[str] = Query(None),
    stylist_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get service history for a client"""
    db = get_db()
    
    try:
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Build filters
        filters = {
            "client_id": client_id,
            "tenant_id": tenant_id,
            "status": "completed",
        }
        
        if service_type:
            filters["service_type"] = service_type
        if stylist_id:
            filters["stylist_id"] = stylist_id
        
        # Get total count
        total = db.bookings.count_documents(filters)
        
        # Get service history
        services = list(db.bookings.find(filters)
            .sort("booking_date", -1)
            .skip(offset)
            .limit(limit))
        
        # Convert ObjectIds to strings
        for service in services:
            service["id"] = str(service["_id"])
            del service["_id"]
        
        return {
            "services": services,
            "total_count": total,
            "has_more": (offset + limit) < total,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting service history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{client_id}/link", response_model=dict, status_code=status.HTTP_201_CREATED)
async def link_client(
    client_id: str,
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Link a client to another client (e.g., family members)"""
    db = get_db()
    
    try:
        # Verify both clients exist
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        related_client_id = data.get("related_client_id")
        relationship_type = data.get("relationship_type", "family")
        notes = data.get("notes")
        
        if not related_client_id:
            raise HTTPException(status_code=400, detail="related_client_id is required")
        
        related_client = db.clients.find_one({
            "_id": ObjectId(related_client_id),
            "tenant_id": tenant_id,
        })
        
        if not related_client:
            raise HTTPException(status_code=404, detail="Related client not found")
        
        # Create relationship record
        relationship = {
            "client_id": client_id,
            "related_client_id": related_client_id,
            "tenant_id": tenant_id,
            "relationship_type": relationship_type,
            "notes": notes,
            "created_at": datetime.utcnow(),
        }
        
        result = db.client_relationships.insert_one(relationship)
        relationship["id"] = str(result.inserted_id)
        del relationship["_id"]
        
        logger.info(f"Linked client {client_id} to {related_client_id}")
        return {
            "success": True,
            "relationship_id": relationship["id"],
            "relationship": relationship,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error linking clients: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Privacy Endpoints
# ============================================================================


# ============================================================================
# Client Spending and Analytics Endpoints
# ============================================================================

@router.get("/{client_id}/spending", response_model=dict)
async def get_client_spending(
    client_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    period: str = Query("month", description="Period: day, week, month, year, all"),
):
    """Get client spending analysis with trends and predictions"""
    db = get_db()
    
    try:
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Get bookings for this client
        bookings = list(db.bookings.find({
            "client_id": client_id,
            "tenant_id": tenant_id,
        }).sort("booking_date", -1))
        
        total_spent = sum(b.get("total_amount", 0) for b in bookings)
        average_transaction = total_spent / len(bookings) if bookings else 0
        
        # Calculate spending by month
        spending_by_month = {}
        for booking in bookings:
            booking_date = booking.get("booking_date")
            if isinstance(booking_date, str):
                booking_date = datetime.fromisoformat(booking_date)
            month_key = booking_date.strftime("%Y-%m")
            spending_by_month[month_key] = spending_by_month.get(month_key, 0) + booking.get("total_amount", 0)
        
        return {
            "client_id": client_id,
            "total_spent": total_spent,
            "average_transaction": average_transaction,
            "transaction_count": len(bookings),
            "spending_by_month": spending_by_month,
            "period": period,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting client spending: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{client_id}/retention", response_model=dict)
async def get_client_retention(
    client_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get client retention metrics and churn risk"""
    db = get_db()
    
    try:
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Get bookings for this client
        bookings = list(db.bookings.find({
            "client_id": client_id,
            "tenant_id": tenant_id,
        }).sort("booking_date", -1))
        
        if not bookings:
            return {
                "client_id": client_id,
                "retention_status": "new",
                "churn_risk": "low",
                "days_since_last_visit": None,
                "visit_frequency": 0,
            }
        
        # Calculate days since last visit
        last_booking = bookings[0]
        last_booking_date = last_booking.get("booking_date")
        if isinstance(last_booking_date, str):
            last_booking_date = datetime.fromisoformat(last_booking_date)
        
        days_since_last_visit = (datetime.utcnow() - last_booking_date).days
        
        # Calculate visit frequency (visits per month)
        if len(bookings) > 1:
            first_booking_date = bookings[-1].get("booking_date")
            if isinstance(first_booking_date, str):
                first_booking_date = datetime.fromisoformat(first_booking_date)
            days_between = (last_booking_date - first_booking_date).days
            months_between = max(days_between / 30, 1)
            visit_frequency = len(bookings) / months_between
        else:
            visit_frequency = 0
        
        # Determine churn risk
        if days_since_last_visit > 90:
            churn_risk = "high"
        elif days_since_last_visit > 60:
            churn_risk = "medium"
        else:
            churn_risk = "low"
        
        return {
            "client_id": client_id,
            "retention_status": "active" if churn_risk == "low" else "at_risk",
            "churn_risk": churn_risk,
            "days_since_last_visit": days_since_last_visit,
            "visit_frequency": round(visit_frequency, 2),
            "total_visits": len(bookings),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting client retention: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Client Segmentation Endpoints
# ============================================================================

@router.get("/segments/list", response_model=dict)
async def list_client_segments(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get all client segments for tenant"""
    db = get_db()
    
    try:
        segments = list(db.client_segments.find({
            "tenant_id": tenant_id,
        }))
        
        # Convert ObjectIds to strings
        for segment in segments:
            segment["id"] = str(segment["_id"])
            del segment["_id"]
        
        return {
            "segments": segments,
            "total_count": len(segments),
        }
    except Exception as e:
        logger.error(f"Error listing client segments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/segments", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_client_segment(
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Create a new client segment"""
    db = get_db()
    
    try:
        segment_name = data.get("name")
        criteria = data.get("criteria", {})
        description = data.get("description")
        
        if not segment_name:
            raise HTTPException(status_code=400, detail="Segment name is required")
        
        segment_doc = {
            "tenant_id": tenant_id,
            "name": segment_name,
            "description": description,
            "criteria": criteria,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        result = db.client_segments.insert_one(segment_doc)
        segment_doc["id"] = str(result.inserted_id)
        del segment_doc["_id"]
        
        logger.info(f"Created client segment {result.inserted_id}")
        return segment_doc
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating client segment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/segments/{segment_id}/clients", response_model=dict)
async def get_segment_clients(
    segment_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get clients in a specific segment"""
    db = get_db()
    
    try:
        segment = db.client_segments.find_one({
            "_id": ObjectId(segment_id),
            "tenant_id": tenant_id,
        })
        
        if not segment:
            raise HTTPException(status_code=404, detail="Segment not found")
        
        # Get clients matching segment criteria
        criteria = segment.get("criteria", {})
        filters = {"tenant_id": tenant_id}
        filters.update(criteria)
        
        total = db.clients.count_documents(filters)
        clients = list(db.clients.find(filters).skip(offset).limit(limit))
        
        # Convert ObjectIds to strings
        for client in clients:
            client["id"] = str(client["_id"])
            del client["_id"]
        
        return {
            "segment_id": segment_id,
            "segment_name": segment.get("name"),
            "clients": clients,
            "total_count": total,
            "offset": offset,
            "limit": limit,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting segment clients: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Client Import/Export Endpoints
# ============================================================================

@router.get("/export", response_model=dict)
async def export_clients(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    format: str = Query("csv", description="Export format: csv or json"),
    fields: Optional[str] = Query(None, description="Comma-separated field names to export"),
):
    """Export clients to CSV or JSON format"""
    db = get_db()
    
    try:
        # Get all clients for tenant
        clients = list(db.clients.find({"tenant_id": tenant_id}))
        
        # Convert ObjectIds to strings
        for client in clients:
            client["id"] = str(client["_id"])
            del client["_id"]
        
        # Filter fields if specified
        if fields:
            field_list = [f.strip() for f in fields.split(",")]
            filtered_clients = []
            for client in clients:
                filtered_client = {k: v for k, v in client.items() if k in field_list}
                filtered_clients.append(filtered_client)
            clients = filtered_clients
        
        return {
            "format": format,
            "clients": clients,
            "total_count": len(clients),
        }
    except Exception as e:
        logger.error(f"Error exporting clients: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import", response_model=dict, status_code=status.HTTP_201_CREATED)
async def import_clients(
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Import clients from CSV or JSON data"""
    db = get_db()
    
    try:
        clients_data = data.get("clients", [])
        
        if not clients_data:
            raise HTTPException(status_code=400, detail="No clients data provided")
        
        imported_count = 0
        skipped_count = 0
        errors = []
        
        for client_data in clients_data:
            try:
                # Validate required fields
                if not client_data.get("name") or not client_data.get("phone"):
                    skipped_count += 1
                    errors.append(f"Skipped client: missing name or phone")
                    continue
                
                # Check for duplicates
                existing = db.clients.find_one({
                    "tenant_id": tenant_id,
                    "phone": client_data.get("phone"),
                })
                
                if existing:
                    skipped_count += 1
                    errors.append(f"Skipped client {client_data.get('name')}: phone already exists")
                    continue
                
                # Create client
                client_doc = {
                    "tenant_id": tenant_id,
                    "name": client_data.get("name"),
                    "phone": client_data.get("phone"),
                    "email": client_data.get("email"),
                    "address": client_data.get("address"),
                    "notes": client_data.get("notes"),
                    "birthday": client_data.get("birthday"),
                    "segment": client_data.get("segment", "regular"),
                    "tags": client_data.get("tags", []),
                    "total_visits": 0,
                    "total_spent": 0,
                    "photos": [],
                    "preferences": client_data.get("preferences", {}),
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                }
                
                result = db.clients.insert_one(client_doc)
                imported_count += 1
                logger.info(f"Imported client {result.inserted_id}")
            except Exception as e:
                skipped_count += 1
                errors.append(f"Error importing client: {str(e)}")
                continue
        
        return {
            "imported_count": imported_count,
            "skipped_count": skipped_count,
            "total_count": len(clients_data),
            "errors": errors,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing clients: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Client Survey/Feedback Endpoints
# ============================================================================

@router.get("/surveys/list", response_model=dict)
async def list_client_surveys(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get all client surveys for tenant"""
    db = get_db()
    
    try:
        surveys = list(db.client_surveys.find({
            "tenant_id": tenant_id,
        }))
        
        # Convert ObjectIds to strings
        for survey in surveys:
            survey["id"] = str(survey["_id"])
            del survey["_id"]
        
        return {
            "surveys": surveys,
            "total_count": len(surveys),
        }
    except Exception as e:
        logger.error(f"Error listing client surveys: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/surveys", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_client_survey(
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Create a new client survey"""
    db = get_db()
    
    try:
        survey_title = data.get("title")
        questions = data.get("questions", [])
        description = data.get("description")
        
        if not survey_title:
            raise HTTPException(status_code=400, detail="Survey title is required")
        
        survey_doc = {
            "tenant_id": tenant_id,
            "title": survey_title,
            "description": description,
            "questions": questions,
            "responses": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        result = db.client_surveys.insert_one(survey_doc)
        survey_doc["id"] = str(result.inserted_id)
        del survey_doc["_id"]
        
        logger.info(f"Created client survey {result.inserted_id}")
        return survey_doc
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating client survey: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{client_id}/survey-response", response_model=dict, status_code=status.HTTP_201_CREATED)
async def submit_survey_response(
    client_id: str,
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Submit a survey response for a client"""
    db = get_db()
    
    try:
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id,
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        survey_id = data.get("survey_id")
        answers = data.get("answers", {})
        rating = data.get("rating")
        
        if not survey_id:
            raise HTTPException(status_code=400, detail="survey_id is required")
        
        # Verify survey exists
        survey = db.client_surveys.find_one({
            "_id": ObjectId(survey_id),
            "tenant_id": tenant_id,
        })
        
        if not survey:
            raise HTTPException(status_code=404, detail="Survey not found")
        
        # Create response record
        response_doc = {
            "client_id": client_id,
            "survey_id": survey_id,
            "tenant_id": tenant_id,
            "answers": answers,
            "rating": rating,
            "submitted_at": datetime.utcnow(),
        }
        
        result = db.survey_responses.insert_one(response_doc)
        response_doc["id"] = str(result.inserted_id)
        del response_doc["_id"]
        
        logger.info(f"Submitted survey response {result.inserted_id}")
        return {
            "success": True,
            "response_id": response_doc["id"],
            "response": response_doc,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting survey response: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/surveys/{survey_id}/responses", response_model=dict)
async def get_survey_responses(
    survey_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get all responses for a survey"""
    db = get_db()
    
    try:
        # Verify survey exists
        survey = db.client_surveys.find_one({
            "_id": ObjectId(survey_id),
            "tenant_id": tenant_id,
        })
        
        if not survey:
            raise HTTPException(status_code=404, detail="Survey not found")
        
        # Get responses
        responses = list(db.survey_responses.find({
            "survey_id": survey_id,
            "tenant_id": tenant_id,
        }))
        
        # Convert ObjectIds to strings
        for response in responses:
            response["id"] = str(response["_id"])
            del response["_id"]
        
        # Calculate average rating
        ratings = [r.get("rating") for r in responses if r.get("rating")]
        average_rating = sum(ratings) / len(ratings) if ratings else 0
        
        return {
            "survey_id": survey_id,
            "survey_title": survey.get("title"),
            "responses": responses,
            "total_responses": len(responses),
            "average_rating": round(average_rating, 2),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting survey responses: {e}")
        raise HTTPException(status_code=500, detail=str(e))
