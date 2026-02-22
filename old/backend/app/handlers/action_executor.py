"""
Action Executor
Executes actions based on recognized intents
"""

import logging
from typing import Dict, Any, Optional, TYPE_CHECKING
from datetime import datetime, timedelta
from app.models.voice_models import Intent, ActionResult
from app.handlers.intent_patterns import INTENT_REQUIRED_ENTITIES

if TYPE_CHECKING:
    from app.services.booking_service import BookingService
    from app.services.client_service import ClientService
    from app.services.inventory_service import InventoryService
    from app.services.stylist_service import StylistService
    from app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)


class ActionExecutor:
    """Executes actions based on voice command intents"""
    
    def __init__(
        self,
        booking_service: Any,
        client_service: Any,
        inventory_service: Any,
        stylist_service: Any,
        analytics_service: Any
    ):
        self.booking_service = booking_service
        self.client_service = client_service
        self.inventory_service = inventory_service
        self.stylist_service = stylist_service
        self.analytics_service = analytics_service
        
        logger.info("ActionExecutor initialized")
    
    async def execute(
        self,
        intent: Intent,
        entities: Dict[str, Any],
        user_id: str,
        tenant_id: str
    ) -> ActionResult:
        """
        Execute action based on intent
        
        Args:
            intent: Recognized intent
            entities: Extracted entities
            user_id: User identifier
            tenant_id: Tenant identifier
            
        Returns:
            ActionResult with execution status
        """
        try:
            # Validate required entities
            validation = self.validate_parameters(intent, entities)
            if not validation['valid']:
                return ActionResult(
                    success=False,
                    message=validation['message'],
                    error="Missing required parameters"
                )
            
            # Route to appropriate handler
            handler_map = {
                # Booking commands
                Intent.BOOK_APPOINTMENT: self._book_appointment,
                Intent.CANCEL_APPOINTMENT: self._cancel_appointment,
                Intent.RESCHEDULE_APPOINTMENT: self._reschedule_appointment,
                Intent.SHOW_APPOINTMENTS: self._show_appointments,
                
                # Client commands
                Intent.ADD_CLIENT: self._add_client,
                Intent.SHOW_CLIENT_INFO: self._show_client_info,
                Intent.FIND_INACTIVE_CLIENTS: self._find_inactive_clients,

                
                # Financial commands
                Intent.SHOW_REVENUE: self._show_revenue,
                Intent.SHOW_ANALYTICS: self._show_analytics,
                
                # Inventory commands
                Intent.CHECK_INVENTORY: self._check_inventory,
                Intent.UPDATE_INVENTORY: self._update_inventory,
                
                # Staff commands
                Intent.SHOW_STAFF_SCHEDULE: self._show_staff_schedule,
                Intent.CHECK_AVAILABILITY: self._check_availability,
                Intent.MARK_ATTENDANCE: self._mark_attendance,
                Intent.SHOW_PERFORMANCE: self._show_performance,
                
                # Shortcuts
                Intent.QUICK_BOOK: self._quick_book,
                Intent.DAILY_SUMMARY: self._daily_summary,
                Intent.EMERGENCY_CANCEL: self._emergency_cancel,
                Intent.CHECK_IN: self._check_in,
                Intent.END_OF_DAY: self._end_of_day,
                
                Intent.HELP: self._show_help,
            }
            
            handler = handler_map.get(intent)
            if not handler:
                return ActionResult(
                    success=False,
                    message=f"No handler for intent: {intent}",
                    error="Unknown intent"
                )
            
            # Execute handler
            result = await handler(entities, user_id, tenant_id)
            
            logger.info(f"Executed {intent} for user {user_id}: {result.success}")
            return result
            
        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            return ActionResult(
                success=False,
                message="Failed to execute action",
                error=str(e)
            )
    
    def validate_parameters(self, intent: Intent, entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that required entities are present
        
        Args:
            intent: Intent to validate
            entities: Extracted entities
            
        Returns:
            Validation result with valid flag and message
        """
        required = INTENT_REQUIRED_ENTITIES.get(intent, [])
        missing = [e for e in required if e not in entities or not entities[e]]
        
        if missing:
            return {
                'valid': False,
                'message': f"Missing required information: {', '.join(missing)}"
            }
        
        return {'valid': True, 'message': 'Valid'}

    
    # ==================== BOOKING COMMANDS ====================
    
    async def _book_appointment(
        self,
        entities: Dict[str, Any],
        user_id: str,
        tenant_id: str
    ) -> ActionResult:
        """Create a new booking"""
        try:
            client_name = entities.get('client')
            service = entities.get('service')
            stylist = entities.get('stylist')
            date = entities.get('date')
            time = entities.get('time')
            
            # Find or create client
            client = await self.client_service.find_by_name(client_name, tenant_id)
            if not client:
                return ActionResult(
                    success=False,
                    message=f"Client '{client_name}' not found. Would you like to add them first?",
                    error="Client not found"
                )
            
            # Create booking
            booking_data = {
                'client_id': str(client['_id']),
                'service': service,
                'tenant_id': tenant_id,
                'status': 'pending'
            }
            
            if stylist:
                stylist_obj = await self.stylist_service.find_by_name(stylist, tenant_id)
                if stylist_obj:
                    booking_data['stylist_id'] = str(stylist_obj['_id'])
            
            if date:
                booking_data['date'] = date
            
            if time:
                booking_data['time'] = time
            
            booking = await self.booking_service.create_booking(booking_data, user_id)
            
            return ActionResult(
                success=True,
                data={'booking_id': str(booking['_id'])},
                message=f"Booked {client_name} for {service}"
            )
            
        except Exception as e:
            logger.error(f"Failed to book appointment: {e}")
            return ActionResult(
                success=False,
                message="Failed to create booking",
                error=str(e)
            )

    
    async def _cancel_appointment(
        self,
        entities: Dict[str, Any],
        user_id: str,
        tenant_id: str
    ) -> ActionResult:
        """Cancel an existing booking"""
        try:
            client_name = entities.get('client')
            
            # Find client's upcoming bookings
            client = await self.client_service.find_by_name(client_name, tenant_id)
            if not client:
                return ActionResult(
                    success=False,
                    message=f"Client '{client_name}' not found",
                    error="Client not found"
                )
            
            # Get upcoming bookings
            bookings = await self.booking_service.get_client_bookings(
                str(client['_id']),
                tenant_id,
                status='pending'
            )
            
            if not bookings:
                return ActionResult(
                    success=False,
                    message=f"No upcoming appointments found for {client_name}",
                    error="No bookings found"
                )
            
            # Cancel the first upcoming booking
            booking = bookings[0]
            await self.booking_service.cancel_booking(str(booking['_id']), user_id)
            
            return ActionResult(
                success=True,
                data={'booking_id': str(booking['_id'])},
                message=f"Cancelled appointment for {client_name}"
            )
            
        except Exception as e:
            logger.error(f"Failed to cancel appointment: {e}")
            return ActionResult(
                success=False,
                message="Failed to cancel appointment",
                error=str(e)
            )
    
    async def _reschedule_appointment(
        self,
        entities: Dict[str, Any],
        user_id: str,
        tenant_id: str
    ) -> ActionResult:
        """Reschedule an existing booking"""
        try:
            client_name = entities.get('client')
            new_date = entities.get('date')
            new_time = entities.get('time')
            
            # Find client's booking
            client = await self.client_service.find_by_name(client_name, tenant_id)
            if not client:
                return ActionResult(
                    success=False,
                    message=f"Client '{client_name}' not found",
                    error="Client not found"
                )
            
            bookings = await self.booking_service.get_client_bookings(
                str(client['_id']),
                tenant_id,
                status='pending'
            )
            
            if not bookings:
                return ActionResult(
                    success=False,
                    message=f"No upcoming appointments found for {client_name}",
                    error="No bookings found"
                )
            
            # Reschedule first booking
            booking = bookings[0]
            update_data = {}
            if new_date:
                update_data['date'] = new_date
            if new_time:
                update_data['time'] = new_time
            
            await self.booking_service.update_booking(
                str(booking['_id']),
                update_data,
                user_id
            )
            
            return ActionResult(
                success=True,
                data={'booking_id': str(booking['_id'])},
                message=f"Rescheduled {client_name}'s appointment"
            )
            
        except Exception as e:
            logger.error(f"Failed to reschedule appointment: {e}")
            return ActionResult(
                success=False,
                message="Failed to reschedule appointment",
                error=str(e)
            )

    
    async def _show_appointments(
        self,
        entities: Dict[str, Any],
        user_id: str,
        tenant_id: str
    ) -> ActionResult:
        """Show appointments for today or specified period"""
        try:
            time_period = entities.get('time_period', 'today')
            
            # Get bookings for today
            today = datetime.now().date()
            bookings = await self.booking_service.get_bookings_by_date(
                tenant_id,
                today
            )
            
            if not bookings:
                return ActionResult(
                    success=True,
                    data={'bookings': [], 'count': 0},
                    message="No appointments scheduled for today"
                )
            
            # Format booking info
            booking_list = []
            for booking in bookings:
                booking_list.append({
                    'client': booking.get('client_name', 'Unknown'),
                    'service': booking.get('service', 'Unknown'),
                    'time': booking.get('time', 'Not set'),
                    'stylist': booking.get('stylist_name', 'Not assigned')
                })
            
            return ActionResult(
                success=True,
                data={'bookings': booking_list, 'count': len(bookings)},
                message=f"You have {len(bookings)} appointments today"
            )
            
        except Exception as e:
            logger.error(f"Failed to show appointments: {e}")
            return ActionResult(
                success=False,
                message="Failed to retrieve appointments",
                error=str(e)
            )

    
    # ==================== CLIENT COMMANDS ====================
    
    async def _add_client(
        self,
        entities: Dict[str, Any],
        user_id: str,
        tenant_id: str
    ) -> ActionResult:
        """Add a new client"""
        try:
            name = entities.get('name')
            phone = entities.get('phone', '')
            email = entities.get('email', '')
            
            client_data = {
                'name': name,
                'phone': phone,
                'email': email,
                'tenant_id': tenant_id
            }
            
            client = await self.client_service.create_client(client_data, user_id)
            
            return ActionResult(
                success=True,
                data={'client_id': str(client['_id'])},
                message=f"Added new client: {name}"
            )
            
        except Exception as e:
            logger.error(f"Failed to add client: {e}")
            return ActionResult(
                success=False,
                message="Failed to add client",
                error=str(e)
            )
    
    async def _show_client_info(
        self,
        entities: Dict[str, Any],
        user_id: str,
        tenant_id: str
    ) -> ActionResult:
        """Show client information and history"""
        try:
            client_name = entities.get('client')
            
            client = await self.client_service.find_by_name(client_name, tenant_id)
            if not client:
                return ActionResult(
                    success=False,
                    message=f"Client '{client_name}' not found",
                    error="Client not found"
                )
            
            # Get client's booking history
            bookings = await self.booking_service.get_client_bookings(
                str(client['_id']),
                tenant_id
            )
            
            client_info = {
                'name': client.get('name'),
                'phone': client.get('phone'),
                'email': client.get('email'),
                'total_visits': len(bookings),
                'last_visit': bookings[0].get('date') if bookings else None
            }
            
            return ActionResult(
                success=True,
                data=client_info,
                message=f"{client_name} has {len(bookings)} total visits"
            )
            
        except Exception as e:
            logger.error(f"Failed to show client info: {e}")
            return ActionResult(
                success=False,
                message="Failed to retrieve client information",
                error=str(e)
            )
    
    async def _find_inactive_clients(
        self,
        entities: Dict[str, Any],
        user_id: str,
        tenant_id: str
    ) -> ActionResult:
        """Find clients who haven't visited recently"""
        try:
            period = entities.get('period', '30 days')
            
            # Parse period (simplified)
            days = 30
            if 'week' in period.lower():
                days = 7
            elif 'month' in period.lower():
                days = 30
            elif 'year' in period.lower():
                days = 365
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Get inactive clients
            inactive_clients = await self.client_service.get_inactive_clients(
                tenant_id,
                cutoff_date
            )
            
            return ActionResult(
                success=True,
                data={'clients': inactive_clients, 'count': len(inactive_clients)},
                message=f"Found {len(inactive_clients)} inactive clients"
            )
            
        except Exception as e:
            logger.error(f"Failed to find inactive clients: {e}")
            return ActionResult(
                success=False,
                message="Failed to find inactive clients",
                error=str(e)
            )

    
    # ==================== FINANCIAL COMMANDS ====================
    
    async def _show_revenue(
        self,
        entities: Dict[str, Any],
        user_id: str,
        tenant_id: str
    ) -> ActionResult:
        """Show revenue for specified period"""
        try:
            time_period = entities.get('time_period', 'today')
            
            if 'today' in time_period.lower():
                start_date = datetime.now().date()
                end_date = start_date
            elif 'week' in time_period.lower():
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=7)
            elif 'month' in time_period.lower():
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=30)
            else:
                start_date = datetime.now().date()
                end_date = start_date
            
            revenue = await self.analytics_service.get_revenue(
                tenant_id,
                start_date,
                end_date
            )
            
            return ActionResult(
                success=True,
                data={'revenue': revenue, 'period': time_period},
                message=f"Revenue for {time_period}: ${revenue:.2f}"
            )
            
        except Exception as e:
            logger.error(f"Failed to show revenue: {e}")
            return ActionResult(
                success=False,
                message="Failed to retrieve revenue",
                error=str(e)
            )
    
    async def _show_analytics(
        self,
        entities: Dict[str, Any],
        user_id: str,
        tenant_id: str
    ) -> ActionResult:
        """Show business analytics"""
        try:
            analytics = await self.analytics_service.get_dashboard_analytics(tenant_id)
            
            summary = {
                'total_revenue': analytics.get('total_revenue', 0),
                'total_bookings': analytics.get('total_bookings', 0),
                'total_clients': analytics.get('total_clients', 0),
                'top_service': analytics.get('top_service', 'N/A')
            }
            
            return ActionResult(
                success=True,
                data=summary,
                message="Here are your business analytics"
            )
            
        except Exception as e:
            logger.error(f"Failed to show analytics: {e}")
            return ActionResult(
                success=False,
                message="Failed to retrieve analytics",
                error=str(e)
            )

    
    # ==================== INVENTORY COMMANDS ====================
    
    async def _check_inventory(
        self,
        entities: Dict[str, Any],
        user_id: str,
        tenant_id: str
    ) -> ActionResult:
        """Check inventory levels"""
        try:
            product = entities.get('product')
            
            if product:
                # Check specific product
                item = await self.inventory_service.find_by_name(product, tenant_id)
                if not item:
                    return ActionResult(
                        success=False,
                        message=f"Product '{product}' not found",
                        error="Product not found"
                    )
                
                return ActionResult(
                    success=True,
                    data={'product': product, 'quantity': item.get('quantity', 0)},
                    message=f"{product}: {item.get('quantity', 0)} units in stock"
                )
            else:
                # Show low stock items
                low_stock = await self.inventory_service.get_low_stock_items(tenant_id)
                
                return ActionResult(
                    success=True,
                    data={'low_stock_items': low_stock, 'count': len(low_stock)},
                    message=f"{len(low_stock)} products are running low"
                )
            
        except Exception as e:
            logger.error(f"Failed to check inventory: {e}")
            return ActionResult(
                success=False,
                message="Failed to check inventory",
                error=str(e)
            )
    
    async def _update_inventory(
        self,
        entities: Dict[str, Any],
        user_id: str,
        tenant_id: str
    ) -> ActionResult:
        """Update inventory levels"""
        try:
            product = entities.get('product')
            quantity = entities.get('quantity', 0)
            action = entities.get('action', 'add')  # add or reduce
            
            item = await self.inventory_service.find_by_name(product, tenant_id)
            if not item:
                return ActionResult(
                    success=False,
                    message=f"Product '{product}' not found",
                    error="Product not found"
                )
            
            current_qty = item.get('quantity', 0)
            
            if action == 'reduce' or 'use' in action.lower():
                new_qty = max(0, current_qty - quantity)
            else:
                new_qty = current_qty + quantity
            
            await self.inventory_service.update_quantity(
                str(item['_id']),
                new_qty,
                user_id
            )
            
            return ActionResult(
                success=True,
                data={'product': product, 'new_quantity': new_qty},
                message=f"Updated {product}: {new_qty} units"
            )
            
        except Exception as e:
            logger.error(f"Failed to update inventory: {e}")
            return ActionResult(
                success=False,
                message="Failed to update inventory",
                error=str(e)
            )

    
    # ==================== STAFF COMMANDS ====================
    
    async def _show_staff_schedule(
        self,
        entities: Dict[str, Any],
        user_id: str,
        tenant_id: str
    ) -> ActionResult:
        """Show staff schedule"""
        try:
            stylist_name = entities.get('stylist')
            
            if stylist_name:
                # Show specific stylist's schedule
                stylist = await self.stylist_service.find_by_name(stylist_name, tenant_id)
                if not stylist:
                    return ActionResult(
                        success=False,
                        message=f"Stylist '{stylist_name}' not found",
                        error="Stylist not found"
                    )
                
                # Get today's appointments for this stylist
                today = datetime.now().date()
                appointments = await self.booking_service.get_stylist_bookings(
                    str(stylist['_id']),
                    tenant_id,
                    today
                )
                
                return ActionResult(
                    success=True,
                    data={'stylist': stylist_name, 'appointments': appointments, 'count': len(appointments)},
                    message=f"{stylist_name} has {len(appointments)} appointments today"
                )
            else:
                # Show all staff schedules
                all_stylists = await self.stylist_service.get_all_stylists(tenant_id)
                
                return ActionResult(
                    success=True,
                    data={'stylists': all_stylists, 'count': len(all_stylists)},
                    message=f"Retrieved schedules for {len(all_stylists)} staff members"
                )
            
        except Exception as e:
            logger.error(f"Failed to show staff schedule: {e}")
            return ActionResult(
                success=False,
                message="Failed to retrieve staff schedule",
                error=str(e)
            )
    
    async def _check_availability(
        self,
        entities: Dict[str, Any],
        user_id: str,
        tenant_id: str
    ) -> ActionResult:
        """Check staff availability"""
        try:
            time = entities.get('time')
            date = entities.get('date', datetime.now().date())
            
            available_staff = await self.stylist_service.get_available_staff(
                tenant_id,
                date,
                time
            )
            
            if not available_staff:
                return ActionResult(
                    success=True,
                    data={'available_staff': [], 'count': 0},
                    message=f"No staff available at {time}"
                )
            
            staff_names = [s.get('name') for s in available_staff]
            
            return ActionResult(
                success=True,
                data={'available_staff': staff_names, 'count': len(staff_names)},
                message=f"{len(staff_names)} staff members available: {', '.join(staff_names)}"
            )
            
        except Exception as e:
            logger.error(f"Failed to check availability: {e}")
            return ActionResult(
                success=False,
                message="Failed to check availability",
                error=str(e)
            )
    
    async def _mark_attendance(
        self,
        entities: Dict[str, Any],
        user_id: str,
        tenant_id: str
    ) -> ActionResult:
        """Mark staff attendance"""
        try:
            stylist_name = entities.get('stylist')
            status = entities.get('status', 'present')  # present or absent
            
            stylist = await self.stylist_service.find_by_name(stylist_name, tenant_id)
            if not stylist:
                return ActionResult(
                    success=False,
                    message=f"Stylist '{stylist_name}' not found",
                    error="Stylist not found"
                )
            
            await self.stylist_service.mark_attendance(
                str(stylist['_id']),
                status,
                datetime.now().date(),
                user_id
            )
            
            return ActionResult(
                success=True,
                data={'stylist': stylist_name, 'status': status},
                message=f"Marked {stylist_name} as {status}"
            )
            
        except Exception as e:
            logger.error(f"Failed to mark attendance: {e}")
            return ActionResult(
                success=False,
                message="Failed to mark attendance",
                error=str(e)
            )
    
    async def _show_performance(
        self,
        entities: Dict[str, Any],
        user_id: str,
        tenant_id: str
    ) -> ActionResult:
        """Show staff performance metrics"""
        try:
            stylist_name = entities.get('stylist')
            
            if stylist_name:
                stylist = await self.stylist_service.find_by_name(stylist_name, tenant_id)
                if not stylist:
                    return ActionResult(
                        success=False,
                        message=f"Stylist '{stylist_name}' not found",
                        error="Stylist not found"
                    )
                
                performance = await self.analytics_service.get_stylist_performance(
                    str(stylist['_id']),
                    tenant_id
                )
                
                return ActionResult(
                    success=True,
                    data=performance,
                    message=f"{stylist_name}'s performance metrics retrieved"
                )
            else:
                # Show all staff performance
                all_performance = await self.analytics_service.get_all_staff_performance(tenant_id)
                
                return ActionResult(
                    success=True,
                    data=all_performance,
                    message="Retrieved performance for all staff"
                )
            
        except Exception as e:
            logger.error(f"Failed to show performance: {e}")
            return ActionResult(
                success=False,
                message="Failed to retrieve performance metrics",
                error=str(e)
            )

    
    # ==================== SHORTCUT COMMANDS ====================
    
    async def _quick_book(
        self,
        entities: Dict[str, Any],
        user_id: str,
        tenant_id: str
    ) -> ActionResult:
        """Quick booking flow"""
        return ActionResult(
            success=True,
            message="Starting quick booking flow. Please provide client name and service.",
            data={'flow': 'quick_book'}
        )
    
    async def _daily_summary(
        self,
        entities: Dict[str, Any],
        user_id: str,
        tenant_id: str
    ) -> ActionResult:
        """Generate daily summary"""
        try:
            today = datetime.now().date()
            
            # Get today's bookings
            bookings = await self.booking_service.get_bookings_by_date(tenant_id, today)
            
            # Get today's revenue
            revenue = await self.analytics_service.get_revenue(tenant_id, today, today)
            
            # Get completed vs pending
            completed = len([b for b in bookings if b.get('status') == 'completed'])
            pending = len([b for b in bookings if b.get('status') == 'pending'])
            
            summary = {
                'total_bookings': len(bookings),
                'completed': completed,
                'pending': pending,
                'revenue': revenue
            }
            
            return ActionResult(
                success=True,
                data=summary,
                message=f"Today: {len(bookings)} bookings, ${revenue:.2f} revenue"
            )
            
        except Exception as e:
            logger.error(f"Failed to generate daily summary: {e}")
            return ActionResult(
                success=False,
                message="Failed to generate summary",
                error=str(e)
            )
    
    async def _emergency_cancel(
        self,
        entities: Dict[str, Any],
        user_id: str,
        tenant_id: str
    ) -> ActionResult:
        """Emergency cancel next appointment"""
        try:
            # Get next upcoming booking
            now = datetime.now()
            bookings = await self.booking_service.get_upcoming_bookings(tenant_id, limit=1)
            
            if not bookings:
                return ActionResult(
                    success=False,
                    message="No upcoming appointments to cancel",
                    error="No bookings found"
                )
            
            booking = bookings[0]
            await self.booking_service.cancel_booking(str(booking['_id']), user_id)
            
            return ActionResult(
                success=True,
                data={'booking_id': str(booking['_id'])},
                message=f"Emergency cancelled appointment for {booking.get('client_name')}"
            )
            
        except Exception as e:
            logger.error(f"Failed emergency cancel: {e}")
            return ActionResult(
                success=False,
                message="Failed to cancel appointment",
                error=str(e)
            )
    
    async def _check_in(
        self,
        entities: Dict[str, Any],
        user_id: str,
        tenant_id: str
    ) -> ActionResult:
        """Check in a client"""
        try:
            client_name = entities.get('client')
            
            # Find client's today's booking
            client = await self.client_service.find_by_name(client_name, tenant_id)
            if not client:
                return ActionResult(
                    success=False,
                    message=f"Client '{client_name}' not found",
                    error="Client not found"
                )
            
            today = datetime.now().date()
            bookings = await self.booking_service.get_client_bookings_by_date(
                str(client['_id']),
                tenant_id,
                today
            )
            
            if not bookings:
                return ActionResult(
                    success=False,
                    message=f"No appointment found for {client_name} today",
                    error="No booking found"
                )
            
            booking = bookings[0]
            await self.booking_service.update_booking(
                str(booking['_id']),
                {'status': 'checked_in'},
                user_id
            )
            
            return ActionResult(
                success=True,
                data={'booking_id': str(booking['_id'])},
                message=f"Checked in {client_name}"
            )
            
        except Exception as e:
            logger.error(f"Failed to check in: {e}")
            return ActionResult(
                success=False,
                message="Failed to check in client",
                error=str(e)
            )
    
    async def _end_of_day(
        self,
        entities: Dict[str, Any],
        user_id: str,
        tenant_id: str
    ) -> ActionResult:
        """Generate end of day report"""
        try:
            today = datetime.now().date()
            
            # Get comprehensive daily stats
            bookings = await self.booking_service.get_bookings_by_date(tenant_id, today)
            revenue = await self.analytics_service.get_revenue(tenant_id, today, today)
            
            completed = len([b for b in bookings if b.get('status') == 'completed'])
            cancelled = len([b for b in bookings if b.get('status') == 'cancelled'])
            no_show = len([b for b in bookings if b.get('status') == 'no_show'])
            
            report = {
                'date': str(today),
                'total_bookings': len(bookings),
                'completed': completed,
                'cancelled': cancelled,
                'no_show': no_show,
                'total_revenue': revenue
            }
            
            return ActionResult(
                success=True,
                data=report,
                message=f"End of day: {completed} completed, ${revenue:.2f} revenue"
            )
            
        except Exception as e:
            logger.error(f"Failed to generate end of day report: {e}")
            return ActionResult(
                success=False,
                message="Failed to generate report",
                error=str(e)
            )
    
    async def _show_help(
        self,
        entities: Dict[str, Any],
        user_id: str,
        tenant_id: str
    ) -> ActionResult:
        """Show available commands"""
        help_text = """
        Available commands:
        - Book appointment: "Book [client] for [service]"
        - Cancel appointment: "Cancel [client]'s appointment"
        - Show appointments: "Show today's appointments"
        - Add client: "Add new client [name]"
        - Check inventory: "What products are low"
        - Show revenue: "Show today's revenue"
        - Staff schedule: "Show [stylist]'s schedule"
        - Daily summary: "Daily summary"
        """
        
        return ActionResult(
            success=True,
            data={'help_text': help_text},
            message="Here are the available commands"
        )
