"""
Guest Bookings API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

router = APIRouter(prefix="/api/guest-bookings", tags=["guest-bookings"])


@router.get("/")
async def get_guest_bookings():
    """Get all guest bookings"""
    return {"message": "Guest bookings endpoint"}


@router.post("/")
async def create_guest_booking():
    """Create a new guest booking"""
    return {"message": "Create guest booking endpoint"}


@router.get("/{booking_id}")
async def get_guest_booking(booking_id: str):
    """Get a specific guest booking"""
    return {"message": f"Guest booking {booking_id}"}