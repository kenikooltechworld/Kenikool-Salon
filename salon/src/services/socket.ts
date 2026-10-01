import { io, Socket } from "socket.io-client";

const SOCKET_URL = import.meta.env.VITE_WS_URL || "/socket.io";

let socket: Socket | null = null;

/**
 * Initialize Socket.io connection
 * Note: Socket connects to /socket.io path on the backend
 * Authentication is handled via httpOnly cookies
 */
export function initializeSocket(options?: { tenantId?: string; userId?: string }): Socket {
  if (socket?.connected) {
    return socket;
  }

  const query: Record<string, string> = {};
  if (options?.tenantId) query.tenant_id = options.tenantId;
  if (options?.userId) query.user_id = options.userId;

  socket = io(SOCKET_URL, {
    path: "/socket.io", // Explicitly set the Socket.IO path
    withCredentials: true, // Send cookies with requests
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionDelayMax: 5000,
    reconnectionAttempts: 5, // Reduced from 10
    timeout: 10000, // Add 10 second connection timeout
    transports: ["websocket"], // Use only websocket, not polling
    query,
  });

  // Connection event handlers
  socket.on("connect_error", (error) => {
    console.error("Socket.io connection error:", error);
  });

  return socket;
}

/**
 * Get Socket.io instance
 */
export function getSocket(): Socket | null {
  return socket;
}

/**
 * Disconnect Socket.io
 */
export function disconnectSocket(): void {
  if (socket) {
    socket.disconnect();
    socket = null;
  }
}

/**
 * Listen to Socket.io event
 */
export function onSocketEvent(
  event: string,
  callback: (data: any) => void,
): void {
  if (socket) {
    socket.on(event, callback);
  }
}

/**
 * Remove Socket.io event listener
 */
export function offSocketEvent(
  event: string,
  callback?: (data: any) => void,
): void {
  if (socket) {
    if (callback) {
      socket.off(event, callback);
    } else {
      socket.off(event);
    }
  }
}

/**
 * Emit Socket.io event
 */
export function emitSocketEvent(event: string, data?: any): void {
  if (socket) {
    socket.emit(event, data);
  }
}

/**
 * Real-time event types
 */
export const SOCKET_EVENTS = {
  // Connection
  CONNECT: "connect",
  DISCONNECT: "disconnect",
  CONNECT_ERROR: "connect_error",
  CONNECT_RESPONSE: "connect_response",

  // Notifications
  NOTIFICATION_NEW: "notification:new",

  // Appointments
  APPOINTMENT_CREATED: "appointment:created",
  APPOINTMENT_UPDATED: "appointment:updated",
  APPOINTMENT_CANCELLED: "appointment:cancelled",

  // Payments
  PAYMENT_RECEIVED: "payment_received",
  PAYMENT_FAILED: "payment_failed",

  // Staff
  STAFF_ALERT: "staff_alert",

  // Inventory
  INVENTORY_ALERT: "inventory_alert",

  // Dashboard
  DASHBOARD_UPDATE: "dashboard:update",

  // Queue
  QUEUE_UPDATED: "queue:updated",

  // Availability
  AVAILABILITY_UPDATE: "availability:update",
  AVAILABILITY_VIEWER_JOINED: "availability:viewer_joined",
  AVAILABILITY_VIEWER_LEFT: "availability:viewer_left",

  // Presence
  PRESENCE_ONLINE: "presence:online",
  PRESENCE_OFFLINE: "presence:offline",
};
