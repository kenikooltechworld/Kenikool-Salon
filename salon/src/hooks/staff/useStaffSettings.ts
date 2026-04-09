import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { get, put } from "@/lib/utils/api";

export interface StaffSettingsData {
  id: string;
  user_id: string;
  first_name: string;
  last_name: string;
  phone?: string;
  email_bookings: boolean;
  email_reminders: boolean;
  email_messages: boolean;
  sms_bookings: boolean;
  sms_reminders: boolean;
  push_bookings: boolean;
  push_reminders: boolean;

  // Phase 3: Availability preferences
  working_hours_start?: string;
  working_hours_end?: string;
  days_off: string[];

  // Phase 3: Emergency contact
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  emergency_contact_relationship?: string;

  // Phase 3: Work preferences
  service_specializations: string[];
  preferred_customer_types: string[];

  created_at: string;
  updated_at: string;
}

export interface StaffSettingsUpdateData {
  first_name?: string;
  last_name?: string;
  phone?: string;
  email_bookings?: boolean;
  email_reminders?: boolean;
  email_messages?: boolean;
  sms_bookings?: boolean;
  sms_reminders?: boolean;
  push_bookings?: boolean;
  push_reminders?: boolean;

  // Phase 3: Availability preferences
  working_hours_start?: string;
  working_hours_end?: string;
  days_off?: string[];

  // Phase 3: Emergency contact
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  emergency_contact_relationship?: string;

  // Phase 3: Work preferences
  service_specializations?: string[];
  preferred_customer_types?: string[];
}

export function useStaffSettings() {
  return useQuery({
    queryKey: ["staff-settings"],
    queryFn: async () => {
      return get<StaffSettingsData>("/staff/settings");
    },
  });
}

export function useUpdateStaffSettings() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: StaffSettingsUpdateData) => {
      return put<StaffSettingsData>("/staff/settings", data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["staff-settings"] });
    },
  });
}
