"""
Payroll Integration Service

Handles integration with payroll system including:
- Payroll transaction syncing
- Wage expense entries
- Tax liability tracking
- Payroll payments
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pymongo.database import Database
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class PayrollIntegrationService:
    def __init__(self, db: Database, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.payroll_records = db.payroll_records
        self.payroll_sync_logs = db.payroll_sync_logs
        self.journal_entries = db.journal_entries
        self.accounts = db.accounts
        self.audit_logs = db.audit_logs

    def sync_payroll(
        self,
        payroll_period: str,
        payroll_date: str,
        employees: List[Dict[str, Any]],
        created_by: str = "system"
    ) -> Dict[str, Any]:
        """Sync payroll to accounting"""
        
        try:
            # Check if payroll already synced
            existing = self.payroll_records.find_one({
                "tenant_id": self.tenant_id,
                "payroll_period": payroll_period
            })
            
            if existing and existing.get("synced"):
                return {
                    "status": "already_synced",
                    "payroll_period": payroll_period,
                    "message": "Payroll already synced"
                }
            
            # Get wage expense account
            wage_account = self.accounts.find_one({
                "tenant_id": self.tenant_id,
                "account_type": "expense",
                "sub_type": "wages"
            })
            
            if not wage_account:
                raise ValueError("Wage expense account not found")
            
            # Calculate totals
            total_gross = sum(emp.get("gross_pay", 0) for emp in employees)
            total_net = sum(emp.get("net_pay", 0) for emp in employees)
            total_taxes = total_gross - total_net
            
            # Create wage expense entry
            wage_entry = self._create_wage_entry(
                payroll_date=payroll_date,
                amount=total_gross,
                wage_account_id=str(wage_account["_id"]),
                reference=f"PAYROLL-{payroll_period}",
                description=f"Payroll for period: {payroll_period}"
            )
            
            # Create tax liability entry
            tax_entry = self._create_tax_entry(
                payroll_date=payroll_date,
                amount=total_taxes,
                reference=f"PAYROLL-TAX-{payroll_period}",
                description=f"Payroll taxes for period: {payroll_period}"
            )
            
            # Record payroll
            payroll_record = {
                "tenant_id": self.tenant_id,
                "payroll_period": payroll_period,
                "payroll_date": payroll_date,
                "employees": employees,
                "total_gross": total_gross,
                "total_net": total_net,
                "total_taxes": total_taxes,
                "wage_journal_entry_id": wage_entry["id"],
                "tax_journal_entry_id": tax_entry["id"],
                "synced": True,
                "created_by": created_by,
                "created_at": datetime.utcnow(),
                "synced_at": datetime.utcnow()
            }
            
            if existing:
                self.payroll_records.update_one(
                    {"_id": existing["_id"]},
                    {"$set": payroll_record}
                )
                payroll_record["id"] = str(existing["_id"])
            else:
                result = self.payroll_records.insert_one(payroll_record)
                payroll_record["id"] = str(result.inserted_id)
            
            del payroll_record["_id"] if "_id" in payroll_record else None
            
            return {
                "status": "success",
                "payroll_period": payroll_period,
                "total_gross": total_gross,
                "total_net": total_net,
                "total_taxes": total_taxes,
                "wage_entry_id": wage_entry["id"],
                "tax_entry_id": tax_entry["id"]
            }
        
        except Exception as e:
            logger.error(f"Error syncing payroll: {str(e)}")
            self._log_sync_error(payroll_period, str(e))
            raise

    def post_payroll_payment(
        self,
        payroll_period: str,
        payment_method: str,
        amount: float,
        created_by: str = "system"
    ) -> Dict[str, Any]:
        """Post payroll payment to bank account"""
        
        try:
            # Get payroll record
            payroll = self.payroll_records.find_one({
                "tenant_id": self.tenant_id,
                "payroll_period": payroll_period
            })
            
            if not payroll:
                raise ValueError(f"Payroll not found: {payroll_period}")
            
            # Get payment account
            payment_account = self._get_payment_account(payment_method)
            if not payment_account:
                raise ValueError(f"Payment account not found for method: {payment_method}")
            
            # Create payment entry
            payment_entry = self._create_payment_entry(
                payroll_date=payroll["payroll_date"],
                amount=amount,
                payment_account_id=str(payment_account["_id"]),
                reference=f"PAYROLL-PAY-{payroll_period}",
                description=f"Payroll payment for period: {payroll_period}"
            )
            
            # Update payroll record
            self.payroll_records.update_one(
                {"_id": payroll["_id"]},
                {
                    "$set": {
                        "payment_posted": True,
                        "payment_account_id": str(payment_account["_id"]),
                        "payment_journal_entry_id": payment_entry["id"],
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return {
                "status": "success",
                "payroll_period": payroll_period,
                "payment_account": payment_account["name"],
                "amount": amount,
                "journal_entry_id": payment_entry["id"]
            }
        
        except Exception as e:
            logger.error(f"Error posting payroll payment: {str(e)}")
            raise

    def get_payroll_records(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get payroll records with optional filtering"""
        
        query = {"tenant_id": self.tenant_id}
        
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query["$gte"] = start_date
            if end_date:
                date_query["$lte"] = end_date
            if date_query:
                query["payroll_date"] = date_query
        
        records = list(
            self.payroll_records.find(query)
            .sort("payroll_date", -1)
            .skip(offset)
            .limit(limit)
        )
        
        for record in records:
            record["id"] = str(record["_id"])
            del record["_id"]
        
        return records

    def get_payroll_expense_report(
        self,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """Get payroll expense report"""
        
        payroll_records = list(self.payroll_records.find({
            "tenant_id": self.tenant_id,
            "payroll_date": {
                "$gte": start_date,
                "$lte": end_date
            },
            "synced": True
        }))
        
        total_gross = sum(record.get("total_gross", 0) for record in payroll_records)
        total_net = sum(record.get("total_net", 0) for record in payroll_records)
        total_taxes = sum(record.get("total_taxes", 0) for record in payroll_records)
        
        # Group by employee
        employee_summary = {}
        for record in payroll_records:
            for emp in record.get("employees", []):
                emp_id = emp.get("employee_id")
                if emp_id not in employee_summary:
                    employee_summary[emp_id] = {
                        "employee_id": emp_id,
                        "employee_name": emp.get("employee_name"),
                        "total_gross": 0,
                        "total_net": 0,
                        "total_taxes": 0,
                        "pay_periods": 0
                    }
                employee_summary[emp_id]["total_gross"] += emp.get("gross_pay", 0)
                employee_summary[emp_id]["total_net"] += emp.get("net_pay", 0)
                employee_summary[emp_id]["total_taxes"] += emp.get("gross_pay", 0) - emp.get("net_pay", 0)
                employee_summary[emp_id]["pay_periods"] += 1
        
        return {
            "period_start": start_date,
            "period_end": end_date,
            "total_gross": total_gross,
            "total_net": total_net,
            "total_taxes": total_taxes,
            "payroll_count": len(payroll_records),
            "employee_count": len(employee_summary),
            "employee_summary": list(employee_summary.values())
        }

    def get_tax_withholding_report(
        self,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """Get tax withholding report"""
        
        payroll_records = list(self.payroll_records.find({
            "tenant_id": self.tenant_id,
            "payroll_date": {
                "$gte": start_date,
                "$lte": end_date
            },
            "synced": True
        }))
        
        # Aggregate tax data
        tax_summary = {
            "federal": 0,
            "state": 0,
            "local": 0,
            "social_security": 0,
            "medicare": 0,
            "other": 0
        }
        
        for record in payroll_records:
            for emp in record.get("employees", []):
                taxes = emp.get("taxes", {})
                tax_summary["federal"] += taxes.get("federal", 0)
                tax_summary["state"] += taxes.get("state", 0)
                tax_summary["local"] += taxes.get("local", 0)
                tax_summary["social_security"] += taxes.get("social_security", 0)
                tax_summary["medicare"] += taxes.get("medicare", 0)
                tax_summary["other"] += taxes.get("other", 0)
        
        total_taxes = sum(tax_summary.values())
        
        return {
            "period_start": start_date,
            "period_end": end_date,
            "total_taxes": total_taxes,
            "tax_breakdown": tax_summary,
            "payroll_count": len(payroll_records)
        }

    def _create_wage_entry(
        self,
        payroll_date: str,
        amount: float,
        wage_account_id: str,
        reference: str,
        description: str
    ) -> Dict[str, Any]:
        """Create wage expense journal entry"""
        
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
            "date": payroll_date,
            "reference": reference,
            "description": description,
            "line_items": [
                {
                    "account_id": wage_account_id,
                    "debit": amount,
                    "credit": 0.0,
                    "description": "Wage Expense"
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
            "created_by": "payroll_integration",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = self.journal_entries.insert_one(journal_entry)
        journal_entry["id"] = str(result.inserted_id)
        del journal_entry["_id"]
        
        return journal_entry

    def _create_tax_entry(
        self,
        payroll_date: str,
        amount: float,
        reference: str,
        description: str
    ) -> Dict[str, Any]:
        """Create tax liability journal entry"""
        
        # Get wage expense account
        wage_account = self.accounts.find_one({
            "tenant_id": self.tenant_id,
            "account_type": "expense",
            "sub_type": "wages"
        })
        
        # Get tax liability account
        tax_liability = self.accounts.find_one({
            "tenant_id": self.tenant_id,
            "account_type": "liability",
            "sub_type": "payroll_taxes"
        })
        
        if not wage_account or not tax_liability:
            raise ValueError("Required accounts not found")
        
        # Get next entry number
        last_entry = self.journal_entries.find_one(
            {"tenant_id": self.tenant_id},
            sort=[("entry_number", -1)]
        )
        entry_number = (last_entry.get("entry_number", 0) if last_entry else 0) + 1
        
        journal_entry = {
            "tenant_id": self.tenant_id,
            "entry_number": entry_number,
            "date": payroll_date,
            "reference": reference,
            "description": description,
            "line_items": [
                {
                    "account_id": str(wage_account["_id"]),
                    "debit": amount,
                    "credit": 0.0,
                    "description": "Payroll Tax Expense"
                },
                {
                    "account_id": str(tax_liability["_id"]),
                    "debit": 0.0,
                    "credit": amount,
                    "description": "Tax Liability"
                }
            ],
            "total_debit": amount,
            "total_credit": amount,
            "balanced": True,
            "created_by": "payroll_integration",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = self.journal_entries.insert_one(journal_entry)
        journal_entry["id"] = str(result.inserted_id)
        del journal_entry["_id"]
        
        return journal_entry

    def _create_payment_entry(
        self,
        payroll_date: str,
        amount: float,
        payment_account_id: str,
        reference: str,
        description: str
    ) -> Dict[str, Any]:
        """Create payroll payment journal entry"""
        
        # Get payroll liability account
        payroll_liability = self.accounts.find_one({
            "tenant_id": self.tenant_id,
            "account_type": "liability",
            "sub_type": "payroll_payable"
        })
        
        if not payroll_liability:
            raise ValueError("Payroll payable account not found")
        
        # Get next entry number
        last_entry = self.journal_entries.find_one(
            {"tenant_id": self.tenant_id},
            sort=[("entry_number", -1)]
        )
        entry_number = (last_entry.get("entry_number", 0) if last_entry else 0) + 1
        
        journal_entry = {
            "tenant_id": self.tenant_id,
            "entry_number": entry_number,
            "date": payroll_date,
            "reference": reference,
            "description": description,
            "line_items": [
                {
                    "account_id": str(payroll_liability["_id"]),
                    "debit": amount,
                    "credit": 0.0,
                    "description": "Payroll Liability"
                },
                {
                    "account_id": payment_account_id,
                    "debit": 0.0,
                    "credit": amount,
                    "description": "Payment"
                }
            ],
            "total_debit": amount,
            "total_credit": amount,
            "balanced": True,
            "created_by": "payroll_integration",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = self.journal_entries.insert_one(journal_entry)
        journal_entry["id"] = str(result.inserted_id)
        del journal_entry["_id"]
        
        return journal_entry

    def _get_payment_account(self, payment_method: str) -> Optional[Dict[str, Any]]:
        """Get payment account based on payment method"""
        
        method_mapping = {
            "cash": "cash",
            "bank": "bank",
            "check": "bank"
        }
        
        sub_type = method_mapping.get(payment_method.lower(), "bank")
        
        return self.accounts.find_one({
            "tenant_id": self.tenant_id,
            "account_type": "asset",
            "sub_type": sub_type
        })

    def _log_sync_error(self, payroll_period: str, error: str) -> None:
        """Log payroll sync error"""
        
        sync_log = {
            "tenant_id": self.tenant_id,
            "payroll_period": payroll_period,
            "status": "error",
            "error": error,
            "timestamp": datetime.utcnow(),
            "created_at": datetime.utcnow()
        }
        
        self.payroll_sync_logs.insert_one(sync_log)

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
