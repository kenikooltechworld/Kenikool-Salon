"""
Opt-Outs API endpoints
"""
from fastapi import APIRouter

router = APIRouter(tags=["opt-outs"])

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}
