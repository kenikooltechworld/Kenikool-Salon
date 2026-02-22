"""
Period Close and Year-End Service

Handles period closing and year-end close processes including:
- Period locking and unlocking
- Closing entry creation
- Year-end close process
- Retained earnings transfer
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pymongo.database import Database
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class PeriodCloseService:
    def __init__(self, db: Database, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.period_closes = db.period_closes
        self.closing_entries = db.closing_entries
        self.journal_entries = db.journal_entries
        self.accounts = db.accounts
        self.audit_logs = db.audit_logs

    def create_period_close(
        self,
        period_start: str,
        period_end: str,
        period_type: str,
        description: Optional[str] = None,
        created_by: str = "system"
    ) -> Dict[str, Any]:
        """Create a new period close record"""
        
        period_close = {
            "tenant_id": self.tenant_id,
            "period_start": period_start,
            "period_end": period_end,
            "period_type": period_type,
            "description": description,
            "status": "open",
            "locked": False,
            "notes": None,
            "created_by": created_by,
            "created_at": datetime.utcnow(),
            "closed_at": None,
            "reopened_at": None,
            "reopened_by": None
        }
        
        result = self.period_closes.insert_one(period_close)
        period_close["id"] = str(result.inserted_id)
        del period_close["_id"]
        
        # Log the creation
        self._log_audit("period_close", str(result.inserted_id), "create", None, period_close, created_by)
        
        return period_close

    def get_period_close(self, period_close_id: str) -> Optional[Dict[str, Any]]:
        """Get a period close by ID"""
        
        period_close = self.period_closes.find_one({
            "_id": ObjectId(period_close_id),
            "tenant_id": self.tenant_id
        })
        
        if period_close:
            period_close["id"] = str(period_close["_id"])
            del period_close["_id"]
        
        return period_close

    def get_period_closes(
        self,
        status: Optional[str] = None,
        period_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get period closes with optional filtering"""
        
        query = {"tenant_id": self.tenant_id}
        
        if status:
            query["status"] = status
        if period_type:
            query["period_type"] = period_type
        
        period_closes = list(
            self.period_closes.find(query)
            .sort("period_end", -1)
            .skip(offset)
            .limit(limit)
        )
        
        for pc in period_closes:
            pc["id"] = str(pc["_id"])
            del pc["_id"]
        
        return period_closes

    def lock_period(
        self,
        period_close_id: str,
        locked_by: str = "system"
    ) -> Dict[str, Any]:
        """Lock a period to prevent further edits"""
        
        period_close = self.get_period_close(period_close_id)
        if not period_close:
            raise ValueError(f"Period close {period_close_id} not found")
        
        old_values = {"locked": period_close.get("locked", False)}
        
        updated = self.period_closes.find_one_and_update(
            {"_id": ObjectId(period_close_id), "tenant_id": self.tenant_id},
            {
                "$set": {
                    "locked": True,
                    "status": "closed",
                    "closed_at": datetime.utcnow()
                }
            },
            return_document=True
        )
        
        if updated:
            updated["id"] = str(updated["_id"])
            del updated["_id"]
            
            # Log the lock
            self._log_audit(
                "period_close",
                period_close_id,
                "update",
                old_values,
                {"locked": True, "status": "closed"},
                locked_by
            )
        
        return updated

    def unlock_period(
        self,
        period_close_id: str,
        reopen_reason: Optional[str] = None,
        reopened_by: str = "system"
    ) -> Dict[str, Any]:
        """Unlock a period to allow edits"""
        
        period_close = self.get_period_close(period_close_id)
        if not period_close:
            raise ValueError(f"Period close {period_close_id} not found")
        
        old_values = {
            "locked": period_close.get("locked", True),
            "status": period_close.get("status", "closed")
        }
        
        updated = self.period_closes.find_one_and_update(
            {"_id": ObjectId(period_close_id), "tenant_id": self.tenant_id},
            {
                "$set": {
                    "locked": False,
                    "status": "reopened",
                    "reopened_at": datetime.utcnow(),
                    "reopened_by": reopened_by,
                    "notes": reopen_reason
                }
            },
            return_document=True
        )
        
        if updated:
            updated["id"] = str(updated["_id"])
            del updated["_id"]
            
            # Log the unlock
            self._log_audit(
                "period_close",
                period_close_id,
                "update",
                old_values,
                {"locked": False, "status": "reopened"},
                reopened_by
            )
        
        return updated

    def is_period_locked(self, period_start: str, period_end: str) -> bool:
        """Check if a period is locked"""
        
        period_close = self.period_closes.find_one({
            "tenant_id": self.tenant_id,
            "period_start": period_start,
            "period_end": period_end,
            "locked": True
        })
        
        return period_close is not None

    def create_closing_entries(
        self,
        fiscal_year: int,
        close_date: str,
        retained_earnings_account_id: str,
        created_by: str = "system"
    ) -> Dict[str, Any]:
        """Create closing entries for year-end close"""
        
        # Get all revenue and expense accounts
        revenue_accounts = list(self.accounts.find({
            "tenant_id": self.tenant_id,
            "account_type": "revenue",
            "active": True
        }))
        
        expense_accounts = list(self.accounts.find({
            "tenant_id": self.tenant_id,
            "account_type": "expense",
            "active": True
        }))
        
        # Get income summary account (or create if doesn't exist)
        income_summary = self.accounts.find_one({
            "tenant_id": self.tenant_id,
            "code": "9999",
            "name": "Income Summary"
        })
        
        if not income_summary:
            # Create income summary account
            income_summary_doc = {
                "tenant_id": self.tenant_id,
                "code": "9999",
                "name": "Income Summary",
                "account_type": "equity",
                "sub_type": "retained_earnings",
                "description": "Temporary account for closing entries",
                "balance": 0.0,
                "active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            result = self.accounts.insert_one(income_summary_doc)
            income_summary_id = str(result.inserted_id)
        else:
            income_summary_id = str(income_summary["_id"])
        
        closing_entries = []
        total_revenue = 0.0
        total_expenses = 0.0
        
        # Create closing entry for revenues
        revenue_line_items = []
        for account in revenue_accounts:
            balance = account.get("balance", 0.0)
            if balance != 0:
                total_revenue += balance
                revenue_line_items.append({
                    "account_id": str(account["_id"]),
                    "debit": balance,  # Debit revenue to close it
                    "credit": 0.0,
                    "description": f"Closing {account['name']}"
                })
        
        if revenue_line_items:
            # Add credit to income summary
            revenue_line_items.append({
                "account_id": income_summary_id,
                "debit": 0.0,
                "credit": total_revenue,
                "description": "Income Summary - Revenue"
            })
            
            # Create journal entry for revenues
            revenue_entry = self._create_journal_entry(
                date=close_date,
                reference=f"CLOSING-REV-{fiscal_year}",
                description=f"Closing revenue accounts for fiscal year {fiscal_year}",
                line_items=revenue_line_items,
                created_by=created_by
            )
            closing_entries.append(revenue_entry)
        
        # Create closing entry for expenses
        expense_line_items = []
        for account in expense_accounts:
            balance = account.get("balance", 0.0)
            if balance != 0:
                total_expenses += balance
                expense_line_items.append({
                    "account_id": str(account["_id"]),
                    "debit": 0.0,
                    "credit": balance,  # Credit expense to close it
                    "description": f"Closing {account['name']}"
                })
        
        if expense_line_items:
            # Add debit to income summary
            expense_line_items.append({
                "account_id": income_summary_id,
                "debit": total_expenses,
                "credit": 0.0,
                "description": "Income Summary - Expenses"
            })
            
            # Create journal entry for expenses
            expense_entry = self._create_journal_entry(
                date=close_date,
                reference=f"CLOSING-EXP-{fiscal_year}",
                description=f"Closing expense accounts for fiscal year {fiscal_year}",
                line_items=expense_line_items,
                created_by=created_by
            )
            closing_entries.append(expense_entry)
        
        # Create closing entry to transfer net income to retained earnings
        net_income = total_revenue - total_expenses
        
        if net_income != 0:
            retained_earnings_line_items = [
                {
                    "account_id": income_summary_id,
                    "debit": 0.0 if net_income > 0 else abs(net_income),
                    "credit": net_income if net_income > 0 else 0.0,
                    "description": "Income Summary - Net Income"
                },
                {
                    "account_id": retained_earnings_account_id,
                    "debit": net_income if net_income > 0 else 0.0,
                    "credit": 0.0 if net_income > 0 else abs(net_income),
                    "description": "Retained Earnings - Net Income"
                }
            ]
            
            retained_earnings_entry = self._create_journal_entry(
                date=close_date,
                reference=f"CLOSING-RE-{fiscal_year}",
                description=f"Closing net income to retained earnings for fiscal year {fiscal_year}",
                line_items=retained_earnings_line_items,
                created_by=created_by
            )
            closing_entries.append(retained_earnings_entry)
        
        return {
            "fiscal_year": fiscal_year,
            "close_date": close_date,
            "net_income": net_income,
            "closing_entries_created": len(closing_entries),
            "journal_entry_ids": [entry["id"] for entry in closing_entries],
            "total_revenue": total_revenue,
            "total_expenses": total_expenses
        }

    def perform_year_end_close(
        self,
        fiscal_year: int,
        close_date: str,
        retained_earnings_account_id: str,
        create_closing_entries: bool = True,
        notes: Optional[str] = None,
        created_by: str = "system"
    ) -> Dict[str, Any]:
        """Perform year-end close process"""
        
        # Create period close record
        period_close = self.create_period_close(
            period_start=f"{fiscal_year}-01-01",
            period_end=f"{fiscal_year}-12-31",
            period_type="yearly",
            description=f"Year-end close for fiscal year {fiscal_year}",
            created_by=created_by
        )
        
        # Create closing entries if requested
        closing_result = None
        if create_closing_entries:
            closing_result = self.create_closing_entries(
                fiscal_year=fiscal_year,
                close_date=close_date,
                retained_earnings_account_id=retained_earnings_account_id,
                created_by=created_by
            )
        
        # Lock the period
        self.lock_period(period_close["id"], created_by)
        
        # Update period close with year-end status
        updated = self.period_closes.find_one_and_update(
            {"_id": ObjectId(period_close["id"]), "tenant_id": self.tenant_id},
            {
                "$set": {
                    "status": "year_end_closed",
                    "notes": notes,
                    "completed_at": datetime.utcnow()
                }
            },
            return_document=True
        )
        
        if updated:
            updated["id"] = str(updated["_id"])
            del updated["_id"]
        
        return {
            "id": updated["id"] if updated else period_close["id"],
            "fiscal_year": fiscal_year,
            "close_date": close_date,
            "status": "year_end_closed",
            "net_income": closing_result["net_income"] if closing_result else 0.0,
            "closing_entries_created": closing_result["closing_entries_created"] if closing_result else 0,
            "journal_entry_ids": closing_result["journal_entry_ids"] if closing_result else [],
            "created_by": created_by,
            "created_at": datetime.utcnow().isoformat()
        }

    def get_year_end_report(
        self,
        fiscal_year: int
    ) -> Optional[Dict[str, Any]]:
        """Get year-end close report"""
        
        period_close = self.period_closes.find_one({
            "tenant_id": self.tenant_id,
            "period_start": f"{fiscal_year}-01-01",
            "period_end": f"{fiscal_year}-12-31",
            "status": "year_end_closed"
        })
        
        if not period_close:
            return None
        
        # Get closing entries
        closing_entries = list(self.closing_entries.find({
            "tenant_id": self.tenant_id,
            "fiscal_year": fiscal_year
        }))
        
        # Calculate net income
        total_revenue = 0.0
        total_expenses = 0.0
        
        for entry in closing_entries:
            if entry.get("closing_type") == "revenue":
                total_revenue += entry.get("credit", 0.0)
            elif entry.get("closing_type") == "expense":
                total_expenses += entry.get("debit", 0.0)
        
        net_income = total_revenue - total_expenses
        
        return {
            "fiscal_year": fiscal_year,
            "close_date": period_close.get("closed_at", "").isoformat() if period_close.get("closed_at") else None,
            "net_income": net_income,
            "total_revenue": total_revenue,
            "total_expenses": total_expenses,
            "closing_entries": len(closing_entries),
            "status": period_close.get("status"),
            "created_by": period_close.get("created_by"),
            "created_at": period_close.get("created_at").isoformat() if period_close.get("created_at") else None
        }

    def _create_journal_entry(
        self,
        date: str,
        reference: str,
        description: str,
        line_items: List[Dict[str, Any]],
        created_by: str
    ) -> Dict[str, Any]:
        """Create a journal entry"""
        
        # Calculate totals
        total_debit = sum(item.get("debit", 0.0) for item in line_items)
        total_credit = sum(item.get("credit", 0.0) for item in line_items)
        
        # Get next entry number
        last_entry = self.journal_entries.find_one(
            {"tenant_id": self.tenant_id},
            sort=[("entry_number", -1)]
        )
        entry_number = (last_entry.get("entry_number", 0) if last_entry else 0) + 1
        
        journal_entry = {
            "tenant_id": self.tenant_id,
            "entry_number": entry_number,
            "date": date,
            "reference": reference,
            "description": description,
            "line_items": line_items,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "balanced": abs(total_debit - total_credit) < 0.01,
            "created_by": created_by,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = self.journal_entries.insert_one(journal_entry)
        journal_entry["id"] = str(result.inserted_id)
        del journal_entry["_id"]
        
        return journal_entry

    def _log_audit(
        self,
        entity_type: str,
        entity_id: str,
        action: str,
        old_values: Optional[Dict[str, Any]],
        new_values: Optional[Dict[str, Any]],
        user_id: str
    ) -> None:
        """Log an audit entry"""
        
        audit_log = {
            "tenant_id": self.tenant_id,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "action": action,
            "old_values": old_values or {},
            "new_values": new_values or {},
            "user_id": user_id,
            "timestamp": datetime.utcnow(),
            "created_at": datetime.utcnow()
        }
        
        self.audit_logs.insert_one(audit_log)
