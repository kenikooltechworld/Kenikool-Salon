"""Gift card service"""
import secrets
import string
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Dict
from bson import ObjectId, Decimal128

from app.models.gift_card import GiftCard, GiftCardTransaction
from app.schemas.gift_card import (
    GiftCardPurchaseRequest,
    GiftCardRedemptionRequest,
    GiftCardBalanceCheck
)


class GiftCardService:
    """Service for managing gift cards"""
    
    @staticmethod
    def generate_gift_card_code() -> str:
        """Generate a unique gift card code"""
        # Format: GC-XXXX-XXXX-XXXX (16 characters total)
        chars = string.ascii_uppercase + string.digits
        code_parts = []
        for _ in range(3):
            part = ''.join(secrets.choice(chars) for _ in range(4))
            code_parts.append(part)
        
        return f"GC-{'-'.join(code_parts)}"
    
    @staticmethod
    async def purchase_gift_card(
        tenant_id: ObjectId,
        purchase_data: GiftCardPurchaseRequest
    ) -> GiftCard:
        """Purchase a new gift card"""
        # Generate unique code
        code = GiftCardService.generate_gift_card_code()
        
        # Ensure code is unique
        while await GiftCard.find_one({"tenant_id": tenant_id, "code": code}):
            code = GiftCardService.generate_gift_card_code()
        
        # Calculate expiry date
        expiry_date = datetime.utcnow() + timedelta(days=purchase_data.expiry_months * 30)
        
        # Create gift card
        gift_card = GiftCard(
            tenant_id=tenant_id,
            code=code,
            initial_amount=Decimal128(str(purchase_data.amount)),
            current_balance=Decimal128(str(purchase_data.amount)),
            currency="NGN",
            purchased_by_name=purchase_data.purchased_by_name,
            purchased_by_email=purchase_data.purchased_by_email,
            purchased_by_phone=purchase_data.purchased_by_phone,
            purchase_date=datetime.utcnow(),
            recipient_name=purchase_data.recipient_name,
            recipient_email=purchase_data.recipient_email,
            recipient_phone=purchase_data.recipient_phone,
            status="active",
            expiry_date=expiry_date,
            is_active=True,
            delivery_method=purchase_data.delivery_method,
            delivery_date=purchase_data.delivery_date,
            is_delivered=False,
            personal_message=purchase_data.personal_message,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        await gift_card.insert()
        
        # Create purchase transaction
        transaction = GiftCardTransaction(
            tenant_id=tenant_id,
            gift_card_id=gift_card.id,
            gift_card_code=code,
            transaction_type="purchase",
            amount=Decimal128(str(purchase_data.amount)),
            balance_before=Decimal128("0"),
            balance_after=Decimal128(str(purchase_data.amount)),
            description=f"Gift card purchased by {purchase_data.purchased_by_name}",
            performed_by=purchase_data.purchased_by_email,
            created_at=datetime.utcnow()
        )
        
        await transaction.insert()
        
        # Schedule delivery if needed
        if not purchase_data.delivery_date or purchase_data.delivery_date <= datetime.utcnow():
            await GiftCardService.deliver_gift_card(gift_card)
        
        return gift_card
    
    @staticmethod
    async def deliver_gift_card(gift_card: GiftCard) -> bool:
        """Deliver gift card via email/SMS"""
        # TODO: Implement email/SMS delivery
        # For now, mark as delivered
        gift_card.is_delivered = True
        gift_card.delivered_at = datetime.utcnow()
        gift_card.updated_at = datetime.utcnow()
        await gift_card.save()
        
        return True
    
    @staticmethod
    async def check_balance(
        tenant_id: ObjectId,
        code: str
    ) -> Optional[GiftCard]:
        """Check gift card balance"""
        gift_card = await GiftCard.find_one({
            "tenant_id": tenant_id,
            "code": code.upper()
        })
        
        if not gift_card:
            return None
        
        # Check if expired
        if gift_card.expiry_date and gift_card.expiry_date < datetime.utcnow():
            if gift_card.status != "expired":
                gift_card.status = "expired"
                gift_card.is_active = False
                gift_card.updated_at = datetime.utcnow()
                await gift_card.save()
        
        return gift_card
    
    @staticmethod
    async def redeem_gift_card(
        tenant_id: ObjectId,
        redemption_data: GiftCardRedemptionRequest,
        booking_id: Optional[ObjectId] = None
    ) -> Dict:
        """Redeem a gift card"""
        # Find gift card
        gift_card = await GiftCard.find_one({
            "tenant_id": tenant_id,
            "code": redemption_data.code.upper()
        })
        
        if not gift_card:
            raise ValueError("Gift card not found")
        
        # Validate gift card
        if not gift_card.is_active:
            raise ValueError("Gift card is not active")
        
        if gift_card.status == "expired":
            raise ValueError("Gift card has expired")
        
        if gift_card.status == "redeemed":
            raise ValueError("Gift card has already been fully redeemed")
        
        if gift_card.expiry_date and gift_card.expiry_date < datetime.utcnow():
            gift_card.status = "expired"
            gift_card.is_active = False
            await gift_card.save()
            raise ValueError("Gift card has expired")
        
        # Check balance
        current_balance = gift_card.current_balance.to_decimal()
        redemption_amount = redemption_data.amount
        
        if redemption_amount > current_balance:
            raise ValueError(f"Insufficient balance. Available: {current_balance}")
        
        # Calculate new balance
        new_balance = current_balance - redemption_amount
        
        # Update gift card
        gift_card.current_balance = Decimal128(str(new_balance))
        gift_card.updated_at = datetime.utcnow()
        
        # Update status if fully redeemed
        if new_balance == 0:
            gift_card.status = "redeemed"
            gift_card.is_active = False
        
        await gift_card.save()
        
        # Create redemption transaction
        transaction = GiftCardTransaction(
            tenant_id=tenant_id,
            gift_card_id=gift_card.id,
            gift_card_code=gift_card.code,
            transaction_type="redemption",
            amount=Decimal128(str(redemption_amount)),
            balance_before=Decimal128(str(current_balance)),
            balance_after=Decimal128(str(new_balance)),
            booking_id=booking_id,
            description=f"Redeemed {redemption_amount} from gift card",
            created_at=datetime.utcnow()
        )
        
        await transaction.insert()
        
        return {
            "success": True,
            "redeemed_amount": float(redemption_amount),
            "remaining_balance": float(new_balance),
            "gift_card_code": gift_card.code
        }
    
    @staticmethod
    async def get_gift_card_transactions(
        tenant_id: ObjectId,
        gift_card_id: ObjectId
    ) -> List[GiftCardTransaction]:
        """Get transaction history for a gift card"""
        transactions = await GiftCardTransaction.find({
            "tenant_id": tenant_id,
            "gift_card_id": gift_card_id
        }).sort("-created_at").to_list()
        
        return transactions
    
    @staticmethod
    async def list_gift_cards(
        tenant_id: ObjectId,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[List[GiftCard], int]:
        """List gift cards for a tenant"""
        query = {"tenant_id": tenant_id}
        
        if status:
            query["status"] = status
        
        total = await GiftCard.find(query).count()
        gift_cards = await GiftCard.find(query).sort("-created_at").skip(skip).limit(limit).to_list()
        
        return gift_cards, total
    
    @staticmethod
    async def cancel_gift_card(
        tenant_id: ObjectId,
        gift_card_id: ObjectId,
        reason: str
    ) -> GiftCard:
        """Cancel a gift card"""
        gift_card = await GiftCard.find_one({
            "tenant_id": tenant_id,
            "_id": gift_card_id
        })
        
        if not gift_card:
            raise ValueError("Gift card not found")
        
        if gift_card.status == "redeemed":
            raise ValueError("Cannot cancel a fully redeemed gift card")
        
        gift_card.status = "cancelled"
        gift_card.is_active = False
        gift_card.updated_at = datetime.utcnow()
        await gift_card.save()
        
        # Create cancellation transaction
        transaction = GiftCardTransaction(
            tenant_id=tenant_id,
            gift_card_id=gift_card.id,
            gift_card_code=gift_card.code,
            transaction_type="refund",
            amount=gift_card.current_balance,
            balance_before=gift_card.current_balance,
            balance_after=Decimal128("0"),
            description=f"Gift card cancelled: {reason}",
            created_at=datetime.utcnow()
        )
        
        await transaction.insert()
        
        return gift_card
