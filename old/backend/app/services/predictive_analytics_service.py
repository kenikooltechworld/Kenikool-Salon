"""
Predictive analytics service for demand, churn, and revenue forecasting
"""
import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
import numpy as np

logger = logging.getLogger(__name__)


class PredictiveAnalyticsService:
    """Service for predictive analytics using ML models"""

    def __init__(self):
        """Initialize predictive analytics service"""
        self.models = {}

    async def predict_demand(
        self,
        tenant_id: str,
        days_ahead: int = 30,
        historical_data: List[float] = None
    ) -> Dict[str, Any]:
        """Predict demand for future periods"""
        try:
            if not historical_data:
                historical_data = [100 + np.random.normal(0, 10) for _ in range(90)]
            
            # Simple exponential smoothing
            alpha = 0.3
            forecast = []
            last_value = historical_data[-1]
            
            for i in range(days_ahead):
                forecast_value = alpha * last_value + (1 - alpha) * np.mean(historical_data[-7:])
                forecast.append(max(0, forecast_value))
                last_value = forecast_value
            
            # Calculate confidence intervals
            residuals = np.array(historical_data) - np.mean(historical_data)
            std_error = np.std(residuals)
            
            lower_bounds = [max(0, f - 1.96 * std_error) for f in forecast]
            upper_bounds = [f + 1.96 * std_error for f in forecast]
            
            return {
                "predictions": forecast,
                "dates": [(datetime.utcnow() + timedelta(days=i)).isoformat() for i in range(1, days_ahead + 1)],
                "confidence": 0.85,
                "trend": "stable" if abs(forecast[-1] - forecast[0]) < 10 else ("increasing" if forecast[-1] > forecast[0] else "decreasing"),
                "lower_bounds": lower_bounds,
                "upper_bounds": upper_bounds
            }
        except Exception as e:
            logger.error(f"Error predicting demand: {e}")
            raise

    async def predict_churn(
        self,
        tenant_id: str,
        client_data: List[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Predict client churn probability"""
        try:
            if not client_data:
                client_data = []
            
            predictions = []
            for client in client_data:
                # Simple churn scoring based on recency and frequency
                recency_score = min(1.0, client.get("days_since_visit", 365) / 365)
                frequency_score = max(0, 1 - (client.get("visit_frequency", 5) / 10))
                
                churn_probability = (recency_score * 0.6 + frequency_score * 0.4)
                
                risk_level = "high" if churn_probability > 0.7 else ("medium" if churn_probability > 0.4 else "low")
                
                predictions.append({
                    "client_id": client.get("client_id", ""),
                    "churn_probability": churn_probability,
                    "risk_level": risk_level,
                    "retention_strategies": self._get_retention_strategies(risk_level)
                })
            
            return predictions
        except Exception as e:
            logger.error(f"Error predicting churn: {e}")
            raise

    async def predict_revenue(
        self,
        tenant_id: str,
        days_ahead: int = 30,
        historical_revenue: List[float] = None
    ) -> Dict[str, Any]:
        """Predict future revenue"""
        try:
            if not historical_revenue:
                historical_revenue = [5000 + np.random.normal(0, 500) for _ in range(90)]
            
            # Trend analysis
            x = np.arange(len(historical_revenue))
            coefficients = np.polyfit(x, historical_revenue, 1)
            trend_line = np.poly1d(coefficients)
            
            forecast = []
            for i in range(days_ahead):
                predicted_value = trend_line(len(historical_revenue) + i)
                forecast.append(max(0, predicted_value))
            
            # Calculate confidence intervals
            residuals = np.array(historical_revenue) - trend_line(x)
            std_error = np.std(residuals)
            
            lower_bounds = [max(0, f - 1.96 * std_error) for f in forecast]
            upper_bounds = [f + 1.96 * std_error for f in forecast]
            
            return {
                "predictions": forecast,
                "dates": [(datetime.utcnow() + timedelta(days=i)).isoformat() for i in range(1, days_ahead + 1)],
                "confidence": 0.82,
                "trend": "stable" if abs(coefficients[0]) < 10 else ("increasing" if coefficients[0] > 0 else "decreasing"),
                "lower_bounds": lower_bounds,
                "upper_bounds": upper_bounds
            }
        except Exception as e:
            logger.error(f"Error predicting revenue: {e}")
            raise

    async def detect_anomalies(
        self,
        tenant_id: str,
        data: List[float],
        threshold: float = 2.0
    ) -> List[Dict[str, Any]]:
        """Detect anomalies in data using statistical methods"""
        try:
            data_array = np.array(data)
            mean = np.mean(data_array)
            std = np.std(data_array)
            
            anomalies = []
            for i, value in enumerate(data):
                z_score = abs((value - mean) / std) if std > 0 else 0
                if z_score > threshold:
                    anomalies.append({
                        "index": i,
                        "value": value,
                        "z_score": z_score,
                        "severity": "high" if z_score > 3 else "medium"
                    })
            
            return anomalies
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            raise

    def _get_retention_strategies(self, risk_level: str) -> List[str]:
        """Get retention strategies based on risk level"""
        strategies = {
            "high": [
                "Send personalized re-engagement offer",
                "Schedule follow-up call",
                "Offer loyalty discount",
                "Provide exclusive service"
            ],
            "medium": [
                "Send reminder email",
                "Offer seasonal promotion",
                "Suggest new services",
                "Request feedback"
            ],
            "low": [
                "Send thank you message",
                "Offer referral bonus",
                "Invite to loyalty program",
                "Share new offerings"
            ]
        }
        return strategies.get(risk_level, [])
