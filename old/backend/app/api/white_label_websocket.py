"""WebSocket endpoints for real-time white label preview updates"""
import json
import logging
from typing import Dict, Set, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from app.services.preview_engine_service import PreviewEngineService
from app.utils.security import decode_token
from app.database import get_database
from pymongo.database import Database as PyMongoDatabase
from bson import ObjectId

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["websocket"])
preview_engine = PreviewEngineService()

# Store active connections per tenant
active_connections: Dict[str, Set[WebSocket]] = {}


class ConnectionManager:
    """Manage WebSocket connections"""

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, tenant_id: str):
        """Accept and register a new connection"""
        await websocket.accept()
        if tenant_id not in self.active_connections:
            self.active_connections[tenant_id] = set()
        self.active_connections[tenant_id].add(websocket)
        logger.info(f"Client connected for tenant {tenant_id}")

    def disconnect(self, websocket: WebSocket, tenant_id: str):
        """Remove a connection"""
        if tenant_id in self.active_connections:
            self.active_connections[tenant_id].discard(websocket)
            if not self.active_connections[tenant_id]:
                del self.active_connections[tenant_id]
        logger.info(f"Client disconnected for tenant {tenant_id}")

    async def broadcast_to_tenant(self, tenant_id: str, message: dict):
        """Send message to all connections for a tenant"""
        if tenant_id in self.active_connections:
            for connection in self.active_connections[tenant_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending message: {e}")

    async def send_personal(self, websocket: WebSocket, message: dict):
        """Send message to a specific connection"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")


manager = ConnectionManager()


@router.websocket("/white-label/preview/{token}")
async def websocket_preview_endpoint(websocket: WebSocket, token: str):
    """
    WebSocket endpoint for real-time preview updates
    
    Message format for client:
    {
        "type": "update_preview",
        "page_type": "home",
        "branding_config": {...}
    }
    
    Server response:
    {
        "type": "preview_updated",
        "html": "...",
        "page_type": "home",
        "warnings": [...]
    }
    """
    tenant_id = None
    try:
        # Authenticate user from token
        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
            return

        user_id = payload.get("sub")
        if not user_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
            return

        # Get database connection
        db = get_database()
        
        # Get user from database
        user = db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="User not found")
            return

        tenant_id = user.get("tenant_id")
        if not tenant_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="No tenant ID")
            return

        # Connect the client
        await manager.connect(websocket, tenant_id)

        # Send connection confirmation
        await manager.send_personal(websocket, {
            "type": "connected",
            "message": "Connected to preview updates",
            "tenant_id": tenant_id,
        })

        # Listen for messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "update_preview":
                try:
                    # Generate preview
                    page_type = message.get("page_type", "home")
                    branding_config = message.get("branding_config", {})

                    preview = await preview_engine.generate_preview(
                        branding_config=branding_config,
                        page_type=page_type,
                        tenant_id=tenant_id,
                    )

                    # Send updated preview
                    await manager.send_personal(websocket, {
                        "type": "preview_updated",
                        "html": preview.html,
                        "page_type": preview.page_type,
                        "accessibility_warnings": [
                            {
                                "type": w.type,
                                "severity": w.severity,
                                "message": w.message,
                                "suggestion": w.suggestion,
                            }
                            for w in preview.accessibility_warnings
                        ],
                        "branding_applied": preview.branding_applied,
                    })

                except ValueError as e:
                    await manager.send_personal(websocket, {
                        "type": "error",
                        "error": str(e),
                    })

            elif message.get("type") == "validate_config":
                try:
                    branding_config = message.get("branding_config", {})

                    # Validate configuration
                    warnings = await preview_engine.validate_preview_config(branding_config)

                    await manager.send_personal(websocket, {
                        "type": "validation_result",
                        "warnings": [
                            {
                                "type": w.type,
                                "severity": w.severity,
                                "message": w.message,
                                "suggestion": w.suggestion,
                            }
                            for w in warnings
                        ],
                        "has_errors": any(w.severity == "error" for w in warnings),
                        "has_warnings": any(w.severity == "warning" for w in warnings),
                    })

                except Exception as e:
                    await manager.send_personal(websocket, {
                        "type": "error",
                        "error": str(e),
                    })

            elif message.get("type") == "ping":
                # Respond to ping to keep connection alive
                await manager.send_personal(websocket, {
                    "type": "pong",
                })

    except WebSocketDisconnect:
        if tenant_id:
            manager.disconnect(websocket, tenant_id)
            logger.info(f"WebSocket disconnected for tenant {tenant_id}")

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if tenant_id:
            manager.disconnect(websocket, tenant_id)
