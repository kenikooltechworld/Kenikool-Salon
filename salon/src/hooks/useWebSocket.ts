import { useEffect, useCallback } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useAuthMe } from "@/hooks/useAuthMe";
import {
  initializeSocket,
  getSocket,
  disconnectSocket,
  onSocketEvent,
  offSocketEvent,
} from "@/services/socket";

export interface SocketMessage {
  type:
    | "new_appointment"
    | "payment_received"
    | "payment_failed"
    | "staff_alert"
    | "inventory_alert";
  data: Record<string, unknown>;
  timestamp: string;
}

export interface UseWebSocketOptions {
  onMessage?: (message: SocketMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Error) => void;
}

/**
 * Hook to establish Socket.IO connection for real-time dashboard updates
 * Listens for: new_appointment, payment_received, payment_failed, staff_alert, inventory_alert
 * Automatically invalidates React Query cache on relevant events
 * Socket.IO handles auto-reconnection automatically
 */
export function useWebSocket(options: UseWebSocketOptions = {}) {
  const { onMessage, onConnect, onDisconnect, onError } = options;

  const queryClient = useQueryClient();
  const { data: user } = useAuthMe();

  // Map event types to cache keys that should be invalidated
  const getInvalidateKeys = useCallback((eventType: string) => {
    const keyMap: Record<string, string[]> = {
      new_appointment: [
        "upcoming-appointments",
        "owner-metrics",
        "pending-actions",
      ],
      payment_received: [
        "owner-metrics",
        "pending-actions",
        "revenue-analytics",
      ],
      payment_failed: ["owner-metrics", "pending-actions"],
      staff_alert: ["pending-actions", "staff-performance"],
      inventory_alert: ["owner-metrics", "pending-actions"],
    };
    return keyMap[eventType] || [];
  }, []);

  // Handle incoming Socket.IO messages
  const handleMessage = useCallback(
    (message: SocketMessage) => {
      try {
        // Call custom message handler if provided
        if (onMessage) {
          onMessage(message);
        }

        // Invalidate relevant cache keys
        const keysToInvalidate = getInvalidateKeys(message.type);
        keysToInvalidate.forEach((key) => {
          queryClient.invalidateQueries({ queryKey: [key] });
        });
      } catch (error) {
        console.error("Error handling Socket.IO message:", error);
      }
    },
    [onMessage, queryClient, getInvalidateKeys],
  );

  // Initialize Socket.IO connection on mount (with delay to avoid blocking initial page load)
  useEffect(() => {
    if (!user) {
      return;
    }

    // Delay socket initialization to avoid blocking initial HTTP requests
    const initTimer = setTimeout(() => {
      try {
        const socket = initializeSocket(user.id);

        // Set up event listeners
        socket.on("connect", () => {
          console.log("Socket.IO connected");
          if (onConnect) {
            onConnect();
          }
        });

        socket.on("disconnect", () => {
          console.log("Socket.IO disconnected");
          if (onDisconnect) {
            onDisconnect();
          }
        });

        socket.on("connect_error", (error) => {
          console.error("Socket.IO connection error:", error);
          // Don't call onError for connection errors - they're expected during network issues
          // Just log them and let Socket.IO handle reconnection
        });

        socket.on("connect_timeout", () => {
          console.warn("Socket.IO connection timeout - will retry");
        });

        // Listen for dashboard events
        onSocketEvent("dashboard:update", handleMessage);
      } catch (error) {
        console.error("Error initializing Socket.IO:", error);
        if (onError && error instanceof Error) {
          onError(error);
        }
      }
    }, 2000); // Wait 2 seconds after component mount before connecting

    return () => {
      clearTimeout(initTimer);
      // Clean up event listeners
      offSocketEvent("dashboard:update", handleMessage);
      disconnectSocket();
    };
  }, [user, onConnect, onDisconnect, onError, handleMessage]);

  return {
    isConnected: getSocket()?.connected || false,
  };
}
