"""
Tests for DDoS Protection Module

Tests rate limiting, pattern analysis, adaptive thresholds,
circuit breaker, and graceful degradation.
"""

import pytest
import time
from unittest.mock import Mock, MagicMock
import redis

from app.security.ddos_protection import (
    DDoSProtection,
    RateLimitConfig,
    RequestPattern,
    ThreatLevel,
    CircuitBreaker,
)


@pytest.fixture
def mock_redis():
    """Create mock Redis client"""
    return MagicMock(spec=redis.Redis)


@pytest.fixture
def ddos_protection(mock_redis):
    """Create DDoS protection instance"""
    config = RateLimitConfig(
        requests_per_second=10.0,
        burst_allowance=20,
        block_duration_seconds=300,
    )
    return DDoSProtection(mock_redis, config)


class TestRateLimiting:
    """Test rate limiting functionality"""

    def test_rate_limit_allows_normal_traffic(self, ddos_protection, mock_redis):
        """Test that normal traffic is allowed"""
        mock_redis.incr.return_value = 5
        mock_redis.exists.return_value = False

        allowed, reason = ddos_protection.check_rate_limit("192.168.1.1")

        assert allowed is True
        assert reason is None

    def test_rate_limit_blocks_excessive_traffic(self, ddos_protection, mock_redis):
        """Test that excessive traffic is blocked"""
        mock_redis.incr.return_value = 20  # Exceeds threshold of 10
        mock_redis.exists.return_value = False

        allowed, reason = ddos_protection.check_rate_limit("192.168.1.1")

        assert allowed is False
        assert "Rate limit exceeded" in reason

    def test_rate_limit_blocks_already_blocked_ip(self, ddos_protection, mock_redis):
        """Test that already blocked IPs are blocked"""
        mock_redis.exists.return_value = True

        allowed, reason = ddos_protection.check_rate_limit("192.168.1.1")

        assert allowed is False
        assert "temporarily blocked" in reason

    def test_rate_limit_trusted_ip_higher_threshold(self, ddos_protection, mock_redis):
        """Test that trusted IPs have higher threshold"""
        mock_redis.incr.return_value = 40  # Would exceed normal threshold
        mock_redis.exists.return_value = False

        allowed, reason = ddos_protection.check_rate_limit("192.168.1.1", is_trusted=True)

        # Should be allowed because trusted IP has 5x multiplier
        assert allowed is True

    def test_rate_limit_redis_failure_fails_open(self, ddos_protection, mock_redis):
        """Test that rate limiting fails open if Redis is down"""
        mock_redis.incr.side_effect = Exception("Redis connection failed")

        allowed, reason = ddos_protection.check_rate_limit("192.168.1.1")

        assert allowed is True  # Fail open


