"""Gift card service"""
import secrets
import string
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Dict
from bson import ObjectId, Decimal128

logger = logging.getLogger(__name__)

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
    def purchase_gift_card(
        tenant_id: ObjectId,
        purchase_data: GiftCardPurchaseRequest
    ) -> GiftCard:
        """Purchase a new gift card"""
        code = GiftCardService.generate_gift_card_code()
        
        while GiftCard.objects(tenant_id=tenant_id, code=code).first():
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
        
        gift_card.save()
        
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
        
        transaction.save()
        
        if not purchase_data.delivery_date or purchase_data.delivery_date <= datetime.utcnow():
            GiftCardService.deliver_gift_card(gift_card)
        
        return gift_card
    
    @staticmethod
    def deliver_gift_card(gift_card: GiftCard) -> bool:
        """Deliver gift card via email/SMS"""
        from app.tasks import send_email
        from app.services.email_template_service import EmailTemplateService
        from app.models.tenant import Tenant

        recipient_email = gift_card.recipient_email or gift_card.purchased_by_email
        recipient_phone = getattr(gift_card, "recipient_phone", None)

        tenant = Tenant.objects(id=gift_card.tenant_id).first()
        business_email = tenant.settings.get("email", tenant.email) if tenant.settings else tenant.email

        email_context = {
            "customer_email": recipient_email,
            "business_email": business_email,
            "gift_card_code": gift_card.code,
            "amount": str(gift_card.initial_amount),
            "currency": gift_card.currency or "NGN",
        }

        try:
            rendered = EmailTemplateService.render_customer_welcome_email(
                str(gift_card.tenant_id), email_context
            )
            run_in_background(send_email,
                to=recipient_email,
                subject="You have received a gift card!",
                template=rendered or "<p>Your gift card code has been delivered.</p>",
                context=email_context,
            )
        except Exception as e:
            logger.warning(f"Gift card delivery email failed: {e}")

        if recipient_phone:
            try:
                from app.services.termii_service import TermiiService
                TermiiService().send_sms(
                    phone_number=recipient_phone,
                    message=f"You have received a gift card! Code: {gift_card.code}",
                )
            except Exception as e:
                logger.warning(f"Gift card SMS delivery failed: {e}")

        gift_card.is_delivered = True
        gift_card.delivered_at = datetime.utcnow()
        gift_card.updated_at = datetime.utcnow()
        gift_card.save()
        return True
    
    @staticmethod
    def check_balance(
        tenant_id: ObjectId,
        code: str
    ) -> Optional[GiftCard]:
        """Check gift card balance"""
        gift_card = GiftCard.objects(tenant_id=tenant_id, code=code.upper()).first()
        
        if not gift_card:
            return None
        
        if gift_card.expiry_date and gift_card.expiry_date < datetime.utcnow():
            if gift_card.status != "expired":
                gift_card.status = "expired"
                gift_card.is_active = False
                gift_card.updated_at = datetime.utcnow()
                gift_card.save()
        
        return gift_card
    
    @staticmethod
    def redeem_gift_card(
        tenant_id: ObjectId,
        redemption_data: GiftCardRedemptionRequest,
        booking_id: Optional[ObjectId] = None
    ) -> Dict:
        """Redeem a gift card"""
        gift_card = GiftCard.objects(tenant_id=tenant_id, code=redemption_data.code.upper()).first()
        
        if not gift_card:
            raise ValueError("Gift card not found")
        
        if not gift_card.is_active:
            raise ValueError("Gift card is not active")
        
        if gift_card.status == "expired":
            raise ValueError("Gift card has expired")
        
        if gift_card.status == "redeemed":
            raise ValueError("Gift card has already been fully redeemed")
        
        if gift_card.expiry_date and gift_card.expiry_date < datetime.utcnow():
            gift_card.status = "expired"
            gift_card.is_active = False
            gift_card.save()
            raise ValueError("Gift card has expired")
        
        current_balance = gift_card.current_balance.to_decimal()
        redemption_amount = redemption_data.amount
        
        if redemption_amount > current_balance:
            raise ValueError(f"Insufficient balance. Available: {current_balance}")
        
        new_balance = current_balance - redemption_amount
        
        gift_card.current_balance = Decimal128(str(new_balance))
        gift_card.updated_at = datetime.utcnow()
        
        if new_balance == 0:
            gift_card.status = "redeemed"
            gift_card.is_active = False
        
        gift_card.save()
        
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
        
        transaction.save()
        
        return {
            "success": True,
            "redeemed_amount": float(redemption_amount),
            "remaining_balance": float(new_balance),
            "gift_card_code": gift_card.code
        }
    
    @staticmethod
    def get_gift_card_transactions(
        tenant_id: ObjectId,
        gift_card_id: ObjectId
    ) -> List[GiftCardTransaction]:
        """Get transaction history for a gift card"""
        transactions = list(GiftCardTransaction.objects(
            tenant_id=tenant_id,
            gift_card_id=gift_card_id
        ).order_by("-created_at"))
        
        return transactions
    
    @staticmethod
    def list_gift_cards(
        tenant_id: ObjectId,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[List[GiftCard], int]:
        """List gift cards for a tenant"""
        from mongoengine import Q
        
        query = Q(tenant_id=tenant_id)
        
        if status:
            query &= Q(status=status)
        
        total = GiftCard.objects(query).count()
        gift_cards = list(GiftCard.objects(query).order_by("-created_at").skip(skip).limit(limit))
        
        return gift_cards, total
    
    @staticmethod
    def cancel_gift_card(
        tenant_id: ObjectId,
        gift_card_id: ObjectId,
        reason: str
    ) -> GiftCard:
        """Cancel a gift card"""
        gift_card = GiftCard.objects(tenant_id=tenant_id, id=gift_card_id).first()
        
        if not gift_card:
            raise ValueError("Gift card not found")
        
        if gift_card.status == "redeemed":
            raise ValueError("Cannot cancel a fully redeemed gift card")
        
        gift_card.status = "cancelled"
        gift_card.is_active = False
        gift_card.updated_at = datetime.utcnow()
        gift_card.save()
        
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
        
        transaction.save()
        
        return gift_card


