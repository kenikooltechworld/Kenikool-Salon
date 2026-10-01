import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils";
import type { CreateBookingInput, BookingFilters } from "@/types";

export interface Appointment {
  id: string;
  customerId: string;
  staffId: string;
  serviceId: string;
  locationId: string;
  startTime: string;
  endTime: string;
  status:
    | "scheduled"
    | "confirmed"
    | "in_progress"
    | "completed"
    | "cancelled"
    | "no_show";
  notes?: string;
  price?: number;
  paymentOption?: "now" | "later";
  paymentStatus?: "pending" | "completed" | "failed";
  cancellationReason?: string;
  cancelledAt?: string;
  cancelledBy?: string;
  noShowReason?: string;
  markedNoShowAt?: string;
  confirmedAt?: string;
  createdAt: string;
  updatedAt: string;
}

export interface AppointmentFilters {
  status?: string;
  customerId?: string;
  staffId?: string;
  serviceId?: string;
  startDate?: string;
  endDate?: string;
  search?: string;
  page?: number;
  limit?: number;
}

const APPOINTMENTS_QUERY_KEY = "appointments";

function transformAppointment(appt: any): Appointment {
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
}

/**
 * Fetch all appointments with optional filters
 */
export function useAppointments(filters?: AppointmentFilters) {
  return useQuery({
    queryKey: [APPOINTMENTS_QUERY_KEY, filters],
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

      return (data?.appointments || []).map(transformAppointment);
    },
    staleTime: 5 * 60 * 1000,
    refetchOnMount: true,
  });
}

/**
 * Alias for useAppointments - kept for backward compatibility
 */
export function useBookings(filters?: BookingFilters) {
  return useAppointments(filters);
}

/**
 * Fetch single appointment by ID
 */
export function useAppointment(id: string, options?: { refetchOnMount?: boolean }) {
  return useQuery({
    queryKey: [APPOINTMENTS_QUERY_KEY, id],
    queryFn: async () => {
      const { data } = await apiClient.get<any>(`/appointments/${id}`);
      return transformAppointment(data);
    },
    ...options,
    enabled: !!id,
  });
}

/**
 * Alias for useAppointment - kept for backward compatibility
 */
export function useBooking(id: string, options?: { refetchOnMount?: boolean }) {
  return useAppointment(id, options);
}

/**
 * Create new appointment
 */
export function useCreateAppointment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (input: CreateBookingInput) => {
      const { data } = await apiClient.post<any>("/appointments", input);
      return transformAppointment(data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [APPOINTMENTS_QUERY_KEY], exact: false });
      queryClient.invalidateQueries({ queryKey: ["calendar"], exact: false });
      queryClient.invalidateQueries({ queryKey: ["resources"] });
    },
  });
}

/**
 * Alias for useCreateAppointment - kept for backward compatibility
 */
export function useBookingDetail(id: string) {
  return useQuery({
    queryKey: ["bookingDetail", id],
    queryFn: async () => {
      const response = await apiClient.get(`/appointments/${id}/detail`);
      return response.data;
    },
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });
}

export function useCreateBooking() {
  return useCreateAppointment();
}

/**
 * Confirm appointment
 */
export function useConfirmAppointment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await apiClient.post<any>(
        `/appointments/${id}/confirm`,
        {},
      );
      return transformAppointment(data);
    },
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: [APPOINTMENTS_QUERY_KEY], exact: false });
      queryClient.invalidateQueries({ queryKey: [APPOINTMENTS_QUERY_KEY, id] });
      queryClient.invalidateQueries({ queryKey: ["bookingDetail", id] });
      queryClient.invalidateQueries({ queryKey: ["calendar"], exact: false });
      queryClient.invalidateQueries({ queryKey: ["resources"] });
    },
  });
}

/**
 * Alias for useConfirmAppointment - kept for backward compatibility
 */
export function useConfirmBooking() {
  return useConfirmAppointment();
}

/**
 * Cancel appointment
 */
export function useCancelAppointment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, reason }: { id: string; reason?: string }) => {
      const { data } = await apiClient.post<any>(`/appointments/${id}/cancel`, {
        reason,
      });
      return transformAppointment(data);
    },
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: [APPOINTMENTS_QUERY_KEY], exact: false });
      queryClient.invalidateQueries({ queryKey: [APPOINTMENTS_QUERY_KEY, id] });
      queryClient.invalidateQueries({ queryKey: ["bookingDetail", id] });
      queryClient.invalidateQueries({ queryKey: ["calendar"], exact: false });
    },
  });
}

