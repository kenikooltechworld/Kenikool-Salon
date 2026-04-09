"""WebSocket endpoint for real-time notifications."""

import logging
import json
from typing import Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from app.context import get_tenant_id
from app.models.notification import Notification
from bson import ObjectId

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])

# Store active WebSocket connections per tenant
active_connections: dict[str, Set[WebSocket]] = {}


class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self):
        self.active_connections: dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, tenant_id: str, user_id: str):
        """Accept and register a WebSocket connection."""
        await websocket.accept()
        connection_key = f"{tenant_id}:{user_id}"
        if connection_key not in self.active_connections:
            self.active_connections[connection_key] = set()
        self.active_connections[connection_key].add(websocket)
        logger.info(f"WebSocket connected: {connection_key}")

    def disconnect(self, websocket: WebSocket, tenant_id: str, user_id: str):
        """Unregister a WebSocket connection."""
        connection_key = f"{tenant_id}:{user_id}"
        if connection_key in self.active_connections:
            self.active_connections[connection_key].discard(websocket)
            if not self.active_connections[connection_key]:
                del self.active_connections[connection_key]
        logger.info(f"WebSocket disconnected: {connection_key}")

    async def broadcast_to_user(
        self, tenant_id: str, user_id: str, message: dict
    ):
        """Send a message to all connections for a specific user."""
        connection_key = f"{tenant_id}:{user_id}"
        if connection_key in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[connection_key]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending message: {e}")
                    disconnected.add(connection)

            # Clean up disconnected connections
            for connection in disconnected:
                self.active_connections[connection_key].discard(connection)

    async def broadcast_to_tenant(self, tenant_id: str, message: dict):
        """Send a message to all connections for a specific tenant."""
        disconnected = []
        for connection_key, connections in self.active_connections.items():
            if connection_key.startswith(f"{tenant_id}:"):
                for connection in connections:
                    try:
                        await connection.send_json(message)
                    except Exception as e:
                        logger.error(f"Error sending message: {e}")
                        disconnected.append((connection_key, connection))

        # Clean up disconnected connections
        for connection_key, connection in disconnected:
            if connection_key in self.active_connections:
                self.active_connections[connection_key].discard(connection)


manager = ConnectionManager()


@router.websocket("/ws/notifications")
async def websocket_notifications_endpoint(
    websocket: WebSocket,
    tenant_id: str = Query(..., description="Tenant ID"),
    user_id: str = Query(..., description="User ID"),
):
    """
    WebSocket endpoint for real-time notifications.

    Clients connect with tenant_id and user_id query parameters.
    Server sends events: new_appointment, payment_received, payment_failed, staff_alert, inventory_alert

    Example connection:
        ws://localhost:8000/ws/notifications?tenant_id=123&user_id=456

    Example message:
        {
            "type": "new_appointment",
            "data": {
                "id": "507f1f77bcf86cd799439011",
                "customerName": "John Doe",
                "serviceName": "Haircut",
                "startTime": "2026-03-20T10:00:00"
            },
            "timestamp": "2026-03-20T09:55:00"
        }
    """
    try:
        await manager.connect(websocket, tenant_id, user_id)

        while True:
            # Receive message from client (for keep-alive or future commands)
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                # Handle any client commands here if needed
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON received: {data}")

    except WebSocketDisconnect:
        manager.disconnect(websocket, tenant_id, user_id)
        logger.info(f"WebSocket disconnected for {tenant_id}:{user_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, tenant_id, user_id)


async def send_notification_to_user(
    tenant_id: ObjectId, user_id: ObjectId, notification_type: str, data: dict
):
    """
    Send a real-time notification to a user via WebSocket.

    Args:
        tenant_id: The tenant ID
        user_id: The user ID
        notification_type: Type of notification (new_appointment, payment_received, etc.)
        data: Notification data
    """
    from datetime import datetime

    message = {
        "type": notification_type,
        "data": data,
        "timestamp": datetime.utcnow().isoformat(),
    }

    await manager.broadcast_to_user(str(tenant_id), str(user_id), message)


async def send_notification_to_tenant(
    tenant_id: ObjectId, notification_type: str, data: dict
):
    """
    Send a real-time notification to all users in a tenant via WebSocket.

    Args:
        tenant_id: The tenant ID
        notification_type: Type of notification
        data: Notification data
    """
    from datetime import datetime

    message = {
        "type": notification_type,
        "data": data,
        "timestamp": datetime.utcnow().isoformat(),
    }

    await manager.broadcast_to_tenant(str(tenant_id), message)
