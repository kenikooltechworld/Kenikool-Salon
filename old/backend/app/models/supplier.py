"""
Supplier Model - Tracks supplier information and performance
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Supplier(BaseModel):
    """Supplier record"""
    id: Optional[str] = Field(None, alias="_id")
    tenant_id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    contact_person: Optional[str] = None
    payment_terms: Optional[str] = None  # e.g., "Net 30"
    is_active: bool = True
    
    # Performance metrics
    total_orders: int = 0
    on_time_deliveries: int = 0
    on_time_delivery_rate: float = 0.0  # Percentage
    average_delivery_days: float = 0.0
    total_spent: float = 0.0
    last_order_date: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_123",
                "name": "Beauty Supplies Inc",
                "email": "sales@beautysupplies.com",
                "phone": "+1-555-0123",
                "address": "123 Supply St",
                "city": "New York",
                "country": "USA",
                "contact_person": "John Doe",
                "payment_terms": "Net 30",
                "is_active": True,
                "total_orders": 15,
                "on_time_deliveries": 14,
                "on_time_delivery_rate": 93.33,
            }
        }


class SupplierResponse(Supplier):
    """Response model for suppliers"""
    pass


class SupplierListResponse(BaseModel):
    """Response for supplier list"""
    suppliers: list[SupplierResponse]
    total_count: int
