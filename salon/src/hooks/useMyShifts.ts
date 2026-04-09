import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";
import { useAuthStore } from "@/stores/auth";
import type { Shift } from "./useShifts";

interface MyShiftFilters {
  status?: string;
  startDate?: string;
  endDate?: string;
}

/**
 * Fetch current staff member's shifts with filtering and sorting
 * Automatically filters by staff_id from authenticated user
 */
export function useMyShifts(filters?: MyShiftFilters) {
  const user = useAuthStore((state) => state.user);

  return useQuery({
    queryKey: ["my-shifts", filters],
    queryFn: async () => {
      const { data } = await apiClient.get<Shift[]>("/shifts", {
        params: {
          staff_id: user?.id,
          ...filters,
        },
      });
      return Array.isArray(data) ? data : [];
    },
    enabled: !!user?.id,
  });
}

/**
 * Fetch single shift by ID (staff view)
 */
export function useMyShift(id: string) {
  const user = useAuthStore((state) => state.user);

  return useQuery({
    queryKey: ["my-shifts", id],
    queryFn: async () => {
      const { data } = await apiClient.get<Shift>(`/shifts/${id}`);
      return data || null;
    },
    enabled: !!id && !!user?.id,
  });
}

/**
 * Update shift (staff view)
 */
export function useUpdateMyShift() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, ...updates }: Partial<Shift> & { id: string }) => {
      const { data } = await apiClient.put<Shift>(`/shifts/${id}`, updates);
      return data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["my-shifts"] });
      queryClient.invalidateQueries({ queryKey: ["my-shifts", data.id] });
    },
  });
}
