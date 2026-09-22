import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { get, post, put, del } from "@/lib/utils/api";
import type { ServiceAddon } from "@/hooks/useServiceAddons";

export interface ServiceAddonFilters {
  is_active?: boolean;
  category?: "product" | "upgrade" | "treatment";
  search?: string;
  page?: number;
  limit?: number;
}

export interface CreateServiceAddonInput {
  name: string;
  description: string;
  price: number;
  duration_minutes: number;
  image_url?: string;
  category: "product" | "upgrade" | "treatment";
  display_order?: number;
  is_active?: boolean;
}

export interface UpdateServiceAddonInput {
  name?: string;
  description?: string;
  price?: number;
  duration_minutes?: number;
  image_url?: string;
  category?: "product" | "upgrade" | "treatment";
  display_order?: number;
  is_active?: boolean;
}

/**
 * Fetch all service addons with optional filters (admin)
 */
export function useAllServiceAddons(filters?: ServiceAddonFilters) {
  return useQuery({
    queryKey: ["service-addons-admin", filters],
    queryFn: async () => {
      try {
        const response = await get<ServiceAddon[]>("/service-addons", {
          params: filters,
        });
        return response || [];
      } catch (error) {
        console.error("Error fetching service addons:", error);
        return [];
      }
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Fetch single service addon by ID (admin)
 */
export function useServiceAddon(id: string) {
  return useQuery({
    queryKey: ["service-addon-admin", id],
    queryFn: async () => {
      const response = await get<ServiceAddon>(`/service-addons/${id}`);
      return response;
    },
    enabled: !!id,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Create new service addon (admin)
 */
export function useCreateServiceAddon() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (addonData: CreateServiceAddonInput) => {
      const response = await post<ServiceAddon>("/service-addons", addonData, {
        headers: { "Idempotency-Key": crypto.randomUUID() }
      });
      return response;
    },
    onSuccess: () => {
      // Invalidate all service addons queries
      queryClient.invalidateQueries({ queryKey: ["service-addons-admin"] });
      queryClient.invalidateQueries({ queryKey: ["service-addons"] });
    },
  });
}

/**
 * Update service addon (admin)
 */
export function useUpdateServiceAddon() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      id,
      ...updates
    }: UpdateServiceAddonInput & { id: string }) => {
      const response = await put<ServiceAddon>(`/service-addons/${id}`, updates);
      return response;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["service-addons-admin"] });
      queryClient.invalidateQueries({ queryKey: ["service-addons"] });
      queryClient.invalidateQueries({
        queryKey: ["service-addon-admin", (data as any).id],
      });
    },
  });
}

/**
 * Delete service addon (admin)
 */
export function useDeleteServiceAddon() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await del(`/service-addons/${id}`);
      return { id };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["service-addons-admin"] });
      queryClient.invalidateQueries({ queryKey: ["service-addons"] });
    },
  });
}