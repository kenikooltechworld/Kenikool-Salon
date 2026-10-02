"""Decorator for tenant-isolated route handlers."""

import logging
import inspect
from functools import wraps
from typing import Callable, Any
from fastapi import HTTPException, status
from app.context import get_tenant_id

logger = logging.getLogger(__name__)


def tenant_isolated(func: Callable) -> Callable:
    """
    Decorator to ensure route handler has valid tenant context.

    Validates that tenant_id is present in context before executing handler.
    Supports both sync and async route handlers.
    """

    if inspect.iscoroutinefunction(func):
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            """Async wrapper function to check tenant context."""
            tenant_id = get_tenant_id()

            if not tenant_id:
                logger.warning("Request attempted without tenant context")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Tenant context required",
                )

            return await func(*args, **kwargs)

        return async_wrapper

    @wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        """Sync wrapper function to check tenant context."""
        tenant_id = get_tenant_id()

        if not tenant_id:
            logger.warning("Request attempted without tenant context")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant context required",
            )

        return func(*args, **kwargs)

    return sync_wrapper
