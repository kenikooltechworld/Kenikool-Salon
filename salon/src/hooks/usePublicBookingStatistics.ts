import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface BookingStatistics {
  total_bookings: number;
  average_rating: number;
  average_response_time: number;
}

export function usePublicBookingStatistics() {
  return useQuery({
    queryKey: ["public-booking-statistics"],
    queryFn: async () => {
      const { data } = await apiClient.get<BookingStatistics>(
        "/public/bookings/statistics",
      );
      return data;
    },
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}
