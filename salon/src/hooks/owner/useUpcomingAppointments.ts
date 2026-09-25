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

      const extracted: UpcomingAppointment[] = [];
      if (Array.isArray(data)) extracted.push(...data);
      else if (Array.isArray(data?.data)) extracted.push(...data.data);
      else if (Array.isArray(data?.data?.appointments)) extracted.push(...data.data.appointments);
      
      return extracted;
    },
    refetchInterval: 30 * 1000,
    staleTime: 30 * 1000,
    retry: false,
  });
}
