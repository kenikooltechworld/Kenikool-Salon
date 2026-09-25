import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils";
import type { CreateBookingInput, BookingFilters } from "@/types";

const BOOKINGS_QUERY_KEY = "bookings";

export function useBookings(filters?: BookingFilters) {
  return useQuery({
    queryKey: [BOOKINGS_QUERY_KEY, filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters?.status) params.append("status", filters.status);
      if (filters?.startDate) params.append("start_date", filters.startDate);
      if (filters?.endDate) params.append("end_date", filters.endDate);
      if (filters?.staffId) params.append("staff_id", filters.staffId);
      if (filters?.serviceId) params.append("service_id", filters.serviceId);
      if (filters?.customerId) params.append("customer_id", filters.customerId);
      if (filters?.search) params.append("search", filters.search);
      if (filters?.page) params.append("page", filters.page.toString());
      if (filters?.limit) params.append("limit", filters.limit.toString());

      const { data } = await apiClient.get<{ appointments: any[] }>(
        `/appointments?${params}`,
      );

      return (data.appointments || []).map((appt: any) => ({
        id: appt.id,
        customerId: appt.customer_id,
        staffId: appt.staff_id,
        serviceId: appt.service_id,
        locationId: appt.location_id,
        startTime: appt.start_time,
        endTime: appt.end_time,
        status: appt.status,
        notes: appt.notes,
        price: appt.price,
        paymentOption: appt.paymentOption,
        paymentStatus: appt.paymentStatus,
        cancellationReason: appt.cancellation_reason,
        cancelledAt: appt.cancelled_at,
        cancelledBy: appt.cancelled_by,
        noShowReason: appt.no_show_reason,
        markedNoShowAt: appt.marked_no_show_at,
        confirmedAt: appt.confirmed_at,
        createdAt: appt.created_at,
        updatedAt: appt.updated_at,
      }));
    },
    staleTime: 5 * 60 * 1000,
    refetchOnMount: true,
  });
}

export function useBooking(id: string, options?: { refetchOnMount?: boolean }) {
  return useQuery({
    queryKey: [BOOKINGS_QUERY_KEY, id],
    queryFn: async () => {
      const { data } = await apiClient.get<any>(`/appointments/${id}`);
      const appt = data;
      if (!appt) return null;
      console.log("[useBooking] raw appointment data:", appt);
      return {
        id: appt.id,
        customerId: appt.customer_id,
        staffId: appt.staff_id,
        serviceId: appt.service_id,
        locationId: appt.location_id,
        startTime: appt.start_time,
        endTime: appt.end_time,
        status: appt.status,
        notes: appt.notes,
        price: appt.price,
        paymentOption: appt.paymentOption,
        paymentStatus: appt.paymentStatus,
        cancellationReason: appt.cancellation_reason,
        cancelledAt: appt.cancelled_at,
        cancelledBy: appt.cancelled_by,
        noShowReason: appt.no_show_reason,
        markedNoShowAt: appt.marked_no_show_at,
        confirmedAt: appt.confirmed_at,
        createdAt: appt.created_at,
        updatedAt: appt.updated_at,
      };
    },
    ...options,
  });
}

export function useCreateBooking() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (input: CreateBookingInput) => {
      const { data } = await apiClient.post<any>("/appointments", input);
      const appt = data;

      // Transform snake_case from backend to camelCase for frontend
      return {
        id: appt.id,
        customerId: appt.customer_id,
        staffId: appt.staff_id,
        serviceId: appt.service_id,
        locationId: appt.location_id,
        startTime: appt.start_time,
        endTime: appt.end_time,
        status: appt.status,
        notes: appt.notes,
        price: appt.price,
        paymentOption: appt.paymentOption,
        paymentStatus: appt.paymentStatus,
        cancellationReason: appt.cancellation_reason,
        cancelledAt: appt.cancelled_at,
        cancelledBy: appt.cancelled_by,
        noShowReason: appt.no_show_reason,
        markedNoShowAt: appt.marked_no_show_at,
        confirmedAt: appt.confirmed_at,
        createdAt: appt.created_at,
        updatedAt: appt.updated_at,
      };
    },
    onSuccess: () => {
      queryClient.refetchQueries({ queryKey: [BOOKINGS_QUERY_KEY], exact: false });
      queryClient.refetchQueries({ queryKey: ["calendar"], exact: false });
    },
  });
}

