"""
Bank Reconciliation Service

Handles bank reconciliation operations including:
- Starting new reconciliations
- Matching transactions
- Completing reconciliations
- Managing reconciliation periods
"""

from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pymongo.database import Database
from bson import ObjectId
import uuid


class BankReconciliationService:
    def __init__(self, db: Database, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.reconciliations = db.reconciliations
        self.accounts = db.accounts
        self.journal_entries = db.journal_entries

    def get_reconciliations(
        self,
        account_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get reconciliations with optional filtering"""
        
        query = {"tenant_id": self.tenant_id}
        
        if account_id:
            query["account_id"] = account_id
        if status:
            query["status"] = status
        
        reconciliations = list(
            self.reconciliations.find(query)
            .sort("created_at", -1)
            .skip(offset)
            .limit(limit)
        )
        
        # Convert ObjectId to string for JSON serialization
        for recon in reconciliations:
            recon["id"] = str(recon["_id"])
            del recon["_id"]
        
        return reconciliations

    def create_reconciliation(self, reconciliation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start a new bank reconciliation"""
        
        account_id = reconciliation_data["account_id"]
        reconciliation_date = reconciliation_data["reconciliation_date"]
        statement_date = reconciliation_data["statement_date"]
        statement_balance = reconciliation_data["statement_balance"]
        
        # Get account information
        account = self.accounts.find_one({
            "_id": ObjectId(account_id),
            "tenant_id": self.tenant_id
        })
        
        if not account:
            raise ValueError("Account not found")
        
        # Calculate beginning balance (ending balance of last reconciliation)
        beginning_balance = self._get_last_reconciled_balance(account_id, reconciliation_date)
        
        # Get unreconciled transactions
        transactions = self._get_unreconciled_transactions(account_id, reconciliation_date)
        
        # Calculate current book balance
        book_balance = beginning_balance + sum(t["amount"] for t in transactions)
        
        reconciliation_doc = {
            "tenant_id": self.tenant_id,
            "account_id": account_id,
            "account_name": account.get("name", "Unknown Account"),
            "reconciliation_date": reconciliation_date,
            "statement_date": statement_date,
            "beginning_balance": beginning_balance,
            "ending_balance": book_balance,
            "statement_balance": statement_balance,
            "reconciled_balance": beginning_balance,
            "difference": statement_balance - beginning_balance,
            "status": "in_progress",
            "created_by": reconciliation_data.get("created_by", "system"),
            "created_at": datetime.utcnow(),
            "completed_at": None,
            "transaction_count": len(transactions),
            "matched_count": 0,
            "unmatched_count": len(transactions),
            "matched_transactions": [],
            "adjustments": []
        }
        
        result = self.reconciliations.insert_one(reconciliation_doc)
        reconciliation_doc["id"] = str(result.inserted_id)
        del reconciliation_doc["_id"]
        
        return reconciliation_doc

    def update_reconciliation(
        self, 
        reconciliation_id: str, 
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update reconciliation with matched transactions"""
        
        update_fields = {}
        
        if "matched_transactions" in update_data:
            matched_transactions = update_data["matched_transactions"]
            update_fields["matched_transactions"] = matched_transactions
            update_fields["matched_count"] = len(matched_transactions)
            update_fields["unmatched_count"] = update_fields.get("transaction_count", 0) - len(matched_transactions)
            
            # Get current reconciliation to calculate new balance
            current_recon = self.reconciliations.find_one({"_id": ObjectId(reconciliation_id)})
            if current_recon:
                matched_amount = sum(t.get("amount", 0) for t in matched_transactions)
                update_fields["reconciled_balance"] = current_recon["beginning_balance"] + matched_amount
                update_fields["difference"] = current_recon["statement_balance"] - update_fields["reconciled_balance"]
        
        if "adjustments" in update_data:
            update_fields["adjustments"] = update_data["adjustments"]
            # Recalculate reconciled balance with adjustments
            current_recon = self.reconciliations.find_one({"_id": ObjectId(reconciliation_id)})
            if current_recon:
                adjustment_amount = sum(adj.get("amount", 0) for adj in update_data["adjustments"])
                base_balance = update_fields.get("reconciled_balance", current_recon.get("reconciled_balance", 0))
                update_fields["reconciled_balance"] = base_balance + adjustment_amount
                update_fields["difference"] = current_recon["statement_balance"] - update_fields["reconciled_balance"]
        
        update_fields["updated_at"] = datetime.utcnow()
        
        self.reconciliations.update_one(
            {"_id": ObjectId(reconciliation_id)},
            {"$set": update_fields}
        )
        
        return self.get_reconciliation(reconciliation_id)

    def complete_reconciliation(
        self, 
        reconciliation_id: str, 
        completion_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Complete a bank reconciliation"""
        
        reconciliation = self.get_reconciliation(reconciliation_id)
        
        if reconciliation["status"] != "in_progress":
            raise ValueError("Reconciliation is not in progress")
        
        # Validate reconciliation is balanced
        if abs(reconciliation["difference"]) > 0.01:
            raise ValueError("Reconciliation is not balanced. Difference must be zero.")
        
        # Create adjustment entries if needed
        if reconciliation.get("adjustments"):
            for adjustment in reconciliation["adjustments"]:
                self._create_adjustment_entry(reconciliation, adjustment)
        
        # Mark matched transactions as reconciled
        if reconciliation.get("matched_transactions"):
            self._mark_transactions_reconciled(reconciliation["matched_transactions"], reconciliation_id)
        
        # Update reconciliation status
        self.reconciliations.update_one(
            {"_id": ObjectId(reconciliation_id)},
            {
                "$set": {
                    "status": "completed",
                    "completed_at": datetime.utcnow(),
                    "completed_by": completion_data.get("completed_by", "system")
                }
            }
        )
        
        return self.get_reconciliation(reconciliation_id)

    def get_reconciliation(self, reconciliation_id: str) -> Dict[str, Any]:
        """Get a specific reconciliation by ID"""
        
        reconciliation = self.reconciliations.find_one({"_id": ObjectId(reconciliation_id)})
        
        if not reconciliation:
            raise ValueError("Reconciliation not found")
        
        reconciliation["id"] = str(reconciliation["_id"])
        del reconciliation["_id"]
        
        # Get transactions for this reconciliation
        reconciliation["transactions"] = self._get_unreconciled_transactions(
            reconciliation["account_id"], 
            reconciliation["reconciliation_date"]
        )
        
        return reconciliation

    def get_unreconciled_transactions(
        self, 
        account_id: str, 
        as_of_date: str
    ) -> List[Dict[str, Any]]:
        """Get unreconciled transactions for an account"""
        
        return self._get_unreconciled_transactions(account_id, as_of_date)

    def add_reconciliation_adjustment(
        self, 
        reconciliation_id: str, 
        adjustment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add an adjustment entry to reconciliation"""
        
        adjustment = {
            "id": str(uuid.uuid4()),
            "reconciliation_id": reconciliation_id,
            "description": adjustment_data["description"],
            "amount": adjustment_data["amount"],
            "account_id": adjustment_data.get("account_id"),
            "reference": adjustment_data.get("reference"),
            "created_at": datetime.utcnow()
        }
        
        # Add adjustment to reconciliation
        self.reconciliations.update_one(
            {"_id": ObjectId(reconciliation_id)},
            {"$push": {"adjustments": adjustment}}
        )
        
        return adjustment

    def _get_last_reconciled_balance(self, account_id: str, as_of_date: str) -> float:
        """Get the last reconciled balance for an account"""
        
        last_reconciliation = self.reconciliations.find_one(
            {
                "tenant_id": self.tenant_id,
                "account_id": account_id,
                "status": "completed",
                "reconciliation_date": {"$lt": as_of_date}
            },
            sort=[("reconciliation_date", -1)]
        )
        
        if last_reconciliation:
            return last_reconciliation.get("statement_balance", 0.0)
        
        # If no previous reconciliation, get account opening balance
        account = self.accounts.find_one({"_id": ObjectId(account_id)})
        return account.get("opening_balance", 0.0) if account else 0.0

    def _get_unreconciled_transactions(self, account_id: str, as_of_date: str) -> List[Dict[str, Any]]:
        """Get unreconciled transactions for an account up to a specific date"""
        
        # Query journal entries that affect this account and are not reconciled
        pipeline = [
            {
                "$match": {
                    "tenant_id": self.tenant_id,
                    "date": {"$lte": as_of_date},
                    "line_items.account_id": account_id
                }
            },
            {
                "$unwind": "$line_items"
            },
            {
                "$match": {
                    "line_items.account_id": account_id,
                    "line_items.reconciled": {"$ne": True}
                }
            },
            {
                "$project": {
                    "id": {"$toString": "$_id"},
                    "date": 1,
                    "description": 1,
                    "reference": 1,
                    "amount": {
                        "$subtract": ["$line_items.debit", "$line_items.credit"]
                    },
                    "type": {
                        "$cond": {
                            "if": {"$gt": ["$line_items.debit", 0]},
                            "then": "debit",
                            "else": "credit"
                        }
                    },
                    "reconciled": "$line_items.reconciled",
                    "journal_entry_id": {"$toString": "$_id"},
                    "line_item_id": "$line_items.id"
                }
            },
            {
                "$sort": {"date": 1}
            }
        ]
        
        transactions = list(self.journal_entries.aggregate(pipeline))
        
        return transactions

    def _create_adjustment_entry(self, reconciliation: Dict[str, Any], adjustment: Dict[str, Any]):
        """Create a journal entry for reconciliation adjustment"""
        
        # Create journal entry for the adjustment
        journal_entry = {
            "tenant_id": self.tenant_id,
            "entry_number": self._get_next_entry_number(),
            "date": reconciliation["reconciliation_date"],
            "description": f"Bank Reconciliation Adjustment: {adjustment['description']}",
            "reference": f"RECON-{reconciliation['id'][:8]}",
            "line_items": [
                {
                    "id": str(uuid.uuid4()),
                    "account_id": reconciliation["account_id"],
                    "debit": adjustment["amount"] if adjustment["amount"] > 0 else 0,
                    "credit": abs(adjustment["amount"]) if adjustment["amount"] < 0 else 0,
                    "description": adjustment["description"]
                },
                {
                    "id": str(uuid.uuid4()),
                    "account_id": adjustment.get("account_id", "misc_expense_account"),
                    "debit": abs(adjustment["amount"]) if adjustment["amount"] < 0 else 0,
                    "credit": adjustment["amount"] if adjustment["amount"] > 0 else 0,
                    "description": adjustment["description"]
                }
            ],
            "total_debit": abs(adjustment["amount"]),
            "total_credit": abs(adjustment["amount"]),
            "balanced": True,
            "created_by": "system",
            "created_at": datetime.utcnow(),
            "reconciliation_id": reconciliation["id"]
        }
        
        self.journal_entries.insert_one(journal_entry)

    def _mark_transactions_reconciled(self, matched_transactions: List[Dict[str, Any]], reconciliation_id: str):
        """Mark matched transactions as reconciled"""
        
        for transaction in matched_transactions:
            self.journal_entries.update_one(
                {
                    "_id": ObjectId(transaction["journal_entry_id"]),
                    "line_items.id": transaction["line_item_id"]
                },
                {
                    "$set": {
                        "line_items.$.reconciled": True,
                        "line_items.$.reconciliation_id": reconciliation_id,
                        "line_items.$.reconciled_at": datetime.utcnow()
                    }
                }
            )

    def _get_next_entry_number(self) -> int:
        """Get the next journal entry number"""
        
        last_entry = self.journal_entries.find_one(
            {"tenant_id": self.tenant_id},
            sort=[("entry_number", -1)]
        )
        
        return (last_entry.get("entry_number", 0) + 1) if last_entry else 1

    def get_reconciliation_history(
        self, 
        account_id: str, 
        limit: int = 12
    ) -> List[Dict[str, Any]]:
        """Get reconciliation history for an account"""
        
        reconciliations = list(
            self.reconciliations.find(
                {
                    "tenant_id": self.tenant_id,
                    "account_id": account_id,
                    "status": "completed"
                }
            )
            .sort("reconciliation_date", -1)
            .limit(limit)
        )
        
        for recon in reconciliations:
            recon["id"] = str(recon["_id"])
            del recon["_id"]
        
        return reconciliations

    def get_reconciliation_summary(self, account_id: str) -> Dict[str, Any]:
        """Get reconciliation summary for an account"""
        
        # Get last reconciliation
        last_reconciliation = self.reconciliations.find_one(
            {
                "tenant_id": self.tenant_id,
                "account_id": account_id,
                "status": "completed"
            },
            sort=[("reconciliation_date", -1)]
        )
        
        # Get current account balance
        account = self.accounts.find_one({"_id": ObjectId(account_id)})
        current_balance = account.get("balance", 0.0) if account else 0.0
        
        # Count unreconciled transactions
        unreconciled_count = len(self._get_unreconciled_transactions(
            account_id, 
            datetime.now().strftime("%Y-%m-%d")
        ))
        
        summary = {
            "account_id": account_id,
            "last_reconciled_date": None,
            "last_reconciled_balance": 0.0,
            "current_book_balance": current_balance,
            "unreconciled_transactions": unreconciled_count,
            "unreconciled_amount": 0.0,  # Would need to calculate this
            "days_since_last_reconciliation": None,
            "reconciliation_frequency": "monthly"
        }
        
        if last_reconciliation:
            summary["last_reconciled_date"] = last_reconciliation["reconciliation_date"]
            summary["last_reconciled_balance"] = last_reconciliation["statement_balance"]
            
            # Calculate days since last reconciliation
            last_date = datetime.strptime(last_reconciliation["reconciliation_date"], "%Y-%m-%d")
            days_since = (datetime.now() - last_date).days
            summary["days_since_last_reconciliation"] = days_since
        
        return summary