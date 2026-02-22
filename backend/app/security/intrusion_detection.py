"""
Intrusion Detection System

Provides anomaly detection, behavioral analysis, signature-based detection,
statistical analysis, and machine learning-ready framework.
"""

import logging
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import statistics
import redis

logger = logging.getLogger(__name__)


class AnomalyType(Enum):
    """Types of anomalies detected"""
    UNUSUAL_REQUEST_SIZE = "unusual_request_size"
    UNUSUAL_REQUEST_FREQUENCY = "unusual_request_frequency"
    UNUSUAL_REQUEST_PATTERN = "unusual_request_pattern"
    UNUSUAL_USER_BEHAVIOR = "unusual_user_behavior"
    UNUSUAL_TIMING = "unusual_timing"
    UNUSUAL_GEOLOCATION = "unusual_geolocation"
    SIGNATURE_MATCH = "signature_match"
    STATISTICAL_ANOMALY = "statistical_anomaly"


@dataclass
class RequestMetrics:
    """Request metrics for analysis"""
    timestamp: float
    user_id: Optional[str]
    ip_address: str
    endpoint: str
    method: str
    request_size: int
    response_time_ms: float
    status_code: int
    user_agent: str
    geolocation: Optional[str]


@dataclass
class UserBehavior:
    """User behavior profile"""
    user_id: str
    avg_requests_per_hour: float
    avg_request_size: float
    avg_response_time_ms: float
    common_endpoints: List[str]
    common_times: List[int]  # Hours of day
    common_locations: List[str]
    last_seen: float


