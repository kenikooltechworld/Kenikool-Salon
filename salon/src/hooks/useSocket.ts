import { useEffect } from "react";
import {
  getSocket,
  initializeSocket,
  disconnectSocket,
} from "@/services/socket";
import { useAuthUser } from "@/hooks/useAuthUser";

/**
 * Hook to initialize and manage Socket.io connection
 */
export function useSocket() {
  const { data: user } = useAuthUser();

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
