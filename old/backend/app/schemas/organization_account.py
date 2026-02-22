"""
Organization Account schemas
"""
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict
from datetime import datetime


class EmployeeAdd(BaseModel):
    """Add employee to organization"""
    name: str
    email: EmailStr
    phone: str
    department: Optional[str] = None
    position: Optional[str] = None


class OrganizationEmployee(BaseModel):
    """Organization employee"""
    id: str
    name: str
    email: str
    phone: str
    department: Optional[str] = None
    position: Optional[str] = None
    added_at: datetime


class ContractTerms(BaseModel):
    """Contract terms for organization"""
    discount_percentage: Optional[float] = 0
    payment_terms: Optional[str] = "net_30"
    min_booking_value: Optional[float] = 0
    max_credit_limit: Optional[float] = 0


class OrganizationAccountCreate(BaseModel):
    """Create organization account"""
    company_name: str
    company_email: EmailStr
    company_phone: str
    industry: Optional[str] = None
    employee_count: Optional[int] = 0
    contract_terms: Optional[ContractTerms] = None
    credit_limit: Optional[float] = 0


class OrganizationAccount(BaseModel):
    """Organization account"""
    id: str
    company_name: str
    company_email: str
    company_phone: str
    industry: Optional[str] = None
    employee_count: int
    employees: List[OrganizationEmployee]
    contract_terms: Optional[ContractTerms] = None
    credit_limit: float
    current_balance: float
    status: str
    created_at: datetime
    updated_at: datetime


class EmployeeBooking(BaseModel):
    """Employee booking in organization booking"""
    employee_id: str
    services: List[str]  # service IDs
    stylist_id: str
    booking_date: str


class OrganizationBookingCreate(BaseModel):
    """Create organization booking"""
    employee_bookings: List[EmployeeBooking]
    deferred_payment: Optional[bool] = False
    contract_reference: Optional[str] = None
