import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface InvoiceLineItem {
  service_id: string;
  service_name: string;
  quantity: number;
  unit_price: number;
  total: number;
}

export interface Invoice {
  id: string;
  appointment_id?: string;
  customer_id: string;
  line_items: InvoiceLineItem[];
  subtotal: number;
  tax: number;
  discount: number;
  total: number;
  status: "draft" | "issued" | "paid" | "cancelled";
  due_date: string;
  paid_at?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

interface InvoiceFilters {
  status?: string;
  customerId?: string;
  startDate?: string;
  endDate?: string;
}

/**
 * Fetch all invoices with optional filters
 */
export function useInvoices(filters?: InvoiceFilters) {
  return useQuery({
    queryKey: ["invoices", filters],
    queryFn: async () => {
      const { data } = await apiClient.get<{ data: Invoice[] }>("/invoices", {
        params: filters,
      });
      return data.data || [];
    },
  });
}

/**
 * Fetch single invoice by ID
 */
export function useInvoice(id: string) {
  return useQuery({
    queryKey: ["invoices", id],
    queryFn: async () => {
      const { data } = await apiClient.get<{ data: Invoice }>(
        `/invoices/${id}`,
      );
      return data.data;
    },
    enabled: !!id,
  });
}

/**
 * Create new invoice
 */
export function useCreateInvoice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (invoice: {
      customer_id: string;
      line_items: Array<{
        service_id: string;
        service_name: string;
        quantity: number;
        unit_price: number;
      }>;
      discount?: number;
      tax?: number;
      notes?: string;
      due_date?: string;
    }) => {
      const { data } = await apiClient.post<{ data: Invoice }>(
        "/invoices",
        invoice,
      );
      return data.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["invoices"] });
    },
  });
}

/**
 * Update invoice
 */
export function useUpdateInvoice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      id,
      ...updates
    }: Partial<Invoice> & { id: string }) => {
      const { data } = await apiClient.put<{ data: Invoice }>(
        `/invoices/${id}`,
        updates,
      );
      return data.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["invoices"] });
      queryClient.invalidateQueries({ queryKey: ["invoices", data.id] });
    },
  });
}

/**
 * Delete invoice
 */
export function useDeleteInvoice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/invoices/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["invoices"] });
    },
  });
}
