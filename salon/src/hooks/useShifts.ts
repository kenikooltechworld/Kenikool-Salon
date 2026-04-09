import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface Shift {
  id: string;
  staff_id: string;
  start_time: string;
  end_time: string;
  status: "scheduled" | "in_progress" | "completed" | "cancelled";
  labor_cost: number;
  created_at: string;
  updated_at: string;
}

interface ShiftFilters {
  staff_id?: string;
  status?: string;
}

interface CreateShiftData {
  staff_id: string;
  start_time: string;
  end_time: string;
  status?: "scheduled" | "in_progress" | "completed" | "cancelled";
}

/**
 * Fetch all shifts with optional filters
 */
export function useShifts(filters?: ShiftFilters) {
  return useQuery({
    queryKey: ["shifts", filters],
    queryFn: async () => {
      const { data } = await apiClient.get<Shift[]>("/shifts", {
        params: filters,
      });
      return Array.isArray(data) ? data : [];
    },
  });
}

/**
 * Fetch single shift by ID
 */
export function useShift(id: string) {
  return useQuery({
    queryKey: ["shifts", id],
    queryFn: async () => {
      const { data } = await apiClient.get<Shift>(`/shifts/${id}`);
      return data || null;
    },
    enabled: !!id,
  });
}

/**
 * Create new shift
 */
export function useCreateShift() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (shiftData: CreateShiftData) => {
      const { data } = await apiClient.post<Shift>("/shifts", shiftData);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["shifts"] });
    },
  });
}

/**
 * Update shift
 */
export function useUpdateShift() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, ...updates }: Partial<Shift> & { id: string }) => {
      const { data } = await apiClient.put<Shift>(`/shifts/${id}`, updates);
      return data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["shifts"] });
      queryClient.invalidateQueries({ queryKey: ["shifts", data.id] });
    },
  });
}

/**
 * Delete shift
 */
export function useDeleteShift() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/shifts/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["shifts"] });
    },
  });
}
