import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface ServiceCommission {
  id: string;
  staffId: string;
  appointmentId: string;
  serviceId: string;
  servicePrice: number;
  commissionPercentage: number;
  commissionAmount: number;
  status: "pending" | "paid";
  earnedDate: string;
  paidDate: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface CommissionSummary {
  totalEarned: number;
  totalPending: number;
  totalPaid: number;
  totalServices: number;
  averageCommission: number;
}

export interface ServiceBreakdown {
  serviceId: string;
  serviceName: string | null;
  totalCommission: number;
  count: number;
}

/**
 * Get staff commissions with filtering
 */
export function useServiceCommissions(
  staffId: string,
  filters?: {
    status?: "pending" | "paid";
    startDate?: string;
    endDate?: string;
    page?: number;
    pageSize?: number;
  },
) {
  return useQuery({
    queryKey: ["service-commissions", staffId, filters],
    queryFn: async () => {
      const response = await apiClient.get<{
        commissions: ServiceCommission[];
        total: number;
        page: number;
        pageSize: number;
      }>(`/service-commissions/staff/${staffId}`, { params: filters });
      return response.data;
    },
    enabled: !!staffId,
  });
}

/**
 * Get commission summary for a staff member
 */
export function useCommissionSummary(
  staffId: string,
  filters?: {
    startDate?: string;
    endDate?: string;
  },
) {
  return useQuery({
    queryKey: ["commission-summary", staffId, filters],
    queryFn: async () => {
      const response = await apiClient.get<{
        summary: CommissionSummary;
        breakdown: ServiceBreakdown[];
      }>(`/service-commissions/staff/${staffId}/summary`, { params: filters });
      return response.data;
    },
    enabled: !!staffId,
  });
}

/**
 * Get pending commissions for a staff member
 */
export function usePendingCommissions(staffId: string) {
  return useQuery({
    queryKey: ["pending-commissions", staffId],
    queryFn: async () => {
      const response = await apiClient.get<{
        commissions: ServiceCommission[];
        totalPending: number;
      }>(`/service-commissions/staff/${staffId}/pending`);
      return response.data;
    },
    enabled: !!staffId,
  });
}

/**
 * Mark a commission as paid
 */
export function useMarkCommissionAsPaid() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (commissionId: string) => {
      const response = await apiClient.patch(
        `/service-commissions/${commissionId}/mark-paid`,
        {},
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["service-commissions"] });
      queryClient.invalidateQueries({ queryKey: ["pending-commissions"] });
      queryClient.invalidateQueries({ queryKey: ["commission-summary"] });
    },
  });
}

/**
 * Mark multiple commissions as paid
 */
export function useMarkCommissionsAsPaidBatch() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      staffId,
      commissionIds,
    }: {
      staffId: string;
      commissionIds: string[];
    }) => {
      const response = await apiClient.post(
        `/service-commissions/staff/${staffId}/mark-paid-batch`,
        commissionIds,
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["service-commissions"] });
      queryClient.invalidateQueries({ queryKey: ["pending-commissions"] });
      queryClient.invalidateQueries({ queryKey: ["commission-summary"] });
    },
  });
}
