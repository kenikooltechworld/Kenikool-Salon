import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface ReceiptItem {
  itemType: "service" | "product" | "package";
  itemId: string;
  itemName: string;
  quantity: number;
  unitPrice: number;
  lineTotal: number;
  taxAmount: number;
  discountAmount: number;
}

export interface Receipt {
  id: string;
  transactionId: string;
  customerId: string;
  receiptNumber: string;
  receiptDate: string;
  customerName: string;
  customerEmail?: string;
  customerPhone?: string;
  items: ReceiptItem[];
  subtotal: number;
  taxAmount: number;
  discountAmount: number;
  total: number;
  paymentMethod: string;
  paymentReference?: string;
  receiptFormat: "thermal" | "standard" | "email" | "digital";
  printedAt?: string;
  emailedAt?: string;
  createdAt: string;
}

/**
 * Get receipt for a transaction
 */
export function useReceipt(transactionId: string) {
  return useQuery({
    queryKey: ["receipts", transactionId],
    queryFn: async () => {
      const response = await apiClient.get<Receipt>(
        `/receipts/${transactionId}`,
      );
      return response.data;
    },
    enabled: !!transactionId,
  });
}

/**
 * List receipts
 */
export function useReceipts(filters?: {
  customerId?: string;
  page?: number;
  pageSize?: number;
}) {
  return useQuery({
    queryKey: ["receipts", filters],
    queryFn: async () => {
      const response = await apiClient.get<{
        receipts: Receipt[];
        total: number;
        page: number;
        pageSize: number;
      }>("/receipts", { params: filters });
      return response.data;
    },
  });
}

/**
 * Print receipt
 */
export function usePrintReceipt() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      receiptId,
      printerName,
    }: {
      receiptId: string;
      printerName?: string;
    }) => {
      const response = await apiClient.post(`/receipts/${receiptId}/print`, {
        printerName,
      });
      return response.data;
    },
    onSuccess: (_, { receiptId }) => {
      queryClient.invalidateQueries({ queryKey: ["receipts", receiptId] });
    },
  });
}

/**
 * Email receipt
 */
export function useEmailReceipt() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      receiptId,
      email,
    }: {
      receiptId: string;
      email: string;
    }) => {
      const response = await apiClient.post(`/receipts/${receiptId}/email`, {
        email,
      });
      return response.data;
    },
    onSuccess: (_, { receiptId }) => {
      queryClient.invalidateQueries({ queryKey: ["receipts", receiptId] });
    },
  });
}

/**
 * Download receipt PDF
 */
export function useDownloadReceiptPDF() {
  return useMutation({
    mutationFn: async (receiptId: string) => {
      const response = await apiClient.get(`/receipts/${receiptId}/pdf`, {
        responseType: "blob",
      });
      return response.data;
    },
  });
}
