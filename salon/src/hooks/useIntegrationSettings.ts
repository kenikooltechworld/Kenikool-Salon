import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface IntegrationConfig {
  termii_enabled: boolean;
  termii_api_key: string;
  paystack_enabled: boolean;
  paystack_public_key: string;
  paystack_webhook_url: string;
  payment_retry_enabled: boolean;
  payment_retry_attempts: number;
  payment_retry_delay: number;
}

export function useIntegrationSettings() {
  return useQuery({
    queryKey: ["integration-settings"],
    queryFn: async () => {
      const response = await apiClient.get("/settings/integrations");
      return response.data as IntegrationConfig;
    },
  });
}

export function useUpdateIntegrationSettings() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (config: IntegrationConfig) => {
      const response = await apiClient.put("/settings/integrations", config);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["integration-settings"] });
    },
  });
}
