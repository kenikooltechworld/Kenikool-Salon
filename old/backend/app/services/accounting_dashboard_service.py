"""
Accounting Dashboard Service

Handles dashboard KPIs, metrics, and reporting including:
- Financial KPIs calculation
- Trend analysis
- Financial ratios
- Alert generation
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pymongo.database import Database
import logging

logger = logging.getLogger(__name__)


class AccountingDashboardService:
    def __init__(self, db: Database, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.accounts = db.accounts
        self.journal_entries = db.journal_entries
        self.invoices = db.invoices
        self.bills = db.bills
        self.payments = db.payments

    def get_dashboard_kpis(self) -> Dict[str, Any]:
        """Get key performance indicators for dashboard"""
        
        try:
            # Get cash balance
            cash_account = self.accounts.find_one({
                "tenant_id": self.tenant_id,
                "account_type": "asset",
                "sub_type": "cash"
            })
            cash_balance = cash_account.get("balance", 0) if cash_account else 0
            
            # Get accounts receivable
            ar_account = self.accounts.find_one({
                "tenant_id": self.tenant_id,
                "account_type": "asset",
                "sub_type": "accounts_receivable"
            })
            ar_balance = ar_account.get("balance", 0) if ar_account else 0
            
            # Get accounts payable
            ap_account = self.accounts.find_one({
                "tenant_id": self.tenant_id,
                "account_type": "liability",
                "sub_type": "accounts_payable"
            })
            ap_balance = ap_account.get("balance", 0) if ap_account else 0
            
            # Get revenue (current month)
            current_month_start = datetime.utcnow().replace(day=1)
            revenue_account = self.accounts.find_one({
                "tenant_id": self.tenant_id,
                "account_type": "revenue"
            })
            
            current_revenue = 0
            if revenue_account:
                entries = list(self.journal_entries.find({
                    "tenant_id": self.tenant_id,
                    "date": {"$gte": current_month_start.isoformat()},
                    "line_items.account_id": str(revenue_account["_id"])
                }))
                current_revenue = sum(
                    item.get("credit", 0)
                    for entry in entries
                    for item in entry.get("line_items", [])
                    if item.get("account_id") == str(revenue_account["_id"])
                )
            
            # Get expenses (current month)
            expense_accounts = list(self.accounts.find({
                "tenant_id": self.tenant_id,
                "account_type": "expense"
            }))
            
            current_expenses = 0
            for exp_account in expense_accounts:
                entries = list(self.journal_entries.find({
                    "tenant_id": self.tenant_id,
                    "date": {"$gte": current_month_start.isoformat()},
                    "line_items.account_id": str(exp_account["_id"])
                }))
                current_expenses += sum(
                    item.get("debit", 0)
                    for entry in entries
                    for item in entry.get("line_items", [])
                    if item.get("account_id") == str(exp_account["_id"])
                )
            
            # Calculate profit
            current_profit = current_revenue - current_expenses
            
            # Get overdue invoices
            overdue_invoices = list(self.invoices.find({
                "tenant_id": self.tenant_id,
                "status": "sent",
                "due_date": {"$lt": datetime.utcnow().isoformat()}
            }))
            overdue_amount = sum(inv.get("total", 0) for inv in overdue_invoices)
            
            # Get overdue bills
            overdue_bills = list(self.bills.find({
                "tenant_id": self.tenant_id,
                "status": "open",
                "due_date": {"$lt": datetime.utcnow().isoformat()}
            }))
            overdue_bill_amount = sum(bill.get("total", 0) for bill in overdue_bills)
            
            return {
                "cash_balance": cash_balance,
                "accounts_receivable": ar_balance,
                "accounts_payable": ap_balance,
                "current_revenue": current_revenue,
                "current_expenses": current_expenses,
                "current_profit": current_profit,
                "profit_margin": (current_profit / current_revenue * 100) if current_revenue > 0 else 0,
                "overdue_invoices_count": len(overdue_invoices),
                "overdue_invoices_amount": overdue_amount,
                "overdue_bills_count": len(overdue_bills),
                "overdue_bills_amount": overdue_bill_amount,
                "working_capital": cash_balance + ar_balance - ap_balance
            }
        
        except Exception as e:
            logger.error(f"Error getting dashboard KPIs: {str(e)}")
            raise

    def get_trend_data(self, months: int = 12) -> Dict[str, Any]:
        """Get trend data for the last N months"""
        
        try:
            trends = []
            
            for i in range(months, 0, -1):
                month_start = datetime.utcnow().replace(day=1) - timedelta(days=30*i)
                month_end = month_start + timedelta(days=30)
                
                # Get revenue for month
                revenue_account = self.accounts.find_one({
                    "tenant_id": self.tenant_id,
                    "account_type": "revenue"
                })
                
                month_revenue = 0
                if revenue_account:
                    entries = list(self.journal_entries.find({
                        "tenant_id": self.tenant_id,
                        "date": {
                            "$gte": month_start.isoformat(),
                            "$lt": month_end.isoformat()
                        },
                        "line_items.account_id": str(revenue_account["_id"])
                    }))
                    month_revenue = sum(
                        item.get("credit", 0)
                        for entry in entries
                        for item in entry.get("line_items", [])
                        if item.get("account_id") == str(revenue_account["_id"])
                    )
                
                # Get expenses for month
                expense_accounts = list(self.accounts.find({
                    "tenant_id": self.tenant_id,
                    "account_type": "expense"
                }))
                
                month_expenses = 0
                for exp_account in expense_accounts:
                    entries = list(self.journal_entries.find({
                        "tenant_id": self.tenant_id,
                        "date": {
                            "$gte": month_start.isoformat(),
                            "$lt": month_end.isoformat()
                        },
                        "line_items.account_id": str(exp_account["_id"])
                    }))
                    month_expenses += sum(
                        item.get("debit", 0)
                        for entry in entries
                        for item in entry.get("line_items", [])
                        if item.get("account_id") == str(exp_account["_id"])
                    )
                
                trends.append({
                    "month": month_start.strftime("%Y-%m"),
                    "revenue": month_revenue,
                    "expenses": month_expenses,
                    "profit": month_revenue - month_expenses
                })
            
            return {"trends": trends}
        
        except Exception as e:
            logger.error(f"Error getting trend data: {str(e)}")
            raise

    def get_financial_ratios(self) -> Dict[str, Any]:
        """Calculate financial ratios"""
        
        try:
            # Get all accounts
            assets = list(self.accounts.find({
                "tenant_id": self.tenant_id,
                "account_type": "asset"
            }))
            
            liabilities = list(self.accounts.find({
                "tenant_id": self.tenant_id,
                "account_type": "liability"
            }))
            
            equity = list(self.accounts.find({
                "tenant_id": self.tenant_id,
                "account_type": "equity"
            }))
            
            # Calculate totals
            total_assets = sum(acc.get("balance", 0) for acc in assets)
            total_liabilities = sum(acc.get("balance", 0) for acc in liabilities)
            total_equity = sum(acc.get("balance", 0) for acc in equity)
            
            # Get current revenue and expenses
            current_month_start = datetime.utcnow().replace(day=1)
            
            revenue_account = self.accounts.find_one({
                "tenant_id": self.tenant_id,
                "account_type": "revenue"
            })
            
            current_revenue = 0
            if revenue_account:
                entries = list(self.journal_entries.find({
                    "tenant_id": self.tenant_id,
                    "date": {"$gte": current_month_start.isoformat()},
                    "line_items.account_id": str(revenue_account["_id"])
                }))
                current_revenue = sum(
                    item.get("credit", 0)
                    for entry in entries
                    for item in entry.get("line_items", [])
                    if item.get("account_id") == str(revenue_account["_id"])
                )
            
            # Calculate ratios
            current_ratio = total_assets / total_liabilities if total_liabilities > 0 else 0
            debt_to_equity = total_liabilities / total_equity if total_equity > 0 else 0
            roa = current_revenue / total_assets if total_assets > 0 else 0
            
            return {
                "current_ratio": round(current_ratio, 2),
                "debt_to_equity": round(debt_to_equity, 2),
                "return_on_assets": round(roa, 2),
                "total_assets": total_assets,
                "total_liabilities": total_liabilities,
                "total_equity": total_equity
            }
        
        except Exception as e:
            logger.error(f"Error calculating financial ratios: {str(e)}")
            raise

    def get_alerts(self) -> Dict[str, Any]:
        """Get alerts for dashboard"""
        
        try:
            alerts = []
            
            # Check for low cash
            cash_account = self.accounts.find_one({
                "tenant_id": self.tenant_id,
                "account_type": "asset",
                "sub_type": "cash"
            })
            
            if cash_account and cash_account.get("balance", 0) < 5000:
                alerts.append({
                    "type": "warning",
                    "title": "Low Cash Balance",
                    "message": f"Cash balance is ${cash_account.get('balance', 0):.2f}",
                    "severity": "high"
                })
            
            # Check for overdue invoices
            overdue_invoices = list(self.invoices.find({
                "tenant_id": self.tenant_id,
                "status": "sent",
                "due_date": {"$lt": datetime.utcnow().isoformat()}
            }))
            
            if overdue_invoices:
                total_overdue = sum(inv.get("total", 0) for inv in overdue_invoices)
                alerts.append({
                    "type": "warning",
                    "title": "Overdue Invoices",
                    "message": f"{len(overdue_invoices)} invoices overdue totaling ${total_overdue:.2f}",
                    "severity": "medium"
                })
            
            # Check for overdue bills
            overdue_bills = list(self.bills.find({
                "tenant_id": self.tenant_id,
                "status": "open",
                "due_date": {"$lt": datetime.utcnow().isoformat()}
            }))
            
            if overdue_bills:
                total_overdue = sum(bill.get("total", 0) for bill in overdue_bills)
                alerts.append({
                    "type": "error",
                    "title": "Overdue Bills",
                    "message": f"{len(overdue_bills)} bills overdue totaling ${total_overdue:.2f}",
                    "severity": "high"
                })
            
            # Check for negative equity
            equity_accounts = list(self.accounts.find({
                "tenant_id": self.tenant_id,
                "account_type": "equity"
            }))
            
            total_equity = sum(acc.get("balance", 0) for acc in equity_accounts)
            if total_equity < 0:
                alerts.append({
                    "type": "error",
                    "title": "Negative Equity",
                    "message": f"Total equity is ${total_equity:.2f}",
                    "severity": "critical"
                })
            
            return {"alerts": alerts}
        
        except Exception as e:
            logger.error(f"Error getting alerts: {str(e)}")
            raise
