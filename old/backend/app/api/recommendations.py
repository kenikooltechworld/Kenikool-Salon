"""
Recommendations API Endpoints

Provides AI-powered salon recommendations using Mapbox MCP Server.

Requirements: 15.1, 15.2, 15.3, 15.4, 15.5
"""

import logging
from typing import Any, Dict, Optional, List

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


# ============================================================================
# Request/Response Models
# ============================================================================


class PreferencesModel(BaseModel):
    max_distance_km: Optional[float] = None
    min_rating: Optional[float] = None
    price_range: Optional[str] = None  # "budget", "moderate", "premium"
    availability: Optional[str] = None  # "immediate", "today", "this_week"


class RecommendationRequest(BaseModel):
    latitude: float
    longitude: float
    service_type: Optional[str] = None
    preferences: Optional[PreferencesModel] = None
    query: Optional[str] = None


class NaturalLanguageRequest(BaseModel):
    query: str
    latitude: float
    longitude: float


class RateRecommendationRequest(BaseModel):
    recommendation_id: str
    rating: int  # 1-5
    feedback: Optional[str] = None


class SalonRecommendation(BaseModel):
    salon_id: str
    name: str
    distance_km: float
    rating: float
    reviews: int
    reasoning: str
    match_score: float
    available_services: List[str]
    estimated_wait_time_minutes: Optional[int] = None


class RecommendationResponse(BaseModel):
    recommendations: List[SalonRecommendation]
    reasoning: str
    search_context: Dict[str, Any]


# ============================================================================
# Recommendation Endpoints
# ============================================================================


@router.post("/salons", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest) -> RecommendationResponse:
    """
    Get AI-powered salon recommendations
    
    Requirement 15.1, 15.2: Use Mapbox MCP Server for intelligent recommendations
    
    Args:
        request: Recommendation request with location and preferences
    
    Returns:
        List of recommended salons with reasoning
    
    Raises:
        HTTPException: If recommendation generation fails
    """
    try:
        from app.services.mcp_server_service import MCPServerService
        
        service = MCPServerService()
        
        recommendations = await service.get_salon_recommendations(
            latitude=request.latitude,
            longitude=request.longitude,
            service_type=request.service_type,
            preferences=request.preferences.dict() if request.preferences else None,
            query=request.query,
        )
        
        return recommendations
    
    except Exception as e:
        logger.error(f"Failed to get recommendations: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get recommendations",
        )


@router.post("/natural-language", response_model=RecommendationResponse)
async def get_natural_language_recommendations(
    request: NaturalLanguageRequest,
) -> RecommendationResponse:
    """
    Get recommendations based on natural language query
    
    Requirement 15.3: Process recommendation requests with reasoning
    
    Args:
        request: Natural language query with location
    
    Returns:
        List of recommended salons with reasoning
    
    Raises:
        HTTPException: If recommendation generation fails
    """
    try:
        from app.services.mcp_server_service import MCPServerService
        
        service = MCPServerService()
        
        recommendations = await service.get_natural_language_recommendations(
            query=request.query,
            latitude=request.latitude,
            longitude=request.longitude,
        )
        
        return recommendations
    
    except Exception as e:
        logger.error(f"Failed to get natural language recommendations: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get recommendations",
        )


@router.get("/trending", response_model=Dict[str, Any])
async def get_trending_salons(
    latitude: float = Query(..., description="User latitude"),
    longitude: float = Query(..., description="User longitude"),
    limit: int = Query(5, ge=1, le=20),
) -> Dict[str, Any]:
    """
    Get trending salons in an area
    
    Args:
        latitude: User latitude
        longitude: User longitude
        limit: Maximum number of results
    
    Returns:
        List of trending salons
    
    Raises:
        HTTPException: If query fails
    """
    try:
        from app.services.mcp_server_service import MCPServerService
        
        service = MCPServerService()
        
        salons = await service.get_trending_salons(
            latitude=latitude,
            longitude=longitude,
            limit=limit,
        )
        
        return {"salons": salons}
    
    except Exception as e:
        logger.error(f"Failed to get trending salons: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get trending salons",
        )


@router.get("/personalized/{customer_id}", response_model=Dict[str, Any])
async def get_personalized_recommendations(
    customer_id: str,
    limit: int = Query(5, ge=1, le=20),
) -> Dict[str, Any]:
    """
    Get personalized recommendations for a customer
    
    Args:
        customer_id: Customer ID
        limit: Maximum number of results
    
    Returns:
        List of personalized recommendations
    
    Raises:
        HTTPException: If query fails
    """
    try:
        from app.services.mcp_server_service import MCPServerService
        
        service = MCPServerService()
        
        salons = await service.get_personalized_recommendations(
            customer_id=customer_id,
            limit=limit,
        )
        
        return {"salons": salons}
    
    except Exception as e:
        logger.error(f"Failed to get personalized recommendations: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get personalized recommendations",
        )


@router.get("/similar/{salon_id}", response_model=Dict[str, Any])
async def get_similar_salons(
    salon_id: str,
    limit: int = Query(5, ge=1, le=20),
) -> Dict[str, Any]:
    """
    Get recommendations similar to a specific salon
    
    Args:
        salon_id: Salon ID
        limit: Maximum number of results
    
    Returns:
        List of similar salons
    
    Raises:
        HTTPException: If query fails
    """
    try:
        from app.services.mcp_server_service import MCPServerService
        
        service = MCPServerService()
        
        salons = await service.get_similar_salons(
            salon_id=salon_id,
            limit=limit,
        )
        
        return {"salons": salons}
    
    except Exception as e:
        logger.error(f"Failed to get similar salons: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get similar salons",
        )


@router.post("/rate", response_model=Dict[str, Any])
async def rate_recommendation(request: RateRecommendationRequest) -> Dict[str, Any]:
    """
    Rate a recommendation (for improving AI model)
    
    Args:
        request: Rating request
    
    Returns:
        Confirmation message
    
    Raises:
        HTTPException: If rating fails
    """
    try:
        from app.services.mcp_server_service import MCPServerService
        
        service = MCPServerService()
        
        await service.rate_recommendation(
            recommendation_id=request.recommendation_id,
            rating=request.rating,
            feedback=request.feedback,
        )
        
        return {"message": "Recommendation rated successfully"}
    
    except Exception as e:
        logger.error(f"Failed to rate recommendation: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to rate recommendation",
        )


@router.get("/stats", response_model=Dict[str, Any])
async def get_recommendation_stats() -> Dict[str, Any]:
    """
    Get recommendation statistics
    
    Returns:
        Statistics about recommendations
    
    Raises:
        HTTPException: If query fails
    """
    try:
        from app.services.mcp_server_service import MCPServerService
        
        service = MCPServerService()
        
        stats = await service.get_recommendation_stats()
        
        return stats
    
    except Exception as e:
        logger.error(f"Failed to get recommendation stats: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get recommendation stats",
        )
