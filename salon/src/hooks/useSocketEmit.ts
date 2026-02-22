import { useCallback } from "react";
import { emitSocketEvent } from "@/services/socket";

/**
 * Hook to emit Socket.io events
 */
export function useSocketEmit() {
  return useCallback((event: string, data?: any) => {
    emitSocketEvent(event, data);
  }, []);
}
