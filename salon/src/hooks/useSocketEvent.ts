import { useEffect } from "react";
import { onSocketEvent, offSocketEvent } from "@/services/socket";

/**
 * Hook to listen to Socket.io events
 */
export function useSocketEvent(event: string, callback: (data: any) => void) {
  useEffect(() => {
    onSocketEvent(event, callback);

    return () => {
      offSocketEvent(event, callback);
    };
  }, [event, callback]);
}
