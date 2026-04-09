import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";
import { useAuthStore } from "@/stores/auth";

export interface Commission {
  id: string;
  staff_id: string;
  transaction_id: string;
  commission_amount: number;
  commission_rate: number;
  commission_type: "percentage" | "fixed";
  calculated_at: string;
}

interface MyEarningsFilters {
  startDate?: string;
  endDate?: string;
  serviceType?: string;
  commissionType?: "percentage" | "fixed";
  page?: number;
  pageSize?: number;
}

interface EarningsSummary {
  totalEarnings: number;
  commissions: Commission[];
  period: {
    startDate: string;
    endDate: string;
  };
}

/**
 * Fetch current staff member's earnings with date range filtering
 * Automatically filters by staff_id from authenticated user
 * Phase 1: Basic version with date range filtering
 */
export function useMyEarnings(filters?: MyEarningsFilters) {
  const user = useAuthStore((state) => state.user);

  return useQuery({
    queryKey: ["my-earnings", filters],
    queryFn: async () => {
      const { data } = await apiClient.get<EarningsSummary>(
        `/commissions/staff/${user?.id}`,
        {
          params: filters,
        },
      );
      return (
        data || {
          totalEarnings: 0,
          commissions: [],
          period: { startDate: "", endDate: "" },
        }
      );
    },
    enabled: !!user?.id,
  });
}

/**
 * Fetch earnings summary for current staff member
 */
export function useMyEarningsSummary() {
  const user = useAuthStore((state) => state.user);

  return useQuery({
    queryKey: ["my-earnings-summary"],
    queryFn: async () => {
      const { data } = await apiClient.get<{
        totalEarnings: number;
        thisMonth: number;
        thisWeek: number;
      }>(`/commissions/staff/${user?.id}/summary`);
      return data || { totalEarnings: 0, thisMonth: 0, thisWeek: 0 };
    },
    enabled: !!user?.id,
  });
}

/**
 * Fetch earnings breakdown by service type or date range
 * Useful for displaying earnings analytics and trends
 */
export function useMyEarningsBreakdown(
  breakdownType: "service" | "date" = "service",
  filters?: MyEarningsFilters,
) {
  const user = useAuthStore((state) => state.user);

  return useQuery({
    queryKey: ["my-earnings-breakdown", breakdownType, filters],
    queryFn: async () => {
      const { data } = await apiClient.get<{
        breakdown: Array<{
          label: string;
          amount: number;
          count: number;
          percentage: number;
        }>;
        total: number;
      }>(`/commissions/staff/${user?.id}/breakdown`, {
        params: {
          ...filters,
          breakdownType,
        },
      });
      return (
        data || {
          breakdown: [],
          total: 0,
        }
      );
    },
    enabled: !!user?.id,
  });
}

/**
 * Fetch earnings by date range with optional service type filter
 * Supports daily, weekly, and monthly aggregation
 */
export function useMyEarningsByDateRange(
  startDate: string,
  endDate: string,
  aggregation: "daily" | "weekly" | "monthly" = "daily",
  serviceType?: string,
) {
  const user = useAuthStore((state) => state.user);

  return useQuery({
    queryKey: [
      "my-earnings-by-date",
      startDate,
      endDate,
      aggregation,
      serviceType,
    ],
    queryFn: async () => {
      const { data } = await apiClient.get<{
        data: Array<{
          date: string;
          amount: number;
          count: number;
        }>;
        total: number;
      }>(`/commissions/staff/${user?.id}/by-date`, {
        params: {
          startDate,
          endDate,
          aggregation,
          serviceType,
        },
      });
      return (
        data || {
          data: [],
          total: 0,
        }
      );
    },
    enabled: !!user?.id && !!startDate && !!endDate,
  });
}
