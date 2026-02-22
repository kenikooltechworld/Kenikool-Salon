"""Request context management for tenant isolation."""

from contextvars import ContextVar
from typing import Optional
from bson import ObjectId

# Context variable for storing tenant_id
_tenant_id_context: ContextVar[Optional[ObjectId]] = ContextVar(
    "tenant_id", default=None
)

# Context variable for storing user_id
_user_id_context: ContextVar[Optional[ObjectId]] = ContextVar(
    "user_id", default=None
)


def set_tenant_id(tenant_id: ObjectId) -> None:
    """Set tenant_id in context."""
    _tenant_id_context.set(tenant_id)


def get_tenant_id() -> Optional[ObjectId]:
    """Get tenant_id from context."""
    return _tenant_id_context.get()


def set_user_id(user_id: ObjectId) -> None:
    """Set user_id in context."""
    _user_id_context.set(user_id)


def get_user_id() -> Optional[ObjectId]:
    """Get user_id from context."""
    return _user_id_context.get()


def clear_context() -> None:
    """Clear all context variables."""
    _tenant_id_context.set(None)
    _user_id_context.set(None)
