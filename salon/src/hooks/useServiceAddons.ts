import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface ServiceAddon {
  id: string;
  name: string;
  description: string;
  price: number;
  duration_minutes: number;
  image_url?: string;
  category: "product" | "upgrade" | "treatment";
  display_order: number;
  is_active: boolean;
}

export function useServiceAddons(serviceId: string | null) {
  return useQuery({
    queryKey: ["service-addons", serviceId],
    queryFn: async () => {
      if (!serviceId) return [];
      const { data } = await apiClient.get<ServiceAddon[]>(
        `/public/service-addons/${serviceId}`,
      );
      return data;
    },
    enabled: !!serviceId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
