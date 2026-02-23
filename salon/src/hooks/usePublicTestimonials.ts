import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface Testimonial {
  customer_name: string;
  rating: number;
  review: string;
  created_at: string;
}

export function usePublicTestimonials(limit: number = 5) {
  return useQuery({
    queryKey: ["public-testimonials", limit],
    queryFn: async () => {
      const { data } = await apiClient.get<Testimonial[]>(
        `/public/bookings/testimonials?limit=${limit}`,
      );
      return data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
