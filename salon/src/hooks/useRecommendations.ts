import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface ServiceRecommendation {
  id: string;
  service_id: string;
  service_name: string;
  service_description: string;
  service_price: number;
  service_duration: number;
  service_image_url?: string;
  staff_id?: string;
  staff_name?: string;
  confidence_score: number;
  recommendation_type: string;
  reasoning: string;
}

export interface CustomerPreference {
  id: string;
  customer_id: string;
  preferred_service_categories: string[];
  preferred_services: string[];
  preferred_staff: string[];
  preferred_time_slots: string[];
  preferred_days: string[];
  average_booking_frequency_days?: number;
  average_spend?: number;
  last_booking_date?: string;
  total_bookings: number;
}

export function useRecommendations(limit: number = 5) {
  return useQuery({
    queryKey: ["recommendations", limit],
    queryFn: async () => {
      const { data } = await apiClient.get<ServiceRecommendation[]>(
        `/public/recommendations?limit=${limit}`,
      );
      return data;
    },
  });
}

export function useCustomerPreferences() {
  return useQuery({
    queryKey: ["customer-preferences"],
    queryFn: async () => {
      const { data } = await apiClient.get<CustomerPreference>(
        "/public/recommendations/preferences",
      );
      return data;
    },
  });
}

export function useRecommendationFeedback() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      recommendationId,
      action,
    }: {
      recommendationId: string;
      action: "clicked" | "booked" | "dismissed";
    }) => {
      const { data } = await apiClient.post(
        "/public/recommendations/feedback",
        {
          recommendation_id: recommendationId,
          action,
        },
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recommendations"] });
    },
  });
}
