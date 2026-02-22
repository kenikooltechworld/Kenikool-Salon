"""
Voice Assistant Performance Optimization and Monitoring
"""

import logging
import time
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import deque
from functools import wraps
import redis.asyncio as redis
from app.config import settings

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitors voice assistant performance metrics"""
    
    def __init__(self):
        """Initialize performance monitor"""
        self.metrics = {
            'stt_latency': deque(maxlen=100),
            'nlu_latency': deque(maxlen=100),
            'action_latency': deque(maxlen=100),
            'tts_latency': deque(maxlen=100),
            'total_latency': deque(maxlen=100),
            'request_count': 0,
            'error_count': 0,
            'success_count': 0
        }
        self.start_time = datetime.utcnow()
        logger.info("Performance monitor initialized")
    
    def record_stt_latency(self, latency: float):
        """Record STT latency"""
        self.metrics['stt_latency'].append(latency)
        logger.debug(f"STT latency: {latency:.3f}s")
    
    def record_nlu_latency(self, latency: float):
        """Record NLU latency"""
        self.metrics['nlu_latency'].append(latency)
        logger.debug(f"NLU latency: {latency:.3f}s")
    
    def record_action_latency(self, latency: float):
        """Record action execution latency"""
        self.metrics['action_latency'].append(latency)
        logger.debug(f"Action latency: {latency:.3f}s")
    
    def record_tts_latency(self, latency: float):
        """Record TTS latency"""
        self.metrics['tts_latency'].append(latency)
        logger.debug(f"TTS latency: {latency:.3f}s")
    
    def record_total_latency(self, latency: float):
        """Record total pipeline latency"""
        self.metrics['total_latency'].append(latency)
        self.metrics['request_count'] += 1
        logger.info(f"Total latency: {latency:.3f}s")
    
    def record_success(self):
        """Record successful request"""
        self.metrics['success_count'] += 1
    
    def record_error(self):
        """Record failed request"""
        self.metrics['error_count'] += 1
    
    def get_average_latency(self, metric: str) -> float:
        """Get average latency for metric"""
        values = self.metrics.get(metric, [])
        return sum(values) / len(values) if values else 0.0
    
    def get_p95_latency(self, metric: str) -> float:
        """Get 95th percentile latency"""
        values = sorted(self.metrics.get(metric, []))
        if not values:
            return 0.0
        index = int(len(values) * 0.95)
        return values[index] if index < len(values) else values[-1]
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        
        return {
            'uptime_seconds': uptime,
            'total_requests': self.metrics['request_count'],
            'successful_requests': self.metrics['success_count'],
            'failed_requests': self.metrics['error_count'],
            'success_rate': (
                self.metrics['success_count'] / self.metrics['request_count']
                if self.metrics['request_count'] > 0 else 0.0
            ),
            'average_latencies': {
                'stt': self.get_average_latency('stt_latency'),
                'nlu': self.get_average_latency('nlu_latency'),
                'action': self.get_average_latency('action_latency'),
                'tts': self.get_average_latency('tts_latency'),
                'total': self.get_average_latency('total_latency')
            },
            'p95_latencies': {
                'stt': self.get_p95_latency('stt_latency'),
                'nlu': self.get_p95_latency('nlu_latency'),
                'action': self.get_p95_latency('action_latency'),
                'tts': self.get_p95_latency('tts_latency'),
                'total': self.get_p95_latency('total_latency')
            }
        }


class ResponseCache:
    """Caches common responses for faster delivery"""
    
    def __init__(self, redis_url: Optional[str] = None):
        """Initialize response cache"""
        self.redis_url = redis_url or settings.REDIS_URL
        self.redis_client: Optional[redis.Redis] = None
        self.cache_ttl = 3600  # 1 hour
        logger.info("Response cache initialized")
    
    async def connect(self):
        """Connect to Redis"""
        if self.redis_client is None:
            self.redis_client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
    
    async def get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached response
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached response or None
        """
        try:
            await self.connect()
            
            data = await self.redis_client.get(f"voice_cache:{cache_key}")
            if data:
                logger.debug(f"Cache hit: {cache_key}")
                import json
                return json.loads(data)
            
            logger.debug(f"Cache miss: {cache_key}")
            return None
            
        except Exception as e:
            logger.error(f"Cache get failed: {e}")
            return None
    
    async def cache_response(self, cache_key: str, response: Dict[str, Any]):
        """
        Cache response
        
        Args:
            cache_key: Cache key
            response: Response to cache
        """
        try:
            await self.connect()
            
            import json
            data = json.dumps(response)
            
            await self.redis_client.setex(
                f"voice_cache:{cache_key}",
                self.cache_ttl,
                data
            )
            
            logger.debug(f"Cached response: {cache_key}")
            
        except Exception as e:
            logger.error(f"Cache set failed: {e}")
    
    @staticmethod
    def generate_cache_key(intent: str, entities: Dict[str, Any], language: str) -> str:
        """Generate cache key from request parameters"""
        import hashlib
        import json
        
        # Create deterministic key
        data = {
            'intent': intent,
            'entities': sorted(entities.items()),
            'language': language
        }
        key_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()


