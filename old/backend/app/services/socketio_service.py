"""
Socket.IO Service for Real-time Notifications
Manages Socket.IO connections and message broadcasting
"""
import logging
from typing import Dict, Set, Optional, Callable, Any
from socketio import AsyncServer, ASGIApp
from fastapi import FastAPI
from app.database import Database
from bson import ObjectId

logger = logging.getLogger(__name__)


class SocketIOService:
    """Socket.IO service for managing real-time connections"""

    def __init__(self):
        self.sio = AsyncServer(
            async_mode="asgi",
            cors_allowed_origins="*",
            ping_timeout=60,
            ping_interval=25,
        )
        self.active_connections: Dict[str, Set[str]] = {}  # tenant_id -> set of sid
        self.user_connections: Dict[str, str] = {}  # sid -> user_id
        self.tenant_connections: Dict[str, str] = {}  # sid -> tenant_id

    def attach_to_app(self, app: FastAPI) -> ASGIApp:
        """Attach Socket.IO to FastAPI app"""
        return ASGIApp(self.sio, app)

    async def connect(self, sid: str, environ: Dict[str, Any], auth: Optional[Dict[str, Any]] = None):
        """Handle client connection"""
        try:
            if not auth or "tenant_id" not in auth:
                logger.warning(f"Connection attempt without tenant_id: {sid}")
                await self.sio.disconnect(sid)
                return

            tenant_id = auth.get("tenant_id")
            user_id = auth.get("user_id")

            # Store connection info
            self.tenant_connections[sid] = tenant_id
            if user_id:
                self.user_connections[sid] = user_id

            # Add to active connections
            if tenant_id not in self.active_connections:
                self.active_connections[tenant_id] = set()
            self.active_connections[tenant_id].add(sid)

            logger.info(f"Client connected: {sid} for tenant {tenant_id}")

            # Send connection confirmation
            await self.sio.emit(
                "connected",
                {"message": "Connected to notification server"},
                to=sid,
            )
        except Exception as e:
            logger.error(f"Error in connect handler: {e}")
            await self.sio.disconnect(sid)

    async def disconnect(self, sid: str):
        """Handle client disconnection"""
        try:
            tenant_id = self.tenant_connections.pop(sid, None)
            user_id = self.user_connections.pop(sid, None)

            if tenant_id and tenant_id in self.active_connections:
                self.active_connections[tenant_id].discard(sid)
                if not self.active_connections[tenant_id]:
                    del self.active_connections[tenant_id]

            logger.info(f"Client disconnected: {sid} (tenant: {tenant_id}, user: {user_id})")
        except Exception as e:
            logger.error(f"Error in disconnect handler: {e}")

    async def broadcast_to_tenant(
        self,
        tenant_id: str,
        event: str,
        data: Dict[str, Any],
        skip_sid: Optional[str] = None,
    ):
        """Broadcast message to all clients in a tenant"""
        try:
            if tenant_id not in self.active_connections:
                logger.debug(f"No active connections for tenant {tenant_id}")
                return

            for sid in self.active_connections[tenant_id]:
                if skip_sid and sid == skip_sid:
                    continue

                try:
                    await self.sio.emit(event, data, to=sid)
                except Exception as e:
                    logger.error(f"Error sending to {sid}: {e}")
        except Exception as e:
            logger.error(f"Error broadcasting to tenant {tenant_id}: {e}")

    async def send_to_user(
        self,
        user_id: str,
        event: str,
        data: Dict[str, Any],
    ):
        """Send message to a specific user"""
        try:
            # Find all connections for this user
            for sid, uid in self.user_connections.items():
                if uid == user_id:
                    try:
                        await self.sio.emit(event, data, to=sid)
                    except Exception as e:
                        logger.error(f"Error sending to user {user_id}: {e}")
        except Exception as e:
            logger.error(f"Error in send_to_user: {e}")

    async def send_to_sid(
        self,
        sid: str,
        event: str,
        data: Dict[str, Any],
    ):
        """Send message to a specific connection"""
        try:
            await self.sio.emit(event, data, to=sid)
        except Exception as e:
            logger.error(f"Error sending to {sid}: {e}")

    def get_active_connections_count(self, tenant_id: str) -> int:
        """Get count of active connections for a tenant"""
        return len(self.active_connections.get(tenant_id, set()))

    def get_all_active_connections_count(self) -> int:
        """Get total count of active connections"""
        return sum(len(sids) for sids in self.active_connections.values())


# Global Socket.IO service instance
socketio_service = SocketIOService()
