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
      const { data } = await apiClient.get<any[]>("/invoices", {
        params: filters,
      });
      const invoices = Array.isArray(data) ? data : [];
      return invoices.map((inv: any) => ({
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
      }));
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
      const { data } = await apiClient.get<any>(`/invoices/${id}`);
      return {
        id: data.id,
        appointmentId: data.appointment_id,
        customerId: data.customer_id,
        lineItems: (data.line_items || []).map((item: any) => ({
          serviceId: item.service_id,
          serviceName: item.service_name,
          quantity: item.quantity,
          unitPrice: item.unit_price,
          total: item.total,
        })),
        subtotal: data.subtotal,
        tax: data.tax,
        discount: data.discount,
        total: data.total,
        status: data.status,
        dueDate: data.due_date,
        paidAt: data.paid_at,
        notes: data.notes,
        createdAt: data.created_at,
        updatedAt: data.updated_at,
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
      dueDate?: string;
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
        due_date: invoice.dueDate,
      };
      const { data } = await apiClient.post<any>("/invoices", payload);
      // Transform response back to camelCase
      return {
        id: data.id,
        appointmentId: data.appointment_id,
        customerId: data.customer_id,
        lineItems: (data.line_items || []).map((item: any) => ({
          serviceId: item.service_id,
          serviceName: item.service_name,
          quantity: item.quantity,
          unitPrice: item.unit_price,
          total: item.total,
        })),
        subtotal: data.subtotal,
        tax: data.tax,
        discount: data.discount,
        total: data.total,
        status: data.status,
        dueDate: data.due_date,
        paidAt: data.paid_at,
        notes: data.notes,
        createdAt: data.created_at,
        updatedAt: data.updated_at,
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
      const payload: any = {};
      if (updates.customerId) payload.customer_id = updates.customerId;
      if (updates.appointmentId) payload.appointment_id = updates.appointmentId;
      if (updates.lineItems) {
        payload.line_items = updates.lineItems.map((item) => ({
          service_id: item.serviceId,
          service_name: item.serviceName,
          quantity: item.quantity,
          unit_price: item.unitPrice,
        }));
      }
      if (updates.subtotal !== undefined) payload.subtotal = updates.subtotal;
      if (updates.tax !== undefined) payload.tax = updates.tax;
      if (updates.discount !== undefined) payload.discount = updates.discount;
      if (updates.total !== undefined) payload.total = updates.total;
      if (updates.status) payload.status = updates.status;
      if (updates.dueDate) payload.due_date = updates.dueDate;
      if (updates.paidAt) payload.paid_at = updates.paidAt;
      if (updates.notes !== undefined) payload.notes = updates.notes;

      const { data } = await apiClient.put<any>(`/invoices/${id}`, payload);
      // Transform response back to camelCase
      return {
        id: data.id,
        appointmentId: data.appointment_id,
        customerId: data.customer_id,
        lineItems: (data.line_items || []).map((item: any) => ({
          serviceId: item.service_id,
          serviceName: item.service_name,
          quantity: item.quantity,
          unitPrice: item.unit_price,
          total: item.total,
        })),
        subtotal: data.subtotal,
        tax: data.tax,
        discount: data.discount,
        total: data.total,
        status: data.status,
        dueDate: data.due_date,
        paidAt: data.paid_at,
        notes: data.notes,
        createdAt: data.created_at,
        updatedAt: data.updated_at,
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
