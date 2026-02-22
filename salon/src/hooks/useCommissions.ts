import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface Commission {
  id: string;
  staffId: string;
  transactionId: string;
  commissionAmount: number;
  commissionRate: number;
  commissionType: "percentage" | "fixed";
  calculatedAt: string;
}

export interface CommissionPayout {
  id: string;
  staffId: string;
  payoutAmount: number;
  period: string;
  payoutDate: string;
  status: "pending" | "processed" | "failed";
  createdAt: string;
}

/**
 * Get staff commissions
 */
export function useCommissions(
  staffId: string,
  filters?: {
    page?: number;
    pageSize?: number;
  },
) {
  return useQuery({
    queryKey: ["commissions", staffId, filters],
    queryFn: async () => {
      const response = await apiClient.get<{
        commissions: Commission[];
        total: number;
        page: number;
        pageSize: number;
      }>(`/commissions/staff/${staffId}`, { params: filters });
      return response.data;
    },
    enabled: !!staffId,
  });
}

/**
 * List commission payouts
 */
export function useCommissionPayouts(filters?: {
  staffId?: string;
  page?: number;
  pageSize?: number;
}) {
  return useQuery({
    queryKey: ["commission-payouts", filters],
    queryFn: async () => {
      const response = await apiClient.get<{
        payouts: CommissionPayout[];
        total: number;
        page: number;
        pageSize: number;
      }>("/commissions/payouts", { params: filters });
      return response.data;
    },
  });
}

/**
 * Create commission payout
 */
export function useCreateCommissionPayout() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      staffId,
      period,
    }: {
      staffId: string;
      period: string;
    }) => {
      const response = await apiClient.post<CommissionPayout>(
        "/commissions/payouts",
        {
          staff_id: staffId,
          period,
        },
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["commission-payouts"] });
    },
  });
}
