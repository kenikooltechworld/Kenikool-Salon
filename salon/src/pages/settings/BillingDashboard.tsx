import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  useSubscription,
  usePricingPlans,
  useUpgradeSubscription,
  useDowngradeSubscription,
  useCancelSubscription,
} from "@/hooks/useSubscription";
import { AlertCircleIcon, CheckIcon, Loader2Icon } from "@/components/icons";

export function BillingDashboard() {
  const { data: subscription, isLoading: subLoading } = useSubscription();
  const { data: plans, isLoading: plansLoading } = usePricingPlans();
  const upgrade = useUpgradeSubscription();
  const downgrade = useDowngradeSubscription();
  const cancel = useCancelSubscription();
  const navigate = useNavigate();
  const [billingCycle, setBillingCycle] = useState<"monthly" | "yearly">(
    "monthly",
  );

  if (subLoading || plansLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2Icon className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  if (!subscription || !plans) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center gap-2">
          <AlertCircleIcon className="w-5 h-5 text-red-600" />
          <p className="text-red-800">
            Failed to load subscription information
          </p>
        </div>
      </div>
    );
  }

  const currentPlan = plans.find(
    (p: any) => p.tier_level === subscription.plan_tier,
  );
  const isTrialExpiring =
    subscription.is_trial && subscription.days_until_expiry <= 7;
  const isTrialExpired = subscription.trial_expiry_action_required;

  const handleUpgrade = async (planId: string) => {
    try {
      if (isTrialExpired) {
        await upgrade.mutateAsync({
          plan_id: planId,
          billing_cycle: billingCycle,
        });
      } else {
        await upgrade.mutateAsync({
          plan_id: planId,
          billing_cycle: billingCycle,
        });
      }
    } catch (error) {
      console.error("Upgrade failed:", error);
    }
  };

  const handleContinueFree = async () => {
    try {
      // Call continue-free endpoint
      const response = await fetch("/api/v1/billing/continue-free", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });
      if (response.ok) {
        window.location.reload();
      }
    } catch (error) {
      console.error("Continue free failed:", error);
    }
  };

  const handleDowngrade = async (planId: string) => {
    if (confirm("Downgrading will reduce your features. Continue?")) {
      try {
        await downgrade.mutateAsync({
          plan_id: planId,
          billing_cycle: billingCycle,
        });
      } catch (error) {
        console.error("Downgrade failed:", error);
      }
    }
  };

  const handleCancel = async () => {
    if (confirm("Are you sure you want to cancel your subscription?")) {
      try {
        await cancel.mutateAsync();
      } catch (error) {
        console.error("Cancellation failed:", error);
      }
    }
  };

  return (
    <div className="space-y-8">
      {/* Back Button */}
      <button
        onClick={() => navigate("/settings")}
        className="text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        ← Back to Settings
      </button>

      {/* Current Plan Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold mb-4">Current Plan</h2>

        {isTrialExpired && (
          <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800 font-semibold mb-3">
              ⚠️ Your trial has expired. Choose an option below:
            </p>
            <div className="flex gap-2">
              <button
                onClick={handleContinueFree}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Continue Free (10% fee)
              </button>
              <button
                onClick={() => {
                  const paidPlan = plans.find((p: any) => p.tier_level > 0);
                  if (paidPlan) handleUpgrade(paidPlan.id);
                }}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                Upgrade to Paid Plan
              </button>
            </div>
          </div>
        )}

        {isTrialExpiring && !isTrialExpired && (
          <div className="mb-4 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <p className="text-yellow-800">
              ⚠️ Your trial expires in {subscription.days_until_expiry} days.
              Upgrade now to continue using all features.
            </p>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-lg font-semibold mb-2">{currentPlan?.name}</h3>
            <p className="text-gray-600 mb-4">{currentPlan?.description}</p>

            <div className="space-y-2 text-sm">
              <p>
                <span className="font-medium">Status:</span>{" "}
                <span
                  className={`px-2 py-1 rounded ${subscription.status === "active" ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}
                >
                  {subscription.status}
                </span>
              </p>
              <p>
                <span className="font-medium">Subscription Status:</span>{" "}
                <span className="px-2 py-1 rounded bg-blue-100 text-blue-800">
                  {subscription.subscription_status}
                </span>
              </p>
              {subscription.transaction_fee_percentage > 0 && (
                <p>
                  <span className="font-medium">Transaction Fee:</span>{" "}
                  <span className="text-orange-600 font-semibold">
                    {subscription.transaction_fee_percentage}%
                  </span>
                </p>
              )}
              <p>
                <span className="font-medium">Billing Cycle:</span>{" "}
                {subscription.billing_cycle}
              </p>
              <p>
                <span className="font-medium">Current Period:</span>{" "}
                {new Date(
                  subscription.current_period_start,
                ).toLocaleDateString()}{" "}
                -{" "}
                {new Date(subscription.current_period_end).toLocaleDateString()}
              </p>
              <p>
                <span className="font-medium">Days Remaining:</span>{" "}
                {subscription.days_until_expiry}
              </p>
              {subscription.last_payment_date && (
                <p>
                  <span className="font-medium">Last Payment:</span>{" "}
                  {new Date(
                    subscription.last_payment_date,
                  ).toLocaleDateString()}{" "}
                  ({subscription.last_payment_amount} NGN)
                </p>
              )}
            </div>
          </div>

          <div>
            <h4 className="font-semibold mb-3">Features Included</h4>
            <div className="space-y-2">
              {currentPlan?.features && (
                <>
                  <div className="flex items-center gap-2">
                    <CheckIcon className="w-4 h-4 text-green-600" />
                    <span className="text-sm">
                      Up to {currentPlan.features.max_staff_count} staff members
                    </span>
                  </div>
                  {currentPlan.features.has_pos && (
                    <div className="flex items-center gap-2">
                      <CheckIcon className="w-4 h-4 text-green-600" />
                      <span className="text-sm">POS System</span>
                    </div>
                  )}
                  {currentPlan.features.has_api_access && (
                    <div className="flex items-center gap-2">
                      <CheckIcon className="w-4 h-4 text-green-600" />
                      <span className="text-sm">API Access</span>
                    </div>
                  )}
                  {currentPlan.features.has_advanced_reports && (
                    <div className="flex items-center gap-2">
                      <CheckIcon className="w-4 h-4 text-green-600" />
                      <span className="text-sm">Advanced Reports</span>
                    </div>
                  )}
                  {currentPlan.features.has_multi_location && (
                    <div className="flex items-center gap-2">
                      <CheckIcon className="w-4 h-4 text-green-600" />
                      <span className="text-sm">Multi-Location Support</span>
                    </div>
                  )}
                  {currentPlan.features.has_white_label && (
                    <div className="flex items-center gap-2">
                      <CheckIcon className="w-4 h-4 text-green-600" />
                      <span className="text-sm">White-Label</span>
                    </div>
                  )}
                  <div className="flex items-center gap-2">
                    <CheckIcon className="w-4 h-4 text-green-600" />
                    <span className="text-sm">
                      {currentPlan.features.support_level} Support
                    </span>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>

        <div className="mt-6 flex gap-2">
          <button
            onClick={handleCancel}
            disabled={cancel.isPending}
            className="px-4 py-2 text-red-600 border border-red-300 rounded-lg hover:bg-red-50 disabled:opacity-50"
          >
            {cancel.isPending ? "Canceling..." : "Cancel Subscription"}
          </button>
        </div>
      </div>

      {/* Billing Cycle Toggle */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Billing Cycle</h3>
        <div className="flex gap-4">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="radio"
              value="monthly"
              checked={billingCycle === "monthly"}
              onChange={(e) =>
                setBillingCycle(e.target.value as "monthly" | "yearly")
              }
              className="w-4 h-4"
            />
            <span>Monthly</span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="radio"
              value="yearly"
              checked={billingCycle === "yearly"}
              onChange={(e) =>
                setBillingCycle(e.target.value as "monthly" | "yearly")
              }
              className="w-4 h-4"
            />
            <span>Yearly (20% discount)</span>
          </label>
        </div>
      </div>

      {/* Pricing Plans */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Available Plans</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {plans.map((plan: any) => (
            <div
              key={plan.id}
              className={`border rounded-lg p-4 ${
                plan.id === currentPlan?.id
                  ? "border-blue-500 bg-blue-50"
                  : "border-gray-200"
              } ${plan.is_featured ? "ring-2 ring-blue-500" : ""}`}
            >
              {plan.is_featured && (
                <div className="text-xs font-semibold text-blue-600 mb-2">
                  RECOMMENDED
                </div>
              )}

              <h4 className="font-semibold text-lg mb-2">{plan.name}</h4>
              <p className="text-sm text-gray-600 mb-3">{plan.description}</p>

              <div className="mb-4">
                <div className="text-2xl font-bold">
                  {billingCycle === "monthly"
                    ? plan.monthly_price
                    : plan.yearly_price}
                  <span className="text-sm font-normal text-gray-600">
                    {" "}
                    {plan.currency}
                  </span>
                </div>
                <p className="text-xs text-gray-500">per {billingCycle}</p>
              </div>

              <div className="mb-4 space-y-1 text-sm">
                <p>
                  <span className="font-medium">
                    {plan.features.max_staff_count}
                  </span>{" "}
                  staff members
                </p>
                {plan.features.has_pos && <p>✓ POS System</p>}
                {plan.features.has_api_access && <p>✓ API Access</p>}
                {plan.features.has_advanced_reports && (
                  <p>✓ Advanced Reports</p>
                )}
                {plan.features.has_multi_location && <p>✓ Multi-Location</p>}
                {plan.features.has_white_label && <p>✓ White-Label</p>}
              </div>

              {plan.id === currentPlan?.id ? (
                <button
                  disabled
                  className="w-full py-2 bg-gray-200 text-gray-600 rounded-lg font-medium"
                >
                  Current Plan
                </button>
              ) : plan.tier_level > subscription.plan_tier ? (
                <button
                  onClick={() => handleUpgrade(plan.id)}
                  disabled={upgrade.isPending}
                  className="w-full py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50"
                >
                  {upgrade.isPending ? "Upgrading..." : "Upgrade"}
                </button>
              ) : (
                <button
                  onClick={() => handleDowngrade(plan.id)}
                  disabled={downgrade.isPending}
                  className="w-full py-2 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300 disabled:opacity-50"
                >
                  {downgrade.isPending ? "Downgrading..." : "Downgrade"}
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
