"""
Enhanced Chart of Accounts service
"""
from bson import ObjectId
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging
import csv
from io import StringIO, BytesIO

from app.database import Database
from app.api.exceptions import NotFoundException, BadRequestException

logger = logging.getLogger(__name__)


class ChartOfAccountsService:
    """Service for enhanced chart of accounts management"""
    
    @staticmethod
    def get_account_hierarchy(tenant_id: str, parent_id: Optional[str] = None) -> List[Dict]:
        """
        Get accounts in hierarchical structure
        
        Returns:
            List of accounts with nested children
        """
        db = Database.get_db()
        
        # Get accounts at this level
        query = {
            "tenant_id": tenant_id,
            "parent_account_id": parent_id
        }
        
        accounts = list(db.accounts.find(query).sort("code", 1))
        
        # Convert ObjectId to string and add children
        result = []
        for account in accounts:
            account["id"] = str(account["_id"])
            del account["_id"]
            
            # Get children recursively
            children = ChartOfAccountsService.get_account_hierarchy(
                tenant_id, str(account["id"])
            )
            account["children"] = children
            account["has_children"] = len(children) > 0
            
            result.append(account)
        
        return result
    
    @staticmethod
    def search_accounts(
        tenant_id: str,
        search_term: Optional[str] = None,
        account_type: Optional[str] = None,
        sub_type: Optional[str] = None,
        active_only: bool = True
    ) -> List[Dict]:
        """
        Search and filter accounts
        
        Returns:
            List of matching accounts
        """
        db = Database.get_db()
        
        # Build query
        query = {"tenant_id": tenant_id}
        
        if active_only:
            query["active"] = True
        
        if account_type:
            query["account_type"] = account_type
        
        if sub_type:
            query["sub_type"] = sub_type
        
        # Add text search
        if search_term:
            query["$or"] = [
                {"code": {"$regex": search_term, "$options": "i"}},
                {"name": {"$regex": search_term, "$options": "i"}},
                {"description": {"$regex": search_term, "$options": "i"}}
            ]
        
        accounts = list(db.accounts.find(query).sort("code", 1))
        
        # Convert ObjectId to string
        for account in accounts:
            account["id"] = str(account["_id"])
            del account["_id"]
        
        return accounts
    
    @staticmethod
    def export_accounts_csv(tenant_id: str) -> BytesIO:
        """
        Export chart of accounts to CSV
        
        Returns:
            BytesIO buffer containing CSV data
        """
        db = Database.get_db()
        
        # Get all accounts
        accounts = list(db.accounts.find({"tenant_id": tenant_id}).sort("code", 1))
        
        # Create CSV content
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Code',
            'Name',
            'Account Type',
            'Sub Type',
            'Description',
            'Parent Account Code',
            'Active',
            'Balance',
            'Created At'
        ])
        
        # Write data
        for account in accounts:
            parent_code = ""
            if account.get("parent_account_id"):
                parent_account = db.accounts.find_one({
                    "_id": ObjectId(account["parent_account_id"])
                })
                if parent_account:
                    parent_code = parent_account.get("code", "")
            
            writer.writerow([
                account.get("code", ""),
                account.get("name", ""),
                account.get("account_type", ""),
                account.get("sub_type", ""),
                account.get("description", ""),
                parent_code,
                account.get("active", True),
                account.get("balance", 0.0),
                account.get("created_at", "").strftime("%Y-%m-%d %H:%M:%S") if account.get("created_at") else ""
            ])
        
        # Convert to BytesIO
        buffer = BytesIO()
        buffer.write(output.getvalue().encode('utf-8'))
        buffer.seek(0)
        
        return buffer
    
    @staticmethod
    def import_accounts_csv(tenant_id: str, csv_content: str) -> Dict:
        """
        Import chart of accounts from CSV
        
        Returns:
            Dict with import results
        """
        db = Database.get_db()
        
        # Parse CSV
        csv_reader = csv.DictReader(StringIO(csv_content))
        
        results = {
            "total_rows": 0,
            "imported": 0,
            "updated": 0,
            "errors": [],
            "warnings": []
        }
        
        # Track parent account mappings for later resolution
        parent_mappings = {}
        
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 for header
            results["total_rows"] += 1
            
            try:
                # Validate required fields
                if not row.get("Code") or not row.get("Name"):
                    results["errors"].append({
                        "row": row_num,
                        "error": "Code and Name are required"
                    })
                    continue
                
                if not row.get("Account Type"):
                    results["errors"].append({
                        "row": row_num,
                        "error": "Account Type is required"
                    })
                    continue
                
                # Check if account exists
                existing_account = db.accounts.find_one({
                    "tenant_id": tenant_id,
                    "code": row["Code"]
                })
                
                # Prepare account data
                account_data = {
                    "tenant_id": tenant_id,
                    "code": row["Code"],
                    "name": row["Name"],
                    "account_type": row["Account Type"].lower(),
                    "sub_type": row.get("Sub Type", "").lower() if row.get("Sub Type") else None,
                    "description": row.get("Description"),
                    "active": row.get("Active", "True").lower() in ["true", "1", "yes"],
                    "balance": float(row.get("Balance", 0)) if row.get("Balance") else 0.0,
                    "updated_at": datetime.utcnow()
                }
                
                # Handle parent account
                if row.get("Parent Account Code"):
                    parent_mappings[row["Code"]] = row["Parent Account Code"]
                
                if existing_account:
                    # Update existing account
                    db.accounts.update_one(
                        {"_id": existing_account["_id"]},
                        {"$set": account_data}
                    )
                    results["updated"] += 1
                else:
                    # Create new account
                    account_data["created_at"] = datetime.utcnow()
                    db.accounts.insert_one(account_data)
                    results["imported"] += 1
                
            except Exception as e:
                results["errors"].append({
                    "row": row_num,
                    "error": str(e)
                })
        
        # Resolve parent account relationships
        for child_code, parent_code in parent_mappings.items():
            try:
                parent_account = db.accounts.find_one({
                    "tenant_id": tenant_id,
                    "code": parent_code
                })
                
                if parent_account:
                    db.accounts.update_one(
                        {"tenant_id": tenant_id, "code": child_code},
                        {"$set": {"parent_account_id": str(parent_account["_id"])}}
                    )
                else:
                    results["warnings"].append({
                        "account": child_code,
                        "warning": f"Parent account '{parent_code}' not found"
                    })
            except Exception as e:
                results["warnings"].append({
                    "account": child_code,
                    "warning": f"Error setting parent: {str(e)}"
                })
        
        return results
    
    @staticmethod
    def validate_csv_import(csv_content: str) -> Dict:
        """
        Validate CSV import without actually importing
        
        Returns:
            Dict with validation results
        """
        csv_reader = csv.DictReader(StringIO(csv_content))
        
        results = {
            "valid": True,
            "total_rows": 0,
            "errors": [],
            "warnings": []
        }
        
        required_columns = ["Code", "Name", "Account Type"]
        
        # Check if required columns exist
        if not all(col in csv_reader.fieldnames for col in required_columns):
            missing_cols = [col for col in required_columns if col not in csv_reader.fieldnames]
            results["valid"] = False
            results["errors"].append({
                "row": 1,
                "error": f"Missing required columns: {', '.join(missing_cols)}"
            })
            return results
        
        # Validate each row
        codes_seen = set()
        
        for row_num, row in enumerate(csv_reader, start=2):
            results["total_rows"] += 1
            
            # Check for duplicate codes
            if row["Code"] in codes_seen:
                results["errors"].append({
                    "row": row_num,
                    "error": f"Duplicate account code: {row['Code']}"
                })
                results["valid"] = False
            else:
                codes_seen.add(row["Code"])
            
            # Validate account type
            valid_types = ["asset", "liability", "equity", "revenue", "expense"]
            if row["Account Type"].lower() not in valid_types:
                results["errors"].append({
                    "row": row_num,
                    "error": f"Invalid account type: {row['Account Type']}. Must be one of: {', '.join(valid_types)}"
                })
                results["valid"] = False
            
            # Validate balance is numeric
            if row.get("Balance") and row["Balance"]:
                try:
                    float(row["Balance"])
                except ValueError:
                    results["errors"].append({
                        "row": row_num,
                        "error": f"Invalid balance value: {row['Balance']}"
                    })
                    results["valid"] = False
        
        return results
    
    @staticmethod
    def merge_accounts(
        tenant_id: str,
        source_account_id: str,
        target_account_id: str,
        merge_transactions: bool = True
    ) -> Dict:
        """
        Merge one account into another
        
        Args:
            tenant_id: Tenant ID
            source_account_id: Account to be merged (will be deactivated)
            target_account_id: Account to merge into
            merge_transactions: Whether to transfer transactions
            
        Returns:
            Dict with merge results
        """
        db = Database.get_db()
        
        # Validate accounts exist
        source_account = db.accounts.find_one({
            "_id": ObjectId(source_account_id),
            "tenant_id": tenant_id
        })
        
        target_account = db.accounts.find_one({
            "_id": ObjectId(target_account_id),
            "tenant_id": tenant_id
        })
        
        if not source_account:
            raise NotFoundException("Source account not found")
        
        if not target_account:
            raise NotFoundException("Target account not found")
        
        # Validate accounts are same type
        if source_account["account_type"] != target_account["account_type"]:
            raise BadRequestException("Cannot merge accounts of different types")
        
        results = {
            "transactions_moved": 0,
            "invoices_updated": 0,
            "bills_updated": 0,
            "journal_entries_updated": 0
        }
        
        if merge_transactions:
            # Update journal entry line items
            journal_update_result = db.journal_entries.update_many(
                {
                    "tenant_id": tenant_id,
                    "line_items.account_id": source_account_id
                },
                {
                    "$set": {
                        "line_items.$.account_id": target_account_id,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            results["journal_entries_updated"] = journal_update_result.modified_count
            
            # Update invoice line items (if they reference accounts)
            invoice_update_result = db.invoices.update_many(
                {
                    "tenant_id": tenant_id,
                    "line_items.account_id": source_account_id
                },
                {
                    "$set": {
                        "line_items.$.account_id": target_account_id,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            results["invoices_updated"] = invoice_update_result.modified_count
            
            # Update bill line items (if they reference accounts)
            bill_update_result = db.bills.update_many(
                {
                    "tenant_id": tenant_id,
                    "line_items.account_id": source_account_id
                },
                {
                    "$set": {
                        "line_items.$.account_id": target_account_id,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            results["bills_updated"] = bill_update_result.modified_count
            
            # Calculate total transactions moved
            results["transactions_moved"] = (
                results["journal_entries_updated"] + 
                results["invoices_updated"] + 
                results["bills_updated"]
            )
        
        # Transfer balance to target account
        if source_account.get("balance", 0) != 0:
            new_target_balance = target_account.get("balance", 0) + source_account.get("balance", 0)
            db.accounts.update_one(
                {"_id": ObjectId(target_account_id)},
                {
                    "$set": {
                        "balance": new_target_balance,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
        
        # Deactivate source account
        db.accounts.update_one(
            {"_id": ObjectId(source_account_id)},
            {
                "$set": {
                    "active": False,
                    "balance": 0.0,
                    "merged_into": target_account_id,
                    "merged_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        results["source_account_deactivated"] = True
        results["target_account_balance_updated"] = True
        
        return results
    
    @staticmethod
    def get_account_usage_stats(tenant_id: str, account_id: str) -> Dict:
        """
        Get usage statistics for an account
        
        Returns:
            Dict with usage statistics
        """
        db = Database.get_db()
        
        # Validate account exists
        account = db.accounts.find_one({
            "_id": ObjectId(account_id),
            "tenant_id": tenant_id
        })
        
        if not account:
            raise NotFoundException("Account not found")
        
        stats = {
            "account_id": account_id,
            "account_code": account.get("code"),
            "account_name": account.get("name"),
            "current_balance": account.get("balance", 0.0),
            "journal_entries": 0,
            "invoices": 0,
            "bills": 0,
            "total_transactions": 0,
            "first_transaction_date": None,
            "last_transaction_date": None,
            "can_be_deleted": True,
            "deletion_blockers": []
        }
        
        # Count journal entries
        journal_count = db.journal_entries.count_documents({
            "tenant_id": tenant_id,
            "line_items.account_id": account_id
        })
        stats["journal_entries"] = journal_count
        
        # Count invoices
        invoice_count = db.invoices.count_documents({
            "tenant_id": tenant_id,
            "line_items.account_id": account_id
        })
        stats["invoices"] = invoice_count
        
        # Count bills
        bill_count = db.bills.count_documents({
            "tenant_id": tenant_id,
            "line_items.account_id": account_id
        })
        stats["bills"] = bill_count
        
        stats["total_transactions"] = journal_count + invoice_count + bill_count
        
        # Get transaction date range
        if stats["total_transactions"] > 0:
            # Find earliest transaction
            earliest_journal = db.journal_entries.find_one(
                {
                    "tenant_id": tenant_id,
                    "line_items.account_id": account_id
                },
                sort=[("date", 1)]
            )
            
            if earliest_journal:
                stats["first_transaction_date"] = earliest_journal.get("date")
            
            # Find latest transaction
            latest_journal = db.journal_entries.find_one(
                {
                    "tenant_id": tenant_id,
                    "line_items.account_id": account_id
                },
                sort=[("date", -1)]
            )
            
            if latest_journal:
                stats["last_transaction_date"] = latest_journal.get("date")
        
        # Determine if account can be deleted
        if stats["total_transactions"] > 0:
            stats["can_be_deleted"] = False
            stats["deletion_blockers"].append("Account has transaction history")
        
        if account.get("balance", 0) != 0:
            stats["can_be_deleted"] = False
            stats["deletion_blockers"].append("Account has non-zero balance")
        
        # Check if account has children
        children_count = db.accounts.count_documents({
            "tenant_id": tenant_id,
            "parent_account_id": account_id
        })
        
        if children_count > 0:
            stats["can_be_deleted"] = False
            stats["deletion_blockers"].append("Account has child accounts")
        
        return stats


# Singleton instance
chart_of_accounts_service = ChartOfAccountsService()