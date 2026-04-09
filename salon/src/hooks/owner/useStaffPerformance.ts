import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface StaffPerformanceMetric {
  staffId: string;
  staffName: string;
  revenue: number;
  revenueRank: number;
  utilizationRate: number;
  satisfactionScore: number;
  attendanceRate: number;
  previousPeriodRevenue: number;
  revenueGrowth: number;
}

export interface StaffPerformanceData {
  topStaff: StaffPerformanceMetric[];
  averageUtilization: number;
  averageSatisfaction: number;
  averageAttendance: number;
}

/**
 * Fetch staff performance metrics
 * Includes top 5 staff by revenue
 * Includes utilization, satisfaction, and attendance rates
 * Includes comparison to previous period
 * Auto-refreshes every 1 hour
 */
export function useStaffPerformance() {
  return useQuery({
    queryKey: ["staff-performance"],
    queryFn: async () => {
      const { data } = await apiClient.get<{ data: StaffPerformanceData }>(
        "/owner/dashboard/staff-performance",
      );
      // Return the performance data directly, not the response wrapper
      return data.data || data;
    },
    refetchInterval: 60 * 60 * 1000, // 1 hour
    staleTime: 60 * 60 * 1000, // 1 hour
    retry: false, // Don't retry - fail fast
    placeholderData: (previousData) => previousData,
  });
}
