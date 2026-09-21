import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";
import { useToast } from "@/components/ui/toast";

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
  const { showToast } = useToast();

  const query = useQuery({
    queryKey: ["pending-actions"],
    queryFn: async () => {
      const { data } = await apiClient.get<{
        success: boolean;
        data: { actions: PendingAction[]; total: number };
        error: any;
      }>("/owner/dashboard/pending-actions");
      const extracted = (Array.isArray(data?.data?.actions) ? data.data.actions : []) || [];
      console.log("[DashboardHook][usePendingActions] raw response:", data);
      console.log("[DashboardHook][usePendingActions] extracted count:", extracted.length);
      return extracted;
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
    onMutate: async (actionId: string) => {
      await queryClient.cancelQueries({ queryKey: ["pending-actions"] });
      const previousActions = queryClient.getQueryData(["pending-actions"]);

      queryClient.setQueryData(["pending-actions"], (old: PendingAction[] = []) =>
        old.filter((action) => action.id !== actionId),
      );

      return { previousActions };
    },
    onSuccess: () => {
      showToast({
        variant: "success",
        title: "Action Completed",
        description: "The pending action has been marked as complete.",
      });
      queryClient.invalidateQueries({ queryKey: ["pending-actions"] });
    },
    onError: (error: any, _actionId, context) => {
      const message = error?.response?.data?.detail || error?.message || "Failed to mark action as complete";
      showToast({
        variant: "error",
        title: "Action Failed",
        description: message,
      });

      if (context?.previousActions) {
        queryClient.setQueryData(["pending-actions"], context.previousActions);
      }
    },
  });

  const dismissMutation = useMutation({
    mutationFn: async (actionId: string) => {
      await apiClient.post(
        `/owner/dashboard/pending-actions/${actionId}/dismiss`,
      );
    },
    onMutate: async (actionId: string) => {
      await queryClient.cancelQueries({ queryKey: ["pending-actions"] });
      const previousActions = queryClient.getQueryData(["pending-actions"]);

      queryClient.setQueryData(["pending-actions"], (old: PendingAction[] = []) =>
        old.filter((action) => action.id !== actionId),
      );

      return { previousActions };
    },
    onSuccess: () => {
      showToast({
        variant: "success",
        title: "Action Dismissed",
        description: "The pending action has been dismissed.",
      });
      queryClient.invalidateQueries({ queryKey: ["pending-actions"] });
    },
    onError: (error: any, _actionId, context) => {
      const message = error?.response?.data?.detail || error?.message || "Failed to dismiss action";
      showToast({
        variant: "error",
        title: "Action Failed",
        description: message,
      });

      if (context?.previousActions) {
        queryClient.setQueryData(["pending-actions"], context.previousActions);
      }
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
