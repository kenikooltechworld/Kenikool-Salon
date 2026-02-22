"""
Inventory Transaction Model - Tracks all inventory changes
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class TransactionType(str, Enum):
    """Types of inventory transactions"""
    ADD = "add"
    REMOVE = "remove"
    SET = "set"
    SERVICE_USAGE = "service_usage"
    POS_SALE = "pos_sale"
    WASTE = "waste"
    TRANSFER = "transfer"
    ADJUSTMENT = "adjustment"


class WasteReason(str, Enum):
    """Reasons for waste"""
    EXPIRED = "expired"
    DAMAGED = "damaged"
    SPILLED = "spilled"
    THEFT = "theft"
    OTHER = "other"


class InventoryTransaction(BaseModel):
    """Inventory transaction record"""
    id: Optional[str] = Field(None, alias="_id")
    tenant_id: str
    product_id: str
    transaction_type: TransactionType
    quantity_before: int
    quantity_after: int
    quantity_changed: int
    user_id: str
    reason: Optional[str] = None
    waste_reason: Optional[WasteReason] = None
    reference_id: Optional[str] = None  # booking_id, po_id, etc.
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    batch_id: Optional[str] = None
    location_id: Optional[str] = None

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_123",
                "product_id": "product_456",
                "transaction_type": "service_usage",
                "quantity_before": 100,
                "quantity_after": 95,
                "quantity_changed": -5,
                "user_id": "user_789",
                "reason": "Used in hair coloring service",
                "reference_id": "booking_123",
            }
        }


class InventoryTransactionResponse(InventoryTransaction):
    """Response model for inventory transactions"""
    pass


class TransactionListResponse(BaseModel):
    """Response for transaction list"""
    transactions: List[InventoryTransactionResponse]
    total_count: int
    page: int
    page_size: int
