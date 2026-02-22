"""
Package bulk operations schemas
"""
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional
from datetime import datetime


class BulkActivateRequest(BaseModel):
    """Request schema for bulk package activation"""
    package_ids: List[str] = Field(..., min_items=1, description="List of package IDs to activate")


class BulkDeactivateRequest(BaseModel):
    """Request schema for bulk package deactivation"""
    package_ids: List[str] = Field(..., min_items=1, description="List of package IDs to deactivate")


class PriceUpdate(BaseModel):
    """Price update for a single package"""
    package_id: str = Field(..., description="Package ID")
    new_price: float = Field(..., ge=0, description="New package price")


class BulkUpdatePricesRequest(BaseModel):
    """Request schema for bulk price updates"""
    package_updates: List[PriceUpdate] = Field(..., min_items=1, description="List of price updates")


class ExpirationExtension(BaseModel):
    """Expiration extension for a single purchase"""
    purchase_id: str = Field(..., description="Package purchase ID")
    additional_days: int = Field(..., gt=0, description="Number of days to extend")


class BulkExtendExpirationRequest(BaseModel):
    """Request schema for bulk expiration extension"""
    purchase_updates: List[ExpirationExtension] = Field(..., min_items=1, description="List of expiration extensions")


class FailedOperation(BaseModel):
    """Details of a failed operation"""
    package_id: Optional[str] = Field(None, description="Package or purchase ID")
    purchase_id: Optional[str] = Field(None, description="Purchase ID (for expiration operations)")
    error: str = Field(..., description="Error message")


class BulkOperationResult(BaseModel):
    """Result of a bulk operation"""
    operation: str = Field(..., description="Operation type (bulk_activate, bulk_deactivate, etc.)")
    total_requested: int = Field(..., description="Total number of items requested")
    successful: int = Field(..., description="Number of successful operations")
    failed: int = Field(..., description="Number of failed operations")
    successful_ids: List[str] = Field(default_factory=list, description="IDs of successful operations")
    failed_details: List[FailedOperation] = Field(default_factory=list, description="Details of failed operations")
    timestamp: datetime = Field(..., description="Operation timestamp")


class BulkActivateResponse(BulkOperationResult):
    """Response schema for bulk activation"""
    pass


class BulkDeactivateResponse(BulkOperationResult):
    """Response schema for bulk deactivation"""
    pass


class BulkUpdatePricesResponse(BulkOperationResult):
    """Response schema for bulk price updates"""
    pass


class BulkExtendExpirationResponse(BulkOperationResult):
    """Response schema for bulk expiration extension"""
    pass
