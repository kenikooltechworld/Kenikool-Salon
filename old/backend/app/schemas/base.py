"""
Base Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, TypeVar, Generic
from datetime import datetime


class ErrorResponse(BaseModel):
    """Standard error response"""
    status: str = "error"
    message: str
    details: Optional[Dict[str, Any]] = None
    code: Optional[str] = None


class SuccessResponse(BaseModel):
    """Standard success response"""
    success: bool = True
    message: str


class PaginationParams(BaseModel):
    """Pagination parameters"""
    offset: int = Field(default=0, ge=0, description="Number of items to skip")
    limit: int = Field(default=20, ge=1, le=100, description="Number of items to return")


class PageInfo(BaseModel):
    """Pagination information"""
    has_next_page: bool
    has_previous_page: bool
    total_count: Optional[int] = None


T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response"""
    items: List[T]
    page_info: PageInfo


class BaseSchema(BaseModel):
    """Base schema with common configuration"""
    class Config:
        from_attributes = True  # Allows creating from ORM models
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
