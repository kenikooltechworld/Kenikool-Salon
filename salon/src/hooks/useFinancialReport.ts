import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface RevenueReport {
  total_revenue: number;
  total_refunds: number;
  net_revenue: number;
  payment_count: number;
  refund_count: number;
}

export interface PaymentReport {
  total_payments: number;
  successful_payments: number;
  failed_payments: number;
  pending_payments: number;
  cancelled_payments: number;
  success_rate: number;
  status_breakdown: Record<string, number>;
}

export interface RefundReport {
  total_refunds: number;
  successful_refunds: number;
  failed_refunds: number;
  pending_refunds: number;
  success_rate: number;
  total_refunded_amount: number;
  status_breakdown: Record<string, number>;
}

export interface OutstandingBalanceReport {
  total_outstanding: number;
  customers_with_balance: number;
  customers: Array<{
    id: string;
    name: string;
    email: string;
    outstanding_balance: number;
  }>;
}

export interface ComprehensiveReport {
  revenue: RevenueReport;
  payments: PaymentReport;
  refunds: RefundReport;
  outstanding_balance: OutstandingBalanceReport;
}

/**
 * Fetch revenue report for date range
 */
export function useRevenueReport(startDate: string, endDate: string) {
  return useQuery({
    queryKey: ["financial-reports", "revenue", startDate, endDate],
    queryFn: async () => {
      const { data } = await apiClient.get<{ data: RevenueReport }>(
        "/financial-reports/revenue",
        {
          params: {
            start_date: startDate,
            end_date: endDate,
            use_cache: true,
          },
        },
      );
      return data.data;
    },
    enabled: !!startDate && !!endDate,
  });
}

/**
 * Fetch payment statistics report for date range
 */
export function usePaymentReport(startDate: string, endDate: string) {
  return useQuery({
    queryKey: ["financial-reports", "payments", startDate, endDate],
    queryFn: async () => {
      const { data } = await apiClient.get<{ data: PaymentReport }>(
        "/financial-reports/payments",
        {
          params: {
            start_date: startDate,
            end_date: endDate,
            use_cache: true,
          },
        },
      );
      return data.data;
    },
    enabled: !!startDate && !!endDate,
  });
}

/**
 * Fetch refund statistics report for date range
 */
export function useRefundReport(startDate: string, endDate: string) {
  return useQuery({
    queryKey: ["financial-reports", "refunds", startDate, endDate],
    queryFn: async () => {
      const { data } = await apiClient.get<{ data: RefundReport }>(
        "/financial-reports/refunds",
        {
          params: {
            start_date: startDate,
            end_date: endDate,
            use_cache: true,
          },
        },
      );
      return data.data;
    },
    enabled: !!startDate && !!endDate,
  });
}

/**
 * Fetch outstanding balance report
 */
export function useOutstandingBalanceReport() {
  return useQuery({
    queryKey: ["financial-reports", "outstanding-balance"],
    queryFn: async () => {
      const { data } = await apiClient.get<{ data: OutstandingBalanceReport }>(
        "/financial-reports/outstanding-balance",
        {
          params: {
            use_cache: true,
          },
        },
      );
      return data.data;
    },
  });
}

/**
 * Fetch comprehensive financial report
 */
export function useComprehensiveReport(startDate: string, endDate: string) {
  return useQuery({
    queryKey: ["financial-reports", "comprehensive", startDate, endDate],
    queryFn: async () => {
      const { data } = await apiClient.get<{ data: ComprehensiveReport }>(
        "/financial-reports/comprehensive",
        {
          params: {
            start_date: startDate,
            end_date: endDate,
            use_cache: true,
          },
        },
      );
      return data.data;
    },
    enabled: !!startDate && !!endDate,
  });
}
