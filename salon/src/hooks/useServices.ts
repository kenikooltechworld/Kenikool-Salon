import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";
import type { Service, ServiceFilters } from "@/types/service";

/**
 * Fetch all services with optional filters
 */
export function useServices(filters?: ServiceFilters) {
  return useQuery({
    queryKey: ["services", filters],
    queryFn: async () => {
      const response = await apiClient.get<{
        services: Service[];
        total: number;
        page: number;
        page_size: number;
      }>("/services", {
        params: filters,
      });
      return (response as any).data?.services || [];
    },
  });
}

/**
 * Fetch single service by ID
 */
export function useService(id: string) {
  return useQuery({
    queryKey: ["services", id],
    queryFn: async () => {
      const response = await apiClient.get<Service>(`/services/${id}`);
      return (response as any).data || null;
    },
    enabled: !!id,
  });
}

/**
 * Create new service
 */
export function useCreateService() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (
      service: Omit<Service, "id" | "createdAt" | "updatedAt">,
    ) => {
      const response = await apiClient.post<Service>("/services", service);
      return (response as any).data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["services"] });
    },
  });
}

/**
 * Update service
 */
export function useUpdateService() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      id,
      ...updates
    }: Partial<Service> & { id: string }) => {
      const response = await apiClient.put<Service>(`/services/${id}`, updates);
      return (response as any).data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["services"] });
      queryClient.invalidateQueries({
        queryKey: ["services", (data as any).id],
      });
    },
  });
}

/**
 * Delete service
 */
export function useDeleteService() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/services/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["services"] });
    },
  });
}
