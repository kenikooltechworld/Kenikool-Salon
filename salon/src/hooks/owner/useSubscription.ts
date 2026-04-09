/**
 * Hook for managing subscription and billing.
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { get, post } from "@/lib/utils/api";

export interface PricingPlan {
  id: string;
  name: string;
  tier_level: number;
  description?: string;
  monthly_price: number;
  yearly_price: number;
  currency: string;
  features: Record<string, any>;
  trial_days: number;
  is_featured: boolean;
}

export interface Subscription {
  id: string;
  tenant_id: string;
  plan_name: string;
  plan_tier: number;
  billing_cycle: "monthly" | "yearly";
  status: "trial" | "active" | "past_due" | "canceled" | "expired";
  subscription_status:
    | "trial"
    | "expired_trial"
    | "free_with_fee"
    | "active"
    | "canceled";
  current_period_start: string;
  current_period_end: string;
  next_billing_date: string;
  is_trial: boolean;
  trial_end?: string;
  trial_expiry_action_required: boolean;
  days_until_expiry: number;
  last_payment_date?: string;
  last_payment_amount?: number;
  transaction_fee_percentage: number;
  auto_renew: boolean;
}

/**
 * Hook to fetch current subscription
 */
export function useSubscription() {
  return useQuery({
    queryKey: ["subscription"],
    queryFn: async () => {
      return await get<Subscription>("/billing/subscription");
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Hook to fetch all pricing plans
 */
export function usePricingPlans() {
  return useQuery({
    queryKey: ["pricing-plans"],
    queryFn: async () => {
      return await get<PricingPlan[]>("/billing/plans");
    },
    staleTime: 60 * 60 * 1000, // 1 hour
  });
}

/**
 * Hook to upgrade subscription
 */
export function useUpgradeSubscription() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: {
      plan_id: string;
      billing_cycle: "monthly" | "yearly";
    }) => {
      return await post<Subscription>("/billing/upgrade", data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["subscription"] });
    },
  });
}

/**
 * Hook to downgrade subscription
 */
export function useDowngradeSubscription() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: {
      plan_id: string;
      billing_cycle: "monthly" | "yearly";
    }) => {
      return await post<Subscription>("/billing/downgrade", data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["subscription"] });
    },
  });
}

/**
 * Hook to cancel subscription
 */
export function useCancelSubscription() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      return await post<Subscription>("/billing/cancel");
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["subscription"] });
    },
  });
}

/**
 * Hook to check if a feature is available
 */
export function useFeatureAvailable(featureName: string) {
  const { data: subscription, isLoading } = useSubscription();
  const { data: plans } = usePricingPlans();

  if (isLoading || !subscription || !plans) {
    return { available: false, isLoading: true };
  }

  const plan = plans.find((p) => p.id === subscription.plan_name);
  if (!plan) {
    return { available: false, isLoading: false };
  }

  const available = plan.features[featureName] === true;
  return { available, isLoading: false };
}

/**
 * Hook to get remaining days in trial
 */
export function useTrialDaysRemaining() {
  const { data: subscription } = useSubscription();

  if (!subscription || !subscription.is_trial) {
    return null;
  }

  return subscription.days_until_expiry;
}

/**
 * Hook to check if subscription is active
 */
export function useIsSubscriptionActive() {
  const { data: subscription } = useSubscription();

  if (!subscription) {
    return false;
  }

  return subscription.status === "active" || subscription.status === "trial";
}
