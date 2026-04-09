import { useQuery, useMutation } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";
import type {
  GroupBooking,
  CreateGroupBookingData,
  GroupBookingParticipant,
} from "./useGroupBookings";

export function usePublicGroupBooking(bookingId: string | null, email: string) {
  return useQuery({
    queryKey: ["public-group-booking", bookingId, email],
    queryFn: async () => {
      if (!bookingId || !email) return null;
      const { data } = await apiClient.get<GroupBooking>(
        `/public/group-bookings/${bookingId}?email=${encodeURIComponent(email)}`,
      );
      return data;
    },
    enabled: !!bookingId && !!email,
  });
}

export function useGroupBookingById(bookingId: string) {
  return useQuery({
    queryKey: ["group-booking-by-id", bookingId],
    queryFn: async () => {
      const { data } = await apiClient.get<GroupBooking>(
        `/public/group-bookings/${bookingId}`,
      );
      return data;
    },
    enabled: !!bookingId,
  });
}

export function useCreatePublicGroupBooking() {
  return useMutation({
    mutationFn: async (bookingData: CreateGroupBookingData) => {
      const { data } = await apiClient.post<GroupBooking>(
        "/public/group-bookings",
        bookingData,
      );
      return data;
    },
  });
}

export function useCancelPublicGroupBooking() {
  return useMutation({
    mutationFn: async ({
      bookingId,
      email,
      cancellationReason,
    }: {
      bookingId: string;
      email: string;
      cancellationReason?: string;
    }) => {
      const { data } = await apiClient.post(
        `/public/group-bookings/${bookingId}/cancel`,
        {
          email,
          cancellation_reason: cancellationReason,
        },
      );
      return data;
    },
  });
}

// Re-export types for convenience
export type { GroupBookingParticipant };
