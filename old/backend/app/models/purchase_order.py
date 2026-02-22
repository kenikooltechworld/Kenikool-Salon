"""
Purchase Order Model - Tracks supplier orders
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class POStatus(str, Enum):
    """Purchase order status"""
    DRAFT = "draft"
    SENT = "sent"
    RECEIVED = "received"
    PARTIAL = "partial"
    CANCELLED = "cancelled"


class POLineItem(BaseModel):
    """Line item in a purchase order"""
    product_id: str
    product_name: str
    quantity_ordered: int
    quantity_received: int = 0
    unit_price: float
    total_price: float


class PurchaseOrder(BaseModel):
    """Purchase order record"""
    id: Optional[str] = Field(None, alias="_id")
    tenant_id: str
    po_number: str  # Auto-generated unique number
    supplier_id: str
    supplier_name: str
    status: POStatus = POStatus.DRAFT
    line_items: List[POLineItem]
    subtotal: float
    tax_amount: float = 0.0
    shipping_cost: float = 0.0
    total_amount: float
    expected_delivery_date: Optional[datetime] = None
    actual_delivery_date: Optional[datetime] = None
    notes: Optional[str] = None
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None
    received_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_123",
                "po_number": "PO-2024-001",
                "supplier_id": "supplier_456",
                "supplier_name": "Beauty Supplies Inc",
                "status": "draft",
                "line_items": [
                    {
                        "product_id": "product_789",
                        "product_name": "Hair Dye",
                        "quantity_ordered": 50,
                        "unit_price": 5.0,
                        "total_price": 250.0,
                    }
                ],
                "subtotal": 250.0,
                "total_amount": 250.0,
            }
        }


class PurchaseOrderResponse(PurchaseOrder):
    """Response model for purchase orders"""
    pass


class PurchaseOrderListResponse(BaseModel):
    """Response for purchase order list"""
    purchase_orders: List[PurchaseOrderResponse]
    total_count: int
    page: int
    page_size: int
