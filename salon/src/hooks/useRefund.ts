import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface Refund {
  id: string;
  originalTransactionId: string;
  refundAmount: number;
  refundReason: string;
  refundStatus: "pending" | "approved" | "completed" | "rejected";
  approvedBy?: string;
  approvedAt?: string;
  completedAt?: string;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

/**
 * Create refund request
 */
export function useCreateRefund() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: {
      originalTransactionId: string;
      refundAmount: number;
      refundReason: string;
      notes?: string;
    }) => {
      const response = await apiClient.post<Refund>("/pos/refunds", data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["refunds"] });
    },
  });
}

/**
 * Get refund by ID
 */
export function useRefund(refundId: string) {
  return useQuery({
    queryKey: ["refunds", refundId],
    queryFn: async () => {
      const response = await apiClient.get<Refund>(`/pos/refunds/${refundId}`);
      return response.data;
    },
    enabled: !!refundId,
  });
}

/**
 * List refunds
 */
export function useRefunds(filters?: {
  status?: string;
  page?: number;
  pageSize?: number;
}) {
  return useQuery({
    queryKey: ["refunds", filters],
    queryFn: async () => {
      const response = await apiClient.get<{
        refunds: Refund[];
        total: number;
        page: number;
        pageSize: number;
      }>("/pos/refunds", { params: filters });
      return response.data;
    },
  });
}

/**
 * Approve refund
 */
export function useApproveRefund() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (refundId: string) => {
      const response = await apiClient.put<Refund>(
        `/pos/refunds/${refundId}/approve`,
        {},
      );
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["refunds"] });
      queryClient.invalidateQueries({ queryKey: ["refunds", data.id] });
    },
  });
}

/**
 * Process refund
 */
export function useProcessRefund() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (refundId: string) => {
      const response = await apiClient.put<Refund>(
        `/pos/refunds/${refundId}/process`,
        {},
      );
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["refunds"] });
      queryClient.invalidateQueries({ queryKey: ["refunds", data.id] });
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
    },
  });
}

/**
 * Reverse refund
 */
export function useReverseRefund() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (refundId: string) => {
      const response = await apiClient.put<Refund>(
        `/pos/refunds/${refundId}/reverse`,
        {},
      );
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["refunds"] });
      queryClient.invalidateQueries({ queryKey: ["refunds", data.id] });
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
    },
  });
}
