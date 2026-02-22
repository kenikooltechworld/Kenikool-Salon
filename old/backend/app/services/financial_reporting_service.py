"""
Enhanced financial reporting service
"""
from bson import ObjectId
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from io import BytesIO
import json

from app.database import Database
from app.api.exceptions import NotFoundException, BadRequestException

logger = logging.getLogger(__name__)


class FinancialReportingService:
    """Service for enhanced financial reporting"""
    
    @staticmethod
    def get_date_range_from_preset(preset: str, reference_date: Optional[datetime] = None) -> Tuple[str, str]:
        """
        Convert date preset to actual date range
        
        Returns:
            Tuple of (start_date, end_date) as strings
        """
        if reference_date is None:
            reference_date = datetime.utcnow()
        
        if preset == "today":
            start_date = end_date = reference_date.strftime("%Y-%m-%d")
        elif preset == "yesterday":
            yesterday = reference_date - timedelta(days=1)
            start_date = end_date = yesterday.strftime("%Y-%m-%d")
        elif preset == "this_week":
            start_of_week = reference_date - timedelta(days=reference_date.weekday())
            start_date = start_of_week.strftime("%Y-%m-%d")
            end_date = reference_date.strftime("%Y-%m-%d")
        elif preset == "last_week":
            start_of_last_week = reference_date - timedelta(days=reference_date.weekday() + 7)
            end_of_last_week = start_of_last_week + timedelta(days=6)
            start_date = start_of_last_week.strftime("%Y-%m-%d")
            end_date = end_of_last_week.strftime("%Y-%m-%d")
        elif preset == "this_month":
            start_date = reference_date.replace(day=1).strftime("%Y-%m-%d")
            end_date = reference_date.strftime("%Y-%m-%d")
        elif preset == "last_month":
            first_of_this_month = reference_date.replace(day=1)
            last_month = first_of_this_month - timedelta(days=1)
            start_date = last_month.replace(day=1).strftime("%Y-%m-%d")
            end_date = last_month.strftime("%Y-%m-%d")
        elif preset == "this_quarter":
            quarter = (reference_date.month - 1) // 3 + 1
            start_date = reference_date.replace(month=(quarter - 1) * 3 + 1, day=1).strftime("%Y-%m-%d")
            end_date = reference_date.strftime("%Y-%m-%d")
        elif preset == "last_quarter":
            current_quarter = (reference_date.month - 1) // 3 + 1
            if current_quarter == 1:
                # Last quarter of previous year
                last_quarter_start = reference_date.replace(year=reference_date.year - 1, month=10, day=1)
                last_quarter_end = reference_date.replace(year=reference_date.year - 1, month=12, day=31)
            else:
                last_quarter_start = reference_date.replace(month=(current_quarter - 2) * 3 + 1, day=1)
                last_quarter_end = reference_date.replace(month=(current_quarter - 1) * 3, day=1) - timedelta(days=1)
            start_date = last_quarter_start.strftime("%Y-%m-%d")
            end_date = last_quarter_end.strftime("%Y-%m-%d")
        elif preset == "this_year":
            start_date = reference_date.replace(month=1, day=1).strftime("%Y-%m-%d")
            end_date = reference_date.strftime("%Y-%m-%d")
        elif preset == "last_year":
            start_date = reference_date.replace(year=reference_date.year - 1, month=1, day=1).strftime("%Y-%m-%d")
            end_date = reference_date.replace(year=reference_date.year - 1, month=12, day=31).strftime("%Y-%m-%d")
        elif preset == "ytd":
            start_date = reference_date.replace(month=1, day=1).strftime("%Y-%m-%d")
            end_date = reference_date.strftime("%Y-%m-%d")
        elif preset == "qtd":
            quarter = (reference_date.month - 1) // 3 + 1
            start_date = reference_date.replace(month=(quarter - 1) * 3 + 1, day=1).strftime("%Y-%m-%d")
            end_date = reference_date.strftime("%Y-%m-%d")
        else:
            raise BadRequestException(f"Invalid date preset: {preset}")
        
        return start_date, end_date
    
    @staticmethod
    def generate_cash_flow_statement(
        tenant_id: str,
        start_date: str,
        end_date: str,
        method: str = "indirect"
    ) -> Dict:
        """
        Generate cash flow statement
        
        Returns:
            Dict with cash flow statement data
        """
        db = Database.get_db()
        
        # Get all transactions in the period
        transactions_pipeline = [
            {
                "$match": {
                    "tenant_id": tenant_id,
                    "date": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$lookup": {
                    "from": "accounts",
                    "localField": "line_items.account_id",
                    "foreignField": "_id",
                    "as": "account_details"
                }
            }
        ]
        
        transactions = list(db.journal_entries.aggregate(transactions_pipeline))
        
        # Initialize cash flow categories
        cash_flows = {
            "operating": {
                "name": "Operating Activities",
                "items": [],
                "total": 0.0
            },
            "investing": {
                "name": "Investing Activities", 
                "items": [],
                "total": 0.0
            },
            "financing": {
                "name": "Financing Activities",
                "items": [],
                "total": 0.0
            }
        }
        
        # Get net income for indirect method
        net_income = 0.0
        if method == "indirect":
            # Calculate net income from revenue and expense accounts
            revenue_expense_pipeline = [
                {
                    "$match": {
                        "tenant_id": tenant_id,
                        "account_type": {"$in": ["revenue", "expense"]}
                    }
                },
                {
                    "$lookup": {
                        "from": "journal_entries",
                        "let": {"account_id": "$_id"},
                        "pipeline": [
                            {
                                "$match": {
                                    "tenant_id": tenant_id,
                                    "date": {"$gte": start_date, "$lte": end_date}
                                }
                            },
                            {"$unwind": "$line_items"},
                            {
                                "$match": {
                                    "$expr": {"$eq": ["$line_items.account_id", {"$toString": "$$account_id"}]}
                                }
                            }
                        ],
                        "as": "transactions"
                    }
                }
            ]
            
            accounts_with_transactions = list(db.accounts.aggregate(revenue_expense_pipeline))
            
            for account in accounts_with_transactions:
                account_balance = 0.0
                for transaction in account["transactions"]:
                    line_item = transaction["line_items"]
                    if account["account_type"] == "revenue":
                        account_balance += line_item.get("credit", 0) - line_item.get("debit", 0)
                    else:  # expense
                        account_balance += line_item.get("debit", 0) - line_item.get("credit", 0)
                
                if account["account_type"] == "revenue":
                    net_income += account_balance
                else:  # expense
                    net_income -= account_balance
            
            # Start with net income for operating activities
            cash_flows["operating"]["items"].append({
                "description": "Net Income",
                "amount": net_income
            })
            cash_flows["operating"]["total"] += net_income
        
        # Categorize cash flows based on account types and transaction patterns
        # This is a simplified categorization - in practice, you'd have more sophisticated rules
        
        # Get cash and cash equivalent accounts
        cash_accounts = list(db.accounts.find({
            "tenant_id": tenant_id,
            "account_type": "asset",
            "sub_type": {"$in": ["cash", "bank", "checking", "savings"]}
        }))
        
        cash_account_ids = [str(acc["_id"]) for acc in cash_accounts]
        
        # Analyze transactions for cash flow categorization
        for transaction in transactions:
            for line_item in transaction.get("line_items", []):
                account_id = line_item.get("account_id")
                
                if account_id in cash_account_ids:
                    # This is a cash transaction
                    amount = line_item.get("debit", 0) - line_item.get("credit", 0)
                    
                    # Categorize based on the other accounts in the transaction
                    other_accounts = [
                        item for item in transaction.get("line_items", [])
                        if item.get("account_id") != account_id
                    ]
                    
                    category = FinancialReportingService._categorize_cash_flow(
                        db, tenant_id, other_accounts, transaction
                    )
                    
                    if category and amount != 0:
                        cash_flows[category]["items"].append({
                            "description": transaction.get("description", "Cash transaction"),
                            "amount": amount,
                            "date": transaction.get("date"),
                            "reference": transaction.get("reference")
                        })
                        cash_flows[category]["total"] += amount
        
        # Calculate net cash flow
        total_cash_flow = sum(cf["total"] for cf in cash_flows.values())
        
        return {
            "report_type": "cash_flow_statement",
            "method": method,
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "cash_flows": cash_flows,
            "net_cash_flow": total_cash_flow,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def _categorize_cash_flow(db, tenant_id: str, other_accounts: List[Dict], transaction: Dict) -> Optional[str]:
        """Categorize cash flow based on related accounts"""
        # This is a simplified categorization logic
        # In practice, you'd have more sophisticated rules based on account types and business logic
        
        for account_item in other_accounts:
            account_id = account_item.get("account_id")
            if account_id:
                try:
                    account = db.accounts.find_one({"_id": ObjectId(account_id)})
                    if account:
                        account_type = account.get("account_type")
                        sub_type = account.get("sub_type", "")
                        
                        # Operating activities
                        if account_type in ["revenue", "expense"]:
                            return "operating"
                        elif account_type == "asset" and sub_type in ["accounts_receivable", "inventory"]:
                            return "operating"
                        elif account_type == "liability" and sub_type in ["accounts_payable", "accrued_expenses"]:
                            return "operating"
                        
                        # Investing activities
                        elif account_type == "asset" and sub_type in ["fixed_assets", "investments"]:
                            return "investing"
                        
                        # Financing activities
                        elif account_type == "liability" and sub_type in ["long_term_debt", "notes_payable"]:
                            return "financing"
                        elif account_type == "equity":
                            return "financing"
                except:
                    continue
        
        # Default to operating if can't categorize
        return "operating"
    
    @staticmethod
    def generate_comparison_report(
        tenant_id: str,
        report_type: str,
        current_start_date: str,
        current_end_date: str,
        comparison_start_date: str,
        comparison_end_date: str
    ) -> Dict:
        """
        Generate period comparison report
        
        Returns:
            Dict with comparison report data
        """
        from app.services.accounting_service import accounting_service
        
        # Generate reports for both periods
        current_report_request = {
            "report_type": report_type,
            "start_date": current_start_date,
            "end_date": current_end_date
        }
        
        comparison_report_request = {
            "report_type": report_type,
            "start_date": comparison_start_date,
            "end_date": comparison_end_date
        }
        
        current_report = accounting_service.generate_financial_report(
            tenant_id=tenant_id,
            **current_report_request
        )
        
        comparison_report = accounting_service.generate_financial_report(
            tenant_id=tenant_id,
            **comparison_report_request
        )
        
        # Calculate variances
        comparison_data = FinancialReportingService._calculate_variances(
            current_report, comparison_report
        )
        
        return {
            "report_type": f"{report_type}_comparison",
            "current_period": {
                "start_date": current_start_date,
                "end_date": current_end_date,
                "data": current_report
            },
            "comparison_period": {
                "start_date": comparison_start_date,
                "end_date": comparison_end_date,
                "data": comparison_report
            },
            "variances": comparison_data,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def _calculate_variances(current_report: Dict, comparison_report: Dict) -> Dict:
        """Calculate variances between two reports"""
        variances = {}
        
        current_data = current_report.get("data", {})
        comparison_data = comparison_report.get("data", {})
        
        # Handle different report structures
        if isinstance(current_data, dict) and isinstance(comparison_data, dict):
            for key, current_value in current_data.items():
                if isinstance(current_value, (int, float)):
                    comparison_value = comparison_data.get(key, 0)
                    variance_amount = current_value - comparison_value
                    variance_percent = (
                        (variance_amount / comparison_value * 100) 
                        if comparison_value != 0 else 0
                    )
                    
                    variances[key] = {
                        "current": current_value,
                        "comparison": comparison_value,
                        "variance_amount": variance_amount,
                        "variance_percent": round(variance_percent, 2)
                    }
        
        return variances
    
    @staticmethod
    def get_drill_down_data(
        tenant_id: str,
        report_type: str,
        account_id: str,
        start_date: str,
        end_date: str,
        transaction_type: Optional[str] = None
    ) -> Dict:
        """
        Get drill-down transaction data for a report line item
        
        Returns:
            Dict with detailed transaction data
        """
        db = Database.get_db()
        
        # Get account details
        account = db.accounts.find_one({
            "_id": ObjectId(account_id),
            "tenant_id": tenant_id
        })
        
        if not account:
            raise NotFoundException("Account not found")
        
        # Get transactions for the account in the period
        pipeline = [
            {
                "$match": {
                    "tenant_id": tenant_id,
                    "date": {"$gte": start_date, "$lte": end_date}
                }
            },
            {"$unwind": "$line_items"},
            {
                "$match": {
                    "line_items.account_id": account_id
                }
            },
            {
                "$project": {
                    "date": 1,
                    "reference": 1,
                    "description": 1,
                    "debit": "$line_items.debit",
                    "credit": "$line_items.credit",
                    "line_description": "$line_items.description"
                }
            },
            {"$sort": {"date": 1}}
        ]
        
        transactions = list(db.journal_entries.aggregate(pipeline))
        
        # Calculate running balance
        running_balance = 0.0
        for transaction in transactions:
            debit = transaction.get("debit", 0)
            credit = transaction.get("credit", 0)
            
            # Calculate balance based on account type
            if account["account_type"] in ["asset", "expense"]:
                running_balance += debit - credit
            else:  # liability, equity, revenue
                running_balance += credit - debit
            
            transaction["running_balance"] = running_balance
        
        # Calculate summary
        total_debits = sum(t.get("debit", 0) for t in transactions)
        total_credits = sum(t.get("credit", 0) for t in transactions)
        
        return {
            "account": {
                "id": str(account["_id"]),
                "code": account["code"],
                "name": account["name"],
                "type": account["account_type"],
                "sub_type": account.get("sub_type")
            },
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "transactions": transactions,
            "summary": {
                "transaction_count": len(transactions),
                "total_debits": total_debits,
                "total_credits": total_credits,
                "net_change": total_debits - total_credits,
                "ending_balance": running_balance
            },
            "generated_at": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def generate_report_visualization_data(
        tenant_id: str,
        report_type: str,
        chart_type: str,
        start_date: str,
        end_date: str,
        group_by: str = "month",
        account_ids: Optional[List[str]] = None
    ) -> Dict:
        """
        Generate data for report visualizations
        
        Returns:
            Dict with chart data
        """
        db = Database.get_db()
        
        # Generate date grouping based on group_by parameter
        date_format = {
            "day": "%Y-%m-%d",
            "week": "%Y-W%U",
            "month": "%Y-%m",
            "quarter": "%Y-Q",
            "year": "%Y"
        }.get(group_by, "%Y-%m")
        
        # Build aggregation pipeline
        pipeline = [
            {
                "$match": {
                    "tenant_id": tenant_id,
                    "date": {"$gte": start_date, "$lte": end_date}
                }
            },
            {"$unwind": "$line_items"}
        ]
        
        # Filter by account IDs if provided
        if account_ids:
            pipeline.append({
                "$match": {
                    "line_items.account_id": {"$in": account_ids}
                }
            })
        
        # Group by date period
        pipeline.extend([
            {
                "$group": {
                    "_id": {
                        "period": {"$dateToString": {"format": date_format, "date": {"$dateFromString": {"dateString": "$date"}}}},
                        "account_id": "$line_items.account_id"
                    },
                    "total_debits": {"$sum": "$line_items.debit"},
                    "total_credits": {"$sum": "$line_items.credit"}
                }
            },
            {
                "$lookup": {
                    "from": "accounts",
                    "localField": "_id.account_id",
                    "foreignField": "_id",
                    "as": "account"
                }
            },
            {"$unwind": "$account"},
            {
                "$project": {
                    "period": "$_id.period",
                    "account_id": "$_id.account_id",
                    "account_name": "$account.name",
                    "account_type": "$account.account_type",
                    "total_debits": 1,
                    "total_credits": 1,
                    "net_amount": {"$subtract": ["$total_debits", "$total_credits"]}
                }
            },
            {"$sort": {"period": 1}}
        ])
        
        results = list(db.journal_entries.aggregate(pipeline))
        
        # Format data for charts
        chart_data = {
            "chart_type": chart_type,
            "group_by": group_by,
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "data": results,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return chart_data


# Singleton instance
financial_reporting_service = FinancialReportingService()