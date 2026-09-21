import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface RevenueReport {
  totalRevenue: number;
  totalRefunds: number;
  netRevenue: number;
  paymentCount: number;
  refundCount: number;
}

export interface PaymentReport {
  totalPayments: number;
  successfulPayments: number;
  failedPayments: number;
  pendingPayments: number;
  cancelledPayments: number;
  successRate: number;
  statusBreakdown: Record<string, number>;
  totalAmount?: number;
  highestPayment?: number;
  byMethod?: Array<{ method: string; count: number }>;
  byStatus?: Array<{ status: string; count: number }>;
  topCustomers?: Array<{
    name: string;
    paymentCount: number;
    totalAmount: number;
  }>;
}

export interface RefundReport {
  totalRefunds: number;
  successfulRefunds: number;
  failedRefunds: number;
  pendingRefunds: number;
  successRate: number;
  totalRefundedAmount: number;
  statusBreakdown: Record<string, number>;
}

export interface OutstandingBalanceReport {
  totalOutstanding: number;
  customersWithBalance: number;
  customers: Array<{
    id: string;
    name: string;
    email: string;
    outstandingBalance: number;
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
      const { data } = await apiClient.get<{ data: any }>(
        "/financial-reports/payments",
        {
          params: {
            start_date: startDate,
            end_date: endDate,
            use_cache: true,
          },
        },
      );
      // Transform snake_case to camelCase
      const report = data.data;
      return {
        totalPayments: report.total_payments,
        successfulPayments: report.successful_payments,
        failedPayments: report.failed_payments,
        pendingPayments: report.pending_payments,
        cancelledPayments: report.cancelled_payments,
        successRate: report.success_rate,
        statusBreakdown: report.status_breakdown,
        totalAmount: report.total_amount,
        highestPayment: report.highest_payment,
        byMethod: report.by_method,
        byStatus: report.by_status,
        topCustomers: report.top_customers?.map((c: any) => ({
          name: c.name,
          paymentCount: c.payment_count,
          totalAmount: c.total_amount,
        })),
      } as PaymentReport;
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
