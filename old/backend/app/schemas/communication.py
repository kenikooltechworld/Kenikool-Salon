"""
Communication Schema
Tracks all client communications (SMS, Email, WhatsApp)
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class Communication(BaseModel):
    """Communication record"""
    client_id: str = Field(..., description="Client ID")
    tenant_id: str = Field(..., description="Tenant ID")
    channel: str = Field(..., description="Communication channel: sms, email, whatsapp")
    direction: str = Field(..., description="Direction: outbound, inbound")
    message_type: str = Field(..., description="Message type: booking_confirmation, reminder, birthday, marketing, manual")
    subject: Optional[str] = Field(None, description="Email subject or message title")
    content: str = Field(..., description="Message content")
    recipient: str = Field(..., description="Recipient phone/email")
    status: str = Field(default="pending", description="Status: pending, sent, delivered, read, failed")
    provider: Optional[str] = Field(None, description="Provider: termii, sendgrid, whatsapp_api")
    provider_message_id: Optional[str] = Field(None, description="Provider's message ID")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    sent_at: Optional[datetime] = Field(None, description="When message was sent")
    delivered_at: Optional[datetime] = Field(None, description="When message was delivered")
    read_at: Optional[datetime] = Field(None, description="When message was read")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class CommunicationCreate(BaseModel):
    """Create communication request"""
    client_id: str
    channel: str
    message_type: str
    subject: Optional[str] = None
    content: str
    recipient: str


class CommunicationResponse(BaseModel):
    """Communication response"""
    id: str
    client_id: str
    tenant_id: str
    channel: str
    direction: str
    message_type: str
    subject: Optional[str]
    content: str
    recipient: str
    status: str
    provider: Optional[str]
    error_message: Optional[str]
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    read_at: Optional[datetime]
    created_at: datetime


class CommunicationFilter(BaseModel):
    """Communication filter parameters"""
    client_id: Optional[str] = None
    channel: Optional[str] = None
    status: Optional[str] = None
    message_type: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    offset: int = 0
    limit: int = 20
