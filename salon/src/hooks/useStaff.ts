import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { get, post, put, del } from "@/lib/utils/api";
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
    queryKey: ["staff", "list", filters || {}],
    queryFn: async () => {
      const response = await get<{
        staff: Staff[];
        total: number;
        page: number;
        page_size: number;
      }>("/staff", {
        params: filters,
      });
      return response.staff || [];
    },
  });
}

/**
 * Fetch single staff member by ID
 */
export function useStaffMember(id: string) {
  return useQuery({
    queryKey: ["staff", "detail", id],
    queryFn: async () => {
      const response = await get<Staff>(`/staff/${id}`);
      return response || null;
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
      const response = await post<Staff>("/staff", staff);
      return response;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["staff", "list"] });
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
      const response = await put<Staff>(`/staff/${id}`, updates);
      return response;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["staff", "list"] });
      queryClient.invalidateQueries({
        queryKey: ["staff", "detail", (data as any).id],
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
      await del(`/staff/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["staff", "list"] });
    },
  });
}
