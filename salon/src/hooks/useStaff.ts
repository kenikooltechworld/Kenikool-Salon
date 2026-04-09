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
    queryKey: ["staff", filters],
    queryFn: async () => {
      const response = await get<{
        staff: Staff[];
        total: number;
        page: number;
        page_size: number;
      }>("/staff", {
        params: filters,
      });
      // get() helper returns response.data which contains { staff: [...], total, page, page_size }
      return response.staff || [];
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
      const response = await get<Staff>(`/staff/${id}`);
      // get() helper returns response.data which is the staff object
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
      // post() helper returns response.data which is the staff object
      return response;
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
      const response = await put<Staff>(`/staff/${id}`, updates);
      // put() helper returns response.data which is the staff object
      return response;
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
      await del(`/staff/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["staff"] });
    },
  });
}
