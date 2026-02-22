import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface AppointmentHistory {
  id: string;
  customer_id: string;
  appointment_id: string;
  service_id: string;
  staff_id: string;
  service_name: string;
  staff_name: string;
  appointment_date: string;
  appointment_time: string;
  notes: string;
  rating: number;
  feedback: string;
  created_at: string;
}

interface HistoryFilters {
  page?: number;
  page_size?: number;
}

/**
 * Fetch customer appointment history
 */
export function useCustomerHistory(
  customerId: string,
  filters?: HistoryFilters,
) {
  return useQuery({
    queryKey: ["customer-history", customerId, filters],
    queryFn: async () => {
      const { data } = await apiClient.get<any>(
        `/customers/${customerId}/history`,
        {
          params: filters,
        },
      );
      // The backend returns { history: [...], total: ..., page: ..., page_size: ... }
      return data?.history || [];
    },
    enabled: !!customerId,
  });
}

/**
 * Fetch single history item by ID
 */
export function useCustomerHistoryItem(customerId: string, historyId: string) {
  return useQuery({
    queryKey: ["customer-history", customerId, historyId],
    queryFn: async () => {
      const { data } = await apiClient.get<AppointmentHistory>(
        `/customers/${customerId}/history/${historyId}`,
      );
      return data || null;
    },
    enabled: !!customerId && !!historyId,
  });
}
