import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { get, post, put, del } from "@/lib/utils";

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
  outstandingBalance?: number;
  emailVerified?: boolean;
  phoneVerified?: boolean;
  isGuest?: boolean;
  lastLogin?: string;
  createdAt: string;
  updatedAt: string;
}

export interface CustomerBalance {
  customerId: string;
  customerName: string;
  outstandingBalance: number;
  unpaidInvoiceCount: number;
  unpaidInvoices: Array<{
    invoiceId: string;
    amount: number;
    status: string;
    dueDate?: string;
    createdAt: string;
  }>;
}

export interface BookingEligibility {
  customerId: string;
  customerName: string;
  outstandingBalance: number;
  isEligibleToBook: boolean;
  reason: string;
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
      const data = await get<any>("/customers", {
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
          outstandingBalance: customer.outstanding_balance,
          emailVerified: customer.email_verified,
          phoneVerified: customer.phone_verified,
          isGuest: customer.is_guest,
          lastLogin: customer.last_login,
          createdAt: customer.created_at,
          updatedAt: customer.updated_at,
        })),
        total: data.total,
        page: data.page,
        pageSize: data.page_size,
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
      const customer = await get<any>(`/customers/${id}`);
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
        outstandingBalance: customer.outstanding_balance,
        emailVerified: customer.email_verified,
        phoneVerified: customer.phone_verified,
        isGuest: customer.is_guest,
        lastLogin: customer.last_login,
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
      // Build payload with only non-empty values
      const payload: any = {
        first_name: customer.firstName,
        last_name: customer.lastName,
        email: customer.email,
        phone: customer.phone,
        communication_preference: customer.communicationPreference || "email",
        status: customer.status || "active",
      };

      // Only include optional fields if they have values
      if (customer.address && customer.address.trim()) {
        payload.address = customer.address;
      }
      if (customer.dateOfBirth && customer.dateOfBirth.trim()) {
        payload.date_of_birth = customer.dateOfBirth;
      }
      if (customer.preferredStaffId) {
        payload.preferred_staff_id = customer.preferredStaffId;
      }
      if (customer.preferredServices && customer.preferredServices.length > 0) {
        payload.preferred_services = customer.preferredServices;
      }

      const data = await post<any>("/customers", payload);
      return data;
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
      if (updates.firstName !== undefined)
        payload.first_name = updates.firstName;
      if (updates.lastName !== undefined) payload.last_name = updates.lastName;
      if (updates.email !== undefined) payload.email = updates.email;
      if (updates.phone !== undefined) payload.phone = updates.phone;
      if (updates.address !== undefined) payload.address = updates.address;
      if (updates.dateOfBirth !== undefined)
        payload.date_of_birth = updates.dateOfBirth;
      if (updates.preferredStaffId !== undefined)
        payload.preferred_staff_id = updates.preferredStaffId;
      if (updates.preferredServices !== undefined)
        payload.preferred_services = updates.preferredServices;
      if (updates.communicationPreference !== undefined)
        payload.communication_preference = updates.communicationPreference;
      if (updates.status !== undefined) payload.status = updates.status;

      const data = await put<any>(`/customers/${id}`, payload);
      return data;
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
      await del(`/customers/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["customers"] });
    },
  });
}

/**
 * Fetch customer balance information
 */
export function useCustomerBalance(id: string) {
  return useQuery({
    queryKey: ["customer-balance", id],
    queryFn: async () => {
      const data = await get<CustomerBalance>(`/customers/${id}/balance`);
      return data;
    },
    enabled: !!id,
  });
}

/**
 * Update customer balance (recalculate from invoices)
 */
export function useUpdateCustomerBalance() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      const data = await put<any>(`/customers/${id}/balance`);
      return data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["customer-balance", data.customer_id] });
      queryClient.invalidateQueries({ queryKey: ["customers", data.customer_id] });
      queryClient.invalidateQueries({ queryKey: ["customers"] });
    },
  });
}

/**
 * Check customer booking eligibility
 */
export function useCustomerBookingEligibility(id: string) {
  return useQuery({
    queryKey: ["customer-booking-eligibility", id],
    queryFn: async () => {
      const data = await get<BookingEligibility>(`/customers/${id}/booking-eligibility`);
      return data;
    },
    enabled: !!id,
  });
}

/**
 * Resend portal invitation to customer
 */
export function useResendPortalInvitation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      const data = await post<any>(`/customers/${id}/resend-portal-invitation`);
      return data;
    },
    onSuccess: (data, id) => {
      queryClient.invalidateQueries({ queryKey: ["customers", id] });
    },
  });
}
