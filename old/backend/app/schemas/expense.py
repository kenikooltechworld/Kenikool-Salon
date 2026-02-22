"""
Expense schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date

class ExpenseBase(BaseModel):
    """Base expense schema"""
    category: str = Field(..., min_length=2, max_length=100, description="Expense category")
    description: str = Field(..., min_length=2, max_length=500, description="Expense description")
    amount: float = Field(..., gt=0, description="Expense amount")
    expense_date: date = Field(..., description="Date of expense")
    payment_method: Optional[str] = Field(None, description="Payment method used")
    vendor: Optional[str] = Field(None, description="Vendor name")
    receipt_url: Optional[str] = Field(None, description="Receipt image URL")
    notes: Optional[str] = Field(None, description="Additional notes")

class ExpenseCreate(ExpenseBase):
    """Expense creation schema"""
    pass

class ExpenseUpdate(BaseModel):
    """Expense update schema"""
    category: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, min_length=2, max_length=500)
    amount: Optional[float] = Field(None, gt=0)
    expense_date: Optional[date] = None
    payment_method: Optional[str] = None
    vendor: Optional[str] = None
    receipt_url: Optional[str] = None
    notes: Optional[str] = None

class ExpenseResponse(ExpenseBase):
    """Expense response schema"""
    id: str = Field(..., alias="_id")
    tenant_id: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True

class ExpenseListResponse(BaseModel):
    """Expense list response schema"""
    expenses: List[ExpenseResponse]
    total: int
    skip: int
    limit: int
