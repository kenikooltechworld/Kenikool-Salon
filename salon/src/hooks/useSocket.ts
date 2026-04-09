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
  const user = useAuthStore((state) => state.user);

  useEffect(() => {
    if (user) {
      // Initialize socket with user info (token is in httpOnly cookie)
      initializeSocket();
    }

    return () => {
      // Don't disconnect on unmount - keep connection alive
      // disconnectSocket();
    };
  }, [user]);

  return getSocket();
}
