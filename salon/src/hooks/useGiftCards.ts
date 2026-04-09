import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface GiftCard {
  id: string;
  code: string;
  initial_amount: number;
  current_balance: number;
  currency: string;
  purchased_by_name?: string;
  purchased_by_email?: string;
  purchase_date: string;
  recipient_name?: string;
  recipient_email?: string;
  status: "active" | "redeemed" | "expired" | "cancelled";
  expiry_date?: string;
  is_active: boolean;
  delivery_method: "email" | "sms" | "both";
  is_delivered: boolean;
  delivered_at?: string;
  personal_message?: string;
  created_at: string;
  updated_at: string;
}

export interface GiftCardTransaction {
  id: string;
  gift_card_code: string;
  transaction_type: "purchase" | "redemption" | "refund" | "adjustment";
  amount: number;
  balance_before: number;
  balance_after: number;
  description: string;
  created_at: string;
}

export interface GiftCardPurchaseData {
  amount: number;
  purchased_by_name: string;
  purchased_by_email: string;
  purchased_by_phone: string;
  recipient_name?: string;
  recipient_email?: string;
  recipient_phone?: string;
  delivery_method: "email" | "sms" | "both";
  delivery_date?: string;
  personal_message?: string;
  expiry_months?: number;
  payment_method: "paystack" | "cash" | "bank_transfer";
}

export interface GiftCardBalanceResponse {
  code: string;
  current_balance: number;
  currency: string;
  status: string;
  expiry_date?: string;
  is_active: boolean;
}

// Admin hooks
export function useGiftCards(status?: string, page = 1, pageSize = 50) {
  return useQuery({
    queryKey: ["gift-cards", status, page, pageSize],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (status) params.append("status", status);
      params.append("page", page.toString());
      params.append("page_size", pageSize.toString());

      const { data } = await apiClient.get<{
        gift_cards: GiftCard[];
        total: number;
        page: number;
        page_size: number;
      }>(`/gift-cards?${params.toString()}`);
      return data;
    },
  });
}

export function useGiftCard(giftCardId: string | null) {
  return useQuery({
    queryKey: ["gift-card", giftCardId],
    queryFn: async () => {
      if (!giftCardId) return null;
      const { data } = await apiClient.get<GiftCard>(
        `/gift-cards/${giftCardId}`,
      );
      return data;
    },
    enabled: !!giftCardId,
  });
}

export function useGiftCardTransactions(giftCardId: string | null) {
  return useQuery({
    queryKey: ["gift-card-transactions", giftCardId],
    queryFn: async () => {
      if (!giftCardId) return [];
      const { data } = await apiClient.get<GiftCardTransaction[]>(
        `/gift-cards/${giftCardId}/transactions`,
      );
      return data;
    },
    enabled: !!giftCardId,
  });
}

export function useCancelGiftCard() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      giftCardId,
      reason,
    }: {
      giftCardId: string;
      reason: string;
    }) => {
      const { data } = await apiClient.post(
        `/gift-cards/${giftCardId}/cancel`,
        null,
        {
          params: { reason },
        },
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["gift-cards"] });
    },
  });
}

// Public hooks
export function usePurchaseGiftCard() {
  return useMutation({
    mutationFn: async (purchaseData: GiftCardPurchaseData) => {
      const { data } = await apiClient.post<{
        gift_card: GiftCard;
        payment_url?: string;
        message: string;
      }>("/public/gift-cards/purchase", purchaseData);
      return data;
    },
  });
}

export function useCheckGiftCardBalance() {
  return useMutation({
    mutationFn: async (code: string) => {
      const { data } = await apiClient.post<GiftCardBalanceResponse>(
        "/public/gift-cards/check-balance",
        { code },
      );
      return data;
    },
  });
}

export function useRedeemGiftCard() {
  return useMutation({
    mutationFn: async ({
      code,
      amount,
      bookingId,
    }: {
      code: string;
      amount: number;
      bookingId?: string;
    }) => {
      const { data } = await apiClient.post<{
        success: boolean;
        redeemed_amount: number;
        remaining_balance: number;
        gift_card_code: string;
      }>("/public/gift-cards/redeem", {
        code,
        amount,
        booking_id: bookingId,
      });
      return data;
    },
  });
}
