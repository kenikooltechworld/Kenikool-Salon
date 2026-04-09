import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";
import { useAuthStore } from "@/stores/auth";
import type { Appointment } from "./useAppointments";

export interface StaffAppointment {
  id: string;
  customerId: string;
  customerName: string;
  customerPhone: string;
  customerEmail: string;
  serviceId: string;
  serviceName: string;
  startTime: string;
  endTime: string;
  status: "scheduled" | "confirmed" | "in_progress" | "completed" | "cancelled";
  notes: string;
  price: number;
  createdAt: string;
}

interface MyAppointmentFilters {
  status?: string;
  startDate?: string;
  endDate?: string;
}

/**
 * Fetch current staff member's appointments with filtering and sorting
 * Automatically filters by staff_id from authenticated user
 */
export function useMyAppointments(filters?: MyAppointmentFilters) {
  const user = useAuthStore((state) => state.user);

  return useQuery({
    queryKey: ["my-appointments", filters],
    queryFn: async () => {
      const { data } = await apiClient.get<{ data: Appointment[] }>(
        "/appointments",
        {
          params: {
            staffId: user?.id,
            ...filters,
          },
        },
      );
      return data.data || [];
    },
    enabled: !!user?.id,
  });
}

/**
 * Fetch single appointment by ID (staff view)
 */
export function useMyAppointment(id: string) {
  const user = useAuthStore((state) => state.user);

  return useQuery({
    queryKey: ["my-appointments", id],
    queryFn: async () => {
      const { data } = await apiClient.get<{ data: Appointment }>(
        `/appointments/${id}`,
      );
      return data.data;
    },
    enabled: !!id && !!user?.id,
  });
}

/**
 * Mark appointment as completed
 */
export function useCompleteAppointment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await apiClient.put<{ data: Appointment }>(
        `/appointments/${id}/complete`,
        {},
      );
      return data.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["my-appointments"] });
      queryClient.invalidateQueries({ queryKey: ["my-appointments", data.id] });
    },
  });
}

/**
 * Cancel appointment
 */
export function useCancelAppointment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, reason }: { id: string; reason?: string }) => {
      const { data } = await apiClient.post<{ data: Appointment }>(
        `/appointments/${id}/cancel`,
        { reason },
      );
      return data.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["my-appointments"] });
      queryClient.invalidateQueries({ queryKey: ["my-appointments", data.id] });
    },
  });
}

/**
 * Reschedule appointment
 */
export function useRescheduleAppointment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      id,
      startTime,
      endTime,
    }: {
      id: string;
      startTime: string;
      endTime: string;
    }) => {
      const { data } = await apiClient.put<{ data: Appointment }>(
        `/appointments/${id}`,
        {
          start_time: startTime,
          end_time: endTime,
        },
      );
      return data.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["my-appointments"] });
      queryClient.invalidateQueries({ queryKey: ["my-appointments", data.id] });
    },
  });
}

/**
 * Update appointment notes
 */
export function useUpdateAppointmentNotes() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, notes }: { id: string; notes: string }) => {
      const { data } = await apiClient.put<{ data: Appointment }>(
        `/appointments/${id}`,
        { notes },
      );
      return data.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["my-appointments"] });
      queryClient.invalidateQueries({ queryKey: ["my-appointments", data.id] });
    },
  });
}
