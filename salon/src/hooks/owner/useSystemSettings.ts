import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface SystemConfig {
  rate_limit_enabled: boolean;
  rate_limit_requests: number;
  rate_limit_window: number;
  ddos_protection_enabled: boolean;
  ddos_threshold: number;
  waf_enabled: boolean;
  intrusion_detection_enabled: boolean;
  audit_logging_enabled: boolean;
  feature_flags: Record<string, boolean>;
}

export function useSystemSettings() {
  return useQuery({
    queryKey: ["system-settings"],
    queryFn: async () => {
      const response = await apiClient.get("/settings/system");
      return response.data as SystemConfig;
    },
  });
}

export function useUpdateSystemSettings() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (config: SystemConfig) => {
      const response = await apiClient.put("/settings/system", config);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["system-settings"] });
    },
  });
}
