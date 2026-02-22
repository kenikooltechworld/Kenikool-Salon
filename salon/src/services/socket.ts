import { io, Socket } from "socket.io-client";

const SOCKET_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

let socket: Socket | null = null;

/**
 * Initialize Socket.io connection
 */
export function initializeSocket(token: string): Socket {
  if (socket?.connected) {
    return socket;
  }

  socket = io(SOCKET_URL, {
    auth: {
      token,
    },
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionDelayMax: 5000,
    reconnectionAttempts: 10,
    transports: ["websocket", "polling"],
  });

  // Connection event handlers
  socket.on("connect", () => {
    console.log("Socket.io connected");
  });

  socket.on("disconnect", () => {
    console.log("Socket.io disconnected");
  });

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
  // Appointments
  APPOINTMENT_CREATED: "appointment:created",
  APPOINTMENT_UPDATED: "appointment:updated",
  APPOINTMENT_CANCELLED: "appointment:cancelled",

  // Notifications
  NOTIFICATION_NEW: "notification:new",

  // Presence
  PRESENCE_ONLINE: "presence:online",
  PRESENCE_OFFLINE: "presence:offline",

  // Queue
  QUEUE_UPDATED: "queue:updated",
};
