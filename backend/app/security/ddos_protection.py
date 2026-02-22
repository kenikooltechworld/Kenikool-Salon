"""
DDoS Protection Module

Provides rate limiting, request pattern analysis, adaptive rate limiting,
circuit breaker pattern, and graceful degradation under load.
"""

import time
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, deque
import redis
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Threat level classification"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    requests_per_second: float = 10.0
    burst_allowance: int = 20
    block_duration_seconds: int = 300
    adaptive_threshold_multiplier: float = 2.0
    trusted_ip_multiplier: float = 5.0


@dataclass
class RequestPattern:
    """Request pattern for analysis"""
    timestamp: float
    ip_address: str
    endpoint: str
    method: str
    response_time_ms: float
    status_code: int
    payload_size: int


class DDoSProtection:
    """
    DDoS protection system with rate limiting, pattern analysis,
    adaptive thresholds, and circuit breaker pattern.
    """

    def __init__(self, redis_client: redis.Redis, config: Optional[RateLimitConfig] = None):
        """
        Initialize DDoS protection system.

        Args:
            redis_client: Redis client for distributed rate limiting
            config: Rate limit configuration
        """
        self.redis = redis_client
        self.config = config or RateLimitConfig()
        self.local_patterns: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.circuit_breakers: Dict[str, 'CircuitBreaker'] = {}
        self.threat_scores: Dict[str, float] = {}

    def check_rate_limit(self, ip_address: str, is_trusted: bool = False) -> Tuple[bool, Optional[str]]:
        """
        Check if IP address has exceeded rate limit.

        Args:
            ip_address: Client IP address
            is_trusted: Whether IP is in trusted list

        Returns:
            Tuple of (allowed: bool, reason: Optional[str])
        """
        try:
            # Check if IP is blocked
            block_key = f"ddos:blocked:{ip_address}"
            if self.redis.exists(block_key):
                return False, "IP address is temporarily blocked"

            # Get current request count
            rate_key = f"ddos:rate:{ip_address}"
            current_count = self.redis.incr(rate_key)

            # Set expiration on first request
            if current_count == 1:
                self.redis.expire(rate_key, 1)

            # Calculate threshold based on IP reputation
            threshold = self.config.requests_per_second
            if is_trusted:
                threshold *= self.config.trusted_ip_multiplier

            # Check if limit exceeded
            if current_count > threshold:
                # Block IP
                self.redis.setex(block_key, self.config.block_duration_seconds, "1")
                logger.warning(f"IP {ip_address} blocked for exceeding rate limit")
                return False, "Rate limit exceeded"

            return True, None

        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            # Fail open - allow request if Redis is down
            return True, None

    def analyze_request_pattern(self, pattern: RequestPattern) -> Tuple[ThreatLevel, float]:
        """
        Analyze request pattern for suspicious activity.

        Args:
            pattern: Request pattern to analyze

        Returns:
            Tuple of (threat_level: ThreatLevel, threat_score: float)
        """
        threat_score = 0.0
        ip_patterns = self.local_patterns[pattern.ip_address]
        ip_patterns.append(pattern)

        # Analyze request frequency
        if len(ip_patterns) > 10:
            recent_patterns = list(ip_patterns)[-10:]
            time_span = recent_patterns[-1].timestamp - recent_patterns[0].timestamp
            if time_span > 0:
                frequency = len(recent_patterns) / time_span
                if frequency > self.config.requests_per_second * 2:
                    threat_score += 20.0

        # Analyze response times (potential slowloris attack)
        if len(ip_patterns) > 5:
            recent_patterns = list(ip_patterns)[-5:]
            avg_response_time = sum(p.response_time_ms for p in recent_patterns) / len(recent_patterns)
            if avg_response_time > 5000:  # 5 seconds
                threat_score += 15.0

        # Analyze payload sizes (potential payload bomb)
        if pattern.payload_size > 10 * 1024 * 1024:  # 10MB
            threat_score += 25.0

        # Analyze error rates
        if len(ip_patterns) > 10:
            recent_patterns = list(ip_patterns)[-10:]
            error_count = sum(1 for p in recent_patterns if p.status_code >= 400)
            error_rate = error_count / len(recent_patterns)
            if error_rate > 0.5:
                threat_score += 15.0

        # Analyze endpoint diversity (scanning behavior)
        if len(ip_patterns) > 20:
            recent_patterns = list(ip_patterns)[-20:]
            unique_endpoints = len(set(p.endpoint for p in recent_patterns))
            if unique_endpoints > 15:
                threat_score += 10.0

        # Classify threat level
        if threat_score >= 70:
            threat_level = ThreatLevel.CRITICAL
        elif threat_score >= 50:
            threat_level = ThreatLevel.HIGH
        elif threat_score >= 30:
            threat_level = ThreatLevel.MEDIUM
        else:
            threat_level = ThreatLevel.LOW

        self.threat_scores[pattern.ip_address] = threat_score
        return threat_level, threat_score

    def get_adaptive_threshold(self, ip_address: str) -> float:
        """
        Get adaptive rate limit threshold based on IP reputation.

        Args:
            ip_address: Client IP address

        Returns:
            Adaptive threshold (requests per second)
        """
        threat_score = self.threat_scores.get(ip_address, 0.0)

        if threat_score >= 70:
            # Critical threat - reduce to 1 request per second
            return 1.0
        elif threat_score >= 50:
            # High threat - reduce to 5 requests per second
            return 5.0
        elif threat_score >= 30:
            # Medium threat - reduce to 10 requests per second
            return 10.0
        else:
            # Low threat - normal threshold
            return self.config.requests_per_second

    def register_circuit_breaker(self, endpoint: str, failure_threshold: int = 5, timeout_seconds: int = 60):
        """
        Register circuit breaker for endpoint.

        Args:
            endpoint: API endpoint path
            failure_threshold: Number of failures before opening circuit
            timeout_seconds: Timeout before attempting to close circuit
        """
        self.circuit_breakers[endpoint] = CircuitBreaker(
            endpoint=endpoint,
            failure_threshold=failure_threshold,
            timeout_seconds=timeout_seconds
        )

    def record_request(self, endpoint: str, success: bool):
        """
        Record request result for circuit breaker.

        Args:
            endpoint: API endpoint path
            success: Whether request succeeded
        """
        if endpoint in self.circuit_breakers:
            self.circuit_breakers[endpoint].record_request(success)

    def is_circuit_open(self, endpoint: str) -> bool:
        """
        Check if circuit breaker is open for endpoint.

        Args:
            endpoint: API endpoint path

        Returns:
            True if circuit is open (endpoint unavailable)
        """
        if endpoint in self.circuit_breakers:
            return self.circuit_breakers[endpoint].is_open()
        return False

    def get_circuit_status(self, endpoint: str) -> Dict:
        """
        Get circuit breaker status for endpoint.

        Args:
            endpoint: API endpoint path

        Returns:
            Circuit breaker status dictionary
        """
        if endpoint in self.circuit_breakers:
            cb = self.circuit_breakers[endpoint]
            return {
                "endpoint": endpoint,
                "state": cb.state.value,
                "failure_count": cb.failure_count,
                "success_count": cb.success_count,
                "last_failure_time": cb.last_failure_time
            }
        return {}


