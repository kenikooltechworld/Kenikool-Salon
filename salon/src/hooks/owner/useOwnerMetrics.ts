import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils";

export interface DashboardMetrics {
  revenue: {
    current: number;
    previous: number;
    trend: "up" | "down" | "neutral";
    trendPercentage: number;
  };
  appointments: {
    today: number;
    thisWeek: number;
    thisMonth: number;
    trend: "up" | "down" | "neutral";
  };
  satisfaction: {
    score: number;
    count: number;
    trend: "up" | "down" | "neutral";
  };
  staffUtilization: {
    percentage: number;
    bookedHours: number;
    availableHours: number;
  };
  pendingPayments: {
    count: number;
    totalAmount: number;
    oldestDate: string | null;
  };
  inventoryStatus: {
    lowStockCount: number;
    expiringCount: number;
  };
}

/**
 * Fetch all dashboard metrics in a single request
 * Includes: revenue, appointments, satisfaction, utilization, pending payments, inventory
 * Auto-refreshes every 30 seconds
 * Implements caching with 30 second TTL
 */
export function useOwnerMetrics() {
  return useQuery({
    queryKey: ["owner-metrics"],
    queryFn: async () => {
      const { data } = await apiClient.get<{ data: DashboardMetrics }>(
        "/owner/dashboard/metrics",
      );
      return data.data || data;
    },
    refetchInterval: 30 * 1000,
    staleTime: 30 * 1000,
    retry: false,
  });
}
