import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface InvoiceLineItem {
  serviceId: string;
  serviceName: string;
  quantity: number;
  unitPrice: number;
  total: number;
}

export interface Invoice {
  id: string;
  appointmentId?: string;
  customerId: string;
  lineItems: InvoiceLineItem[];
  subtotal: number;
  tax: number;
  discount: number;
  total: number;
  status: "draft" | "issued" | "paid" | "cancelled";
  dueDate: string;
  paidAt?: string;
  notes?: string;
  createdAt: string;
  updatedAt: string;
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
      const response = await apiClient.get<{
        invoices: Invoice[];
        total: number;
        page: number;
        page_size: number;
      }>("/invoices", {
        params: filters,
      });
      return response.data.invoices || [];
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
      const response = await apiClient.get<Invoice>(`/invoices/${id}`);
      const inv = response.data;
      return {
        id: inv.id,
        appointmentId: inv.appointment_id,
        customerId: inv.customer_id,
        lineItems: (inv.line_items || []).map((item: any) => ({
          serviceId: item.service_id,
          serviceName: item.service_name,
          quantity: item.quantity,
          unitPrice: item.unit_price,
          total: item.total,
        })),
        subtotal: inv.subtotal,
        tax: inv.tax,
        discount: inv.discount,
        total: inv.total,
        status: inv.status,
        dueDate: inv.due_date,
        paidAt: inv.paid_at,
        notes: inv.notes,
        createdAt: inv.created_at,
        updatedAt: inv.updated_at,
      } as Invoice;
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
      customerId: string;
      lineItems: Array<{
        serviceId: string;
        serviceName: string;
        quantity: number;
        unitPrice: number;
      }>;
      discount?: number;
      tax?: number;
      notes?: string;
      appointmentId?: string;
    }) => {
      // Transform camelCase to snake_case for API
      const payload = {
        customer_id: invoice.customerId,
        line_items: invoice.lineItems.map((item) => ({
          service_id: item.serviceId,
          service_name: item.serviceName,
          quantity: item.quantity,
          unit_price: item.unitPrice,
        })),
        discount: invoice.discount,
        tax: invoice.tax,
        notes: invoice.notes,
        appointment_id: invoice.appointmentId,
      };
      const response = await apiClient.post<Invoice>("/invoices", payload);
      const inv = response.data;
      return {
        id: inv.id,
        appointmentId: inv.appointment_id,
        customerId: inv.customer_id,
        lineItems: (inv.line_items || []).map((item: any) => ({
          serviceId: item.service_id,
          serviceName: item.service_name,
          quantity: item.quantity,
          unitPrice: item.unit_price,
          total: item.total,
        })),
        subtotal: inv.subtotal,
        tax: inv.tax,
        discount: inv.discount,
        total: inv.total,
        status: inv.status,
        dueDate: inv.due_date,
        paidAt: inv.paid_at,
        notes: inv.notes,
        createdAt: inv.created_at,
        updatedAt: inv.updated_at,
      } as Invoice;
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
      // Transform camelCase to snake_case for API
      // Only send fields that the backend accepts
      const payload: any = {};
      if (updates.status) payload.status = updates.status;
      if (updates.discount !== undefined) payload.discount = updates.discount;
      if (updates.tax !== undefined) payload.tax = updates.tax;
      if (updates.notes !== undefined) payload.notes = updates.notes;

      const response = await apiClient.put<Invoice>(`/invoices/${id}`, payload);
      const inv = response.data;
      return {
        id: inv.id,
        appointmentId: inv.appointment_id,
        customerId: inv.customer_id,
        lineItems: (inv.line_items || []).map((item: any) => ({
          serviceId: item.service_id,
          serviceName: item.service_name,
          quantity: item.quantity,
          unitPrice: item.unit_price,
          total: item.total,
        })),
        subtotal: inv.subtotal,
        tax: inv.tax,
        discount: inv.discount,
        total: inv.total,
        status: inv.status,
        dueDate: inv.due_date,
        paidAt: inv.paid_at,
        notes: inv.notes,
        createdAt: inv.created_at,
        updatedAt: inv.updated_at,
      } as Invoice;
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

/**
 * Issue invoice (change status from draft to issued)
 */
export function useIssueInvoice() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (invoiceId: string) => {
      const response = await apiClient.post<Invoice>(`/invoices/${invoiceId}/issue`);
      const inv = response.data;
      return {
        id: inv.id,
        appointmentId: inv.appointment_id,
        customerId: inv.customer_id,
        lineItems: (inv.line_items || []).map((item: any) => ({
          serviceId: item.service_id,
          serviceName: item.service_name,
          quantity: item.quantity,
          unitPrice: item.unit_price,
          total: item.total,
        })),
        subtotal: inv.subtotal,
        tax: inv.tax,
        discount: inv.discount,
        total: inv.total,
        status: inv.status,
        dueDate: inv.due_date,
        paidAt: inv.paid_at,
        notes: inv.notes,
        createdAt: inv.created_at,
        updatedAt: inv.updated_at,
      } as Invoice;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["invoices"] });
      queryClient.invalidateQueries({ queryKey: ["invoices", data.id] });
    },
  });
}

/**
 * Mark invoice as paid
 */
export function useMarkInvoicePaid() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (invoiceId: string) => {
      const response = await apiClient.post<Invoice>(`/invoices/${invoiceId}/mark-paid`);
      const inv = response.data;
      return {
        id: inv.id,
        appointmentId: inv.appointment_id,
        customerId: inv.customer_id,
        lineItems: (inv.line_items || []).map((item: any) => ({
          serviceId: item.service_id,
          serviceName: item.service_name,
          quantity: item.quantity,
          unitPrice: item.unit_price,
          total: item.total,
        })),
        subtotal: inv.subtotal,
        tax: inv.tax,
        discount: inv.discount,
        total: inv.total,
        status: inv.status,
        dueDate: inv.due_date,
        paidAt: inv.paid_at,
        notes: inv.notes,
        createdAt: inv.created_at,
        updatedAt: inv.updated_at,
      } as Invoice;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["invoices"] });
      queryClient.invalidateQueries({ queryKey: ["invoices", data.id] });
    },
  });
}
