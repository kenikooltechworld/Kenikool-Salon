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
      let extracted: UpcomingAppointment[] = [];
      if (Array.isArray(data)) extracted = data;
      else if (Array.isArray(data?.data)) extracted = data.data;
      else if (Array.isArray(data?.data?.appointments)) extracted = data.data.appointments;
      
      console.log("[DashboardHook][useUpcomingAppointments] raw response:", data);
      console.log("[DashboardHook][useUpcomingAppointments] extracted count:", extracted.length);
      return extracted || [];
    },
    refetchInterval: 30 * 1000, // 30 seconds
    staleTime: 30 * 1000, // 30 seconds
    retry: false, // Don't retry - fail fast
    placeholderData: (previousData) => previousData, // Keep old data while refetching
  });
}
