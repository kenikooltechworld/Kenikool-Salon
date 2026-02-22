import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";
import type { Staff } from "@/types/staff";

export interface StaffFilters {
  status?: string;
  specialty?: string;
  page?: number;
  page_size?: number;
}

/**
 * Fetch all staff with optional filters
 */
export function useStaff(filters?: StaffFilters) {
  return useQuery({
    queryKey: ["staff", filters],
    queryFn: async () => {
      const response = await apiClient.get<{
        staff: Staff[];
        total: number;
        page: number;
        page_size: number;
      }>("/staff", {
        params: filters,
      });
      return (response as any).data?.staff || [];
    },
  });
}

/**
 * Fetch single staff member by ID
 */
export function useStaffMember(id: string) {
  return useQuery({
    queryKey: ["staff", id],
    queryFn: async () => {
      const response = await apiClient.get<Staff>(`/staff/${id}`);
      return (response as any).data || null;
    },
    enabled: !!id,
  });
}

/**
 * Create new staff member
 */
export function useCreateStaff() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (
      staff: Omit<Staff, "id" | "createdAt" | "updatedAt">,
    ) => {
      const response = await apiClient.post<Staff>("/staff", staff);
      return (response as any).data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["staff"] });
    },
  });
}

/**
 * Update staff member
 */
export function useUpdateStaff() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, ...updates }: Partial<Staff> & { id: string }) => {
      const response = await apiClient.put<Staff>(`/staff/${id}`, updates);
      return (response as any).data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["staff"] });
      queryClient.invalidateQueries({
        queryKey: ["staff", (data as any).id],
      });
    },
  });
}

/**
 * Delete staff member
 */
export function useDeleteStaff() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/staff/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["staff"] });
    },
  });
}
