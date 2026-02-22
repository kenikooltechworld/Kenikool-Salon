"""
Socket.IO Event Handlers for Real-time Notifications
"""
import logging
from typing import Dict, Any, Optional
from app.services.socketio_service import socketio_service

logger = logging.getLogger(__name__)


def register_socketio_handlers():
    """Register all Socket.IO event handlers"""

    @socketio_service.sio.event
    async def connect(sid: str, environ: Dict[str, Any], auth: Optional[Dict[str, Any]] = None):
        """Handle client connection"""
        await socketio_service.connect(sid, environ, auth)

    @socketio_service.sio.event
    async def disconnect(sid: str):
        """Handle client disconnection"""
        await socketio_service.disconnect(sid)

    @socketio_service.sio.event
    async def authenticate(sid: str, data: Dict[str, Any]):
        """Handle authentication after connection"""
        try:
            tenant_id = data.get("tenant_id")
            user_id = data.get("user_id")

            if not tenant_id:
                logger.warning(f"Authentication without tenant_id: {sid}")
                await socketio_service.sio.disconnect(sid)
                return

            # Update connection info
            socketio_service.tenant_connections[sid] = tenant_id
            if user_id:
                socketio_service.user_connections[sid] = user_id

            # Add to active connections if not already there
            if tenant_id not in socketio_service.active_connections:
                socketio_service.active_connections[tenant_id] = set()
            socketio_service.active_connections[tenant_id].add(sid)

            logger.info(f"Client authenticated: {sid} for tenant {tenant_id}")

            # Send authentication confirmation
            await socketio_service.sio.emit(
                "authenticated",
                {"message": "Successfully authenticated"},
                to=sid,
            )
        except Exception as e:
            logger.error(f"Error in authenticate handler: {e}")

    @socketio_service.sio.event
    async def ping(sid: str):
        """Handle ping from client"""
        try:
            await socketio_service.sio.emit("pong", {}, to=sid)
        except Exception as e:
            logger.error(f"Error in ping handler: {e}")

    @socketio_service.sio.event
    async def subscribe_to_events(sid: str, data: Dict[str, Any]):
        """Handle event subscription"""
        try:
            event_types = data.get("event_types", [])
            logger.info(f"Client {sid} subscribed to events: {event_types}")

            await socketio_service.sio.emit(
                "subscribed",
                {"event_types": event_types},
                to=sid,
            )
        except Exception as e:
            logger.error(f"Error in subscribe_to_events handler: {e}")

    logger.info("Socket.IO event handlers registered")


# Broadcast functions for use in other services

async def broadcast_booking_created(tenant_id: str, booking_data: Dict[str, Any]):
    """Broadcast booking created event"""
    await socketio_service.broadcast_to_tenant(
        tenant_id,
        "booking_created",
        {
            "type": "booking_created",
            "data": booking_data,
        },
    )


async def broadcast_booking_updated(tenant_id: str, booking_data: Dict[str, Any]):
    """Broadcast booking updated event"""
    await socketio_service.broadcast_to_tenant(
        tenant_id,
        "booking_updated",
        {
            "type": "booking_updated",
            "data": booking_data,
        },
    )


async def broadcast_booking_cancelled(tenant_id: str, booking_data: Dict[str, Any]):
    """Broadcast booking cancelled event"""
    await socketio_service.broadcast_to_tenant(
        tenant_id,
        "booking_cancelled",
        {
            "type": "booking_cancelled",
            "data": booking_data,
        },
    )


async def broadcast_booking_confirmed(tenant_id: str, booking_data: Dict[str, Any]):
    """Broadcast booking confirmed event"""
    await socketio_service.broadcast_to_tenant(
        tenant_id,
        "booking_confirmed",
        {
            "type": "booking_confirmed",
            "data": booking_data,
        },
    )


async def broadcast_client_created(tenant_id: str, client_data: Dict[str, Any]):
    """Broadcast client created event"""
    await socketio_service.broadcast_to_tenant(
        tenant_id,
        "client_created",
        {
            "type": "client_created",
            "data": client_data,
        },
    )


async def broadcast_client_updated(tenant_id: str, client_data: Dict[str, Any]):
    """Broadcast client updated event"""
    await socketio_service.broadcast_to_tenant(
        tenant_id,
        "client_updated",
        {
            "type": "client_updated",
            "data": client_data,
        },
    )


async def broadcast_staff_status_changed(tenant_id: str, staff_data: Dict[str, Any]):
    """Broadcast staff status changed event"""
    await socketio_service.broadcast_to_tenant(
        tenant_id,
        "staff_status_changed",
        {
            "type": "staff_status_changed",
            "data": staff_data,
        },
    )


async def broadcast_staff_schedule_updated(tenant_id: str, schedule_data: Dict[str, Any]):
    """Broadcast staff schedule updated event"""
    await socketio_service.broadcast_to_tenant(
        tenant_id,
        "staff_schedule_updated",
        {
            "type": "staff_schedule_updated",
            "data": schedule_data,
        },
    )


async def broadcast_staff_break_started(tenant_id: str, staff_data: Dict[str, Any]):
    """Broadcast staff break started event"""
    await socketio_service.broadcast_to_tenant(
        tenant_id,
        "staff_break_started",
        {
            "type": "staff_break_started",
            "data": staff_data,
        },
    )


async def broadcast_staff_break_ended(tenant_id: str, staff_data: Dict[str, Any]):
    """Broadcast staff break ended event"""
    await socketio_service.broadcast_to_tenant(
        tenant_id,
        "staff_break_ended",
        {
            "type": "staff_break_ended",
            "data": staff_data,
        },
    )


async def broadcast_system_notification(tenant_id: str, notification_data: Dict[str, Any]):
    """Broadcast system notification event"""
    await socketio_service.broadcast_to_tenant(
        tenant_id,
        "system_notification",
        {
            "type": "system_notification",
            "data": notification_data,
        },
    )


async def send_notification_to_user(user_id: str, notification_data: Dict[str, Any]):
    """Send notification to a specific user"""
    await socketio_service.send_to_user(
        user_id,
        "notification_received",
        {
            "type": "notification_received",
            "data": notification_data,
        },
    )
