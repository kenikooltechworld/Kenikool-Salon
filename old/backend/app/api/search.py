"""
Global Search API endpoints
Provides unified search across multiple entities (clients, services, inventory, etc.)
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional, List, Dict, Any
import logging
from bson import ObjectId

from app.api.dependencies import get_current_user, get_tenant_id
from app.database import Database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/search", tags=["search"])


def get_db():
    """Get database instance"""
    return Database.get_db()


@router.get("", response_model=Dict[str, Any])
async def global_search(
    query: str = Query(..., min_length=1, description="Search query"),
    categories: Optional[List[str]] = Query(None, description="Categories to search in: clients, services, inventory, stylists, bookings"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results per category"),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """
    Global search across multiple entities
    
    Args:
        query: Search term
        categories: List of categories to search in (default: all)
        limit: Maximum results per category
        tenant_id: Current tenant ID
        current_user: Current authenticated user
    
    Returns:
        Dictionary with search results grouped by category
    """
    try:
        db = get_db()
        
        # Default categories if none specified
        if not categories:
            categories = ["clients", "services", "inventory", "stylists", "bookings"]
        
        results = {}
        total_results = 0
        
        # Search clients
        if "clients" in categories:
            clients = list(db.clients.find({
                "tenant_id": tenant_id,
                "$or": [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"phone": {"$regex": query, "$options": "i"}},
                    {"email": {"$regex": query, "$options": "i"}},
                ]
            }).limit(limit))
            
            # Format client results
            client_results = []
            for client in clients:
                client_results.append({
                    "id": str(client["_id"]),
                    "type": "client",
                    "title": client.get("name", "Unknown"),
                    "subtitle": client.get("phone", ""),
                    "description": client.get("email", ""),
                    "url": f"/clients/{str(client['_id'])}",
                    "avatar": client.get("photo_url"),
                })
            
            results["clients"] = {
                "items": client_results,
                "total": len(client_results),
                "category": "Clients"
            }
            total_results += len(client_results)
        
        # Search services
        if "services" in categories:
            services = list(db.services.find({
                "tenant_id": tenant_id,
                "is_active": True,
                "$or": [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"description": {"$regex": query, "$options": "i"}},
                    {"category": {"$regex": query, "$options": "i"}},
                ]
            }).limit(limit))
            
            # Format service results
            service_results = []
            for service in services:
                service_results.append({
                    "id": str(service["_id"]),
                    "type": "service",
                    "title": service.get("name", "Unknown"),
                    "subtitle": f"${service.get('price', 0)} • {service.get('duration_minutes', 0)}min",
                    "description": service.get("description", ""),
                    "url": f"/services/{str(service['_id'])}",
                    "avatar": service.get("photo_url"),
                })
            
            results["services"] = {
                "items": service_results,
                "total": len(service_results),
                "category": "Services"
            }
            total_results += len(service_results)
        
        # Search inventory
        if "inventory" in categories:
            inventory = list(db.inventory.find({
                "tenant_id": tenant_id,
                "$or": [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"sku": {"$regex": query, "$options": "i"}},
                    {"category": {"$regex": query, "$options": "i"}},
                ]
            }).limit(limit))
            
            # Format inventory results
            inventory_results = []
            for item in inventory:
                inventory_results.append({
                    "id": str(item["_id"]),
                    "type": "inventory",
                    "title": item.get("name", "Unknown"),
                    "subtitle": f"SKU: {item.get('sku', 'N/A')} • Qty: {item.get('quantity', 0)}",
                    "description": item.get("category", ""),
                    "url": f"/inventory/{str(item['_id'])}",
                    "avatar": None,
                })
            
            results["inventory"] = {
                "items": inventory_results,
                "total": len(inventory_results),
                "category": "Inventory"
            }
            total_results += len(inventory_results)
        
        # Search stylists
        if "stylists" in categories:
            stylists = list(db.stylists.find({
                "tenant_id": tenant_id,
                "is_active": True,
                "$or": [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"email": {"$regex": query, "$options": "i"}},
                    {"phone": {"$regex": query, "$options": "i"}},
                    {"specialties": {"$regex": query, "$options": "i"}},
                ]
            }).limit(limit))
            
            # Format stylist results
            stylist_results = []
            for stylist in stylists:
                stylist_results.append({
                    "id": str(stylist["_id"]),
                    "type": "stylist",
                    "title": stylist.get("name", "Unknown"),
                    "subtitle": stylist.get("phone", ""),
                    "description": ", ".join(stylist.get("specialties", [])),
                    "url": f"/stylists/{str(stylist['_id'])}",
                    "avatar": stylist.get("photo_url"),
                })
            
            results["stylists"] = {
                "items": stylist_results,
                "total": len(stylist_results),
                "category": "Staff"
            }
            total_results += len(stylist_results)
        
        # Search bookings
        if "bookings" in categories:
            bookings = list(db.bookings.find({
                "tenant_id": tenant_id,
                "$or": [
                    {"client_name": {"$regex": query, "$options": "i"}},
                    {"service_name": {"$regex": query, "$options": "i"}},
                    {"stylist_name": {"$regex": query, "$options": "i"}},
                ]
            }).limit(limit))
            
            # Format booking results
            booking_results = []
            for booking in bookings:
                booking_results.append({
                    "id": str(booking["_id"]),
                    "type": "booking",
                    "title": f"{booking.get('client_name', 'Unknown')} - {booking.get('service_name', 'Service')}",
                    "subtitle": f"with {booking.get('stylist_name', 'Staff')}",
                    "description": booking.get("booking_date", "").split("T")[0] if booking.get("booking_date") else "",
                    "url": f"/bookings/{str(booking['_id'])}",
                    "avatar": None,
                })
            
            results["bookings"] = {
                "items": booking_results,
                "total": len(booking_results),
                "category": "Bookings"
            }
            total_results += len(booking_results)
        
        return {
            "query": query,
            "total_results": total_results,
            "categories": list(results.keys()),
            "results": results,
            "suggestions": _generate_search_suggestions(query, db, tenant_id) if total_results == 0 else []
        }
        
    except Exception as e:
        logger.error(f"Error in global search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed. Please try again."
        )


def _generate_search_suggestions(query: str, db, tenant_id: str) -> List[str]:
    """Generate search suggestions when no results found"""
    try:
        suggestions = []
        
        # Get popular client names
        clients = list(db.clients.find(
            {"tenant_id": tenant_id},
            {"name": 1}
        ).limit(5))
        suggestions.extend([c.get("name", "") for c in clients if c.get("name")])
        
        # Get popular service names
        services = list(db.services.find(
            {"tenant_id": tenant_id, "is_active": True},
            {"name": 1}
        ).limit(5))
        suggestions.extend([s.get("name", "") for s in services if s.get("name")])
        
        # Get stylist names
        stylists = list(db.stylists.find(
            {"tenant_id": tenant_id, "is_active": True},
            {"name": 1}
        ).limit(3))
        suggestions.extend([s.get("name", "") for s in stylists if s.get("name")])
        
        return suggestions[:8]  # Return max 8 suggestions
        
    except Exception:
        return []


@router.get("/suggestions", response_model=List[str])
async def get_search_suggestions(
    query: Optional[str] = Query(None, description="Partial query for suggestions"),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """
    Get search suggestions based on partial query
    
    Args:
        query: Partial search query
        tenant_id: Current tenant ID
        current_user: Current authenticated user
    
    Returns:
        List of search suggestions
    """
    try:
        db = get_db()
        
        if not query or len(query) < 2:
            # Return popular searches
            return [
                "Hair Cut", "Hair Color", "Manicure", "Pedicure", 
                "Facial", "Massage", "Eyebrow", "Makeup"
            ]
        
        suggestions = set()
        
        # Client name suggestions
        clients = list(db.clients.find({
            "tenant_id": tenant_id,
            "name": {"$regex": f"^{query}", "$options": "i"}
        }, {"name": 1}).limit(5))
        suggestions.update([c.get("name", "") for c in clients if c.get("name")])
        
        # Service name suggestions
        services = list(db.services.find({
            "tenant_id": tenant_id,
            "is_active": True,
            "name": {"$regex": f"^{query}", "$options": "i"}
        }, {"name": 1}).limit(5))
        suggestions.update([s.get("name", "") for s in services if s.get("name")])
        
        # Stylist name suggestions
        stylists = list(db.stylists.find({
            "tenant_id": tenant_id,
            "is_active": True,
            "name": {"$regex": f"^{query}", "$options": "i"}
        }, {"name": 1}).limit(3))
        suggestions.update([s.get("name", "") for s in stylists if s.get("name")])
        
        return list(suggestions)[:10]  # Return max 10 suggestions
        
    except Exception as e:
        logger.error(f"Error getting search suggestions: {e}")
        return []