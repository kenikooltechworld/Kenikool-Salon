"""
Accounts Receivable/Payable service
"""
from bson import ObjectId
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

from app.database import Database
from app.api.exceptions import NotFoundException, BadRequestException

logger = logging.getLogger(__name__)


class ARAPService:
    """Service for Accounts Receivable and Accounts Payable"""
    
    @staticmethod
    def create_invoice(
        tenant_id: str,
        client_id: str,
        invoice_date: str,
        due_date: str,
        line_items: List[Dict],
        tax_rate_id: Optional[str] = None,
        tax_exempt: bool = False,
        notes: Optional[str] = None
    ) -> Dict:
        """
        Create an invoice (Accounts Receivable)
        
        Returns:
            Dict with created invoice data
        """
        db = Database.get_db()
        
        # Get client info
        client = db.clients.find_one({"_id": ObjectId(client_id), "tenant_id": tenant_id})
        if not client:
            raise NotFoundException("Client not found")
        
        # Calculate totals
        subtotal = sum(item.get("amount", 0) for item in line_items)
        
        # Calculate tax
        tax_amount = 0.0
        tax_rate = 0.0
        tax_rate_name = None
        
        if not tax_exempt and tax_rate_id:
            # Get tax rate
            tax_rate_doc = db.tax_rates.find_one({
                "_id": ObjectId(tax_rate_id),
                "tenant_id": tenant_id,
                "active": True
            })
            if tax_rate_doc:
                tax_rate = tax_rate_doc["rate"]
                tax_rate_name = tax_rate_doc["name"]
                tax_amount = subtotal * (tax_rate / 100)
        
        total = subtotal + tax_amount
        
        # Generate invoice number
        last_invoice = db.invoices.find_one(
            {"tenant_id": tenant_id},
            sort=[("created_at", -1)]
        )
        
        if last_invoice and "invoice_number" in last_invoice:
            last_num = int(last_invoice["invoice_number"].split("-")[-1])
            invoice_number = f"INV-{last_num + 1:05d}"
        else:
            invoice_number = "INV-00001"
        
        invoice_data = {
            "tenant_id": tenant_id,
            "invoice_number": invoice_number,
            "client_id": client_id,
            "client_name": f"{client.get('first_name', '')} {client.get('last_name', '')}".strip() or client.get("name", ""),
            "invoice_date": invoice_date,
            "due_date": due_date,
            "line_items": line_items,
            "subtotal": round(subtotal, 2),
            "tax_rate_id": tax_rate_id,
            "tax_rate_name": tax_rate_name,
            "tax_rate": tax_rate,
            "tax_amount": round(tax_amount, 2),
            "tax_exempt": tax_exempt,
            "total": round(total, 2),
            "amount_paid": 0.0,
            "amount_due": round(total, 2),
            "status": "draft",
            "notes": notes,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.invoices.insert_one(invoice_data)
        invoice_id = str(result.inserted_id)
        
        logger.info(f"Invoice created: {invoice_id} ({invoice_number}) for tenant: {tenant_id}")
        
        invoice_doc = db.invoices.find_one({"_id": ObjectId(invoice_id)})
        return ARAPService._format_invoice_response(invoice_doc)
    
    @staticmethod
    def get_invoices(
        tenant_id: str,
        status: Optional[str] = None,
        client_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Get invoices for tenant
        
        Returns:
            List of invoice dicts
        """
        db = Database.get_db()
        
        query = {"tenant_id": tenant_id}
        if status:
            query["status"] = status
        if client_id:
            query["client_id"] = client_id
        
        invoices = list(db.invoices.find(query).sort("invoice_date", -1))
        
        # Update overdue status
        today = datetime.utcnow().strftime("%Y-%m-%d")
        for invoice in invoices:
            if (invoice.get("status") == "sent" and 
                invoice.get("due_date") < today and 
                invoice.get("amount_due", 0) > 0):
                db.invoices.update_one(
                    {"_id": invoice["_id"]},
                    {"$set": {"status": "overdue"}}
                )
                invoice["status"] = "overdue"
        
        return [ARAPService._format_invoice_response(i) for i in invoices]
    
    @staticmethod
    def record_payment(
        tenant_id: str,
        invoice_id: str,
        amount: float,
        payment_date: str,
        payment_method: str,
        reference: Optional[str] = None
    ) -> Dict:
        """
        Record a payment against an invoice
        
        Returns:
            Dict with payment data
        """
        db = Database.get_db()
        
        # Get invoice
        invoice = db.invoices.find_one({
            "_id": ObjectId(invoice_id),
            "tenant_id": tenant_id
        })
        
        if not invoice:
            raise NotFoundException("Invoice not found")
        
        # Validate payment amount
        amount_due = invoice.get("amount_due", 0)
        if amount > amount_due:
            raise BadRequestException(f"Payment amount (₦{amount}) exceeds amount due (₦{amount_due})")
        
        # Create payment record
        payment_data = {
            "tenant_id": tenant_id,
            "invoice_id": invoice_id,
            "amount": round(amount, 2),
            "payment_date": payment_date,
            "payment_method": payment_method,
            "reference": reference,
            "created_at": datetime.utcnow()
        }
        
        result = db.payments.insert_one(payment_data)
        payment_id = str(result.inserted_id)
        
        # Update invoice
        new_amount_paid = invoice.get("amount_paid", 0) + amount
        new_amount_due = invoice.get("total", 0) - new_amount_paid
        
        new_status = "paid" if new_amount_due <= 0.01 else invoice.get("status")
        
        db.invoices.update_one(
            {"_id": ObjectId(invoice_id)},
            {
                "$set": {
                    "amount_paid": round(new_amount_paid, 2),
                    "amount_due": round(new_amount_due, 2),
                    "status": new_status,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"Payment recorded: {payment_id} for invoice: {invoice_id}")
        
        payment_doc = db.payments.find_one({"_id": ObjectId(payment_id)})
        return ARAPService._format_payment_response(payment_doc)
    
    @staticmethod
    def get_aging_report(tenant_id: str) -> Dict:
        """
        Generate accounts receivable aging report
        
        Returns:
            Dict with aging data
        """
        db = Database.get_db()
        
        invoices = list(db.invoices.find({
            "tenant_id": tenant_id,
            "status": {"$in": ["sent", "overdue"]},
            "amount_due": {"$gt": 0}
        }))
        
        today = datetime.utcnow()
        
        aging_buckets = {
            "current": 0.0,  # 0-30 days
            "30_days": 0.0,  # 31-60 days
            "60_days": 0.0,  # 61-90 days
            "90_plus": 0.0   # 90+ days
        }
        
        aged_invoices = []
        
        for invoice in invoices:
            due_date = datetime.strptime(invoice.get("due_date"), "%Y-%m-%d")
            days_overdue = (today - due_date).days
            amount_due = invoice.get("amount_due", 0)
            
            if days_overdue <= 0:
                aging_buckets["current"] += amount_due
                bucket = "current"
            elif days_overdue <= 30:
                aging_buckets["30_days"] += amount_due
                bucket = "30_days"
            elif days_overdue <= 60:
                aging_buckets["60_days"] += amount_due
                bucket = "60_days"
            else:
                aging_buckets["90_plus"] += amount_due
                bucket = "90_plus"
            
            aged_invoices.append({
                "invoice_number": invoice.get("invoice_number"),
                "client_name": invoice.get("client_name"),
                "invoice_date": invoice.get("invoice_date"),
                "due_date": invoice.get("due_date"),
                "amount_due": round(amount_due, 2),
                "days_overdue": max(0, days_overdue),
                "aging_bucket": bucket
            })
        
        total_outstanding = sum(aging_buckets.values())
        
        return {
            "report_type": "aging_report",
            "as_of_date": today.strftime("%Y-%m-%d"),
            "aging_buckets": {
                "current": round(aging_buckets["current"], 2),
                "30_days": round(aging_buckets["30_days"], 2),
                "60_days": round(aging_buckets["60_days"], 2),
                "90_plus": round(aging_buckets["90_plus"], 2)
            },
            "total_outstanding": round(total_outstanding, 2),
            "invoices": aged_invoices
        }
    
    @staticmethod
    def get_invoice(tenant_id: str, invoice_id: str) -> Dict:
        """
        Get a single invoice by ID
        
        Returns:
            Dict with invoice data
        """
        db = Database.get_db()
        
        invoice = db.invoices.find_one({
            "_id": ObjectId(invoice_id),
            "tenant_id": tenant_id
        })
        
        if not invoice:
            raise NotFoundException("Invoice not found")
        
        return ARAPService._format_invoice_response(invoice)
    
    @staticmethod
    def update_invoice(
        tenant_id: str,
        invoice_id: str,
        client_id: Optional[str] = None,
        invoice_date: Optional[str] = None,
        due_date: Optional[str] = None,
        line_items: Optional[List[Dict]] = None,
        tax_rate_id: Optional[str] = None,
        tax_exempt: Optional[bool] = None,
        notes: Optional[str] = None
    ) -> Dict:
        """
        Update an invoice (only if status is draft)
        
        Returns:
            Dict with updated invoice data
        """
        db = Database.get_db()
        
        # Get existing invoice
        invoice = db.invoices.find_one({
            "_id": ObjectId(invoice_id),
            "tenant_id": tenant_id
        })
        
        if not invoice:
            raise NotFoundException("Invoice not found")
        
        # Only allow editing draft invoices
        if invoice.get("status") != "draft":
            raise BadRequestException("Can only edit draft invoices")
        
        update_data = {"updated_at": datetime.utcnow()}
        
        # Update client if provided
        if client_id:
            client = db.clients.find_one({"_id": ObjectId(client_id), "tenant_id": tenant_id})
            if not client:
                raise NotFoundException("Client not found")
            update_data["client_id"] = client_id
            update_data["client_name"] = f"{client.get('first_name', '')} {client.get('last_name', '')}".strip()
        
        # Update dates
        if invoice_date:
            update_data["invoice_date"] = invoice_date
        if due_date:
            update_data["due_date"] = due_date
        
        # Update line items and recalculate totals
        if line_items is not None:
            update_data["line_items"] = line_items
            subtotal = sum(item.get("amount", 0) for item in line_items)
            update_data["subtotal"] = subtotal
            
            # Calculate tax
            tax_amount = 0.0
            tax_rate = 0.0
            tax_rate_name = None
            
            if not tax_exempt and tax_rate_id:
                # Get tax rate
                tax_rate_doc = db.tax_rates.find_one({
                    "_id": ObjectId(tax_rate_id),
                    "tenant_id": tenant_id,
                    "active": True
                })
                if tax_rate_doc:
                    tax_rate = tax_rate_doc["rate"]
                    tax_rate_name = tax_rate_doc["name"]
                    tax_amount = subtotal * (tax_rate / 100)
            
            update_data["tax_rate_id"] = tax_rate_id
            update_data["tax_rate_name"] = tax_rate_name
            update_data["tax_rate"] = tax_rate
            update_data["tax_amount"] = tax_amount
            update_data["tax_exempt"] = tax_exempt or False
            update_data["total"] = subtotal + tax_amount
            update_data["amount_due"] = subtotal + tax_amount - invoice.get("amount_paid", 0)
        
        # Update tax settings if provided
        if tax_rate_id is not None or tax_exempt is not None:
            if tax_exempt:
                update_data["tax_rate_id"] = None
                update_data["tax_rate_name"] = None
                update_data["tax_rate"] = 0.0
                update_data["tax_amount"] = 0.0
                update_data["tax_exempt"] = True
            elif tax_rate_id:
                tax_rate_doc = db.tax_rates.find_one({
                    "_id": ObjectId(tax_rate_id),
                    "tenant_id": tenant_id,
                    "active": True
                })
                if tax_rate_doc:
                    subtotal = invoice.get("subtotal", 0)
                    tax_rate = tax_rate_doc["rate"]
                    tax_amount = subtotal * (tax_rate / 100)
                    
                    update_data["tax_rate_id"] = tax_rate_id
                    update_data["tax_rate_name"] = tax_rate_doc["name"]
                    update_data["tax_rate"] = tax_rate
                    update_data["tax_amount"] = tax_amount
                    update_data["tax_exempt"] = False
                    update_data["total"] = subtotal + tax_amount
                    update_data["amount_due"] = subtotal + tax_amount - invoice.get("amount_paid", 0)
        
        # Update notes
        if notes is not None:
            update_data["notes"] = notes
        
        # Update the invoice
        db.invoices.update_one(
            {"_id": ObjectId(invoice_id)},
            {"$set": update_data}
        )
        
        # Return updated invoice
        updated_invoice = db.invoices.find_one({"_id": ObjectId(invoice_id)})
        return ARAPService._format_invoice_response(updated_invoice)
    
    @staticmethod
    def delete_invoice(tenant_id: str, invoice_id: str) -> Dict:
        """
        Delete/cancel an invoice
        
        Returns:
            Dict with cancellation result
        """
        db = Database.get_db()
        
        # Get existing invoice
        invoice = db.invoices.find_one({
            "_id": ObjectId(invoice_id),
            "tenant_id": tenant_id
        })
        
        if not invoice:
            raise NotFoundException("Invoice not found")
        
        # Check if invoice has payments
        if invoice.get("amount_paid", 0) > 0:
            raise BadRequestException("Cannot delete invoice with payments. Cancel instead.")
        
        # If draft, delete completely
        if invoice.get("status") == "draft":
            db.invoices.delete_one({"_id": ObjectId(invoice_id)})
            return {"message": "Invoice deleted successfully", "deleted": True}
        
        # Otherwise, cancel the invoice
        update_data = {
            "status": "cancelled",
            "updated_at": datetime.utcnow(),
            "cancelled_at": datetime.utcnow()
        }
        
        db.invoices.update_one(
            {"_id": ObjectId(invoice_id)},
            {"$set": update_data}
        )
        
        # TODO: Reverse any journal entries created for this invoice
        # This would be implemented when we add automatic journal entry creation
        
        return {"message": "Invoice cancelled successfully", "cancelled": True}
    
    @staticmethod
    def create_bill(
        tenant_id: str,
        vendor_id: str,
        bill_date: str,
        due_date: str,
        line_items: List[Dict],
        reference_number: Optional[str] = None,
        tax_rate_id: Optional[str] = None,
        tax_exempt: bool = False,
        notes: Optional[str] = None
    ) -> Dict:
        """
        Create a bill (Accounts Payable)
        
        Returns:
            Dict with created bill data
        """
        db = Database.get_db()
        
        # Get vendor info
        vendor = db.vendors.find_one({"_id": ObjectId(vendor_id), "tenant_id": tenant_id})
        if not vendor:
            raise NotFoundException("Vendor not found")
        
        # Calculate totals
        subtotal = sum(item.get("amount", 0) for item in line_items)
        
        # Calculate tax
        tax_amount = 0.0
        tax_rate = 0.0
        tax_rate_name = None
        
        if not tax_exempt and tax_rate_id:
            # Get tax rate
            tax_rate_doc = db.tax_rates.find_one({
                "_id": ObjectId(tax_rate_id),
                "tenant_id": tenant_id,
                "active": True
            })
            if tax_rate_doc:
                tax_rate = tax_rate_doc["rate"]
                tax_rate_name = tax_rate_doc["name"]
                tax_amount = subtotal * (tax_rate / 100)
        
        total = subtotal + tax_amount
        
        # Generate bill number
        last_bill = db.bills.find_one(
            {"tenant_id": tenant_id},
            sort=[("created_at", -1)]
        )
        
        if last_bill and "bill_number" in last_bill:
            last_num = int(last_bill["bill_number"].split("-")[-1])
            bill_number = f"BILL-{last_num + 1:05d}"
        else:
            bill_number = "BILL-00001"
        
        bill_data = {
            "tenant_id": tenant_id,
            "bill_number": bill_number,
            "vendor_id": vendor_id,
            "vendor_name": vendor["name"],
            "bill_date": bill_date,
            "due_date": due_date,
            "reference_number": reference_number,
            "line_items": line_items,
            "subtotal": round(subtotal, 2),
            "tax_rate_id": tax_rate_id,
            "tax_rate_name": tax_rate_name,
            "tax_rate": tax_rate,
            "tax_amount": round(tax_amount, 2),
            "tax_exempt": tax_exempt,
            "total": round(total, 2),
            "amount_paid": 0.0,
            "amount_due": round(total, 2),
            "status": "draft",
            "notes": notes,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.bills.insert_one(bill_data)
        bill_id = str(result.inserted_id)
        
        logger.info(f"Bill created: {bill_id} ({bill_number}) for tenant: {tenant_id}")
        
        bill_doc = db.bills.find_one({"_id": ObjectId(bill_id)})
        return ARAPService._format_bill_response(bill_doc)
    
    @staticmethod
    def get_bills(
        tenant_id: str,
        status: Optional[str] = None,
        vendor_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Get bills for tenant
        
        Returns:
            List of bill dicts
        """
        db = Database.get_db()
        
        query = {"tenant_id": tenant_id}
        if status:
            query["status"] = status
        if vendor_id:
            query["vendor_id"] = vendor_id
        
        bills = list(db.bills.find(query).sort("bill_date", -1))
        
        # Update overdue status
        today = datetime.utcnow().strftime("%Y-%m-%d")
        for bill in bills:
            if (bill.get("status") in ["pending", "approved"] and 
                bill.get("due_date") < today and 
                bill.get("amount_due", 0) > 0):
                db.bills.update_one(
                    {"_id": bill["_id"]},
                    {"$set": {"status": "overdue"}}
                )
                bill["status"] = "overdue"
        
        return [ARAPService._format_bill_response(b) for b in bills]
    
    @staticmethod
    def get_bill(tenant_id: str, bill_id: str) -> Dict:
        """
        Get a single bill by ID
        
        Returns:
            Dict with bill data
        """
        db = Database.get_db()
        
        bill = db.bills.find_one({
            "_id": ObjectId(bill_id),
            "tenant_id": tenant_id
        })
        
        if not bill:
            raise NotFoundException("Bill not found")
        
        return ARAPService._format_bill_response(bill)
    
    @staticmethod
    def update_bill(
        tenant_id: str,
        bill_id: str,
        vendor_id: Optional[str] = None,
        bill_date: Optional[str] = None,
        due_date: Optional[str] = None,
        reference_number: Optional[str] = None,
        line_items: Optional[List[Dict]] = None,
        tax_rate_id: Optional[str] = None,
        tax_exempt: Optional[bool] = None,
        notes: Optional[str] = None
    ) -> Dict:
        """
        Update a bill (only if status is draft)
        
        Returns:
            Dict with updated bill data
        """
        db = Database.get_db()
        
        # Get existing bill
        bill = db.bills.find_one({
            "_id": ObjectId(bill_id),
            "tenant_id": tenant_id
        })
        
        if not bill:
            raise NotFoundException("Bill not found")
        
        # Only allow editing draft bills
        if bill.get("status") != "draft":
            raise BadRequestException("Can only edit draft bills")
        
        update_data = {"updated_at": datetime.utcnow()}
        
        # Update vendor if provided
        if vendor_id:
            vendor = db.vendors.find_one({"_id": ObjectId(vendor_id), "tenant_id": tenant_id})
            if not vendor:
                raise NotFoundException("Vendor not found")
            update_data["vendor_id"] = vendor_id
            update_data["vendor_name"] = vendor["name"]
        
        # Update dates
        if bill_date:
            update_data["bill_date"] = bill_date
        if due_date:
            update_data["due_date"] = due_date
        if reference_number is not None:
            update_data["reference_number"] = reference_number
        
        # Update line items and recalculate totals
        if line_items is not None:
            update_data["line_items"] = line_items
            subtotal = sum(item.get("amount", 0) for item in line_items)
            update_data["subtotal"] = subtotal
            
            # Calculate tax
            tax_amount = 0.0
            tax_rate = 0.0
            tax_rate_name = None
            
            if not tax_exempt and tax_rate_id:
                # Get tax rate
                tax_rate_doc = db.tax_rates.find_one({
                    "_id": ObjectId(tax_rate_id),
                    "tenant_id": tenant_id,
                    "active": True
                })
                if tax_rate_doc:
                    tax_rate = tax_rate_doc["rate"]
                    tax_rate_name = tax_rate_doc["name"]
                    tax_amount = subtotal * (tax_rate / 100)
            
            update_data["tax_rate_id"] = tax_rate_id
            update_data["tax_rate_name"] = tax_rate_name
            update_data["tax_rate"] = tax_rate
            update_data["tax_amount"] = tax_amount
            update_data["tax_exempt"] = tax_exempt or False
            update_data["total"] = subtotal + tax_amount
            update_data["amount_due"] = subtotal + tax_amount - bill.get("amount_paid", 0)
        
        # Update tax settings if provided
        if tax_rate_id is not None or tax_exempt is not None:
            if tax_exempt:
                update_data["tax_rate_id"] = None
                update_data["tax_rate_name"] = None
                update_data["tax_rate"] = 0.0
                update_data["tax_amount"] = 0.0
                update_data["tax_exempt"] = True
            elif tax_rate_id:
                tax_rate_doc = db.tax_rates.find_one({
                    "_id": ObjectId(tax_rate_id),
                    "tenant_id": tenant_id,
                    "active": True
                })
                if tax_rate_doc:
                    subtotal = bill.get("subtotal", 0)
                    tax_rate = tax_rate_doc["rate"]
                    tax_amount = subtotal * (tax_rate / 100)
                    
                    update_data["tax_rate_id"] = tax_rate_id
                    update_data["tax_rate_name"] = tax_rate_doc["name"]
                    update_data["tax_rate"] = tax_rate
                    update_data["tax_amount"] = tax_amount
                    update_data["tax_exempt"] = False
                    update_data["total"] = subtotal + tax_amount
                    update_data["amount_due"] = subtotal + tax_amount - bill.get("amount_paid", 0)
        
        # Update notes
        if notes is not None:
            update_data["notes"] = notes
        
        # Update the bill
        db.bills.update_one(
            {"_id": ObjectId(bill_id)},
            {"$set": update_data}
        )
        
        # Return updated bill
        updated_bill = db.bills.find_one({"_id": ObjectId(bill_id)})
        return ARAPService._format_bill_response(updated_bill)
    
    @staticmethod
    def delete_bill(tenant_id: str, bill_id: str) -> Dict:
        """
        Delete/cancel a bill
        
        Returns:
            Dict with cancellation result
        """
        db = Database.get_db()
        
        # Get existing bill
        bill = db.bills.find_one({
            "_id": ObjectId(bill_id),
            "tenant_id": tenant_id
        })
        
        if not bill:
            raise NotFoundException("Bill not found")
        
        # Check if bill has payments
        if bill.get("amount_paid", 0) > 0:
            raise BadRequestException("Cannot delete bill with payments. Cancel instead.")
        
        # If draft, delete completely
        if bill.get("status") == "draft":
            db.bills.delete_one({"_id": ObjectId(bill_id)})
            return {"message": "Bill deleted successfully", "deleted": True}
        
        # Otherwise, cancel the bill
        update_data = {
            "status": "cancelled",
            "updated_at": datetime.utcnow(),
            "cancelled_at": datetime.utcnow()
        }
        
        db.bills.update_one(
            {"_id": ObjectId(bill_id)},
            {"$set": update_data}
        )
        
        return {"message": "Bill cancelled successfully", "cancelled": True}
    
    @staticmethod
    def record_bill_payment(
        tenant_id: str,
        bill_id: str,
        amount: float,
        payment_date: str,
        payment_method: str,
        reference: Optional[str] = None
    ) -> Dict:
        """
        Record a payment against a bill
        
        Returns:
            Dict with payment data
        """
        db = Database.get_db()
        
        # Get bill
        bill = db.bills.find_one({
            "_id": ObjectId(bill_id),
            "tenant_id": tenant_id
        })
        
        if not bill:
            raise NotFoundException("Bill not found")
        
        # Validate payment amount
        amount_due = bill.get("amount_due", 0)
        if amount > amount_due:
            raise BadRequestException(f"Payment amount (₦{amount}) exceeds amount due (₦{amount_due})")
        
        # Create payment record
        payment_data = {
            "tenant_id": tenant_id,
            "bill_id": bill_id,
            "amount": amount,
            "payment_date": payment_date,
            "payment_method": payment_method,
            "reference": reference,
            "created_at": datetime.utcnow()
        }
        
        result = db.bill_payments.insert_one(payment_data)
        payment_id = str(result.inserted_id)
        
        # Update bill amounts
        new_amount_paid = bill.get("amount_paid", 0) + amount
        new_amount_due = bill.get("total", 0) - new_amount_paid
        
        # Update bill status
        new_status = bill.get("status")
        if new_amount_due <= 0:
            new_status = "paid"
        elif new_amount_paid > 0 and bill.get("status") == "draft":
            new_status = "pending"
        
        db.bills.update_one(
            {"_id": ObjectId(bill_id)},
            {
                "$set": {
                    "amount_paid": new_amount_paid,
                    "amount_due": new_amount_due,
                    "status": new_status,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"Bill payment recorded: {payment_id} for bill: {bill_id}")
        
        payment_doc = db.bill_payments.find_one({"_id": ObjectId(payment_id)})
        return ARAPService._format_bill_payment_response(payment_doc)
    
    @staticmethod
    def get_ap_aging_report(tenant_id: str) -> Dict:
        """
        Generate accounts payable aging report
        
        Returns:
            Dict with aging report data
        """
        db = Database.get_db()
        
        # Get all outstanding bills
        bills = list(db.bills.find({
            "tenant_id": tenant_id,
            "status": {"$nin": ["paid", "cancelled"]},
            "amount_due": {"$gt": 0}
        }))
        
        today = datetime.utcnow()
        aging_buckets = {
            "current": 0.0,
            "30_days": 0.0,
            "60_days": 0.0,
            "90_plus": 0.0
        }
        
        aged_bills = []
        total_outstanding = 0.0
        
        for bill in bills:
            due_date = datetime.strptime(bill["due_date"], "%Y-%m-%d")
            days_overdue = (today - due_date).days
            amount_due = bill.get("amount_due", 0)
            
            # Categorize by age
            if days_overdue <= 0:
                aging_buckets["current"] += amount_due
                age_category = "Current"
            elif days_overdue <= 30:
                aging_buckets["30_days"] += amount_due
                age_category = "1-30 days"
            elif days_overdue <= 60:
                aging_buckets["60_days"] += amount_due
                age_category = "31-60 days"
            else:
                aging_buckets["90_plus"] += amount_due
                age_category = "60+ days"
            
            total_outstanding += amount_due
            
            aged_bills.append({
                "bill_id": str(bill["_id"]),
                "bill_number": bill["bill_number"],
                "vendor_name": bill["vendor_name"],
                "bill_date": bill["bill_date"],
                "due_date": bill["due_date"],
                "amount_due": amount_due,
                "days_overdue": max(0, days_overdue),
                "age_category": age_category
            })
        
        return {
            "aging_summary": {
                "current": round(aging_buckets["current"], 2),
                "30_days": round(aging_buckets["30_days"], 2),
                "60_days": round(aging_buckets["60_days"], 2),
                "90_plus": round(aging_buckets["90_plus"], 2)
            },
            "total_outstanding": round(total_outstanding, 2),
            "bills": aged_bills
        }
    
    @staticmethod
    def _format_bill_response(bill_doc: Dict) -> Dict:
        """Format bill document for response"""
        return {
            "id": str(bill_doc["_id"]),
            "tenant_id": bill_doc["tenant_id"],
            "bill_number": bill_doc["bill_number"],
            "vendor_id": bill_doc["vendor_id"],
            "vendor_name": bill_doc["vendor_name"],
            "bill_date": bill_doc["bill_date"],
            "due_date": bill_doc["due_date"],
            "reference_number": bill_doc.get("reference_number"),
            "line_items": bill_doc["line_items"],
            "subtotal": bill_doc["subtotal"],
            "tax_rate_id": bill_doc.get("tax_rate_id"),
            "tax_rate_name": bill_doc.get("tax_rate_name"),
            "tax_rate": bill_doc.get("tax_rate", 0.0),
            "tax_amount": bill_doc.get("tax_amount", 0.0),
            "tax_exempt": bill_doc.get("tax_exempt", False),
            "total": bill_doc["total"],
            "amount_paid": bill_doc.get("amount_paid", 0.0),
            "amount_due": bill_doc.get("amount_due", bill_doc["total"]),
            "status": bill_doc.get("status", "draft"),
            "notes": bill_doc.get("notes"),
            "created_at": bill_doc["created_at"],
            "updated_at": bill_doc["updated_at"]
        }
    
    @staticmethod
    def _format_bill_payment_response(payment_doc: Dict) -> Dict:
        """Format bill payment document for response"""
        return {
            "id": str(payment_doc["_id"]),
            "tenant_id": payment_doc["tenant_id"],
            "bill_id": payment_doc["bill_id"],
            "amount": payment_doc["amount"],
            "payment_date": payment_doc["payment_date"],
            "payment_method": payment_doc["payment_method"],
            "reference": payment_doc.get("reference"),
            "created_at": payment_doc["created_at"]
        }
    
    @staticmethod
    def _format_invoice_response(invoice_doc: Dict) -> Dict:
        """Format invoice document for response"""
        return {
            "id": str(invoice_doc["_id"]),
            "tenant_id": invoice_doc["tenant_id"],
            "invoice_number": invoice_doc["invoice_number"],
            "client_id": invoice_doc["client_id"],
            "client_name": invoice_doc["client_name"],
            "invoice_date": invoice_doc["invoice_date"],
            "due_date": invoice_doc["due_date"],
            "line_items": invoice_doc["line_items"],
            "subtotal": invoice_doc["subtotal"],
            "tax_rate_id": invoice_doc.get("tax_rate_id"),
            "tax_rate_name": invoice_doc.get("tax_rate_name"),
            "tax_rate": invoice_doc.get("tax_rate", 0.0),
            "tax_amount": invoice_doc.get("tax_amount", invoice_doc.get("tax", 0.0)),  # Backward compatibility
            "tax_exempt": invoice_doc.get("tax_exempt", False),
            "total": invoice_doc["total"],
            "amount_paid": invoice_doc.get("amount_paid", 0.0),
            "amount_due": invoice_doc.get("amount_due", invoice_doc["total"]),
            "status": invoice_doc.get("status", "draft"),
            "notes": invoice_doc.get("notes"),
            "created_at": invoice_doc["created_at"],
            "updated_at": invoice_doc["updated_at"]
        }
    
    @staticmethod
    def _format_payment_response(payment_doc: Dict) -> Dict:
        """Format payment document for response"""
        return {
            "id": str(payment_doc["_id"]),
            "tenant_id": payment_doc["tenant_id"],
            "invoice_id": payment_doc["invoice_id"],
            "amount": payment_doc["amount"],
            "payment_date": payment_doc["payment_date"],
            "payment_method": payment_doc["payment_method"],
            "reference": payment_doc.get("reference"),
            "created_at": payment_doc["created_at"]
        }


# Singleton instance
ar_ap_service = ARAPService()
