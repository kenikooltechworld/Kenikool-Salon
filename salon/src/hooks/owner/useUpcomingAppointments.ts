import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface UpcomingAppointment {
  id: string;
  customerName: string;
  serviceName: string;
  staffName: string;
  startTime: string;
  endTime: string;
  status: "confirmed" | "pending" | "completed" | "cancelled";
  isPublicBooking: boolean;
}

/**
 * Fetch upcoming appointments for the dashboard
 * Returns next 5-10 appointments sorted chronologically
 * Includes both internal and public bookings
 * Auto-refreshes every 30 seconds
 */
export function useUpcomingAppointments(limit: number = 10) {
  return useQuery({
    queryKey: ["upcoming-appointments", limit],
    queryFn: async () => {
      const { data } = await apiClient.get<{
        data: {
          appointments: UpcomingAppointment[];
          total: number;
          limit: number;
          offset: number;
        };
      }>("/owner/dashboard/appointments", { params: { limit } });

      // Extract appointments array from response
      if (Array.isArray(data)) return data;
      if (Array.isArray(data?.data)) return data.data;
      if (Array.isArray(data?.data?.appointments))
        return data.data.appointments;
      return [];
    },
    refetchInterval: 30 * 1000, // 30 seconds
    staleTime: 30 * 1000, // 30 seconds
    retry: false, // Don't retry - fail fast
    placeholderData: (previousData) => previousData, // Keep old data while refetching
  });
}
