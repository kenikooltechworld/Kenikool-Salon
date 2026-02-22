"""
Expense Pydantic models
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
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


class ExpenseBase(BaseModel):
    """Base expense model"""
    category: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., min_length=2, max_length=500)
    amount: float = Field(..., gt=0)
    expense_date: date
    payment_method: Optional[str] = None
    vendor: Optional[str] = None
    receipt_url: Optional[str] = None
    notes: Optional[str] = None


class ExpenseCreate(ExpenseBase):
    """Expense creation model"""
    tenant_id: str


class ExpenseUpdate(BaseModel):
    """Expense update model"""
    category: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, min_length=2, max_length=500)
    amount: Optional[float] = Field(None, gt=0)
    expense_date: Optional[date] = None
    payment_method: Optional[str] = None
    vendor: Optional[str] = None
    receipt_url: Optional[str] = None
    notes: Optional[str] = None


class ExpenseInDB(ExpenseBase):
    """Expense model as stored in database"""
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    tenant_id: str
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str, date: lambda v: v.isoformat()}

