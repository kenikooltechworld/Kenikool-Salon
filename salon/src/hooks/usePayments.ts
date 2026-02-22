import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface Payment {
  id: string;
  invoiceId: string;
  customerId: string;
  amount: number;
  method: "card" | "bank_transfer" | "cash" | "paystack";
  status: "pending" | "completed" | "failed" | "refunded";
  transactionId?: string;
  createdAt: string;
  updatedAt: string;
}

export interface PaymentInitializeRequest {
  amount: number;
  customerId: string;
  invoiceId: string;
  email: string;
  metadata?: Record<string, any>;
  idempotencyKey?: string;
}

export interface PaymentInitializeResponse {
  paymentId: string;
  authorizationUrl: string;
  accessCode: string;
  reference: string;
}

interface PaymentFilters {
  status?: string;
  customerId?: string;
  method?: string;
  startDate?: string;
  endDate?: string;
}

/**
 * Fetch all payments with optional filters
 */
export function usePayments(filters?: PaymentFilters) {
  return useQuery({
    queryKey: ["payments", filters],
    queryFn: async () => {
      const { data } = await apiClient.get<{ data: Payment[] }>("/payments", {
        params: filters,
      });
      return data.data;
    },
  });
}

/**
 * Fetch single payment by ID
 */
export function usePayment(id: string) {
  return useQuery({
    queryKey: ["payments", id],
    queryFn: async () => {
      const { data } = await apiClient.get<{ data: Payment }>(
        `/payments/${id}`,
      );
      return data.data;
    },
    enabled: !!id,
  });
}

/**
 * Create new payment
 */
export function useCreatePayment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (
      payment: Omit<Payment, "id" | "createdAt" | "updatedAt">,
    ) => {
      const { data } = await apiClient.post<{ data: Payment }>(
        "/payments",
        payment,
      );
      return data.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["payments"] });
      queryClient.invalidateQueries({ queryKey: ["invoices"] });
    },
  });
}

/**
 * Update payment
 */
export function useUpdatePayment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      id,
      ...updates
    }: Partial<Payment> & { id: string }) => {
      const { data } = await apiClient.put<{ data: Payment }>(
        `/payments/${id}`,
        updates,
      );
      return data.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["payments"] });
      queryClient.invalidateQueries({ queryKey: ["payments", data.id] });
      queryClient.invalidateQueries({ queryKey: ["invoices"] });
    },
  });
}

/**
 * Refund payment
 */
export function useRefundPayment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await apiClient.post<{ data: Payment }>(
        `/payments/${id}/refund`,
      );
      return data.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["payments"] });
      queryClient.invalidateQueries({ queryKey: ["invoices"] });
    },
  });
}

/**
 * Initialize a payment transaction with Paystack
 * Handles payment initialization and redirects to Paystack payment page
 */
export function useInitializePayment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (request: PaymentInitializeRequest) => {
      const { data } = await apiClient.post<PaymentInitializeResponse>(
        "/payments/initialize",
        {
          amount: request.amount,
          customer_id: request.customerId,
          invoice_id: request.invoiceId,
          email: request.email,
          metadata: request.metadata,
          idempotency_key: request.idempotencyKey,
        },
      );
      return data;
    },
    onSuccess: (data) => {
      // Invalidate payments query to refresh list
      queryClient.invalidateQueries({ queryKey: ["payments"] });

      // Redirect to Paystack payment page
      if (data.authorizationUrl) {
        window.location.href = data.authorizationUrl;
      }
    },
    onError: (error: any) => {
      console.error("Payment initialization failed:", error);
    },
  });
}

/**
 * Verify a payment transaction status
 */
export function useVerifyPayment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (reference: string) => {
      const { data } = await apiClient.get<{ data: Payment }>(
        `/payments/${reference}/verify`,
      );
      return data.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["payments"] });
      queryClient.invalidateQueries({ queryKey: ["invoices"] });
    },
  });
}

/**
 * Retry a failed payment
 */
export function useRetryPayment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (paymentId: string) => {
      const { data } = await apiClient.post<{ data: Payment }>(
        `/payments/${paymentId}/retry`,
      );
      return data.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["payments"] });
    },
  });
}
