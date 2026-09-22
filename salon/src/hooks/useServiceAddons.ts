import { useQuery } from "@tanstack/react-query";
import { get } from "@/lib/utils/api";

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
      try {
        const response = await get<ServiceAddon[]>(
          `/public/service-addons/${serviceId}`,
        );
        return response || [];
      } catch (error) {
        console.error("Error fetching service addons:", error);
        return [];
      }
    },
    enabled: !!serviceId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
