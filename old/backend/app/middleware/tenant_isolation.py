"""
Tenant isolation middleware for multi-tenant analytics
"""
import logging
from fastapi import Request, HTTPException, status
from typing import Callable, Any

logger = logging.getLogger(__name__)


class TenantIsolationMiddleware:
    """Middleware to ensure tenant isolation in analytics queries"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, request: Request, call_next: Callable) -> Any:
        """Process request and ensure tenant isolation"""
        # Extract tenant_id from user context
        user = getattr(request.state, "user", None)
        
        if user and hasattr(user, "tenant_id"):
            request.state.tenant_id = user.tenant_id
        
        response = await call_next(request)
        return response


def ensure_tenant_isolation(tenant_id: str, query_tenant_id: str) -> None:
    """Ensure that query tenant_id matches user's tenant_id"""
    if tenant_id != query_tenant_id:
        logger.warning(
            f"Tenant isolation violation: User tenant {tenant_id} "
            f"attempted to access tenant {query_tenant_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this tenant's data"
        )


def add_tenant_filter(query: dict, tenant_id: str) -> dict:
    """Add tenant_id filter to MongoDB query"""
    if "$and" in query:
        query["$and"].append({"tenant_id": tenant_id})
    else:
        query["tenant_id"] = tenant_id
    return query


def add_tenant_filter_to_aggregation(pipeline: list, tenant_id: str) -> list:
    """Add tenant_id filter to MongoDB aggregation pipeline"""
    # Insert tenant filter at the beginning
    pipeline.insert(0, {"$match": {"tenant_id": tenant_id}})
    return pipeline


class TenantAwareQuery:
    """Helper class for building tenant-aware queries"""

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.query = {}

    def add_filter(self, field: str, value: Any) -> "TenantAwareQuery":
        """Add a filter to the query"""
        self.query[field] = value
        return self

    def add_range_filter(self, field: str, start: Any, end: Any) -> "TenantAwareQuery":
        """Add a range filter to the query"""
        self.query[field] = {"$gte": start, "$lte": end}
        return self

    def add_in_filter(self, field: str, values: list) -> "TenantAwareQuery":
        """Add an IN filter to the query"""
        self.query[field] = {"$in": values}
        return self

    def build(self) -> dict:
        """Build the final query with tenant isolation"""
        return add_tenant_filter(self.query, self.tenant_id)


class TenantAwareAggregation:
    """Helper class for building tenant-aware aggregation pipelines"""

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.pipeline = []

    def add_match(self, match_stage: dict) -> "TenantAwareAggregation":
        """Add a match stage"""
        self.pipeline.append({"$match": match_stage})
        return self

    def add_group(self, group_stage: dict) -> "TenantAwareAggregation":
        """Add a group stage"""
        self.pipeline.append({"$group": group_stage})
        return self

    def add_sort(self, sort_stage: dict) -> "TenantAwareAggregation":
        """Add a sort stage"""
        self.pipeline.append({"$sort": sort_stage})
        return self

    def add_limit(self, limit: int) -> "TenantAwareAggregation":
        """Add a limit stage"""
        self.pipeline.append({"$limit": limit})
        return self

    def add_skip(self, skip: int) -> "TenantAwareAggregation":
        """Add a skip stage"""
        self.pipeline.append({"$skip": skip})
        return self

    def add_project(self, project_stage: dict) -> "TenantAwareAggregation":
        """Add a project stage"""
        self.pipeline.append({"$project": project_stage})
        return self

    def build(self) -> list:
        """Build the final pipeline with tenant isolation"""
        return add_tenant_filter_to_aggregation(self.pipeline, self.tenant_id)


def validate_tenant_access(user_tenant_id: str, resource_tenant_id: str) -> bool:
    """Validate that user has access to resource"""
    return user_tenant_id == resource_tenant_id


def get_tenant_specific_collection(db, collection_name: str, tenant_id: str):
    """Get a tenant-specific view of a collection"""
    # This would typically be implemented with MongoDB views or similar
    # For now, we return the collection and rely on query filters
    return db[collection_name]
