"""
Campaign Budget API endpoints
"""
from fastapi import APIRouter

router = APIRouter(tags=["campaign-budget"])

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}
