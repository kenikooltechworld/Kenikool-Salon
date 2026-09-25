import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

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
  cancellationReason?: string;
  cancelledAt?: string;
  createdAt: string;
  updatedAt: string;
}

interface AppointmentFilters {
  status?: string;
  customerId?: string;
  staffId?: string;
  startDate?: string;
  endDate?: string;
}

/**
 * Fetch all appointments with optional filters
 */
export function useAppointments(filters?: AppointmentFilters) {
  const queryKey = React.useMemo(() => {
    const normalizedFilters = filters || {};
    return ["appointments", normalizedFilters] as const;
  }, [filters]);

  return useQuery({
    queryKey,
    queryFn: async () => {
      const { data } = await apiClient.get<{ appointments: Appointment[] }>(
        "/appointments",
        { params: filters || {} },
      );
      return data.appointments;
    },
  });
}

/**
 * Fetch single appointment by ID
 */
export function useAppointment(id: string) {
  return useQuery({
    queryKey: ["appointments", id],
    queryFn: async () => {
      const { data } = await apiClient.get<{ appointment: Appointment }>(
        `/appointments/${id}`,
      );
      return data.appointment;
    },
    enabled: !!id,
  });
}

/**
 * Create new appointment
 */
export function useCreateAppointment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (
      appointment: Omit<Appointment, "id" | "createdAt" | "updatedAt">,
    ) => {
      const { data } = await apiClient.post<{ data: Appointment }>(
        "/appointments",
        appointment,
      );
      return data.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["appointments"] });
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
      queryClient.invalidateQueries({ queryKey: ["appointments"] });
      queryClient.invalidateQueries({ queryKey: ["appointments", data.id] });
    },
  });
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
      queryClient.invalidateQueries({ queryKey: ["appointments"] });
    },
  });
}
