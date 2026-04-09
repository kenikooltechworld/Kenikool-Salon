import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface PendingAction {
  id: string;
  description: string;
  dueDate: string;
  priority: "high" | "medium" | "low";
  type: "payment" | "staff" | "inventory" | "customer" | "system";
  actionUrl?: string;
}

/**
 * Fetch pending actions requiring owner attention
 * Actions are sorted by priority (high, medium, low)
 * Maximum 10 displayed with total count
 * Auto-refreshes every 30 seconds
 */
export function usePendingActions() {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: ["pending-actions"],
    queryFn: async () => {
      const { data } = await apiClient.get<{ data: PendingAction[] }>(
        "/owner/dashboard/pending-actions",
      );
      // Return the array directly, not the response wrapper
      return (Array.isArray(data.data) ? data.data : data) || [];
    },
    refetchInterval: 30 * 1000, // 30 seconds
    staleTime: 30 * 1000, // 30 seconds
    retry: false, // Don't retry - fail fast
    placeholderData: (previousData) => previousData, // Keep old data while refetching
  });

  const markCompleteMutation = useMutation({
    mutationFn: async (actionId: string) => {
      await apiClient.post(
        `/owner/dashboard/pending-actions/${actionId}/complete`,
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pending-actions"] });
    },
  });

  const dismissMutation = useMutation({
    mutationFn: async (actionId: string) => {
      await apiClient.post(
        `/owner/dashboard/pending-actions/${actionId}/dismiss`,
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pending-actions"] });
    },
  });

  return {
    data: query.data || [],
    isLoading: query.isLoading,
    error: query.error,
    markComplete: markCompleteMutation.mutate,
    dismiss: dismissMutation.mutate,
    isMarkingComplete: markCompleteMutation.isPending,
    isDismissing: dismissMutation.isPending,
  };
}
