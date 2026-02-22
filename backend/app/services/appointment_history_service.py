"""Service for appointment history management."""

from datetime import datetime, timedelta
from typing import List, Tuple, Optional
from bson import ObjectId
from mongoengine import Q
from app.models.appointment_history import AppointmentHistory
from app.models.appointment import Appointment
from app.models.service import Service


class AppointmentHistoryService:
    """Service for managing appointment history."""

    @staticmethod
    def create_history_from_appointment(
        tenant_id: ObjectId,
        appointment_id: ObjectId,
    ) -> AppointmentHistory:
        """
        Create appointment history entry from a confirmed or completed appointment.
        
        Args:
            tenant_id: Tenant ID
            appointment_id: Appointment ID
            
        Returns:
            Created AppointmentHistory document
            
        Raises:
            ValueError: If appointment not found or not confirmed/completed
        """
        appointment = Appointment.objects(
            tenant_id=tenant_id,
            id=appointment_id
        ).first()
        
        if not appointment:
            raise ValueError(f"Appointment {appointment_id} not found")
        
        if appointment.status not in ["confirmed", "completed", "cancelled", "no_show"]:
            raise ValueError(f"Appointment {appointment_id} has invalid status for history")
        
        # Calculate duration in minutes
        duration_minutes = int((appointment.end_time - appointment.start_time).total_seconds() / 60)
        
        # Use appointment price as amount paid (or 0 if not set)
        amount_paid = appointment.price or 0
        
        # Create history entry
        history = AppointmentHistory(
            tenant_id=tenant_id,
            customer_id=appointment.customer_id,
            appointment_id=appointment.id,
            service_id=appointment.service_id,
            staff_id=appointment.staff_id,
            appointment_date=appointment.start_time,
            duration_minutes=duration_minutes,
            amount_paid=amount_paid,
            notes=appointment.notes,
        )
        history.save()
        return history

    @staticmethod
    def get_customer_history(
        tenant_id: ObjectId,
        customer_id: ObjectId,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[AppointmentHistory], int]:
        """
        Get customer appointment history with pagination.
        
        Args:
            tenant_id: Tenant ID
            customer_id: Customer ID
            page: Page number (1-indexed)
            page_size: Number of results per page
            
        Returns:
            Tuple of (history entries list, total count)
        """
        query = Q(tenant_id=tenant_id) & Q(customer_id=customer_id)
        
        total = AppointmentHistory.objects(query).count()
        
        skip = (page - 1) * page_size
        history_entries = AppointmentHistory.objects(query).order_by(
            "-appointment_date"
        ).skip(skip).limit(page_size)
        
        return list(history_entries), total

    @staticmethod
    def get_history_entry(
        tenant_id: ObjectId,
        history_id: ObjectId,
        customer_id: Optional[ObjectId] = None,
    ) -> Optional[AppointmentHistory]:
        """
        Get a specific history entry.
        
        Args:
            tenant_id: Tenant ID
            history_id: History entry ID
            customer_id: Optional customer ID for additional filtering
            
        Returns:
            AppointmentHistory document or None if not found
        """
        query = Q(tenant_id=tenant_id) & Q(id=history_id)
        
        if customer_id:
            query &= Q(customer_id=customer_id)
        
        return AppointmentHistory.objects(query).first()

    @staticmethod
    def get_customer_history_stats(
        tenant_id: ObjectId,
        customer_id: ObjectId,
    ) -> dict:
        """
        Get statistics about customer's appointment history.
        
        Args:
            tenant_id: Tenant ID
            customer_id: Customer ID
            
        Returns:
            Dictionary with history statistics
        """
        history_entries = AppointmentHistory.objects(
            tenant_id=tenant_id,
            customer_id=customer_id
        )
        
        total_appointments = history_entries.count()
        
        if total_appointments == 0:
            return {
                "total_appointments": 0,
                "total_amount_paid": 0,
                "total_duration_minutes": 0,
                "average_duration_minutes": 0,
                "first_appointment_date": None,
                "last_appointment_date": None,
            }
        
        # Calculate totals
        total_amount_paid = sum(entry.amount_paid for entry in history_entries)
        total_duration_minutes = sum(entry.duration_minutes for entry in history_entries)
        average_duration_minutes = total_duration_minutes / total_appointments if total_appointments > 0 else 0
        
        # Get first and last appointment dates
        sorted_entries = sorted(history_entries, key=lambda x: x.appointment_date)
        first_appointment_date = sorted_entries[0].appointment_date if sorted_entries else None
        last_appointment_date = sorted_entries[-1].appointment_date if sorted_entries else None
        
        return {
            "total_appointments": total_appointments,
            "total_amount_paid": float(total_amount_paid),
            "total_duration_minutes": total_duration_minutes,
            "average_duration_minutes": float(average_duration_minutes),
            "first_appointment_date": first_appointment_date.isoformat() if first_appointment_date else None,
            "last_appointment_date": last_appointment_date.isoformat() if last_appointment_date else None,
        }

    @staticmethod
    def get_service_history(
        tenant_id: ObjectId,
        customer_id: ObjectId,
        service_id: ObjectId,
    ) -> List[AppointmentHistory]:
        """
        Get customer's history for a specific service.
        
        Args:
            tenant_id: Tenant ID
            customer_id: Customer ID
            service_id: Service ID
            
        Returns:
            List of history entries for the service
        """
        return list(
            AppointmentHistory.objects(
                tenant_id=tenant_id,
                customer_id=customer_id,
                service_id=service_id
            ).order_by("-appointment_date")
        )

    @staticmethod
    def get_staff_history(
        tenant_id: ObjectId,
        customer_id: ObjectId,
        staff_id: ObjectId,
    ) -> List[AppointmentHistory]:
        """
        Get customer's history with a specific staff member.
        
        Args:
            tenant_id: Tenant ID
            customer_id: Customer ID
            staff_id: Staff ID
            
        Returns:
            List of history entries with the staff member
        """
        return list(
            AppointmentHistory.objects(
                tenant_id=tenant_id,
                customer_id=customer_id,
                staff_id=staff_id
            ).order_by("-appointment_date")
        )
