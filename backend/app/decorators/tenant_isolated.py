"""Decorator for tenant-isolated route handlers."""

import logging
from functools import wraps
from typing import Callable, Any
from fastapi import HTTPException, status
from app.context import get_tenant_id

logger = logging.getLogger(__name__)


def tenant_isolated(func: Callable) -> Callable:
    """
    Decorator to ensure route handler has valid tenant context.

    Validates that tenant_id is present in context before executing handler.
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """Wrapper function to check tenant context."""
        tenant_id = get_tenant_id()

        if not tenant_id:
            logger.warning("Request attempted without tenant context")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant context required",
            )

        return func(*args, **kwargs)

    return wrapper
