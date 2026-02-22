"""
Base client for Docker AI model communication
Provides connection pooling, retry logic, and error handling
"""

import httpx
import logging
from typing import Optional, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)


class BaseDockerClient:
    """Base class for Docker AI model clients"""
    
    def __init__(
        self,
        container_url: str,
        timeout: float = 30.0,
        max_retries: int = 3,
        pool_limits: Optional[httpx.Limits] = None
    ):
        """
        Initialize base Docker client
        
        Args:
            container_url: URL of the Docker container
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            pool_limits: Connection pool limits
        """
        self.container_url = container_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Configure connection pooling
        if pool_limits is None:
            pool_limits = httpx.Limits(
                max_keepalive_connections=20,
                max_connections=100,
                keepalive_expiry=30.0
            )
        
        # Create async HTTP client with connection pooling
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            limits=pool_limits,
            follow_redirects=True
        )
        
        logger.info(f"Initialized {self.__class__.__name__} for {container_url}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        reraise=True
    )
    async def _post(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> httpx.Response:
        """
        Make POST request with retry logic
        
        Args:
            endpoint: API endpoint path
            json_data: JSON data to send
            files: Files to upload
            **kwargs: Additional request parameters
            
        Returns:
            HTTP response
            
        Raises:
            httpx.HTTPError: If request fails after retries
        """
        url = f"{self.container_url}{endpoint}"
        
        try:
            logger.debug(f"POST {url}")
            response = await self.client.post(
                url,
                json=json_data,
                files=files,
                **kwargs
            )
            response.raise_for_status()
            return response
            
        except httpx.TimeoutException as e:
            logger.error(f"Timeout calling {url}: {e}")
            raise
        except httpx.NetworkError as e:
            logger.error(f"Network error calling {url}: {e}")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} calling {url}: {e}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        reraise=True
    )
    async def _get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> httpx.Response:
        """
        Make GET request with retry logic
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            **kwargs: Additional request parameters
            
        Returns:
            HTTP response
            
        Raises:
            httpx.HTTPError: If request fails after retries
        """
        url = f"{self.container_url}{endpoint}"
        
        try:
            logger.debug(f"GET {url}")
            response = await self.client.get(
                url,
                params=params,
                **kwargs
            )
            response.raise_for_status()
            return response
            
        except httpx.TimeoutException as e:
            logger.error(f"Timeout calling {url}: {e}")
            raise
        except httpx.NetworkError as e:
            logger.error(f"Network error calling {url}: {e}")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} calling {url}: {e}")
            raise
    
    async def health_check(self) -> bool:
        """
        Check if the Docker container is healthy
        
        Returns:
            True if container is healthy, False otherwise
        """
        try:
            # Try root endpoint first
            response = await self.client.get(
                self.container_url,
                timeout=5.0
            )
            # Accept various status codes that indicate server is up
            # 200 = OK, 404 = Not Found (but server up), 405 = Method Not Allowed, 307 = Redirect
            return response.status_code in [200, 307, 404, 405]
        except httpx.RemoteProtocolError:
            # Server disconnected - this can happen with some containers but they're still running
            logger.warning(f"RemoteProtocolError for {self.container_url} - server may be up but not responding to GET")
            return True  # Assume healthy if we get protocol error (server is listening)
        except Exception as e:
            logger.warning(f"Health check failed for {self.container_url}: {e}")
            return False
    
    async def close(self):
        """Close the HTTP client and release connections"""
        await self.client.aclose()
        logger.info(f"Closed {self.__class__.__name__}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
