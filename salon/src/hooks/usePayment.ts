import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface PaymentInitiation {
  amount: number;
  email: string;
  reference: string;
  transactionId: string;
}

export interface PaymentVerification {
  reference: string;
  status: "success" | "failed" | "pending";
  amount: number;
  paystackReference?: string;
}

/**
 * Initialize payment with Paystack
 */
export function useInitializePayment() {
  return useMutation({
    mutationFn: async (data: PaymentInitiation) => {
      const response = await apiClient.post<{
        authorizationUrl: string;
        accessCode: string;
        reference: string;
      }>("/payments/initialize", data);
      return response.data;
    },
  });
}

/**
 * Verify payment status
 */
export function useVerifyPayment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (reference: string) => {
      const response = await apiClient.get<PaymentVerification>(
        `/payments/${reference}/verify`,
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
    },
  });
}

/**
 * Process refund
 */
export function useProcessRefund() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      reference,
      amount,
    }: {
      reference: string;
      amount: number;
    }) => {
      const response = await apiClient.post(`/payments/${reference}/refund`, {
        amount,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      queryClient.invalidateQueries({ queryKey: ["refunds"] });
    },
  });
}

/**
 * Retry failed payment
 */
export function useRetryPayment() {
  return useMutation({
    mutationFn: async (transactionId: string) => {
      const response = await apiClient.post(
        `/payments/${transactionId}/retry`,
        {},
      );
      return response.data;
    },
  });
}

/**
 * Initialize payment for POS transaction
 */
export function useInitializePOSPayment() {
  return useMutation({
    mutationFn: async ({
      transactionId,
      email,
      callbackUrl,
    }: {
      transactionId: string;
      email: string;
      callbackUrl?: string;
    }) => {
      const response = await apiClient.post<{
        success: boolean;
        paymentId: string;
        authorizationUrl: string;
        accessCode: string;
        reference: string;
      }>(`/transactions/${transactionId}/initialize-payment`, {
        email,
        callback_url: callbackUrl,
      });
      return response.data;
    },
  });
}

/**
 * Verify payment for POS transaction
 */
export function useVerifyPOSPayment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      transactionId,
      reference,
    }: {
      transactionId: string;
      reference: string;
    }) => {
      const response = await apiClient.post<{
        success: boolean;
        paymentStatus: string;
        transactionId: string;
        reference: string;
        amount: number;
        message: string;
      }>(`/transactions/${transactionId}/verify-payment`, {
        reference,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
    },
  });
}
