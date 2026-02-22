"""
Inventory Pydantic models
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId


class PyObjectId(str):
    """Custom type for MongoDB ObjectId"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)


class InventoryTransaction(BaseModel):
    """Inventory transaction model"""
    transaction_type: str  # purchase, usage, adjustment, return
    quantity: int
    booking_id: Optional[str] = None
    service_id: Optional[str] = None
    notes: Optional[str] = None
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class InventoryProductBase(BaseModel):
    """Base inventory product model"""
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = None
    unit: str = "unit"  # unit, ml, g, kg, etc.
    quantity: int = 0
    low_stock_threshold: int = 10
    unit_cost: float = 0.0
    supplier: Optional[str] = None
    sku: Optional[str] = None
    is_active: bool = True


class InventoryProductCreate(InventoryProductBase):
    """Inventory product creation model"""
    tenant_id: str


class InventoryProductInDB(InventoryProductBase):
    """Inventory product model as stored in database"""
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    tenant_id: str
    transactions: List[dict] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class ProductServiceMapping(BaseModel):
    """Product-service mapping model"""
    product_id: str
    product_name: str
    quantity_per_service: float
