"""
Expense Integration Service

Handles integration with expense system including:
- Expense syncing to accounting
- Category to GL account mapping
- Expense approval workflow
- Expense reconciliation
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pymongo.database import Database
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class ExpenseIntegrationService:
    def __init__(self, db: Database, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.expenses = db.expenses
        self.expense_mappings = db.expense_mappings
        self.expense_sync_logs = db.expense_sync_logs
        self.journal_entries = db.journal_entries
        self.accounts = db.accounts
        self.audit_logs = db.audit_logs

    def create_expense_mapping(
        self,
        category: str,
        account_id: str,
        description: Optional[str] = None,
        created_by: str = "system"
    ) -> Dict[str, Any]:
        """Create expense category to GL account mapping"""
        
        # Check if mapping already exists
        existing = self.expense_mappings.find_one({
            "tenant_id": self.tenant_id,
            "category": category
        })
        
        if existing:
            raise ValueError(f"Mapping already exists for category: {category}")
        
        # Verify account exists
        account = self.accounts.find_one({
            "_id": ObjectId(account_id),
            "tenant_id": self.tenant_id
        })
        
        if not account:
            raise ValueError(f"Account not found: {account_id}")
        
        mapping = {
            "tenant_id": self.tenant_id,
            "category": category,
            "account_id": account_id,
            "account_name": account["name"],
            "account_code": account["code"],
            "description": description,
            "active": True,
            "created_by": created_by,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = self.expense_mappings.insert_one(mapping)
        mapping["id"] = str(result.inserted_id)
        del mapping["_id"]
        
        # Log the creation
        self._log_audit(
            "expense_mapping",
            str(result.inserted_id),
            "create",
            None,
            mapping,
            created_by
        )
        
        return mapping

    def get_expense_mappings(self) -> List[Dict[str, Any]]:
        """Get all expense category mappings"""
        
        mappings = list(self.expense_mappings.find({
            "tenant_id": self.tenant_id,
            "active": True
        }))
        
        for mapping in mappings:
            mapping["id"] = str(mapping["_id"])
            del mapping["_id"]
        
        return mappings

    def update_expense_mapping(
        self,
        mapping_id: str,
        account_id: Optional[str] = None,
        description: Optional[str] = None,
        active: Optional[bool] = None,
        updated_by: str = "system"
    ) -> Dict[str, Any]:
        """Update expense mapping"""
        
        mapping = self.expense_mappings.find_one({
            "_id": ObjectId(mapping_id),
            "tenant_id": self.tenant_id
        })
        
        if not mapping:
            raise ValueError(f"Mapping not found: {mapping_id}")
        
        old_values = {
            "account_id": mapping.get("account_id"),
            "description": mapping.get("description"),
            "active": mapping.get("active")
        }
        
        update_data = {"updated_at": datetime.utcnow()}
        
        if account_id:
            account = self.accounts.find_one({
                "_id": ObjectId(account_id),
                "tenant_id": self.tenant_id
            })
            if not account:
                raise ValueError(f"Account not found: {account_id}")
            
            update_data["account_id"] = account_id
            update_data["account_name"] = account["name"]
            update_data["account_code"] = account["code"]
        
        if description is not None:
            update_data["description"] = description
        
        if active is not None:
            update_data["active"] = active
        
        updated = self.expense_mappings.find_one_and_update(
            {"_id": ObjectId(mapping_id), "tenant_id": self.tenant_id},
            {"$set": update_data},
            return_document=True
        )
        
        if updated:
            updated["id"] = str(updated["_id"])
            del updated["_id"]
            
            # Log the update
            self._log_audit(
                "expense_mapping",
                mapping_id,
                "update",
                old_values,
                update_data,
                updated_by
            )
        
        return updated

    def sync_expense(
        self,
        expense_id: str,
        category: str,
        amount: float,
        expense_date: str,
        description: str,
        approval_status: str = "pending",
        created_by: str = "system"
    ) -> Dict[str, Any]:
        """Sync expense to accounting"""
        
        try:
            # Check if already synced
            existing = self.expenses.find_one({
                "tenant_id": self.tenant_id,
                "expense_id": expense_id
            })
            
            if existing and existing.get("synced"):
                return {
                    "status": "already_synced",
                    "expense_id": expense_id,
                    "message": "Expense already synced"
                }
            
            # Get mapping for category
            mapping = self.expense_mappings.find_one({
                "tenant_id": self.tenant_id,
                "category": category,
                "active": True
            })
            
            if not mapping:
                raise ValueError(f"No mapping found for category: {category}")
            
            # Only create journal entry if approved
            journal_entry_id = None
            if approval_status == "approved":
                journal_entry = self._create_expense_entry(
                    expense_date=expense_date,
                    amount=amount,
                    account_id=mapping["account_id"],
                    reference=f"EXP-{expense_id}",
                    description=description
                )
                journal_entry_id = journal_entry["id"]
            
            # Record expense
            expense_record = {
                "tenant_id": self.tenant_id,
                "expense_id": expense_id,
                "category": category,
                "amount": amount,
                "expense_date": expense_date,
                "description": description,
                "approval_status": approval_status,
                "mapping_id": str(mapping["_id"]),
                "account_id": mapping["account_id"],
                "journal_entry_id": journal_entry_id,
                "synced": approval_status == "approved",
                "created_by": created_by,
                "created_at": datetime.utcnow(),
                "synced_at": datetime.utcnow() if approval_status == "approved" else None
            }
            
            if existing:
                # Update existing
                self.expenses.update_one(
                    {"_id": existing["_id"]},
                    {"$set": expense_record}
                )
                expense_record["id"] = str(existing["_id"])
            else:
                # Insert new
                result = self.expenses.insert_one(expense_record)
                expense_record["id"] = str(result.inserted_id)
            
            del expense_record["_id"] if "_id" in expense_record else None
            
            return {
                "status": "success",
                "expense_id": expense_id,
                "synced": approval_status == "approved",
                "journal_entry_id": journal_entry_id,
                "amount": amount
            }
        
        except Exception as e:
            logger.error(f"Error syncing expense: {str(e)}")
            self._log_sync_error(expense_id, str(e))
            raise

    def approve_expense(
        self,
        expense_id: str,
        approved_by: str = "system"
    ) -> Dict[str, Any]:
        """Approve expense and create journal entry"""
        
        try:
            expense = self.expenses.find_one({
                "tenant_id": self.tenant_id,
                "expense_id": expense_id
            })
            
            if not expense:
                raise ValueError(f"Expense not found: {expense_id}")
            
            if expense.get("approval_status") == "approved":
                return {
                    "status": "already_approved",
                    "expense_id": expense_id
                }
            
            # Create journal entry
            journal_entry = self._create_expense_entry(
                expense_date=expense["expense_date"],
                amount=expense["amount"],
                account_id=expense["account_id"],
                reference=f"EXP-{expense_id}",
                description=expense["description"]
            )
            
            # Update expense
            self.expenses.update_one(
                {"_id": expense["_id"]},
                {
                    "$set": {
                        "approval_status": "approved",
                        "journal_entry_id": journal_entry["id"],
                        "synced": True,
                        "synced_at": datetime.utcnow(),
                        "approved_by": approved_by,
                        "approved_at": datetime.utcnow()
                    }
                }
            )
            
            return {
                "status": "success",
                "expense_id": expense_id,
                "journal_entry_id": journal_entry["id"],
                "amount": expense["amount"]
            }
        
        except Exception as e:
            logger.error(f"Error approving expense: {str(e)}")
            raise

    def reject_expense(
        self,
        expense_id: str,
        reason: str,
        rejected_by: str = "system"
    ) -> Dict[str, Any]:
        """Reject expense"""
        
        expense = self.expenses.find_one({
            "tenant_id": self.tenant_id,
            "expense_id": expense_id
        })
        
        if not expense:
            raise ValueError(f"Expense not found: {expense_id}")
        
        self.expenses.update_one(
            {"_id": expense["_id"]},
            {
                "$set": {
                    "approval_status": "rejected",
                    "rejection_reason": reason,
                    "rejected_by": rejected_by,
                    "rejected_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "status": "success",
            "expense_id": expense_id,
            "approval_status": "rejected"
        }

    def get_expenses(
        self,
        approval_status: Optional[str] = None,
        category: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get expenses with optional filtering"""
        
        query = {"tenant_id": self.tenant_id}
        
        if approval_status:
            query["approval_status"] = approval_status
        
        if category:
            query["category"] = category
        
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query["$gte"] = start_date
            if end_date:
                date_query["$lte"] = end_date
            if date_query:
                query["expense_date"] = date_query
        
        expenses = list(
            self.expenses.find(query)
            .sort("expense_date", -1)
            .skip(offset)
            .limit(limit)
        )
        
        for exp in expenses:
            exp["id"] = str(exp["_id"])
            del exp["_id"]
        
        return expenses

    def get_expense_reconciliation(
        self,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """Get expense vs accounting reconciliation"""
        
        # Get approved expenses
        approved_expenses = list(self.expenses.find({
            "tenant_id": self.tenant_id,
            "approval_status": "approved",
            "expense_date": {
                "$gte": start_date,
                "$lte": end_date
            }
        }))
        
        # Get pending expenses
        pending_expenses = list(self.expenses.find({
            "tenant_id": self.tenant_id,
            "approval_status": "pending",
            "expense_date": {
                "$gte": start_date,
                "$lte": end_date
            }
        }))
        
        # Get rejected expenses
        rejected_expenses = list(self.expenses.find({
            "tenant_id": self.tenant_id,
            "approval_status": "rejected",
            "expense_date": {
                "$gte": start_date,
                "$lte": end_date
            }
        }))
        
        approved_total = sum(exp.get("amount", 0) for exp in approved_expenses)
        pending_total = sum(exp.get("amount", 0) for exp in pending_expenses)
        rejected_total = sum(exp.get("amount", 0) for exp in rejected_expenses)
        
        return {
            "period_start": start_date,
            "period_end": end_date,
            "approved_expenses": {
                "count": len(approved_expenses),
                "total": approved_total,
                "expenses": [
                    {
                        "id": str(exp["_id"]),
                        "expense_id": exp["expense_id"],
                        "category": exp["category"],
                        "amount": exp["amount"],
                        "expense_date": exp["expense_date"],
                        "description": exp["description"]
                    }
                    for exp in approved_expenses
                ]
            },
            "pending_expenses": {
                "count": len(pending_expenses),
                "total": pending_total,
                "expenses": [
                    {
                        "id": str(exp["_id"]),
                        "expense_id": exp["expense_id"],
                        "category": exp["category"],
                        "amount": exp["amount"],
                        "expense_date": exp["expense_date"],
                        "description": exp["description"]
                    }
                    for exp in pending_expenses
                ]
            },
            "rejected_expenses": {
                "count": len(rejected_expenses),
                "total": rejected_total
            },
            "total_expenses": approved_total + pending_total + rejected_total
        }

    def _create_expense_entry(
        self,
        expense_date: str,
        amount: float,
        account_id: str,
        reference: str,
        description: str
    ) -> Dict[str, Any]:
        """Create expense journal entry"""
        
        # Get cash account
        cash_account = self.accounts.find_one({
            "tenant_id": self.tenant_id,
            "account_type": "asset",
            "sub_type": "cash"
        })
        
        if not cash_account:
            raise ValueError("Cash account not found")
        
        # Get next entry number
        last_entry = self.journal_entries.find_one(
            {"tenant_id": self.tenant_id},
            sort=[("entry_number", -1)]
        )
        entry_number = (last_entry.get("entry_number", 0) if last_entry else 0) + 1
        
        journal_entry = {
            "tenant_id": self.tenant_id,
            "entry_number": entry_number,
            "date": expense_date,
            "reference": reference,
            "description": description,
            "line_items": [
                {
                    "account_id": account_id,
                    "debit": amount,
                    "credit": 0.0,
                    "description": "Expense"
                },
                {
                    "account_id": str(cash_account["_id"]),
                    "debit": 0.0,
                    "credit": amount,
                    "description": "Cash Payment"
                }
            ],
            "total_debit": amount,
            "total_credit": amount,
            "balanced": True,
            "created_by": "expense_integration",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = self.journal_entries.insert_one(journal_entry)
        journal_entry["id"] = str(result.inserted_id)
        del journal_entry["_id"]
        
        return journal_entry

    def _log_sync_error(self, expense_id: str, error: str) -> None:
        """Log expense sync error"""
        
        sync_log = {
            "tenant_id": self.tenant_id,
            "expense_id": expense_id,
            "status": "error",
            "error": error,
            "timestamp": datetime.utcnow(),
            "created_at": datetime.utcnow()
        }
        
        self.expense_sync_logs.insert_one(sync_log)

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
