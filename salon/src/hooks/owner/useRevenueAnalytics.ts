import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface RevenueDataPoint {
  date: string;
  revenue: number;
}

export interface ServiceRevenue {
  serviceName: string;
  revenue: number;
  percentage: number;
}

export interface StaffRevenue {
  staffName: string;
  revenue: number;
  percentage: number;
}

export interface RevenueAnalytics {
  dailyRevenue: RevenueDataPoint[];
  weeklyRevenue: RevenueDataPoint[];
  monthlyRevenue: RevenueDataPoint[];
  byService: ServiceRevenue[];
  byStaff: StaffRevenue[];
  totalRevenue: number;
  averageDailyRevenue: number;
  growthPercentage: number;
  period: "daily" | "weekly" | "monthly";
}

/**
 * Fetch revenue analytics data for charts
 * Includes daily, weekly, monthly aggregations
 * Includes revenue by service type and staff member
 * Auto-refreshes every 1 hour
 */
export function useRevenueAnalytics(
  period: "daily" | "weekly" | "monthly" = "daily",
  days: number = 30,
) {
  return useQuery({
    queryKey: ["revenue-analytics", period, days],
    queryFn: async () => {
      const { data } = await apiClient.get<{ data: RevenueAnalytics }>(
        "/owner/dashboard/revenue-analytics",
        { params: { period, days } },
      );
      // Return the analytics object directly, not the response wrapper
      return data.data || data;
    },
    refetchInterval: 60 * 60 * 1000, // 1 hour
    staleTime: 60 * 60 * 1000, // 1 hour
    retry: false, // Don't retry - fail fast
    placeholderData: (previousData) => previousData,
  });
}
