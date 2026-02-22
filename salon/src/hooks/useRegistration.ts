import { useMutation } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface RegistrationData {
  salon_name: string;
  owner_name: string;
  email: string;
  phone: string;
  password: string;
  address: string;
  bank_account?: string;
  referral_code?: string;
}

export interface RegistrationResponse {
  success: boolean;
  message: string;
  data?: {
    temp_registration_id: string;
    email: string;
    expires_at?: string;
  };
}

export interface VerificationResponse {
  success: boolean;
  message: string;
  data?: {
    tenant_id: string;
    subdomain: string;
    full_url: string;
    user_id: string;
    token: string;
  };
}

/**
 * Register a new salon owner
 */
export function useRegisterSalon() {
  return useMutation({
    mutationFn: async (data: RegistrationData) => {
      const { data: response } = await apiClient.post<RegistrationResponse>(
        "/auth/register",
        data,
      );
      return response;
    },
  });
}

/**
 * Verify registration code and create accounts
 */
export function useVerifyRegistrationCode() {
  return useMutation({
    mutationFn: async ({ email, code }: { email: string; code: string }) => {
      const { data } = await apiClient.post<VerificationResponse>(
        "/auth/verify-code",
        { email, code },
      );
      return data;
    },
  });
}

/**
 * Resend verification code
 */
export function useResendVerificationCode() {
  return useMutation({
    mutationFn: async (email: string) => {
      const { data } = await apiClient.post<RegistrationResponse>(
        "/auth/resend-code",
        { email },
      );
      return data;
    },
  });
}
