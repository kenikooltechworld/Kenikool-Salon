import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { get, post, put, del } from "@/lib/utils/api";
import type { Service, ServiceFilters } from "@/types/service";

/**
 * Fetch all services with optional filters
 */
export function useServices(filters?: ServiceFilters) {
  return useQuery({
    queryKey: ["services", filters],
    queryFn: async () => {
      try {
        const response = await get<{
          services: Service[];
          total: number;
          page: number;
          page_size: number;
        }>("/services", {
          params: filters,
        });
        // get() helper returns response.data which contains { services: [...], total, page, page_size }
        return response.services || [];
      } catch (error) {
        console.error("Error fetching services:", error);
        return [];
      }
    },
    staleTime: 0, // Always refetch to ensure fresh data
  });
}

/**
 * Fetch single service by ID
 */
export function useService(id: string) {
  return useQuery({
    queryKey: ["services", id],
    queryFn: async () => {
      const response = await get<Service>(`/services/${id}`);
      // get() helper returns response.data which is the service object
      return response;
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
      const response = await post<Service>("/services", service);
      // post() helper returns response.data which is the service object
      return response;
    },
    onSuccess: () => {
      // Invalidate all services queries regardless of filters
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
      const response = await put<Service>(`/services/${id}`, updates);
      // put() helper returns response.data which is the service object
      return response;
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
      await del(`/services/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["services"] });
    },
  });
}
