"""TimeOffRequest schemas for request/response validation."""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import date


class TimeOffRequestCreate(BaseModel):
    """Schema for creating a time-off request."""

    staff_id: str = Field(..., description="Staff ID")
    start_date: date = Field(..., description="Start date of time off")
    end_date: date = Field(..., description="End date of time off")
    reason: str = Field(..., max_length=500, description="Reason for time off")


class TimeOffRequestUpdate(BaseModel):
    """Schema for updating a time-off request."""

    start_date: Optional[date] = Field(None, description="Start date of time off")
    end_date: Optional[date] = Field(None, description="End date of time off")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for time off")


class TimeOffRequestApprove(BaseModel):
    """Schema for approving a time-off request."""

    pass


class TimeOffRequestDeny(BaseModel):
    """Schema for denying a time-off request."""

    denial_reason: Optional[str] = Field(None, max_length=500, description="Reason for denial")


class TimeOffRequestResponse(BaseModel):
    """Schema for time-off request response."""

    id: str = Field(..., description="Request ID")
    staff_id: str = Field(..., description="Staff ID")
    start_date: str = Field(..., description="Start date of time off")
    end_date: str = Field(..., description="End date of time off")
    reason: str = Field(..., description="Reason for time off")
    status: str = Field(..., description="Request status")
    requested_at: str = Field(..., description="When request was made")
    reviewed_at: Optional[str] = Field(None, description="When request was reviewed")
    reviewed_by: Optional[str] = Field(None, description="User ID of reviewer")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Update timestamp")

    class Config:
        """Pydantic config."""

        from_attributes = True


class TimeOffRequestListResponse(BaseModel):
    """Schema for time-off request list response."""

    requests: List[TimeOffRequestResponse] = Field(..., description="List of time-off requests")
    total: int = Field(..., description="Total number of requests")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Page size")
