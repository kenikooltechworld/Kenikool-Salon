import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";
import { useAuthStore } from "@/stores/auth";

export interface StaffMetrics {
  todayAppointments: number;
  upcomingShifts: number;
  pendingTimeOff: number;
  earningsSummary: {
    total: number;
    thisMonth: number;
    thisWeek: number;
  };
}

/**
 * Fetch dashboard metrics for current staff member
 * Includes: today's appointments, upcoming shifts, pending time off, earnings summary
 * Auto-refreshes every 5 minutes
 * Implements exponential backoff retry strategy for failed requests
 */
export function useStaffMetrics() {
  const user = useAuthStore((state) => state.user);

  return useQuery({
    queryKey: ["staff-metrics"],
    queryFn: async () => {
      const { data } = await apiClient.get<StaffMetrics>(
        `/staff/${user?.id}/metrics`,
      );
      return (
        data || {
          todayAppointments: 0,
          upcomingShifts: 0,
          pendingTimeOff: 0,
          earningsSummary: {
            total: 0,
            thisMonth: 0,
            thisWeek: 0,
          },
        }
      );
    },
    enabled: !!user?.id,
    refetchInterval: 5 * 60 * 1000, // 5 minutes
    staleTime: 1 * 60 * 1000, // 1 minute
    retry: 3, // Retry up to 3 times
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000), // Exponential backoff: 1s, 2s, 4s
  });
}
