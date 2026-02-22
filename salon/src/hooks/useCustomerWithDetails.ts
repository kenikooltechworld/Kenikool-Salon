import { useCustomer } from "./useCustomers";
import { useCustomerHistory } from "./useCustomerHistory";
import { useCustomerPreferences } from "./useCustomerPreferences";

export interface CustomerWithHistory {
  id: string;
  email: string;
  phone: string;
  firstName: string;
  lastName: string;
  status: "active" | "inactive" | "suspended";
  createdAt: string;
  updatedAt: string;
  history: Array<{
    id: string;
    appointment_id: string;
    service_id: string;
    staff_id: string;
    service_name: string;
    staff_name: string;
    appointment_date: string;
    appointment_time: string;
    notes: string;
    rating: number;
    feedback: string;
  }>;
}

export interface CustomerWithPreferences {
  id: string;
  email: string;
  phone: string;
  firstName: string;
  lastName: string;
  status: "active" | "inactive" | "suspended";
  createdAt: string;
  updatedAt: string;
  preferences: {
    id: string;
    preferred_staff_ids: string[];
    preferred_service_ids: string[];
    communication_methods: ("email" | "sms" | "phone")[];
    preferred_time_slots: ("morning" | "afternoon" | "evening")[];
    language: string;
    notes: string;
  };
}

export interface CustomerProfile {
  id: string;
  email: string;
  phone: string;
  firstName: string;
  lastName: string;
  status: "active" | "inactive" | "suspended";
  createdAt: string;
  updatedAt: string;
  history: Array<{
    id: string;
    appointment_id: string;
    service_id: string;
    staff_id: string;
    service_name: string;
    staff_name: string;
    appointment_date: string;
    appointment_time: string;
    notes: string;
    rating: number;
    feedback: string;
  }>;
  preferences: {
    id: string;
    preferred_staff_ids: string[];
    preferred_service_ids: string[];
    communication_methods: ("email" | "sms" | "phone")[];
    preferred_time_slots: ("morning" | "afternoon" | "evening")[];
    language: string;
    notes: string;
  };
}

/**
 * Fetch customer with their appointment history
 */
export function useCustomerWithHistory(customerId: string) {
  const { data: customer, isLoading: customerLoading } =
    useCustomer(customerId);
  const { data: history, isLoading: historyLoading } =
    useCustomerHistory(customerId);

  return {
    data: customer && history ? { ...customer, history } : null,
    isLoading: customerLoading || historyLoading,
  };
}

/**
 * Fetch customer with their preferences
 */
export function useCustomerWithPreferences(customerId: string) {
  const { data: customer, isLoading: customerLoading } =
    useCustomer(customerId);
  const { data: preferences, isLoading: preferencesLoading } =
    useCustomerPreferences(customerId);

  return {
    data: customer && preferences ? { ...customer, preferences } : null,
    isLoading: customerLoading || preferencesLoading,
  };
}

/**
 * Fetch complete customer profile (history + preferences)
 */
export function useCustomerProfile(customerId: string) {
  const { data: customer, isLoading: customerLoading } =
    useCustomer(customerId);
  const { data: history, isLoading: historyLoading } =
    useCustomerHistory(customerId);
  const { data: preferences, isLoading: preferencesLoading } =
    useCustomerPreferences(customerId);

  return {
    data: customer
      ? {
          ...customer,
          history: history || [],
          preferences: preferences || null,
        }
      : null,
    isLoading: customerLoading || historyLoading || preferencesLoading,
  };
}
