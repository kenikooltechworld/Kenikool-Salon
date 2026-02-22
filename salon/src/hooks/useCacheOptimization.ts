import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface CacheStatistics {
  total_keys: number;
  key_types: Record<string, number>;
  hits: number;
  misses: number;
  hit_rate: number;
}

export const useCacheOptimization = () => {
  const queryClient = useQueryClient();

  // Get cache statistics
  const { data: cacheStats, isLoading: isLoadingStats } = useQuery({
    queryKey: ["cache", "statistics"],
    queryFn: async () => {
      const response = await apiClient.get("/cache/statistics");
      return response.data;
    },
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  // Warm cache
  const warmCacheMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.post("/cache/warm");
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cache"] });
    },
  });

  // Clear cache
  const clearCacheMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.post("/cache/clear");
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cache"] });
      // Invalidate all queries to refresh data
      queryClient.invalidateQueries();
    },
  });

  // Invalidate specific cache
  const invalidateCacheMutation = useMutation({
    mutationFn: async (cacheType: string) => {
      const response = await apiClient.post(`/cache/invalidate/${cacheType}`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cache"] });
    },
  });

  return {
    // Queries
    cacheStats,
    isLoadingStats,

    // Mutations
    warmCache: warmCacheMutation.mutate,
    isWarmingCache: warmCacheMutation.isPending,
    clearCache: clearCacheMutation.mutate,
    isClearingCache: clearCacheMutation.isPending,
    invalidateCache: invalidateCacheMutation.mutate,
    isInvalidatingCache: invalidateCacheMutation.isPending,
  };
};
