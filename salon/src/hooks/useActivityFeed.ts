import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";
import { useAuthStore } from "@/stores/auth";

export interface ActivityEvent {
  id: string;
  type: "appointment" | "shift" | "timeoff" | "earnings" | "review";
  title: string;
  description: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

/**
 * Fetch recent activity feed for current staff member
 * Returns last N events (default 10)
 * Auto-refreshes every 5 minutes
 * Implements exponential backoff retry strategy for failed requests
 */
export function useActivityFeed(limit: number = 10) {
  const user = useAuthStore((state) => state.user);

  return useQuery({
    queryKey: ["activity-feed", limit],
    queryFn: async () => {
      const { data } = await apiClient.get<ActivityEvent[]>(
        `/staff/${user?.id}/activity-feed`,
        {
          params: { limit },
        },
      );
      return Array.isArray(data) ? data : [];
    },
    enabled: !!user?.id,
    refetchInterval: 5 * 60 * 1000, // 5 minutes
    staleTime: 1 * 60 * 1000, // 1 minute
    retry: 3, // Retry up to 3 times
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000), // Exponential backoff: 1s, 2s, 4s
  });
}
