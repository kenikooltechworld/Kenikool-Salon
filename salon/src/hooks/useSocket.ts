import { useEffect } from "react";
import {
  getSocket,
  initializeSocket,
  disconnectSocket,
} from "@/services/socket";
import { useAuthStore } from "@/stores";

/**
 * Hook to initialize and manage Socket.io connection
 */
export function useSocket() {
  const token = useAuthStore((state) => state.token);

  useEffect(() => {
    if (token) {
      initializeSocket(token);
    }

    return () => {
      // Don't disconnect on unmount - keep connection alive
      // disconnectSocket();
    };
  }, [token]);

  return getSocket();
}
