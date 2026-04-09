import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

interface CustomerRegisterData {
  email: string;
  phone: string;
  password: string;
  first_name: string;
  last_name: string;
}

interface CustomerLoginData {
  username: string; // email
  password: string;
}

interface CustomerToken {
  access_token: string;
  token_type: string;
  customer_id: string;
  email: string;
  first_name: string;
  last_name: string;
}

interface CustomerProfile {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  phone: string;
  address?: string;
  date_of_birth?: string;
  email_verified: boolean;
  phone_verified: boolean;
  communication_preference: string;
  notification_preferences: Record<string, boolean>;
  outstanding_balance: number;
  created_at: string;
}

interface CustomerProfileUpdate {
  first_name?: string;
  last_name?: string;
  phone?: string;
  address?: string;
  date_of_birth?: string;
  communication_preference?: string;
  notification_preferences?: Record<string, boolean>;
}

export function useCustomerRegister() {
  return useMutation({
    mutationFn: async (data: CustomerRegisterData) => {
      const { data: response } = await apiClient.post(
        "/public/customer-auth/register",
        data,
      );
      return response;
    },
  });
}

export function useCustomerLogin() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: CustomerLoginData) => {
      const formData = new FormData();
      formData.append("username", data.username);
      formData.append("password", data.password);

      const { data: response } = await apiClient.post<CustomerToken>(
        "/public/customer-auth/login",
        formData,
        {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
        },
      );

      // Store token in localStorage
      localStorage.setItem("customer_token", response.access_token);
      localStorage.setItem("customer_id", response.customer_id);

      return response;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["customer-profile"] });
    },
  });
}

export function useCustomerLogout() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      localStorage.removeItem("customer_token");
      localStorage.removeItem("customer_id");
    },
    onSuccess: () => {
      queryClient.clear();
    },
  });
}

export function useCustomerProfile() {
  const token = localStorage.getItem("customer_token");

  return useQuery({
    queryKey: ["customer-profile"],
    queryFn: async () => {
      const { data } = await apiClient.get<CustomerProfile>(
        "/public/customer-auth/me",
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      );
      return data;
    },
    enabled: !!token,
  });
}

export function useUpdateCustomerProfile() {
  const queryClient = useQueryClient();
  const token = localStorage.getItem("customer_token");

  return useMutation({
    mutationFn: async (data: CustomerProfileUpdate) => {
      const { data: response } = await apiClient.put<CustomerProfile>(
        "/public/customer-auth/me",
        data,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      );
      return response;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["customer-profile"] });
    },
  });
}

export function useIsCustomerAuthenticated() {
  const token = localStorage.getItem("customer_token");
  return !!token;
}
