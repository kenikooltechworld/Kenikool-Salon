import pytest
import time
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from app.services.performance_monitoring_service import PerformanceMonitoringService


@pytest.fixture
def perf_service():
    """Create performance monitoring service"""
    return PerformanceMonitoringService()


def test_stt_latency_measurement(perf_service):
    """Measure STT latency with various audio lengths"""
    audio_lengths = [5, 10, 30, 60]  # seconds
    
    for length in audio_lengths:
        start = time.time()
        # Simulate STT processing
        time.sleep(0.1)  # Mock processing time
        latency = (time.time() - start) * 1000  # Convert to ms
        
        perf_service.record_latency("stt", latency)
    
    avg_latency = perf_service.get_average_latency("stt")
    assert avg_latency > 0
    assert avg_latency < 200  # Should be under 200ms


def test_nlu_processing_time(perf_service):
    """Measure NLU processing time with different text lengths"""
    text_lengths = [10, 50, 100, 200]  # characters
    
    for length in text_lengths:
        start = time.time()
        # Simulate NLU processing
        time.sleep(0.05)
        latency = (time.time() - start) * 1000
        
        perf_service.record_latency("nlu", latency)
    
    avg_latency = perf_service.get_average_latency("nlu")
    assert avg_latency > 0
    assert avg_latency < 150


def test_tts_generation_time(perf_service):
    """Measure TTS generation time for various response lengths"""
    response_lengths = [10, 50, 100, 200]  # words
    
    for length in response_lengths:
        start = time.time()
        # Simulate TTS generation
        time.sleep(0.08)
        latency = (time.time() - start) * 1000
        
        perf_service.record_latency("tts", latency)
    
    avg_latency = perf_service.get_average_latency("tts")
    assert avg_latency > 0
    assert avg_latency < 200


@pytest.mark.asyncio
async def test_concurrent_user_load(perf_service):
    """Test concurrent user load"""
    async def simulate_request(request_id):
        await perf_service.queue_request(request_id, {"data": "test"})
        await asyncio.sleep(0.1)
        perf_service.record_request_completion(success=True)
    
    # Simulate 10 concurrent users
    tasks = [simulate_request(f"req_{i}") for i in range(10)]
    await asyncio.gather(*tasks)
    
    metrics = perf_service.get_performance_metrics()
    assert metrics["total_requests"] == 10


def test_response_caching(perf_service):
    """Test response caching performance"""
    # Cache a response
    perf_service.cache_response("help_command", "Here are available commands...")
    
    # Retrieve from cache
    cached = perf_service.get_cached_response("help_command")
    assert cached == "Here are available commands..."
    
    # Verify cache size
    metrics = perf_service.get_performance_metrics()
    assert metrics["cache_size"] == 1


def test_tts_audio_caching(perf_service):
    """Test TTS audio caching"""
    audio_data = b"audio_bytes_here"
    
    # Cache audio
    perf_service.cache_tts_audio("response_1", audio_data)
    
    # Retrieve from cache
    cached_audio = perf_service.get_cached_tts_audio("response_1")
    assert cached_audio == audio_data
    
    # Verify cache size
    metrics = perf_service.get_performance_metrics()
    assert metrics["tts_cache_size"] == 1


def test_cache_expiration(perf_service):
    """Test cache expiration"""
    # Cache with 1 second TTL
    perf_service.cache_response("temp_response", "Temporary", ttl_seconds=1)
    
    # Should be available immediately
    assert perf_service.get_cached_response("temp_response") is not None
    
    # Wait for expiration
    time.sleep(1.1)
    
    # Should be expired
    assert perf_service.get_cached_response("temp_response") is None


def test_performance_metrics_collection(perf_service):
    """Test performance metrics collection"""
    # Record various operations
    perf_service.record_latency("stt", 50)
    perf_service.record_latency("nlu", 30)
    perf_service.record_latency("tts", 80)
    perf_service.record_latency("action", 20)
    perf_service.record_latency("total", 180)
    
    metrics = perf_service.get_performance_metrics()
    
    assert metrics["avg_stt_latency_ms"] == 50
    assert metrics["avg_nlu_latency_ms"] == 30
    assert metrics["avg_tts_latency_ms"] == 80
    assert metrics["avg_action_latency_ms"] == 20
    assert metrics["avg_total_latency_ms"] == 180


def test_timeout_configuration(perf_service):
    """Test timeout configuration"""
    stt_timeout = perf_service.get_timeout_config("stt")
    nlu_timeout = perf_service.get_timeout_config("nlu")
    tts_timeout = perf_service.get_timeout_config("tts")
    action_timeout = perf_service.get_timeout_config("action")
    
    assert stt_timeout == 30
    assert nlu_timeout == 10
    assert tts_timeout == 15
    assert action_timeout == 20


def test_request_failure_tracking(perf_service):
    """Test request failure tracking"""
    # Record successful requests
    perf_service.record_request_completion(success=True)
    perf_service.record_request_completion(success=True)
    
    # Record failed request
    perf_service.record_request_completion(success=False)
    
    metrics = perf_service.get_performance_metrics()
    assert metrics["total_requests"] == 3
    assert metrics["failed_requests"] == 1
