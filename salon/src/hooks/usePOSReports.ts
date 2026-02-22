import { useQuery, useMutation } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface SalesReport {
  totalSales: number;
  totalTransactions: number;
  averageTransaction: number;
  period: {
    startDate?: string;
    endDate?: string;
  };
}

export interface RevenueReport {
  totalRevenue: number;
  totalTax: number;
  totalDiscount: number;
  netRevenue: number;
  period: {
    startDate?: string;
    endDate?: string;
  };
}

export interface InventoryReport {
  totalItems: number;
  lowStockItems: Array<{
    productId: string;
    quantityOnHand: number;
    reorderPoint: number;
  }>;
  lowStockCount: number;
}

export interface PaymentReport {
  paymentMethods: Record<
    string,
    {
      count: number;
      total: number;
    }
  >;
  totalTransactions: number;
  period: {
    startDate?: string;
    endDate?: string;
  };
}

/**
 * Get sales report
 */
export function useSalesReport(filters?: {
  startDate?: string;
  endDate?: string;
}) {
  return useQuery({
    queryKey: ["reports", "sales", filters],
    queryFn: async () => {
      const response = await apiClient.get<SalesReport>("/reports/sales", {
        params: filters,
      });
      return response.data;
    },
  });
}

/**
 * Get revenue report
 */
export function useRevenueReport(filters?: {
  startDate?: string;
  endDate?: string;
}) {
  return useQuery({
    queryKey: ["reports", "revenue", filters],
    queryFn: async () => {
      const response = await apiClient.get<RevenueReport>("/reports/revenue", {
        params: filters,
      });
      return response.data;
    },
  });
}

/**
 * Get inventory report
 */
export function useInventoryReport() {
  return useQuery({
    queryKey: ["reports", "inventory"],
    queryFn: async () => {
      const response =
        await apiClient.get<InventoryReport>("/reports/inventory");
      return response.data;
    },
  });
}

/**
 * Get payment report
 */
export function usePaymentReport(filters?: {
  startDate?: string;
  endDate?: string;
}) {
  return useQuery({
    queryKey: ["reports", "payments", filters],
    queryFn: async () => {
      const response = await apiClient.get<PaymentReport>("/reports/payments", {
        params: filters,
      });
      return response.data;
    },
  });
}

/**
 * Export report
 */
export function useExportReport() {
  return useMutation({
    mutationFn: async ({
      reportType,
      format,
    }: {
      reportType: "sales" | "revenue" | "inventory" | "payments";
      format: "pdf" | "csv" | "excel";
    }) => {
      const response = await apiClient.get("/reports/export", {
        params: { reportType, format },
        responseType: "blob",
      });
      return response.data;
    },
  });
}
