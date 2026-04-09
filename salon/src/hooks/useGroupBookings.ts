import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface GroupBookingParticipant {
  name: string;
  email?: string;
  phone?: string;
  service_id: string;
  staff_id?: string;
  appointment_id?: string;
  status?: string;
  notes?: string;
}

export interface GroupBooking {
  id: string;
  tenant_id: string;
  group_name: string;
  group_type: string;
  organizer_name: string;
  organizer_email: string;
  organizer_phone: string;
  booking_date: string;
  participants: GroupBookingParticipant[];
  total_participants: number;
  base_total: number;
  discount_percentage: number;
  discount_amount: number;
  final_total: number;
  payment_option: string;
  payment_status: string;
  amount_paid: number;
  status: string;
  special_requests?: string;
  internal_notes?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateGroupBookingData {
  group_name: string;
  group_type: string;
  organizer_name: string;
  organizer_email: string;
  organizer_phone: string;
  booking_date: string;
  participants: GroupBookingParticipant[];
  payment_option?: string;
  special_requests?: string;
}

export interface UpdateGroupBookingData {
  group_name?: string;
  booking_date?: string;
  status?: string;
  payment_status?: string;
  special_requests?: string;
  internal_notes?: string;
}

export function useGroupBookings(filters?: {
  status?: string;
  start_date?: string;
  end_date?: string;
  skip?: number;
  limit?: number;
}) {
  return useQuery({
    queryKey: ["group-bookings", filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters?.status) params.append("status", filters.status);
      if (filters?.start_date) params.append("start_date", filters.start_date);
      if (filters?.end_date) params.append("end_date", filters.end_date);
      if (filters?.skip) params.append("skip", filters.skip.toString());
      if (filters?.limit) params.append("limit", filters.limit.toString());

      const { data } = await apiClient.get<GroupBooking[]>(
        `/group-bookings?${params.toString()}`,
      );
      return data;
    },
  });
}

export function useGroupBooking(bookingId: string | null) {
  return useQuery({
    queryKey: ["group-booking", bookingId],
    queryFn: async () => {
      if (!bookingId) return null;
      const { data } = await apiClient.get<GroupBooking>(
        `/group-bookings/${bookingId}`,
      );
      return data;
    },
    enabled: !!bookingId,
  });
}

export function useCreateGroupBooking() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (bookingData: CreateGroupBookingData) => {
      const { data } = await apiClient.post<GroupBooking>(
        "/group-bookings",
        bookingData,
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["group-bookings"] });
    },
  });
}

export function useUpdateGroupBooking() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      bookingId,
      updateData,
    }: {
      bookingId: string;
      updateData: UpdateGroupBookingData;
    }) => {
      const { data } = await apiClient.put<GroupBooking>(
        `/group-bookings/${bookingId}`,
        updateData,
      );
      return data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["group-bookings"] });
      queryClient.invalidateQueries({
        queryKey: ["group-booking", variables.bookingId],
      });
    },
  });
}

export function useConfirmGroupBooking() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (bookingId: string) => {
      const { data } = await apiClient.post<GroupBooking>(
        `/group-bookings/${bookingId}/confirm`,
      );
      return data;
    },
    onSuccess: (_, bookingId) => {
      queryClient.invalidateQueries({ queryKey: ["group-bookings"] });
      queryClient.invalidateQueries({ queryKey: ["group-booking", bookingId] });
      queryClient.invalidateQueries({ queryKey: ["appointments"] });
    },
  });
}

export function useCancelGroupBooking() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      bookingId,
      cancellationReason,
    }: {
      bookingId: string;
      cancellationReason?: string;
    }) => {
      const { data } = await apiClient.post<GroupBooking>(
        `/group-bookings/${bookingId}/cancel`,
        { cancellation_reason: cancellationReason },
      );
      return data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["group-bookings"] });
      queryClient.invalidateQueries({
        queryKey: ["group-booking", variables.bookingId],
      });
      queryClient.invalidateQueries({ queryKey: ["appointments"] });
    },
  });
}
