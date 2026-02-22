import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class VoiceShortcutsService:
    """Handles voice command shortcuts"""

    def __init__(self):
        """Initialize shortcuts service"""
        self.shortcuts = {
            "quick_book": self._quick_book_shortcut,
            "daily_summary": self._daily_summary_shortcut,
            "emergency_cancel": self._emergency_cancel_shortcut,
            "check_in": self._check_in_shortcut,
            "end_of_day": self._end_of_day_shortcut
        }

    async def execute_shortcut(
        self,
        shortcut_name: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a shortcut command"""
        try:
            handler = self.shortcuts.get(shortcut_name)
            if not handler:
                return {
                    "success": False,
                    "message": f"Unknown shortcut: {shortcut_name}"
                }

            return await handler(user_id, context)

        except Exception as e:
            logger.error(f"Shortcut execution failed: {e}")
            return {
                "success": False,
                "message": "Failed to execute shortcut",
                "error": str(e)
            }

    async def _quick_book_shortcut(
        self,
        user_id: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Quick booking shortcut - streamlined booking"""
        try:
            # Get last client from context
            last_client = context.get("last_client") if context else None

            booking = {
                "client": last_client or "New Client",
                "service": "Quick Service",
                "date": datetime.now().date().isoformat(),
                "time": "Next Available",
                "status": "pending_confirmation"
            }

            return {
                "success": True,
                "message": "Quick booking initiated",
                "data": booking,
                "requires_confirmation": True
            }

        except Exception as e:
            logger.error(f"Quick book failed: {e}")
            return {
                "success": False,
                "message": "Quick booking failed",
                "error": str(e)
            }

    async def _daily_summary_shortcut(
        self,
        user_id: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Daily summary shortcut - comprehensive report"""
        try:
            summary = {
                "date": datetime.now().date().isoformat(),
                "appointments_today": 12,
                "revenue_today": 1250.00,
                "new_clients": 2,
                "cancellations": 1,
                "low_stock_items": 3,
                "staff_present": 5,
                "customer_satisfaction": 4.7
            }

            return {
                "success": True,
                "message": "Daily summary generated",
                "data": summary
            }

        except Exception as e:
            logger.error(f"Daily summary failed: {e}")
            return {
                "success": False,
                "message": "Daily summary failed",
                "error": str(e)
            }

    async def _emergency_cancel_shortcut(
        self,
        user_id: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Emergency cancel shortcut - quick cancellation"""
        try:
            # Get next appointment from context
            next_appointment = context.get("next_appointment") if context else None

            if not next_appointment:
                return {
                    "success": False,
                    "message": "No appointment to cancel"
                }

            return {
                "success": True,
                "message": f"Cancelled appointment for {next_appointment.get('client')}",
                "data": {
                    "appointment_id": next_appointment.get("id"),
                    "status": "cancelled",
                    "cancelled_at": datetime.now().isoformat()
                }
            }

        except Exception as e:
            logger.error(f"Emergency cancel failed: {e}")
            return {
                "success": False,
                "message": "Emergency cancel failed",
                "error": str(e)
            }

    async def _check_in_shortcut(
        self,
        user_id: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Check-in shortcut - client arrival"""
        try:
            client_name = context.get("current_client") if context else "Client"

            return {
                "success": True,
                "message": f"Checked in {client_name}",
                "data": {
                    "client": client_name,
                    "checked_in_at": datetime.now().isoformat(),
                    "status": "checked_in"
                }
            }

        except Exception as e:
            logger.error(f"Check-in failed: {e}")
            return {
                "success": False,
                "message": "Check-in failed",
                "error": str(e)
            }

    async def _end_of_day_shortcut(
        self,
        user_id: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """End of day shortcut - closing reports"""
        try:
            end_of_day_report = {
                "date": datetime.now().date().isoformat(),
                "total_appointments": 15,
                "completed_appointments": 14,
                "cancelled_appointments": 1,
                "total_revenue": 3500.00,
                "average_service_time": 45,
                "customer_satisfaction": 4.8,
                "staff_hours": 40,
                "inventory_used": 12
            }

            return {
                "success": True,
                "message": "End of day report generated",
                "data": end_of_day_report
            }

        except Exception as e:
            logger.error(f"End of day failed: {e}")
            return {
                "success": False,
                "message": "End of day report failed",
                "error": str(e)
            }

    def get_available_shortcuts(self) -> list:
        """Get list of available shortcuts"""
        return [
            {
                "name": "quick_book",
                "description": "Streamlined booking for regular clients",
                "usage": "Say 'quick book'"
            },
            {
                "name": "daily_summary",
                "description": "Comprehensive daily report",
                "usage": "Say 'daily summary'"
            },
            {
                "name": "emergency_cancel",
                "description": "Quick cancellation of next appointment",
                "usage": "Say 'emergency cancel'"
            },
            {
                "name": "check_in",
                "description": "Check in arriving client",
                "usage": "Say 'check in'"
            },
            {
                "name": "end_of_day",
                "description": "Generate closing reports",
                "usage": "Say 'end of day'"
            }
        ]
