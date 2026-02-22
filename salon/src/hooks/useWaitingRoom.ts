import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface QueueEntry {
  id: string;
  appointment_id: string;
  customer_id: string;
  customer_name: string;
  customer_phone?: string;
  check_in_time: string;
  called_time?: string;
  service_start_time?: string;
  service_end_time?: string;
  status:
    | "waiting"
    | "called"
    | "in_service"
    | "completed"
    | "no_show"
    | "cancelled";
  position: number;
  wait_duration_minutes?: number;
  service_duration_minutes?: number;
  estimated_wait_time_minutes?: number;
  service_id?: string;
  service_name?: string;
  staff_id?: string;
  staff_name?: string;
  notes?: string;
}

export interface WaitingRoomStats {
  total_waiting: number;
  average_wait_time_minutes: number;
  longest_wait_time_minutes: number;
  total_completed_today: number;
  total_no_shows_today: number;
}

export interface QueuePosition {
  position: number;
  estimated_wait_time_minutes: number;
  status: string;
}

// Get current queue
export const useWaitingRoomQueue = () => {
  return useQuery({
    queryKey: ["waiting-room-queue"],
    queryFn: async () => {
      const { data } = await apiClient.get("/waiting-room/queue");
      return data.data as QueueEntry[];
    },
    refetchInterval: 5000, // Refetch every 5 seconds
  });
};

// Check in customer
export const useCheckIn = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (appointmentId: string) => {
      const { data } = await apiClient.post("/waiting-room/check-in", {
        appointment_id: appointmentId,
      });
      return data.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["waiting-room-queue"] });
      queryClient.invalidateQueries({ queryKey: ["queue-stats"] });
    },
  });
};

// Get customer position in queue
export const useQueuePosition = (customerId: string) => {
  return useQuery({
    queryKey: ["queue-position", customerId],
    queryFn: async () => {
      const { data } = await apiClient.get(
        `/waiting-room/position/${customerId}`,
      );
      return data.data as QueuePosition;
    },
    refetchInterval: 5000,
    enabled: !!customerId,
  });
};

// Get queue statistics
export const useQueueStats = () => {
  return useQuery({
    queryKey: ["queue-stats"],
    queryFn: async () => {
      const { data } = await apiClient.get("/waiting-room/stats");
      return data.data as WaitingRoomStats;
    },
    refetchInterval: 10000, // Refetch every 10 seconds
  });
};

// Call next customer
export const useCallNextCustomer = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      const { data } = await apiClient.post("/waiting-room/call-next");
      return data.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["waiting-room-queue"] });
      queryClient.invalidateQueries({ queryKey: ["queue-stats"] });
    },
  });
};

// Mark customer as in service
export const useMarkInService = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (queueEntryId: string) => {
      const { data } = await apiClient.patch(
        `/waiting-room/${queueEntryId}/in-service`,
      );
      return data.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["waiting-room-queue"] });
      queryClient.invalidateQueries({ queryKey: ["queue-stats"] });
    },
  });
};

// Mark customer as completed
export const useMarkCompleted = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (queueEntryId: string) => {
      const { data } = await apiClient.patch(
        `/waiting-room/${queueEntryId}/completed`,
      );
      return data.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["waiting-room-queue"] });
      queryClient.invalidateQueries({ queryKey: ["queue-stats"] });
    },
  });
};

// Mark customer as no-show
export const useMarkNoShow = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({
      queueEntryId,
      reason,
    }: {
      queueEntryId: string;
      reason?: string;
    }) => {
      const { data } = await apiClient.patch(
        `/waiting-room/${queueEntryId}/no-show`,
        {
          reason,
        },
      );
      return data.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["waiting-room-queue"] });
      queryClient.invalidateQueries({ queryKey: ["queue-stats"] });
    },
  });
};

// Get queue history
export const useQueueHistory = (filters?: {
  date?: string;
  status?: string;
}) => {
  return useQuery({
    queryKey: ["queue-history", filters],
    queryFn: async () => {
      const { data } = await apiClient.get("/waiting-room/history", {
        params: filters,
      });
      return data.data as QueueEntry[];
    },
  });
};
