import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";
import { useAuthStore } from "@/stores/auth";

export interface PerformanceMetrics {
  averageRating: number;
  totalReviews: number;
  appointmentsCompleted: number;
  customerSatisfaction: number; // percentage
  totalEarnings?: number;
  topService?: string;
  ratingDistribution?: {
    "1": number;
    "2": number;
    "3": number;
    "4": number;
    "5": number;
  };
  recentReviews?: Array<{
    id: string;
    customerName: string;
    rating: number;
    feedback: string;
    date: string;
  }>;
}

export function usePerformanceMetrics() {
  const user = useAuthStore((state) => state.user);

  return useQuery({
    queryKey: ["performance-metrics"],
    queryFn: async () => {
      try {
        // In a real implementation, this would call an API endpoint
        // For now, we'll return mock data
        const mockData: PerformanceMetrics = {
          averageRating: 4.5,
          totalReviews: 42,
          appointmentsCompleted: 156,
          customerSatisfaction: 92,
          totalEarnings: 12540.75,
          topService: "Haircut & Style",
          ratingDistribution: {
            "1": 2,
            "2": 3,
            "3": 8,
            "4": 15,
            "5": 14,
          },
          recentReviews: [
            {
              id: "1",
              customerName: "John Doe",
              rating: 5,
              feedback: "Excellent service, very professional!",
              date: "2024-01-15",
            },
            {
              id: "2",
              customerName: "Jane Smith",
              rating: 4,
              feedback: "Good service, but had to wait a bit",
              date: "2024-01-14",
            },
          ],
        };
        return mockData;
      } catch (error) {
        console.error("Error fetching performance metrics:", error);
        throw error;
      }
    },
    enabled: !!user?.id,
    refetchOnWindowFocus: false,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function usePerformanceReviews() {
  const user = useAuthStore((state) => state.user);

  return useQuery({
    queryKey: ["performance-reviews"],
    queryFn: async () => {
      try {
        // In a real implementation, this would be an API call
        // For now, return mock data
        const mockReviews = [
          {
            id: "1",
            customerId: "cust1",
            customerName: "John Doe",
            appointmentId: "appt1",
            serviceName: "Haircut & Style",
            rating: 5,
            feedback: "Excellent service, very professional!",
            appointmentDate: "2024-01-15",
            createdAt: "2024-01-15T10:30:00Z",
          },
          {
            id: "2",
            customerId: "cust2",
            customerName: "Jane Smith",
            appointmentId: "appt2",
            serviceName: "Hair Coloring",
            rating: 4,
            feedback: "Good service, but had to wait a bit",
            appointmentDate: "2024-01-14",
            createdAt: "2024-01-14T14:20:00Z",
          },
          {
            id: "3",
            customerId: "cust3",
            customerName: "Bob Johnson",
            appointmentId: "appt3",
            serviceName: "Haircut",
            rating: 5,
            feedback: "Amazing work! Will definitely come back.",
            appointmentDate: "2024-01-13",
            createdAt: "2024-01-13T16:45:00Z",
          },
        ];
        return mockReviews;
      } catch (error) {
        console.error("Error fetching reviews:", error);
        throw error;
      }
    },
    enabled: !!user?.id,
  });
}
