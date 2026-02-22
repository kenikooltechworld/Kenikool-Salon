"""
Delivery Tracking API endpoints
"""
from fastapi import APIRouter

router = APIRouter(tags=["delivery-tracking"])

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}
