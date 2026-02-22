import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from app.schemas.voice import Intent, ActionResult, ConversationContext
from app.services.ai_voice_commands import AIVoiceCommands

logger = logging.getLogger(__name__)


class ActionExecutor:
    """Executes actions based on voice commands"""

    def __init__(self, ai_commands: Optional[AIVoiceCommands] = None):
        """Initialize action executor"""
        self.ai_commands = ai_commands
        self.action_handlers = {
            Intent.BOOK_APPOINTMENT: self._handle_book_appointment,
            Intent.CANCEL_APPOINTMENT: self._handle_cancel_appointment,
            Intent.RESCHEDULE_APPOINTMENT: self._handle_reschedule_appointment,
            Intent.SHOW_APPOINTMENTS: self._handle_show_appointments,
            Intent.ADD_CLIENT: self._handle_add_client,
            Intent.SHOW_CLIENT_INFO: self._handle_show_client_info,
            Intent.SHOW_REVENUE: self._handle_show_revenue,
            Intent.SHOW_ANALYTICS: self._handle_show_analytics,
            Intent.CHECK_INVENTORY: self._handle_check_inventory,
            Intent.UPDATE_INVENTORY: self._handle_update_inventory,
            Intent.SHOW_STAFF_SCHEDULE: self._handle_show_staff_schedule,
            Intent.MARK_ATTENDANCE: self._handle_mark_attendance,
            Intent.HELP: self._handle_help,
        }

    async def execute(
        self,
        intent: Intent,
        entities: Dict[str, Any],
        user_id: str,
        context: Optional[ConversationContext] = None,
        command_text: Optional[str] = None
    ) -> ActionResult:
        """
        Execute action based on intent
        
        Args:
            intent: Detected intent
            entities: Extracted entities
            user_id: User ID
            context: Conversation context
            command_text: Original command text for AI commands
            
        Returns:
            Action result
        """
        try:
            # Check if this is an AI command
            if self.ai_commands and command_text:
                ai_result = await self._try_ai_command(command_text, user_id, context)
                if ai_result:
                    return ai_result
            
            handler = self.action_handlers.get(intent)
            
            if handler:
                return await handler(entities, user_id, context)
            else:
                return ActionResult(
                    success=False,
                    message="Unknown command",
                    error="No handler for this intent"
                )

        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            return ActionResult(
                success=False,
                message="Failed to execute action",
                error=str(e)
            )

    async def _try_ai_command(
        self,
        command_text: str,
        user_id: str,
        context: Optional[ConversationContext]
    ) -> Optional[ActionResult]:
        """Try to execute as AI command"""
        try:
            command_lower = command_text.lower()
            
            if any(keyword in command_lower for keyword in ["suggest", "insight", "predict", "churn", "reorder"]):
                return await self.ai_commands.execute_ai_command(
                    command=command_text,
                    user_id=user_id,
                    context=context
                )
        except Exception as e:
            logger.debug(f"Not an AI command: {e}")
        
        return None

    async def _handle_book_appointment(
        self,
        entities: Dict[str, Any],
        user_id: str,
        context: Optional[ConversationContext]
    ) -> ActionResult:
        """Handle booking appointment"""
        try:
            # Extract entities
            client_name = entities.get("PERSON", ["Unknown"])[0]
            service = entities.get("SERVICE", ["General Service"])[0]
            
            # Placeholder for actual booking logic
            booking_data = {
                "client": client_name,
                "service": service,
                "date": datetime.now().date().isoformat(),
                "time": "10:00 AM",
                "status": "confirmed"
            }
            
            return ActionResult(
                success=True,
                data=booking_data,
                message=f"Booked {service} for {client_name}"
            )

        except Exception as e:
            logger.error(f"Booking failed: {e}")
            return ActionResult(
                success=False,
                message="Failed to book appointment",
                error=str(e)
            )

    async def _handle_cancel_appointment(
        self,
        entities: Dict[str, Any],
        user_id: str,
        context: Optional[ConversationContext]
    ) -> ActionResult:
        """Handle cancelling appointment"""
        try:
            client_name = entities.get("PERSON", ["Unknown"])[0]
            
            return ActionResult(
                success=True,
                data={"client": client_name, "status": "cancelled"},
                message=f"Cancelled appointment for {client_name}"
            )

        except Exception as e:
            return ActionResult(
                success=False,
                message="Failed to cancel appointment",
                error=str(e)
            )

    async def _handle_reschedule_appointment(
        self,
        entities: Dict[str, Any],
        user_id: str,
        context: Optional[ConversationContext]
    ) -> ActionResult:
        """Handle rescheduling appointment"""
        try:
            client_name = entities.get("PERSON", ["Unknown"])[0]
            
            return ActionResult(
                success=True,
                data={"client": client_name, "status": "rescheduled"},
                message=f"Rescheduled appointment for {client_name}"
            )

        except Exception as e:
            return ActionResult(
                success=False,
                message="Failed to reschedule appointment",
                error=str(e)
            )

    async def _handle_show_appointments(
        self,
        entities: Dict[str, Any],
        user_id: str,
        context: Optional[ConversationContext]
    ) -> ActionResult:
        """Handle showing appointments"""
        try:
            appointments = [
                {
                    "client": "John Doe",
                    "service": "Haircut",
                    "time": "10:00 AM",
                    "stylist": "Sarah"
                },
                {
                    "client": "Jane Smith",
                    "service": "Hair Coloring",
                    "time": "11:30 AM",
                    "stylist": "Maria"
                }
            ]
            
            return ActionResult(
                success=True,
                data={"appointments": appointments},
                message=f"You have {len(appointments)} appointments today"
            )

        except Exception as e:
            return ActionResult(
                success=False,
                message="Failed to retrieve appointments",
                error=str(e)
            )

    async def _handle_add_client(
        self,
        entities: Dict[str, Any],
        user_id: str,
        context: Optional[ConversationContext]
    ) -> ActionResult:
        """Handle adding new client"""
        try:
            client_name = entities.get("PERSON", ["Unknown"])[0]
            
            return ActionResult(
                success=True,
                data={"client": client_name, "status": "created"},
                message=f"Added new client: {client_name}"
            )

        except Exception as e:
            return ActionResult(
                success=False,
                message="Failed to add client",
                error=str(e)
            )

    async def _handle_show_client_info(
        self,
        entities: Dict[str, Any],
        user_id: str,
        context: Optional[ConversationContext]
    ) -> ActionResult:
        """Handle showing client information"""
        try:
            client_name = entities.get("PERSON", ["Unknown"])[0]
            
            client_info = {
                "name": client_name,
                "phone": "555-0123",
                "email": "client@example.com",
                "total_visits": 12,
                "last_visit": "2024-01-15",
                "preferred_service": "Haircut"
            }
            
            return ActionResult(
                success=True,
                data=client_info,
                message=f"Client information for {client_name}"
            )

        except Exception as e:
            return ActionResult(
                success=False,
                message="Failed to retrieve client information",
                error=str(e)
            )

    async def _handle_show_revenue(
        self,
        entities: Dict[str, Any],
        user_id: str,
        context: Optional[ConversationContext]
    ) -> ActionResult:
        """Handle showing revenue"""
        try:
            revenue_data = {
                "today": 1250.00,
                "this_week": 8500.00,
                "this_month": 35000.00,
                "currency": "USD"
            }
            
            return ActionResult(
                success=True,
                data=revenue_data,
                message=f"Today's revenue: ${revenue_data['today']}"
            )

        except Exception as e:
            return ActionResult(
                success=False,
                message="Failed to retrieve revenue",
                error=str(e)
            )

    async def _handle_show_analytics(
        self,
        entities: Dict[str, Any],
        user_id: str,
        context: Optional[ConversationContext]
    ) -> ActionResult:
        """Handle showing analytics"""
        try:
            analytics = {
                "total_clients": 245,
                "new_clients_this_month": 18,
                "repeat_clients": 180,
                "average_service_time": 45,
                "customer_satisfaction": 4.7
            }
            
            return ActionResult(
                success=True,
                data=analytics,
                message="Here are your salon analytics"
            )

        except Exception as e:
            return ActionResult(
                success=False,
                message="Failed to retrieve analytics",
                error=str(e)
            )

    async def _handle_check_inventory(
        self,
        entities: Dict[str, Any],
        user_id: str,
        context: Optional[ConversationContext]
    ) -> ActionResult:
        """Handle checking inventory"""
        try:
            inventory = {
                "low_stock_items": [
                    {"name": "Hair Dye - Black", "quantity": 3},
                    {"name": "Shampoo - Premium", "quantity": 5}
                ],
                "total_items": 45,
                "items_below_threshold": 2
            }
            
            return ActionResult(
                success=True,
                data=inventory,
                message=f"You have {inventory['items_below_threshold']} items low on stock"
            )

        except Exception as e:
            return ActionResult(
                success=False,
                message="Failed to check inventory",
                error=str(e)
            )

    async def _handle_update_inventory(
        self,
        entities: Dict[str, Any],
        user_id: str,
        context: Optional[ConversationContext]
    ) -> ActionResult:
        """Handle updating inventory"""
        try:
            product = entities.get("PRODUCT", ["Unknown"])[0]
            
            return ActionResult(
                success=True,
                data={"product": product, "status": "updated"},
                message=f"Updated inventory for {product}"
            )

        except Exception as e:
            return ActionResult(
                success=False,
                message="Failed to update inventory",
                error=str(e)
            )

    async def _handle_show_staff_schedule(
        self,
        entities: Dict[str, Any],
        user_id: str,
        context: Optional[ConversationContext]
    ) -> ActionResult:
        """Handle showing staff schedule"""
        try:
            schedule = {
                "staff": [
                    {"name": "Sarah", "shift": "9 AM - 5 PM", "status": "working"},
                    {"name": "Maria", "shift": "10 AM - 6 PM", "status": "working"},
                    {"name": "John", "shift": "Off", "status": "off"}
                ]
            }
            
            return ActionResult(
                success=True,
                data=schedule,
                message="Here's today's staff schedule"
            )

        except Exception as e:
            return ActionResult(
                success=False,
                message="Failed to retrieve staff schedule",
                error=str(e)
            )

    async def _handle_mark_attendance(
        self,
        entities: Dict[str, Any],
        user_id: str,
        context: Optional[ConversationContext]
    ) -> ActionResult:
        """Handle marking attendance"""
        try:
            staff_name = entities.get("PERSON", ["Unknown"])[0]
            
            return ActionResult(
                success=True,
                data={"staff": staff_name, "status": "present"},
                message=f"Marked {staff_name} as present"
            )

        except Exception as e:
            return ActionResult(
                success=False,
                message="Failed to mark attendance",
                error=str(e)
            )

    async def _handle_help(
        self,
        entities: Dict[str, Any],
        user_id: str,
        context: Optional[ConversationContext]
    ) -> ActionResult:
        """Handle help command"""
        commands = [
            "Book appointment",
            "Cancel appointment",
            "Show appointments",
            "Check inventory",
            "Show revenue",
            "Show staff schedule",
            "Add new client",
            "Show client information"
        ]
        
        return ActionResult(
            success=True,
            data={"commands": commands},
            message="Available commands: " + ", ".join(commands)
        )