class CircuitBreaker:
    """
    Circuit breaker pattern implementation for handling overloaded endpoints.
    """

    class State(Enum):
        CLOSED = "closed"
        OPEN = "open"
        HALF_OPEN = "half_open"

    def __init__(self, endpoint: str, failure_threshold: int = 5, timeout_seconds: int = 60):
        """
        Initialize circuit breaker.

        Args:
            endpoint: API endpoint path
            failure_threshold: Number of failures before opening circuit
            timeout_seconds: Timeout before attempting to close circuit
        """
        self.endpoint = endpoint
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.state = self.State.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.opened_at: Optional[float] = None

    def record_request(self, success: bool):
        """
        Record request result.

        Args:
            success: Whether request succeeded
        """
        if success:
            self.success_count += 1
            if self.state == self.State.HALF_OPEN:
                # Transition to closed
                self.state = self.State.CLOSED
                self.failure_count = 0
                logger.info(f"Circuit breaker for {self.endpoint} closed")
        else:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = self.State.OPEN
                self.opened_at = time.time()
                logger.warning(f"Circuit breaker for {self.endpoint} opened")

    def is_open(self) -> bool:
        """
        Check if circuit is open.

        Returns:
            True if circuit is open
        """
        if self.state == self.State.OPEN:
            # Check if timeout has elapsed
            if self.opened_at and time.time() - self.opened_at > self.timeout_seconds:
                self.state = self.State.HALF_OPEN
                self.failure_count = 0
                logger.info(f"Circuit breaker for {self.endpoint} half-open")
                return False
            return True
        return False


def graceful_degradation(primary_func, fallback_func, *args, **kwargs):
    """
    Execute primary function with fallback on failure.

    Args:
        primary_func: Primary function to execute
        fallback_func: Fallback function if primary fails
        *args: Arguments to pass to functions
        **kwargs: Keyword arguments to pass to functions

    Returns:
        Result from primary or fallback function
    """
    try:
        return primary_func(*args, **kwargs)
    except Exception as e:
        logger.warning(f"Primary function failed: {e}, using fallback")
        try:
            return fallback_func(*args, **kwargs)
        except Exception as fallback_error:
            logger.error(f"Fallback function also failed: {fallback_error}")
            raise
