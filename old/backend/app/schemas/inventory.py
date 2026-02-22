"""
Inventory schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.base import BaseSchema


class InventoryProductCreate(BaseModel):
    """Inventory product creation request"""
    name: str = Field(..., min_length=2, max_length=100)
    category: Optional[str] = Field(None, max_length=50)
    sku: Optional[str] = Field(None, max_length=50)
    quantity: int = Field(..., ge=0)
    unit: str = Field(..., description="Unit of measurement (e.g., bottle, piece, ml)")
    cost_price: float = Field(..., ge=0)
    selling_price: Optional[float] = Field(None, ge=0)
    reorder_level: int = Field(default=10, ge=0, description="Minimum quantity before reorder alert")
    supplier: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=500)


class InventoryProductUpdate(BaseModel):
    """Inventory product update request"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    category: Optional[str] = Field(None, max_length=50)
    sku: Optional[str] = Field(None, max_length=50)
    unit: Optional[str] = None
    cost_price: Optional[float] = Field(None, ge=0)
    selling_price: Optional[float] = Field(None, ge=0)
    reorder_level: Optional[int] = Field(None, ge=0)
    supplier: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=500)


class InventoryAdjustmentRequest(BaseModel):
    """Inventory adjustment request"""
    adjustment_type: str = Field(..., description="add, remove, or set")
    quantity: int = Field(..., description="Quantity to adjust")
    reason: str = Field(..., max_length=200, description="Reason for adjustment")
    notes: Optional[str] = Field(None, max_length=500)


class InventoryTransactionResponse(BaseModel):
    """Inventory transaction response"""
    transaction_type: str
    quantity: int
    reason: str
    notes: Optional[str] = None
    created_at: datetime


class InventoryProductResponse(BaseSchema):
    """Inventory product response"""
    id: str
    tenant_id: str
    name: str
    category: Optional[str] = None
    sku: Optional[str] = None
    quantity: int
    unit: str
    cost_price: float
    selling_price: Optional[float] = None
    reorder_level: int
    supplier: Optional[str] = None
    notes: Optional[str] = None
    is_low_stock: bool = False
    created_at: datetime
    updated_at: datetime


class LowStockAlertResponse(BaseModel):
    """Low stock alert response"""
    products: List[InventoryProductResponse]
    total_count: int


class InventoryFilter(BaseModel):
    """Inventory filter parameters"""
    category: Optional[str] = None
    low_stock: Optional[bool] = None
    search: Optional[str] = Field(None, description="Search by name or SKU")
