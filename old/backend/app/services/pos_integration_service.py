"""
POS Integration Service

Handles integration with POS system including:
- POS transaction syncing
- Revenue journal entry creation
- COGS recording
- Payment posting
- POS reconciliation
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pymongo.database import Database
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class POSIntegrationService:
    def __init__(self, db: Database, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.pos_transactions = db.pos_transactions
        self.pos_sync_logs = db.pos_sync_logs
        self.journal_entries = db.journal_entries
        self.accounts = db.accounts
        self.audit_logs = db.audit_logs

    def sync_pos_transaction(
        self,
        pos_transaction_id: str,
        transaction_date: str,
        transaction_type: str,
        amount: float,
        items: List[Dict[str, Any]],
        payment_method: str,
        reference: Optional[str] = None,
        notes: Optional[str] = None,
        created_by: str = "system"
    ) -> Dict[str, Any]:
        """Sync a POS transaction to accounting"""
        
        try:
            # Check if transaction already synced
            existing = self.pos_transactions.find_one({
                "tenant_id": self.tenant_id,
                "pos_transaction_id": pos_transaction_id
            })
            
            if existing:
                return {
                    "status": "already_synced",
                    "pos_transaction_id": pos_transaction_id,
                    "message": "Transaction already synced"
                }
            
            # Get revenue account
            revenue_account = self.accounts.find_one({
                "tenant_id": self.tenant_id,
                "account_type": "revenue",
                "sub_type": "service_revenue"
            })
            
            if not revenue_account:
                raise ValueError("Revenue account not found")
            
            # Get payment account based on payment method
            payment_account = self._get_payment_account(payment_method)
            if not payment_account:
                raise ValueError(f"Payment account not found for method: {payment_method}")
            
            # Create journal entry for revenue
            journal_entry = self._create_revenue_entry(
                transaction_date=transaction_date,
                amount=amount,
                revenue_account_id=str(revenue_account["_id"]),
                payment_account_id=str(payment_account["_id"]),
                reference=reference or f"POS-{pos_transaction_id}",
                description=f"POS Transaction: {transaction_type}"
            )
            
            # Record POS transaction
            pos_record = {
                "tenant_id": self.tenant_id,
                "pos_transaction_id": pos_transaction_id,
                "transaction_date": transaction_date,
                "transaction_type": transaction_type,
                "amount": amount,
                "items": items,
                "payment_method": payment_method,
                "reference": reference,
                "notes": notes,
                "journal_entry_id": journal_entry["id"],
                "status": "synced",
                "created_by": created_by,
                "created_at": datetime.utcnow(),
                "synced_at": datetime.utcnow()
            }
            
            result = self.pos_transactions.insert_one(pos_record)
            pos_record["id"] = str(result.inserted_id)
            del pos_record["_id"]
            
            # Log the sync
            self._log_audit(
                "pos_transaction",
                str(result.inserted_id),
                "create",
                None,
                pos_record,
                created_by
            )
            
            return {
                "status": "success",
                "pos_transaction_id": pos_transaction_id,
                "journal_entry_id": journal_entry["id"],
                "amount": amount
            }
        
        except Exception as e:
            logger.error(f"Error syncing POS transaction: {str(e)}")
            self._log_sync_error(pos_transaction_id, str(e))
            raise

    def record_cogs(
        self,
        pos_transaction_id: str,
        items: List[Dict[str, Any]],
        created_by: str = "system"
    ) -> Dict[str, Any]:
        """Record cost of goods sold for POS transaction"""
        
        try:
            # Get POS transaction
            pos_transaction = self.pos_transactions.find_one({
                "tenant_id": self.tenant_id,
                "pos_transaction_id": pos_transaction_id
            })
            
            if not pos_transaction:
                raise ValueError(f"POS transaction not found: {pos_transaction_id}")
            
            # Get COGS account
            cogs_account = self.accounts.find_one({
                "tenant_id": self.tenant_id,
                "account_type": "expense",
                "sub_type": "cost_of_goods"
            })
            
            if not cogs_account:
                raise ValueError("COGS account not found")
            
            # Get inventory account
            inventory_account = self.accounts.find_one({
                "tenant_id": self.tenant_id,
                "account_type": "asset",
                "sub_type": "inventory"
            })
            
            if not inventory_account:
                raise ValueError("Inventory account not found")
            
            # Calculate total COGS
            total_cogs = sum(item.get("cost", 0) * item.get("quantity", 1) for item in items)
            
            if total_cogs <= 0:
                return {
                    "status": "skipped",
                    "message": "No COGS to record"
                }
            
            # Create COGS journal entry
            journal_entry = self._create_cogs_entry(
                transaction_date=pos_transaction["transaction_date"],
                amount=total_cogs,
                cogs_account_id=str(cogs_account["_id"]),
                inventory_account_id=str(inventory_account["_id"]),
                reference=f"COGS-{pos_transaction_id}",
                description=f"COGS for POS Transaction: {pos_transaction_id}"
            )
            
            # Update POS transaction with COGS entry
            self.pos_transactions.update_one(
                {"_id": pos_transaction["_id"]},
                {
                    "$set": {
                        "cogs_journal_entry_id": journal_entry["id"],
                        "cogs_amount": total_cogs,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return {
                "status": "success",
                "pos_transaction_id": pos_transaction_id,
                "cogs_amount": total_cogs,
                "journal_entry_id": journal_entry["id"]
            }
        
        except Exception as e:
            logger.error(f"Error recording COGS: {str(e)}")
            raise

    def post_payment(
        self,
        pos_transaction_id: str,
        payment_method: str,
        amount: float,
        created_by: str = "system"
    ) -> Dict[str, Any]:
        """Post payment to bank account"""
        
        try:
            # Get POS transaction
            pos_transaction = self.pos_transactions.find_one({
                "tenant_id": self.tenant_id,
                "pos_transaction_id": pos_transaction_id
            })
            
            if not pos_transaction:
                raise ValueError(f"POS transaction not found: {pos_transaction_id}")
            
            # Get payment account
            payment_account = self._get_payment_account(payment_method)
            if not payment_account:
                raise ValueError(f"Payment account not found for method: {payment_method}")
            
            # Update payment account balance
            self.accounts.update_one(
                {"_id": payment_account["_id"]},
                {
                    "$inc": {"balance": amount}
                }
            )
            
            # Update POS transaction
            self.pos_transactions.update_one(
                {"_id": pos_transaction["_id"]},
                {
                    "$set": {
                        "payment_posted": True,
                        "payment_account_id": str(payment_account["_id"]),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return {
                "status": "success",
                "pos_transaction_id": pos_transaction_id,
                "payment_account": payment_account["name"],
                "amount": amount
            }
        
        except Exception as e:
            logger.error(f"Error posting payment: {str(e)}")
            raise

    def get_pos_transactions(
        self,
        status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get POS transactions with optional filtering"""
        
        query = {"tenant_id": self.tenant_id}
        
        if status:
            query["status"] = status
        
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query["$gte"] = start_date
            if end_date:
                date_query["$lte"] = end_date
            if date_query:
                query["transaction_date"] = date_query
        
        transactions = list(
            self.pos_transactions.find(query)
            .sort("transaction_date", -1)
            .skip(offset)
            .limit(limit)
        )
        
        for tx in transactions:
            tx["id"] = str(tx["_id"])
            del tx["_id"]
        
        return transactions

    def get_pos_reconciliation(
        self,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """Get POS vs accounting reconciliation"""
        
        # Get POS totals
        pos_transactions = list(self.pos_transactions.find({
            "tenant_id": self.tenant_id,
            "transaction_date": {
                "$gte": start_date,
                "$lte": end_date
            },
            "status": "synced"
        }))
        
        pos_total = sum(tx.get("amount", 0) for tx in pos_transactions)
        pos_count = len(pos_transactions)
        
        # Get accounting totals (from revenue account)
        revenue_account = self.accounts.find_one({
            "tenant_id": self.tenant_id,
            "account_type": "revenue",
            "sub_type": "service_revenue"
        })
        
        accounting_total = revenue_account.get("balance", 0) if revenue_account else 0
        
        # Calculate variance
        variance = abs(pos_total - accounting_total)
        variance_percent = (variance / pos_total * 100) if pos_total > 0 else 0
        
        return {
            "period_start": start_date,
            "period_end": end_date,
            "pos_total": pos_total,
            "pos_transaction_count": pos_count,
            "accounting_total": accounting_total,
            "variance": variance,
            "variance_percent": variance_percent,
            "reconciled": variance < 0.01,
            "transactions": [
                {
                    "id": str(tx["_id"]),
                    "pos_transaction_id": tx["pos_transaction_id"],
                    "amount": tx["amount"],
                    "transaction_date": tx["transaction_date"],
                    "payment_method": tx["payment_method"]
                }
                for tx in pos_transactions
            ]
        }

    def get_sync_status(self) -> Dict[str, Any]:
        """Get POS integration sync status"""
        
        # Get recent sync logs
        sync_logs = list(self.pos_sync_logs.find({
            "tenant_id": self.tenant_id
        }).sort("timestamp", -1).limit(10))
        
        # Count by status
        total_synced = self.pos_transactions.count_documents({
            "tenant_id": self.tenant_id,
            "status": "synced"
        })
        
        total_failed = self.pos_sync_logs.count_documents({
            "tenant_id": self.tenant_id,
            "status": "error"
        })
        
        # Get last sync time
        last_sync = self.pos_transactions.find_one(
            {"tenant_id": self.tenant_id},
            sort=[("synced_at", -1)]
        )
        
        return {
            "total_synced": total_synced,
            "total_failed": total_failed,
            "last_sync_time": last_sync.get("synced_at").isoformat() if last_sync else None,
            "recent_logs": [
                {
                    "id": str(log["_id"]),
                    "pos_transaction_id": log["pos_transaction_id"],
                    "status": log["status"],
                    "error": log.get("error"),
                    "timestamp": log["timestamp"].isoformat()
                }
                for log in sync_logs
            ]
        }

    def _get_payment_account(self, payment_method: str) -> Optional[Dict[str, Any]]:
        """Get payment account based on payment method"""
        
        method_mapping = {
            "cash": "cash",
            "card": "bank",
            "bank_transfer": "bank",
            "check": "bank",
            "mobile_money": "bank"
        }
        
        sub_type = method_mapping.get(payment_method.lower(), "bank")
        
        return self.accounts.find_one({
            "tenant_id": self.tenant_id,
            "account_type": "asset",
            "sub_type": sub_type
        })

    def _create_revenue_entry(
        self,
        transaction_date: str,
        amount: float,
        revenue_account_id: str,
        payment_account_id: str,
        reference: str,
        description: str
    ) -> Dict[str, Any]:
        """Create revenue journal entry"""
        
        # Get next entry number
        last_entry = self.journal_entries.find_one(
            {"tenant_id": self.tenant_id},
            sort=[("entry_number", -1)]
        )
        entry_number = (last_entry.get("entry_number", 0) if last_entry else 0) + 1
        
        journal_entry = {
            "tenant_id": self.tenant_id,
            "entry_number": entry_number,
            "date": transaction_date,
            "reference": reference,
            "description": description,
            "line_items": [
                {
                    "account_id": payment_account_id,
                    "debit": amount,
                    "credit": 0.0,
                    "description": "POS Payment"
                },
                {
                    "account_id": revenue_account_id,
                    "debit": 0.0,
                    "credit": amount,
                    "description": "POS Revenue"
                }
            ],
            "total_debit": amount,
            "total_credit": amount,
            "balanced": True,
            "created_by": "pos_integration",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = self.journal_entries.insert_one(journal_entry)
        journal_entry["id"] = str(result.inserted_id)
        del journal_entry["_id"]
        
        return journal_entry

    def _create_cogs_entry(
        self,
        transaction_date: str,
        amount: float,
        cogs_account_id: str,
        inventory_account_id: str,
        reference: str,
        description: str
    ) -> Dict[str, Any]:
        """Create COGS journal entry"""
        
        # Get next entry number
        last_entry = self.journal_entries.find_one(
            {"tenant_id": self.tenant_id},
            sort=[("entry_number", -1)]
        )
        entry_number = (last_entry.get("entry_number", 0) if last_entry else 0) + 1
        
        journal_entry = {
            "tenant_id": self.tenant_id,
            "entry_number": entry_number,
            "date": transaction_date,
            "reference": reference,
            "description": description,
            "line_items": [
                {
                    "account_id": cogs_account_id,
                    "debit": amount,
                    "credit": 0.0,
                    "description": "COGS"
                },
                {
                    "account_id": inventory_account_id,
                    "debit": 0.0,
                    "credit": amount,
                    "description": "Inventory Reduction"
                }
            ],
            "total_debit": amount,
            "total_credit": amount,
            "balanced": True,
            "created_by": "pos_integration",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = self.journal_entries.insert_one(journal_entry)
        journal_entry["id"] = str(result.inserted_id)
        del journal_entry["_id"]
        
        return journal_entry

    def _log_sync_error(self, pos_transaction_id: str, error: str) -> None:
        """Log POS sync error"""
        
        sync_log = {
            "tenant_id": self.tenant_id,
            "pos_transaction_id": pos_transaction_id,
            "status": "error",
            "error": error,
            "timestamp": datetime.utcnow(),
            "created_at": datetime.utcnow()
        }
        
        self.pos_sync_logs.insert_one(sync_log)

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
