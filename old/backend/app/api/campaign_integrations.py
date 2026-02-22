"""
Campaign Integrations API endpoints
"""
from fastapi import APIRouter

router = APIRouter(tags=["integrations"])

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}
