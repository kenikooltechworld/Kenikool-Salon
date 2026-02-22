"""
Dashboard API endpoints
"""
from fastapi import APIRouter, Depends, Query
from datetime import datetime, timedelta
from typing import Optional
import logging
from app.api.dependencies import get_current_user, get_tenant_id
from app.database import Database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def get_db():
    """Get database instance"""
    return Database.get_db()


@router.get("/revenue-chart")
async def get_revenue_chart(
    period: str = Query("daily"),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Get revenue chart data
    
    Args:
        period: Time period (daily, weekly, monthly)
    
    Returns:
        Revenue data for chart
    """
    try:
        now = datetime.now()
        
        # Determine date range and grouping
        if period == "daily":
            start_date = now - timedelta(days=7)
            group_format = "%Y-%m-%d"
        elif period == "weekly":
            start_date = now - timedelta(weeks=8)
            group_format = "%Y-W%V"
        else:  # monthly
            start_date = now - timedelta(days=365)
            group_format = "%Y-%m"
        
        # Get bookings for the period
        bookings = list(db.bookings.find({
            "tenant_id": tenant_id,
            "booking_date": {"$gte": start_date},
            "status": {"$in": ["completed", "confirmed"]}
        }))
        
        # Group by date and sum revenue
        revenue_by_date = {}
        for booking in bookings:
            booking_date = booking.get("booking_date")
            if booking_date:
                if isinstance(booking_date, str):
                    booking_date = datetime.fromisoformat(booking_date)
                date_key = booking_date.strftime(group_format)
                revenue = booking.get("total_amount", 0)
                revenue_by_date[date_key] = revenue_by_date.get(date_key, 0) + revenue
        
        # Format response
        data = [
            {"date": date, "revenue": revenue}
            for date, revenue in sorted(revenue_by_date.items())
        ]
        
        return {
            "data": data,
            "period": period,
            "total_revenue": sum(b.get("total_amount", 0) for b in bookings)
        }
    except Exception as e:
        logger.error(f"Error getting revenue chart: {e}")
        return {
            "data": [],
            "period": period,
            "total_revenue": 0,
            "error": str(e)
        }


@router.get("/top-services")
async def get_top_services(
    limit: int = Query(5, ge=1, le=20),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Get top performing services
    
    Args:
        limit: Number of services to return
    
    Returns:
        List of top services
    """
    try:
        # Get all bookings for the tenant (last 90 days)
        start_date = datetime.now() - timedelta(days=90)
        bookings = list(db.bookings.find({
            "tenant_id": tenant_id,
            "booking_date": {"$gte": start_date},
            "status": {"$in": ["completed", "confirmed"]}
        }))
        
        # Aggregate by service
        service_stats = {}
        for booking in bookings:
            service_id = str(booking.get("service_id", ""))
            if service_id:
                if service_id not in service_stats:
                    service_stats[service_id] = {
                        "booking_count": 0,
                        "revenue": 0,
                        "service_name": booking.get("service_name", "Unknown")
                    }
                service_stats[service_id]["booking_count"] += 1
                service_stats[service_id]["revenue"] += booking.get("total_amount", 0)
        
        # Sort by revenue and get top services
        sorted_services = sorted(
            service_stats.items(),
            key=lambda x: x[1]["revenue"],
            reverse=True
        )[:limit]
        
        # Calculate trend for each service (compare with previous 90 days)
        prev_start_date = start_date - timedelta(days=90)
        prev_bookings = list(db.bookings.find({
            "tenant_id": tenant_id,
            "booking_date": {"$gte": prev_start_date, "$lt": start_date},
            "status": {"$in": ["completed", "confirmed"]}
        }))
        
        prev_service_stats = {}
        for booking in prev_bookings:
            service_id = str(booking.get("service_id", ""))
            if service_id:
                if service_id not in prev_service_stats:
                    prev_service_stats[service_id] = {"revenue": 0}
                prev_service_stats[service_id]["revenue"] += booking.get("total_amount", 0)
        
        # Format response
        top_services = []
        for service_id, stats in sorted_services:
            prev_revenue = prev_service_stats.get(service_id, {}).get("revenue", 0)
            trend = ((stats["revenue"] - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
            
            top_services.append({
                "id": service_id,
                "name": stats["service_name"],
                "booking_count": stats["booking_count"],
                "revenue": stats["revenue"],
                "trend": round(trend, 1),
            })
        
        return {
            "services": top_services,
            "total": len(top_services),
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error getting top services: {e}")
        return {
            "services": [],
            "total": 0,
            "limit": limit,
            "error": str(e)
        }


@router.get("/staff-performance")
async def get_staff_performance(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Get staff performance metrics
    
    Returns:
        Staff performance data
    """
    try:
        # Get all bookings for the tenant (last 90 days)
        start_date = datetime.now() - timedelta(days=90)
        bookings = list(db.bookings.find({
            "tenant_id": tenant_id,
            "booking_date": {"$gte": start_date},
            "status": {"$in": ["completed", "confirmed"]}
        }))
        
        # Aggregate by stylist
        stylist_stats = {}
        for booking in bookings:
            stylist_id = str(booking.get("stylist_id", ""))
            if stylist_id:
                if stylist_id not in stylist_stats:
                    stylist_stats[stylist_id] = {
                        "total_bookings": 0,
                        "total_revenue": 0,
                        "ratings": [],
                        "stylist_name": booking.get("stylist_name", "Unknown")
                    }
                stylist_stats[stylist_id]["total_bookings"] += 1
                stylist_stats[stylist_id]["total_revenue"] += booking.get("total_amount", 0)
                
                # Collect ratings if available
                if booking.get("rating"):
                    stylist_stats[stylist_id]["ratings"].append(booking.get("rating"))
        
        # Calculate average ratings and sort by revenue
        staff_performance = []
        for stylist_id, stats in sorted(
            stylist_stats.items(),
            key=lambda x: x[1]["total_revenue"],
            reverse=True
        )[:5]:
            avg_rating = sum(stats["ratings"]) / len(stats["ratings"]) if stats["ratings"] else 0
            
            # Get stylist photo
            stylist = db.stylists.find_one({"_id": stylist_id})
            stylist_photo = stylist.get("photo_url") if stylist else None
            
            staff_performance.append({
                "stylist_id": stylist_id,
                "stylist_name": stats["stylist_name"],
                "stylist_photo": stylist_photo,
                "total_bookings": stats["total_bookings"],
                "total_revenue": stats["total_revenue"],
                "average_rating": round(avg_rating, 1),
                "clients_served": len(set(b.get("client_id") for b in bookings if b.get("stylist_id") == stylist_id)),
            })
        
        return {
            "staff": staff_performance,
            "total": len(staff_performance)
        }
    except Exception as e:
        logger.error(f"Error getting staff performance: {e}")
        return {
            "staff": [],
            "total": 0,
            "error": str(e)
        }


@router.get("/metrics")
async def get_dashboard_metrics(
    period: str = Query("month"),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Get dashboard metrics
    
    Args:
        period: Time period (day, week, month, year)
    
    Returns:
        Dashboard metrics data
    """
    try:
        from datetime import datetime, timedelta
        
        # Calculate date range based on period
        now = datetime.now()
        if period == "day":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "week":
            start_date = now - timedelta(days=now.weekday())
        elif period == "month":
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == "year":
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = now - timedelta(days=30)
        
        # Query bookings for the period
        bookings = list(db.bookings.find({
            "tenant_id": tenant_id,
            "booking_date": {"$gte": start_date}
        }))
        
        # Calculate metrics
        total_revenue = sum(booking.get("total_amount", 0) for booking in bookings)
        total_bookings = len(bookings)
        completed_bookings = len([b for b in bookings if b.get("status") == "completed"])
        pending_bookings = len([b for b in bookings if b.get("status") in ["pending", "confirmed"]])
        
        # Get unique clients
        client_ids = set()
        new_client_ids = set()
        for booking in bookings:
            if booking.get("client_id"):
                client_ids.add(booking.get("client_id"))
                # Check if this is a new client (first booking in this period)
                client_bookings = list(db.bookings.find({
                    "tenant_id": tenant_id,
                    "client_id": booking.get("client_id"),
                    "booking_date": {"$gte": start_date}
                }))
                if len(client_bookings) == 1:  # First booking in this period
                    new_client_ids.add(booking.get("client_id"))
        
        total_clients = len(client_ids)
        new_clients = len(new_client_ids)
        
        # Get unique services
        service_ids = set()
        for booking in bookings:
            if booking.get("service_id"):
                service_ids.add(booking.get("service_id"))
        total_services = len(service_ids)
        
        # Calculate retention rate (returning clients)
        returning_clients = total_clients - new_clients
        returning_client_percentage = (returning_clients / total_clients * 100) if total_clients > 0 else 0
        retention_rate = returning_client_percentage
        
        return {
            "period": period,
            "total_revenue": total_revenue,
            "revenue_trend": None,
            "total_bookings": total_bookings,
            "booking_trend": None,
            "new_clients": new_clients,
            "total_clients": total_clients,
            "client_trend": None,
            "returning_client_percentage": returning_client_percentage,
            "retention_rate": retention_rate,
            "total_services": total_services,
            "pending_bookings": pending_bookings,
            "completed_bookings": completed_bookings,
        }
    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {e}")
        return {
            "period": period,
            "total_revenue": 0,
            "revenue_trend": None,
            "total_bookings": 0,
            "booking_trend": None,
            "new_clients": 0,
            "total_clients": 0,
            "client_trend": None,
            "returning_client_percentage": 0,
            "retention_rate": 0,
            "total_services": 0,
            "pending_bookings": 0,
            "completed_bookings": 0,
            "error": str(e)
        }


@router.get("/overview")
async def get_dashboard_overview(
    period: str = Query("month"),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Get dashboard overview with key metrics
    
    Args:
        period: Time period (day, week, month, year)
    
    Returns:
        Dashboard overview data
    """
    try:
        # Calculate date range based on period
        now = datetime.now()
        if period == "day":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "week":
            start_date = now - timedelta(days=now.weekday())
        elif period == "month":
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == "year":
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = now - timedelta(days=30)
        
        # Get bookings for the period
        bookings = list(db.bookings.find({
            "tenant_id": tenant_id,
            "booking_date": {"$gte": start_date},
            "status": {"$in": ["completed", "confirmed"]}
        }))
        
        # Calculate top services
        service_stats = {}
        for booking in bookings:
            service_id = str(booking.get("service_id", ""))
            if service_id:
                if service_id not in service_stats:
                    service_stats[service_id] = {
                        "booking_count": 0,
                        "revenue": 0,
                        "service_name": booking.get("service_name", "Unknown")
                    }
                service_stats[service_id]["booking_count"] += 1
                service_stats[service_id]["revenue"] += booking.get("total_amount", 0)
        
        top_services = []
        for service_id, stats in sorted(
            service_stats.items(),
            key=lambda x: x[1]["revenue"],
            reverse=True
        )[:5]:
            # Calculate trend for each service
            prev_start_date = start_date - timedelta(days=90)
            prev_bookings = list(db.bookings.find({
                "tenant_id": tenant_id,
                "service_id": service_id,
                "booking_date": {"$gte": prev_start_date, "$lt": start_date},
                "status": {"$in": ["completed", "confirmed"]}
            }))
            prev_revenue = sum(b.get("total_amount", 0) for b in prev_bookings)
            trend = ((stats["revenue"] - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
            
            top_services.append({
                "id": service_id,
                "name": stats["service_name"],
                "booking_count": stats["booking_count"],
                "revenue": stats["revenue"],
                "trend": round(trend, 1),
            })
        
        # Calculate staff performance
        stylist_stats = {}
        for booking in bookings:
            stylist_id = str(booking.get("stylist_id", ""))
            if stylist_id:
                if stylist_id not in stylist_stats:
                    stylist_stats[stylist_id] = {
                        "total_bookings": 0,
                        "total_revenue": 0,
                        "ratings": [],
                        "stylist_name": booking.get("stylist_name", "Unknown")
                    }
                stylist_stats[stylist_id]["total_bookings"] += 1
                stylist_stats[stylist_id]["total_revenue"] += booking.get("total_amount", 0)
                if booking.get("rating"):
                    stylist_stats[stylist_id]["ratings"].append(booking.get("rating"))
        
        staff_performance = []
        for stylist_id, stats in sorted(
            stylist_stats.items(),
            key=lambda x: x[1]["total_revenue"],
            reverse=True
        )[:5]:
            avg_rating = sum(stats["ratings"]) / len(stats["ratings"]) if stats["ratings"] else 0
            stylist = db.stylists.find_one({"_id": stylist_id})
            staff_performance.append({
                "stylist_id": stylist_id,
                "stylist_name": stats["stylist_name"],
                "stylist_photo": stylist.get("photo_url") if stylist else None,
                "total_bookings": stats["total_bookings"],
                "total_revenue": stats["total_revenue"],
                "average_rating": round(avg_rating, 1),
                "clients_served": len(set(b.get("client_id") for b in bookings if b.get("stylist_id") == stylist_id)),
            })
        
        # Calculate revenue chart data
        revenue_by_date = {}
        for booking in bookings:
            booking_date = booking.get("booking_date")
            if booking_date:
                if isinstance(booking_date, str):
                    booking_date = datetime.fromisoformat(booking_date)
                date_key = booking_date.strftime("%Y-%m-%d")
                revenue = booking.get("total_amount", 0)
                revenue_by_date[date_key] = revenue_by_date.get(date_key, 0) + revenue
        
        revenue_chart = [
            {"date": date, "revenue": revenue}
            for date, revenue in sorted(revenue_by_date.items())
        ]
        
        # Calculate metrics
        total_revenue = sum(b.get("total_amount", 0) for b in bookings)
        total_bookings = len(bookings)
        
        # Get unique clients
        client_ids = set(b.get("client_id") for b in bookings if b.get("client_id"))
        total_clients = len(client_ids)
        
        # Calculate average rating
        ratings = [b.get("rating") for b in bookings if b.get("rating")]
        average_rating = sum(ratings) / len(ratings) if ratings else 0
        
        # Calculate growth rate (compare with previous period)
        prev_start_date = start_date - (now - start_date)
        prev_bookings = list(db.bookings.find({
            "tenant_id": tenant_id,
            "booking_date": {"$gte": prev_start_date, "$lt": start_date},
            "status": {"$in": ["completed", "confirmed"]}
        }))
        prev_revenue = sum(b.get("total_amount", 0) for b in prev_bookings)
        growth_rate = ((total_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
        
        return {
            "period": period,
            "start_date": start_date.isoformat(),
            "end_date": now.isoformat(),
            "total_revenue": total_revenue,
            "total_bookings": total_bookings,
            "total_clients": total_clients,
            "average_rating": round(average_rating, 1),
            "growth_rate": round(growth_rate, 1),
            "top_services": top_services,
            "staff_performance": staff_performance,
            "revenue_chart": revenue_chart,
        }
    except Exception as e:
        logger.error(f"Error getting dashboard overview: {e}")
        return {
            "error": str(e),
            "period": period,
            "total_revenue": 0,
            "total_bookings": 0,
            "total_clients": 0,
            "average_rating": 0,
            "growth_rate": 0,
            "top_services": [],
            "staff_performance": [],
            "revenue_chart": [],
        }


@router.get("/activity-feed")
async def get_activity_feed(
    limit: int = Query(10, ge=1, le=100),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Get recent activity feed from all sources
    """
    try:
        activities = []
        batch_limit = max(5, limit // 15)
        
        # 1. Bookings
        for booking in db.bookings.find({"tenant_id": tenant_id}).sort("booking_date", -1).limit(batch_limit):
            activity_type = "booking"
            if booking.get("status") == "cancelled":
                activity_type = "cancellation"
            elif booking.get("status") == "completed":
                activity_type = "booking_completed"
            activities.append({
                "id": str(booking.get("_id")),
                "type": activity_type,
                "source": "booking",
                "message": f"{booking.get('client_name', 'Client')} booked {booking.get('service_name', 'service')} with {booking.get('stylist_name', 'stylist')}",
                "timestamp": booking.get("booking_date", datetime.now()).isoformat() if isinstance(booking.get("booking_date"), datetime) else booking.get("booking_date"),
                "metadata": {"client_id": str(booking.get("client_id", "")), "amount": booking.get("total_amount", 0)}
            })
        
        # 2. Payments
        for payment in db.bookings.find({"tenant_id": tenant_id, "payment_status": "failed"}).sort("updated_at", -1).limit(batch_limit):
            activities.append({
                "id": f"payment_{str(payment.get('_id'))}",
                "type": "payment_failed",
                "source": "payment",
                "message": f"Payment failed for {payment.get('client_name', 'Client')}",
                "timestamp": payment.get("updated_at", datetime.now()).isoformat() if isinstance(payment.get("updated_at"), datetime) else payment.get("updated_at"),
                "metadata": {"amount": payment.get("total_amount", 0)}
            })
        
        # 3. Clients
        for client in db.clients.find({"tenant_id": tenant_id}).sort("created_at", -1).limit(batch_limit):
            activities.append({
                "id": f"client_{str(client.get('_id'))}",
                "type": "new_client",
                "source": "client",
                "message": f"New client: {client.get('name', 'Unknown')}",
                "timestamp": client.get("created_at", datetime.now()).isoformat() if isinstance(client.get("created_at"), datetime) else client.get("created_at"),
                "metadata": {"client_id": str(client.get("_id", ""))}
            })
        
        # 4. Reviews
        for review in db.reviews.find({"tenant_id": tenant_id}).sort("created_at", -1).limit(batch_limit):
            activities.append({
                "id": f"review_{str(review.get('_id'))}",
                "type": "review",
                "source": "review",
                "message": f"{review.get('client_name', 'Client')} left a {review.get('rating', 5)}-star review",
                "timestamp": review.get("created_at", datetime.now()).isoformat() if isinstance(review.get("created_at"), datetime) else review.get("created_at"),
                "metadata": {"rating": review.get("rating", 0)}
            })
        
        # 5. Gift Cards
        for gc in db.gift_cards.find({"tenant_id": tenant_id}).sort("created_at", -1).limit(batch_limit):
            activities.append({
                "id": f"giftcard_{str(gc.get('_id'))}",
                "type": "gift_card_purchased",
                "source": "gift_card",
                "message": f"Gift card purchased: {gc.get('amount', 0)} by {gc.get('buyer_name', 'Unknown')}",
                "timestamp": gc.get("created_at", datetime.now()).isoformat() if isinstance(gc.get("created_at"), datetime) else gc.get("created_at"),
                "metadata": {"amount": gc.get("amount", 0)}
            })
        
        # 6. Memberships
        for mem in db.memberships.find({"tenant_id": tenant_id}).sort("created_at", -1).limit(batch_limit):
            activities.append({
                "id": f"membership_{str(mem.get('_id'))}",
                "type": "membership_purchased",
                "source": "membership",
                "message": f"{mem.get('client_name', 'Client')} subscribed to {mem.get('plan_name', 'membership')}",
                "timestamp": mem.get("created_at", datetime.now()).isoformat() if isinstance(mem.get("created_at"), datetime) else mem.get("created_at"),
                "metadata": {"amount": mem.get("amount", 0)}
            })
        
        # 7. Inventory
        for inv in db.inventory.find({"tenant_id": tenant_id}).sort("updated_at", -1).limit(batch_limit):
            activities.append({
                "id": f"inventory_{str(inv.get('_id'))}",
                "type": "inventory_updated",
                "source": "inventory",
                "message": f"Inventory updated: {inv.get('name', 'Item')} - {inv.get('quantity', 0)} units",
                "timestamp": inv.get("updated_at", datetime.now()).isoformat() if isinstance(inv.get("updated_at"), datetime) else inv.get("updated_at"),
                "metadata": {"quantity": inv.get("quantity", 0)}
            })
        
        # 8. Staff/Stylists
        for staff in db.stylists.find({"tenant_id": tenant_id}).sort("created_at", -1).limit(batch_limit):
            activities.append({
                "id": f"staff_{str(staff.get('_id'))}",
                "type": "staff_added",
                "source": "staff",
                "message": f"New staff added: {staff.get('name', 'Unknown')}",
                "timestamp": staff.get("created_at", datetime.now()).isoformat() if isinstance(staff.get("created_at"), datetime) else staff.get("created_at"),
                "metadata": {"staff_id": str(staff.get("_id", ""))}
            })
        
        # 9. Waitlist
        for wl in db.waitlist.find({"tenant_id": tenant_id}).sort("created_at", -1).limit(batch_limit):
            activities.append({
                "id": f"waitlist_{str(wl.get('_id'))}",
                "type": "waitlist_added",
                "source": "waitlist",
                "message": f"{wl.get('client_name', 'Client')} added to waitlist for {wl.get('service_name', 'service')}",
                "timestamp": wl.get("created_at", datetime.now()).isoformat() if isinstance(wl.get("created_at"), datetime) else wl.get("created_at"),
                "metadata": {"client_id": str(wl.get("client_id", ""))}
            })
        
        # 10. Refunds
        for refund in db.bookings.find({"tenant_id": tenant_id, "refund_status": "completed"}).sort("updated_at", -1).limit(batch_limit):
            activities.append({
                "id": f"refund_{str(refund.get('_id'))}",
                "type": "refund_processed",
                "source": "refund",
                "message": f"Refund processed for {refund.get('client_name', 'Client')} - {refund.get('refund_amount', 0)}",
                "timestamp": refund.get("updated_at", datetime.now()).isoformat() if isinstance(refund.get("updated_at"), datetime) else refund.get("updated_at"),
                "metadata": {"amount": refund.get("refund_amount", 0)}
            })
        
        # 11. Promo Codes
        for promo in db.promo_codes.find({"tenant_id": tenant_id}).sort("created_at", -1).limit(batch_limit):
            activities.append({
                "id": f"promo_{str(promo.get('_id'))}",
                "type": "promo_created",
                "source": "promo",
                "message": f"Promo code created: {promo.get('code', 'N/A')} - {promo.get('discount', 0)}% off",
                "timestamp": promo.get("created_at", datetime.now()).isoformat() if isinstance(promo.get("created_at"), datetime) else promo.get("created_at"),
                "metadata": {"discount": promo.get("discount", 0)}
            })
        
        # 12. Loyalty Points
        for loyalty in db.loyalty_transactions.find({"tenant_id": tenant_id}).sort("created_at", -1).limit(batch_limit):
            activity_type = "loyalty_earned" if loyalty.get("type") == "earn" else "loyalty_redeemed"
            activities.append({
                "id": f"loyalty_{str(loyalty.get('_id'))}",
                "type": activity_type,
                "source": "loyalty",
                "message": f"{loyalty.get('client_name', 'Client')} {loyalty.get('type', 'earned')} {loyalty.get('points', 0)} loyalty points",
                "timestamp": loyalty.get("created_at", datetime.now()).isoformat() if isinstance(loyalty.get("created_at"), datetime) else loyalty.get("created_at"),
                "metadata": {"points": loyalty.get("points", 0)}
            })
        
        # 13. Campaigns
        for campaign in db.campaigns.find({"tenant_id": tenant_id}).sort("created_at", -1).limit(batch_limit):
            activities.append({
                "id": f"campaign_{str(campaign.get('_id'))}",
                "type": "campaign_created",
                "source": "campaign",
                "message": f"Campaign created: {campaign.get('name', 'N/A')}",
                "timestamp": campaign.get("created_at", datetime.now()).isoformat() if isinstance(campaign.get("created_at"), datetime) else campaign.get("created_at"),
                "metadata": {"campaign_id": str(campaign.get("_id", ""))}
            })
        
        # 14. Expenses
        for expense in db.expenses.find({"tenant_id": tenant_id}).sort("date", -1).limit(batch_limit):
            activities.append({
                "id": f"expense_{str(expense.get('_id'))}",
                "type": "expense_added",
                "source": "expense",
                "message": f"Expense added: {expense.get('category', 'Other')} - {expense.get('amount', 0)}",
                "timestamp": expense.get("date", datetime.now()).isoformat() if isinstance(expense.get("date"), datetime) else expense.get("date"),
                "metadata": {"amount": expense.get("amount", 0), "category": expense.get("category", "")}
            })
        
        # 15. Service Inquiries
        for inquiry in db.service_inquiries.find({"tenant_id": tenant_id}).sort("created_at", -1).limit(batch_limit):
            activities.append({
                "id": f"inquiry_{str(inquiry.get('_id'))}",
                "type": "service_inquiry",
                "source": "inquiry",
                "message": f"Service inquiry from {inquiry.get('client_name', 'Unknown')} for {inquiry.get('service_name', 'service')}",
                "timestamp": inquiry.get("created_at", datetime.now()).isoformat() if isinstance(inquiry.get("created_at"), datetime) else inquiry.get("created_at"),
                "metadata": {"client_id": str(inquiry.get("client_id", ""))}
            })
        
        # 16. Referrals
        for referral in db.referrals.find({"tenant_id": tenant_id}).sort("created_at", -1).limit(batch_limit):
            activities.append({
                "id": f"referral_{str(referral.get('_id'))}",
                "type": "referral_created",
                "source": "referral",
                "message": f"Referral from {referral.get('referrer_name', 'Unknown')} to {referral.get('referred_name', 'Unknown')}",
                "timestamp": referral.get("created_at", datetime.now()).isoformat() if isinstance(referral.get("created_at"), datetime) else referral.get("created_at"),
                "metadata": {"referrer_id": str(referral.get("referrer_id", ""))}
            })
        
        # Sort and limit
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        activities = activities[:limit]
        
        return {
            "activities": activities,
            "total": len(activities),
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error getting activity feed: {e}")
        return {
            "activities": [],
            "total": 0,
            "limit": limit,
            "error": str(e)
        }


@router.get("/alerts")
async def get_alerts(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Get dashboard alerts
    
    Returns:
        List of alerts
    """
    try:
        alerts = []
        
        # Check for pending bookings
        pending_bookings = db.bookings.count_documents({
            "tenant_id": tenant_id,
            "status": "pending"
        })
        if pending_bookings > 0:
            alerts.append({
                "id": "pending_bookings",
                "type": "pending_booking",
                "severity": "medium",
                "message": f"{pending_bookings} pending booking(s) awaiting confirmation",
                "action_url": "/dashboard/bookings"
            })
        
        # Check for low inventory
        low_inventory_items = list(db.inventory.find({
            "tenant_id": tenant_id,
            "quantity": {"$lt": 5}
        }).limit(5))
        if low_inventory_items:
            alerts.append({
                "id": "low_inventory",
                "type": "inventory",
                "severity": "high",
                "message": f"{len(low_inventory_items)} item(s) running low on inventory",
                "action_url": "/dashboard/inventory"
            })
        
        # Check for failed payments
        failed_payments = db.bookings.count_documents({
            "tenant_id": tenant_id,
            "payment_status": "failed"
        })
        if failed_payments > 0:
            alerts.append({
                "id": "failed_payments",
                "type": "payment_failure",
                "severity": "high",
                "message": f"{failed_payments} payment(s) failed",
                "action_url": "/dashboard/payments"
            })
        
        # Check for schedule conflicts
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        bookings_today = list(db.bookings.find({
            "tenant_id": tenant_id,
            "booking_date": {"$gte": today, "$lt": tomorrow},
            "status": {"$in": ["confirmed", "pending"]}
        }))
        
        # Simple conflict detection: same stylist at same time
        stylist_times = {}
        conflicts = 0
        for booking in bookings_today:
            stylist_id = str(booking.get("stylist_id", ""))
            booking_time = booking.get("booking_date")
            if stylist_id and booking_time:
                if stylist_id not in stylist_times:
                    stylist_times[stylist_id] = []
                stylist_times[stylist_id].append(booking_time)
        
        for times in stylist_times.values():
            if len(times) > 1:
                conflicts += 1
        
        if conflicts > 0:
            alerts.append({
                "id": "schedule_conflicts",
                "type": "schedule_conflict",
                "severity": "medium",
                "message": f"{conflicts} potential schedule conflict(s) detected",
                "action_url": "/dashboard/bookings"
            })
        
        return {
            "alerts": alerts,
            "total": len(alerts),
            "critical": len([a for a in alerts if a["severity"] == "high"]),
            "warning": len([a for a in alerts if a["severity"] == "medium"]),
            "info": len([a for a in alerts if a["severity"] == "low"])
        }
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        return {
            "alerts": [],
            "total": 0,
            "critical": 0,
            "warning": 0,
            "info": 0,
            "error": str(e)
        }


@router.get("/upcoming-events")
async def get_upcoming_events(
    days: int = Query(7, ge=1, le=365),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Get upcoming events/bookings
    
    Args:
        days: Number of days to look ahead
    
    Returns:
        List of upcoming events
    """
    try:
        now = datetime.now()
        future_date = now + timedelta(days=days)
        
        # Get bookings for the upcoming period
        bookings = list(db.bookings.find({
            "tenant_id": tenant_id,
            "booking_date": {"$gte": now, "$lte": future_date},
            "status": {"$in": ["confirmed", "pending"]}
        }).sort("booking_date", 1))
        
        # Group by date
        events_by_date = {}
        for booking in bookings:
            booking_date = booking.get("booking_date")
            if booking_date:
                if isinstance(booking_date, str):
                    booking_date = datetime.fromisoformat(booking_date)
                date_key = booking_date.strftime("%Y-%m-%d")
                if date_key not in events_by_date:
                    events_by_date[date_key] = {
                        "date": date_key,
                        "appointment_count": 0,
                        "is_fully_booked": False
                    }
                events_by_date[date_key]["appointment_count"] += 1
        
        events = list(events_by_date.values())
        
        return {
            "events": events,
            "total": len(events),
            "days": days
        }
    except Exception as e:
        logger.error(f"Error getting upcoming events: {e}")
        return {
            "events": [],
            "total": 0,
            "days": days,
            "error": str(e)
        }


@router.get("/expense-summary")
async def get_expense_summary(
    period: str = Query("month"),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Get expense summary
    
    Args:
        period: Time period (day, week, month, year)
    
    Returns:
        Expense summary data
    """
    try:
        # Calculate date range
        now = datetime.now()
        if period == "day":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "week":
            start_date = now - timedelta(days=now.weekday())
        elif period == "month":
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == "year":
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = now - timedelta(days=30)
        
        # Get expenses
        expenses = list(db.expenses.find({
            "tenant_id": tenant_id,
            "date": {"$gte": start_date}
        }))
        
        # Calculate totals by category
        total_expenses = 0
        by_category = {}
        for expense in expenses:
            amount = expense.get("amount", 0)
            category = expense.get("category", "Other")
            total_expenses += amount
            by_category[category] = by_category.get(category, 0) + amount
        
        # Get revenue for profit margin calculation
        bookings = list(db.bookings.find({
            "tenant_id": tenant_id,
            "booking_date": {"$gte": start_date},
            "status": {"$in": ["completed", "confirmed"]}
        }))
        total_revenue = sum(b.get("total_amount", 0) for b in bookings)
        
        # Calculate profit margin
        profit = total_revenue - total_expenses
        profit_margin = (profit / total_revenue * 100) if total_revenue > 0 else 0
        
        # Calculate expense trend (compare with previous period)
        prev_start_date = start_date - (now - start_date)
        prev_expenses = list(db.expenses.find({
            "tenant_id": tenant_id,
            "date": {"$gte": prev_start_date, "$lt": start_date}
        }))
        prev_total_expenses = sum(e.get("amount", 0) for e in prev_expenses)
        expense_trend = ((total_expenses - prev_total_expenses) / prev_total_expenses * 100) if prev_total_expenses > 0 else 0
        
        # Calculate breakdown
        breakdown = [
            {"category": cat, "amount": amount}
            for cat, amount in by_category.items()
        ]
        
        return {
            "period": period,
            "total_expenses": total_expenses,
            "by_category": by_category,
            "breakdown": breakdown,
            "profit_margin": round(profit_margin, 1),
            "total_revenue": total_revenue,
            "profit": profit,
            "expense_trend": round(expense_trend, 1)
        }
    except Exception as e:
        logger.error(f"Error getting expense summary: {e}")
        return {
            "period": period,
            "total_expenses": 0,
            "by_category": {},
            "breakdown": [],
            "profit_margin": 0,
            "error": str(e)
        }


@router.get("/waitlist-summary")
async def get_waitlist_summary(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Get waitlist summary
    
    Returns:
        Waitlist summary data
    """
    try:
        # Get all waitlist entries
        waitlist_entries = list(db.waitlist.find({
            "tenant_id": tenant_id,
            "status": {"$in": ["active", "pending"]}
        }))
        
        # Group by service
        by_service = {}
        urgent_count = 0
        for entry in waitlist_entries:
            service_id = str(entry.get("service_id", ""))
            service_name = entry.get("service_name", "Unknown")
            
            if service_id not in by_service:
                by_service[service_id] = {
                    "service_name": service_name,
                    "count": 0
                }
            by_service[service_id]["count"] += 1
            
            # Check if urgent (waiting for more than 7 days)
            created_at = entry.get("created_at")
            if created_at:
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at)
                days_waiting = (datetime.now() - created_at).days
                if days_waiting > 7:
                    urgent_count += 1
        
        # Format response
        by_service_list = [
            {"service_name": v["service_name"], "count": v["count"]}
            for v in by_service.values()
        ]
        
        return {
            "total_count": len(waitlist_entries),
            "by_service": by_service_list,
            "urgent_count": urgent_count
        }
    except Exception as e:
        logger.error(f"Error getting waitlist summary: {e}")
        return {
            "total_count": 0,
            "by_service": [],
            "urgent_count": 0,
            "error": str(e)
        }


@router.get("/quick-stats")
async def get_quick_stats(
    period: str = Query("month"),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Get quick statistics
    
    Args:
        period: Time period (day, week, month, year)
    
    Returns:
        Quick statistics
    """
    try:
        # Calculate date range
        now = datetime.now()
        if period == "day":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "week":
            start_date = now - timedelta(days=now.weekday())
        elif period == "month":
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == "year":
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = now - timedelta(days=30)
        
        # Get bookings
        bookings = list(db.bookings.find({
            "tenant_id": tenant_id,
            "booking_date": {"$gte": start_date}
        }))
        
        # Calculate stats
        total_bookings = len(bookings)
        completed_bookings = len([b for b in bookings if b.get("status") == "completed"])
        cancelled_bookings = len([b for b in bookings if b.get("status") == "cancelled"])
        
        total_revenue = sum(b.get("total_amount", 0) for b in bookings if b.get("status") in ["completed", "confirmed"])
        avg_booking_value = (total_revenue / total_bookings) if total_bookings > 0 else 0
        
        # Calculate cancellation rate
        cancellation_rate = (cancelled_bookings / total_bookings * 100) if total_bookings > 0 else 0
        
        # Calculate no-show rate (bookings that were confirmed but not completed)
        no_show_bookings = len([b for b in bookings if b.get("status") == "no_show"])
        no_show_rate = (no_show_bookings / total_bookings * 100) if total_bookings > 0 else 0
        
        # Calculate online booking percentage
        online_bookings = len([b for b in bookings if b.get("booking_source") == "online"])
        online_booking_percentage = (online_bookings / total_bookings * 100) if total_bookings > 0 else 0
        
        # Get gift card sales
        gift_card_sales = db.gift_cards.count_documents({
            "tenant_id": tenant_id,
            "created_at": {"$gte": start_date},
            "status": "active"
        })
        
        # Get loyalty points redeemed
        loyalty_transactions = list(db.loyalty_transactions.find({
            "tenant_id": tenant_id,
            "created_at": {"$gte": start_date},
            "type": "redemption"
        }))
        loyalty_points_redeemed = sum(t.get("points", 0) for t in loyalty_transactions)
        
        # Get pending tasks
        pending_tasks = db.bookings.count_documents({
            "tenant_id": tenant_id,
            "status": "pending"
        })
        
        return {
            "period": period,
            "avg_booking_value": round(avg_booking_value, 2),
            "cancellation_rate": round(cancellation_rate, 1),
            "no_show_rate": round(no_show_rate, 1),
            "online_booking_percentage": round(online_booking_percentage, 1),
            "gift_card_sales": gift_card_sales,
            "loyalty_points_redeemed": loyalty_points_redeemed,
            "total_bookings": total_bookings,
            "total_revenue": total_revenue,
            "pending_tasks": pending_tasks
        }
    except Exception as e:
        logger.error(f"Error getting quick stats: {e}")
        return {
            "period": period,
            "avg_booking_value": 0,
            "cancellation_rate": 0,
            "no_show_rate": 0,
            "online_booking_percentage": 0,
            "gift_card_sales": 0,
            "loyalty_points_redeemed": 0,
            "error": str(e)
        }
