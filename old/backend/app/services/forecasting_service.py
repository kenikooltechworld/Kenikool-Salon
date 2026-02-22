"""
Forecasting Service - AI-powered inventory forecasting
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from statistics import mean, stdev


class ForecastingService:
    """Service for inventory forecasting and analytics"""

    def __init__(self, db):
        self.db = db
        self.transactions_collection = db["inventory_transactions"]
        self.products_collection = db["inventory_products"]
        self.forecasts_collection = db["inventory_forecasts"]

    async def calculate_usage_rates(
        self,
        tenant_id: str,
        product_id: str,
        days: int = 90,
    ) -> Dict[str, Any]:
        """Calculate usage rates from transaction data"""
        start_date = datetime.utcnow() - timedelta(days=days)

        # Get all removal transactions
        transactions = await self.transactions_collection.find({
            "tenant_id": tenant_id,
            "product_id": product_id,
            "transaction_type": {"$in": ["remove", "service_usage", "pos_sale", "waste"]},
            "created_at": {"$gte": start_date},
        }).to_list(length=None)

        if not transactions:
            return {
                "daily_usage": 0,
                "weekly_usage": 0,
                "monthly_usage": 0,
                "data_points": 0,
            }

        total_removed = sum(abs(tx["quantity_changed"]) for tx in transactions)
        data_points = len(transactions)

        daily_usage = total_removed / days if days > 0 else 0
        weekly_usage = daily_usage * 7
        monthly_usage = daily_usage * 30

        return {
            "daily_usage": round(daily_usage, 2),
            "weekly_usage": round(weekly_usage, 2),
            "monthly_usage": round(monthly_usage, 2),
            "data_points": data_points,
            "total_removed": total_removed,
        }

    async def predict_stockout_date(
        self,
        tenant_id: str,
        product_id: str,
    ) -> Dict[str, Any]:
        """Predict when product will run out of stock"""
        product = await self.products_collection.find_one({
            "_id": product_id,
            "tenant_id": tenant_id,
        })

        if not product:
            return {"error": "Product not found"}

        current_quantity = product.get("quantity", 0)
        usage_rates = await self.calculate_usage_rates(
            tenant_id=tenant_id,
            product_id=product_id,
        )

        daily_usage = usage_rates["daily_usage"]

        if daily_usage <= 0:
            return {
                "stockout_date": None,
                "days_until_stockout": None,
                "confidence": 0,
                "message": "No usage data available",
            }

        days_until_stockout = current_quantity / daily_usage if daily_usage > 0 else None

        # Calculate confidence based on data points
        data_points = usage_rates["data_points"]
        confidence = min(100, (data_points / 30) * 100)  # 30 data points = 100% confidence

        stockout_date = None
        if days_until_stockout:
            stockout_date = (
                datetime.utcnow() + timedelta(days=days_until_stockout)
            ).isoformat()

        return {
            "current_quantity": current_quantity,
            "daily_usage": daily_usage,
            "days_until_stockout": round(days_until_stockout, 1) if days_until_stockout else None,
            "stockout_date": stockout_date,
            "confidence": round(confidence, 1),
        }

    async def detect_seasonality(
        self,
        tenant_id: str,
        product_id: str,
        days: int = 180,
    ) -> Dict[str, Any]:
        """Detect seasonal patterns in usage"""
        start_date = datetime.utcnow() - timedelta(days=days)

        transactions = await self.transactions_collection.find({
            "tenant_id": tenant_id,
            "product_id": product_id,
            "transaction_type": {"$in": ["remove", "service_usage", "pos_sale"]},
            "created_at": {"$gte": start_date},
        }).to_list(length=None)

        if not transactions:
            return {"seasonal": False, "pattern": None}

        # Group by week
        weekly_usage = {}
        for tx in transactions:
            week = tx["created_at"].isocalendar()[1]
            if week not in weekly_usage:
                weekly_usage[week] = 0
            weekly_usage[week] += abs(tx["quantity_changed"])

        if len(weekly_usage) < 4:
            return {"seasonal": False, "pattern": None, "message": "Insufficient data"}

        # Calculate variance
        usages = list(weekly_usage.values())
        avg_usage = mean(usages)
        usage_stdev = stdev(usages) if len(usages) > 1 else 0
        coefficient_of_variation = (usage_stdev / avg_usage * 100) if avg_usage > 0 else 0

        # If CV > 30%, consider it seasonal
        is_seasonal = coefficient_of_variation > 30

        return {
            "seasonal": is_seasonal,
            "coefficient_of_variation": round(coefficient_of_variation, 2),
            "average_weekly_usage": round(avg_usage, 2),
            "pattern": "High variation detected" if is_seasonal else "Consistent usage",
        }

    async def get_reorder_suggestions(
        self,
        tenant_id: str,
    ) -> List[Dict[str, Any]]:
        """Get reorder suggestions for all products"""
        products = await self.products_collection.find({
            "tenant_id": tenant_id,
            "is_active": True,
        }).to_list(length=None)

        suggestions = []

        for product in products:
            current_quantity = product.get("quantity", 0)
            reorder_point = product.get("reorder_point", 10)

            if current_quantity <= reorder_point:
                usage_rates = await self.calculate_usage_rates(
                    tenant_id=tenant_id,
                    product_id=str(product["_id"]),
                )

                stockout_info = await self.predict_stockout_date(
                    tenant_id=tenant_id,
                    product_id=str(product["_id"]),
                )

                suggestions.append({
                    "product_id": str(product["_id"]),
                    "product_name": product.get("name"),
                    "current_quantity": current_quantity,
                    "reorder_point": reorder_point,
                    "reorder_quantity": product.get("reorder_quantity", 50),
                    "daily_usage": usage_rates["daily_usage"],
                    "days_until_stockout": stockout_info.get("days_until_stockout"),
                    "urgency": "critical" if current_quantity == 0 else "high" if current_quantity < reorder_point / 2 else "medium",
                })

        return sorted(suggestions, key=lambda x: x["urgency"] == "critical", reverse=True)

    async def refresh_forecasts(
        self,
        tenant_id: str,
    ) -> int:
        """Refresh forecasts for all products"""
        products = await self.products_collection.find({
            "tenant_id": tenant_id,
            "is_active": True,
        }).to_list(length=None)

        updated_count = 0

        for product in products:
            product_id = str(product["_id"])

            usage_rates = await self.calculate_usage_rates(
                tenant_id=tenant_id,
                product_id=product_id,
            )

            stockout_info = await self.predict_stockout_date(
                tenant_id=tenant_id,
                product_id=product_id,
            )

            seasonality = await self.detect_seasonality(
                tenant_id=tenant_id,
                product_id=product_id,
            )

            forecast_data = {
                "tenant_id": tenant_id,
                "product_id": product_id,
                "usage_rates": usage_rates,
                "stockout_prediction": stockout_info,
                "seasonality": seasonality,
                "updated_at": datetime.utcnow(),
            }

            await self.forecasts_collection.update_one(
                {
                    "tenant_id": tenant_id,
                    "product_id": product_id,
                },
                {"$set": forecast_data},
                upsert=True,
            )

            updated_count += 1

        return updated_count