export function useConfirmBooking() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await apiClient.post<any>(
        `/appointments/${id}/confirm`,
        {},
      );
      const appt = data;

      // Transform snake_case from backend to camelCase for frontend
      return {
        id: appt.id,
        customerId: appt.customer_id,
        staffId: appt.staff_id,
        serviceId: appt.service_id,
        locationId: appt.location_id,
        startTime: appt.start_time,
        endTime: appt.end_time,
        status: appt.status,
        notes: appt.notes,
        price: appt.price,
        paymentOption: appt.paymentOption,
        paymentStatus: appt.paymentStatus,
        cancellationReason: appt.cancellation_reason,
        cancelledAt: appt.cancelled_at,
        cancelledBy: appt.cancelled_by,
        noShowReason: appt.no_show_reason,
        markedNoShowAt: appt.marked_no_show_at,
        confirmedAt: appt.confirmed_at,
        createdAt: appt.created_at,
        updatedAt: appt.updated_at,
      };
    },
    onSuccess: (_, id) => {
      queryClient.refetchQueries({ queryKey: [BOOKINGS_QUERY_KEY], exact: false });
      queryClient.refetchQueries({ queryKey: [BOOKINGS_QUERY_KEY, id] });
      queryClient.refetchQueries({ queryKey: ["bookingDetail", id] });
      queryClient.refetchQueries({ queryKey: ["calendar"], exact: false });
    },
  });
}

export function useCancelBooking() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, reason }: { id: string; reason: string }) => {
      const { data } = await apiClient.post<any>(`/appointments/${id}/cancel`, {
        reason,
      });
      const appt = data;

      // Transform snake_case from backend to camelCase for frontend
      return {
        id: appt.id,
        customerId: appt.customer_id,
        staffId: appt.staff_id,
        serviceId: appt.service_id,
        locationId: appt.location_id,
        startTime: appt.start_time,
        endTime: appt.end_time,
        status: appt.status,
        notes: appt.notes,
        price: appt.price,
        paymentOption: appt.paymentOption,
        paymentStatus: appt.paymentStatus,
        cancellationReason: appt.cancellation_reason,
        cancelledAt: appt.cancelled_at,
        cancelledBy: appt.cancelled_by,
        noShowReason: appt.no_show_reason,
        markedNoShowAt: appt.marked_no_show_at,
        confirmedAt: appt.confirmed_at,
        createdAt: appt.created_at,
        updatedAt: appt.updated_at,
      };
    },
    onSuccess: (_, { id }) => {
      queryClient.refetchQueries({ queryKey: [BOOKINGS_QUERY_KEY], exact: false });
      queryClient.refetchQueries({ queryKey: [BOOKINGS_QUERY_KEY, id] });
      queryClient.refetchQueries({ queryKey: ["bookingDetail", id] });
      queryClient.refetchQueries({ queryKey: ["calendar"], exact: false });
    },
  });
}

export function useAvailableSlots(
  staffId: string,
  serviceId: string,
  date: string,
) {
  return useQuery({
    queryKey: ["availableSlots", staffId, serviceId, date],
    queryFn: async () => {
      const { data } = await apiClient.get(
        `/appointments/available-slots/${staffId}/${serviceId}?date=${date}`,
      );
      return data.data || [];
    },
    enabled: !!staffId && !!serviceId && !!date,
    staleTime: 5 * 60 * 1000,
  });
}

export function useCalendarView(view: "day" | "week" | "month", date: string) {
  return useQuery({
    queryKey: ["calendar", view, date],
    queryFn: async () => {
      let appointments: any[] = [];

      try {
        if (view === "day") {
          const response = await apiClient.get<any>(
            `/appointments/day/${date}`,
          );
          const data = response.data || response;
          appointments = data.appointments || [];
        } else if (view === "week") {
          const response = await apiClient.get<any>(
            `/appointments/week/${date}`,
          );
          const data = response.data || response;
          appointments = data.appointments || [];
        } else {
          const response = await apiClient.get<any>(
            `/appointments/month/${date}`,
          );
          const data = response.data || response;
          appointments = data.appointments || [];
        }
      } catch (error) {
        console.error(`Error fetching ${view} view for date ${date}:`, error);
        throw error;
      }

      return appointments.map((appt: any) => ({
        id: appt.id,
        customerId: appt.customer_id,
        staffId: appt.staff_id,
        serviceId: appt.service_id,
        locationId: appt.location_id,
        startTime: appt.start_time,
        endTime: appt.end_time,
        status: appt.status,
        notes: appt.notes,
        price: appt.price,
        cancellationReason: appt.cancellation_reason,
        cancelledAt: appt.cancelled_at,
        cancelledBy: appt.cancelled_by,
        noShowReason: appt.no_show_reason,
        markedNoShowAt: appt.marked_no_show_at,
        confirmedAt: appt.confirmed_at,
        createdAt: appt.created_at,
        updatedAt: appt.updated_at,
      }));
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useCompleteBooking() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await apiClient.post<any>(
        `/appointments/${id}/complete`,
      );
      const appt = data;
      console.log("[useCompleteBooking] raw complete response:", appt);

      // Transform snake_case from backend to camelCase for frontend
      return {
        id: appt.id,
        customerId: appt.customer_id,
        staffId: appt.staff_id,
        serviceId: appt.service_id,
        locationId: appt.location_id,
        startTime: appt.start_time,
        endTime: appt.end_time,
        status: appt.status,
        notes: appt.notes,
        price: appt.price,
        paymentOption: appt.paymentOption,
        paymentStatus: appt.paymentStatus,
        cancellationReason: appt.cancellation_reason,
        cancelledAt: appt.cancelled_at,
        cancelledBy: appt.cancelled_by,
        noShowReason: appt.no_show_reason,
        markedNoShowAt: appt.marked_no_show_at,
        confirmedAt: appt.confirmed_at,
        createdAt: appt.created_at,
        updatedAt: appt.updated_at,
      };
    },
    onSuccess: (_, id) => {
      console.log("[useCompleteBooking] success, refetching queries for id:", id);
      queryClient.refetchQueries({
        queryKey: [BOOKINGS_QUERY_KEY],
        exact: false,
      });
      queryClient.refetchQueries({ queryKey: [BOOKINGS_QUERY_KEY, id] });
      queryClient.refetchQueries({ queryKey: ["bookingDetail", id] });
      queryClient.refetchQueries({
        queryKey: ["calendar"],
        exact: false,
      });
      queryClient.refetchQueries({
        queryKey: ["calendar"],
        exact: false,
      });
    },
  });
}

