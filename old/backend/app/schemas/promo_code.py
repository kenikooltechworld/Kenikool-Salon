"""
Promo code schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class PromoCodeBase(BaseModel):
    """Base promo code schema"""
    code: str = Field(..., min_length=3, max_length=50, description="Promo code (will be uppercased)")
    description: Optional[str] = Field(None, description="Promo code description")
    discount_type: str = Field(..., pattern="^(percentage|fixed)$", description="Discount type: percentage or fixed")
    discount_value: float = Field(..., gt=0, description="Discount value (percentage or fixed amount)")
    min_purchase_amount: Optional[float] = Field(None, description="Minimum purchase amount required")
    max_discount_amount: Optional[float] = Field(None, description="Maximum discount amount cap")
    is_active: bool = Field(default=True, description="Whether promo code is active")
    valid_from: Optional[datetime] = Field(None, description="Promo code validity start date")
    valid_until: Optional[datetime] = Field(None, description="Promo code validity end date")
    max_uses: Optional[int] = Field(None, description="Maximum total uses")
    max_uses_per_client: Optional[int] = Field(default=1, description="Maximum uses per client")
    applicable_services: List[str] = Field(default=[], description="Service IDs (empty = all services)")

class PromoCodeCreate(PromoCodeBase):
    """Promo code creation schema"""
    pass

class PromoCodeUpdate(BaseModel):
    """Promo code update schema"""
    code: Optional[str] = Field(None, min_length=3, max_length=50)
    description: Optional[str] = None
    discount_type: Optional[str] = Field(None, pattern="^(percentage|fixed)$")
    discount_value: Optional[float] = Field(None, gt=0)
    min_purchase_amount: Optional[float] = None
    max_discount_amount: Optional[float] = None
    is_active: Optional[bool] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    max_uses: Optional[int] = None
    max_uses_per_client: Optional[int] = None
    applicable_services: Optional[List[str]] = None

class PromoCodeResponse(PromoCodeBase):
    """Promo code response schema"""
    id: str = Field(..., alias="_id")
    tenant_id: str
    current_uses: int = Field(default=0, description="Current number of uses")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True

class PromoCodeListResponse(BaseModel):
    """Promo code list response schema"""
    promo_codes: List[PromoCodeResponse]
    total: int

class PromoCodeValidateRequest(BaseModel):
    """Promo code validation request schema"""
    code: str = Field(..., description="Promo code to validate")
    client_id: str = Field(..., description="Client ID")
    service_ids: List[str] = Field(..., description="Service IDs in booking")
    total_amount: float = Field(..., gt=0, description="Total booking amount")

class PromoCodeValidationResponse(BaseModel):
    """Promo code validation response schema"""
    valid: bool = Field(..., description="Whether promo code is valid")
    error: Optional[str] = Field(None, description="Error message if invalid")
    promo_code_id: Optional[str] = Field(None, description="Promo code ID if valid")
    code: Optional[str] = Field(None, description="Promo code if valid")
    discount_amount: Optional[float] = Field(None, description="Discount amount if valid")
    final_amount: Optional[float] = Field(None, description="Final amount after discount if valid")
