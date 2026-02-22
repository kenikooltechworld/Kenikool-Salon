"""
Segments API endpoints
"""
from fastapi import APIRouter

router = APIRouter(tags=["segments"])

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}
