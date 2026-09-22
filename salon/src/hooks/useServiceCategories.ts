import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { get, post, put, del } from "@/lib/utils/api";

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
      try {
        const response = await get<{
          categories: ServiceCategory[];
          total: number;
        }>("/service-categories");
        return (response as any)?.categories || [];
      } catch (error) {
        console.error("Error fetching service categories:", error);
        return [];
      }
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
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
      const response = await post<ServiceCategory>(
        "/service-categories",
        category,
        {
          headers: { "Idempotency-Key": crypto.randomUUID() }
        }
      );
      return response;
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
      const response = await put<ServiceCategory>(
        `/service-categories/${id}`,
        updates,
      );
      return response;
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
      await del(`/service-categories/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["serviceCategories"] });
    },
  });
}