class TestPatternAnalysis:
    """Test request pattern analysis"""

    def test_detect_high_frequency_attack(self, ddos_protection):
        """Test detection of high frequency attacks"""
        # Create 20 requests in quick succession
        for i in range(20):
            pattern = RequestPattern(
                timestamp=time.time() + i * 0.01,
                ip_address="192.168.1.1",
                endpoint="/api/users",
                method="GET",
                response_time_ms=100,
                status_code=200,
                payload_size=1000,
            )
            ddos_protection.local_patterns["192.168.1.1"].append(pattern)

        # Analyze latest pattern
        latest_pattern = RequestPattern(
            timestamp=time.time() + 20,
            ip_address="192.168.1.1",
            endpoint="/api/users",
            method="GET",
            response_time_ms=100,
            status_code=200,
            payload_size=1000,
        )

        threat_level, threat_score = ddos_protection.analyze_request_pattern(latest_pattern)

        assert threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]
        assert threat_score > 20

    def test_detect_slowloris_attack(self, ddos_protection):
        """Test detection of slowloris attacks"""
        # Create requests with very high response times
        for i in range(5):
            pattern = RequestPattern(
                timestamp=time.time() + i * 1,
                ip_address="192.168.1.1",
                endpoint="/api/users",
                method="GET",
                response_time_ms=10000,  # 10 seconds
                status_code=200,
                payload_size=1000,
            )
            ddos_protection.local_patterns["192.168.1.1"].append(pattern)

        latest_pattern = RequestPattern(
            timestamp=time.time() + 5,
            ip_address="192.168.1.1",
            endpoint="/api/users",
            method="GET",
            response_time_ms=10000,
            status_code=200,
            payload_size=1000,
        )

        threat_level, threat_score = ddos_protection.analyze_request_pattern(latest_pattern)

        assert threat_level in [ThreatLevel.MEDIUM, ThreatLevel.HIGH]
        assert threat_score > 15

    def test_detect_payload_bomb(self, ddos_protection):
        """Test detection of payload bombs"""
        pattern = RequestPattern(
            timestamp=time.time(),
            ip_address="192.168.1.1",
            endpoint="/api/upload",
            method="POST",
            response_time_ms=100,
            status_code=413,
            payload_size=20 * 1024 * 1024,  # 20MB
        )

        threat_level, threat_score = ddos_protection.analyze_request_pattern(pattern)

        assert threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]
        assert threat_score >= 25

    def test_detect_scanning_behavior(self, ddos_protection):
        """Test detection of endpoint scanning"""
        # Create requests to many different endpoints
        for i in range(20):
            pattern = RequestPattern(
                timestamp=time.time() + i * 0.1,
                ip_address="192.168.1.1",
                endpoint=f"/api/endpoint{i}",
                method="GET",
                response_time_ms=100,
                status_code=404,
                payload_size=1000,
            )
            ddos_protection.local_patterns["192.168.1.1"].append(pattern)

        latest_pattern = RequestPattern(
            timestamp=time.time() + 20,
            ip_address="192.168.1.1",
            endpoint="/api/endpoint20",
            method="GET",
            response_time_ms=100,
            status_code=404,
            payload_size=1000,
        )

        threat_level, threat_score = ddos_protection.analyze_request_pattern(latest_pattern)

        assert threat_level in [ThreatLevel.MEDIUM, ThreatLevel.HIGH]
        assert threat_score > 10


class TestAdaptiveThresholds:
    """Test adaptive rate limiting thresholds"""

    def test_adaptive_threshold_low_threat(self, ddos_protection):
        """Test adaptive threshold for low threat"""
        ddos_protection.threat_scores["192.168.1.1"] = 10.0

        threshold = ddos_protection.get_adaptive_threshold("192.168.1.1")

        assert threshold == ddos_protection.config.requests_per_second

    def test_adaptive_threshold_medium_threat(self, ddos_protection):
        """Test adaptive threshold for medium threat"""
        ddos_protection.threat_scores["192.168.1.1"] = 35.0

        threshold = ddos_protection.get_adaptive_threshold("192.168.1.1")

        assert threshold == 10.0

    def test_adaptive_threshold_high_threat(self, ddos_protection):
        """Test adaptive threshold for high threat"""
        ddos_protection.threat_scores["192.168.1.1"] = 55.0

        threshold = ddos_protection.get_adaptive_threshold("192.168.1.1")

        assert threshold == 5.0

    def test_adaptive_threshold_critical_threat(self, ddos_protection):
        """Test adaptive threshold for critical threat"""
        ddos_protection.threat_scores["192.168.1.1"] = 75.0

        threshold = ddos_protection.get_adaptive_threshold("192.168.1.1")

        assert threshold == 1.0


