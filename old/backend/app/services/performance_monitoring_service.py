import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime
from collections import deque
import asyncio

logger = logging.getLogger(__name__)


class PerformanceMonitoringService:
    """Monitors and optimizes voice assistant performance"""

    def __init__(self, max_queue_size: int = 100):
        """Initialize performance monitoring"""
        self.request_queue = asyncio.Queue(maxsize=max_queue_size)
        self.metrics = {
            "stt_latencies": deque(maxlen=100),
            "nlu_latencies": deque(maxlen=100),
            "tts_latencies": deque(maxlen=100),
            "action_latencies": deque(maxlen=100),
            "total_latencies": deque(maxlen=100),
            "concurrent_users": 0,
            "total_requests": 0,
            "failed_requests": 0
        }
        self.response_cache = {}
        self.tts_audio_cache = {}
        self.operation_timeouts = {
            "stt_timeout": 30,
            "nlu_timeout": 10,
            "tts_timeout": 15,
            "action_timeout": 20
        }

    async def queue_request(self, request_id: str, request_data: dict):
        """Queue voice request for processing"""
        try:
            await asyncio.wait_for(
                self.request_queue.put((request_id, request_data)),
                timeout=5
            )
            self.metrics["concurrent_users"] += 1
        except asyncio.TimeoutError:
            logger.error(f"Request queue full for {request_id}")
            raise

    async def dequeue_request(self):
        """Dequeue next request"""
        try:
            return await asyncio.wait_for(
                self.request_queue.get(),
                timeout=1
            )
        except asyncio.TimeoutError:
            return None

    def record_latency(self, operation: str, latency_ms: float):
        """Record operation latency"""
        if operation == "stt":
            self.metrics["stt_latencies"].append(latency_ms)
        elif operation == "nlu":
            self.metrics["nlu_latencies"].append(latency_ms)
        elif operation == "tts":
            self.metrics["tts_latencies"].append(latency_ms)
        elif operation == "action":
            self.metrics["action_latencies"].append(latency_ms)
        elif operation == "total":
            self.metrics["total_latencies"].append(latency_ms)

    def get_average_latency(self, operation: str) -> float:
        """Get average latency for operation"""
        latencies = self.metrics.get(f"{operation}_latencies", deque())
        if not latencies:
            return 0
        return sum(latencies) / len(latencies)

    def cache_response(self, key: str, response: str, ttl_seconds: int = 3600):
        """Cache common responses"""
        self.response_cache[key] = {
            "response": response,
            "cached_at": datetime.utcnow(),
            "ttl": ttl_seconds
        }

    def get_cached_response(self, key: str) -> Optional[str]:
        """Get cached response if valid"""
        if key not in self.response_cache:
            return None

        cached = self.response_cache[key]
        age = (datetime.utcnow() - cached["cached_at"]).total_seconds()

        if age > cached["ttl"]:
            del self.response_cache[key]
            return None

        return cached["response"]

    def cache_tts_audio(self, key: str, audio_data: bytes, ttl_seconds: int = 3600):
        """Cache TTS audio"""
        self.tts_audio_cache[key] = {
            "audio": audio_data,
            "cached_at": datetime.utcnow(),
            "ttl": ttl_seconds
        }

    def get_cached_tts_audio(self, key: str) -> Optional[bytes]:
        """Get cached TTS audio if valid"""
        if key not in self.tts_audio_cache:
            return None

        cached = self.tts_audio_cache[key]
        age = (datetime.utcnow() - cached["cached_at"]).total_seconds()

        if age > cached["ttl"]:
            del self.tts_audio_cache[key]
            return None

        return cached["audio"]

    def get_performance_metrics(self) -> dict:
        """Get current performance metrics"""
        return {
            "avg_stt_latency_ms": self.get_average_latency("stt"),
            "avg_nlu_latency_ms": self.get_average_latency("nlu"),
            "avg_tts_latency_ms": self.get_average_latency("tts"),
            "avg_action_latency_ms": self.get_average_latency("action"),
            "avg_total_latency_ms": self.get_average_latency("total"),
            "concurrent_users": self.metrics["concurrent_users"],
            "total_requests": self.metrics["total_requests"],
            "failed_requests": self.metrics["failed_requests"],
            "cache_size": len(self.response_cache),
            "tts_cache_size": len(self.tts_audio_cache)
        }

    def record_request_completion(self, success: bool):
        """Record request completion"""
        self.metrics["total_requests"] += 1
        if not success:
            self.metrics["failed_requests"] += 1
        self.metrics["concurrent_users"] = max(0, self.metrics["concurrent_users"] - 1)

    def get_timeout_config(self, operation: str) -> int:
        """Get timeout for operation"""
        return self.operation_timeouts.get(f"{operation}_timeout", 30)
