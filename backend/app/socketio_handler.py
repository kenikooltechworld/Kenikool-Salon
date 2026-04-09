"""Socket.IO event handlers and configuration."""

import logging
from typing import Dict, Any
from socketio import AsyncServer, ASGIApp
from fastapi import FastAPI

logger = logging.getLogger(__name__)

# Create Socket.IO server
sio = AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    ping_timeout=20,  # Reduced from 60 to 20 seconds
    ping_interval=10,  # Reduced from 25 to 10 seconds
    logger=True,
    engineio_logger=True,
    max_http_buffer_size=1e6,  # 1MB max message size
    allow_upgrades=True,  # Allow transport upgrades
)

# Track connected clients
connected_clients: Dict[str, Dict[str, Any]] = {}


@sio.event
async def connect(sid, environ):
    """Handle client connection."""
    try:
        # Get auth token from query params or headers
        query_string = environ.get('QUERY_STRING', '')
        headers = environ.get('headers', {})
        
        logger.info(f"Client {sid} connected")
        logger.info(f"Query string: {query_string}")
        logger.info(f"Headers: {headers}")
        
        connected_clients[sid] = {
            'sid': sid,
            'connected_at': None,
        }
        
        # Send connection confirmation
        await sio.emit('connect_response', {'data': 'Connected to server'}, to=sid)
        logger.info(f"Connection confirmed for client {sid}")
    except Exception as e:
        logger.error(f"Error in connect handler: {e}", exc_info=True)


@sio.event
async def disconnect(sid):
    """Handle client disconnection."""
    try:
        if sid in connected_clients:
            del connected_clients[sid]
        logger.info(f"Client {sid} disconnected")
    except Exception as e:
        logger.error(f"Error in disconnect handler: {e}", exc_info=True)


@sio.event
async def dashboard_update(sid, data):
    """Handle dashboard update events."""
    try:
        logger.info(f"Dashboard update from {sid}: {data}")
        # Broadcast to all connected clients
        await sio.emit('dashboard:update', data, skip_sid=sid)
    except Exception as e:
        logger.error(f"Error in dashboard_update handler: {e}", exc_info=True)


@sio.event
async def join_availability_room(sid, data):
    """Join a room for availability updates for a specific service/date."""
    try:
        tenant_id = data.get('tenant_id')
        service_id = data.get('service_id')
        date = data.get('date')
        
        if not all([tenant_id, service_id, date]):
            logger.warning(f"Missing required data for join_availability_room: {data}")
            return
        
        room = f"availability:{tenant_id}:{service_id}:{date}"
        await sio.enter_room(sid, room)
        
        logger.info(f"Client {sid} joined availability room: {room}")
        
        # Notify others in the room about new viewer
        await sio.emit('availability:viewer_joined', {
            'service_id': service_id,
            'date': date,
        }, room=room, skip_sid=sid)
    except Exception as e:
        logger.error(f"Error in join_availability_room handler: {e}", exc_info=True)


@sio.event
async def leave_availability_room(sid, data):
    """Leave an availability room."""
    try:
        tenant_id = data.get('tenant_id')
        service_id = data.get('service_id')
        date = data.get('date')
        
        if not all([tenant_id, service_id, date]):
            logger.warning(f"Missing required data for leave_availability_room: {data}")
            return
        
        room = f"availability:{tenant_id}:{service_id}:{date}"
        await sio.leave_room(sid, room)
        
        logger.info(f"Client {sid} left availability room: {room}")
        
        # Notify others in the room about viewer leaving
        await sio.emit('availability:viewer_left', {
            'service_id': service_id,
            'date': date,
        }, room=room, skip_sid=sid)
    except Exception as e:
        logger.error(f"Error in leave_availability_room handler: {e}", exc_info=True)


"""Socket.IO event handlers and configuration."""

import logging
from typing import Dict, Any
from socketio import AsyncServer
from fastapi import FastAPI

logger = logging.getLogger(__name__)

# Create Socket.IO server with optimized settings
sio = AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    ping_timeout=20,  # Reduced from 60 to 20 seconds
    ping_interval=10,  # Reduced from 25 to 10 seconds
    logger=True,
    engineio_logger=True,
    max_http_buffer_size=1e6,  # 1MB max message size
    allow_upgrades=True,  # Allow transport upgrades
)

