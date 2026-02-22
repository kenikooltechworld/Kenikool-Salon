"""
Docker Container Health Check Utility

This module provides functions to check the health and availability
of AI model Docker containers.
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
import aiohttp
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ContainerHealth(BaseModel):
    """Health status of a Docker container"""
    name: str
    url: str
    is_healthy: bool
    response_time_ms: Optional[float]
    error: Optional[str]
    last_checked: datetime


class DockerHealthChecker:
    """Checks health of AI model Docker containers"""
    
    CONTAINERS = {
        "whisper-stt": "http://localhost:9000/health",
        "kimi-k2": "http://localhost:8001/health",
        "qwen3-reranker": "http://localhost:8002/health",
        "coqui-tts": "http://localhost:5002/health",
        "deepseek": "http://localhost:8003/health",
    }
    
    def __init__(self, timeout: int = 5):
        """
        Initialize health checker
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
    
    async def check_container(
        self,
        name: str,
        url: str
    ) -> ContainerHealth:
        """
        Check health of a single container
        
        Args:
            name: Container name
            url: Health check URL
            
        Returns:
            ContainerHealth object with status
        """
        start_time = datetime.now()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    end_time = datetime.now()
                    response_time = (end_time - start_time).total_seconds() * 1000
                    
                    is_healthy = response.status == 200
                    
                    return ContainerHealth(
                        name=name,
                        url=url,
                        is_healthy=is_healthy,
                        response_time_ms=response_time,
                        error=None if is_healthy else f"HTTP {response.status}",
                        last_checked=datetime.now()
                    )
        
        except asyncio.TimeoutError:
            return ContainerHealth(
                name=name,
                url=url,
                is_healthy=False,
                response_time_ms=None,
                error=f"Timeout after {self.timeout}s",
                last_checked=datetime.now()
            )
        
        except aiohttp.ClientError as e:
            return ContainerHealth(
                name=name,
                url=url,
                is_healthy=False,
                response_time_ms=None,
                error=f"Connection error: {str(e)}",
                last_checked=datetime.now()
            )
        
        except Exception as e:
            logger.error(f"Unexpected error checking {name}: {e}")
            return ContainerHealth(
                name=name,
                url=url,
                is_healthy=False,
                response_time_ms=None,
                error=f"Unexpected error: {str(e)}",
                last_checked=datetime.now()
            )
    
    async def check_all_containers(self) -> List[ContainerHealth]:
        """
        Check health of all containers concurrently
        
        Returns:
            List of ContainerHealth objects
        """
        tasks = [
            self.check_container(name, url)
            for name, url in self.CONTAINERS.items()
        ]
        
        results = await asyncio.gather(*tasks)
        return list(results)
    
    async def get_health_summary(self) -> Dict[str, any]:
        """
        Get summary of all container health statuses
        
        Returns:
            Dictionary with health summary
        """
        health_checks = await self.check_all_containers()
        
        healthy_count = sum(1 for h in health_checks if h.is_healthy)
        total_count = len(health_checks)
        
        return {
            "all_healthy": healthy_count == total_count,
            "healthy_count": healthy_count,
            "total_count": total_count,
            "containers": [h.dict() for h in health_checks],
            "checked_at": datetime.now().isoformat()
        }
    
    async def wait_for_containers(
        self,
        max_wait_seconds: int = 120,
        check_interval: int = 5
    ) -> bool:
        """
        Wait for all containers to become healthy
        
        Args:
            max_wait_seconds: Maximum time to wait
            check_interval: Seconds between checks
            
        Returns:
            True if all containers are healthy, False if timeout
        """
        start_time = datetime.now()
        
        while (datetime.now() - start_time).total_seconds() < max_wait_seconds:
            summary = await self.get_health_summary()
            
            if summary["all_healthy"]:
                logger.info("All containers are healthy")
                return True
            
            unhealthy = [
                c["name"] for c in summary["containers"]
                if not c["is_healthy"]
            ]
            logger.info(
                f"Waiting for containers: {', '.join(unhealthy)}. "
                f"Retrying in {check_interval}s..."
            )
            
            await asyncio.sleep(check_interval)
        
        logger.error(f"Timeout waiting for containers after {max_wait_seconds}s")
        return False
    
    def get_container_url(self, container_name: str) -> Optional[str]:
        """
        Get the base URL for a container
        
        Args:
            container_name: Name of the container
            
        Returns:
            Base URL or None if not found
        """
        health_url = self.CONTAINERS.get(container_name)
        if health_url:
            # Remove /health suffix to get base URL
            return health_url.rsplit("/", 1)[0]
        return None


# Singleton instance
_health_checker = None


def get_health_checker() -> DockerHealthChecker:
    """Get singleton health checker instance"""
    global _health_checker
    if _health_checker is None:
        _health_checker = DockerHealthChecker()
    return _health_checker


# Convenience functions
async def check_all_containers() -> List[ContainerHealth]:
    """Check health of all containers"""
    checker = get_health_checker()
    return await checker.check_all_containers()


async def get_health_summary() -> Dict[str, any]:
    """Get health summary of all containers"""
    checker = get_health_checker()
    return await checker.get_health_summary()


async def wait_for_containers(
    max_wait_seconds: int = 120,
    check_interval: int = 5
) -> bool:
    """Wait for all containers to become healthy"""
    checker = get_health_checker()
    return await checker.wait_for_containers(max_wait_seconds, check_interval)


def get_container_url(container_name: str) -> Optional[str]:
    """Get base URL for a container"""
    checker = get_health_checker()
    return checker.get_container_url(container_name)