class IntrusionDetection:
    """
    Intrusion detection system with anomaly detection, behavioral analysis,
    signature-based detection, and statistical analysis.
    """

    def __init__(self, redis_client: redis.Redis):
        """
        Initialize intrusion detection system.

        Args:
            redis_client: Redis client for storing behavior profiles
        """
        self.redis = redis_client
        self.user_behaviors: Dict[str, UserBehavior] = {}
        self.request_history: Dict[str, List[RequestMetrics]] = {}
        self.signatures = self._load_signatures()
        self.alerts: List[Dict] = []

    def _load_signatures(self) -> Dict[str, str]:
        """
        Load attack signatures for detection.

        Returns:
            Dictionary of signature patterns
        """
        return {
            "sql_injection": r"(\bUNION\b|\bSELECT\b|\bDROP\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b)",
            "xss_attack": r"(<script|javascript:|onerror=|onload=|<iframe)",
            "command_injection": r"(;\s*rm\s|-rf|bash|sh\s|exec|system)",
            "path_traversal": r"(\.\./|\.\.\\|%2e%2e)",
            "xxe_attack": r"(<!ENTITY|SYSTEM|PUBLIC)",
            "csrf_attack": r"(csrf|xsrf)",
        }

    def detect_anomalies(self, metrics: RequestMetrics) -> List[Tuple[AnomalyType, float]]:
        """
        Detect anomalies in request metrics.

        Args:
            metrics: Request metrics to analyze

        Returns:
            List of (anomaly_type, confidence_score) tuples
        """
        anomalies = []

        # Check for unusual request size
        size_anomaly = self._check_request_size_anomaly(metrics)
        if size_anomaly:
            anomalies.append(size_anomaly)

        # Check for unusual request frequency
        frequency_anomaly = self._check_request_frequency_anomaly(metrics)
        if frequency_anomaly:
            anomalies.append(frequency_anomaly)

        # Check for unusual request pattern
        pattern_anomaly = self._check_request_pattern_anomaly(metrics)
        if pattern_anomaly:
            anomalies.append(pattern_anomaly)

        # Check for unusual timing
        timing_anomaly = self._check_timing_anomaly(metrics)
        if timing_anomaly:
            anomalies.append(timing_anomaly)

        # Check for unusual geolocation
        geolocation_anomaly = self._check_geolocation_anomaly(metrics)
        if geolocation_anomaly:
            anomalies.append(geolocation_anomaly)

        # Check for signature matches
        signature_anomalies = self._check_signatures(metrics)
        anomalies.extend(signature_anomalies)

        # Check for statistical anomalies
        statistical_anomalies = self._check_statistical_anomalies(metrics)
        anomalies.extend(statistical_anomalies)

        return anomalies

    def _check_request_size_anomaly(self, metrics: RequestMetrics) -> Optional[Tuple[AnomalyType, float]]:
        """Check for unusual request sizes"""
        # Very large requests (potential payload bomb)
        if metrics.request_size > 10 * 1024 * 1024:  # 10MB
            return (AnomalyType.UNUSUAL_REQUEST_SIZE, 0.95)

        # Very small requests (potential scanning)
        if metrics.request_size < 10 and metrics.method in ["POST", "PUT"]:
            return (AnomalyType.UNUSUAL_REQUEST_SIZE, 0.7)

        return None

    def _check_request_frequency_anomaly(self, metrics: RequestMetrics) -> Optional[Tuple[AnomalyType, float]]:
        """Check for unusual request frequency"""
        if not metrics.user_id:
            return None

        # Get user behavior profile
        behavior = self.user_behaviors.get(metrics.user_id)
        if not behavior:
            return None

        # Check if current frequency is significantly higher than normal
        current_frequency = self._calculate_current_frequency(metrics.user_id)
        if current_frequency > behavior.avg_requests_per_hour * 3:
            confidence = min(0.95, current_frequency / (behavior.avg_requests_per_hour * 10))
            return (AnomalyType.UNUSUAL_REQUEST_FREQUENCY, confidence)

        return None

    def _check_request_pattern_anomaly(self, metrics: RequestMetrics) -> Optional[Tuple[AnomalyType, float]]:
        """Check for unusual request patterns"""
        if not metrics.user_id:
            return None

        behavior = self.user_behaviors.get(metrics.user_id)
        if not behavior:
            return None

        # Check if endpoint is unusual for this user
        if metrics.endpoint not in behavior.common_endpoints:
            # Accessing unusual endpoint
            return (AnomalyType.UNUSUAL_REQUEST_PATTERN, 0.6)

        return None

    def _check_timing_anomaly(self, metrics: RequestMetrics) -> Optional[Tuple[AnomalyType, float]]:
        """Check for unusual timing patterns"""
        if not metrics.user_id:
            return None

        behavior = self.user_behaviors.get(metrics.user_id)
        if not behavior:
            return None

        # Check if request is at unusual time
        current_hour = datetime.fromtimestamp(metrics.timestamp).hour
        if current_hour not in behavior.common_times:
            return (AnomalyType.UNUSUAL_TIMING, 0.7)

        return None

    def _check_geolocation_anomaly(self, metrics: RequestMetrics) -> Optional[Tuple[AnomalyType, float]]:
        """Check for unusual geolocation"""
        if not metrics.user_id or not metrics.geolocation:
            return None

        behavior = self.user_behaviors.get(metrics.user_id)
        if not behavior:
            return None

        # Check if geolocation is unusual
        if metrics.geolocation not in behavior.common_locations:
            return (AnomalyType.UNUSUAL_GEOLOCATION, 0.8)

        return None

    def _check_signatures(self, metrics: RequestMetrics) -> List[Tuple[AnomalyType, float]]:
        """Check for known attack signatures"""
        anomalies = []

        # Check endpoint for SQL injection patterns
        if any(pattern in metrics.endpoint.upper() for pattern in ["UNION", "SELECT", "DROP"]):
            anomalies.append((AnomalyType.SIGNATURE_MATCH, 0.95))

        # Check user agent for suspicious patterns
        if metrics.user_agent and any(bot in metrics.user_agent for bot in ["sqlmap", "nikto", "nmap"]):
            anomalies.append((AnomalyType.SIGNATURE_MATCH, 0.9))

        return anomalies

    def _check_statistical_anomalies(self, metrics: RequestMetrics) -> List[Tuple[AnomalyType, float]]:
        """Check for statistical anomalies"""
        anomalies = []

        # Check response time
        if metrics.response_time_ms > 30000:  # 30 seconds
            anomalies.append((AnomalyType.STATISTICAL_ANOMALY, 0.85))

        # Check for error responses
        if metrics.status_code >= 500:
            anomalies.append((AnomalyType.STATISTICAL_ANOMALY, 0.7))

        return anomalies

    def update_user_behavior(self, metrics: RequestMetrics):
        """
        Update user behavior profile based on request metrics.

        Args:
            metrics: Request metrics to incorporate
        """
        if not metrics.user_id:
            return

        if metrics.user_id not in self.user_behaviors:
            # Create new behavior profile
            self.user_behaviors[metrics.user_id] = UserBehavior(
                user_id=metrics.user_id,
                avg_requests_per_hour=1.0,
                avg_request_size=float(metrics.request_size),
                avg_response_time_ms=metrics.response_time_ms,
                common_endpoints=[metrics.endpoint],
                common_times=[datetime.fromtimestamp(metrics.timestamp).hour],
                common_locations=[metrics.geolocation or "unknown"],
                last_seen=metrics.timestamp
            )
        else:
            # Update existing profile
            behavior = self.user_behaviors[metrics.user_id]
            behavior.avg_request_size = (behavior.avg_request_size + metrics.request_size) / 2
            behavior.avg_response_time_ms = (behavior.avg_response_time_ms + metrics.response_time_ms) / 2
            behavior.last_seen = metrics.timestamp

            # Update common endpoints
            if metrics.endpoint not in behavior.common_endpoints:
                behavior.common_endpoints.append(metrics.endpoint)
            behavior.common_endpoints = behavior.common_endpoints[-10:]  # Keep last 10

            # Update common times
            current_hour = datetime.fromtimestamp(metrics.timestamp).hour
            if current_hour not in behavior.common_times:
                behavior.common_times.append(current_hour)
            behavior.common_times = sorted(behavior.common_times)[-10:]  # Keep last 10

            # Update common locations
            if metrics.geolocation and metrics.geolocation not in behavior.common_locations:
                behavior.common_locations.append(metrics.geolocation)
            behavior.common_locations = behavior.common_locations[-5:]  # Keep last 5

    def _calculate_current_frequency(self, user_id: str) -> float:
        """
        Calculate current request frequency for user.

        Args:
            user_id: User ID

        Returns:
            Requests per hour
        """
        if user_id not in self.request_history:
            return 0.0

        history = self.request_history[user_id]
        if not history:
            return 0.0

        # Count requests in last hour
        one_hour_ago = time.time() - 3600
        recent_requests = [r for r in history if r.timestamp > one_hour_ago]

        return len(recent_requests)

    def generate_alert(self, metrics: RequestMetrics, anomalies: List[Tuple[AnomalyType, float]]) -> Dict:
        """
        Generate alert for detected anomalies.

        Args:
            metrics: Request metrics
            anomalies: List of detected anomalies

        Returns:
            Alert dictionary
        """
        alert = {
            "timestamp": datetime.now().isoformat(),
            "user_id": metrics.user_id,
            "ip_address": metrics.ip_address,
            "endpoint": metrics.endpoint,
            "anomalies": [
                {
                    "type": anomaly_type.value,
                    "confidence": confidence
                }
                for anomaly_type, confidence in anomalies
            ],
            "severity": self._calculate_severity(anomalies)
        }

        self.alerts.append(alert)
        logger.warning(f"Intrusion detection alert: {alert}")

        return alert

    def _calculate_severity(self, anomalies: List[Tuple[AnomalyType, float]]) -> str:
        """
        Calculate alert severity based on anomalies.

        Args:
            anomalies: List of detected anomalies

        Returns:
            Severity level (low, medium, high, critical)
        """
        if not anomalies:
            return "low"

        max_confidence = max(confidence for _, confidence in anomalies)
        anomaly_count = len(anomalies)

        if max_confidence >= 0.9 and anomaly_count >= 2:
            return "critical"
        elif max_confidence >= 0.8 or anomaly_count >= 3:
            return "high"
        elif max_confidence >= 0.7:
            return "medium"
        else:
            return "low"

    def get_alerts(self, limit: int = 100) -> List[Dict]:
        """
        Get recent alerts.

        Args:
            limit: Maximum number of alerts to return

        Returns:
            List of alerts
        """
        return self.alerts[-limit:]
