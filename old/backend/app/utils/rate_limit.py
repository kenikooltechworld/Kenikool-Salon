"""
Rate limiting and monitoring utilities.
Provides functions for tracking API usage and implementing rate limiting.
"""

import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
import redis

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter for API requests"""

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """
        Initialize rate limiter with Redis client.

        Args:
            redis_client: Optional Redis client for distributed rate limiting
        """
        self.redis = redis_client
        self.quota_percentage_warning = 80  # Warn at 80% quota

    async def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int = 3600
    ) -> Dict[str, any]:
        """
        Check if a request is within rate limits.

        Args:
            key: Rate limit key (e.g., "mapbox:geocoding")
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds (default 1 hour)

        Returns:
            Dictionary with rate limit info:
            - allowed: Whether request is allowed
            - remaining: Remaining requests in window
            - reset_at: When the window resets
            - quota_percentage: Percentage of quota used

        Requirement 7.3: Rate limit monitoring
        """
        if not self.redis:
            # If no Redis, allow all requests
            return {
                "allowed": True,
                "remaining": max_requests,
                "reset_at": datetime.utcnow() + timedelta(seconds=window_seconds),
                "quota_percentage": 0,
            }

        try:
            # Get current count
            current_count = self.redis.get(key)
            if current_count is None:
                current_count = 0
            else:
                current_count = int(current_count)

            # Check if limit exceeded
            allowed = current_count < max_requests
            remaining = max(0, max_requests - current_count)
            quota_percentage = (current_count / max_requests) * 100

            # Log warning if approaching limit
            if quota_percentage >= self.quota_percentage_warning:
                logger.warning(
                    f"Rate limit warning for {key}: {quota_percentage:.1f}% of quota used "
                    f"({current_count}/{max_requests} requests)"
                )

            # Calculate reset time
            ttl = self.redis.ttl(key)
            if ttl == -1:
                # Key exists but has no expiry, set it
                self.redis.expire(key, window_seconds)
                ttl = window_seconds
            elif ttl == -2:
                # Key doesn't exist
                ttl = window_seconds

            reset_at = datetime.utcnow() + timedelta(seconds=ttl)

            return {
                "allowed": allowed,
                "remaining": remaining,
                "reset_at": reset_at,
                "quota_percentage": quota_percentage,
            }

        except Exception as e:
            logger.error(f"Error checking rate limit for {key}: {e}")
            # Allow request if rate limiter fails
            return {
                "allowed": True,
                "remaining": max_requests,
                "reset_at": datetime.utcnow() + timedelta(seconds=window_seconds),
                "quota_percentage": 0,
            }

    async def increment_counter(
        self,
        key: str,
        window_seconds: int = 3600
    ) -> int:
        """
        Increment rate limit counter.

        Args:
            key: Rate limit key
            window_seconds: Time window in seconds

        Returns:
            New counter value

        Requirement 7.3: Track API usage
        """
        if not self.redis:
            return 1

        try:
            # Increment counter
            new_count = self.redis.incr(key)

            # Set expiry if this is the first request
            if new_count == 1:
                self.redis.expire(key, window_seconds)

            return new_count

        except Exception as e:
            logger.error(f"Error incrementing counter for {key}: {e}")
            return 1

    async def queue_request(
        self,
        key: str,
        max_queue_size: int = 100
    ) -> bool:
        """
        Queue a request when approaching rate limits.

        Args:
            key: Queue key
            max_queue_size: Maximum queue size

        Returns:
            True if queued successfully, False if queue is full

        Requirement 7.3: Request queuing
        """
        if not self.redis:
            return True

        try:
            queue_length = self.redis.llen(key)

            if queue_length >= max_queue_size:
                logger.warning(f"Request queue full for {key}")
                return False

            # Add request to queue
            self.redis.rpush(key, datetime.utcnow().isoformat())
            logger.debug(f"Queued request for {key} (queue size: {queue_length + 1})")

            return True

        except Exception as e:
            logger.error(f"Error queuing request for {key}: {e}")
            return True

    async def get_queue_size(self, key: str) -> int:
        """
        Get current queue size.

        Args:
            key: Queue key

        Returns:
            Queue size
        """
        if not self.redis:
            return 0

        try:
            return self.redis.llen(key)
        except Exception as e:
            logger.error(f"Error getting queue size for {key}: {e}")
            return 0

    async def process_queue(self, key: str, batch_size: int = 10) -> int:
        """
        Process queued requests.

        Args:
            key: Queue key
            batch_size: Number of requests to process

        Returns:
            Number of requests processed
        """
        if not self.redis:
            return 0

        try:
            processed = 0
            for _ in range(batch_size):
                item = self.redis.lpop(key)
                if item is None:
                    break
                processed += 1

            if processed > 0:
                logger.info(f"Processed {processed} queued requests for {key}")

            return processed

        except Exception as e:
            logger.error(f"Error processing queue for {key}: {e}")
            return 0

    def get_rate_limit_headers(
        self,
        rate_limit_info: Dict[str, any]
    ) -> Dict[str, str]:
        """
        Get HTTP headers for rate limit info.

        Args:
            rate_limit_info: Rate limit info from check_rate_limit

        Returns:
            Dictionary of HTTP headers

        Requirement 7.4: Rate limit response handling
        """
        reset_at = rate_limit_info.get("reset_at")
        reset_timestamp = int(reset_at.timestamp()) if reset_at else 0

        return {
            "X-RateLimit-Remaining": str(rate_limit_info.get("remaining", 0)),
            "X-RateLimit-Reset": str(reset_timestamp),
            "X-RateLimit-Quota-Percentage": f"{rate_limit_info.get('quota_percentage', 0):.1f}%",
        }
