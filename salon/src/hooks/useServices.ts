import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { get, post, put, del } from "@/lib/utils/api";
import type { Service, ServiceFilters } from "@/types/service";

/**
 * Fetch all services with optional filters
 */
export function useServices(filters?: ServiceFilters) {
  return useQuery({
    queryKey: ["services", filters || {}],
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
        return response.services || [];
      } catch (error) {
        console.error("Error fetching services:", error);
        return [];
      }
    },
    staleTime: 60 * 60 * 1000, // 1 hour
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
      return response;
    },
    onSuccess: (newService) => {
      queryClient.setQueryData(
        ["services", {}],
        (oldData: Service[] = []) => [newService, ...oldData],
      );
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
      return response;
    },
    onSuccess: (updatedService) => {
      queryClient.setQueryData(
        ["services", updatedService.id],
        updatedService,
      );
      queryClient.setQueryData(
        ["services", {}],
        (oldData: Service[] = []) =>
          oldData.map((service) =>
            service.id === updatedService.id ? updatedService : service,
          ),
      );
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
      const result = await del<{ message?: string }>(`/services/${id}`);
      return result;
    },
    onSuccess: (_, deletedId) => {
      queryClient.setQueryData(
        ["services", {}],
        (oldData: Service[] = []) =>
          oldData.filter((service) => service.id !== deletedId),
      );
    },
  });
}
