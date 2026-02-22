import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface ServiceCategory {
  id: string;
  name: string;
  description?: string;
  color?: string;
  icon?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * Fetch all service categories
 */
export function useServiceCategories() {
  return useQuery({
    queryKey: ["serviceCategories"],
    queryFn: async () => {
      const response = await apiClient.get<{
        categories: ServiceCategory[];
        total: number;
      }>("/service-categories");
      return (response as any).data?.categories || [];
    },
  });
}

/**
 * Create new service category
 */
export function useCreateServiceCategory() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (
      category: Omit<ServiceCategory, "id" | "created_at" | "updated_at">,
    ) => {
      const response = await apiClient.post<ServiceCategory>(
        "/service-categories",
        category,
      );
      return (response as any).data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["serviceCategories"] });
    },
  });
}

/**
 * Update service category
 */
export function useUpdateServiceCategory() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      id,
      ...updates
    }: Partial<ServiceCategory> & { id: string }) => {
      const response = await apiClient.put<ServiceCategory>(
        `/service-categories/${id}`,
        updates,
      );
      return (response as any).data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["serviceCategories"] });
    },
  });
}

/**
 * Delete service category
 */
export function useDeleteServiceCategory() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/service-categories/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["serviceCategories"] });
    },
  });
}