class TestCircuitBreaker:
    """Test circuit breaker pattern"""

    def test_circuit_breaker_closed_initially(self):
        """Test that circuit breaker starts closed"""
        cb = CircuitBreaker("test_endpoint", failure_threshold=5)

        assert cb.state == CircuitBreaker.State.CLOSED
        assert not cb.is_open()

    def test_circuit_breaker_opens_on_failures(self):
        """Test that circuit breaker opens after threshold failures"""
        cb = CircuitBreaker("test_endpoint", failure_threshold=3)

        # Record 3 failures
        for _ in range(3):
            cb.record_request(False)

        assert cb.state == CircuitBreaker.State.OPEN
        assert cb.is_open()

    def test_circuit_breaker_half_open_after_timeout(self):
        """Test that circuit breaker transitions to half-open after timeout"""
        cb = CircuitBreaker("test_endpoint", failure_threshold=3, timeout_seconds=1)

        # Record 3 failures
        for _ in range(3):
            cb.record_request(False)

        assert cb.is_open()

        # Wait for timeout
        time.sleep(1.1)

        # Check again - should transition to half-open
        assert not cb.is_open()
        assert cb.state == CircuitBreaker.State.HALF_OPEN

    def test_circuit_breaker_closes_on_success(self):
        """Test that circuit breaker closes on success in half-open state"""
        cb = CircuitBreaker("test_endpoint", failure_threshold=3, timeout_seconds=1)

        # Record 3 failures
        for _ in range(3):
            cb.record_request(False)

        # Wait for timeout
        time.sleep(1.1)

        # Record success
        cb.record_request(True)

        assert cb.state == CircuitBreaker.State.CLOSED
        assert not cb.is_open()

    def test_circuit_breaker_reopens_on_failure_in_half_open(self):
        """Test that circuit breaker reopens on failure in half-open state"""
        cb = CircuitBreaker("test_endpoint", failure_threshold=3, timeout_seconds=1)

        # Record 3 failures
        for _ in range(3):
            cb.record_request(False)

        # Wait for timeout
        time.sleep(1.1)

        # Record failure in half-open state
        cb.record_request(False)

        assert cb.state == CircuitBreaker.State.OPEN


class TestCircuitBreakerRegistration:
    """Test circuit breaker registration and management"""

    def test_register_circuit_breaker(self, ddos_protection):
        """Test registering circuit breaker"""
        ddos_protection.register_circuit_breaker("/api/users")

        assert "/api/users" in ddos_protection.circuit_breakers

    def test_get_circuit_status(self, ddos_protection):
        """Test getting circuit breaker status"""
        ddos_protection.register_circuit_breaker("/api/users")

        status = ddos_protection.get_circuit_status("/api/users")

        assert status["endpoint"] == "/api/users"
        assert status["state"] == "closed"
        assert status["failure_count"] == 0

    def test_record_request_success(self, ddos_protection):
        """Test recording successful request"""
        ddos_protection.register_circuit_breaker("/api/users")

        ddos_protection.record_request("/api/users", True)

        status = ddos_protection.get_circuit_status("/api/users")
        assert status["success_count"] == 1

    def test_record_request_failure(self, ddos_protection):
        """Test recording failed request"""
        ddos_protection.register_circuit_breaker("/api/users")

        ddos_protection.record_request("/api/users", False)

        status = ddos_protection.get_circuit_status("/api/users")
        assert status["failure_count"] == 1


class TestGracefulDegradation:
    """Test graceful degradation under load"""

    def test_graceful_degradation_primary_success(self, ddos_protection):
        """Test graceful degradation when primary succeeds"""
        from app.security.ddos_protection import graceful_degradation

        def primary():
            return "primary_result"

        def fallback():
            return "fallback_result"

        result = graceful_degradation(primary, fallback)

        assert result == "primary_result"

    def test_graceful_degradation_fallback_on_failure(self, ddos_protection):
        """Test graceful degradation when primary fails"""
        from app.security.ddos_protection import graceful_degradation

        def primary():
            raise Exception("Primary failed")

        def fallback():
            return "fallback_result"

        result = graceful_degradation(primary, fallback)

        assert result == "fallback_result"

    def test_graceful_degradation_both_fail(self, ddos_protection):
        """Test graceful degradation when both fail"""
        from app.security.ddos_protection import graceful_degradation

        def primary():
            raise Exception("Primary failed")

        def fallback():
            raise Exception("Fallback failed")

        with pytest.raises(Exception):
            graceful_degradation(primary, fallback)
