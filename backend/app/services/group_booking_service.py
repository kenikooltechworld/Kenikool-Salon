from typing import List, Optional, Dict
from bson import ObjectId
from datetime import datetime, timedelta
from decimal import Decimal

from app.models.group_booking import GroupBooking, GroupBookingParticipant
from app.models.appointment import Appointment
from app.models.service import Service
from app.schemas.group_booking import GroupBookingCreate, GroupBookingUpdate


class GroupBookingService:
    """Service for managing group bookings"""
    
    @staticmethod
    def calculate_group_discount(participant_count: int, base_total: Decimal) -> tuple[float, Decimal]:
        """
        Calculate group discount based on number of participants
        
        Returns:
            tuple: (discount_percentage, discount_amount)
        """
        # Discount tiers
        if participant_count >= 10:
            discount_pct = 20.0
        elif participant_count >= 5:
            discount_pct = 15.0
        elif participant_count >= 3:
            discount_pct = 10.0
        else:
            discount_pct = 0.0
        
        discount_amount = base_total * Decimal(discount_pct / 100)
        return discount_pct, discount_amount
    
    @staticmethod
    def calculate_pricing(
        tenant_id: ObjectId,
        participants: List[Dict]
    ) -> tuple[Decimal, float, Decimal, Decimal]:
        """
        Calculate total pricing for group booking
        
        Returns:
            tuple: (base_total, discount_percentage, discount_amount, final_total)
        """
        base_total = Decimal("0")
        
        # Calculate base total from all services
        for participant in participants:
            service = Service.objects(
                id=ObjectId(participant["service_id"]),
                tenant_id=tenant_id
            ).first()
            
            if service:
                base_total += Decimal(str(service.price.to_decimal()))
        
        # Calculate group discount
        participant_count = len(participants)
        discount_pct, discount_amount = GroupBookingService.calculate_group_discount(
            participant_count, base_total
        )
        
        final_total = base_total - discount_amount
        
        return base_total, discount_pct, discount_amount, final_total
    
    @staticmethod
    def create_group_booking(
        tenant_id: ObjectId,
        booking_data: GroupBookingCreate,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> GroupBooking:
        """Create a new group booking"""
        
        # Calculate pricing
        base_total, discount_pct, discount_amount, final_total = (
            GroupBookingService.calculate_pricing(
                tenant_id,
                [p.dict() for p in booking_data.participants]
            )
        )
        
        # Create participant records
        participants = []
        for p_data in booking_data.participants:
            participant = GroupBookingParticipant(
                name=p_data.name,
                email=p_data.email,
                phone=p_data.phone,
                service_id=ObjectId(p_data.service_id),
                staff_id=ObjectId(p_data.staff_id) if p_data.staff_id else None,
                notes=p_data.notes,
                status="pending"
            )
            participants.append(participant)
        
        # Create group booking
        group_booking = GroupBooking(
            tenant_id=tenant_id,
            group_name=booking_data.group_name,
            group_type=booking_data.group_type,
            organizer_name=booking_data.organizer_name,
            organizer_email=booking_data.organizer_email,
            organizer_phone=booking_data.organizer_phone,
            booking_date=booking_data.booking_date,
            participants=participants,
            total_participants=len(participants),
            base_total=base_total,
            discount_percentage=discount_pct,
            discount_amount=discount_amount,
            final_total=final_total,
            payment_option=booking_data.payment_option,
            special_requests=booking_data.special_requests,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        group_booking.save()
        return group_booking
    
    @staticmethod
    def get_group_booking(booking_id: ObjectId) -> Optional[GroupBooking]:
        """Get a group booking by ID"""
        return GroupBooking.objects(id=booking_id).first()
    
    @staticmethod
    def get_group_bookings(
        tenant_id: ObjectId,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[GroupBooking]:
        """Get group bookings with filters"""
        query = {"tenant_id": tenant_id}
        
        if status:
            query["status"] = status
        
        if start_date and end_date:
            query["booking_date"] = {"$gte": start_date, "$lte": end_date}
        elif start_date:
            query["booking_date"] = {"$gte": start_date}
        elif end_date:
            query["booking_date"] = {"$lte": end_date}
        
        return GroupBooking.objects(**query).skip(skip).limit(limit).order_by("-booking_date")
    
    @staticmethod
    def update_group_booking(
        booking_id: ObjectId,
        update_data: GroupBookingUpdate
    ) -> Optional[GroupBooking]:
        """Update a group booking"""
        group_booking = GroupBooking.objects(id=booking_id).first()
        
        if not group_booking:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        
        for key, value in update_dict.items():
            setattr(group_booking, key, value)
        
        group_booking.updated_at = datetime.utcnow()
        group_booking.save()
        
        return group_booking
    
    @staticmethod
    def confirm_group_booking(booking_id: ObjectId) -> Optional[GroupBooking]:
        """Confirm a group booking and create individual appointments"""
        group_booking = GroupBooking.objects(id=booking_id).first()
        
        if not group_booking or group_booking.status != "pending":
            return None
        
        # Create individual appointments for each participant
        from app.services.appointment_service import AppointmentService
        
        for participant in group_booking.participants:
            try:
                # Get service to calculate end time
                service = Service.objects(
                    id=participant.service_id,
                    tenant_id=group_booking.tenant_id
                ).first()
                
                if not service:
                    participant.status = "pending"
                    continue
                
                # Calculate end time based on service duration
                start_time = group_booking.booking_date
                end_time = start_time + timedelta(minutes=service.duration_minutes)
                
                appointment = AppointmentService.create_appointment(
                    tenant_id=group_booking.tenant_id,
                    service_id=participant.service_id,
                    staff_id=participant.staff_id,
                    start_time=start_time,
                    end_time=end_time,
                    guest_name=participant.name,
                    guest_email=participant.email,
                    guest_phone=participant.phone,
                    notes=f"Group: {group_booking.group_name}\n{participant.notes or ''}",
                )
                
                # Link appointment to participant
                participant.appointment_id = appointment.id
                participant.status = "confirmed"
                
                # Create booking activity for social proof
                try:
                    from app.services.booking_activity_service import BookingActivityService
                    BookingActivityService.create_activity(
                        tenant_id=group_booking.tenant_id,
                        customer_name=participant.name,
                        service_name=service.name,
                        booking_time=start_time
                    )
                except Exception as e:
                    print(f"Error creating booking activity for {participant.name}: {e}")
                
            except Exception as e:
                # Log error but continue with other participants
                print(f"Error creating appointment for participant {participant.name}: {e}")
                participant.status = "pending"
        
        # Update group booking status
        group_booking.status = "confirmed"
        group_booking.confirmed_at = datetime.utcnow()
        group_booking.save()
        
        return group_booking
    
    @staticmethod
    def cancel_group_booking(
        booking_id: ObjectId,
        cancellation_reason: Optional[str] = None
    ) -> Optional[GroupBooking]:
        """Cancel a group booking and all associated appointments"""
        group_booking = GroupBooking.objects(id=booking_id).first()
        
        if not group_booking:
            return None
        
        # Cancel all individual appointments
        for participant in group_booking.participants:
            if participant.appointment_id:
                appointment = Appointment.objects(id=participant.appointment_id).first()
                if appointment:
                    appointment.status = "cancelled"
                    appointment.save()
                
                participant.status = "cancelled"
        
        # Update group booking
        group_booking.status = "cancelled"
        group_booking.cancelled_at = datetime.utcnow()
        group_booking.cancellation_reason = cancellation_reason
        group_booking.save()
        
        return group_booking
