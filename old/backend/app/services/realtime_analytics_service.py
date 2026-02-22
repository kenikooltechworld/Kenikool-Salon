"""
Real-time analytics service for live metrics and WebSocket streaming
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
import json

logger = logging.getLogger(__name__)


class RealTimeAnalyticsService:
    """Service for real-time analytics and WebSocket streaming"""

    def __init__(self):
        """Initialize real-time analytics service"""
        self.active_connections: Dict[str, List] = {}
        self.metrics_cache: Dict[str, Any] = {}
        self.alert_thresholds: Dict[str, float] = {
            "revenue_per_hour": 500,
            "bookings_per_hour": 5,
            "staff_utilization": 0.9
        }

    async def get_current_metrics(
        self,
        tenant_id: str
    ) -> Dict[str, Any]:
        """Get current real-time metrics"""
        try:
            metrics = [
                {
                    "metric_name": "active_bookings",
                    "current_value": 12,
                    "previous_value": 10,
                    "change_percentage": 20.0,
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "normal"
                },
                {
                    "metric_name": "current_revenue",
                    "current_value": 2500,
                    "previous_value": 2300,
                    "change_percentage": 8.7,
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "normal"
                },
                {
                    "metric_name": "staff_utilization",
                    "current_value": 0.85,
                    "previous_value": 0.80,
                    "change_percentage": 6.25,
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "normal"
                },
                {
                    "metric_name": "queue_length",
                    "current_value": 3,
                    "previous_value": 2,
                    "change_percentage": 50.0,
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "warning"
                }
            ]
            
            return {
                "metrics": metrics,
                "active_bookings": 12,
                "current_revenue": 2500,
                "staff_utilization": 0.85,
                "queue_length": 3,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting current metrics: {e}")
            raise

    async def stream_metrics(
        self,
        tenant_id: str,
        websocket_id: str
    ) -> None:
        """Stream metrics via WebSocket"""
        try:
            if tenant_id not in self.active_connections:
                self.active_connections[tenant_id] = []
            
            self.active_connections[tenant_id].append(websocket_id)
            
            # Simulate streaming metrics
            while True:
                metrics = await self.get_current_metrics(tenant_id)
                yield json.dumps(metrics)
                await asyncio.sleep(5)  # Update every 5 seconds
        except Exception as e:
            logger.error(f"Error streaming metrics: {e}")
            if tenant_id in self.active_connections:
                self.active_connections[tenant_id].remove(websocket_id)
            raise

    async def check_alert_thresholds(
        self,
        tenant_id: str,
        metrics: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Check if metrics exceed alert thresholds"""
        try:
            alerts = []
            
            for metric_name, value in metrics.items():
                if metric_name in self.alert_thresholds:
                    threshold = self.alert_thresholds[metric_name]
                    
                    if value > threshold:
                        alerts.append({
                            "metric_name": metric_name,
                            "current_value": value,
                            "threshold": threshold,
                            "severity": "high" if value > threshold * 1.5 else "medium",
                            "timestamp": datetime.utcnow().isoformat(),
                            "message": f"{metric_name} exceeded threshold: {value} > {threshold}"
                        })
            
            return alerts
        except Exception as e:
            logger.error(f"Error checking alert thresholds: {e}")
            raise

    async def broadcast_alert(
        self,
        tenant_id: str,
        alert: Dict[str, Any]
    ) -> None:
        """Broadcast alert to all connected clients"""
        try:
            if tenant_id in self.active_connections:
                for websocket_id in self.active_connections[tenant_id]:
                    # In a real implementation, send to WebSocket
                    logger.info(f"Broadcasting alert to {websocket_id}: {alert}")
        except Exception as e:
            logger.error(f"Error broadcasting alert: {e}")

    def set_alert_threshold(
        self,
        metric_name: str,
        threshold: float
    ) -> None:
        """Set alert threshold for a metric"""
        self.alert_thresholds[metric_name] = threshold
        logger.info(f"Alert threshold set for {metric_name}: {threshold}")

    def get_alert_thresholds(self) -> Dict[str, float]:
        """Get all alert thresholds"""
        return self.alert_thresholds.copy()
