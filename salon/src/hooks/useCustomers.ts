import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface Customer {
  id: string;
  email: string;
  phone: string;
  firstName: string;
  lastName: string;
  address?: string;
  dateOfBirth?: string;
  preferredStaffId?: string;
  preferredServices?: string[];
  communicationPreference?: "email" | "sms" | "phone" | "none";
  status: "active" | "inactive";
  createdAt: string;
  updatedAt: string;
}

interface CustomerFilters {
  status?: string;
  search?: string;
}

/**
 * Fetch all customers with optional filters
 */
export function useCustomers(filters?: CustomerFilters) {
  return useQuery({
    queryKey: ["customers", filters],
    queryFn: async () => {
      const { data } = await apiClient.get<any>("/customers", {
        params: filters,
      });
      // Transform backend response to match frontend interface
      return {
        customers: (data.customers || []).map((customer: any) => ({
          id: customer.id,
          email: customer.email,
          phone: customer.phone,
          firstName: customer.first_name,
          lastName: customer.last_name,
          address: customer.address,
          dateOfBirth: customer.date_of_birth,
          preferredStaffId: customer.preferred_staff_id,
          preferredServices: customer.preferred_services,
          communicationPreference: customer.communication_preference,
          status: customer.status,
          createdAt: customer.created_at,
          updatedAt: customer.updated_at,
        })),
        total: data.total,
        page: data.page,
        page_size: data.page_size,
      };
    },
  });
}

/**
 * Fetch single customer by ID
 */
export function useCustomer(id: string) {
  return useQuery({
    queryKey: ["customers", id],
    queryFn: async () => {
      const { data } = await apiClient.get<any>(`/customers/${id}`);
      const customer = data.data || data;
      if (!customer) return null;
      // Transform backend response to match frontend interface
      return {
        id: customer.id,
        email: customer.email,
        phone: customer.phone,
        firstName: customer.first_name,
        lastName: customer.last_name,
        address: customer.address,
        dateOfBirth: customer.date_of_birth,
        preferredStaffId: customer.preferred_staff_id,
        preferredServices: customer.preferred_services,
        communicationPreference: customer.communication_preference,
        status: customer.status,
        createdAt: customer.created_at,
        updatedAt: customer.updated_at,
      };
    },
    enabled: !!id,
  });
}

/**
 * Create new customer
 */
export function useCreateCustomer() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (
      customer: Omit<Customer, "id" | "createdAt" | "updatedAt">,
    ) => {
      const payload = {
        first_name: customer.firstName,
        last_name: customer.lastName,
        email: customer.email,
        phone: customer.phone,
        address: customer.address,
        date_of_birth: customer.dateOfBirth,
        preferred_staff_id: customer.preferredStaffId,
        preferred_services: customer.preferredServices,
        communication_preference: customer.communicationPreference,
        status: customer.status,
      };
      const { data } = await apiClient.post<any>("/customers", payload);
      return data.data || data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["customers"] });
    },
  });
}

/**
 * Update customer
 */
export function useUpdateCustomer() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      id,
      ...updates
    }: Partial<Customer> & { id: string }) => {
      const payload: any = {};
      if (updates.firstName) payload.first_name = updates.firstName;
      if (updates.lastName) payload.last_name = updates.lastName;
      if (updates.email) payload.email = updates.email;
      if (updates.phone) payload.phone = updates.phone;
      if (updates.address !== undefined) payload.address = updates.address;
      if (updates.dateOfBirth !== undefined)
        payload.date_of_birth = updates.dateOfBirth;
      if (updates.preferredStaffId !== undefined)
        payload.preferred_staff_id = updates.preferredStaffId;
      if (updates.preferredServices !== undefined)
        payload.preferred_services = updates.preferredServices;
      if (updates.communicationPreference)
        payload.communication_preference = updates.communicationPreference;
      if (updates.status) payload.status = updates.status;

      const { data } = await apiClient.put<any>(`/customers/${id}`, payload);
      return data.data || data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["customers"] });
      queryClient.invalidateQueries({ queryKey: ["customers", data.id] });
    },
  });
}

/**
 * Delete customer
 */
export function useDeleteCustomer() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/customers/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["customers"] });
    },
  });
}