# Track connected clients
connected_clients: Dict[str, Dict[str, Any]] = {}


@sio.event
async def connect(sid, environ):
    """Handle client connection."""
    try:
        # Get auth token from query params or headers
        query_string = environ.get('QUERY_STRING', '')
        headers = environ.get('headers', {})
        
        logger.info(f"Client {sid} connected")
        logger.debug(f"Query string: {query_string}")
        
        connected_clients[sid] = {
            'sid': sid,
            'connected_at': None,
        }
        
        # Send connection confirmation
        await sio.emit('connect_response', {'data': 'Connected to server'}, to=sid)
        logger.info(f"Connection confirmed for client {sid}")
    except Exception as e:
        logger.error(f"Error in connect handler: {e}", exc_info=True)


@sio.event
async def disconnect(sid):
    """Handle client disconnection."""
    try:
        if sid in connected_clients:
            del connected_clients[sid]
        logger.info(f"Client {sid} disconnected")
    except Exception as e:
        logger.error(f"Error in disconnect handler: {e}", exc_info=True)


@sio.event
async def dashboard_update(sid, data):
    """Handle dashboard update events."""
    try:
        logger.info(f"Dashboard update from {sid}: {data}")
        # Broadcast to all connected clients
        await sio.emit('dashboard:update', data, skip_sid=sid)
    except Exception as e:
        logger.error(f"Error in dashboard_update handler: {e}", exc_info=True)


@sio.event
async def join_availability_room(sid, data):
    """Join a room for availability updates for a specific service/date."""
    try:
        tenant_id = data.get('tenant_id')
        service_id = data.get('service_id')
        date = data.get('date')
        
        if not all([tenant_id, service_id, date]):
            logger.warning(f"Missing required data for join_availability_room: {data}")
            return
        
        room = f"availability:{tenant_id}:{service_id}:{date}"
        await sio.enter_room(sid, room)
        
        logger.info(f"Client {sid} joined availability room: {room}")
        
        # Notify others in the room about new viewer
        await sio.emit('availability:viewer_joined', {
            'service_id': service_id,
            'date': date,
        }, room=room, skip_sid=sid)
    except Exception as e:
        logger.error(f"Error in join_availability_room handler: {e}", exc_info=True)


@sio.event
async def leave_availability_room(sid, data):
    """Leave an availability room."""
    try:
        tenant_id = data.get('tenant_id')
        service_id = data.get('service_id')
        date = data.get('date')
        
        if not all([tenant_id, service_id, date]):
            logger.warning(f"Missing required data for leave_availability_room: {data}")
            return
        
        room = f"availability:{tenant_id}:{service_id}:{date}"
        await sio.leave_room(sid, room)
        
        logger.info(f"Client {sid} left availability room: {room}")
        
        # Notify others in the room about viewer leaving
        await sio.emit('availability:viewer_left', {
            'service_id': service_id,
            'date': date,
        }, room=room, skip_sid=sid)
    except Exception as e:
        logger.error(f"Error in leave_availability_room handler: {e}", exc_info=True)


async def emit_availability_update(tenant_id: str, service_id: str, date: str, event_data: dict):
    """Emit availability update to all clients in the room."""
    try:
        room = f"availability:{tenant_id}:{service_id}:{date}"
        await sio.emit('availability:update', event_data, room=room)
        logger.info(f"Emitted availability update to room {room}: {event_data}")
    except Exception as e:
        logger.error(f"Error emitting availability update: {e}", exc_info=True)


def setup_socketio(app: FastAPI):
    """Setup Socket.IO with FastAPI app.
    
    IMPORTANT: Socket.IO wraps the entire FastAPI app, but this is necessary
    for Socket.IO to work correctly. The performance impact is minimal because:
    1. Socket.IO only intercepts requests to /socket.io/* paths
    2. Regular HTTP requests are passed through to FastAPI immediately
    3. The ASGI wrapper adds negligible overhead (<1ms per request)
    """
    from socketio import ASGIApp
    
    # Create ASGI app that wraps FastAPI with Socket.IO
    # Socket.IO will handle /socket.io/* paths, all other paths go to FastAPI
    asgi_app = ASGIApp(sio, app, socketio_path='socket.io')
    
    logger.info("Socket.IO ASGI app created (wraps FastAPI, handles /socket.io/* paths only)")
    return asgi_app
