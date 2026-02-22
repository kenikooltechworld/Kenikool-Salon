from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from datetime import datetime
from app.services.pos_service import POSService
from app.schemas.gift_card import GiftCardResponse
from app.models.gift_card import GiftCard
from app.database import Database

router = APIRouter(prefix="/api/gift-cards", tags=["gift-cards-staff"])

def get_db():
    """Get database instance"""
    return Database.get_db()

@router.get("/list")
async def list_gift_cards(
    tenant_id: str = Query(...),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    card_type: Optional[str] = Query(None),
):
    """List gift cards with filtering and pagination"""
    try:
        db = get_db()
        skip = (page - 1) * limit
        query = {"tenant_id": tenant_id}
        
        if status:
            query["status"] = status
        if card_type:
            query["card_type"] = card_type
        
        total = await db.gift_cards.count_documents(query)
        cards = await db.gift_cards.find(query).skip(skip).limit(limit).to_list(limit)
        
        return {
            "cards": cards,
            "total": total,
            "page": page,
            "limit": limit,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/activate")
async def activate_card(
    tenant_id: str,
    card_id: str,
):
    """Activate a gift card"""
    try:
        db = get_db()
        result = await db.gift_cards.update_one(
            {"_id": card_id, "tenant_id": tenant_id},
            {
                "$set": {
                    "status": "active",
                    "activation_required": False,
                    "updated_at": datetime.utcnow(),
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Gift card not found")
        
        card = await db.gift_cards.find_one({"_id": card_id})
        return {"success": True, "card": card}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/void")
async def void_card(
    tenant_id: str,
    card_id: str,
    refund: bool = False,
):
    """Void a gift card with optional refund"""
    try:
        db = get_db()
        card = await db.gift_cards.find_one({"_id": card_id, "tenant_id": tenant_id})
        
        if not card:
            raise HTTPException(status_code=404, detail="Gift card not found")
        
        update_data = {
            "status": "voided",
            "updated_at": datetime.utcnow(),
        }
        
        if refund:
            update_data["refund_amount"] = card.get("balance", 0)
            update_data["refund_processed"] = True
        
        await db.gift_cards.update_one(
            {"_id": card_id},
            {"$set": update_data}
        )
        
        updated_card = await db.gift_cards.find_one({"_id": card_id})
        return {"success": True, "card": updated_card}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reload")
async def reload_card(
    tenant_id: str,
    card_id: str,
    amount: float,
):
    """Reload a gift card with additional balance"""
    try:
        db = get_db()
        if amount <= 0:
            raise HTTPException(status_code=400, detail="Amount must be greater than 0")
        
        card = await db.gift_cards.find_one({"_id": card_id, "tenant_id": tenant_id})
        
        if not card:
            raise HTTPException(status_code=404, detail="Gift card not found")
        
        new_balance = card.get("balance", 0) + amount
        new_expiry = datetime.utcnow()
        new_expiry = new_expiry.replace(year=new_expiry.year + 1)
        
        await db.gift_cards.update_one(
            {"_id": card_id},
            {
                "$set": {
                    "balance": new_balance,
                    "expires_at": new_expiry,
                    "updated_at": datetime.utcnow(),
                },
                "$push": {
                    "audit_log": {
                        "action": "reload",
                        "amount": amount,
                        "timestamp": datetime.utcnow(),
                    }
                }
            }
        )
        
        updated_card = await db.gift_cards.find_one({"_id": card_id})
        return {"success": True, "card": updated_card}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/resend")
async def resend_card(
    tenant_id: str,
    card_id: str,
    email: str,
):
    """Resend gift card to a new email"""
    try:
        db = get_db()
        card = await db.gift_cards.find_one({"_id": card_id, "tenant_id": tenant_id})
        
        if not card:
            raise HTTPException(status_code=404, detail="Gift card not found")
        
        if card.get("card_type") != "digital":
            raise HTTPException(status_code=400, detail="Only digital cards can be resent")
        
        await db.gift_cards.update_one(
            {"_id": card_id},
            {
                "$set": {
                    "recipient_email": email,
                    "updated_at": datetime.utcnow(),
                },
                "$push": {
                    "audit_log": {
                        "action": "resend",
                        "new_email": email,
                        "timestamp": datetime.utcnow(),
                    }
                }
            }
        )
        
        updated_card = await db.gift_cards.find_one({"_id": card_id})
        return {"success": True, "card": updated_card}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
