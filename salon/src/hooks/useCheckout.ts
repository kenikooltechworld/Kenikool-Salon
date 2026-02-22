import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";
import { usePOSStore } from "@/stores/pos";

export interface TransactionItem {
  itemType: "service" | "product" | "package";
  itemId: string;
  itemName: string;
  quantity: number;
  unitPrice: number;
  lineTota: number;
  taxRate: number;
  discountRate: number;
}

export interface Transaction {
  id: string;
  customerId: string;
  staffId: string;
  appointmentId?: string;
  transactionType: "service" | "product" | "package" | "refund";
  items: TransactionItem[];
  subtotal: number;
  taxAmount: number;
  discountAmount: number;
  total: number;
  paymentMethod: string;
  paymentStatus: "pending" | "completed" | "failed" | "refunded";
  referenceNumber: string;
  paystackReference?: string;
  notes?: string;
  createdAt: string;
  updatedAt: string;
}

/**
 * Create a transaction (checkout)
 */
export function useCheckout() {
  const queryClient = useQueryClient();
  const { setCurrentTransactionId, addToTransactionHistory } = usePOSStore();

  return useMutation({
    mutationFn: async (data: {
      customer_id: string;
      staff_id: string;
      appointment_id?: string;
      transaction_type?: string;
      items: Array<{
        item_type: string;
        item_id: string;
        item_name: string;
        quantity: number;
        unit_price: number;
        tax_rate?: number;
        discount_rate?: number;
      }>;
      payment_method: string;
      discount_amount?: number;
      notes?: string;
    }) => {
      const response = await apiClient.post<Transaction>("/transactions", data);
      return response.data;
    },
    onSuccess: (data) => {
      // Set current transaction ID in POS store
      setCurrentTransactionId(data.id);
      addToTransactionHistory(data.id);
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
    },
  });
}

/**
 * Get transaction by ID
 */
export function useTransaction(transactionId: string) {
  return useQuery({
    queryKey: ["transactions", transactionId],
    queryFn: async () => {
      const response = await apiClient.get<Transaction>(
        `/transactions/${transactionId}`,
      );
      return response.data;
    },
    enabled: !!transactionId,
  });
}

/**
 * List transactions
 */
export function useTransactions(filters?: {
  customerId?: string;
  staffId?: string;
  paymentStatus?: string;
  page?: number;
  pageSize?: number;
}) {
  return useQuery({
    queryKey: ["transactions", filters],
    queryFn: async () => {
      const response = await apiClient.get<{
        transactions: Transaction[];
        total: number;
        page: number;
        pageSize: number;
      }>("/transactions", { params: filters });
      return response.data;
    },
  });
}

/**
 * Update transaction
 */
export function useUpdateTransaction() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      transactionId,
      data,
    }: {
      transactionId: string;
      data: { paymentStatus?: string; notes?: string };
    }) => {
      const response = await apiClient.put<Transaction>(
        `/transactions/${transactionId}`,
        data,
      );
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      queryClient.invalidateQueries({
        queryKey: ["transactions", data.id],
      });
    },
  });
}
