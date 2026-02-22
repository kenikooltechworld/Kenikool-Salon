"""
Family accounts API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional
from bson import ObjectId
import logging

from app.api.dependencies import get_current_user, get_tenant_id
from app.database import Database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/family-accounts", tags=["family-accounts"])


def get_db():
    """Get database instance"""
    return Database.get_db()


@router.get("", response_model=dict)
async def list_family_accounts(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List all family accounts for tenant"""
    db = get_db()
    
    try:
        # Get total count
        total = db.family_accounts.count_documents({"tenant_id": tenant_id})
        
        # Get paginated results
        accounts = list(db.family_accounts.find(
            {"tenant_id": tenant_id}
        ).skip(offset).limit(limit).sort("created_at", -1))
        
        return {
            "accounts": accounts,
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    except Exception as e:
        logger.error(f"Error listing family accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{account_id}", response_model=dict)
async def get_family_account(
    account_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get a specific family account"""
    db = get_db()
    
    try:
        account = db.family_accounts.find_one({
            "_id": ObjectId(account_id),
            "tenant_id": tenant_id,
        })
        
        if not account:
            raise HTTPException(status_code=404, detail="Family account not found")
        
        return account
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting family account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_family_account(
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Create a new family account"""
    db = get_db()
    
    try:
        account_doc = {
            "tenant_id": tenant_id,
            **data,
            "created_at": __import__("datetime").datetime.utcnow(),
            "updated_at": __import__("datetime").datetime.utcnow(),
        }
        
        result = db.family_accounts.insert_one(account_doc)
        account_doc["_id"] = result.inserted_id
        
        logger.info(f"Created family account {result.inserted_id}")
        return account_doc
    except Exception as e:
        logger.error(f"Error creating family account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_family_account(
    account_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Delete a family account"""
    db = get_db()
    
    try:
        result = db.family_accounts.delete_one({
            "_id": ObjectId(account_id),
            "tenant_id": tenant_id,
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Family account not found")
        
        logger.info(f"Deleted family account {account_id}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting family account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{account_id}/bookings", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_family_booking(
    account_id: str,
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Create a booking for a family account member"""
    db = get_db()
    
    try:
        # Verify family account exists
        account = db.family_accounts.find_one({
            "_id": ObjectId(account_id),
            "tenant_id": tenant_id,
        })
        
        if not account:
            raise HTTPException(status_code=404, detail="Family account not found")
        
        # Create booking
        booking_doc = {
            "tenant_id": tenant_id,
            "family_account_id": account_id,
            **data,
            "created_at": __import__("datetime").datetime.utcnow(),
            "updated_at": __import__("datetime").datetime.utcnow(),
        }
        
        result = db.bookings.insert_one(booking_doc)
        booking_doc["_id"] = result.inserted_id
        
        logger.info(f"Created family booking {result.inserted_id} for account {account_id}")
        return booking_doc
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating family booking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== UPDATE OPERATIONS =====

@router.put("", response_model=dict)
async def update_family_account(
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Update family account"""
    db = get_db()
    
    try:
        # Find account by primary member
        account = db.family_accounts.find_one({
            "primary_member_id": current_user.get("id"),
            "tenant_id": tenant_id,
        })
        
        if not account:
            raise HTTPException(status_code=404, detail="Family account not found")
        
        from datetime import datetime
        update_data = {k: v for k, v in data.items() if k != "_id"}
        update_data["updated_at"] = datetime.utcnow()
        
        db.family_accounts.update_one(
            {"_id": account["_id"]},
            {"$set": update_data},
        )
        
        return db.family_accounts.find_one({"_id": account["_id"]})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating family account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/notification-preferences", response_model=dict)
async def update_notification_preferences(
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Update family account notification preferences"""
    db = get_db()
    
    try:
        account = db.family_accounts.find_one({
            "primary_member_id": current_user.get("id"),
            "tenant_id": tenant_id,
        })
        
        if not account:
            raise HTTPException(status_code=404, detail="Family account not found")
        
        db.family_accounts.update_one(
            {"_id": account["_id"]},
            {"$set": {"notification_preferences": data}},
        )
        
        return db.family_accounts.find_one({"_id": account["_id"]})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating notification preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== FAMILY MEMBERS =====

@router.get("/members", response_model=list)
async def get_family_members(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get all family members"""
    db = get_db()
    
    try:
        account = db.family_accounts.find_one({
            "primary_member_id": current_user.get("id"),
            "tenant_id": tenant_id,
        })
        
        if not account:
            raise HTTPException(status_code=404, detail="Family account not found")
        
        members = list(db.family_members.find({
            "family_account_id": str(account.get("_id")),
            "tenant_id": tenant_id,
        }))
        
        return members
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting family members: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/members/{member_id}", response_model=dict)
async def get_family_member(
    member_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get family member details"""
    db = get_db()
    
    try:
        member = db.family_members.find_one({
            "_id": ObjectId(member_id),
            "tenant_id": tenant_id,
        })
        
        if not member:
            raise HTTPException(status_code=404, detail="Family member not found")
        
        return member
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting family member: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/members", response_model=dict, status_code=status.HTTP_201_CREATED)
async def add_family_member(
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Add a family member"""
    db = get_db()
    
    try:
        account = db.family_accounts.find_one({
            "primary_member_id": current_user.get("id"),
            "tenant_id": tenant_id,
        })
        
        if not account:
            raise HTTPException(status_code=404, detail="Family account not found")
        
        from datetime import datetime
        member = {
            "family_account_id": str(account.get("_id")),
            "tenant_id": tenant_id,
            "name": data.get("name"),
            "email": data.get("email"),
            "phone": data.get("phone"),
            "relationship": data.get("relationship", "other"),
            "date_of_birth": data.get("dateOfBirth"),
            "is_active": True,
            "joined_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        result = db.family_members.insert_one(member)
        member["_id"] = result.inserted_id
        
        db.family_accounts.update_one(
            {"_id": account["_id"]},
            {"$inc": {"member_count": 1}},
        )
        
        return member
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding family member: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/members/{member_id}", response_model=dict)
async def update_family_member(
    member_id: str,
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Update family member"""
    db = get_db()
    
    try:
        member = db.family_members.find_one({
            "_id": ObjectId(member_id),
            "tenant_id": tenant_id,
        })
        
        if not member:
            raise HTTPException(status_code=404, detail="Family member not found")
        
        from datetime import datetime
        update_data = {k: v for k, v in data.items() if k != "_id"}
        update_data["updated_at"] = datetime.utcnow()
        
        db.family_members.update_one(
            {"_id": ObjectId(member_id)},
            {"$set": update_data},
        )
        
        return db.family_members.find_one({"_id": ObjectId(member_id)})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating family member: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_family_member(
    member_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Remove family member"""
    db = get_db()
    
    try:
        member = db.family_members.find_one({
            "_id": ObjectId(member_id),
            "tenant_id": tenant_id,
        })
        
        if not member:
            raise HTTPException(status_code=404, detail="Family member not found")
        
        db.family_members.delete_one({"_id": ObjectId(member_id)})
        
        db.family_accounts.update_one(
            {"_id": ObjectId(member.get("family_account_id"))},
            {"$inc": {"member_count": -1}},
        )
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing family member: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/members/invite", response_model=dict, status_code=status.HTTP_201_CREATED)
async def invite_family_member(
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Invite family member"""
    db = get_db()
    
    try:
        account = db.family_accounts.find_one({
            "primary_member_id": current_user.get("id"),
            "tenant_id": tenant_id,
        })
        
        if not account:
            raise HTTPException(status_code=404, detail="Family account not found")
        
        from datetime import datetime
        invitation = {
            "family_account_id": str(account.get("_id")),
            "tenant_id": tenant_id,
            "email": data.get("email"),
            "relationship": data.get("relationship"),
            "message": data.get("message"),
            "status": "pending",
            "created_at": datetime.utcnow(),
        }
        
        result = db.family_invitations.insert_one(invitation)
        invitation["_id"] = result.inserted_id
        
        return invitation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inviting family member: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== MEMBER PERMISSIONS =====

@router.get("/members/{member_id}/permissions", response_model=dict)
async def get_member_permissions(
    member_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get member permissions"""
    db = get_db()
    
    try:
        permissions = db.family_permissions.find_one({
            "member_id": member_id,
            "tenant_id": tenant_id,
        })
        
        if not permissions:
            permissions = {
                "member_id": member_id,
                "tenant_id": tenant_id,
                "can_book": True,
                "can_manage_members": False,
                "can_view_analytics": False,
                "can_manage_payments": False,
            }
        
        return permissions
    except Exception as e:
        logger.error(f"Error getting member permissions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/members/{member_id}/permissions", response_model=dict)
async def update_member_permissions(
    member_id: str,
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Update member permissions"""
    db = get_db()
    
    try:
        permissions_doc = {
            "member_id": member_id,
            "tenant_id": tenant_id,
            **data,
        }
        
        db.family_permissions.update_one(
            {"member_id": member_id, "tenant_id": tenant_id},
            {"$set": permissions_doc},
            upsert=True,
        )
        
        return db.family_permissions.find_one({
            "member_id": member_id,
            "tenant_id": tenant_id,
        })
    except Exception as e:
        logger.error(f"Error updating member permissions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/permissions", response_model=dict)
async def get_all_member_permissions(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get all member permissions"""
    db = get_db()
    
    try:
        account = db.family_accounts.find_one({
            "primary_member_id": current_user.get("id"),
            "tenant_id": tenant_id,
        })
        
        if not account:
            raise HTTPException(status_code=404, detail="Family account not found")
        
        permissions_list = list(db.family_permissions.find({
            "tenant_id": tenant_id,
        }))
        
        return {str(p.get("member_id")): p for p in permissions_list}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting all member permissions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== SHARED LOYALTY =====

@router.get("/loyalty-pool", response_model=dict)
async def get_shared_loyalty_pool(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get shared loyalty pool"""
    db = get_db()
    
    try:
        account = db.family_accounts.find_one({
            "primary_member_id": current_user.get("id"),
            "tenant_id": tenant_id,
        })
        
        if not account:
            raise HTTPException(status_code=404, detail="Family account not found")
        
        pool = db.family_loyalty_pools.find_one({
            "family_account_id": str(account.get("_id")),
            "tenant_id": tenant_id,
        })
        
        if not pool:
            pool = {
                "family_account_id": str(account.get("_id")),
                "tenant_id": tenant_id,
                "total_points": 0,
                "member_contributions": {},
            }
        
        return pool
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting shared loyalty pool: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/members/{member_id}/loyalty-points", response_model=dict)
async def get_member_loyalty_points(
    member_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get member loyalty points in pool"""
    db = get_db()
    
    try:
        pool = db.family_loyalty_pools.find_one({
            "tenant_id": tenant_id,
        })
        
        if not pool:
            return {"points": 0}
        
        points = pool.get("member_contributions", {}).get(member_id, 0)
        return {"points": points}
    except Exception as e:
        logger.error(f"Error getting member loyalty points: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/loyalty-pool/transfer", response_model=dict)
async def transfer_loyalty_points(
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Transfer loyalty points between members"""
    db = get_db()
    
    try:
        from_member_id = data.get("fromMemberId")
        to_member_id = data.get("toMemberId")
        points = data.get("points", 0)
        
        account = db.family_accounts.find_one({
            "primary_member_id": current_user.get("id"),
            "tenant_id": tenant_id,
        })
        
        if not account:
            raise HTTPException(status_code=404, detail="Family account not found")
        
        pool = db.family_loyalty_pools.find_one({
            "family_account_id": str(account.get("_id")),
            "tenant_id": tenant_id,
        })
        
        if not pool:
            raise HTTPException(status_code=404, detail="Loyalty pool not found")
        
        from_points = pool.get("member_contributions", {}).get(from_member_id, 0)
        if from_points < points:
            raise HTTPException(status_code=400, detail="Insufficient points")
        
        db.family_loyalty_pools.update_one(
            {"_id": pool.get("_id")},
            {
                "$inc": {
                    f"member_contributions.{from_member_id}": -points,
                    f"member_contributions.{to_member_id}": points,
                }
            },
        )
        
        return {"success": True, "message": "Points transferred successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error transferring loyalty points: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/loyalty-pool/rewards", response_model=list)
async def get_shared_rewards(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get shared rewards"""
    db = get_db()
    
    try:
        rewards = list(db.loyalty_rewards.find({
            "tenant_id": tenant_id,
            "is_shared": True,
        }))
        
        return rewards
    except Exception as e:
        logger.error(f"Error getting shared rewards: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== FAMILY BOOKINGS =====

@router.post("/members/{member_id}/bookings", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_booking_for_member(
    member_id: str,
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Create booking for family member"""
    db = get_db()
    
    try:
        member = db.family_members.find_one({
            "_id": ObjectId(member_id),
            "tenant_id": tenant_id,
        })
        
        if not member:
            raise HTTPException(status_code=404, detail="Family member not found")
        
        from datetime import datetime
        booking = {
            "tenant_id": tenant_id,
            "family_member_id": member_id,
            **data,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        result = db.bookings.insert_one(booking)
        booking["_id"] = result.inserted_id
        
        return booking
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating booking for member: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/booking-history", response_model=list)
async def get_family_booking_history(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """Get family booking history"""
    db = get_db()
    
    try:
        account = db.family_accounts.find_one({
            "primary_member_id": current_user.get("id"),
            "tenant_id": tenant_id,
        })
        
        if not account:
            raise HTTPException(status_code=404, detail="Family account not found")
        
        bookings = list(db.bookings.find({
            "family_account_id": str(account.get("_id")),
            "tenant_id": tenant_id,
        }).sort("created_at", -1).skip(offset).limit(limit))
        
        return bookings
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting family booking history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/members/{member_id}/booking-history", response_model=list)
async def get_member_booking_history(
    member_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """Get member booking history"""
    db = get_db()
    
    try:
        bookings = list(db.bookings.find({
            "family_member_id": member_id,
            "tenant_id": tenant_id,
        }).sort("created_at", -1).skip(offset).limit(limit))
        
        return bookings
    except Exception as e:
        logger.error(f"Error getting member booking history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/booking-templates", response_model=list)
async def get_shared_booking_templates(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get shared booking templates"""
    db = get_db()
    
    try:
        templates = list(db.booking_templates.find({
            "tenant_id": tenant_id,
            "is_shared": True,
        }))
        
        return templates
    except Exception as e:
        logger.error(f"Error getting shared booking templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/booking-templates/{template_id}/share", response_model=dict)
async def share_booking_template(
    template_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Share booking template with family"""
    db = get_db()
    
    try:
        db.booking_templates.update_one(
            {"_id": ObjectId(template_id), "tenant_id": tenant_id},
            {"$set": {"is_shared": True}},
        )
        
        return {"success": True, "message": "Template shared successfully"}
    except Exception as e:
        logger.error(f"Error sharing booking template: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== PAYMENT METHODS =====

@router.get("/payment-methods", response_model=list)
async def get_shared_payment_methods(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get shared payment methods"""
    db = get_db()
    
    try:
        account = db.family_accounts.find_one({
            "primary_member_id": current_user.get("id"),
            "tenant_id": tenant_id,
        })
        
        if not account:
            raise HTTPException(status_code=404, detail="Family account not found")
        
        methods = list(db.family_payment_methods.find({
            "family_account_id": str(account.get("_id")),
            "tenant_id": tenant_id,
        }))
        
        return methods
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting shared payment methods: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/payment-methods", response_model=dict, status_code=status.HTTP_201_CREATED)
async def add_shared_payment_method(
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Add shared payment method"""
    db = get_db()
    
    try:
        account = db.family_accounts.find_one({
            "primary_member_id": current_user.get("id"),
            "tenant_id": tenant_id,
        })
        
        if not account:
            raise HTTPException(status_code=404, detail="Family account not found")
        
        from datetime import datetime
        method = {
            "family_account_id": str(account.get("_id")),
            "tenant_id": tenant_id,
            **data,
            "created_at": datetime.utcnow(),
        }
        
        result = db.family_payment_methods.insert_one(method)
        method["_id"] = result.inserted_id
        
        return method
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding shared payment method: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/payment-methods/{payment_method_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_shared_payment_method(
    payment_method_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Remove shared payment method"""
    db = get_db()
    
    try:
        result = db.family_payment_methods.delete_one({
            "_id": ObjectId(payment_method_id),
            "tenant_id": tenant_id,
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Payment method not found")
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing shared payment method: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== ANALYTICS =====

@router.get("/analytics", response_model=dict)
async def get_family_analytics(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get family account analytics"""
    db = get_db()
    
    try:
        account = db.family_accounts.find_one({
            "primary_member_id": current_user.get("id"),
            "tenant_id": tenant_id,
        })
        
        if not account:
            raise HTTPException(status_code=404, detail="Family account not found")
        
        members = db.family_members.count_documents({
            "family_account_id": str(account.get("_id")),
            "tenant_id": tenant_id,
        })
        
        bookings = db.bookings.count_documents({
            "family_account_id": str(account.get("_id")),
            "tenant_id": tenant_id,
        })
        
        return {
            "total_members": members,
            "total_bookings": bookings,
            "account_created": account.get("created_at"),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting family analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/members/{member_id}/analytics", response_model=dict)
async def get_member_contribution_analytics(
    member_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get member contribution analytics"""
    db = get_db()
    
    try:
        bookings = db.bookings.count_documents({
            "family_member_id": member_id,
            "tenant_id": tenant_id,
        })
        
        pool = db.family_loyalty_pools.find_one({
            "tenant_id": tenant_id,
        })
        
        loyalty_points = 0
        if pool:
            loyalty_points = pool.get("member_contributions", {}).get(member_id, 0)
        
        return {
            "total_bookings": bookings,
            "loyalty_points_contributed": loyalty_points,
        }
    except Exception as e:
        logger.error(f"Error getting member contribution analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
