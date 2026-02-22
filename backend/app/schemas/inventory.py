from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class InventoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    sku: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(default=0, ge=0)
    reorder_level: int = Field(default=10, ge=0)
    unit_cost: float = Field(default=0.0, ge=0)
    unit: str = Field(default="unit", max_length=50)
    category: Optional[str] = Field(None, max_length=100)
    supplier_id: Optional[str] = None
    expiry_date: Optional[datetime] = None
    notes: Optional[str] = None


class InventoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    sku: Optional[str] = Field(None, min_length=1, max_length=100)
    reorder_level: Optional[int] = Field(None, ge=0)
    unit_cost: Optional[float] = Field(None, ge=0)
    unit: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, max_length=100)
    supplier_id: Optional[str] = None
    expiry_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class InventoryResponse(BaseModel):
    id: str
    name: str
    sku: str
    quantity: int
    reorder_level: int
    unit_cost: float
    unit: str
    category: Optional[str]
    supplier_id: Optional[str]
    last_restocked_at: Optional[datetime]
    expiry_date: Optional[datetime]
    is_active: bool
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InventoryTransactionCreate(BaseModel):
    quantity: int = Field(..., gt=0)
    reason: str = Field(..., max_length=255)
    reference_id: Optional[str] = None
    reference_type: Optional[str] = Field(None, max_length=50)


class InventoryTransactionResponse(BaseModel):
    id: str
    inventory_id: str
    transaction_type: str
    quantity_change: int
    reason: str
    reference_id: Optional[str]
    reference_type: Optional[str]
    user_id: Optional[str]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class StockAlertResponse(BaseModel):
    id: str
    inventory_id: str
    alert_type: str
    current_quantity: int
    threshold: int
    is_resolved: bool
    resolved_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class InventoryReconciliationRequest(BaseModel):
    physical_count: int = Field(..., ge=0)
    notes: Optional[str] = None


class InventoryReconciliationResponse(BaseModel):
    inventory_id: str
    system_count: int
    physical_count: int
    discrepancy: int
    reconciled_at: datetime


class InventoryValueResponse(BaseModel):
    total_value: float
    total_items: int
    item_count: int
