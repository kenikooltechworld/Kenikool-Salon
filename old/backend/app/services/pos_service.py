"""
Point of Sale (POS) service - Business logic layer
"""
from bson import ObjectId
from datetime import datetime, timezone
from typing import Dict, List, Optional
import logging
import uuid

from app.database import Database
from app.api.exceptions import NotFoundException, BadRequestException

logger = logging.getLogger(__name__)


class POSService:
    """POS service for handling point of sale business logic"""
    
    @staticmethod
    def create_transaction(
        tenant_id: str,
        user_id: str,
        items: List[Dict],
        client_id: Optional[str] = None,
        stylist_id: Optional[str] = None,
        discount_total: float = 0,
        tax: float = 0,
        tip: float = 0,
        notes: Optional[str] = None
    ) -> Dict:
        """
        Create a POS transaction
        
        Args:
            tenant_id: Tenant ID
            user_id: User creating the transaction
            items: List of cart items
            client_id: Optional client ID
            stylist_id: Optional stylist ID
            discount_total: Total discount amount
            tax: Tax amount
            tip: Tip amount
            notes: Optional notes
            
        Returns:
            Dict with transaction details
        """
        db = Database.get_db()
        
        # Calculate subtotal
        subtotal = sum(item["quantity"] * item["price"] - item.get("discount", 0) for item in items)
        
        # Calculate total
        total = subtotal - discount_total + tax + tip
        
        if total < 0:
            raise BadRequestException("Transaction total cannot be negative")
        
        # Generate transaction number
        transaction_number = f"POS-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        # Create transaction
        transaction_data = {
            "tenant_id": tenant_id,
            "transaction_number": transaction_number,
            "items": items,
            "subtotal": subtotal,
            "discount_total": discount_total,
            "tax": tax,
            "tip": tip,
            "total": total,
            "payments": [],
            "client_id": client_id,
            "stylist_id": stylist_id,
            "created_by": user_id,
            "created_at": datetime.now(timezone.utc),
            "status": "pending",
            "notes": notes
        }
        
        result = db.pos_transactions.insert_one(transaction_data)
        transaction_id = str(result.inserted_id)
        
        logger.info(f"POS transaction created: {transaction_id} by user: {user_id}")
        
        transaction_data["id"] = transaction_id
        transaction_data["_id"] = result.inserted_id
        
        return transaction_data
    
    @staticmethod
    def process_payment(
        transaction_id: str,
        tenant_id: str,
        payments: List[Dict]
    ) -> Dict:
        """
        Process payment for a POS transaction
        
        Args:
            transaction_id: Transaction ID
            tenant_id: Tenant ID
            payments: List of payment methods
            
        Returns:
            Dict with payment status
        """
        db = Database.get_db()
        
        # Get transaction
        transaction = db.pos_transactions.find_one({
            "_id": ObjectId(transaction_id),
            "tenant_id": tenant_id
        })
        
        if not transaction:
            raise NotFoundException("Transaction not found")
        
        if transaction["status"] == "completed":
            raise BadRequestException("Transaction already completed")
        
        # Calculate total paid
        total_paid = sum(payment["amount"] for payment in payments)
        
        # Validate payment amount
        if total_paid < transaction["total"]:
            raise BadRequestException(f"Insufficient payment. Required: {transaction['total']}, Paid: {total_paid}")
        
        # Process gift card payments
        gift_card_redemptions = []
        for payment in payments:
            if payment["method"] == "gift_card":
                card_number = payment.get("reference")
                if not card_number:
                    raise BadRequestException("Gift card number is required")
                
                # Redeem gift card
                try:
                    redemption = POSService.redeem_gift_card(
                        tenant_id=tenant_id,
                        card_number=card_number,
                        amount=payment["amount"],
                        transaction_id=transaction_id,
                        location="POS"
                    )
                    gift_card_redemptions.append({
                        "card_number": card_number,
                        "amount": payment["amount"],
                        "remaining_balance": redemption["remaining_balance"]
                    })
                except Exception as e:
                    # Rollback any successful gift card redemptions
                    for redemption in gift_card_redemptions:
                        try:
                            # Refund the gift card
                            gift_card = db.gift_cards.find_one({
                                "tenant_id": tenant_id,
                                "card_number": redemption["card_number"]
                            })
                            if gift_card:
                                db.gift_cards.update_one(
                                    {"_id": gift_card["_id"]},
                                    {
                                        "$inc": {"balance": redemption["amount"]},
                                        "$push": {
                                            "transactions": {
                                                "type": "refund",
                                                "transaction_id": transaction_id,
                                                "amount": redemption["amount"],
                                                "balance_after": gift_card["balance"] + redemption["amount"],
                                                "timestamp": datetime.now(timezone.utc),
                                                "reason": "payment_failed"
                                            }
                                        }
                                    }
                                )
                        except Exception as rollback_error:
                            logger.error(f"Failed to rollback gift card redemption: {str(rollback_error)}")
                    
                    raise BadRequestException(f"Gift card payment failed: {str(e)}")
        
        # Update transaction with payments
        update_data = {
            "$set": {
                "payments": payments,
                "status": "completed",
                "completed_at": datetime.now(timezone.utc)
            }
        }
        
        # Add gift card redemption details if any
        if gift_card_redemptions:
            update_data["$set"]["gift_card_redemptions"] = gift_card_redemptions
        
        db.pos_transactions.update_one(
            {"_id": ObjectId(transaction_id)},
            update_data
        )
        
        # Update inventory for products
        for item in transaction["items"]:
            if item["type"] == "product":
                db.inventory.update_one(
                    {"_id": ObjectId(item["item_id"]), "tenant_id": tenant_id},
                    {"$inc": {"quantity": -item["quantity"]}}
                )
        
        # Update cash drawer if cash payment
        cash_amount = sum(p["amount"] for p in payments if p["method"] == "cash")
        if cash_amount > 0:
            POSService._update_cash_drawer(tenant_id, "sale", cash_amount, transaction_id)
        
        # Record transaction in current shift
        for payment in payments:
            POSService.record_shift_transaction(
                tenant_id=tenant_id,
                user_id=transaction["created_by"],
                transaction_id=transaction_id,
                amount=payment["amount"],
                payment_method=payment["method"]
            )
        
        logger.info(f"POS transaction completed: {transaction_id}")
        
        return {
            "status": "completed",
            "transaction_id": transaction_id,
            "total_paid": total_paid,
            "change": total_paid - transaction["total"] if total_paid > transaction["total"] else 0,
            "gift_card_redemptions": gift_card_redemptions
        }
    
    @staticmethod
    def split_payment(
        transaction_id: str,
        tenant_id: str,
        payments: List[Dict]
    ) -> Dict:
        """
        Process split payment for a POS transaction
        
        Args:
            transaction_id: Transaction ID
            tenant_id: Tenant ID
            payments: List of payment methods with amounts
            
        Returns:
            Dict with payment status
        """
        # Split payment is handled the same way as regular payment
        return POSService.process_payment(transaction_id, tenant_id, payments)
    
    @staticmethod
    def get_transaction(transaction_id: str, tenant_id: str) -> Dict:
        """Get a POS transaction by ID"""
        db = Database.get_db()
        
        transaction = db.pos_transactions.find_one({
            "_id": ObjectId(transaction_id),
            "tenant_id": tenant_id
        })
        
        if not transaction:
            raise NotFoundException("Transaction not found")
        
        transaction["id"] = str(transaction["_id"])
        return transaction
    
    @staticmethod
    def list_transactions(
        tenant_id: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        stylist_id: Optional[str] = None,
        client_id: Optional[str] = None,
        status: Optional[str] = None,
        offset: int = 0,
        limit: int = 20
    ) -> List[Dict]:
        """List POS transactions with filters"""
        db = Database.get_db()
        
        query = {"tenant_id": tenant_id}
        
        if date_from:
            query["created_at"] = {"$gte": datetime.fromisoformat(date_from)}
        if date_to:
            if "created_at" in query:
                query["created_at"]["$lte"] = datetime.fromisoformat(date_to)
            else:
                query["created_at"] = {"$lte": datetime.fromisoformat(date_to)}
        if stylist_id:
            query["stylist_id"] = stylist_id
        if client_id:
            query["client_id"] = client_id
        if status:
            query["status"] = status
        
        transactions = list(db.pos_transactions.find(query).sort("created_at", -1).skip(offset).limit(limit))
        
        for transaction in transactions:
            transaction["id"] = str(transaction["_id"])
        
        return transactions
    
    @staticmethod
    def open_cash_drawer(
        tenant_id: str,
        user_id: str,
        opening_balance: float,
        notes: Optional[str] = None
    ) -> Dict:
        """
        Open a cash drawer session
        
        Args:
            tenant_id: Tenant ID
            user_id: User opening the drawer
            opening_balance: Starting cash amount
            notes: Optional notes
            
        Returns:
            Dict with cash drawer details
        """
        db = Database.get_db()
        
        # Check if there's already an open drawer
        existing_drawer = db.cash_drawers.find_one({
            "tenant_id": tenant_id,
            "status": "open"
        })
        
        if existing_drawer:
            raise BadRequestException("A cash drawer is already open. Please close it first.")
        
        # Create cash drawer
        drawer_data = {
            "tenant_id": tenant_id,
            "opened_by": user_id,
            "opened_at": datetime.now(timezone.utc),
            "opening_balance": opening_balance,
            "expected_balance": opening_balance,
            "actual_balance": None,
            "variance": None,
            "closed_at": None,
            "transactions": [],
            "status": "open",
            "notes": notes
        }
        
        result = db.cash_drawers.insert_one(drawer_data)
        drawer_id = str(result.inserted_id)
        
        logger.info(f"Cash drawer opened: {drawer_id} by user: {user_id}")
        
        drawer_data["id"] = drawer_id
        drawer_data["_id"] = result.inserted_id
        
        return drawer_data
    
    @staticmethod
    def record_cash_drop(
        tenant_id: str,
        amount: float,
        notes: Optional[str] = None
    ) -> Dict:
        """
        Record a cash drop (removing cash from drawer)
        
        Args:
            tenant_id: Tenant ID
            amount: Amount to drop
            notes: Optional notes
            
        Returns:
            Dict with updated drawer details
        """
        db = Database.get_db()
        
        # Get open drawer
        drawer = db.cash_drawers.find_one({
            "tenant_id": tenant_id,
            "status": "open"
        })
        
        if not drawer:
            raise NotFoundException("No open cash drawer found")
        
        # Record transaction
        transaction = {
            "type": "drop",
            "amount": amount,
            "timestamp": datetime.now(timezone.utc),
            "notes": notes
        }
        
        # Update drawer
        db.cash_drawers.update_one(
            {"_id": drawer["_id"]},
            {
                "$push": {"transactions": transaction},
                "$inc": {"expected_balance": -amount}
            }
        )
        
        logger.info(f"Cash drop recorded: {amount} for drawer: {drawer['_id']}")
        
        return {"status": "success", "amount": amount}
    
    @staticmethod
    def close_cash_drawer(
        tenant_id: str,
        actual_balance: float,
        notes: Optional[str] = None
    ) -> Dict:
        """
        Close a cash drawer session
        
        Args:
            tenant_id: Tenant ID
            actual_balance: Actual cash counted
            notes: Optional notes
            
        Returns:
            Dict with cash drawer details including variance
        """
        db = Database.get_db()
        
        # Get open drawer
        drawer = db.cash_drawers.find_one({
            "tenant_id": tenant_id,
            "status": "open"
        })
        
        if not drawer:
            raise NotFoundException("No open cash drawer found")
        
        # Calculate variance
        variance = actual_balance - drawer["expected_balance"]
        
        # Update drawer
        db.cash_drawers.update_one(
            {"_id": drawer["_id"]},
            {
                "$set": {
                    "actual_balance": actual_balance,
                    "variance": variance,
                    "closed_at": datetime.now(timezone.utc),
                    "status": "closed",
                    "close_notes": notes
                }
            }
        )
        
        logger.info(f"Cash drawer closed: {drawer['_id']} with variance: {variance}")
        
        return {
            "status": "closed",
            "expected_balance": drawer["expected_balance"],
            "actual_balance": actual_balance,
            "variance": variance
        }
    
    @staticmethod
    def get_current_cash_drawer(tenant_id: str) -> Optional[Dict]:
        """Get the currently open cash drawer"""
        db = Database.get_db()
        
        drawer = db.cash_drawers.find_one({
            "tenant_id": tenant_id,
            "status": "open"
        })
        
        if drawer:
            drawer["id"] = str(drawer["_id"])
        
        return drawer
    
    @staticmethod
    def get_daily_summary(tenant_id: str, date: str) -> Dict:
        """
        Get daily POS summary
        
        Args:
            tenant_id: Tenant ID
            date: Date in YYYY-MM-DD format
            
        Returns:
            Dict with daily summary
        """
        db = Database.get_db()
        
        # Parse date
        start_date = datetime.fromisoformat(f"{date}T00:00:00")
        end_date = datetime.fromisoformat(f"{date}T23:59:59")
        
        # Get transactions for the day
        transactions = list(db.pos_transactions.find({
            "tenant_id": tenant_id,
            "created_at": {"$gte": start_date, "$lte": end_date},
            "status": "completed"
        }))
        
        # Calculate totals
        transaction_count = len(transactions)
        total_sales = sum(t["total"] for t in transactions)
        total_cash = sum(
            sum(p["amount"] for p in t["payments"] if p["method"] == "cash")
            for t in transactions
        )
        total_card = sum(
            sum(p["amount"] for p in t["payments"] if p["method"] == "card")
            for t in transactions
        )
        total_tips = sum(t.get("tip", 0) for t in transactions)
        total_discounts = sum(t.get("discount_total", 0) for t in transactions)
        total_tax = sum(t.get("tax", 0) for t in transactions)
        
        # Calculate average transaction
        average_transaction = total_sales / transaction_count if transaction_count > 0 else 0
        
        # Calculate payment methods breakdown
        payment_methods = {}
        for t in transactions:
            for p in t.get("payments", []):
                method = p["method"]
                if method not in payment_methods:
                    payment_methods[method] = {"method": method, "total": 0, "count": 0}
                payment_methods[method]["total"] += p["amount"]
                payment_methods[method]["count"] += 1
        
        # Calculate services vs products revenue
        services_revenue = 0
        services_count = 0
        products_revenue = 0
        products_count = 0
        
        for t in transactions:
            for item in t.get("items", []):
                if item["type"] == "service":
                    services_revenue += item["price"] * item["quantity"]
                    services_count += item["quantity"]
                elif item["type"] == "product":
                    products_revenue += item["price"] * item["quantity"]
                    products_count += item["quantity"]
        
        # Get cash drawer variance
        drawer = db.cash_drawers.find_one({
            "tenant_id": tenant_id,
            "opened_at": {"$gte": start_date, "$lte": end_date},
            "status": "closed"
        })
        
        cash_drawer_variance = drawer.get("variance") if drawer else None
        
        return {
            "date": date,
            "transaction_count": transaction_count,
            "total_sales": total_sales,
            "average_transaction": average_transaction,
            "total_cash": total_cash,
            "total_card": total_card,
            "total_tips": total_tips,
            "total_discounts": total_discounts,
            "total_tax": total_tax,
            "payment_methods": list(payment_methods.values()),
            "services_revenue": services_revenue,
            "services_count": services_count,
            "products_revenue": products_revenue,
            "products_count": products_count,
            "cash_drawer_variance": cash_drawer_variance
        }
    
    @staticmethod
    def refund_transaction(
        transaction_id: str,
        tenant_id: str,
        refund_amount: float,
        reason: str,
        items: Optional[List[str]] = None
    ) -> Dict:
        """
        Refund a POS transaction (full or partial)
        
        Args:
            transaction_id: Transaction ID to refund
            tenant_id: Tenant ID
            refund_amount: Amount to refund
            reason: Refund reason
            items: Optional list of item IDs for partial refund
            
        Returns:
            Dict with refund status
        """
        db = Database.get_db()
        
        # Get transaction
        transaction = db.pos_transactions.find_one({
            "_id": ObjectId(transaction_id),
            "tenant_id": tenant_id
        })
        
        if not transaction:
            raise NotFoundException("Transaction not found")
        
        if transaction["status"] == "refunded":
            raise BadRequestException("Transaction already refunded")
        
        if transaction["status"] != "completed":
            raise BadRequestException("Can only refund completed transactions")
        
        # Validate refund amount
        if refund_amount <= 0 or refund_amount > transaction["total"]:
            raise BadRequestException(f"Invalid refund amount. Must be between 0 and {transaction['total']}")
        
        # Determine if full or partial refund
        is_full_refund = refund_amount == transaction["total"]
        
        # Update transaction status
        refund_data = {
            "refund_amount": refund_amount,
            "refund_reason": reason,
            "refunded_at": datetime.now(timezone.utc),
            "refund_type": "full" if is_full_refund else "partial"
        }
        
        update_fields = {
            "$set": {
                "status": "refunded" if is_full_refund else "partially_refunded",
                **refund_data
            }
        }
        
        db.pos_transactions.update_one(
            {"_id": ObjectId(transaction_id)},
            update_fields
        )
        
        # Restore inventory for products (full refund or specified items)
        if is_full_refund:
            for item in transaction["items"]:
                if item["type"] == "product":
                    db.inventory.update_one(
                        {"_id": ObjectId(item["item_id"]), "tenant_id": tenant_id},
                        {"$inc": {"quantity": item["quantity"]}}
                    )
        elif items:
            for item in transaction["items"]:
                if item["type"] == "product" and item["item_id"] in items:
                    db.inventory.update_one(
                        {"_id": ObjectId(item["item_id"]), "tenant_id": tenant_id},
                        {"$inc": {"quantity": item["quantity"]}}
                    )
        
        # Update cash drawer if cash refund
        cash_payments = [p for p in transaction["payments"] if p["method"] == "cash"]
        if cash_payments:
            # Calculate cash refund amount proportionally
            total_paid = sum(p["amount"] for p in transaction["payments"])
            cash_total = sum(p["amount"] for p in cash_payments)
            cash_refund = (cash_total / total_paid) * refund_amount if total_paid > 0 else 0
            
            if cash_refund > 0:
                POSService._update_cash_drawer(tenant_id, "refund", cash_refund, transaction_id)
        
        logger.info(f"Transaction refunded: {transaction_id}, amount: {refund_amount}, type: {'full' if is_full_refund else 'partial'}")
        
        return {
            "status": "success",
            "transaction_id": transaction_id,
            "refund_amount": refund_amount,
            "refund_type": "full" if is_full_refund else "partial"
        }
    
    @staticmethod
    def void_transaction(
        transaction_id: str,
        tenant_id: str,
        reason: str,
        voided_by: str
    ) -> Dict:
        """
        Void a pending POS transaction
        
        Args:
            transaction_id: Transaction ID to void
            tenant_id: Tenant ID
            reason: Void reason
            voided_by: User ID who voided the transaction
            
        Returns:
            Dict with void status
        """
        db = Database.get_db()
        
        # Get transaction
        transaction = db.pos_transactions.find_one({
            "_id": ObjectId(transaction_id),
            "tenant_id": tenant_id
        })
        
        if not transaction:
            raise NotFoundException("Transaction not found")
        
        if transaction["status"] == "voided":
            raise BadRequestException("Transaction already voided")
        
        if transaction["status"] != "pending":
            raise BadRequestException("Can only void pending transactions. Use refund for completed transactions.")
        
        # Update transaction status
        void_data = {
            "void_reason": reason,
            "voided_at": datetime.now(timezone.utc),
            "voided_by": voided_by
        }
        
        db.pos_transactions.update_one(
            {"_id": ObjectId(transaction_id)},
            {
                "$set": {
                    "status": "voided",
                    **void_data
                }
            }
        )
        
        logger.info(f"Transaction voided: {transaction_id} by user: {voided_by}, reason: {reason}")
        
        return {
            "status": "success",
            "transaction_id": transaction_id,
            "void_reason": reason
        }
    
    @staticmethod
    def update_transaction_notes(
        transaction_id: str,
        tenant_id: str,
        notes: str
    ) -> Dict:
        """
        Update transaction notes
        
        Args:
            transaction_id: Transaction ID
            tenant_id: Tenant ID
            notes: New notes text
            
        Returns:
            Dict with update status
        """
        db = Database.get_db()
        
        # Get transaction
        transaction = db.pos_transactions.find_one({
            "_id": ObjectId(transaction_id),
            "tenant_id": tenant_id
        })
        
        if not transaction:
            raise NotFoundException("Transaction not found")
        
        # Update notes
        db.pos_transactions.update_one(
            {"_id": ObjectId(transaction_id)},
            {
                "$set": {
                    "notes": notes,
                    "notes_updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        logger.info(f"Transaction notes updated: {transaction_id}")
        
        return {
            "status": "success",
            "transaction_id": transaction_id,
            "notes": notes
        }
    
    @staticmethod
    def process_return(
        transaction_id: str,
        tenant_id: str,
        return_items: List[Dict],
        return_reason: str,
        restocking_fee: float = 0,
        exchange_items: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Process product return/exchange
        
        Args:
            transaction_id: Original transaction ID
            tenant_id: Tenant ID
            return_items: Items being returned
            return_reason: Reason for return
            restocking_fee: Optional restocking fee
            exchange_items: Optional items for exchange
            
        Returns:
            Dict with return details
        """
        db = Database.get_db()
        
        # Get original transaction
        transaction = db.pos_transactions.find_one({
            "_id": ObjectId(transaction_id),
            "tenant_id": tenant_id
        })
        
        if not transaction:
            raise NotFoundException("Transaction not found")
        
        if transaction["status"] not in ["completed", "partially_refunded"]:
            raise BadRequestException("Can only return items from completed transactions")
        
        # Calculate return amount
        return_amount = sum(
            item["quantity"] * item["price"]
            for item in return_items
        )
        
        # Calculate exchange amount
        exchange_amount = 0
        if exchange_items:
            exchange_amount = sum(
                item["quantity"] * item["price"]
                for item in exchange_items
            )
        
        # Calculate net refund
        net_refund = return_amount - restocking_fee - exchange_amount
        
        if net_refund < 0:
            raise BadRequestException("Exchange amount exceeds return amount")
        
        # Create return record
        return_data = {
            "tenant_id": tenant_id,
            "transaction_id": transaction_id,
            "return_items": return_items,
            "return_reason": return_reason,
            "return_amount": return_amount,
            "restocking_fee": restocking_fee,
            "exchange_items": exchange_items or [],
            "exchange_amount": exchange_amount,
            "net_refund": net_refund,
            "created_at": datetime.now(timezone.utc),
            "created_by": transaction["created_by"]
        }
        
        result = db.pos_returns.insert_one(return_data)
        return_id = str(result.inserted_id)
        
        # Restore inventory for returned products
        for item in return_items:
            if item.get("type") == "product":
                db.inventory.update_one(
                    {"_id": ObjectId(item["item_id"]), "tenant_id": tenant_id},
                    {"$inc": {"quantity": item["quantity"]}}
                )
        
        # Deduct inventory for exchange products
        if exchange_items:
            for item in exchange_items:
                if item.get("type") == "product":
                    db.inventory.update_one(
                        {"_id": ObjectId(item["item_id"]), "tenant_id": tenant_id},
                        {"$inc": {"quantity": -item["quantity"]}}
                    )
        
        # Update cash drawer if net refund > 0
        if net_refund > 0:
            POSService._update_cash_drawer(tenant_id, "return", net_refund, return_id)
        elif exchange_amount > return_amount:
            # Customer owes money for exchange
            additional_payment = exchange_amount - return_amount + restocking_fee
            POSService._update_cash_drawer(tenant_id, "sale", additional_payment, return_id)
        
        logger.info(f"Return processed: {return_id} for transaction: {transaction_id}")
        
        return {
            "status": "success",
            "return_id": return_id,
            "transaction_id": transaction_id,
            "return_amount": return_amount,
            "restocking_fee": restocking_fee,
            "exchange_amount": exchange_amount,
            "net_refund": net_refund
        }
    
    @staticmethod
    def _update_cash_drawer(
        tenant_id: str,
        transaction_type: str,
        amount: float,
        reference: str
    ):
        """Internal method to update cash drawer with transaction"""
        db = Database.get_db()
        
        drawer = db.cash_drawers.find_one({
            "tenant_id": tenant_id,
            "status": "open"
        })
        
        if drawer:
            transaction = {
                "type": transaction_type,
                "amount": amount,
                "timestamp": datetime.now(timezone.utc),
                "reference": reference
            }
            
            db.cash_drawers.update_one(
                {"_id": drawer["_id"]},
                {
                    "$push": {"transactions": transaction},
                    "$inc": {"expected_balance": amount if transaction_type == "sale" else -amount}
                }
            )

    @staticmethod
    def park_transaction(
        tenant_id: str,
        user_id: str,
        items: List[Dict],
        client_id: Optional[str] = None,
        stylist_id: Optional[str] = None,
        discount_total: float = 0,
        tax: float = 0,
        tip: float = 0,
        notes: Optional[str] = None,
        customer_name: Optional[str] = None,
        customer_phone: Optional[str] = None
    ) -> Dict:
        """
        Park/hold a transaction for later completion
        
        Args:
            tenant_id: Tenant ID
            user_id: User parking the transaction
            items: List of cart items
            client_id: Optional client ID
            stylist_id: Optional stylist ID
            discount_total: Total discount amount
            tax: Tax amount
            tip: Tip amount
            notes: Optional notes
            customer_name: Customer name for identification
            customer_phone: Customer phone for identification
            
        Returns:
            Dict with parked transaction details
        """
        db = Database.get_db()
        
        # Calculate subtotal
        subtotal = sum(item["quantity"] * item["price"] - item.get("discount", 0) for item in items)
        
        # Calculate total
        total = subtotal - discount_total + tax + tip
        
        # Generate hold number
        hold_number = f"HOLD-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        # Create parked transaction
        parked_data = {
            "tenant_id": tenant_id,
            "hold_number": hold_number,
            "items": items,
            "subtotal": subtotal,
            "discount_total": discount_total,
            "tax": tax,
            "tip": tip,
            "total": total,
            "client_id": client_id,
            "stylist_id": stylist_id,
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "parked_by": user_id,
            "parked_at": datetime.now(timezone.utc),
            "status": "parked",
            "notes": notes,
            "expires_at": None  # No expiration by default
        }
        
        result = db.pos_parked_transactions.insert_one(parked_data)
        parked_id = str(result.inserted_id)
        
        logger.info(f"Transaction parked: {parked_id} by user: {user_id}")
        
        parked_data["id"] = parked_id
        parked_data["_id"] = result.inserted_id
        
        return parked_data
    
    @staticmethod
    def list_parked_transactions(tenant_id: str) -> List[Dict]:
        """
        List all parked transactions for a tenant
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            List of parked transactions
        """
        db = Database.get_db()
        
        parked = list(db.pos_parked_transactions.find({
            "tenant_id": tenant_id,
            "status": "parked"
        }).sort("parked_at", -1))
        
        for p in parked:
            p["id"] = str(p["_id"])
        
        return parked
    
    @staticmethod
    def get_parked_transaction(parked_id: str, tenant_id: str) -> Dict:
        """
        Get a parked transaction by ID
        
        Args:
            parked_id: Parked transaction ID
            tenant_id: Tenant ID
            
        Returns:
            Parked transaction details
        """
        db = Database.get_db()
        
        parked = db.pos_parked_transactions.find_one({
            "_id": ObjectId(parked_id),
            "tenant_id": tenant_id
        })
        
        if not parked:
            raise NotFoundException("Parked transaction not found")
        
        parked["id"] = str(parked["_id"])
        return parked
    
    @staticmethod
    def resume_parked_transaction(
        parked_id: str,
        tenant_id: str,
        user_id: str
    ) -> Dict:
        """
        Resume a parked transaction and convert it to active transaction
        
        Args:
            parked_id: Parked transaction ID
            tenant_id: Tenant ID
            user_id: User resuming the transaction
            
        Returns:
            New active transaction details
        """
        db = Database.get_db()
        
        # Get parked transaction
        parked = db.pos_parked_transactions.find_one({
            "_id": ObjectId(parked_id),
            "tenant_id": tenant_id,
            "status": "parked"
        })
        
        if not parked:
            raise NotFoundException("Parked transaction not found")
        
        # Create new active transaction from parked data
        transaction = POSService.create_transaction(
            tenant_id=tenant_id,
            user_id=user_id,
            items=parked["items"],
            client_id=parked.get("client_id"),
            stylist_id=parked.get("stylist_id"),
            discount_total=parked.get("discount_total", 0),
            tax=parked.get("tax", 0),
            tip=parked.get("tip", 0),
            notes=parked.get("notes")
        )
        
        # Mark parked transaction as resumed
        db.pos_parked_transactions.update_one(
            {"_id": ObjectId(parked_id)},
            {
                "$set": {
                    "status": "resumed",
                    "resumed_at": datetime.now(timezone.utc),
                    "resumed_by": user_id,
                    "transaction_id": transaction["id"]
                }
            }
        )
        
        logger.info(f"Parked transaction {parked_id} resumed as {transaction['id']}")
        
        return transaction
    
    @staticmethod
    def delete_parked_transaction(
        parked_id: str,
        tenant_id: str
    ):
        """
        Delete a parked transaction
        
        Args:
            parked_id: Parked transaction ID
            tenant_id: Tenant ID
        """
        db = Database.get_db()
        
        result = db.pos_parked_transactions.delete_one({
            "_id": ObjectId(parked_id),
            "tenant_id": tenant_id,
            "status": "parked"
        })
        
        if result.deleted_count == 0:
            raise NotFoundException("Parked transaction not found")
        
        logger.info(f"Parked transaction deleted: {parked_id}")

    @staticmethod
    def start_shift(
        tenant_id: str,
        user_id: str,
        opening_cash: float = 0,
        notes: Optional[str] = None
    ) -> Dict:
        """
        Start a new shift for a cashier
        
        Args:
            tenant_id: Tenant ID
            user_id: User starting the shift
            opening_cash: Opening cash amount
            notes: Optional notes
            
        Returns:
            Dict with shift details
        """
        db = Database.get_db()
        
        # Check if user already has an open shift
        existing_shift = db.pos_shifts.find_one({
            "tenant_id": tenant_id,
            "user_id": user_id,
            "status": "open"
        })
        
        if existing_shift:
            raise BadRequestException("User already has an open shift")
        
        # Create shift
        shift_data = {
            "tenant_id": tenant_id,
            "user_id": user_id,
            "start_time": datetime.now(timezone.utc),
            "opening_cash": opening_cash,
            "expected_cash": opening_cash,
            "status": "open",
            "notes": notes,
            "transactions": [],
            "total_sales": 0,
            "total_cash": 0,
            "total_card": 0,
            "total_tips": 0
        }
        
        result = db.pos_shifts.insert_one(shift_data)
        shift_id = str(result.inserted_id)
        
        logger.info(f"Shift started: {shift_id} by user: {user_id}")
        
        shift_data["id"] = shift_id
        shift_data["_id"] = result.inserted_id
        
        return shift_data
    
    @staticmethod
    def end_shift(
        tenant_id: str,
        user_id: str,
        closing_cash: float,
        notes: Optional[str] = None
    ) -> Dict:
        """
        End the current shift for a cashier
        
        Args:
            tenant_id: Tenant ID
            user_id: User ending the shift
            closing_cash: Actual closing cash amount
            notes: Optional notes
            
        Returns:
            Dict with shift summary
        """
        db = Database.get_db()
        
        # Get open shift
        shift = db.pos_shifts.find_one({
            "tenant_id": tenant_id,
            "user_id": user_id,
            "status": "open"
        })
        
        if not shift:
            raise NotFoundException("No open shift found for user")
        
        # Calculate variance
        variance = closing_cash - shift["expected_cash"]
        
        # Update shift
        db.pos_shifts.update_one(
            {"_id": shift["_id"]},
            {
                "$set": {
                    "end_time": datetime.now(timezone.utc),
                    "closing_cash": closing_cash,
                    "variance": variance,
                    "status": "closed",
                    "end_notes": notes
                }
            }
        )
        
        logger.info(f"Shift ended: {shift['_id']} by user: {user_id}")
        
        shift["id"] = str(shift["_id"])
        shift["end_time"] = datetime.now(timezone.utc)
        shift["closing_cash"] = closing_cash
        shift["variance"] = variance
        shift["status"] = "closed"
        shift["end_notes"] = notes
        
        return shift
    
    @staticmethod
    def get_current_shift(tenant_id: str, user_id: str) -> Optional[Dict]:
        """
        Get the current open shift for a user
        
        Args:
            tenant_id: Tenant ID
            user_id: User ID
            
        Returns:
            Current shift or None
        """
        db = Database.get_db()
        
        shift = db.pos_shifts.find_one({
            "tenant_id": tenant_id,
            "user_id": user_id,
            "status": "open"
        })
        
        if shift:
            shift["id"] = str(shift["_id"])
        
        return shift
    
    @staticmethod
    def list_shifts(
        tenant_id: str,
        user_id: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> List[Dict]:
        """
        List shifts with optional filters
        
        Args:
            tenant_id: Tenant ID
            user_id: Optional user ID filter
            date_from: Optional start date filter
            date_to: Optional end date filter
            
        Returns:
            List of shifts
        """
        db = Database.get_db()
        
        query = {"tenant_id": tenant_id}
        
        if user_id:
            query["user_id"] = user_id
        
        if date_from or date_to:
            query["start_time"] = {}
            if date_from:
                query["start_time"]["$gte"] = datetime.fromisoformat(date_from)
            if date_to:
                query["start_time"]["$lte"] = datetime.fromisoformat(date_to)
        
        shifts = list(db.pos_shifts.find(query).sort("start_time", -1))
        
        for shift in shifts:
            shift["id"] = str(shift["_id"])
        
        return shifts
    
    @staticmethod
    def record_shift_transaction(
        tenant_id: str,
        user_id: str,
        transaction_id: str,
        amount: float,
        payment_method: str
    ):
        """
        Record a transaction in the current shift
        
        Args:
            tenant_id: Tenant ID
            user_id: User ID
            transaction_id: Transaction ID
            amount: Transaction amount
            payment_method: Payment method used
        """
        db = Database.get_db()
        
        shift = db.pos_shifts.find_one({
            "tenant_id": tenant_id,
            "user_id": user_id,
            "status": "open"
        })
        
        if shift:
            update = {
                "$push": {
                    "transactions": {
                        "transaction_id": transaction_id,
                        "amount": amount,
                        "payment_method": payment_method,
                        "timestamp": datetime.now(timezone.utc)
                    }
                },
                "$inc": {
                    "total_sales": amount
                }
            }
            
            if payment_method == "cash":
                update["$inc"]["total_cash"] = amount
                update["$inc"]["expected_cash"] = amount
            elif payment_method == "card":
                update["$inc"]["total_card"] = amount
            
            db.pos_shifts.update_one({"_id": shift["_id"]}, update)
    
    @staticmethod
    def check_inventory_alerts(
        tenant_id: str,
        product_id: str,
        quantity_needed: int
    ) -> Dict:
        """
        Check inventory levels and generate alerts
        
        Args:
            tenant_id: Tenant ID
            product_id: Product ID
            quantity_needed: Quantity needed for sale
            
        Returns:
            Dict with alert information
        """
        db = Database.get_db()
        
        product = db.inventory.find_one({
            "_id": ObjectId(product_id),
            "tenant_id": tenant_id
        })
        
        if not product:
            return {
                "alert_type": "not_found",
                "message": "Product not found",
                "available": False
            }
        
        current_stock = product.get("quantity", 0)
        low_stock_threshold = product.get("low_stock_threshold", 10)
        
        if current_stock < quantity_needed:
            return {
                "alert_type": "out_of_stock",
                "message": f"Insufficient stock. Available: {current_stock}, Needed: {quantity_needed}",
                "available": False,
                "current_stock": current_stock,
                "quantity_needed": quantity_needed
            }
        
        if current_stock - quantity_needed <= low_stock_threshold:
            return {
                "alert_type": "low_stock",
                "message": f"Low stock warning. After sale: {current_stock - quantity_needed} remaining",
                "available": True,
                "current_stock": current_stock,
                "quantity_needed": quantity_needed,
                "remaining_after_sale": current_stock - quantity_needed,
                "threshold": low_stock_threshold
            }
        
        return {
            "alert_type": "ok",
            "message": "Stock level OK",
            "available": True,
            "current_stock": current_stock
        }
    
    @staticmethod
    def get_alternative_products(
        tenant_id: str,
        product_id: str,
        limit: int = 5
    ) -> List[Dict]:
        """
        Get alternative products when item is out of stock
        
        Args:
            tenant_id: Tenant ID
            product_id: Original product ID
            limit: Maximum alternatives to return
            
        Returns:
            List of alternative products
        """
        db = Database.get_db()
        
        # Get original product
        product = db.inventory.find_one({
            "_id": ObjectId(product_id),
            "tenant_id": tenant_id
        })
        
        if not product:
            return []
        
        # Find similar products (same category, in stock)
        query = {
            "tenant_id": tenant_id,
            "_id": {"$ne": ObjectId(product_id)},
            "quantity": {"$gt": 0}
        }
        
        if product.get("category"):
            query["category"] = product["category"]
        
        alternatives = list(db.inventory.find(query).limit(limit))
        
        for alt in alternatives:
            alt["id"] = str(alt["_id"])
        
        return alternatives
    
    @staticmethod
    def lookup_barcode(
        tenant_id: str,
        barcode: str
    ) -> Optional[Dict]:
        """
        Lookup product by barcode
        
        Args:
            tenant_id: Tenant ID
            barcode: Barcode string
            
        Returns:
            Product details or None
        """
        db = Database.get_db()
        
        # Try to find product by barcode
        product = db.inventory.find_one({
            "tenant_id": tenant_id,
            "barcode": barcode
        })
        
        if product:
            product["id"] = str(product["_id"])
            return product
        
        # Try to find service by barcode
        service = db.services.find_one({
            "tenant_id": tenant_id,
            "barcode": barcode
        })
        
        if service:
            service["id"] = str(service["_id"])
            service["type"] = "service"
            return service
        
        return None
    
    @staticmethod
    def generate_receipt_qr(
        transaction_id: str,
        tenant_id: str
    ) -> str:
        """
        Generate QR code data for receipt
        
        Args:
            transaction_id: Transaction ID
            tenant_id: Tenant ID
            
        Returns:
            QR code data string (URL or JSON)
        """
        # Generate review/feedback URL
        base_url = "https://app.salonflow.com"  # Replace with actual domain
        qr_data = f"{base_url}/review/{tenant_id}/{transaction_id}"
        
        return qr_data
    
    @staticmethod
    def get_receipt_template(
        tenant_id: str
    ) -> Dict:
        """
        Get custom receipt template for tenant
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Receipt template configuration
        """
        db = Database.get_db()
        
        # Get tenant settings
        tenant = db.tenants.find_one({"_id": ObjectId(tenant_id)})
        
        if not tenant:
            return POSService._get_default_receipt_template()
        
        # Get custom template if exists
        template = tenant.get("receipt_template")
        
        if template:
            return template
        
        return POSService._get_default_receipt_template()
    
    @staticmethod
    def _get_default_receipt_template() -> Dict:
        """Get default receipt template"""
        return {
            "show_logo": True,
            "logo_url": None,
            "header_text": "Thank you for your business!",
            "footer_text": "Please visit us again",
            "show_social_media": True,
            "social_media": {
                "facebook": None,
                "instagram": None,
                "twitter": None
            },
            "show_qr_code": True,
            "promotional_message": None,
            "show_loyalty_info": True
        }
    
    @staticmethod
    def save_receipt_template(
        tenant_id: str,
        template: Dict
    ) -> Dict:
        """
        Save custom receipt template
        
        Args:
            tenant_id: Tenant ID
            template: Template configuration
            
        Returns:
            Saved template
        """
        db = Database.get_db()
        
        db.tenants.update_one(
            {"_id": ObjectId(tenant_id)},
            {"$set": {"receipt_template": template}}
        )
        
        logger.info(f"Receipt template saved for tenant: {tenant_id}")
        
        return template
    
    # Feature 21: Gift Cards (Enhanced)
    @staticmethod
    def create_gift_card(
        tenant_id: str,
        amount: float,
        card_type: str = "physical",
        recipient_name: Optional[str] = None,
        recipient_email: Optional[str] = None,
        message: Optional[str] = None,
        expiration_months: int = 12,
        created_by: Optional[str] = None,
        design_theme: str = "default",
        activation_required: bool = False,
        pin: Optional[str] = None
    ) -> Dict:
        """Create a new gift card with enhanced features"""
        db = Database.get_db()
        
        # Generate unique card number
        card_number = f"GC-{uuid.uuid4().hex[:12].upper()}"
        
        # Calculate expiration date
        from dateutil.relativedelta import relativedelta
        expires_at = datetime.now(timezone.utc) + relativedelta(months=expiration_months)
        
        # Hash PIN if provided
        hashed_pin = None
        pin_enabled = False
        if pin:
            import bcrypt
            hashed_pin = bcrypt.hashpw(pin.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            pin_enabled = True
        
        # Determine initial status
        initial_status = "inactive" if activation_required else "active"
        if card_type == "digital":
            initial_status = "active"
        
        gift_card_data = {
            "tenant_id": tenant_id,
            "card_number": card_number,
            "amount": amount,
            "balance": amount,
            "card_type": card_type,
            "status": initial_status,
            "recipient_name": recipient_name,
            "recipient_email": recipient_email,
            "message": message,
            "created_at": datetime.now(timezone.utc),
            "created_by": created_by,
            "expires_at": expires_at,
            "redeemed_at": None,
            "transactions": [],
            # New fields
            "delivery_status": "pending" if card_type == "digital" else None,
            "delivery_method": "email" if card_type == "digital" else None,
            "delivery_attempts": 0,
            "last_delivery_attempt": None,
            "scheduled_delivery": None,
            "pin": hashed_pin,
            "pin_enabled": pin_enabled,
            "activation_required": activation_required,
            "activated_at": None,
            "activated_by": None,
            "terms_version": "1.0",
            "design_theme": design_theme,
            "certificate_url": None,
            "qr_code_data": card_number,
            "security_flags": [],
            "suspicious_activity_count": 0,
            "last_balance_check": None,
            "balance_check_count_today": 0,
            "audit_log": [
                {
                    "action": "created",
                    "user_id": created_by,
                    "timestamp": datetime.now(timezone.utc),
                    "details": {"card_type": card_type, "amount": amount}
                }
            ]
        }
        
        result = db.gift_cards.insert_one(gift_card_data)
        gift_card_id = str(result.inserted_id)
        
        logger.info(f"Gift card created: {card_number} for tenant: {tenant_id}")
        
        gift_card_data["id"] = gift_card_id
        gift_card_data["_id"] = result.inserted_id
        
        return gift_card_data
    
    @staticmethod
    def get_gift_card_balance(
        tenant_id: str,
        card_number: str
    ) -> Dict:
        """Get gift card balance"""
        db = Database.get_db()
        
        gift_card = db.gift_cards.find_one({
            "tenant_id": tenant_id,
            "card_number": card_number
        })
        
        if not gift_card:
            raise NotFoundException("Gift card not found")
        
        # Check if expired
        if gift_card["expires_at"] < datetime.now(timezone.utc):
            if gift_card["status"] != "expired":
                db.gift_cards.update_one(
                    {"_id": gift_card["_id"]},
                    {"$set": {"status": "expired"}}
                )
            gift_card["status"] = "expired"
        
        return {
            "card_number": gift_card["card_number"],
            "balance": gift_card["balance"],
            "status": gift_card["status"],
            "expires_at": gift_card["expires_at"]
        }
    
    @staticmethod
    def redeem_gift_card(
        tenant_id: str,
        card_number: str,
        amount: float,
        transaction_id: str,
        location: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Dict:
        """Redeem gift card with fraud detection"""
        db = Database.get_db()
        
        from app.services.fraud_detection_service import FraudDetectionService
        
        gift_card = db.gift_cards.find_one({
            "tenant_id": tenant_id,
            "card_number": card_number
        })
        
        if not gift_card:
            # Record failed attempt
            FraudDetectionService.record_redemption_attempt(
                card_number=card_number,
                tenant_id=tenant_id,
                amount=amount,
                success=False,
                ip_address=ip_address,
                location=location,
                error_reason="card_not_found"
            )
            raise NotFoundException("Gift card not found")
        
        # Check if card is suspended
        if gift_card["status"] == "suspended":
            FraudDetectionService.record_redemption_attempt(
                card_number=card_number,
                tenant_id=tenant_id,
                amount=amount,
                success=False,
                ip_address=ip_address,
                location=location,
                error_reason="card_suspended"
            )
            raise BadRequestException("Gift card is suspended pending investigation. Please contact support.")
        
        if gift_card["status"] != "active":
            FraudDetectionService.record_redemption_attempt(
                card_number=card_number,
                tenant_id=tenant_id,
                amount=amount,
                success=False,
                ip_address=ip_address,
                location=location,
                error_reason=f"card_{gift_card['status']}"
            )
            raise BadRequestException(f"Gift card is {gift_card['status']}")
        
        if gift_card["expires_at"] < datetime.now(timezone.utc):
            db.gift_cards.update_one(
                {"_id": gift_card["_id"]},
                {"$set": {"status": "expired"}}
            )
            FraudDetectionService.record_redemption_attempt(
                card_number=card_number,
                tenant_id=tenant_id,
                amount=amount,
                success=False,
                ip_address=ip_address,
                location=location,
                error_reason="card_expired"
            )
            raise BadRequestException("Gift card has expired")
        
        if gift_card["balance"] < amount:
            FraudDetectionService.record_redemption_attempt(
                card_number=card_number,
                tenant_id=tenant_id,
                amount=amount,
                success=False,
                ip_address=ip_address,
                location=location,
                error_reason="insufficient_balance"
            )
            raise BadRequestException(f"Insufficient balance. Available: {gift_card['balance']}")
        
        # Fraud detection checks
        card_id = str(gift_card["_id"])
        
        # Check velocity (max 3 redemptions per day)
        velocity_check = FraudDetectionService.check_redemption_velocity(
            card_number=card_number,
            tenant_id=tenant_id
        )
        
        if velocity_check.get("suspicious"):
            # Flag card and notify staff
            FraudDetectionService.flag_card(
                card_id=card_id,
                reason="high_velocity",
                severity="medium",
                details=velocity_check
            )
            
            # Send notification asynchronously
            import asyncio
            try:
                asyncio.create_task(
                    FraudDetectionService.notify_staff_of_fraud(
                        tenant_id=tenant_id,
                        card_number=card_number,
                        reason="high_velocity",
                        severity="medium",
                        details=velocity_check
                    )
                )
            except Exception as e:
                logger.error(f"Failed to send fraud notification: {str(e)}")
            
            FraudDetectionService.record_redemption_attempt(
                card_number=card_number,
                tenant_id=tenant_id,
                amount=amount,
                success=False,
                ip_address=ip_address,
                location=location,
                error_reason="velocity_limit_exceeded"
            )
            raise BadRequestException("Too many redemptions today. Please try again tomorrow.")
        
        # Check for rapid succession redemptions
        rapid_check = FraudDetectionService.check_rapid_succession_redemptions(
            card_number=card_number,
            tenant_id=tenant_id
        )
        
        if rapid_check.get("suspicious"):
            FraudDetectionService.flag_card(
                card_id=card_id,
                reason="rapid_succession_redemptions",
                severity="high",
                details=rapid_check
            )
            
            # Send notification
            import asyncio
            try:
                asyncio.create_task(
                    FraudDetectionService.notify_staff_of_fraud(
                        tenant_id=tenant_id,
                        card_number=card_number,
                        reason="rapid_succession_redemptions",
                        severity="high",
                        details=rapid_check
                    )
                )
            except Exception as e:
                logger.error(f"Failed to send fraud notification: {str(e)}")
        
        # Check for unusual patterns
        pattern_check = FraudDetectionService.check_unusual_pattern(
            card_number=card_number,
            amount=amount,
            location=location,
            tenant_id=tenant_id
        )
        
        if pattern_check.get("suspicious"):
            FraudDetectionService.flag_card(
                card_id=card_id,
                reason=pattern_check.get("reason", "unusual_pattern"),
                severity="medium",
                details=pattern_check
            )
            
            # Send notification
            import asyncio
            try:
                asyncio.create_task(
                    FraudDetectionService.notify_staff_of_fraud(
                        tenant_id=tenant_id,
                        card_number=card_number,
                        reason=pattern_check.get("reason", "unusual_pattern"),
                        severity="medium",
                        details=pattern_check
                    )
                )
            except Exception as e:
                logger.error(f"Failed to send fraud notification: {str(e)}")
        
        # Check for failed redemption attempts
        failed_check = FraudDetectionService.check_failed_redemptions(
            card_number=card_number,
            tenant_id=tenant_id
        )
        
        if failed_check.get("suspicious"):
            FraudDetectionService.flag_card(
                card_id=card_id,
                reason="multiple_failed_redemptions",
                severity="high",
                details=failed_check
            )
            
            # Suspend card automatically
            FraudDetectionService.suspend_card(
                card_id=card_id,
                reason="Multiple failed redemption attempts detected",
                suspended_by="system"
            )
            
            # Send notification
            import asyncio
            try:
                asyncio.create_task(
                    FraudDetectionService.notify_staff_of_fraud(
                        tenant_id=tenant_id,
                        card_number=card_number,
                        reason="multiple_failed_redemptions",
                        severity="high",
                        details=failed_check
                    )
                )
            except Exception as e:
                logger.error(f"Failed to send fraud notification: {str(e)}")
            
            FraudDetectionService.record_redemption_attempt(
                card_number=card_number,
                tenant_id=tenant_id,
                amount=amount,
                success=False,
                ip_address=ip_address,
                location=location,
                error_reason="card_suspended_fraud"
            )
            raise BadRequestException("Card has been suspended due to suspicious activity. Please contact support.")
        
        # Proceed with redemption
        new_balance = gift_card["balance"] - amount
        
        # Update gift card
        update_data = {
            "$set": {"balance": new_balance},
            "$push": {
                "transactions": {
                    "type": "redeem",
                    "transaction_id": transaction_id,
                    "amount": amount,
                    "balance_after": new_balance,
                    "timestamp": datetime.now(timezone.utc),
                    "location": location
                },
                "audit_log": {
                    "action": "redeemed",
                    "user_id": None,
                    "ip_address": ip_address,
                    "timestamp": datetime.now(timezone.utc),
                    "details": {
                        "amount": amount,
                        "transaction_id": transaction_id,
                        "location": location
                    }
                }
            }
        }
        
        if new_balance == 0:
            update_data["$set"]["status"] = "redeemed"
            update_data["$set"]["redeemed_at"] = datetime.now(timezone.utc)
        
        db.gift_cards.update_one({"_id": gift_card["_id"]}, update_data)
        
        # Record successful redemption attempt
        FraudDetectionService.record_redemption_attempt(
            card_number=card_number,
            tenant_id=tenant_id,
            amount=amount,
            success=True,
            ip_address=ip_address,
            location=location
        )
        
        logger.info(f"Gift card redeemed: {card_number}, amount: {amount}")
        
        return {
            "card_number": card_number,
            "redeemed_amount": amount,
            "remaining_balance": new_balance,
            "status": "redeemed" if new_balance == 0 else "active"
        }
    
    @staticmethod
    def list_gift_cards(
        tenant_id: str,
        status: Optional[str] = None
    ) -> List[Dict]:
        """List gift cards"""
        db = Database.get_db()
        
        query = {"tenant_id": tenant_id}
        if status:
            query["status"] = status
        
        gift_cards = list(db.gift_cards.find(query).sort("created_at", -1))
        
        for gc in gift_cards:
            gc["id"] = str(gc["_id"])
        
        return gift_cards
    
    @staticmethod
    def activate_gift_card(
        tenant_id: str,
        card_number: str,
        activated_by: str
    ) -> Dict:
        """Activate an inactive gift card"""
        db = Database.get_db()
        
        gift_card = db.gift_cards.find_one({
            "tenant_id": tenant_id,
            "card_number": card_number
        })
        
        if not gift_card:
            raise NotFoundException("Gift card not found")
        
        if gift_card["status"] != "inactive":
            raise BadRequestException(f"Gift card cannot be activated. Current status: {gift_card['status']}")
        
        now = datetime.now(timezone.utc)
        
        db.gift_cards.update_one(
            {"_id": gift_card["_id"]},
            {
                "$set": {
                    "status": "active",
                    "activated_at": now,
                    "activated_by": activated_by
                },
                "$push": {
                    "audit_log": {
                        "action": "activated",
                        "user_id": activated_by,
                        "timestamp": now,
                        "details": {}
                    }
                }
            }
        )
        
        logger.info(f"Gift card activated: {card_number} by {activated_by}")
        
        return {"card_number": card_number, "status": "active"}
    
    @staticmethod
    def void_gift_card(
        tenant_id: str,
        card_number: str,
        reason: str,
        voided_by: str,
        refund: bool = False
    ) -> Dict:
        """Void a gift card"""
        db = Database.get_db()
        
        gift_card = db.gift_cards.find_one({
            "tenant_id": tenant_id,
            "card_number": card_number
        })
        
        if not gift_card:
            raise NotFoundException("Gift card not found")
        
        now = datetime.now(timezone.utc)
        
        db.gift_cards.update_one(
            {"_id": gift_card["_id"]},
            {
                "$set": {
                    "status": "voided",
                    "voided_at": now,
                    "voided_by": voided_by,
                    "void_reason": reason
                },
                "$push": {
                    "audit_log": {
                        "action": "voided",
                        "user_id": voided_by,
                        "timestamp": now,
                        "details": {"reason": reason, "refund": refund}
                    }
                }
            }
        )
        
        logger.info(f"Gift card voided: {card_number} by {voided_by}, reason: {reason}")
        
        return {
            "card_number": card_number,
            "status": "voided",
            "refund_amount": gift_card["balance"] if refund else 0
        }
    
    @staticmethod
    def reload_gift_card(
        tenant_id: str,
        card_number: str,
        amount: float,
        reload_by: str
    ) -> Dict:
        """Reload (add value to) a gift card"""
        db = Database.get_db()
        
        gift_card = db.gift_cards.find_one({
            "tenant_id": tenant_id,
            "card_number": card_number
        })
        
        if not gift_card:
            raise NotFoundException("Gift card not found")
        
        if gift_card["status"] not in ["active", "redeemed"]:
            raise BadRequestException(f"Cannot reload card with status: {gift_card['status']}")
        
        from dateutil.relativedelta import relativedelta
        now = datetime.now(timezone.utc)
        new_expiration = now + relativedelta(months=12)
        new_balance = gift_card["balance"] + amount
        
        db.gift_cards.update_one(
            {"_id": gift_card["_id"]},
            {
                "$set": {
                    "balance": new_balance,
                    "expires_at": new_expiration,
                    "status": "active"
                },
                "$push": {
                    "transactions": {
                        "type": "reload",
                        "amount": amount,
                        "balance_after": new_balance,
                        "timestamp": now
                    },
                    "audit_log": {
                        "action": "reloaded",
                        "user_id": reload_by,
                        "timestamp": now,
                        "details": {"reload_amount": amount}
                    }
                }
            }
        )
        
        logger.info(f"Gift card reloaded: {card_number}, amount: {amount}")
        
        return {
            "card_number": card_number,
            "reload_amount": amount,
            "new_balance": new_balance,
            "new_expiration": new_expiration
        }
    
    @staticmethod
    def set_gift_card_pin(
        tenant_id: str,
        card_number: str,
        pin: str
    ) -> Dict:
        """Set or change PIN for a gift card"""
        db = Database.get_db()
        
        if not pin or len(pin) < 4 or len(pin) > 6:
            raise BadRequestException("PIN must be 4-6 digits")
        
        gift_card = db.gift_cards.find_one({
            "tenant_id": tenant_id,
            "card_number": card_number
        })
        
        if not gift_card:
            raise NotFoundException("Gift card not found")
        
        import bcrypt
        hashed_pin = bcrypt.hashpw(pin.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        db.gift_cards.update_one(
            {"_id": gift_card["_id"]},
            {
                "$set": {
                    "pin": hashed_pin,
                    "pin_enabled": True
                },
                "$push": {
                    "audit_log": {
                        "action": "pin_set",
                        "timestamp": datetime.now(timezone.utc),
                        "details": {}
                    }
                }
            }
        )
        
        logger.info(f"PIN set for gift card: {card_number}")
        
        return {"card_number": card_number, "pin_enabled": True}
    
    @staticmethod
    def validate_gift_card_pin(
        tenant_id: str,
        card_number: str,
        pin: str
    ) -> bool:
        """Validate PIN for a gift card"""
        db = Database.get_db()
        
        gift_card = db.gift_cards.find_one({
            "tenant_id": tenant_id,
            "card_number": card_number
        })
        
        if not gift_card or not gift_card.get("pin_enabled"):
            return False
        
        import bcrypt
        return bcrypt.checkpw(pin.encode('utf-8'), gift_card["pin"].encode('utf-8'))
    
    @staticmethod
    def transfer_gift_card_balance(
        tenant_id: str,
        source_card: str,
        destination_card: Optional[str],
        amount: float,
        transferred_by: str
    ) -> Dict:
        """
        Transfer balance from one gift card to another
        
        Args:
            tenant_id: Tenant ID
            source_card: Source card number
            destination_card: Destination card number (optional, creates new if not provided)
            amount: Amount to transfer
            transferred_by: User ID who initiated transfer
            
        Returns:
            Dict with transfer details
            
        Raises:
            BadRequestException: If daily transfer limit exceeded or insufficient balance
            NotFoundException: If source or destination card not found
        """
        db = Database.get_db()
        
        # Get source card
        source = db.gift_cards.find_one({
            "tenant_id": tenant_id,
            "card_number": source_card
        })
        
        if not source:
            raise NotFoundException("Source gift card not found")
        
        # Check if source card is active
        if source["status"] != "active":
            raise BadRequestException(f"Source card is {source['status']} and cannot be used for transfers")
        
        # Check if expired
        if source["expires_at"] < datetime.now(timezone.utc):
            raise BadRequestException("Source card has expired")
        
        # Check balance
        if source["balance"] < amount:
            raise BadRequestException(f"Insufficient balance. Available: ₦{source['balance']:,.0f}")
        
        # Validate amount
        if amount <= 0:
            raise BadRequestException("Transfer amount must be greater than 0")
        
        now = datetime.now(timezone.utc)
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Check daily transfer limit (1 per card per day)
        transfer_count_today = sum(
            1 for t in source.get("transactions", [])
            if t.get("type") == "transfer_out" and t.get("timestamp") >= today_start
        )
        
        if transfer_count_today >= 1:
            raise BadRequestException("Daily transfer limit reached. You can only transfer once per day per card.")
        
        # If no destination card, create new one
        created_new_card = False
        if not destination_card:
            new_card = POSService.create_gift_card(
                tenant_id=tenant_id,
                amount=0,  # Start with 0, will add transfer amount
                card_type="digital",
                created_by=transferred_by,
                recipient_name=source.get("recipient_name"),
                recipient_email=source.get("recipient_email")
            )
            destination_card = new_card["card_number"]
            created_new_card = True
        else:
            # Get destination card
            dest = db.gift_cards.find_one({
                "tenant_id": tenant_id,
                "card_number": destination_card
            })
            
            if not dest:
                raise NotFoundException("Destination gift card not found")
            
            # Check if destination card can receive transfers
            if dest["status"] not in ["active", "inactive"]:
                raise BadRequestException(f"Destination card is {dest['status']} and cannot receive transfers")
        
        # Update source card
        new_source_balance = source["balance"] - amount
        db.gift_cards.update_one(
            {"_id": source["_id"]},
            {
                "$set": {
                    "balance": new_source_balance,
                    "status": "redeemed" if new_source_balance == 0 else source["status"]
                },
                "$push": {
                    "transactions": {
                        "type": "transfer_out",
                        "amount": amount,
                        "balance_after": new_source_balance,
                        "timestamp": now,
                        "notes": f"Transferred to {destination_card}"
                    },
                    "audit_log": {
                        "action": "transfer_out",
                        "user_id": transferred_by,
                        "timestamp": now,
                        "details": {
                            "destination": destination_card,
                            "amount": amount,
                            "new_balance": new_source_balance
                        }
                    }
                }
            }
        )
        
        # Update destination card
        dest_card = db.gift_cards.find_one({"card_number": destination_card})
        new_dest_balance = dest_card["balance"] + amount
        
        db.gift_cards.update_one(
            {"_id": dest_card["_id"]},
            {
                "$set": {
                    "balance": new_dest_balance,
                    "status": "active"  # Activate destination card if it was inactive
                },
                "$push": {
                    "transactions": {
                        "type": "transfer_in",
                        "amount": amount,
                        "balance_after": new_dest_balance,
                        "timestamp": now,
                        "notes": f"Received from {source_card}"
                    },
                    "audit_log": {
                        "action": "transfer_in",
                        "user_id": transferred_by,
                        "timestamp": now,
                        "details": {
                            "source": source_card,
                            "amount": amount,
                            "new_balance": new_dest_balance
                        }
                    }
                }
            }
        )
        
        logger.info(f"Transfer completed: {source_card} -> {destination_card}, amount: ₦{amount:,.0f}")
        
        # Send confirmation emails to both parties (async task)
        try:
            from app.tasks.gift_card_tasks import send_transfer_confirmation_emails
            send_transfer_confirmation_emails.delay(
                source_card_id=str(source["_id"]),
                dest_card_id=str(dest_card["_id"]),
                amount=amount,
                tenant_id=tenant_id
            )
        except Exception as e:
            logger.warning(f"Failed to queue transfer confirmation emails: {str(e)}")
        
        return {
            "success": True,
            "source_card": source_card,
            "destination_card": destination_card,
            "amount": amount,
            "source_balance": new_source_balance,
            "destination_balance": new_dest_balance,
            "created_new_card": created_new_card,
            "transfer_date": now.isoformat()
        }
    
    # Feature 22: Multi-Currency Support
    @staticmethod
    def convert_currency(
        tenant_id: str,
        from_currency: str,
        to_currency: str,
        amount: float
    ) -> Dict:
        """Convert currency"""
        db = Database.get_db()
        
        # Get exchange rates
        rates = db.exchange_rates.find_one({"tenant_id": tenant_id})
        
        if not rates:
            # Use default rates (USD as base)
            rates = {
                "base_currency": "USD",
                "rates": {
                    "USD": 1.0,
                    "EUR": 0.85,
                    "GBP": 0.73,
                    "CAD": 1.25,
                    "AUD": 1.35
                }
            }
        
        from_rate = rates["rates"].get(from_currency, 1.0)
        to_rate = rates["rates"].get(to_currency, 1.0)
        
        # Convert to base currency first, then to target
        base_amount = amount / from_rate
        converted_amount = base_amount * to_rate
        exchange_rate = to_rate / from_rate
        
        return {
            "from_currency": from_currency,
            "to_currency": to_currency,
            "from_amount": amount,
            "to_amount": round(converted_amount, 2),
            "exchange_rate": round(exchange_rate, 4),
            "timestamp": datetime.now(timezone.utc)
        }
    
    @staticmethod
    def update_exchange_rate(
        tenant_id: str,
        currency_code: str,
        rate: float
    ) -> Dict:
        """Update exchange rate"""
        db = Database.get_db()
        
        db.exchange_rates.update_one(
            {"tenant_id": tenant_id},
            {
                "$set": {
                    f"rates.{currency_code}": rate,
                    "updated_at": datetime.now(timezone.utc)
                }
            },
            upsert=True
        )
        
        logger.info(f"Exchange rate updated: {currency_code} = {rate}")
        
        return {
            "currency_code": currency_code,
            "rate": rate,
            "status": "success"
        }
    
    @staticmethod
    def get_exchange_rates(tenant_id: str) -> Dict:
        """Get all exchange rates"""
        db = Database.get_db()
        
        rates = db.exchange_rates.find_one({"tenant_id": tenant_id})
        
        if not rates:
            return {
                "base_currency": "USD",
                "rates": {
                    "USD": 1.0,
                    "EUR": 0.85,
                    "GBP": 0.73,
                    "CAD": 1.25,
                    "AUD": 1.35
                },
                "updated_at": datetime.now(timezone.utc)
            }
        
        return rates
    
    # Feature 23: Customer Notes at Checkout
    @staticmethod
    def get_customer_notes(
        tenant_id: str,
        client_id: str
    ) -> Dict:
        """Get customer notes and preferences for checkout"""
        db = Database.get_db()
        
        # Get client
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id
        })
        
        if not client:
            raise NotFoundException("Client not found")
        
        # Get purchase history
        transactions = list(db.pos_transactions.find({
            "tenant_id": tenant_id,
            "client_id": client_id,
            "status": "completed"
        }).sort("created_at", -1).limit(10))
        
        # Calculate stats
        total_spent = sum(t.get("total", 0) for t in transactions)
        visit_count = len(transactions)
        last_visit = transactions[0]["created_at"] if transactions else None
        
        # Get frequently purchased items
        item_counts = {}
        for t in transactions:
            for item in t.get("items", []):
                item_name = item.get("item_name")
                if item_name:
                    item_counts[item_name] = item_counts.get(item_name, 0) + 1
        
        recommended_products = [
            {"name": name, "purchase_count": count}
            for name, count in sorted(item_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        # Format purchase history
        purchase_history = [
            {
                "date": t["created_at"],
                "transaction_number": t["transaction_number"],
                "total": t["total"],
                "items_count": len(t.get("items", []))
            }
            for t in transactions
        ]
        
        return {
            "client_id": client_id,
            "preferences": client.get("preferences", {}),
            "allergies": client.get("allergies", []),
            "special_requirements": client.get("special_requirements"),
            "purchase_history": purchase_history,
            "recommended_products": recommended_products,
            "last_visit": last_visit,
            "total_spent": total_spent,
            "visit_count": visit_count
        }
    
    # Feature 24: Analytics Dashboard
    @staticmethod
    def get_pos_analytics(
        tenant_id: str,
        date_from: str,
        date_to: str,
        interval: str = "day"
    ) -> Dict:
        """Get POS analytics"""
        db = Database.get_db()
        
        start_date = datetime.fromisoformat(f"{date_from}T00:00:00")
        end_date = datetime.fromisoformat(f"{date_to}T23:59:59")
        
        # Get transactions
        transactions = list(db.pos_transactions.find({
            "tenant_id": tenant_id,
            "created_at": {"$gte": start_date, "$lte": end_date},
            "status": "completed"
        }))
        
        # Calculate totals
        total_sales = sum(t.get("total", 0) for t in transactions)
        total_transactions = len(transactions)
        average_transaction = total_sales / total_transactions if total_transactions > 0 else 0
        
        # Best selling items
        item_sales = {}
        for t in transactions:
            for item in t.get("items", []):
                item_name = item.get("item_name")
                if item_name:
                    if item_name not in item_sales:
                        item_sales[item_name] = {"name": item_name, "quantity": 0, "revenue": 0}
                    item_sales[item_name]["quantity"] += item.get("quantity", 0)
                    item_sales[item_name]["revenue"] += item.get("price", 0) * item.get("quantity", 0)
        
        best_selling_items = sorted(
            item_sales.values(),
            key=lambda x: x["revenue"],
            reverse=True
        )[:10]
        
        # Peak hours
        hour_sales = {}
        for t in transactions:
            hour = t["created_at"].hour
            if hour not in hour_sales:
                hour_sales[hour] = {"hour": hour, "transactions": 0, "revenue": 0}
            hour_sales[hour]["transactions"] += 1
            hour_sales[hour]["revenue"] += t.get("total", 0)
        
        peak_hours = sorted(
            hour_sales.values(),
            key=lambda x: x["revenue"],
            reverse=True
        )[:5]
        
        # Stylist performance
        stylist_sales = {}
        for t in transactions:
            stylist_id = t.get("stylist_id")
            if stylist_id:
                if stylist_id not in stylist_sales:
                    stylist_sales[stylist_id] = {
                        "stylist_id": stylist_id,
                        "transactions": 0,
                        "revenue": 0
                    }
                stylist_sales[stylist_id]["transactions"] += 1
                stylist_sales[stylist_id]["revenue"] += t.get("total", 0)
        
        stylist_performance = sorted(
            stylist_sales.values(),
            key=lambda x: x["revenue"],
            reverse=True
        )
        
        # Revenue trend
        revenue_trend = []
        if interval == "hour":
            for hour in range(24):
                hour_data = hour_sales.get(hour, {"hour": hour, "transactions": 0, "revenue": 0})
                revenue_trend.append(hour_data)
        else:
            # Daily trend
            date_sales = {}
            for t in transactions:
                date_key = t["created_at"].strftime("%Y-%m-%d")
                if date_key not in date_sales:
                    date_sales[date_key] = {"date": date_key, "transactions": 0, "revenue": 0}
                date_sales[date_key]["transactions"] += 1
                date_sales[date_key]["revenue"] += t.get("total", 0)
            
            revenue_trend = sorted(date_sales.values(), key=lambda x: x["date"])
        
        # Payment method breakdown
        payment_breakdown = {}
        for t in transactions:
            for payment in t.get("payments", []):
                method = payment.get("method", "unknown")
                payment_breakdown[method] = payment_breakdown.get(method, 0) + payment.get("amount", 0)
        
        # Category performance
        category_sales = {}
        for t in transactions:
            for item in t.get("items", []):
                item_type = item.get("type", "unknown")
                if item_type not in category_sales:
                    category_sales[item_type] = {"category": item_type, "quantity": 0, "revenue": 0}
                category_sales[item_type]["quantity"] += item.get("quantity", 0)
                category_sales[item_type]["revenue"] += item.get("price", 0) * item.get("quantity", 0)
        
        category_performance = list(category_sales.values())
        
        return {
            "date_from": date_from,
            "date_to": date_to,
            "total_sales": total_sales,
            "total_transactions": total_transactions,
            "average_transaction": average_transaction,
            "best_selling_items": best_selling_items,
            "peak_hours": peak_hours,
            "stylist_performance": stylist_performance,
            "revenue_trend": revenue_trend,
            "category_performance": category_performance,
            "payment_method_breakdown": payment_breakdown
        }
    
    # Feature 25: Receipt Options
    @staticmethod
    async def send_receipt(
        tenant_id: str,
        transaction_id: str,
        method: str,
        recipient: Optional[str] = None,
        save_preference: bool = False
    ) -> Dict:
        """Send receipt via email, SMS, or print"""
        db = Database.get_db()
        
        # Get transaction
        transaction = db.pos_transactions.find_one({
            "_id": ObjectId(transaction_id),
            "tenant_id": tenant_id
        })
        
        if not transaction:
            raise NotFoundException("Transaction not found")
        
        if method == "email":
            if not recipient:
                raise BadRequestException("Email address required")
            
            # Send receipt email
            from app.services.email_service import email_service
            
            try:
                # Format receipt content
                receipt_html = POSService._format_receipt_html(transaction)
                
                success = await email_service.send_email(
                    to=recipient,
                    subject=f"Receipt - {transaction.get('transaction_number', 'N/A')}",
                    html=receipt_html
                )
                
                if not success:
                    raise BadRequestException("Failed to send email")
                
                logger.info(f"Receipt email sent to {recipient} for transaction {transaction_id}")
                message = f"Receipt sent to {recipient}"
            except Exception as e:
                logger.error(f"Failed to send receipt email: {str(e)}")
                raise BadRequestException(f"Failed to send email: {str(e)}")
            
        elif method == "sms":
            if not recipient:
                raise BadRequestException("Phone number required")
            
            # Send receipt SMS via Termii
            from app.services.termii_service import send_sms
            
            try:
                # Format receipt content for SMS
                receipt_text = POSService._format_receipt_sms(transaction)
                
                success = await send_sms(
                    phone=recipient,
                    message=receipt_text
                )
                
                if not success:
                    raise BadRequestException("Failed to send SMS")
                
                logger.info(f"Receipt SMS sent to {recipient} for transaction {transaction_id}")
                message = f"Receipt sent to {recipient}"
            except Exception as e:
                logger.error(f"Failed to send receipt SMS: {str(e)}")
                raise BadRequestException(f"Failed to send SMS: {str(e)}")
            
        elif method == "print":
            # Print functionality is handled on the frontend
            logger.info(f"Receipt printed for transaction {transaction_id}")
            message = "Receipt sent to printer"
            
        else:
            raise BadRequestException("Invalid method")
        
        # Save preference if requested
        if save_preference and transaction.get("client_id"):
            db.clients.update_one(
                {"_id": ObjectId(transaction["client_id"])},
                {
                    "$set": {
                        "receipt_preference": {
                            "method": method,
                            "recipient": recipient
                        }
                    }
                }
            )
        
        return {
            "status": "success",
            "method": method,
            "recipient": recipient,
            "message": message
        }
    
    @staticmethod
    def _format_receipt_html(transaction: Dict) -> str:
        """Format receipt as HTML for email"""
        items_html = ""
        for item in transaction.get("items", []):
            items_html += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #eee;">{item.get('item_name', 'N/A')}</td>
                <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: center;">{item.get('quantity', 0)}</td>
                <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: right;">₦{item.get('price', 0):,.2f}</td>
                <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: right;">₦{(item.get('price', 0) * item.get('quantity', 0)):,.2f}</td>
            </tr>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .receipt-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                .totals {{ margin-top: 20px; text-align: right; }}
                .footer {{ text-align: center; margin-top: 30px; padding-top: 20px; border-top: 2px solid #333; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Receipt</h1>
                <p><strong>Transaction #:</strong> {transaction.get('transaction_number', 'N/A')}</p>
                <p><strong>Date:</strong> {transaction.get('created_at', 'N/A')}</p>
            </div>
            
            <table class="receipt-table">
                <thead>
                    <tr style="background-color: #f5f5f5;">
                        <th style="padding: 10px; text-align: left;">Item</th>
                        <th style="padding: 10px; text-align: center;">Qty</th>
                        <th style="padding: 10px; text-align: right;">Price</th>
                        <th style="padding: 10px; text-align: right;">Total</th>
                    </tr>
                </thead>
                <tbody>
                    {items_html}
                </tbody>
            </table>
            
            <div class="totals">
                <p><strong>Subtotal:</strong> ₦{transaction.get('subtotal', 0):,.2f}</p>
                <p><strong>Discount:</strong> -₦{transaction.get('discount_total', 0):,.2f}</p>
                <p><strong>Tax:</strong> ₦{transaction.get('tax', 0):,.2f}</p>
                <p><strong>Tip:</strong> ₦{transaction.get('tip', 0):,.2f}</p>
                <p style="font-size: 18px; margin-top: 10px;"><strong>Total:</strong> ₦{transaction.get('total', 0):,.2f}</p>
            </div>
            
            <div class="footer">
                <p>Thank you for your business!</p>
                <p><em>Powered by Kenikool Salon</em></p>
            </div>
        </body>
        </html>
        """
        return html
    
    @staticmethod
    def _format_receipt_sms(transaction: Dict) -> str:
        """Format receipt as text for SMS"""
        items_text = ""
        for item in transaction.get("items", []):
            items_text += f"{item.get('item_name', 'N/A')} x{item.get('quantity', 0)}: ₦{(item.get('price', 0) * item.get('quantity', 0)):,.2f}\n"
        
        text = f"""Receipt - {transaction.get('transaction_number', 'N/A')}
Date: {transaction.get('created_at', 'N/A')[:10]}

{items_text}
Subtotal: ₦{transaction.get('subtotal', 0):,.2f}
Discount: -₦{transaction.get('discount_total', 0):,.2f}
Tax: ₦{transaction.get('tax', 0):,.2f}
Tip: ₦{transaction.get('tip', 0):,.2f}
Total: ₦{transaction.get('total', 0):,.2f}

Thank you!
- Kenikool Salon"""
        return text

    
    # Feature 28: Transaction Search
    @staticmethod
    def search_transactions(
        tenant_id: str,
        query: Optional[str] = None,
        transaction_number: Optional[str] = None,
        client_name: Optional[str] = None,
        amount_min: Optional[float] = None,
        amount_max: Optional[float] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        payment_method: Optional[str] = None,
        status: Optional[str] = None,
        offset: int = 0,
        limit: int = 20
    ) -> List[Dict]:
        """
        Advanced transaction search
        
        Args:
            tenant_id: Tenant ID
            query: General search query (searches transaction number, client name, items)
            transaction_number: Specific transaction number
            client_name: Client name to search
            amount_min: Minimum amount
            amount_max: Maximum amount
            date_from: Start date
            date_to: End date
            payment_method: Payment method filter
            status: Transaction status filter
            offset: Pagination offset
            limit: Results limit
            
        Returns:
            List of matching transactions
        """
        db = Database.get_db()
        
        # Build query
        search_query = {"tenant_id": tenant_id}
        
        # Transaction number search
        if transaction_number:
            search_query["transaction_number"] = {"$regex": transaction_number, "$options": "i"}
        
        # General query search (transaction number, items, notes)
        if query:
            search_query["$or"] = [
                {"transaction_number": {"$regex": query, "$options": "i"}},
                {"items.item_name": {"$regex": query, "$options": "i"}},
                {"notes": {"$regex": query, "$options": "i"}}
            ]
        
        # Amount range
        if amount_min is not None or amount_max is not None:
            search_query["total"] = {}
            if amount_min is not None:
                search_query["total"]["$gte"] = amount_min
            if amount_max is not None:
                search_query["total"]["$lte"] = amount_max
        
        # Date range
        if date_from or date_to:
            search_query["created_at"] = {}
            if date_from:
                search_query["created_at"]["$gte"] = datetime.fromisoformat(date_from)
            if date_to:
                search_query["created_at"]["$lte"] = datetime.fromisoformat(date_to)
        
        # Payment method
        if payment_method:
            search_query["payments.method"] = payment_method
        
        # Status
        if status:
            search_query["status"] = status
        
        # Client name search (requires join with clients collection)
        if client_name:
            # Find clients matching the name
            clients = list(db.clients.find({
                "tenant_id": tenant_id,
                "name": {"$regex": client_name, "$options": "i"}
            }))
            client_ids = [str(c["_id"]) for c in clients]
            if client_ids:
                search_query["client_id"] = {"$in": client_ids}
            else:
                # No matching clients, return empty result
                return []
        
        # Execute search
        transactions = list(db.pos_transactions.find(search_query)
                          .sort("created_at", -1)
                          .skip(offset)
                          .limit(limit))
        
        # Enrich with client names
        for t in transactions:
            t["id"] = str(t["_id"])
            if t.get("client_id"):
                client = db.clients.find_one({"_id": ObjectId(t["client_id"])})
                if client:
                    t["client_name"] = client.get("name")
        
        return transactions

    
    # Feature 30: Print Kitchen/Service Tickets
    @staticmethod
    def create_service_ticket(
        tenant_id: str,
        transaction_id: str,
        stylist_id: Optional[str] = None
    ) -> Dict:
        """
        Create a service ticket for stylists
        
        Args:
            tenant_id: Tenant ID
            transaction_id: Transaction ID
            stylist_id: Optional stylist ID filter
            
        Returns:
            Service ticket details
        """
        db = Database.get_db()
        
        # Get transaction
        transaction = db.pos_transactions.find_one({
            "_id": ObjectId(transaction_id),
            "tenant_id": tenant_id
        })
        
        if not transaction:
            raise NotFoundException("Transaction not found")
        
        # Filter items for specific stylist or get all service items
        service_items = []
        for item in transaction.get("items", []):
            if item.get("type") == "service":
                if not stylist_id or transaction.get("stylist_id") == stylist_id:
                    service_items.append(item)
        
        # Get client info
        client = None
        if transaction.get("client_id"):
            client = db.clients.find_one({"_id": ObjectId(transaction["client_id"])})
        
        # Get stylist info
        stylist = None
        if transaction.get("stylist_id"):
            stylist = db.users.find_one({"_id": ObjectId(transaction["stylist_id"])})
        
        # Create ticket
        ticket_data = {
            "tenant_id": tenant_id,
            "transaction_id": transaction_id,
            "transaction_number": transaction["transaction_number"],
            "ticket_number": f"TKT-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}",
            "items": service_items,
            "client_name": client.get("name") if client else "Walk-in",
            "client_phone": client.get("phone") if client else None,
            "stylist_name": stylist.get("name") if stylist else "Unassigned",
            "stylist_id": transaction.get("stylist_id"),
            "notes": transaction.get("notes"),
            "status": "pending",
            "created_at": datetime.now(timezone.utc),
            "completed_at": None
        }
        
        result = db.service_tickets.insert_one(ticket_data)
        ticket_id = str(result.inserted_id)
        
        logger.info(f"Service ticket created: {ticket_id} for transaction: {transaction_id}")
        
        ticket_data["id"] = ticket_id
        ticket_data["_id"] = result.inserted_id
        
        return ticket_data
    
    @staticmethod
    def list_service_tickets(
        tenant_id: str,
        stylist_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        """List service tickets"""
        db = Database.get_db()
        
        query = {"tenant_id": tenant_id}
        if stylist_id:
            query["stylist_id"] = stylist_id
        if status:
            query["status"] = status
        
        tickets = list(db.service_tickets.find(query).sort("created_at", -1))
        
        for ticket in tickets:
            ticket["id"] = str(ticket["_id"])
        
        return tickets
    
    @staticmethod
    def update_ticket_status(
        tenant_id: str,
        ticket_id: str,
        status: str
    ) -> Dict:
        """Update service ticket status"""
        db = Database.get_db()
        
        update_data = {"status": status}
        if status == "completed":
            update_data["completed_at"] = datetime.now(timezone.utc)
        
        result = db.service_tickets.update_one(
            {"_id": ObjectId(ticket_id), "tenant_id": tenant_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise NotFoundException("Service ticket not found")
        
        logger.info(f"Service ticket {ticket_id} status updated to {status}")
        
        return {"status": "success", "ticket_id": ticket_id, "new_status": status}

    @staticmethod
    async def send_digital_gift_card(
        tenant_id: str,
        card_id: str,
        recipient_email: str,
        recipient_name: Optional[str] = None,
        message: Optional[str] = None,
        scheduled_delivery: Optional[datetime] = None
    ) -> Dict:
        """Send digital gift card via email"""
        from app.services.gift_card_email_service import GiftCardEmailService
        
        db = Database.get_db()
        
        # Get gift card
        gift_card = db.gift_cards.find_one({"_id": ObjectId(card_id), "tenant_id": tenant_id})
        if not gift_card:
            raise NotFoundException("Gift card not found")
        
        # If scheduled delivery, store and return
        if scheduled_delivery:
            db.gift_cards.update_one(
                {"_id": ObjectId(card_id)},
                {
                    "$set": {
                        "scheduled_delivery": scheduled_delivery,
                        "delivery_status": "scheduled"
                    },
                    "$push": {
                        "audit_log": {
                            "action": "delivery_scheduled",
                            "timestamp": datetime.now(timezone.utc),
                            "details": {"scheduled_for": scheduled_delivery.isoformat()}
                        }
                    }
                }
            )
            return {"success": True, "status": "scheduled", "scheduled_for": scheduled_delivery}
        
        # Send immediately
        result = await GiftCardEmailService.send_gift_card_delivery_email(
            card_id=card_id,
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            message=message
        )
        
        return result
    
    @staticmethod
    async def resend_gift_card_email(
        tenant_id: str,
        card_id: str,
        new_recipient_email: Optional[str] = None
    ) -> Dict:
        """Resend gift card email to recipient"""
        from app.services.gift_card_email_service import GiftCardEmailService
        
        db = Database.get_db()
        
        # Get gift card
        gift_card = db.gift_cards.find_one({"_id": ObjectId(card_id), "tenant_id": tenant_id})
        if not gift_card:
            raise NotFoundException("Gift card not found")
        
        # Use new email or existing
        recipient_email = new_recipient_email or gift_card.get("recipient_email")
        if not recipient_email:
            raise BadRequestException("No recipient email provided")
        
        # Update recipient email if new one provided
        if new_recipient_email:
            db.gift_cards.update_one(
                {"_id": ObjectId(card_id)},
                {
                    "$set": {"recipient_email": new_recipient_email},
                    "$push": {
                        "audit_log": {
                            "action": "recipient_email_updated",
                            "timestamp": datetime.now(timezone.utc),
                            "details": {"new_email": new_recipient_email}
                        }
                    }
                }
            )
        
        # Send email
        result = await GiftCardEmailService.send_gift_card_delivery_email(
            card_id=card_id,
            recipient_email=recipient_email,
            recipient_name=gift_card.get("recipient_name"),
            message=gift_card.get("message")
        )
        
        return result
    
    @staticmethod
    async def update_delivery_status(
        tenant_id: str,
        card_id: str,
        status: str
    ) -> Dict:
        """Update gift card delivery status"""
        db = Database.get_db()
        
        # Validate status
        valid_statuses = ["pending", "scheduled", "delivered", "failed", "bounced"]
        if status not in valid_statuses:
            raise BadRequestException(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        # Update status
        db.gift_cards.update_one(
            {"_id": ObjectId(card_id), "tenant_id": tenant_id},
            {
                "$set": {
                    "delivery_status": status,
                    "last_delivery_attempt": datetime.now(timezone.utc)
                },
                "$push": {
                    "audit_log": {
                        "action": f"delivery_status_updated",
                        "timestamp": datetime.now(timezone.utc),
                        "details": {"new_status": status}
                    }
                }
            }
        )
        
        return {"success": True, "status": status}

    @staticmethod
    async def bulk_create_gift_cards(
        tenant_id: str,
        cards_data: List[Dict],
        created_by: str
    ) -> Dict:
        """
        Bulk create gift cards from CSV data
        
        Args:
            tenant_id: Tenant ID
            cards_data: List of card data dicts with amount, recipient_name, recipient_email, etc.
            created_by: User creating the cards
            
        Returns:
            Dict with bulk creation results
        """
        db = Database.get_db()
        
        if len(cards_data) > 100:
            raise BadRequestException("Maximum 100 cards per batch")
        
        created_cards = []
        failed_cards = []
        
        for idx, card_data in enumerate(cards_data):
            try:
                # Validate required fields
                if "amount" not in card_data or card_data["amount"] < 1000:
                    failed_cards.append({
                        "row": idx + 1,
                        "error": "Invalid amount (minimum ₦1,000)"
                    })
                    continue
                
                # Create gift card
                gift_card = POSService.create_gift_card(
                    tenant_id=tenant_id,
                    amount=card_data["amount"],
                    card_type=card_data.get("card_type", "digital"),
                    recipient_name=card_data.get("recipient_name"),
                    recipient_email=card_data.get("recipient_email"),
                    message=card_data.get("message"),
                    expiration_months=card_data.get("expiration_months", 12),
                    created_by=created_by,
                    design_theme=card_data.get("design_theme", "default"),
                    activation_required=card_data.get("activation_required", False),
                    pin=card_data.get("pin")
                )
                
                created_cards.append({
                    "card_number": gift_card["card_number"],
                    "amount": gift_card["amount"],
                    "recipient_email": gift_card.get("recipient_email")
                })
                
                # Send email if digital card
                if gift_card["card_type"] == "digital" and gift_card.get("recipient_email"):
                    try:
                        await POSService.send_digital_gift_card(
                            tenant_id=tenant_id,
                            card_id=str(gift_card["_id"]),
                            recipient_email=gift_card["recipient_email"],
                            recipient_name=gift_card.get("recipient_name"),
                            message=gift_card.get("message")
                        )
                    except Exception as e:
                        logger.error(f"Failed to send email for card {gift_card['card_number']}: {str(e)}")
                
            except Exception as e:
                failed_cards.append({
                    "row": idx + 1,
                    "error": str(e)
                })
        
        logger.info(f"Bulk gift card creation completed: {len(created_cards)} created, {len(failed_cards)} failed")
        
        return {
            "total": len(cards_data),
            "created": len(created_cards),
            "failed": len(failed_cards),
            "created_cards": created_cards,
            "failed_cards": failed_cards
        }
    
    @staticmethod
    def get_gift_card_analytics(
        tenant_id: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> Dict:
        """
        Get comprehensive gift card analytics
        
        Args:
            tenant_id: Tenant ID
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            
        Returns:
            Dict with analytics data
        """
        db = Database.get_db()
        
        # Build query
        query = {"tenant_id": tenant_id}
        
        if date_from or date_to:
            date_query = {}
            if date_from:
                date_query["$gte"] = datetime.fromisoformat(f"{date_from}T00:00:00")
            if date_to:
                date_query["$lte"] = datetime.fromisoformat(f"{date_to}T23:59:59")
            query["created_at"] = date_query
        
        # Get all gift cards
        gift_cards = list(db.gift_cards.find(query))
        
        # Calculate metrics
        total_sold = len(gift_cards)
        total_revenue = sum(gc.get("amount", 0) for gc in gift_cards)
        total_redeemed = sum(gc.get("amount", 0) - gc.get("balance", 0) for gc in gift_cards)
        outstanding_liability = sum(gc.get("balance", 0) for gc in gift_cards if gc.get("status") in ["active", "redeemed"])
        
        # Count by status
        status_breakdown = {}
        for gc in gift_cards:
            status = gc.get("status", "unknown")
            if status not in status_breakdown:
                status_breakdown[status] = 0
            status_breakdown[status] += 1
        
        # Count by type
        type_breakdown = {}
        for gc in gift_cards:
            card_type = gc.get("card_type", "unknown")
            if card_type not in type_breakdown:
                type_breakdown[card_type] = {"count": 0, "revenue": 0}
            type_breakdown[card_type]["count"] += 1
            type_breakdown[card_type]["revenue"] += gc.get("amount", 0)
        
        # Calculate expiration rate
        expired_cards = [gc for gc in gift_cards if gc.get("status") == "expired"]
        expired_with_balance = [gc for gc in expired_cards if gc.get("balance", 0) > 0]
        expiration_rate = (len(expired_with_balance) / total_sold * 100) if total_sold > 0 else 0
        
        # Calculate redemption rate
        redemption_rate = (total_redeemed / total_revenue * 100) if total_revenue > 0 else 0
        
        # Average card value
        average_card_value = total_revenue / total_sold if total_sold > 0 else 0
        
        # Most popular amounts
        amount_counts = {}
        for gc in gift_cards:
            amount = gc.get("amount", 0)
            if amount not in amount_counts:
                amount_counts[amount] = 0
            amount_counts[amount] += 1
        
        popular_amounts = sorted(
            amount_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Top purchasers (by email)
        purchaser_counts = {}
        for gc in gift_cards:
            purchaser = gc.get("purchaser_email") or gc.get("created_by", "Unknown")
            if purchaser not in purchaser_counts:
                purchaser_counts[purchaser] = 0
            purchaser_counts[purchaser] += 1
        
        top_purchasers = sorted(
            purchaser_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Top recipients
        recipient_counts = {}
        for gc in gift_cards:
            recipient = gc.get("recipient_email") or gc.get("recipient_name", "Unknown")
            if recipient and recipient != "Unknown":
                if recipient not in recipient_counts:
                    recipient_counts[recipient] = 0
                recipient_counts[recipient] += 1
        
        top_recipients = sorted(
            recipient_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            "summary": {
                "total_sold": total_sold,
                "total_revenue": total_revenue,
                "total_redeemed": total_redeemed,
                "outstanding_liability": outstanding_liability,
                "average_card_value": average_card_value,
                "redemption_rate": round(redemption_rate, 2),
                "expiration_rate": round(expiration_rate, 2)
            },
            "status_breakdown": status_breakdown,
            "type_breakdown": type_breakdown,
            "popular_amounts": [{"amount": amount, "count": count} for amount, count in popular_amounts],
            "top_purchasers": [{"purchaser": purchaser, "count": count} for purchaser, count in top_purchasers],
            "top_recipients": [{"recipient": recipient, "count": count} for recipient, count in top_recipients]
        }

    # ========================================================================
    # Membership Discount Integration
    # ========================================================================

    @staticmethod
    def apply_membership_discount(
        tenant_id: str,
        client_id: str,
        items: List[Dict],
        membership_service
    ) -> Dict:
        """
        Apply membership discount to POS transaction items.

        Args:
            tenant_id: Tenant ID
            client_id: Client ID
            items: List of transaction items
            membership_service: MembershipService instance

        Returns:
            Dict with discount details
        """
        import asyncio
        
        # Run async method in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                membership_service.apply_membership_discount(
                    tenant_id=tenant_id,
                    client_id=client_id,
                    items=items,
                    promo_code=None
                )
            )
            return result
        finally:
            loop.close()

    @staticmethod
    def get_client_discount(
        tenant_id: str,
        client_id: str,
        membership_service
    ) -> Dict:
        """
        Get active membership discount for a client.

        Args:
            tenant_id: Tenant ID
            client_id: Client ID
            membership_service: MembershipService instance

        Returns:
            Dict with discount information
        """
        import asyncio
        
        # Run async method in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                membership_service.get_client_discount(
                    tenant_id=tenant_id,
                    client_id=client_id
                )
            )
            return result
        finally:
            loop.close()