/**
 * Alias for useCancelAppointment - kept for backward compatibility
 */
export function useCancelBooking() {
  return useCancelAppointment();
}

/**
 * Mark appointment as completed
 */
export function useCompleteAppointment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await apiClient.post<any>(
        `/appointments/${id}/complete`,
      );
      return transformAppointment(data);
    },
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: [APPOINTMENTS_QUERY_KEY], exact: false });
      queryClient.invalidateQueries({ queryKey: [APPOINTMENTS_QUERY_KEY, id] });
      queryClient.invalidateQueries({ queryKey: ["bookingDetail", id] });
      queryClient.invalidateQueries({ queryKey: ["calendar"], exact: false });
      queryClient.invalidateQueries({ queryKey: ["resources"] });
    },
  });
}

/**
 * Alias for useCompleteAppointment - kept for backward compatibility
 */
export function useCompleteBooking() {
  return useCompleteAppointment();
}

/**
 * Collect payment for appointment
 */
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
      return transformAppointment(data);
    },
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: [APPOINTMENTS_QUERY_KEY], exact: false });
      queryClient.invalidateQueries({ queryKey: [APPOINTMENTS_QUERY_KEY, id] });
      queryClient.invalidateQueries({ queryKey: ["bookingDetail", id] });
      queryClient.invalidateQueries({ queryKey: ["calendar"], exact: false });
      queryClient.invalidateQueries({ queryKey: ["transactions"], exact: false });
      queryClient.invalidateQueries({ queryKey: ["resources"] });
    },
  });
}

/**
 * Mark appointment as no-show
 */
export function useMarkNoShow() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, reason }: { id: string; reason?: string }) => {
      const { data } = await apiClient.post<any>(
        `/appointments/${id}/no-show`,
        { reason },
      );
      return transformAppointment(data);
    },
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: [APPOINTMENTS_QUERY_KEY], exact: false });
      queryClient.invalidateQueries({ queryKey: [APPOINTMENTS_QUERY_KEY, id] });
      queryClient.invalidateQueries({ queryKey: ["bookingDetail", id] });
      queryClient.invalidateQueries({ queryKey: ["calendar"], exact: false });
      queryClient.invalidateQueries({ queryKey: ["resources"] });
    },
  });
}

/**
 * Update appointment
 */
export function useUpdateAppointment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      id,
      ...updates
    }: Partial<Appointment> & { id: string }) => {
      const { data } = await apiClient.put<{ data: Appointment }>(
        `/appointments/${id}`,
        updates,
      );
      return data.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: [APPOINTMENTS_QUERY_KEY], exact: false });
      queryClient.invalidateQueries({ queryKey: [APPOINTMENTS_QUERY_KEY, data.id] });
      queryClient.invalidateQueries({ queryKey: ["resources"] });
    },
  });
}

/**
 * Alias for useUpdateAppointment - kept for backward compatibility
 */
export function useUpdateBooking() {
  return useUpdateAppointment();
}

/**
 * Delete appointment
 */
export function useDeleteAppointment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/appointments/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [APPOINTMENTS_QUERY_KEY], exact: false });
      queryClient.invalidateQueries({ queryKey: ["resources"] });
    },
  });
}

/**
 * Alias for useDeleteAppointment - kept for backward compatibility
 */
export function useDeleteBooking() {
  return useDeleteAppointment();
}

/**
 * Fetch available time slots
 */
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

/**
 * Fetch calendar view (day/week/month)
 */
export function useCalendarView(view: "day" | "week" | "month", date: string) {
  return useQuery({
    queryKey: ["calendar", view, date],
    queryFn: async () => {
      let appointments: Appointment[] = [];

      try {
        if (view === "day") {
          const response = await apiClient.get<any>(
            `/appointments/day/${date}`,
          );
          const data = response.data || response;
          appointments = (data.appointments || []).map(transformAppointment);
        } else if (view === "week") {
          const response = await apiClient.get<any>(
            `/appointments/week/${date}`,
          );
          const data = response.data || response;
          appointments = (data.appointments || []).map(transformAppointment);
        } else {
          const response = await apiClient.get<any>(
            `/appointments/month/${date}`,
          );
          const data = response.data || response;
          appointments = (data.appointments || []).map(transformAppointment);
        }
      } catch (error) {
        console.error(`Error fetching ${view} view for date ${date}:`, error);
        throw error;
      }

      return appointments;
    },
    staleTime: 5 * 60 * 1000,
  });
}
