import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface CustomerPreference {
  id: string;
  customer_id: string;
  preferred_staff_ids: string[];
  preferred_service_ids: string[];
  communication_methods: ("email" | "sms" | "phone")[];
  preferred_time_slots: ("morning" | "afternoon" | "evening")[];
  language: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

interface UpdatePreferenceData {
  preferred_staff_ids?: string[];
  preferred_service_ids?: string[];
  communication_methods?: ("email" | "sms" | "phone")[];
  preferred_time_slots?: ("morning" | "afternoon" | "evening")[];
  language?: string;
  notes?: string;
}

/**
 * Fetch customer preferences
 */
export function useCustomerPreferences(customerId: string) {
  return useQuery({
    queryKey: ["customer-preferences", customerId],
    queryFn: async () => {
      const { data } = await apiClient.get<CustomerPreference>(
        `/customers/${customerId}/preferences`,
      );
      return data || null;
    },
    enabled: !!customerId,
  });
}

/**
 * Update customer preferences
 */
export function useUpdateCustomerPreferences() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      customerId,
      ...updates
    }: UpdatePreferenceData & { customerId: string }) => {
      const { data } = await apiClient.put<CustomerPreference>(
        `/customers/${customerId}/preferences`,
        updates,
      );
      return data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: ["customer-preferences", data.customer_id],
      });
    },
  });
}
