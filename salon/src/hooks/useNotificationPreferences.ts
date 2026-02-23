import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface NotificationPreferences {
  send_confirmation_email: boolean;
  send_24h_reminder_email: boolean;
  send_1h_reminder_email: boolean;
  send_sms_reminders: boolean;
}

export function useNotificationPreferences(bookingId: string | undefined) {
  return useQuery({
    queryKey: ["notification-preferences", bookingId],
    queryFn: async () => {
      if (!bookingId) throw new Error("Booking ID is required");
      const response = await apiClient.get(
        `/public/bookings/${bookingId}/notification-preferences`,
      );
      return response.data as NotificationPreferences;
    },
    enabled: !!bookingId,
  });
}

export function useUpdateNotificationPreferences() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      bookingId,
      preferences,
    }: {
      bookingId: string;
      preferences: NotificationPreferences;
    }) => {
      const response = await apiClient.post(
        `/public/bookings/${bookingId}/notification-preferences`,
        preferences,
      );
      return response.data;
    },
    onSuccess: (_, { bookingId }) => {
      queryClient.invalidateQueries({
        queryKey: ["notification-preferences", bookingId],
      });
    },
  });
}
