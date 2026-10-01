import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useMemo } from "react";
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
  const filtersKey = useMemo(() => {
    if (!filters) return "{}";
    return JSON.stringify(filters);
  }, [filters]);

  return useQuery({
    queryKey: ["staff", "list", filtersKey],
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
    staleTime: 60 * 60 * 1000,
    gcTime: 24 * 60 * 60 * 1000,
    refetchOnMount: false,
    refetchOnWindowFocus: false,
    retry: false,
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
    staleTime: 60 * 60 * 1000,
    gcTime: 24 * 60 * 60 * 1000,
    refetchOnMount: false,
    refetchOnWindowFocus: false,
    retry: false,
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
      console.log("[StaffCreate] API request payload:", staff);
      const response = await post<Staff>("/staff", staff);
      console.log("[StaffCreate] API response:", response);
      return response;
    },
    onSuccess: (newStaff) => {
      queryClient.invalidateQueries({ queryKey: ["staff"], exact: false });
      queryClient.invalidateQueries({ queryKey: ["staff", "detail", newStaff.id] });
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
    onSuccess: (updatedStaff) => {
      queryClient.invalidateQueries({ queryKey: ["staff"], exact: false });
      queryClient.invalidateQueries({ queryKey: ["staff", "detail", updatedStaff.id] });
      queryClient.invalidateQueries({ queryKey: ["staff", "list"] });
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
    onSuccess: (_, deletedId) => {
      queryClient.invalidateQueries({ queryKey: ["staff"], exact: false });
      queryClient.invalidateQueries({ queryKey: ["staff", "detail", deletedId] });
      queryClient.invalidateQueries({ queryKey: ["staff", "list"] });
    },
  });
}
