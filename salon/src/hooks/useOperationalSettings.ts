import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface OperationalConfig {
  inventory_tracking_enabled: boolean;
  low_stock_threshold: number;
  waiting_room_enabled: boolean;
  waiting_room_max_capacity: number;
  resource_management_enabled: boolean;
  notification_preferences_enabled: boolean;
  sms_provider: "termii" | "twilio" | "none";
  email_provider: "smtp" | "sendgrid" | "none";
  backup_enabled: boolean;
  backup_frequency: "daily" | "weekly" | "monthly";
  cache_optimization_enabled: boolean;
  cache_ttl_minutes: number;
}

export function useOperationalSettings() {
  return useQuery({
    queryKey: ["operational-settings"],
    queryFn: async () => {
      const response = await apiClient.get("/settings/operational");
      return response.data as OperationalConfig;
    },
  });
}

export function useUpdateOperationalSettings() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (config: OperationalConfig) => {
      const response = await apiClient.put("/settings/operational", config);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["operational-settings"] });
    },
  });
}
