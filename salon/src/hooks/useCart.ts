import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface CartItem {
  itemType: "service" | "product" | "package";
  itemId: string;
  itemName: string;
  quantity: number;
  unitPrice: number;
  lineTotal: number;
}

export interface Cart {
  id: string;
  customerId?: string;
  staffId: string;
  items: CartItem[];
  subtotal: number;
  taxAmount: number;
  discountAmount: number;
  total: number;
  status: "active" | "completed" | "abandoned";
  createdAt: string;
  updatedAt: string;
}

/**
 * Create a new cart
 */
export function useCreateCart() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: { customerId?: string; staffId: string }) => {
      const response = await apiClient.post<Cart>("/pos/carts", data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["carts"] });
    },
  });
}

/**
 * Get cart by ID
 */
export function useCart(cartId: string) {
  return useQuery({
    queryKey: ["carts", cartId],
    queryFn: async () => {
      const response = await apiClient.get<Cart>(`/pos/carts/${cartId}`);
      return response.data;
    },
    enabled: !!cartId,
  });
}

/**
 * Add item to cart
 */
export function useAddToCart() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      cartId,
      item,
    }: {
      cartId: string;
      item: CartItem;
    }) => {
      const response = await apiClient.post<Cart>(
        `/pos/carts/${cartId}/items`,
        item,
      );
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["carts", data.id] });
    },
  });
}

/**
 * Remove item from cart
 */
export function useRemoveFromCart() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      cartId,
      itemId,
    }: {
      cartId: string;
      itemId: string;
    }) => {
      const response = await apiClient.delete<Cart>(
        `/pos/carts/${cartId}/items/${itemId}`,
      );
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["carts", data.id] });
    },
  });
}

/**
 * Update cart item quantity
 */
export function useUpdateCartItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      cartId,
      itemId,
      quantity,
    }: {
      cartId: string;
      itemId: string;
      quantity: number;
    }) => {
      const response = await apiClient.put<Cart>(
        `/pos/carts/${cartId}/items/${itemId}`,
        { quantity },
      );
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["carts", data.id] });
    },
  });
}

/**
 * Clear cart
 */
export function useClearCart() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (cartId: string) => {
      const response = await apiClient.delete<Cart>(`/pos/carts/${cartId}`);
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["carts", data.id] });
    },
  });
}
