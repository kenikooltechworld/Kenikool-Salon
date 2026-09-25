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
  reference?: string;
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
      const params = new URLSearchParams();
      if (filters?.status) params.append("status", filters.status);
      if (filters?.customerId) params.append("customerId", filters.customerId);
      if (filters?.method) params.append("method", filters.method);
      if (filters?.startDate) params.append("startDate", filters.startDate);
      if (filters?.endDate) params.append("endDate", filters.endDate);

      const queryString = params.toString();
      const { data } = await apiClient.get<{ payments: any[] }>(
        queryString ? `/payments?${queryString}` : "/payments",
      );
      return (data.payments || []).map((p: any) => ({
        id: p.id,
        invoiceId: p.invoiceId,
        customerId: p.customerId,
        amount: p.amount,
        method: p.paymentMethod || p.method || "paystack",
        status: p.status,
        transactionId: p.transactionId,
        createdAt: p.createdAt,
        updatedAt: p.updatedAt,
      }));
    },
    refetchOnMount: true,
  });
}

/**
 * Fetch single payment by ID
 */
export function usePayment(id: string) {
  return useQuery({
    queryKey: ["payments", id],
    queryFn: async () => {
      const { data } = await apiClient.get<any>(`/payments/${id}`);
      return {
        id: data.id,
        invoiceId: data.invoiceId,
        customerId: data.customerId,
        amount: data.amount,
        method: data.paymentMethod || data.method || "paystack",
        status: data.status,
        transactionId: data.transactionId,
        createdAt: data.createdAt,
        updatedAt: data.updatedAt,
      };
    },
    enabled: !!id,
    refetchOnMount: true,
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
      const { data } = await apiClient.post<{ data: any }>(
        "/payments",
        {
          ...payment,
          paymentMethod: payment.method,
        },
      );
      return data.data;
    },
    onSuccess: () => {
      queryClient.refetchQueries({ queryKey: ["payments"], exact: false });
      queryClient.refetchQueries({ queryKey: ["invoices"], exact: false });
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
      const { data } = await apiClient.post<{ data: any }>(
        `/payments/${id}`,
        {
          ...updates,
          paymentMethod: updates.method,
        },
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
      queryClient.refetchQueries({ queryKey: ["payments"], exact: false });
      queryClient.refetchQueries({ queryKey: ["invoices"], exact: false });
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
          reference: request.reference,
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
      const payment = await apiClient.get<{
        id: string;
        invoiceId: string;
        customerId: string;
        amount: number;
        paymentMethod?: string;
        method?: string;
        status: string;
        transactionId?: string;
        createdAt?: string;
        updatedAt?: string;
      }>(`/payments/${reference}/verify`);

      if (payment.status === "cancelled") {
        throw new Error("Payment was cancelled by the user");
      }

      if (payment.status === "failed") {
        throw new Error("Payment failed. Please try again.");
      }

      return {
        id: payment.id,
        invoiceId: payment.invoiceId,
        customerId: payment.customerId,
        amount: payment.amount,
        method: payment.paymentMethod || payment.method || "paystack",
        status: payment.status,
        transactionId: payment.transactionId,
        createdAt: payment.createdAt,
        updatedAt: payment.updatedAt,
      };
    },
    onSuccess: () => {
      queryClient.refetchQueries({ queryKey: ["payments"], exact: false });
      queryClient.refetchQueries({ queryKey: ["invoices"], exact: false });
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
      const response = await apiClient.post<{
        id: string;
        invoiceId: string;
        customerId: string;
        amount: number;
        paymentMethod?: string;
        method?: string;
        status: string;
        transactionId?: string;
        createdAt?: string;
        updatedAt?: string;
      }>(`/payments/${paymentId}/retry`);
      const payment = response.data;

      return {
        id: payment.id,
        invoiceId: payment.invoiceId,
        customerId: payment.customerId,
        amount: payment.amount,
        method: payment.paymentMethod || payment.method || "paystack",
        status: payment.status,
        transactionId: payment.transactionId,
        createdAt: payment.createdAt,
        updatedAt: payment.updatedAt,
      };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["payments"] });
    },
  });
}
