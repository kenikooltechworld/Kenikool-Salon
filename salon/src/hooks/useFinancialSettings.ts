import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface FinancialConfig {
  balance_enforcement_enabled: boolean;
  minimum_balance_threshold: number;
  refund_policy_enabled: boolean;
  refund_window_days: number;
  commission_tracking_enabled: boolean;
  staff_commission_percentage: number;
  service_commission_percentage: number;
  invoice_numbering_prefix: string;
  invoice_numbering_start: number;
}

export function useFinancialSettings() {
  return useQuery({
    queryKey: ["financial-settings"],
    queryFn: async () => {
      const response = await apiClient.get("/settings/financial");
      return response.data as FinancialConfig;
    },
  });
}

export function useUpdateFinancialSettings() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (config: FinancialConfig) => {
      const response = await apiClient.put("/settings/financial", config);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["financial-settings"] });
    },
  });
}
