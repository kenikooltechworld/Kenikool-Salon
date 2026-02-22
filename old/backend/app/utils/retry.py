"""
Retry utility with exponential backoff.
Provides functions for retrying failed operations with configurable backoff strategies.
"""

import asyncio
import logging
from typing import Callable, Any, Optional, TypeVar, Coroutine
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RetryException(Exception):
    """Exception raised when all retry attempts fail"""
    pass


async def retry_with_backoff(
    func: Callable[..., Coroutine[Any, Any, T]],
    *args,
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    **kwargs
) -> T:
    """
    Retry an async function with exponential backoff.
    
    Args:
        func: Async function to retry
        *args: Positional arguments to pass to func
        max_attempts: Maximum number of attempts (default 3)
        initial_delay: Initial delay in seconds (default 1.0)
        backoff_factor: Multiplier for delay between attempts (default 2.0)
        max_delay: Maximum delay in seconds (default 60.0)
        **kwargs: Keyword arguments to pass to func
    
    Returns:
        Result from func
    
    Raises:
        RetryException: If all attempts fail
    
    Requirement 6.5: Retry logic with exponential backoff (1s, 2s, 4s)
    """
    last_exception = None
    delay = initial_delay
    
    for attempt in range(1, max_attempts + 1):
        try:
            logger.debug(f"Attempt {attempt}/{max_attempts} for {func.__name__}")
            result = await func(*args, **kwargs)
            
            if attempt > 1:
                logger.info(f"Succeeded on attempt {attempt} for {func.__name__}")
            
            return result
        
        except Exception as e:
            last_exception = e
            
            if attempt < max_attempts:
                # Calculate delay with exponential backoff
                current_delay = min(delay, max_delay)
                logger.warning(
                    f"Attempt {attempt} failed for {func.__name__}: {str(e)}. "
                    f"Retrying in {current_delay}s..."
                )
                
                await asyncio.sleep(current_delay)
                delay *= backoff_factor
            else:
                logger.error(
                    f"All {max_attempts} attempts failed for {func.__name__}: {str(e)}"
                )
    
    raise RetryException(
        f"Failed after {max_attempts} attempts: {str(last_exception)}"
    ) from last_exception


def retry_async(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0
):
    """
    Decorator for retrying async functions with exponential backoff.
    
    Args:
        max_attempts: Maximum number of attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for delay between attempts
        max_delay: Maximum delay in seconds
    
    Returns:
        Decorated function
    
    Example:
        @retry_async(max_attempts=3, initial_delay=1.0)
        async def my_function():
            # Function that might fail
            pass
    """
    def decorator(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            return await retry_with_backoff(
                func,
                *args,
                max_attempts=max_attempts,
                initial_delay=initial_delay,
                backoff_factor=backoff_factor,
                max_delay=max_delay,
                **kwargs
            )
        return wrapper
    return decorator


def get_backoff_delay(attempt: int, initial_delay: float = 1.0, backoff_factor: float = 2.0) -> float:
    """
    Calculate backoff delay for a given attempt number.
    
    Args:
        attempt: Attempt number (1-indexed)
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for delay between attempts
    
    Returns:
        Delay in seconds
    
    Example:
        >>> get_backoff_delay(1)  # First retry
        1.0
        >>> get_backoff_delay(2)  # Second retry
        2.0
        >>> get_backoff_delay(3)  # Third retry
        4.0
    """
    if attempt < 1:
        return 0.0
    
    return initial_delay * (backoff_factor ** (attempt - 1))
