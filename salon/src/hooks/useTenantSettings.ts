import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";
import { useTenantStore } from "@/stores/tenant";

export interface BusinessHours {
  open_time: string;
  close_time: string;
  is_closed: boolean;
}

export interface TenantSettingsData {
  salon_name: string;
  email: string;
  phone: string;
  address: string;
  tax_rate: number;
  currency: string;
  timezone: string;
  language: string;
  business_hours: {
    monday: BusinessHours;
    tuesday: BusinessHours;
    wednesday: BusinessHours;
    thursday: BusinessHours;
    friday: BusinessHours;
    saturday: BusinessHours;
    sunday: BusinessHours;
  };
  notification_email: boolean;
  notification_sms: boolean;
  notification_push: boolean;
  logo_url?: string;
  primary_color: string;
  secondary_color: string;
  appointment_reminder_hours: number;
  allow_online_booking: boolean;
  require_customer_approval: boolean;
  auto_confirm_bookings: boolean;
}

const TENANT_SETTINGS_KEY = "tenantSettings";

// Default business hours
const DEFAULT_BUSINESS_HOURS = {
  monday: { open_time: "09:00", close_time: "18:00", is_closed: false },
  tuesday: { open_time: "09:00", close_time: "18:00", is_closed: false },
  wednesday: { open_time: "09:00", close_time: "18:00", is_closed: false },
  thursday: { open_time: "09:00", close_time: "18:00", is_closed: false },
  friday: { open_time: "09:00", close_time: "18:00", is_closed: false },
  saturday: { open_time: "10:00", close_time: "16:00", is_closed: false },
  sunday: { open_time: "00:00", close_time: "00:00", is_closed: true },
};

export function useTenantSettings() {
  const tenantId = useTenantStore((state) => state.tenantId());

  return useQuery({
    queryKey: [TENANT_SETTINGS_KEY, tenantId],
    queryFn: async () => {
      if (!tenantId) throw new Error("No tenant ID");

      const { data } = await apiClient.get(`/settings`);
      return data.data as TenantSettingsData;
    },
    enabled: !!tenantId,
    staleTime: 5 * 60 * 1000,
  });
}

export function useUpdateTenantSettings() {
  const queryClient = useQueryClient();
  const tenantId = useTenantStore((state) => state.tenantId());

  return useMutation({
    mutationFn: async (updates: Partial<TenantSettingsData>) => {
      if (!tenantId) throw new Error("No tenant ID");

      const { data } = await apiClient.put(`/settings`, updates);
      return data.data as TenantSettingsData;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [TENANT_SETTINGS_KEY] });
    },
  });
}
