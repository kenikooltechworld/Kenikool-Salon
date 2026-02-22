"""
Accounting service - Double-entry bookkeeping
"""
from bson import ObjectId
from datetime import datetime
from typing import Dict, List, Optional
import logging

from app.database import Database
from app.api.exceptions import NotFoundException, BadRequestException

logger = logging.getLogger(__name__)


class AccountingService:
    """Service for accounting and financial management"""
    
    @staticmethod
    def create_account(
        tenant_id: str,
        code: str,
        name: str,
        account_type: str,
        sub_type: str,
        description: Optional[str] = None,
        parent_account_id: Optional[str] = None
    ) -> Dict:
        """
        Create a new account in chart of accounts
        
        Returns:
            Dict with created account data
        """
        db = Database.get_db()
        
        # Check if code already exists
        existing = db.accounts.find_one({
            "tenant_id": tenant_id,
            "code": code
        })
        
        if existing:
            raise BadRequestException(f"Account code {code} already exists")
        
        account_data = {
            "tenant_id": tenant_id,
            "code": code,
            "name": name,
            "account_type": account_type,
            "sub_type": sub_type,
            "description": description,
            "parent_account_id": parent_account_id,
            "balance": 0.0,
            "active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.accounts.insert_one(account_data)
        account_id = str(result.inserted_id)
        
        logger.info(f"Account created: {account_id} ({code}) for tenant: {tenant_id}")
        
        account_doc = db.accounts.find_one({"_id": ObjectId(account_id)})
        return AccountingService._format_account_response(account_doc)
    
    @staticmethod
    def get_chart_of_accounts(tenant_id: str) -> List[Dict]:
        """
        Get chart of accounts for tenant
        
        Returns:
            List of account dicts
        """
        db = Database.get_db()
        
        accounts = list(db.accounts.find({
            "tenant_id": tenant_id,
            "active": True
        }).sort("code", 1))
        
        return [AccountingService._format_account_response(a) for a in accounts]
    
    @staticmethod
    def update_account(
        account_id: str,
        tenant_id: str,
        **updates
    ) -> Dict:
        """
        Update an account
        
        Returns:
            Dict with updated account data
        """
        db = Database.get_db()
        
        account_doc = db.accounts.find_one({
            "_id": ObjectId(account_id),
            "tenant_id": tenant_id
        })
        
        if not account_doc:
            raise NotFoundException("Account not found")
        
        update_data = {"updated_at": datetime.utcnow()}
        for key, value in updates.items():
            if value is not None:
                update_data[key] = value
        
        db.accounts.update_one(
            {"_id": ObjectId(account_id)},
            {"$set": update_data}
        )
        
        logger.info(f"Account updated: {account_id}")
        
        account_doc = db.accounts.find_one({"_id": ObjectId(account_id)})
        return AccountingService._format_account_response(account_doc)
    
    @staticmethod
    def create_journal_entry(
        tenant_id: str,
        date: str,
        description: str,
        line_items: List[Dict],
        reference: Optional[str] = None,
        created_by: str = "system"
    ) -> Dict:
        """
        Create a journal entry (double-entry bookkeeping)
        
        Returns:
            Dict with created journal entry data
        """
        db = Database.get_db()
        
        # Validate line items
        total_debit = sum(item.get("debit", 0) for item in line_items)
        total_credit = sum(item.get("credit", 0) for item in line_items)
        
        if abs(total_debit - total_credit) > 0.01:  # Allow small rounding errors
            raise BadRequestException(
                f"Journal entry not balanced: Debit={total_debit}, Credit={total_credit}"
            )
        
        # Get next entry number
        last_entry = db.journal_entries.find_one(
            {"tenant_id": tenant_id},
            sort=[("entry_number", -1)]
        )
        entry_number = (last_entry.get("entry_number", 0) + 1) if last_entry else 1
        
        entry_data = {
            "tenant_id": tenant_id,
            "entry_number": entry_number,
            "date": date,
            "reference": reference,
            "description": description,
            "line_items": line_items,
            "total_debit": round(total_debit, 2),
            "total_credit": round(total_credit, 2),
            "balanced": True,
            "created_by": created_by,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.journal_entries.insert_one(entry_data)
        entry_id = str(result.inserted_id)
        
        # Update account balances
        for item in line_items:
            account_id = item.get("account_id")
            debit = item.get("debit", 0)
            credit = item.get("credit", 0)
            
            # Get account to determine normal balance
            account = db.accounts.find_one({"_id": ObjectId(account_id)})
            if account:
                account_type = account.get("account_type")
                
                # Assets, Expenses: Debit increases, Credit decreases
                # Liabilities, Equity, Revenue: Credit increases, Debit decreases
                if account_type in ["asset", "expense"]:
                    balance_change = debit - credit
                else:
                    balance_change = credit - debit
                
                db.accounts.update_one(
                    {"_id": ObjectId(account_id)},
                    {"$inc": {"balance": balance_change}}
                )
        
        logger.info(f"Journal entry created: {entry_id} for tenant: {tenant_id}")
        
        entry_doc = db.journal_entries.find_one({"_id": ObjectId(entry_id)})
        return AccountingService._format_journal_entry_response(entry_doc)
    
    @staticmethod
    def get_journal_entries(
        tenant_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        Get journal entries for tenant
        
        Returns:
            List of journal entry dicts
        """
        db = Database.get_db()
        
        query = {"tenant_id": tenant_id}
        
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query["$gte"] = start_date
            if end_date:
                date_query["$lte"] = end_date
            query["date"] = date_query
        
        entries = list(db.journal_entries.find(query).sort("date", -1).limit(limit))
        
        return [AccountingService._format_journal_entry_response(e) for e in entries]
    
    @staticmethod
    def generate_financial_report(
        tenant_id: str,
        report_type: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict:
        """
        Generate financial reports
        
        Returns:
            Dict with report data
        """
        db = Database.get_db()
        
        if report_type == "balance_sheet":
            return AccountingService._generate_balance_sheet(tenant_id, end_date)
        elif report_type == "income_statement":
            return AccountingService._generate_income_statement(tenant_id, start_date, end_date)
        elif report_type == "trial_balance":
            return AccountingService._generate_trial_balance(tenant_id, end_date)
        else:
            raise BadRequestException(f"Unknown report type: {report_type}")
    
    @staticmethod
    def _generate_balance_sheet(tenant_id: str, as_of_date: Optional[str] = None) -> Dict:
        """Generate balance sheet"""
        db = Database.get_db()
        
        accounts = list(db.accounts.find({
            "tenant_id": tenant_id,
            "active": True
        }))
        
        assets = [a for a in accounts if a.get("account_type") == "asset"]
        liabilities = [a for a in accounts if a.get("account_type") == "liability"]
        equity = [a for a in accounts if a.get("account_type") == "equity"]
        
        total_assets = sum(a.get("balance", 0) for a in assets)
        total_liabilities = sum(a.get("balance", 0) for a in liabilities)
        total_equity = sum(a.get("balance", 0) for a in equity)
        
        return {
            "report_type": "balance_sheet",
            "as_of_date": as_of_date or datetime.utcnow().strftime("%Y-%m-%d"),
            "assets": [AccountingService._format_account_response(a) for a in assets],
            "liabilities": [AccountingService._format_account_response(a) for a in liabilities],
            "equity": [AccountingService._format_account_response(a) for a in equity],
            "total_assets": round(total_assets, 2),
            "total_liabilities": round(total_liabilities, 2),
            "total_equity": round(total_equity, 2)
        }
    
    @staticmethod
    def _generate_income_statement(
        tenant_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict:
        """Generate income statement (P&L)"""
        db = Database.get_db()
        
        accounts = list(db.accounts.find({
            "tenant_id": tenant_id,
            "active": True
        }))
        
        revenue = [a for a in accounts if a.get("account_type") == "revenue"]
        expenses = [a for a in accounts if a.get("account_type") == "expense"]
        
        total_revenue = sum(a.get("balance", 0) for a in revenue)
        total_expenses = sum(a.get("balance", 0) for a in expenses)
        net_income = total_revenue - total_expenses
        
        return {
            "report_type": "income_statement",
            "start_date": start_date or "2024-01-01",
            "end_date": end_date or datetime.utcnow().strftime("%Y-%m-%d"),
            "revenue": [AccountingService._format_account_response(a) for a in revenue],
            "expenses": [AccountingService._format_account_response(a) for a in expenses],
            "total_revenue": round(total_revenue, 2),
            "total_expenses": round(total_expenses, 2),
            "net_income": round(net_income, 2)
        }
    
    @staticmethod
    def _generate_trial_balance(tenant_id: str, as_of_date: Optional[str] = None) -> Dict:
        """Generate trial balance"""
        db = Database.get_db()
        
        accounts = list(db.accounts.find({
            "tenant_id": tenant_id,
            "active": True
        }).sort("code", 1))
        
        total_debit = 0
        total_credit = 0
        
        account_balances = []
        for account in accounts:
            balance = account.get("balance", 0)
            account_type = account.get("account_type")
            
            # Determine debit/credit based on account type and balance
            if account_type in ["asset", "expense"]:
                debit = balance if balance > 0 else 0
                credit = abs(balance) if balance < 0 else 0
            else:
                credit = balance if balance > 0 else 0
                debit = abs(balance) if balance < 0 else 0
            
            total_debit += debit
            total_credit += credit
            
            account_balances.append({
                "code": account.get("code"),
                "name": account.get("name"),
                "account_type": account_type,
                "debit": round(debit, 2),
                "credit": round(credit, 2)
            })
        
        return {
            "report_type": "trial_balance",
            "as_of_date": as_of_date or datetime.utcnow().strftime("%Y-%m-%d"),
            "accounts": account_balances,
            "total_debit": round(total_debit, 2),
            "total_credit": round(total_credit, 2),
            "balanced": abs(total_debit - total_credit) < 0.01
        }
    
    @staticmethod
    def create_tax_rate(
        tenant_id: str,
        name: str,
        rate: float,
        description: Optional[str] = None,
        active: bool = True
    ) -> Dict:
        """
        Create a new tax rate
        
        Returns:
            Dict with created tax rate data
        """
        db = Database.get_db()
        
        # Check if name already exists
        existing = db.tax_rates.find_one({
            "tenant_id": tenant_id,
            "name": name,
            "active": True
        })
        
        if existing:
            raise BadRequestException(f"Tax rate '{name}' already exists")
        
        tax_rate_data = {
            "tenant_id": tenant_id,
            "name": name,
            "rate": round(rate, 4),  # Store as percentage (e.g., 7.5 for 7.5%)
            "description": description,
            "active": active,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.tax_rates.insert_one(tax_rate_data)
        tax_rate_id = str(result.inserted_id)
        
        logger.info(f"Tax rate created: {tax_rate_id} ({name}) for tenant: {tenant_id}")
        
        tax_rate_doc = db.tax_rates.find_one({"_id": ObjectId(tax_rate_id)})
        return AccountingService._format_tax_rate_response(tax_rate_doc)
    
    @staticmethod
    def get_tax_rates(tenant_id: str, active_only: bool = True) -> List[Dict]:
        """
        Get tax rates for tenant
        
        Returns:
            List of tax rate dicts
        """
        db = Database.get_db()
        
        query = {"tenant_id": tenant_id}
        if active_only:
            query["active"] = True
        
        tax_rates = list(db.tax_rates.find(query).sort("name", 1))
        
        return [AccountingService._format_tax_rate_response(tr) for tr in tax_rates]
    
    @staticmethod
    def update_tax_rate(
        tax_rate_id: str,
        tenant_id: str,
        **updates
    ) -> Dict:
        """
        Update a tax rate
        
        Returns:
            Dict with updated tax rate data
        """
        db = Database.get_db()
        
        tax_rate_doc = db.tax_rates.find_one({
            "_id": ObjectId(tax_rate_id),
            "tenant_id": tenant_id
        })
        
        if not tax_rate_doc:
            raise NotFoundException("Tax rate not found")
        
        update_data = {"updated_at": datetime.utcnow()}
        for key, value in updates.items():
            if value is not None:
                if key == "rate":
                    update_data[key] = round(value, 4)
                else:
                    update_data[key] = value
        
        db.tax_rates.update_one(
            {"_id": ObjectId(tax_rate_id)},
            {"$set": update_data}
        )
        
        logger.info(f"Tax rate updated: {tax_rate_id}")
        
        tax_rate_doc = db.tax_rates.find_one({"_id": ObjectId(tax_rate_id)})
        return AccountingService._format_tax_rate_response(tax_rate_doc)
    
    @staticmethod
    def calculate_tax(subtotal: float, tax_rate_id: Optional[str] = None, tenant_id: str = None) -> Dict:
        """
        Calculate tax amount based on subtotal and tax rate
        
        Returns:
            Dict with tax calculation details
        """
        if not tax_rate_id:
            return {
                "tax_rate_id": None,
                "tax_rate_name": None,
                "tax_rate": 0.0,
                "tax_amount": 0.0,
                "total": subtotal
            }
        
        db = Database.get_db()
        
        tax_rate_doc = db.tax_rates.find_one({
            "_id": ObjectId(tax_rate_id),
            "tenant_id": tenant_id,
            "active": True
        })
        
        if not tax_rate_doc:
            raise NotFoundException("Tax rate not found or inactive")
        
        tax_rate = tax_rate_doc.get("rate", 0.0)
        tax_amount = round(subtotal * (tax_rate / 100), 2)
        total = round(subtotal + tax_amount, 2)
        
        return {
            "tax_rate_id": str(tax_rate_doc["_id"]),
            "tax_rate_name": tax_rate_doc["name"],
            "tax_rate": tax_rate,
            "tax_amount": tax_amount,
            "total": total
        }
    
    @staticmethod
    def generate_tax_report(
        tenant_id: str,
        start_date: str,
        end_date: str,
        tax_rate_id: Optional[str] = None
    ) -> Dict:
        """
        Generate tax report for a period
        
        Returns:
            Dict with tax report data
        """
        db = Database.get_db()
        
        # Build query for invoices in date range
        query = {
            "tenant_id": tenant_id,
            "invoice_date": {"$gte": start_date, "$lte": end_date},
            "status": {"$ne": "cancelled"}
        }
        
        if tax_rate_id:
            query["tax_rate_id"] = tax_rate_id
        
        invoices = list(db.invoices.find(query))
        
        total_taxable_amount = 0.0
        total_tax_collected = 0.0
        invoice_count = len(invoices)
        breakdown = []
        
        # Group by tax rate
        tax_rate_groups = {}
        
        for invoice in invoices:
            subtotal = invoice.get("subtotal", 0.0)
            tax_amount = invoice.get("tax_amount", 0.0)
            tax_rate_id = invoice.get("tax_rate_id")
            tax_rate_name = invoice.get("tax_rate_name", "No Tax")
            
            total_taxable_amount += subtotal
            total_tax_collected += tax_amount
            
            # Group by tax rate
            key = tax_rate_id or "no_tax"
            if key not in tax_rate_groups:
                tax_rate_groups[key] = {
                    "tax_rate_name": tax_rate_name,
                    "invoice_count": 0,
                    "taxable_amount": 0.0,
                    "tax_collected": 0.0
                }
            
            tax_rate_groups[key]["invoice_count"] += 1
            tax_rate_groups[key]["taxable_amount"] += subtotal
            tax_rate_groups[key]["tax_collected"] += tax_amount
        
        # Convert to breakdown list
        for group_data in tax_rate_groups.values():
            breakdown.append({
                "tax_rate_name": group_data["tax_rate_name"],
                "invoice_count": group_data["invoice_count"],
                "taxable_amount": round(group_data["taxable_amount"], 2),
                "tax_collected": round(group_data["tax_collected"], 2)
            })
        
        # Get tax rate name if specific tax rate requested
        tax_rate_name = None
        if tax_rate_id:
            tax_rate_doc = db.tax_rates.find_one({"_id": ObjectId(tax_rate_id)})
            if tax_rate_doc:
                tax_rate_name = tax_rate_doc["name"]
        
        return {
            "period_start": start_date,
            "period_end": end_date,
            "tax_rate_name": tax_rate_name,
            "total_taxable_amount": round(total_taxable_amount, 2),
            "total_tax_collected": round(total_tax_collected, 2),
            "invoice_count": invoice_count,
            "breakdown": breakdown
        }
    
    @staticmethod
    def _format_tax_rate_response(tax_rate_doc: Dict) -> Dict:
        """Format tax rate document for response"""
        return {
            "id": str(tax_rate_doc["_id"]),
            "tenant_id": tax_rate_doc["tenant_id"],
            "name": tax_rate_doc["name"],
            "rate": tax_rate_doc["rate"],
            "description": tax_rate_doc.get("description"),
            "active": tax_rate_doc.get("active", True),
            "created_at": tax_rate_doc["created_at"],
            "updated_at": tax_rate_doc["updated_at"]
        }
        """Format account document for response"""
        return {
            "id": str(account_doc["_id"]),
            "tenant_id": account_doc["tenant_id"],
            "code": account_doc["code"],
            "name": account_doc["name"],
            "account_type": account_doc["account_type"],
            "sub_type": account_doc["sub_type"],
            "description": account_doc.get("description"),
            "parent_account_id": account_doc.get("parent_account_id"),
            "balance": round(account_doc.get("balance", 0), 2),
            "active": account_doc.get("active", True),
            "created_at": account_doc["created_at"],
            "updated_at": account_doc["updated_at"]
        }
    
    @staticmethod
    def _format_journal_entry_response(entry_doc: Dict) -> Dict:
        """Format journal entry document for response"""
        return {
            "id": str(entry_doc["_id"]),
            "tenant_id": entry_doc["tenant_id"],
            "entry_number": entry_doc["entry_number"],
            "date": entry_doc["date"],
            "reference": entry_doc.get("reference"),
            "description": entry_doc["description"],
            "line_items": entry_doc["line_items"],
            "total_debit": entry_doc["total_debit"],
            "total_credit": entry_doc["total_credit"],
            "balanced": entry_doc["balanced"],
            "created_by": entry_doc.get("created_by", "system"),
            "created_at": entry_doc["created_at"],
            "updated_at": entry_doc["updated_at"]
        }


# Singleton instance
accounting_service = AccountingService()
