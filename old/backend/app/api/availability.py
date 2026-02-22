"""
Availability API endpoints for checking stylist/service availability
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional, List
from datetime import datetime, timedelta
from bson import ObjectId

from app.api.dependencies import get_current_user, get_tenant_id
from app.database import Database

router = APIRouter(prefix="/api/availability", tags=["availability"])


def get_db():
    """Get database instance"""
    return Database.get_db()


@router.get("", response_model=dict)
async def get_availability(
    stylist_id: str = Query(..., description="Stylist ID"),
    service_id: str = Query(..., description="Service ID"),
    date: str = Query(..., description="Date (YYYY-MM-DD)"),
    location_id: Optional[str] = Query(None, description="Location ID"),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """Get available time slots for a stylist on a specific date"""
    try:
        # Parse the date
        booking_date = datetime.strptime(date, "%Y-%m-%d")
        
        # Get service to find duration
        service = db.services.find_one({
            "_id": ObjectId(service_id),
            "tenant_id": tenant_id
        })
        
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        service_duration = service.get("duration_minutes", 60)
        
        # Get stylist's schedule/availability
        stylist = db.stylists.find_one({
            "_id": ObjectId(stylist_id),
            "tenant_id": tenant_id
        })
        
        if not stylist:
            raise HTTPException(status_code=404, detail="Stylist not found")
        
        # Get all bookings for this stylist on this date
        bookings = list(db.bookings.find({
            "tenant_id": tenant_id,
            "stylist_id": stylist_id,
            "booking_date": {
                "$gte": booking_date,
                "$lt": booking_date + timedelta(days=1)
            },
            "status": {"$in": ["pending", "confirmed", "completed"]}
        }))
        
        # Define working hours (9 AM to 6 PM, 30-minute slots)
        working_hours = {
            "start": 9,
            "end": 18,
            "slot_duration": 30
        }
        
        # Generate all possible time slots
        available_slots = []
        current_hour = working_hours["start"]
        current_minute = 0
        
        while current_hour < working_hours["end"]:
            slot_start = booking_date.replace(hour=current_hour, minute=current_minute)
            slot_end = slot_start + timedelta(minutes=service_duration)
            
            # Check if slot is within working hours
            if slot_end.hour > working_hours["end"] or (slot_end.hour == working_hours["end"] and slot_end.minute > 0):
                current_minute += working_hours["slot_duration"]
                if current_minute >= 60:
                    current_hour += 1
                    current_minute = 0
                continue
            
            # Check if slot conflicts with existing bookings
            is_available = True
            for booking in bookings:
                booking_start = booking.get("booking_date")
                booking_duration = booking.get("service_duration", 60)
                booking_end = booking_start + timedelta(minutes=booking_duration)
                
                # Check for overlap
                if not (slot_end <= booking_start or slot_start >= booking_end):
                    is_available = False
                    break
            
            if is_available:
                available_slots.append({
                    "time": slot_start.strftime("%H:%M"),
                    "timestamp": slot_start.isoformat(),
                    "available": True
                })
            
            current_minute += working_hours["slot_duration"]
            if current_minute >= 60:
                current_hour += 1
                current_minute = 0
        
        return {
            "date": date,
            "stylist_id": stylist_id,
            "stylist_name": stylist.get("name"),
            "service_id": service_id,
            "service_name": service.get("name"),
            "service_duration": service_duration,
            "available_slots": available_slots,
            "total_available": len(available_slots),
            "working_hours": {
                "start": f"{working_hours['start']:02d}:00",
                "end": f"{working_hours['end']:02d}:00"
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bulk", response_model=dict)
async def get_bulk_availability(
    stylist_ids: str = Query(..., description="Comma-separated stylist IDs"),
    service_id: str = Query(..., description="Service ID"),
    date_from: str = Query(..., description="Start date (YYYY-MM-DD)"),
    date_to: str = Query(..., description="End date (YYYY-MM-DD)"),
    location_id: Optional[str] = Query(None, description="Location ID"),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """Get availability for multiple stylists across a date range"""
    try:
        stylist_id_list = [s.strip() for s in stylist_ids.split(",")]
        start_date = datetime.strptime(date_from, "%Y-%m-%d")
        end_date = datetime.strptime(date_to, "%Y-%m-%d")
        
        availability_map = {}
        
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            availability_map[date_str] = {}
            
            for stylist_id in stylist_id_list:
                try:
                    stylist = db.stylists.find_one({
                        "_id": ObjectId(stylist_id),
                        "tenant_id": tenant_id
                    })
                    
                    if not stylist:
                        continue
                    
                    # Get bookings for this stylist on this date
                    bookings = list(db.bookings.find({
                        "tenant_id": tenant_id,
                        "stylist_id": stylist_id,
                        "booking_date": {
                            "$gte": current_date,
                            "$lt": current_date + timedelta(days=1)
                        },
                        "status": {"$in": ["pending", "confirmed"]}
                    }))
                    
                    availability_map[date_str][stylist_id] = {
                        "stylist_name": stylist.get("name"),
                        "booked_slots": len(bookings),
                        "available": len(bookings) < 8  # Assuming 8 slots per day
                    }
                except:
                    pass
            
            current_date += timedelta(days=1)
        
        return {
            "date_range": {
                "from": date_from,
                "to": date_to
            },
            "service_id": service_id,
            "availability": availability_map
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