export function useCollectPayment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      id,
      paymentMethod,
      amount,
      notes,
    }: {
      id: string;
      paymentMethod: string;
      amount: number;
      notes?: string;
    }) => {
      const { data } = await apiClient.post<any>(
        `/appointments/${id}/collect-payment`,
        {
          payment_method: paymentMethod,
          amount,
          notes,
        },
      );
      const appt = data;

      // Transform snake_case from backend to camelCase for frontend
      return {
        id: appt.id,
        customerId: appt.customer_id,
        staffId: appt.staff_id,
        serviceId: appt.service_id,
        locationId: appt.location_id,
        startTime: appt.start_time,
        endTime: appt.end_time,
        status: appt.status,
        notes: appt.notes,
        price: appt.price,
        paymentOption: appt.paymentOption,
        paymentStatus: appt.paymentStatus,
        cancellationReason: appt.cancellation_reason,
        cancelledAt: appt.cancelled_at,
        cancelledBy: appt.cancelled_by,
        noShowReason: appt.no_show_reason,
        markedNoShowAt: appt.marked_no_show_at,
        confirmedAt: appt.confirmed_at,
        createdAt: appt.created_at,
        updatedAt: appt.updated_at,
      };
    },
    onSuccess: (_, { id }) => {
      queryClient.refetchQueries({
        queryKey: [BOOKINGS_QUERY_KEY],
        exact: false,
      });
      queryClient.refetchQueries({ queryKey: [BOOKINGS_QUERY_KEY, id] });
      queryClient.refetchQueries({ queryKey: ["bookingDetail", id] });
      queryClient.refetchQueries({
        queryKey: ["calendar"],
        exact: false,
      });
      queryClient.refetchQueries({
        queryKey: ["transactions"],
        exact: false,
      });
    },
  });
}

export function useMarkNoShow() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, reason }: { id: string; reason?: string }) => {
      const { data } = await apiClient.post<any>(
        `/appointments/${id}/no-show`,
        { reason },
      );
      const appt = data;

      // Transform snake_case from backend to camelCase for frontend
      return {
        id: appt.id,
        customerId: appt.customer_id,
        staffId: appt.staff_id,
        serviceId: appt.service_id,
        locationId: appt.location_id,
        startTime: appt.start_time,
        endTime: appt.end_time,
        status: appt.status,
        notes: appt.notes,
        price: appt.price,
        paymentOption: appt.paymentOption,
        paymentStatus: appt.paymentStatus,
        cancellationReason: appt.cancellation_reason,
        cancelledAt: appt.cancelled_at,
        cancelledBy: appt.cancelled_by,
        noShowReason: appt.no_show_reason,
        markedNoShowAt: appt.marked_no_show_at,
        confirmedAt: appt.confirmed_at,
        createdAt: appt.created_at,
        updatedAt: appt.updated_at,
      };
    },
    onSuccess: (_, { id }) => {
      queryClient.refetchQueries({
        queryKey: [BOOKINGS_QUERY_KEY],
        exact: false,
      });
      queryClient.refetchQueries({ queryKey: [BOOKINGS_QUERY_KEY, id] });
      queryClient.refetchQueries({ queryKey: ["bookingDetail", id] });
      queryClient.refetchQueries({
        queryKey: ["calendar"],
        exact: false,
      });
    },
  });
}
