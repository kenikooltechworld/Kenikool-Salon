import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";
import { useAuthStore } from "@/stores/auth";

export interface PerformanceMetrics {
  averageRating: number;
  totalReviews: number;
  appointmentsCompleted: number;
  customerSatisfaction: number;
  totalEarnings?: number;
  topService?: string;
  ratingDistribution?: Record<string, number>;
  recentReviews?: Array<{
    id: string;
    customerId: string;
    customerName: string;
    appointmentId: string;
    serviceName: string;
    rating: number;
    feedback: string;
    appointmentDate: string;
    createdAt: string;
  }>;
}

export function usePerformanceMetrics() {
  const user = useAuthStore((state) => state.user);

  return useQuery({
    queryKey: ["performance-metrics", user?.id],
    queryFn: async () => {
      const { data } = await apiClient.get<PerformanceMetrics>(
        `/staff/${user?.id}/performance-metrics`,
      );
      if (data && !data.topService && data.recentReviews?.length) {
        const serviceCounts: Record<string, number> = {};
        data.recentReviews.forEach((r) => {
          if (r.serviceName) serviceCounts[r.serviceName] = (serviceCounts[r.serviceName] || 0) + 1;
        });
        const top = Object.entries(serviceCounts).sort((a, b) => b[1] - a[1])[0];
        if (top) data.topService = top[0];
      }
      return data || {
        averageRating: 0,
        totalReviews: 0,
        appointmentsCompleted: 0,
        customerSatisfaction: 0,
        ratingDistribution: { "1": 0, "2": 0, "3": 0, "4": 0, "5": 0 },
        recentReviews: [],
      } as PerformanceMetrics;
    },
    enabled: !!user?.id,
    refetchOnWindowFocus: false,
    staleTime: 5 * 60 * 1000,
  });
}

export function usePerformanceReviews(limit: number = 50) {
  const user = useAuthStore((state) => state.user);

  return useQuery({
    queryKey: ["performance-reviews", user?.id, limit],
    queryFn: async () => {
      const { data } = await apiClient.get<{ reviews: Array<{
        id: string;
        customerId: string;
        customerName: string;
        appointmentId: string;
        serviceName: string;
        rating: number;
        feedback: string;
        appointmentDate: string;
        createdAt: string;
      }> }>(`/staff/${user?.id}/reviews`, { params: { limit } });
      return (data?.reviews || []).map((r) => ({
        id: r.id,
        customerId: r.customerId,
        customerName: r.customerName,
        appointmentId: r.appointmentId,
        serviceName: r.serviceName,
        rating: r.rating,
        feedback: r.feedback,
        appointmentDate: r.appointmentDate,
        createdAt: r.createdAt,
      }));
    },
    enabled: !!user?.id,
    staleTime: 5 * 60 * 1000,
  });
}
