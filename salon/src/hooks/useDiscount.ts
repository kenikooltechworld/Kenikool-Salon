import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface Discount {
  id: string;
  discountCode: string;
  discountType: "percentage" | "fixed" | "loyalty" | "bulk";
  discountValue: number;
  applicableTo: "transaction" | "item" | "service" | "product";
  conditions?: Record<string, any>;
  maxDiscount?: number;
  active: boolean;
  validFrom?: string;
  validUntil?: string;
  usageCount: number;
  usageLimit?: number;
  createdAt: string;
  updatedAt: string;
}

/**
 * Create a discount
 */
export function useCreateDiscount() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: {
      discountCode: string;
      discountType: string;
      discountValue: number;
      applicableTo?: string;
      conditions?: Record<string, any>;
      maxDiscount?: number;
      validFrom?: string;
      validUntil?: string;
      usageLimit?: number;
    }) => {
      const response = await apiClient.post<Discount>("/discounts", data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["discounts"] });
    },
  });
}

/**
 * List discounts
 */
export function useDiscounts(filters?: {
  activeOnly?: boolean;
  page?: number;
  pageSize?: number;
}) {
  return useQuery({
    queryKey: ["discounts", filters],
    queryFn: async () => {
      const response = await apiClient.get<{
        discounts: Discount[];
        total: number;
        page: number;
        pageSize: number;
      }>("/discounts", { params: filters });
      return response.data;
    },
  });
}

/**
 * Validate discount code
 */
export function useValidateDiscount() {
  return useMutation({
    mutationFn: async ({
      discountCode,
      subtotal,
    }: {
      discountCode: string;
      subtotal: number;
    }) => {
      const response = await apiClient.post<{
        valid: boolean;
        discountAmount: number;
        message: string;
      }>("/discounts/validate", {
        discountCode,
        subtotal,
      });
      return response.data;
    },
  });
}

/**
 * Apply discount to transaction
 */
export function useApplyDiscount() {
  return useMutation({
    mutationFn: async ({
      discountCode,
      subtotal,
    }: {
      discountCode: string;
      subtotal: number;
    }) => {
      const response = await apiClient.post<{
        success: boolean;
        discountAmount: number;
        message: string;
      }>("/discounts/apply", {
        discountCode,
        subtotal,
      });
      return response.data;
    },
  });
}

/**
 * Update discount
 */
export function useUpdateDiscount() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      discountId,
      data,
    }: {
      discountId: string;
      data: {
        discountValue?: number;
        active?: boolean;
        validUntil?: string;
        usageLimit?: number;
      };
    }) => {
      const response = await apiClient.put<Discount>(
        `/discounts/${discountId}`,
        data,
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["discounts"] });
    },
  });
}
