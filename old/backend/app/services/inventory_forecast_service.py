"""
Inventory forecasting service using AI/ML
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


async def analyze_usage_patterns(product_id: str, tenant_id: str, db) -> Dict:
    """
    Analyze usage patterns for a product
    """
    try:
        # Get product
        from bson import ObjectId
        product = await db.inventory.find_one({
            "_id": ObjectId(product_id),
            "tenant_id": tenant_id
        })
        
        if product is None:
            return {"error": "Product not found"}
        
        # Get transactions
        transactions = product.get("transactions", [])
        
        if len(transactions) < 10:
            return {
                "product_id": product_id,
                "product_name": product["name"],
                "insufficient_data": True,
                "message": "Need at least 10 transactions for analysis"
            }
        
        # Filter usage transactions
        usage_transactions = [
            t for t in transactions
            if t.get("transaction_type") == "usage"
        ]
        
        if len(usage_transactions) < 5:
            return {
                "product_id": product_id,
                "product_name": product["name"],
                "insufficient_data": True,
                "message": "Need at least 5 usage transactions for analysis"
            }
        
        # Create DataFrame
        df = pd.DataFrame(usage_transactions)
        df["created_at"] = pd.to_datetime(df["created_at"])
        df["quantity"] = df["quantity"].abs()  # Make positive for analysis
        df = df.sort_values("created_at")
        
        # Calculate statistics
        daily_usage = df.groupby(df["created_at"].dt.date)["quantity"].sum()
        
        avg_daily_usage = daily_usage.mean()
        std_daily_usage = daily_usage.std()
        max_daily_usage = daily_usage.max()
        min_daily_usage = daily_usage.min()
        
        # Calculate trend (simple linear regression)
        days = (df["created_at"] - df["created_at"].min()).dt.days
        if len(days) > 1:
            trend = np.polyfit(days, df["quantity"], 1)[0]
        else:
            trend = 0
        
        return {
            "product_id": product_id,
            "product_name": product["name"],
            "current_quantity": product["quantity"],
            "unit": product["unit"],
            "avg_daily_usage": float(avg_daily_usage),
            "std_daily_usage": float(std_daily_usage),
            "max_daily_usage": float(max_daily_usage),
            "min_daily_usage": float(min_daily_usage),
            "trend": float(trend),
            "total_transactions": len(usage_transactions),
            "analysis_period_days": (df["created_at"].max() - df["created_at"].min()).days
        }
    
    except Exception as e:
        logger.error(f"Error analyzing usage patterns: {e}")
        return {"error": str(e)}


async def predict_stockout_date(product_id: str, tenant_id: str, db) -> Dict:
    """
    Predict when a product will run out of stock
    """
    try:
        # Get usage patterns
        patterns = await analyze_usage_patterns(product_id, tenant_id, db)
        
        if patterns.get("error") or patterns.get("insufficient_data"):
            return patterns
        
        current_quantity = patterns["current_quantity"]
        avg_daily_usage = patterns["avg_daily_usage"]
        
        if avg_daily_usage <= 0:
            return {
                "product_id": product_id,
                "product_name": patterns["product_name"],
                "prediction": "No usage detected",
                "days_until_stockout": None
            }
        
        # Calculate days until stockout
        days_until_stockout = int(current_quantity / avg_daily_usage)
        stockout_date = datetime.utcnow() + timedelta(days=days_until_stockout)
        
        # Determine urgency
        if days_until_stockout <= 7:
            urgency = "critical"
        elif days_until_stockout <= 14:
            urgency = "high"
        elif days_until_stockout <= 30:
            urgency = "medium"
        else:
            urgency = "low"
        
        return {
            "product_id": product_id,
            "product_name": patterns["product_name"],
            "current_quantity": current_quantity,
            "avg_daily_usage": avg_daily_usage,
            "days_until_stockout": days_until_stockout,
            "predicted_stockout_date": stockout_date.strftime("%Y-%m-%d"),
            "urgency": urgency,
            "recommendation": f"Reorder within {max(1, days_until_stockout - 7)} days"
        }
    
    except Exception as e:
        logger.error(f"Error predicting stockout: {e}")
        return {"error": str(e)}


async def generate_reorder_suggestions(tenant_id: str, db) -> List[Dict]:
    """
    Generate reorder suggestions for all products
    """
    try:
        # Get all active products
        cursor = db.inventory.find({
            "tenant_id": tenant_id,
            "is_active": True
        })
        
        suggestions = []
        
        async for product in cursor:
            product_id = str(product["_id"])
            
            # Get stockout prediction
            prediction = await predict_stockout_date(product_id, tenant_id, db)
            
            if prediction.get("error") or prediction.get("insufficient_data"):
                continue
            
            # Only suggest if stockout is within 30 days
            days_until_stockout = prediction.get("days_until_stockout")
            if days_until_stockout and days_until_stockout <= 30:
                # Calculate suggested reorder quantity
                # Order enough for 30 days + safety stock (1 week)
                avg_daily_usage = prediction["avg_daily_usage"]
                suggested_quantity = int(avg_daily_usage * 37)  # 30 + 7 days
                
                suggestions.append({
                    "product_id": product_id,
                    "product_name": prediction["product_name"],
                    "current_quantity": prediction["current_quantity"],
                    "days_until_stockout": days_until_stockout,
                    "predicted_stockout_date": prediction["predicted_stockout_date"],
                    "urgency": prediction["urgency"],
                    "suggested_reorder_quantity": suggested_quantity,
                    "estimated_cost": suggested_quantity * product.get("unit_cost", 0),
                    "supplier": product.get("supplier")
                })
        
        # Sort by urgency
        urgency_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        suggestions.sort(key=lambda x: urgency_order.get(x["urgency"], 4))
        
        return suggestions
    
    except Exception as e:
        logger.error(f"Error generating reorder suggestions: {e}")
        return []
