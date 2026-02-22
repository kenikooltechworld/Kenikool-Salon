"""
A/B Testing API endpoints
"""
from fastapi import APIRouter

router = APIRouter(tags=["ab-testing"])

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}
