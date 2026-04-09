import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/utils/api";

export type {
  ServicePackage,
  ServicePackageItem,
  ServicePackageCreate,
  ServicePackageUpdate,
  ServicePackageFilters,
  ServicePackageListResponse,
};

export interface ServicePackageItem {
  id: string;
  service_id: string;
  service_name: string;
  service_price: number;
  service_duration: number;
  quantity: number;
}

export interface ServicePackage {
  id: string;
  tenant_id: string;
  name: string;
  description?: string;
  services: ServicePackageItem[];
  original_price: number;
  package_price: number;
  discount_amount: number;
  discount_percentage: number;
  valid_from?: string;
  valid_until?: string;
  is_active: boolean;
  max_bookings_per_customer?: number;
  total_bookings_limit?: number;
  current_bookings_count: number;
  image_url?: string;
  display_order: number;
  is_featured: boolean;
  total_duration: number;
  is_valid: boolean;
  savings: {
    original_price: number;
    package_price: number;
    discount_amount: number;
    discount_percentage: number;
    you_save: number;
  };
  created_at: string;
  updated_at: string;
}

export interface ServicePackageCreate {
  name: string;
  description?: string;
  services: Array<{
    service_id: string;
    quantity: number;
  }>;
  package_price: number;
  valid_from?: string;
  valid_until?: string;
  is_active?: boolean;
  max_bookings_per_customer?: number;
  total_bookings_limit?: number;
  image_url?: string;
  display_order?: number;
  is_featured?: boolean;
}

export interface ServicePackageUpdate {
  name?: string;
  description?: string;
  services?: Array<{
    service_id: string;
    quantity: number;
  }>;
  package_price?: number;
  valid_from?: string;
  valid_until?: string;
  is_active?: boolean;
  max_bookings_per_customer?: number;
  total_bookings_limit?: number;
  image_url?: string;
  display_order?: number;
  is_featured?: boolean;
}

export interface ServicePackageFilters {
  page?: number;
  page_size?: number;
  is_active?: boolean;
  is_featured?: boolean;
  include_expired?: boolean;
}

export interface ServicePackageListResponse {
  packages: ServicePackage[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// Admin hooks
export function useServicePackages(filters?: ServicePackageFilters) {
  return useQuery({
    queryKey: ["service-packages", filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters?.page) params.append("page", filters.page.toString());
      if (filters?.page_size)
        params.append("page_size", filters.page_size.toString());
      if (filters?.is_active !== undefined)
        params.append("is_active", filters.is_active.toString());
      if (filters?.is_featured !== undefined)
        params.append("is_featured", filters.is_featured.toString());
      if (filters?.include_expired !== undefined)
        params.append("include_expired", filters.include_expired.toString());

      const response = await api.get<ServicePackageListResponse>(
        `/service-packages?${params.toString()}`,
      );
      return response.data;
    },
  });
}

export function useServicePackage(packageId: string) {
  return useQuery({
    queryKey: ["service-package", packageId],
    queryFn: async () => {
      const response = await api.get<ServicePackage>(
        `/service-packages/${packageId}`,
      );
      return response.data;
    },
    enabled: !!packageId,
  });
}

export function useCreateServicePackage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: ServicePackageCreate) => {
      const response = await api.post<ServicePackage>(
        "/service-packages",
        data,
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["service-packages"] });
    },
  });
}

export function useUpdateServicePackage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      id,
      data,
    }: {
      id: string;
      data: ServicePackageUpdate;
    }) => {
      const response = await api.put<ServicePackage>(
        `/service-packages/${id}`,
        data,
      );
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["service-packages"] });
      queryClient.invalidateQueries({
        queryKey: ["service-package", variables.id],
      });
    },
  });
}

export function useDeleteServicePackage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/service-packages/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["service-packages"] });
    },
  });
}

export function useTogglePackageActive() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      const response = await api.post<ServicePackage>(
        `/service-packages/${id}/toggle-active`,
      );
      return response.data;
    },
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ["service-packages"] });
      queryClient.invalidateQueries({ queryKey: ["service-package", id] });
    },
  });
}

export function useTogglePackageFeatured() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      const response = await api.post<ServicePackage>(
        `/service-packages/${id}/toggle-featured`,
      );
      return response.data;
    },
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ["service-packages"] });
      queryClient.invalidateQueries({ queryKey: ["service-package", id] });
    },
  });
}

// Public hooks (for customer-facing pages)
export function usePublicServicePackages(
  filters?: Omit<ServicePackageFilters, "is_active" | "include_expired">,
) {
  return useQuery({
    queryKey: ["public-service-packages", filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters?.page) params.append("page", filters.page.toString());
      if (filters?.page_size)
        params.append("page_size", filters.page_size.toString());
      if (filters?.is_featured !== undefined)
        params.append("is_featured", filters.is_featured.toString());

      const response = await api.get<ServicePackageListResponse>(
        `/public/service-packages?${params.toString()}`,
      );
      return response.data;
    },
  });
}

export function usePublicServicePackage(packageId: string) {
  return useQuery({
    queryKey: ["public-service-package", packageId],
    queryFn: async () => {
      const response = await api.get<ServicePackage>(
        `/public/service-packages/${packageId}`,
      );
      return response.data;
    },
    enabled: !!packageId,
  });
}
