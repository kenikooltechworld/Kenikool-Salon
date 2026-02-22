"""
Enhanced Journal Entry service
"""
from bson import ObjectId
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging
from io import BytesIO
import json

from app.database import Database
from app.api.exceptions import NotFoundException, BadRequestException

logger = logging.getLogger(__name__)


class JournalEntryService:
    """Service for enhanced journal entry management"""
    
    @staticmethod
    def get_journal_entry(tenant_id: str, entry_id: str) -> Dict:
        """
        Get a single journal entry by ID
        
        Returns:
            Dict with journal entry data
        """
        db = Database.get_db()
        
        entry = db.journal_entries.find_one({
            "_id": ObjectId(entry_id),
            "tenant_id": tenant_id
        })
        
        if not entry:
            raise NotFoundException("Journal entry not found")
        
        # Convert ObjectId to string
        entry["id"] = str(entry["_id"])
        del entry["_id"]
        
        # Get account details for line items
        for line_item in entry.get("line_items", []):
            account_id = line_item.get("account_id")
            if account_id:
                try:
                    account = db.accounts.find_one({"_id": ObjectId(account_id)})
                    if account:
                        line_item["account_code"] = account.get("code")
                        line_item["account_name"] = account.get("name")
                except:
                    pass
        
        return entry
    
    @staticmethod
    def update_journal_entry(
        tenant_id: str,
        entry_id: str,
        date: Optional[str] = None,
        description: Optional[str] = None,
        line_items: Optional[List[Dict]] = None,
        reference: Optional[str] = None,
        updated_by: str = "system"
    ) -> Dict:
        """
        Update a journal entry (only if not in locked period)
        
        Returns:
            Dict with updated journal entry data
        """
        db = Database.get_db()
        
        # Get existing entry
        existing_entry = db.journal_entries.find_one({
            "_id": ObjectId(entry_id),
            "tenant_id": tenant_id
        })
        
        if not existing_entry:
            raise NotFoundException("Journal entry not found")
        
        # Check if period is locked (simplified check - in production, implement proper period locking)
        entry_date = datetime.strptime(existing_entry.get("date", ""), "%Y-%m-%d")
        current_date = datetime.utcnow()
        
        # Don't allow editing entries older than 30 days (simplified rule)
        if (current_date - entry_date).days > 30:
            raise BadRequestException("Cannot edit journal entries in locked periods")
        
        # Prepare update data
        update_data = {
            "updated_at": datetime.utcnow(),
            "updated_by": updated_by
        }
        
        if date is not None:
            update_data["date"] = date
        
        if description is not None:
            update_data["description"] = description
        
        if reference is not None:
            update_data["reference"] = reference
        
        if line_items is not None:
            # Validate line items balance
            total_debit = sum(item.get("debit", 0) for item in line_items)
            total_credit = sum(item.get("credit", 0) for item in line_items)
            
            if abs(total_debit - total_credit) > 0.01:  # Allow for small rounding differences
                raise BadRequestException("Journal entry must be balanced (debits must equal credits)")
            
            # Validate accounts exist
            for item in line_items:
                account_id = item.get("account_id")
                if account_id:
                    account = db.accounts.find_one({
                        "_id": ObjectId(account_id),
                        "tenant_id": tenant_id
                    })
                    if not account:
                        raise BadRequestException(f"Account {account_id} not found")
            
            update_data["line_items"] = line_items
            update_data["total_debit"] = total_debit
            update_data["total_credit"] = total_credit
            update_data["balanced"] = True
        
        # Update the entry
        result = db.journal_entries.update_one(
            {"_id": ObjectId(entry_id)},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise BadRequestException("Failed to update journal entry")
        
        # Update account balances if line items changed
        if line_items is not None:
            JournalEntryService._update_account_balances_for_edit(
                db, tenant_id, existing_entry.get("line_items", []), line_items
            )
        
        # Return updated entry
        return JournalEntryService.get_journal_entry(tenant_id, entry_id)
    
    @staticmethod
    def reverse_journal_entry(
        tenant_id: str,
        entry_id: str,
        reversal_date: str,
        reversal_reason: str,
        created_by: str = "system"
    ) -> Dict:
        """
        Create a reversal entry for an existing journal entry
        
        Returns:
            Dict with reversal entry data
        """
        db = Database.get_db()
        
        # Get original entry
        original_entry = db.journal_entries.find_one({
            "_id": ObjectId(entry_id),
            "tenant_id": tenant_id
        })
        
        if not original_entry:
            raise NotFoundException("Original journal entry not found")
        
        # Check if already reversed
        if original_entry.get("reversed"):
            raise BadRequestException("Journal entry has already been reversed")
        
        # Generate new entry number
        last_entry = db.journal_entries.find_one(
            {"tenant_id": tenant_id},
            sort=[("entry_number", -1)]
        )
        entry_number = (last_entry.get("entry_number", 0) + 1) if last_entry else 1
        
        # Create reversal line items (swap debits and credits)
        reversal_line_items = []
        for item in original_entry.get("line_items", []):
            reversal_item = {
                "account_id": item.get("account_id"),
                "debit": item.get("credit", 0),  # Swap credit to debit
                "credit": item.get("debit", 0),  # Swap debit to credit
                "description": f"Reversal: {item.get('description', '')}"
            }
            reversal_line_items.append(reversal_item)
        
        # Create reversal entry
        reversal_entry = {
            "tenant_id": tenant_id,
            "entry_number": entry_number,
            "date": reversal_date,
            "reference": f"REV-{original_entry.get('entry_number', entry_id)}",
            "description": f"Reversal of entry #{original_entry.get('entry_number', entry_id)}: {reversal_reason}",
            "line_items": reversal_line_items,
            "total_debit": original_entry.get("total_credit", 0),
            "total_credit": original_entry.get("total_debit", 0),
            "balanced": True,
            "is_reversal": True,
            "original_entry_id": str(original_entry["_id"]),
            "reversal_reason": reversal_reason,
            "created_by": created_by,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert reversal entry
        result = db.journal_entries.insert_one(reversal_entry)
        reversal_id = str(result.inserted_id)
        
        # Mark original entry as reversed
        db.journal_entries.update_one(
            {"_id": ObjectId(entry_id)},
            {
                "$set": {
                    "reversed": True,
                    "reversal_entry_id": reversal_id,
                    "reversed_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Update account balances
        from app.services.accounting_service import accounting_service
        accounting_service._update_account_balances(db, tenant_id, reversal_line_items)
        
        return JournalEntryService.get_journal_entry(tenant_id, reversal_id)
    
    @staticmethod
    def add_attachment(
        tenant_id: str,
        entry_id: str,
        attachment_url: str,
        attachment_name: str,
        attachment_type: str = "document"
    ) -> Dict:
        """
        Add an attachment to a journal entry
        
        Returns:
            Dict with updated journal entry data
        """
        db = Database.get_db()
        
        # Verify entry exists
        entry = db.journal_entries.find_one({
            "_id": ObjectId(entry_id),
            "tenant_id": tenant_id
        })
        
        if not entry:
            raise NotFoundException("Journal entry not found")
        
        # Create attachment object
        attachment = {
            "id": str(ObjectId()),
            "name": attachment_name,
            "url": attachment_url,
            "type": attachment_type,
            "uploaded_at": datetime.utcnow().isoformat()
        }
        
        # Add attachment to entry
        result = db.journal_entries.update_one(
            {"_id": ObjectId(entry_id)},
            {
                "$push": {"attachments": attachment},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        if result.modified_count == 0:
            raise BadRequestException("Failed to add attachment")
        
        return JournalEntryService.get_journal_entry(tenant_id, entry_id)
    
    @staticmethod
    def remove_attachment(
        tenant_id: str,
        entry_id: str,
        attachment_id: str
    ) -> Dict:
        """
        Remove an attachment from a journal entry
        
        Returns:
            Dict with updated journal entry data
        """
        db = Database.get_db()
        
        # Remove attachment from entry
        result = db.journal_entries.update_one(
            {
                "_id": ObjectId(entry_id),
                "tenant_id": tenant_id
            },
            {
                "$pull": {"attachments": {"id": attachment_id}},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        if result.modified_count == 0:
            raise BadRequestException("Failed to remove attachment or attachment not found")
        
        return JournalEntryService.get_journal_entry(tenant_id, entry_id)
    
    @staticmethod
    def create_template(
        tenant_id: str,
        template_name: str,
        template_description: str,
        line_items: List[Dict],
        created_by: str = "system"
    ) -> Dict:
        """
        Create a journal entry template
        
        Returns:
            Dict with template data
        """
        db = Database.get_db()
        
        # Validate line items (accounts must exist)
        for item in line_items:
            account_id = item.get("account_id")
            if account_id:
                account = db.accounts.find_one({
                    "_id": ObjectId(account_id),
                    "tenant_id": tenant_id
                })
                if not account:
                    raise BadRequestException(f"Account {account_id} not found")
        
        # Create template
        template = {
            "tenant_id": tenant_id,
            "name": template_name,
            "description": template_description,
            "line_items": line_items,
            "created_by": created_by,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.journal_entry_templates.insert_one(template)
        
        # Return template with string ID
        template["id"] = str(result.inserted_id)
        del template["_id"]
        
        return template
    
    @staticmethod
    def get_templates(tenant_id: str) -> List[Dict]:
        """
        Get all journal entry templates for tenant
        
        Returns:
            List of template dictionaries
        """
        db = Database.get_db()
        
        templates = list(db.journal_entry_templates.find(
            {"tenant_id": tenant_id}
        ).sort("name", 1))
        
        # Convert ObjectId to string
        for template in templates:
            template["id"] = str(template["_id"])
            del template["_id"]
            
            # Get account details for line items
            for line_item in template.get("line_items", []):
                account_id = line_item.get("account_id")
                if account_id:
                    try:
                        account = db.accounts.find_one({"_id": ObjectId(account_id)})
                        if account:
                            line_item["account_code"] = account.get("code")
                            line_item["account_name"] = account.get("name")
                    except:
                        pass
        
        return templates
    
    @staticmethod
    def delete_template(tenant_id: str, template_id: str) -> Dict:
        """
        Delete a journal entry template
        
        Returns:
            Dict with success message
        """
        db = Database.get_db()
        
        result = db.journal_entry_templates.delete_one({
            "_id": ObjectId(template_id),
            "tenant_id": tenant_id
        })
        
        if result.deleted_count == 0:
            raise NotFoundException("Template not found")
        
        return {"message": "Template deleted successfully"}
    
    @staticmethod
    def create_from_template(
        tenant_id: str,
        template_id: str,
        date: str,
        description: Optional[str] = None,
        reference: Optional[str] = None,
        amount_overrides: Optional[Dict[str, float]] = None,
        created_by: str = "system"
    ) -> Dict:
        """
        Create a journal entry from a template
        
        Returns:
            Dict with created journal entry data
        """
        db = Database.get_db()
        
        # Get template
        template = db.journal_entry_templates.find_one({
            "_id": ObjectId(template_id),
            "tenant_id": tenant_id
        })
        
        if not template:
            raise NotFoundException("Template not found")
        
        # Prepare line items from template
        line_items = []
        for item in template.get("line_items", []):
            new_item = {
                "account_id": item.get("account_id"),
                "debit": item.get("debit", 0),
                "credit": item.get("credit", 0),
                "description": item.get("description", "")
            }
            
            # Apply amount overrides if provided
            if amount_overrides:
                account_id = item.get("account_id")
                if account_id in amount_overrides:
                    override_amount = amount_overrides[account_id]
                    if item.get("debit", 0) > 0:
                        new_item["debit"] = override_amount
                    elif item.get("credit", 0) > 0:
                        new_item["credit"] = override_amount
            
            line_items.append(new_item)
        
        # Use template description if none provided
        if not description:
            description = template.get("description", "")
        
        # Create journal entry using existing service
        from app.services.accounting_service import accounting_service
        
        return accounting_service.create_journal_entry(
            tenant_id=tenant_id,
            date=date,
            description=description,
            line_items=line_items,
            reference=reference,
            created_by=created_by
        )
    
    @staticmethod
    def submit_for_approval(
        tenant_id: str,
        entry_id: str,
        submitted_by: str = "system"
    ) -> Dict:
        """
        Submit a journal entry for approval
        
        Returns:
            Dict with updated journal entry data
        """
        db = Database.get_db()
        
        # Update entry status
        result = db.journal_entries.update_one(
            {
                "_id": ObjectId(entry_id),
                "tenant_id": tenant_id
            },
            {
                "$set": {
                    "approval_status": "pending",
                    "submitted_for_approval_at": datetime.utcnow(),
                    "submitted_by": submitted_by,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            raise NotFoundException("Journal entry not found")
        
        return JournalEntryService.get_journal_entry(tenant_id, entry_id)
    
    @staticmethod
    def approve_entry(
        tenant_id: str,
        entry_id: str,
        approved_by: str = "system",
        approval_notes: Optional[str] = None
    ) -> Dict:
        """
        Approve a journal entry
        
        Returns:
            Dict with updated journal entry data
        """
        db = Database.get_db()
        
        # Get entry to check current status
        entry = db.journal_entries.find_one({
            "_id": ObjectId(entry_id),
            "tenant_id": tenant_id
        })
        
        if not entry:
            raise NotFoundException("Journal entry not found")
        
        if entry.get("approval_status") != "pending":
            raise BadRequestException("Entry is not pending approval")
        
        # Update entry status
        update_data = {
            "approval_status": "approved",
            "approved_at": datetime.utcnow(),
            "approved_by": approved_by,
            "updated_at": datetime.utcnow()
        }
        
        if approval_notes:
            update_data["approval_notes"] = approval_notes
        
        result = db.journal_entries.update_one(
            {"_id": ObjectId(entry_id)},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise BadRequestException("Failed to approve journal entry")
        
        return JournalEntryService.get_journal_entry(tenant_id, entry_id)
    
    @staticmethod
    def reject_entry(
        tenant_id: str,
        entry_id: str,
        rejected_by: str = "system",
        rejection_reason: Optional[str] = None
    ) -> Dict:
        """
        Reject a journal entry
        
        Returns:
            Dict with updated journal entry data
        """
        db = Database.get_db()
        
        # Get entry to check current status
        entry = db.journal_entries.find_one({
            "_id": ObjectId(entry_id),
            "tenant_id": tenant_id
        })
        
        if not entry:
            raise NotFoundException("Journal entry not found")
        
        if entry.get("approval_status") != "pending":
            raise BadRequestException("Entry is not pending approval")
        
        # Update entry status
        update_data = {
            "approval_status": "rejected",
            "rejected_at": datetime.utcnow(),
            "rejected_by": rejected_by,
            "updated_at": datetime.utcnow()
        }
        
        if rejection_reason:
            update_data["rejection_reason"] = rejection_reason
        
        result = db.journal_entries.update_one(
            {"_id": ObjectId(entry_id)},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise BadRequestException("Failed to reject journal entry")
        
        return JournalEntryService.get_journal_entry(tenant_id, entry_id)
    
    @staticmethod
    def get_entries_for_approval(tenant_id: str) -> List[Dict]:
        """
        Get all journal entries pending approval
        
        Returns:
            List of journal entries pending approval
        """
        db = Database.get_db()
        
        entries = list(db.journal_entries.find({
            "tenant_id": tenant_id,
            "approval_status": "pending"
        }).sort("submitted_for_approval_at", 1))
        
        # Convert ObjectId to string and add account details
        for entry in entries:
            entry["id"] = str(entry["_id"])
            del entry["_id"]
            
            # Get account details for line items
            for line_item in entry.get("line_items", []):
                account_id = line_item.get("account_id")
                if account_id:
                    try:
                        account = db.accounts.find_one({"_id": ObjectId(account_id)})
                        if account:
                            line_item["account_code"] = account.get("code")
                            line_item["account_name"] = account.get("name")
                    except:
                        pass
        
        return entries
    
    @staticmethod
    def _update_account_balances_for_edit(
        db, 
        tenant_id: str, 
        old_line_items: List[Dict], 
        new_line_items: List[Dict]
    ):
        """
        Update account balances when editing a journal entry
        """
        # Reverse the old line items
        for item in old_line_items:
            account_id = item.get("account_id")
            if account_id:
                try:
                    account = db.accounts.find_one({
                        "_id": ObjectId(account_id),
                        "tenant_id": tenant_id
                    })
                    
                    if account:
                        # Reverse the previous entry
                        debit_adjustment = -(item.get("debit", 0))
                        credit_adjustment = -(item.get("credit", 0))
                        
                        if account["account_type"] in ["asset", "expense"]:
                            balance_change = debit_adjustment - credit_adjustment
                        else:  # liability, equity, revenue
                            balance_change = credit_adjustment - debit_adjustment
                        
                        new_balance = account.get("balance", 0) + balance_change
                        
                        db.accounts.update_one(
                            {"_id": ObjectId(account_id)},
                            {
                                "$set": {
                                    "balance": new_balance,
                                    "updated_at": datetime.utcnow()
                                }
                            }
                        )
                except Exception as e:
                    logger.error(f"Error reversing balance for account {account_id}: {str(e)}")
        
        # Apply the new line items
        from app.services.accounting_service import accounting_service
        accounting_service._update_account_balances(db, tenant_id, new_line_items)


# Singleton instance
journal_entry_service = JournalEntryService()