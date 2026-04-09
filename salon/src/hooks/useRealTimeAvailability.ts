import { useEffect, useState, useCallback } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";
import { io, Socket } from "socket.io-client";

interface AvailabilityEvent {
  id: string;
  tenant_id: string;
  service_id: string;
  staff_id?: string;
  date: string;
  time_slot: string;
  event_type: "slot_taken" | "slot_freed" | "slot_blocked";
  viewer_count: number;
  created_at: string;
}

interface SlotViewerCount {
  service_id: string;
  staff_id?: string;
  date: string;
  time_slot: string;
  viewer_count: number;
}

interface UseRealTimeAvailabilityOptions {
  serviceId: string | null;
  date: string | null; // YYYY-MM-DD format
  enabled?: boolean;
}

let socket: Socket | null = null;

export function useRealTimeAvailability({
  serviceId,
  date,
  enabled = true,
}: UseRealTimeAvailabilityOptions) {
  const queryClient = useQueryClient();
  const [isConnected, setIsConnected] = useState(false);
  const [slotViewers, setSlotViewers] = useState<Record<string, number>>({});

  // Fetch recent availability events
  const { data: recentEvents, isLoading } = useQuery({
    queryKey: ["availability-events", serviceId, date],
    queryFn: async () => {
      if (!serviceId || !date) return [];
      const { data } = await apiClient.get<AvailabilityEvent[]>(
        `/public/availability-events/recent`,
        {
          params: { service_id: serviceId, date, minutes: 30 },
        },
      );
      return data;
    },
    enabled: enabled && !!serviceId && !!date,
    refetchInterval: 30000, // Fallback polling every 30 seconds
  });

  // Initialize WebSocket connection
  useEffect(() => {
    if (!enabled || !serviceId || !date) return;

    // Get tenant ID from subdomain
    const hostname = window.location.hostname;
    const parts = hostname.split(".");
    const tenantSubdomain = parts[0];

    // Connect to WebSocket server
    const socketUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";

    if (!socket) {
      socket = io(socketUrl, {
        transports: ["websocket", "polling"],
        reconnection: true,
        reconnectionDelay: 1000,
        reconnectionAttempts: 5,
      });

      socket.on("connect", () => {
        console.log("WebSocket connected");
        setIsConnected(true);
      });

      socket.on("disconnect", () => {
        console.log("WebSocket disconnected");
        setIsConnected(false);
      });

      socket.on("connect_error", (error) => {
        console.error("WebSocket connection error:", error);
        setIsConnected(false);
      });
    }

    // Join availability room for this service/date
    socket.emit("join_availability_room", {
      tenant_id: tenantSubdomain,
      service_id: serviceId,
      date: date,
    });

    // Listen for availability updates
    const handleAvailabilityUpdate = (data: {
      event_type: string;
      time_slot: string;
      staff_id?: string;
      appointment_id?: string;
    }) => {
      console.log("Availability update received:", data);

      // Invalidate availability queries to refetch
      queryClient.invalidateQueries({ queryKey: ["availability"] });
      queryClient.invalidateQueries({ queryKey: ["time-slots"] });
      queryClient.invalidateQueries({ queryKey: ["availability-events"] });
    };

    // Listen for viewer count updates
    const handleViewerJoined = (data: { service_id: string; date: string }) => {
      console.log("Viewer joined:", data);
      // Could update viewer count here if needed
    };

    const handleViewerLeft = (data: { service_id: string; date: string }) => {
      console.log("Viewer left:", data);
      // Could update viewer count here if needed
    };

    socket.on("availability:update", handleAvailabilityUpdate);
    socket.on("availability:viewer_joined", handleViewerJoined);
    socket.on("availability:viewer_left", handleViewerLeft);

    // Cleanup on unmount
    return () => {
      if (socket) {
        socket.emit("leave_availability_room", {
          tenant_id: tenantSubdomain,
          service_id: serviceId,
          date: date,
        });

        socket.off("availability:update", handleAvailabilityUpdate);
        socket.off("availability:viewer_joined", handleViewerJoined);
        socket.off("availability:viewer_left", handleViewerLeft);
      }
    };
  }, [enabled, serviceId, date, queryClient]);

  // Track slot viewing
  const trackSlotView = useCallback(
    async (
      timeSlot: string,
      staffId?: string,
      action: "join" | "leave" = "join",
    ) => {
      if (!serviceId || !date) return;

      try {
        const { data } = await apiClient.post<SlotViewerCount>(
          "/public/availability-events/viewer-update",
          {
            service_id: serviceId,
            staff_id: staffId,
            date: date,
            time_slot: timeSlot,
            action: action,
          },
        );

        // Update local viewer count
        const key = `${timeSlot}-${staffId || "any"}`;
        setSlotViewers((prev) => ({
          ...prev,
          [key]: data.viewer_count,
        }));

        return data.viewer_count;
      } catch (error) {
        console.error("Error tracking slot view:", error);
        return 0;
      }
    },
    [serviceId, date],
  );

  // Get viewer count for a specific slot
  const getSlotViewerCount = useCallback(
    (timeSlot: string, staffId?: string): number => {
      const key = `${timeSlot}-${staffId || "any"}`;
      return slotViewers[key] || 0;
    },
    [slotViewers],
  );

  return {
    recentEvents,
    isLoading,
    isConnected,
    trackSlotView,
    getSlotViewerCount,
    slotViewers,
  };
}
