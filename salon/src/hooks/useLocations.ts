import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface Location {
  id: string;
  name: string;
  address?: string;
  phone?: string;
  email?: string;
  isActive: boolean;
  timezone?: string;
  createdAt?: string;
  updatedAt?: string;
}

export interface LocationCreateInput {
  name: string;
  address?: string;
  phone?: string;
  email?: string;
  isActive?: boolean;
  timezone?: string;
}

export interface LocationUpdateInput {
  name?: string;
  address?: string;
  phone?: string;
  email?: string;
  isActive?: boolean;
  timezone?: string;
}

export function useLocations(filters?: { isActive?: boolean }) {
  return useQuery({
    queryKey: ["locations", filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters?.isActive !== undefined) {
        params.append("is_active", String(filters.isActive));
      }
      const { data } = await apiClient.get<{
        locations: Location[];
        total: number;
        page: number;
        page_size: number;
      }>(`/locations?${params.toString()}`);
      return data.locations || [];
    },
  });
}

export function useLocation(id: string) {
  return useQuery({
    queryKey: ["locations", id],
    queryFn: async () => {
      const { data } = await apiClient.get<Location>(`/locations/${id}`);
      return data;
    },
    enabled: !!id,
  });
}

export function useCreateLocation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (input: LocationCreateInput) => {
      const { data } = await apiClient.post<any>("/locations", input);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["locations"] });
    },
  });
}

export function useUpdateLocation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, input }: { id: string; input: LocationUpdateInput }) => {
      const { data } = await apiClient.put<any>(`/locations/${id}`, input);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["locations"] });
    },
  });
}

export function useDeleteLocation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await apiClient.delete<any>(`/locations/${id}`);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["locations"] });
    },
  });
}
