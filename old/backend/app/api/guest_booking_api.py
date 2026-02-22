"""
Guest Booking API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

router = APIRouter(prefix="/api/guest-booking-api", tags=["guest-booking-api"])


@router.get("/")
async def get_guest_bookings():
    """Get all guest bookings"""
    return {"message": "Guest booking API endpoint"}


@router.post("/")
async def create_guest_booking():
    """Create a new guest booking"""
    return {"message": "Create guest booking API endpoint"}


@router.get("/{booking_id}")
async def get_guest_booking(booking_id: str):
    """Get a specific guest booking"""
    return {"message": f"Guest booking API {booking_id}"}