class RequestQueue:
    """Manages request queuing for concurrent users"""
    
    def __init__(self, max_concurrent: int = 10):
        """
        Initialize request queue
        
        Args:
            max_concurrent: Maximum concurrent requests
        """
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.queue_size = 0
        self.max_queue_size = 50
        logger.info(f"Request queue initialized (max concurrent: {max_concurrent})")
    
    async def acquire(self) -> bool:
        """
        Acquire slot in queue
        
        Returns:
            True if acquired, False if queue full
        """
        if self.queue_size >= self.max_queue_size:
            logger.warning("Request queue full")
            return False
        
        self.queue_size += 1
        await self.semaphore.acquire()
        return True
    
    def release(self):
        """Release slot in queue"""
        self.semaphore.release()
        self.queue_size = max(0, self.queue_size - 1)
    
    async def __aenter__(self):
        """Async context manager entry"""
        success = await self.acquire()
        if not success:
            raise Exception("Request queue full")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        self.release()


class TimeoutHandler:
    """Handles operation timeouts"""
    
    DEFAULT_TIMEOUTS = {
        'stt': 5.0,
        'nlu': 3.0,
        'action': 10.0,
        'tts': 5.0,
        'total': 30.0
    }
    
    @staticmethod
    async def with_timeout(coro, timeout: float, operation: str):
        """
        Execute coroutine with timeout
        
        Args:
            coro: Coroutine to execute
            timeout: Timeout in seconds
            operation: Operation name for logging
            
        Returns:
            Coroutine result
            
        Raises:
            asyncio.TimeoutError: If operation times out
        """
        try:
            result = await asyncio.wait_for(coro, timeout=timeout)
            return result
        except asyncio.TimeoutError:
            logger.error(f"Operation timeout: {operation} ({timeout}s)")
            raise
    
    @classmethod
    def get_timeout(cls, operation: str) -> float:
        """Get timeout for operation"""
        return cls.DEFAULT_TIMEOUTS.get(operation, 10.0)


def measure_performance(operation: str):
    """
    Decorator to measure operation performance
    
    Args:
        operation: Operation name
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                latency = time.time() - start_time
                logger.info(f"{operation} completed in {latency:.3f}s")
                return result
            except Exception as e:
                latency = time.time() - start_time
                logger.error(f"{operation} failed after {latency:.3f}s: {e}")
                raise
        return wrapper
    return decorator


class ResourceMonitor:
    """Monitors Docker container resources"""
    
    @staticmethod
    async def check_container_resources(container_name: str) -> Dict[str, Any]:
        """
        Check container resource usage
        
        Args:
            container_name: Container name
            
        Returns:
            Resource usage metrics
        """
        # In production, this would query Docker API
        return {
            'container': container_name,
            'cpu_percent': 0.0,
            'memory_mb': 0.0,
            'status': 'running'
        }
    
    @staticmethod
    async def get_all_container_stats() -> List[Dict[str, Any]]:
        """Get stats for all voice containers"""
        containers = ['whisper', 'kimi', 'qwen', 'coqui', 'deepseek']
        stats = []
        
        for container in containers:
            stat = await ResourceMonitor.check_container_resources(container)
            stats.append(stat)
        
        return stats


# Global instances
performance_monitor = PerformanceMonitor()
response_cache = ResponseCache()
request_queue = RequestQueue(max_concurrent=10)
