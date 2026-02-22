"""
Campaign Templates API endpoints
"""
from fastapi import APIRouter

router = APIRouter(tags=["campaign-templates"])

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}
