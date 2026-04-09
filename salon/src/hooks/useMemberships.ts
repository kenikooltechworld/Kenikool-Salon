import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export interface MembershipBenefit {
  benefit_type: string;
  description: string;
  value?: string;
}

export interface MembershipTier {
  id: string;
  name: string;
  description?: string;
  monthly_price: number;
  annual_price?: number;
  billing_cycle: string;
  discount_percentage: number;
  priority_booking: boolean;
  exclusive_services: string[];
  free_services_per_month: number;
  rollover_unused: boolean;
  benefits: MembershipBenefit[];
  max_members?: number;
  display_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Membership {
  id: string;
  customer_id: string;
  tier_id: string;
  tier_name: string;
  status: string;
  start_date: string;
  end_date?: string;
  next_billing_date: string;
  last_payment_date?: string;
  last_payment_amount?: number;
  services_used_this_cycle: number;
  services_remaining_this_cycle: number;
  rollover_services: number;
  created_at: string;
  updated_at: string;
}

export interface MembershipTransaction {
  id: string;
  membership_id: string;
  customer_id: string;
  transaction_type: string;
  amount: number;
  status: string;
  payment_method?: string;
  description?: string;
  created_at: string;
}

// Admin hooks
export function useMembershipTiers() {
  return useQuery({
    queryKey: ["membership-tiers"],
    queryFn: async () => {
      const { data } =
        await apiClient.get<MembershipTier[]>("/memberships/tiers");
      return data;
    },
  });
}

export function useCreateMembershipTier() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (tierData: Partial<MembershipTier>) => {
      const { data } = await apiClient.post<MembershipTier>(
        "/memberships/tiers",
        tierData,
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["membership-tiers"] });
    },
  });
}

export function useUpdateMembershipTier() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      tierId,
      tierData,
    }: {
      tierId: string;
      tierData: Partial<MembershipTier>;
    }) => {
      const { data } = await apiClient.put<MembershipTier>(
        `/memberships/tiers/${tierId}`,
        tierData,
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["membership-tiers"] });
    },
  });
}

export function useDeleteMembershipTier() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (tierId: string) => {
      await apiClient.delete(`/memberships/tiers/${tierId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["membership-tiers"] });
    },
  });
}

export function useCreateMembershipSubscription() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (subscriptionData: {
      customer_id: string;
      tier_id: string;
      payment_method_id?: string;
      start_date?: string;
    }) => {
      const { data } = await apiClient.post<Membership>(
        "/memberships/subscriptions",
        subscriptionData,
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["memberships"] });
    },
  });
}

export function useCustomerMembership(customerId: string) {
  return useQuery({
    queryKey: ["customer-membership", customerId],
    queryFn: async () => {
      const { data } = await apiClient.get<Membership>(
        `/memberships/subscriptions/customer/${customerId}`,
      );
      return data;
    },
    enabled: !!customerId,
  });
}

export function usePauseMembership() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      membershipId,
      reason,
    }: {
      membershipId: string;
      reason: string;
    }) => {
      await apiClient.post(
        `/memberships/subscriptions/${membershipId}/pause`,
        null,
        {
          params: { pause_reason: reason },
        },
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["memberships"] });
      queryClient.invalidateQueries({ queryKey: ["customer-membership"] });
    },
  });
}

export function useResumeMembership() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (membershipId: string) => {
      await apiClient.post(`/memberships/subscriptions/${membershipId}/resume`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["memberships"] });
      queryClient.invalidateQueries({ queryKey: ["customer-membership"] });
    },
  });
}

export function useCancelMembership() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      membershipId,
      reason,
    }: {
      membershipId: string;
      reason: string;
    }) => {
      await apiClient.post(
        `/memberships/subscriptions/${membershipId}/cancel`,
        null,
        {
          params: { cancellation_reason: reason },
        },
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["memberships"] });
      queryClient.invalidateQueries({ queryKey: ["customer-membership"] });
    },
  });
}

export function useMembershipTransactions(membershipId: string) {
  return useQuery({
    queryKey: ["membership-transactions", membershipId],
    queryFn: async () => {
      const { data } = await apiClient.get<MembershipTransaction[]>(
        `/memberships/subscriptions/${membershipId}/transactions`,
      );
      return data;
    },
    enabled: !!membershipId,
  });
}

export function useAllMemberships(filters?: {
  status?: string;
  tier_id?: string;
  limit?: number;
  skip?: number;
}) {
  return useQuery({
    queryKey: ["all-memberships", filters],
    queryFn: async () => {
      const { data } = await apiClient.get<Membership[]>(
        "/memberships/subscriptions",
        { params: filters },
      );
      return data;
    },
  });
}

export function useMembershipStats() {
  return useQuery({
    queryKey: ["membership-stats"],
    queryFn: async () => {
      const { data } = await apiClient.get<{
        total_active: number;
        total_paused: number;
        total_cancelled: number;
        monthly_revenue: number;
        total_members: number;
      }>("/memberships/stats");
      return data;
    },
  });
}

// Public/Customer hooks
export function usePublicMembershipTiers() {
  return useQuery({
    queryKey: ["public-membership-tiers"],
    queryFn: async () => {
      const { data } = await apiClient.get<MembershipTier[]>(
        "/public/memberships/tiers",
      );
      return data;
    },
  });
}

export function useSubscribeToMembership() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (subscriptionData: {
      customer_id: string;
      tier_id: string;
      payment_method_id?: string;
    }) => {
      const { data } = await apiClient.post<Membership>(
        "/public/memberships/subscribe",
        subscriptionData,
      );
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["my-membership"] });
    },
  });
}

export function useMyMembership() {
  return useQuery({
    queryKey: ["my-membership"],
    queryFn: async () => {
      const { data } = await apiClient.get<Membership>(
        "/public/memberships/my-membership",
      );
      return data;
    },
  });
}

export function usePauseMyMembership() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (reason: string) => {
      await apiClient.post("/public/memberships/my-membership/pause", null, {
        params: { pause_reason: reason },
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["my-membership"] });
    },
  });
}

export function useCancelMyMembership() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (reason: string) => {
      await apiClient.post("/public/memberships/my-membership/cancel", null, {
        params: { cancellation_reason: reason },
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["my-membership"] });
    },
  });
}

export function useMyMembershipTransactions() {
  return useQuery({
    queryKey: ["my-membership-transactions"],
    queryFn: async () => {
      const { data } = await apiClient.get<MembershipTransaction[]>(
        "/public/memberships/my-membership/transactions",
      );
      return data;
    },
  });
}
