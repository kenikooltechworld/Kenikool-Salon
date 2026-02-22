"""
AI-powered client retention prediction service
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)


async def calculate_client_features(client_id: str, tenant_id: str, db) -> Dict:
    """
    Calculate features for a client for churn prediction
    """
    try:
        from bson import ObjectId
        
        # Get client
        client = await db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id
        })
        
        if client is None:
            return {"error": "Client not found"}
        
        # Get client's bookings
        bookings = await db.bookings.find({
            "client_id": client_id,
            "tenant_id": tenant_id,
            "status": {"$in": ["completed", "confirmed"]}
        }).sort("booking_date", -1).to_list(length=None)
        
        if len(bookings) == 0:
            return {
                "error": "No booking history",
                "client_id": client_id
            }
        
        # Calculate features
        total_visits = len(bookings)
        total_spent = sum(b.get("service_price", 0) for b in bookings)
        avg_spend_per_visit = total_spent / total_visits if total_visits > 0 else 0
        
        # Calculate days since last visit
        last_visit = client.get("last_visit_date") or bookings[0].get("booking_date")
        if last_visit:
            days_since_last_visit = (datetime.utcnow() - last_visit).days
        else:
            days_since_last_visit = 999
        
        # Calculate visit frequency (days between visits)
        if len(bookings) >= 2:
            visit_dates = [b["booking_date"] for b in bookings if b.get("booking_date")]
            visit_dates.sort()
            intervals = [(visit_dates[i+1] - visit_dates[i]).days 
                        for i in range(len(visit_dates)-1)]
            avg_days_between_visits = np.mean(intervals) if intervals else 30
            std_days_between_visits = np.std(intervals) if len(intervals) > 1 else 0
        else:
            avg_days_between_visits = 30
            std_days_between_visits = 0
        
        # Calculate cancellation rate
        all_bookings = await db.bookings.find({
            "client_id": client_id,
            "tenant_id": tenant_id
        }).to_list(length=None)
        
        cancelled_count = sum(1 for b in all_bookings if b.get("status") == "cancelled")
        cancellation_rate = cancelled_count / len(all_bookings) if all_bookings else 0
        
        # Calculate no-show rate
        no_show_count = sum(1 for b in all_bookings if b.get("status") == "no_show")
        no_show_rate = no_show_count / len(all_bookings) if all_bookings else 0
        
        # Calculate recency score (0-1, higher is better)
        recency_score = max(0, 1 - (days_since_last_visit / 90))
        
        # Calculate frequency score (0-1, higher is better)
        frequency_score = min(1, total_visits / 10)
        
        # Calculate monetary score (0-1, higher is better)
        monetary_score = min(1, total_spent / 50000)  # Normalize to 50k
        
        return {
            "client_id": client_id,
            "client_name": client["name"],
            "total_visits": total_visits,
            "total_spent": total_spent,
            "avg_spend_per_visit": avg_spend_per_visit,
            "days_since_last_visit": days_since_last_visit,
            "avg_days_between_visits": avg_days_between_visits,
            "std_days_between_visits": std_days_between_visits,
            "cancellation_rate": cancellation_rate,
            "no_show_rate": no_show_rate,
            "recency_score": recency_score,
            "frequency_score": frequency_score,
            "monetary_score": monetary_score,
            "last_visit_date": last_visit.isoformat() if last_visit else None
        }
    
    except Exception as e:
        logger.error(f"Error calculating client features: {e}")
        return {"error": str(e)}


async def predict_churn_risk(client_id: str, tenant_id: str, db) -> Dict:
    """
    Predict churn risk for a client using simple rule-based model
    (Can be upgraded to ML model with more data)
    """
    try:
        # Get client features
        features = await calculate_client_features(client_id, tenant_id, db)
        
        if features.get("error"):
            return features
        
        # Simple rule-based churn prediction
        risk_score = 0
        risk_factors = []
        
        # Factor 1: Days since last visit
        days_since = features["days_since_last_visit"]
        avg_interval = features["avg_days_between_visits"]
        
        if days_since > avg_interval * 2:
            risk_score += 40
            risk_factors.append(f"Overdue by {days_since - avg_interval} days")
        elif days_since > avg_interval * 1.5:
            risk_score += 25
            risk_factors.append(f"Approaching overdue")
        
        # Factor 2: Cancellation rate
        if features["cancellation_rate"] > 0.3:
            risk_score += 20
            risk_factors.append(f"High cancellation rate ({features['cancellation_rate']:.1%})")
        elif features["cancellation_rate"] > 0.15:
            risk_score += 10
            risk_factors.append(f"Moderate cancellation rate")
        
        # Factor 3: No-show rate
        if features["no_show_rate"] > 0.2:
            risk_score += 15
            risk_factors.append(f"High no-show rate ({features['no_show_rate']:.1%})")
        
        # Factor 4: Low frequency
        if features["total_visits"] < 3 and days_since > 60:
            risk_score += 15
            risk_factors.append("Low visit frequency")
        
        # Factor 5: Declining engagement (irregular visits)
        if features["std_days_between_visits"] > 20:
            risk_score += 10
            risk_factors.append("Irregular visit pattern")
        
        # Determine risk level
        if risk_score >= 60:
            risk_level = "high"
            action = "immediate"
        elif risk_score >= 40:
            risk_level = "medium"
            action = "soon"
        elif risk_score >= 20:
            risk_level = "low"
            action = "monitor"
        else:
            risk_level = "minimal"
            action = "none"
        
        # Calculate expected return date
        expected_return_date = datetime.utcnow() + timedelta(days=int(avg_interval))
        
        return {
            "client_id": client_id,
            "client_name": features["client_name"],
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "recommended_action": action,
            "days_since_last_visit": days_since,
            "expected_return_date": expected_return_date.strftime("%Y-%m-%d"),
            "total_visits": features["total_visits"],
            "total_spent": features["total_spent"],
            "recency_score": features["recency_score"],
            "frequency_score": features["frequency_score"],
            "monetary_score": features["monetary_score"]
        }
    
    except Exception as e:
        logger.error(f"Error predicting churn risk: {e}")
        return {"error": str(e)}


async def get_at_risk_clients(tenant_id: str, db, min_risk_level: str = "low") -> List[Dict]:
    """
    Get all at-risk clients for a tenant
    """
    try:
        # Get all clients with at least one visit
        clients = await db.clients.find({
            "tenant_id": tenant_id,
            "total_visits": {"$gt": 0}
        }).to_list(length=None)
        
        at_risk_clients = []
        risk_level_order = {"minimal": 0, "low": 1, "medium": 2, "high": 3}
        min_risk_value = risk_level_order.get(min_risk_level, 1)
        
        for client in clients:
            client_id = str(client["_id"])
            
            # Get churn prediction
            prediction = await predict_churn_risk(client_id, tenant_id, db)
            
            if prediction.get("error"):
                continue
            
            # Filter by risk level
            risk_value = risk_level_order.get(prediction["risk_level"], 0)
            if risk_value >= min_risk_value:
                at_risk_clients.append({
                    "client_id": client_id,
                    "client_name": prediction["client_name"],
                    "client_phone": client["phone"],
                    "client_email": client.get("email"),
                    "risk_score": prediction["risk_score"],
                    "risk_level": prediction["risk_level"],
                    "risk_factors": prediction["risk_factors"],
                    "days_since_last_visit": prediction["days_since_last_visit"],
                    "expected_return_date": prediction["expected_return_date"],
                    "total_visits": prediction["total_visits"],
                    "total_spent": prediction["total_spent"]
                })
        
        # Sort by risk score (highest first)
        at_risk_clients.sort(key=lambda x: x["risk_score"], reverse=True)
        
        return at_risk_clients
    
    except Exception as e:
        logger.error(f"Error getting at-risk clients: {e}")
        return []
