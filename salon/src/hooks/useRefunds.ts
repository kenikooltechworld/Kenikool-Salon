import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface Refund {
  id: string;
  payment_id: string;
  amount: number;
  reason: string;
  status: "pending" | "success" | "failed";
  reference: string;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface RefundListResponse {
  total: number;
  page: number;
  page_size: number;
  refunds: Refund[];
}

interface RefundFilters {
  payment_id?: string;
  status?: "pending" | "success" | "failed";
  skip?: number;
  limit?: number;
}

/**
 * Fetch all refunds with optional filters
 */
export function useRefunds(filters?: RefundFilters) {
  return useQuery({
    queryKey: ["refunds", filters],
    queryFn: async () => {
      const { data } = await apiClient.get<RefundListResponse>(
        "/payments/refunds",
        {
          params: {
            payment_id: filters?.payment_id,
            status: filters?.status,
            skip: filters?.skip || 0,
            limit: filters?.limit || 10,
          },
        },
      );
      return data.refunds;
    },
  });
}

/**
 * Fetch single refund by ID
 */
export function useRefund(id: string) {
  return useQuery({
    queryKey: ["refunds", id],
    queryFn: async () => {
      const { data } = await apiClient.get<Refund>(`/payments/refunds/${id}`);
      return data;
    },
    enabled: !!id,
  });
}

/**
 * Create refund for a payment
 */
export function useCreateRefund() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      paymentId,
      amount,
      reason,
    }: {
      paymentId: string;
      amount: number;
      reason: string;
    }) => {
      const { data } = await apiClient.post<Refund>(
        `/payments/${paymentId}/refund`,
        {
          amount,
          reason,
        },
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["refunds"] });
      queryClient.invalidateQueries({ queryKey: ["payments"] });
    },
  });
}
