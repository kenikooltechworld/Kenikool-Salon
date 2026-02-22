"""
Budget and Forecasting Service

Handles budget management and forecasting operations including:
- Creating and managing budgets
- Budget vs actual variance analysis
- Trend-based forecasting
- Budget copying and adjustments
"""

from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from pymongo.database import Database
from bson import ObjectId
import uuid
import statistics
from dateutil.relativedelta import relativedelta


class BudgetService:
    def __init__(self, db: Database, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.budgets = db.budgets
        self.accounts = db.accounts
        self.journal_entries = db.journal_entries

    def get_budgets(
        self,
        budget_year: Optional[int] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get budgets with optional filtering"""
        
        query = {"tenant_id": self.tenant_id}
        
        if budget_year:
            query["budget_year"] = budget_year
        if status:
            query["status"] = status
        
        budgets = list(
            self.budgets.find(query)
            .sort("created_at", -1)
            .skip(offset)
            .limit(limit)
        )
        
        # Convert ObjectId to string and calculate totals
        for budget in budgets:
            budget["id"] = str(budget["_id"])
            del budget["_id"]
            
            # Calculate budget totals
            self._calculate_budget_totals(budget)
        
        return budgets

    def create_budget(self, budget_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new budget"""
        
        # Validate accounts exist
        account_ids = [item["account_id"] for item in budget_data["line_items"]]
        accounts = list(self.accounts.find({
            "_id": {"$in": [ObjectId(aid) for aid in account_ids]},
            "tenant_id": self.tenant_id
        }))
        
        if len(accounts) != len(account_ids):
            raise ValueError("One or more accounts not found")
        
        # Create account lookup for names and codes
        account_lookup = {str(acc["_id"]): acc for acc in accounts}
        
        # Enrich line items with account information
        enriched_line_items = []
        for item in budget_data["line_items"]:
            account = account_lookup[item["account_id"]]
            enriched_item = {
                "id": str(uuid.uuid4()),
                "account_id": item["account_id"],
                "account_code": account.get("code", ""),
                "account_name": account.get("name", ""),
                "budgeted_amount": item["budgeted_amount"],
                "actual_amount": 0.0,
                "variance_amount": -item["budgeted_amount"],  # Initially all variance
                "variance_percentage": -100.0 if item["budgeted_amount"] != 0 else 0.0,
                "notes": item.get("notes", "")
            }
            enriched_line_items.append(enriched_item)
        
        budget_doc = {
            "tenant_id": self.tenant_id,
            "name": budget_data["name"],
            "description": budget_data.get("description", ""),
            "budget_year": budget_data["budget_year"],
            "period_type": budget_data["period_type"],
            "start_date": budget_data["start_date"],
            "end_date": budget_data["end_date"],
            "status": "draft",
            "line_items": enriched_line_items,
            "created_by": budget_data.get("created_by", "system"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Calculate totals
        self._calculate_budget_totals(budget_doc)
        
        result = self.budgets.insert_one(budget_doc)
        budget_doc["id"] = str(result.inserted_id)
        del budget_doc["_id"]
        
        return budget_doc

    def update_budget(
        self, 
        budget_id: str, 
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing budget"""
        
        update_fields = {}
        
        if "name" in update_data:
            update_fields["name"] = update_data["name"]
        if "description" in update_data:
            update_fields["description"] = update_data["description"]
        if "status" in update_data:
            update_fields["status"] = update_data["status"]
        
        if "line_items" in update_data:
            # Enrich line items with account information
            account_ids = [item["account_id"] for item in update_data["line_items"]]
            accounts = list(self.accounts.find({
                "_id": {"$in": [ObjectId(aid) for aid in account_ids]},
                "tenant_id": self.tenant_id
            }))
            
            account_lookup = {str(acc["_id"]): acc for acc in accounts}
            
            enriched_line_items = []
            for item in update_data["line_items"]:
                account = account_lookup[item["account_id"]]
                enriched_item = {
                    "id": item.get("id", str(uuid.uuid4())),
                    "account_id": item["account_id"],
                    "account_code": account.get("code", ""),
                    "account_name": account.get("name", ""),
                    "budgeted_amount": item["budgeted_amount"],
                    "notes": item.get("notes", "")
                }
                enriched_line_items.append(enriched_item)
            
            update_fields["line_items"] = enriched_line_items
        
        update_fields["updated_at"] = datetime.utcnow()
        
        self.budgets.update_one(
            {"_id": ObjectId(budget_id), "tenant_id": self.tenant_id},
            {"$set": update_fields}
        )
        
        return self.get_budget(budget_id)

    def get_budget(self, budget_id: str) -> Dict[str, Any]:
        """Get a specific budget by ID"""
        
        budget = self.budgets.find_one({
            "_id": ObjectId(budget_id),
            "tenant_id": self.tenant_id
        })
        
        if not budget:
            raise ValueError("Budget not found")
        
        budget["id"] = str(budget["_id"])
        del budget["_id"]
        
        # Calculate actual amounts and variances
        self._calculate_actual_amounts(budget)
        self._calculate_budget_totals(budget)
        
        return budget

    def get_budget_variance(self, budget_id: str) -> Dict[str, Any]:
        """Get budget variance analysis"""
        
        budget = self.get_budget(budget_id)
        
        # Separate over/under budget accounts
        over_budget_accounts = []
        under_budget_accounts = []
        
        for item in budget["line_items"]:
            if item["variance_amount"] > 0:
                over_budget_accounts.append(item)
            elif item["variance_amount"] < 0:
                under_budget_accounts.append(item)
        
        variance_analysis = {
            "budget_id": budget["id"],
            "budget_name": budget["name"],
            "period_start": budget["start_date"],
            "period_end": budget["end_date"],
            "total_budgeted": budget["total_budgeted"],
            "total_actual": budget["total_actual"],
            "total_variance": budget["total_variance"],
            "variance_percentage": budget["variance_percentage"],
            "line_items": budget["line_items"],
            "over_budget_accounts": over_budget_accounts,
            "under_budget_accounts": under_budget_accounts
        }
        
        return variance_analysis

    def copy_budget(self, copy_request: Dict[str, Any]) -> Dict[str, Any]:
        """Copy an existing budget with optional adjustments"""
        
        source_budget = self.get_budget(copy_request["source_budget_id"])
        
        # Apply percentage adjustment to line items
        adjustment_factor = 1 + (copy_request.get("adjustment_percentage", 0) / 100)
        
        new_line_items = []
        for item in source_budget["line_items"]:
            new_item = {
                "account_id": item["account_id"],
                "budgeted_amount": item["budgeted_amount"] * adjustment_factor,
                "notes": item.get("notes", "")
            }
            new_line_items.append(new_item)
        
        # Create new budget
        new_budget_data = {
            "name": copy_request["new_budget_name"],
            "description": f"Copied from {source_budget['name']}",
            "budget_year": copy_request["new_budget_year"],
            "period_type": source_budget["period_type"],
            "start_date": copy_request["start_date"],
            "end_date": copy_request["end_date"],
            "line_items": new_line_items,
            "created_by": copy_request.get("created_by", "system")
        }
        
        return self.create_budget(new_budget_data)

    def generate_forecast(self, forecast_request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate forecast for an account based on historical data"""
        
        account_id = forecast_request["account_id"]
        forecast_periods = forecast_request["forecast_periods"]
        forecast_method = forecast_request.get("forecast_method", "trend")
        
        # Get account information
        account = self.accounts.find_one({
            "_id": ObjectId(account_id),
            "tenant_id": self.tenant_id
        })
        
        if not account:
            raise ValueError("Account not found")
        
        # Get historical data (last 12 months)
        historical_data = self._get_historical_account_data(account_id, 12)
        
        # Generate forecast based on method
        if forecast_method == "trend":
            forecast_data = self._generate_trend_forecast(historical_data, forecast_periods)
        elif forecast_method == "average":
            forecast_data = self._generate_average_forecast(historical_data, forecast_periods)
        elif forecast_method == "seasonal":
            forecast_data = self._generate_seasonal_forecast(historical_data, forecast_periods)
        else:
            raise ValueError(f"Unknown forecast method: {forecast_method}")
        
        # Apply manual adjustments if provided
        if forecast_request.get("manual_adjustments"):
            forecast_data = self._apply_manual_adjustments(
                forecast_data, 
                forecast_request["manual_adjustments"]
            )
        
        forecast_response = {
            "account_id": account_id,
            "account_name": account.get("name", "Unknown Account"),
            "forecast_method": forecast_method,
            "historical_data": historical_data,
            "forecast_data": forecast_data,
            "confidence_level": self._calculate_confidence_level(historical_data),
            "generated_at": datetime.utcnow()
        }
        
        return forecast_response

    def _calculate_budget_totals(self, budget: Dict[str, Any]):
        """Calculate budget totals and variances"""
        
        total_budgeted = sum(item["budgeted_amount"] for item in budget["line_items"])
        total_actual = sum(item.get("actual_amount", 0) for item in budget["line_items"])
        total_variance = total_actual - total_budgeted
        variance_percentage = (total_variance / total_budgeted * 100) if total_budgeted != 0 else 0
        
        budget["total_budgeted"] = total_budgeted
        budget["total_actual"] = total_actual
        budget["total_variance"] = total_variance
        budget["variance_percentage"] = variance_percentage

    def _calculate_actual_amounts(self, budget: Dict[str, Any]):
        """Calculate actual amounts for budget line items"""
        
        start_date = budget["start_date"]
        end_date = budget["end_date"]
        
        for item in budget["line_items"]:
            account_id = item["account_id"]
            
            # Get actual amount from journal entries
            actual_amount = self._get_account_actual_amount(account_id, start_date, end_date)
            
            item["actual_amount"] = actual_amount
            item["variance_amount"] = actual_amount - item["budgeted_amount"]
            item["variance_percentage"] = (
                (item["variance_amount"] / item["budgeted_amount"] * 100) 
                if item["budgeted_amount"] != 0 else 0
            )

    def _get_account_actual_amount(self, account_id: str, start_date: str, end_date: str) -> float:
        """Get actual amount for an account within a date range"""
        
        pipeline = [
            {
                "$match": {
                    "tenant_id": self.tenant_id,
                    "date": {"$gte": start_date, "$lte": end_date},
                    "line_items.account_id": account_id
                }
            },
            {
                "$unwind": "$line_items"
            },
            {
                "$match": {
                    "line_items.account_id": account_id
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_debit": {"$sum": "$line_items.debit"},
                    "total_credit": {"$sum": "$line_items.credit"}
                }
            }
        ]
        
        result = list(self.journal_entries.aggregate(pipeline))
        
        if result:
            # For most accounts, we want net change (debit - credit)
            # For revenue and liability accounts, this might need to be reversed
            return result[0]["total_debit"] - result[0]["total_credit"]
        
        return 0.0

    def _get_historical_account_data(self, account_id: str, months: int) -> List[Dict[str, Any]]:
        """Get historical monthly data for an account"""
        
        historical_data = []
        current_date = datetime.now()
        
        for i in range(months):
            # Calculate month start and end dates
            month_date = current_date - relativedelta(months=i)
            month_start = month_date.replace(day=1).strftime("%Y-%m-%d")
            
            # Get last day of month
            next_month = month_date.replace(day=28) + timedelta(days=4)
            month_end = (next_month - timedelta(days=next_month.day)).strftime("%Y-%m-%d")
            
            amount = self._get_account_actual_amount(account_id, month_start, month_end)
            
            historical_data.append({
                "period": month_date.strftime("%Y-%m"),
                "amount": amount,
                "start_date": month_start,
                "end_date": month_end
            })
        
        return list(reversed(historical_data))  # Oldest first

    def _generate_trend_forecast(self, historical_data: List[Dict[str, Any]], periods: int) -> List[Dict[str, Any]]:
        """Generate forecast using linear trend analysis"""
        
        if len(historical_data) < 2:
            # Not enough data for trend analysis, use last value
            last_amount = historical_data[-1]["amount"] if historical_data else 0
            return self._generate_flat_forecast(last_amount, periods)
        
        # Calculate linear trend
        amounts = [data["amount"] for data in historical_data]
        x_values = list(range(len(amounts)))
        
        # Simple linear regression
        n = len(amounts)
        sum_x = sum(x_values)
        sum_y = sum(amounts)
        sum_xy = sum(x * y for x, y in zip(x_values, amounts))
        sum_x2 = sum(x * x for x in x_values)
        
        # Calculate slope and intercept
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        intercept = (sum_y - slope * sum_x) / n
        
        # Generate forecast
        forecast_data = []
        current_date = datetime.now()
        
        for i in range(1, periods + 1):
            forecast_date = current_date + relativedelta(months=i)
            forecast_amount = intercept + slope * (len(amounts) + i - 1)
            
            forecast_data.append({
                "period": forecast_date.strftime("%Y-%m"),
                "amount": max(0, forecast_amount),  # Don't forecast negative amounts
                "method": "trend"
            })
        
        return forecast_data

    def _generate_average_forecast(self, historical_data: List[Dict[str, Any]], periods: int) -> List[Dict[str, Any]]:
        """Generate forecast using historical average"""
        
        if not historical_data:
            return self._generate_flat_forecast(0, periods)
        
        amounts = [data["amount"] for data in historical_data]
        average_amount = statistics.mean(amounts)
        
        return self._generate_flat_forecast(average_amount, periods)

    def _generate_seasonal_forecast(self, historical_data: List[Dict[str, Any]], periods: int) -> List[Dict[str, Any]]:
        """Generate forecast using seasonal patterns"""
        
        if len(historical_data) < 12:
            # Not enough data for seasonal analysis, fall back to trend
            return self._generate_trend_forecast(historical_data, periods)
        
        # Calculate seasonal factors (simplified)
        monthly_averages = {}
        for data in historical_data:
            month = int(data["period"].split("-")[1])
            if month not in monthly_averages:
                monthly_averages[month] = []
            monthly_averages[month].append(data["amount"])
        
        # Calculate average for each month
        seasonal_factors = {}
        overall_average = statistics.mean([data["amount"] for data in historical_data])
        
        for month, amounts in monthly_averages.items():
            month_average = statistics.mean(amounts)
            seasonal_factors[month] = month_average / overall_average if overall_average != 0 else 1
        
        # Generate forecast
        forecast_data = []
        current_date = datetime.now()
        
        for i in range(1, periods + 1):
            forecast_date = current_date + relativedelta(months=i)
            month = forecast_date.month
            
            seasonal_factor = seasonal_factors.get(month, 1.0)
            forecast_amount = overall_average * seasonal_factor
            
            forecast_data.append({
                "period": forecast_date.strftime("%Y-%m"),
                "amount": max(0, forecast_amount),
                "method": "seasonal"
            })
        
        return forecast_data

    def _generate_flat_forecast(self, amount: float, periods: int) -> List[Dict[str, Any]]:
        """Generate flat forecast with constant amount"""
        
        forecast_data = []
        current_date = datetime.now()
        
        for i in range(1, periods + 1):
            forecast_date = current_date + relativedelta(months=i)
            
            forecast_data.append({
                "period": forecast_date.strftime("%Y-%m"),
                "amount": amount,
                "method": "flat"
            })
        
        return forecast_data

    def _apply_manual_adjustments(self, forecast_data: List[Dict[str, Any]], adjustments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply manual adjustments to forecast data"""
        
        adjustment_lookup = {adj["period"]: adj["amount"] for adj in adjustments}
        
        for data in forecast_data:
            if data["period"] in adjustment_lookup:
                data["amount"] = adjustment_lookup[data["period"]]
                data["method"] = "manual"
        
        return forecast_data

    def _calculate_confidence_level(self, historical_data: List[Dict[str, Any]]) -> float:
        """Calculate confidence level based on data consistency"""
        
        if len(historical_data) < 3:
            return 0.5  # Low confidence with limited data
        
        amounts = [data["amount"] for data in historical_data]
        
        # Calculate coefficient of variation
        mean_amount = statistics.mean(amounts)
        if mean_amount == 0:
            return 0.5
        
        std_dev = statistics.stdev(amounts)
        coefficient_of_variation = std_dev / mean_amount
        
        # Convert to confidence level (lower variation = higher confidence)
        confidence = max(0.1, min(0.9, 1 - coefficient_of_variation))
        
        return confidence

    def get_budget_summary(self) -> Dict[str, Any]:
        """Get budget summary for the tenant"""
        
        current_year = datetime.now().year
        
        # Get active budgets for current year
        active_budgets = list(self.budgets.find({
            "tenant_id": self.tenant_id,
            "budget_year": current_year,
            "status": "active"
        }))
        
        total_budgeted = 0
        total_actual = 0
        
        for budget in active_budgets:
            self._calculate_actual_amounts(budget)
            self._calculate_budget_totals(budget)
            total_budgeted += budget["total_budgeted"]
            total_actual += budget["total_actual"]
        
        summary = {
            "budget_year": current_year,
            "active_budgets_count": len(active_budgets),
            "total_budgeted": total_budgeted,
            "total_actual": total_actual,
            "total_variance": total_actual - total_budgeted,
            "variance_percentage": ((total_actual - total_budgeted) / total_budgeted * 100) if total_budgeted != 0 else 0,
            "budgets": [
                {
                    "id": str(budget["_id"]),
                    "name": budget["name"],
                    "total_budgeted": budget["total_budgeted"],
                    "total_actual": budget["total_actual"],
                    "variance_percentage": budget["variance_percentage"]
                }
                for budget in active_budgets
            ]
        }
        
        return summary