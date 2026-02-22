import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Modal,
  ModalHeader,
  ModalTitle,
  ModalDescription,
  ModalBody,
  ModalFooter,
} from "@/components/ui/modal";
import { Spinner } from "@/components/ui/spinner";
import {
  CreditCardIcon,
  CheckIcon,
  AlertTriangleIcon,
} from "@/components/icons";
import { useTenant } from "@/lib/api/hooks/useTenant";
import {
  useCurrentSubscription,
  useUpgradeSubscription,
  useCancelSubscription,
  usePaymentMethods,
  useBillingHistory,
} from "@/lib/api/hooks/useSubscriptions";
import { UsageDashboard } from "@/components/subscriptions/usage-dashboard";

type BillingCycle = "monthly" | "yearly";

export default function BillingSettingsPage() {
  const { data: tenant } = useTenant();
  const { data: subscription, isLoading: subLoading } =
    useCurrentSubscription();
  const { data: paymentMethods } = usePaymentMethods();
  const { data: billingHistory } = useBillingHistory();
  const upgradeMutation = useUpgradeSubscription();
  const cancelMutation = useCancelSubscription();

  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [showHistoryModal, setShowHistoryModal] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null);
  const [billingCycle, setBillingCycle] = useState<BillingCycle>("monthly");

  const plans = [
    {
      id: "free",
      name: "FREE",
      monthlyPrice: 0,
      yearlyPrice: 0,
      features: [
        "1 staff user",
        "50 bookings per month",
        "100 clients maximum",
        "Basic appointment booking",
        "Service catalog (up to 10)",
        "Basic calendar view",
        "Basic POS (online only)",
        "Cash payments only",
        "Email support (48-72h)",
      ],
      limits: "Powered by watermark • No offline POS",
      current: tenant?.subscription_plan === "free",
    },
    {
      id: "starter",
      name: "STARTER",
      monthlyPrice: 15000,
      yearlyPrice: 12750, // 15% discount
      features: [
        "1-3 staff users",
        "Unlimited bookings",
        "500 clients",
        "100 SMS/month included",
        "Offline POS (works without internet)",
        "Multiple payment methods",
        "Paystack/Flutterwave integration",
        "Digital receipts",
        "Basic reporting",
        "Online booking widget",
      ],
      current: tenant?.subscription_plan === "starter",
    },
    {
      id: "professional",
      name: "PROFESSIONAL",
      monthlyPrice: 35000,
      yearlyPrice: 29750, // 15% discount
      features: [
        "4-10 staff users",
        "Unlimited bookings",
        "2,000 clients",
        "500 SMS/month included",
        "Advanced POS (split payments, discounts)",
        "Inventory management",
        "Staff scheduling & commissions",
        "Loyalty program",
        "SMS & Email campaigns",
        "Group bookings (up to 5)",
        "Advanced analytics",
      ],
      current: tenant?.subscription_plan === "professional",
      popular: true,
    },
    {
      id: "business",
      name: "BUSINESS",
      monthlyPrice: 65000,
      yearlyPrice: 55250, // 15% discount
      features: [
        "11-25 staff users",
        "Unlimited bookings & clients",
        "2,000 SMS/month included",
        "Advanced accounting (P&L, invoices)",
        "Expense management",
        "Packages & memberships",
        "Advanced campaigns & automation",
        "Group bookings (up to 20)",
        "Predictive analytics",
        "QuickBooks integration",
        "Custom domain support",
      ],
      current: tenant?.subscription_plan === "business",
    },
    {
      id: "enterprise",
      name: "ENTERPRISE",
      monthlyPrice: 120000,
      yearlyPrice: 102000, // 15% discount
      features: [
        "26-50 staff users",
        "Unlimited everything",
        "5,000 SMS/month included",
        "White-label platform",
        "Multi-location (3 locations)",
        "Full API access",
        "Advanced integrations",
        "Dedicated account manager",
        "2FA & advanced security",
        "Franchise management",
        "24/7 support",
      ],
      current: tenant?.subscription_plan === "enterprise",
    },
    {
      id: "unlimited",
      name: "UNLIMITED",
      monthlyPrice: 250000,
      yearlyPrice: 212500, // 15% discount
      features: [
        "Unlimited staff & locations",
        "Unlimited SMS & communications",
        "White-label reseller rights",
        "Custom development (40hrs/year)",
        "99.9% uptime SLA",
        "AI-powered insights",
        "Dedicated technical team",
        "1-hour response time",
        "On-site training",
        "Custom integrations",
        "On-premise deployment option",
      ],
      current: tenant?.subscription_plan === "unlimited",
    },
  ];

  const getPrice = (plan: (typeof plans)[0]) => {
    const price =
      billingCycle === "monthly" ? plan.monthlyPrice : plan.yearlyPrice;
    const period = billingCycle === "monthly" ? "/month" : "/year";
    return { price, period };
  };

  const handleUpgrade = (planId: string) => {
    setSelectedPlan(planId);
    setShowUpgradeModal(true);
  };

  const confirmUpgrade = async () => {
    if (!selectedPlan) return;

    try {
      const result = await upgradeMutation.mutateAsync({
        plan_id: selectedPlan,
        payment_method: "paystack",
      });

      if (result.authorization_url) {
        window.location.href = result.authorization_url;
      } else {
        setShowUpgradeModal(false);
        showToast("Plan updated successfully!", "success");
      }
    } catch (error: any) {
      showToast(
        error?.response?.data?.detail || "Failed to upgrade plan",
        "error",
      );
    }
  };

  const handleCancelSubscription = async () => {
    try {
      await cancelMutation.mutateAsync(false);
      setShowCancelModal(false);
      showToast(
        "Subscription will be cancelled at the end of billing period",
        "success",
      );
    } catch (error: any) {
      showToast(
        error?.response?.data?.detail || "Failed to cancel subscription",
        "error",
      );
    }
  };

  if (subLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-6xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground">
          Billing & Subscription
        </h1>
        <p className="text-muted-foreground">
          Manage your subscription and payment methods
        </p>
      </div>

      {/* Usage Dashboard - Show for active subscriptions */}
      {subscription?.status === "active" && <UsageDashboard />}

      {/* Current Plan */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-semibold text-foreground">
              Current Plan
            </h2>
            <p className="text-sm text-muted-foreground">
              {subscription?.status === "trial" ? (
                <>
                  You are on a{" "}
                  <span className="font-medium">30-day free trial</span> with
                  full Enterprise features. Trial ends on{" "}
                  <span className="font-medium">
                    {subscription?.current_period_end
                      ? new Date(
                          subscription.current_period_end,
                        ).toLocaleDateString()
                      : "N/A"}
                  </span>
                </>
              ) : (
                <>
                  You are currently on the{" "}
                  <span className="font-medium capitalize">
                    {tenant?.subscription_plan || "Trial"}
                  </span>{" "}
                  plan
                </>
              )}
            </p>
          </div>
          <Badge
            variant={subscription?.status === "trial" ? "warning" : "success"}
          >
            {subscription?.status === "trial" ? "Trial" : "Active"}
          </Badge>
        </div>

        {/* Plan Features/Limits */}
        {subscription?.status !== "trial" && (
          <div className="mb-4 p-4 bg-muted/50 rounded-lg">
            <h3 className="text-sm font-medium text-foreground mb-3">
              Your Plan Includes:
            </h3>
            <ul className="text-sm text-muted-foreground space-y-2">
              {tenant?.subscription_plan === "free" && (
                <>
                  <li className="flex items-center gap-2">
                    <CheckIcon size={16} className="text-success shrink-0" />1
                    staff user
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckIcon size={16} className="text-success shrink-0" />
                    50 bookings/month
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckIcon size={16} className="text-success shrink-0" />
                    100 clients maximum
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckIcon size={16} className="text-success shrink-0" />
                    Basic POS (online only)
                  </li>
                </>
              )}
              {tenant?.subscription_plan === "starter" && (
                <>
                  <li className="flex items-center gap-2">
                    <CheckIcon size={16} className="text-success shrink-0" />
                    1-3 staff users
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckIcon size={16} className="text-success shrink-0" />
                    Unlimited bookings
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckIcon size={16} className="text-success shrink-0" />
                    500 clients & 100 SMS/month
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckIcon size={16} className="text-success shrink-0" />
                    Offline POS (works without internet)
                  </li>
                </>
              )}
              {tenant?.subscription_plan === "professional" && (
                <>
                  <li className="flex items-center gap-2">
                    <CheckIcon size={16} className="text-success shrink-0" />
                    4-10 staff users
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckIcon size={16} className="text-success shrink-0" />
                    Unlimited bookings & 2,000 clients
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckIcon size={16} className="text-success shrink-0" />
                    500 SMS/month & advanced POS
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckIcon size={16} className="text-success shrink-0" />
                    Inventory, loyalty & campaigns
                  </li>
                </>
              )}
              {tenant?.subscription_plan === "business" && (
                <>
                  <li className="flex items-center gap-2">
                    <CheckIcon size={16} className="text-success shrink-0" />
                    11-25 staff users
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckIcon size={16} className="text-success shrink-0" />
                    Unlimited bookings & clients
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckIcon size={16} className="text-success shrink-0" />
                    2,000 SMS/month & advanced accounting
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckIcon size={16} className="text-success shrink-0" />
                    Packages, memberships & custom domain
                  </li>
                </>
              )}
              {tenant?.subscription_plan === "enterprise" && (
                <>
                  <li className="flex items-center gap-2">
                    <CheckIcon size={16} className="text-success shrink-0" />
                    26-50 staff users
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckIcon size={16} className="text-success shrink-0" />
                    Unlimited everything & 5,000 SMS/month
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckIcon size={16} className="text-success shrink-0" />
                    White-label & multi-location (3)
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckIcon size={16} className="text-success shrink-0" />
                    API access & dedicated support
                  </li>
                </>
              )}
              {tenant?.subscription_plan === "unlimited" && (
                <>
                  <li className="flex items-center gap-2">
                    <CheckIcon size={16} className="text-success shrink-0" />
                    Unlimited staff & locations
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckIcon size={16} className="text-success shrink-0" />
                    Unlimited SMS & communications
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckIcon size={16} className="text-success shrink-0" />
                    White-label reseller rights
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckIcon size={16} className="text-success shrink-0" />
                    Custom development & 99.9% SLA
                  </li>
                </>
              )}
            </ul>
          </div>
        )}

        <div className="flex items-center gap-4">
          {subscription?.status === "trial" ? (
            <Button onClick={() => handleUpgrade("starter")}>
              Subscribe Now
            </Button>
          ) : (
            <Button onClick={() => handleUpgrade("professional")}>
              Upgrade Plan
            </Button>
          )}
          <Button variant="outline" onClick={() => setShowHistoryModal(true)}>
            View Billing History
          </Button>
        </div>
      </Card>

      {/* Available Plans */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-foreground">
            Available Plans
          </h2>

          {/* Billing Cycle Toggle */}
          <div className="flex items-center gap-2 p-1 bg-muted rounded-lg">
            <button
              onClick={() => setBillingCycle("monthly")}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                billingCycle === "monthly"
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingCycle("yearly")}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                billingCycle === "yearly"
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              Yearly
              <span className="ml-1 text-xs">(Save 15%)</span>
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {plans.map((plan) => {
            const { price, period } = getPrice(plan);
            const isFree = plan.id === "free";
            return (
              <Card
                key={plan.name}
                className={`p-6 relative transition-all hover:shadow-lg ${
                  plan.current
                    ? "border-primary border-2 shadow-md"
                    : "border-border"
                } ${isFree ? "bg-muted/30" : ""}`}
              >
                {plan.popular && (
                  <Badge className="absolute top-4 right-4 bg-primary">
                    Most Popular
                  </Badge>
                )}

                <h3 className="text-xl font-bold text-foreground mb-2">
                  {plan.name}
                </h3>
                <div className="mb-4">
                  {isFree ? (
                    <span className="text-3xl font-bold text-foreground">
                      Free Forever
                    </span>
                  ) : (
                    <>
                      <span className="text-3xl font-bold text-foreground">
                        ₦{price.toLocaleString()}
                      </span>
                      <span className="text-muted-foreground">{period}</span>
                    </>
                  )}
                </div>

                {plan.limits && (
                  <p className="text-xs text-muted-foreground mb-4 italic">
                    {plan.limits}
                  </p>
                )}

                <ul className="space-y-2.5 mb-6 min-h-[280px]">
                  {plan.features.map((feature, index) => (
                    <li
                      key={index}
                      className="flex items-start gap-2 text-sm text-foreground"
                    >
                      <CheckIcon
                        size={16}
                        className="text-success mt-0.5 shrink-0"
                      />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>

                {plan.current ? (
                  <Button fullWidth disabled className="bg-muted">
                    Current Plan
                  </Button>
                ) : (
                  <Button
                    fullWidth
                    variant={plan.popular ? "primary" : "outline"}
                    onClick={() => handleUpgrade(plan.id)}
                  >
                    {isFree
                      ? "Downgrade to Free"
                      : subscription?.status === "trial"
                        ? "Subscribe"
                        : "Upgrade to " + plan.name}
                  </Button>
                )}
              </Card>
            );
          })}
        </div>
      </div>

      {/* Payment Method */}
      <Card className="p-6">
        <h2 className="text-lg font-semibold text-foreground mb-4">
          Payment Method
        </h2>

        {paymentMethods && paymentMethods.length > 0 ? (
          <div className="space-y-3">
            {paymentMethods.map((method) => (
              <div
                key={method.id}
                className="flex items-center gap-4 p-4 border border-border rounded-lg hover:bg-muted/50 transition-colors"
              >
                <CreditCardIcon size={32} className="text-muted-foreground" />
                <div className="flex-1">
                  <p className="font-medium text-foreground">
                    {method.card_type} •••• {method.last4}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Expires {method.exp_month}/{method.exp_year}
                  </p>
                </div>
                {method.is_default && <Badge variant="success">Default</Badge>}
              </div>
            ))}
          </div>
        ) : (
          <div className="flex items-center gap-4 p-4 border border-border rounded-lg bg-muted/30">
            <CreditCardIcon size={32} className="text-muted-foreground" />
            <div className="flex-1">
              <p className="font-medium text-foreground">
                No payment method added
              </p>
              <p className="text-sm text-muted-foreground">
                Payment methods are added automatically when you subscribe to a
                plan
              </p>
            </div>
          </div>
        )}
      </Card>

      {/* Billing Information */}
      <Card className="p-6">
        <h2 className="text-lg font-semibold text-foreground mb-4">
          Billing Information
        </h2>

        <div className="space-y-3 text-sm">
          <div className="flex justify-between items-center p-3 bg-muted/30 rounded-lg">
            <span className="text-muted-foreground">Next billing date:</span>
            <span className="font-medium text-foreground">
              {subscription?.current_period_end
                ? new Date(subscription.current_period_end).toLocaleDateString(
                    "en-US",
                    {
                      year: "numeric",
                      month: "long",
                      day: "numeric",
                    },
                  )
                : "N/A"}
            </span>
          </div>
          <div className="flex justify-between items-center p-3 bg-muted/30 rounded-lg">
            <span className="text-muted-foreground">Billing cycle:</span>
            <span className="font-medium text-foreground capitalize">
              {billingCycle}
            </span>
          </div>
          <div className="flex justify-between items-center p-3 bg-muted/30 rounded-lg">
            <span className="text-muted-foreground">Amount:</span>
            <span className="font-semibold text-foreground text-lg">
              ₦{subscription?.plan_price?.toLocaleString() || 0}
            </span>
          </div>
        </div>
      </Card>

      {/* Danger Zone - Only show for active subscriptions */}
      {subscription?.status === "active" && (
        <Card className="p-6 border-error bg-error/5">
          <div className="flex items-start gap-3">
            <AlertTriangleIcon size={20} className="text-error mt-0.5" />
            <div className="flex-1">
              <h2 className="text-lg font-semibold text-foreground mb-2">
                Cancel Subscription
              </h2>
              <p className="text-sm text-muted-foreground mb-4">
                Once you cancel, your account will be deactivated at the end of
                your billing period and you will lose access to all features.
              </p>
              <Button
                variant="outline"
                className="text-error border-error hover:bg-error hover:text-white"
                onClick={() => setShowCancelModal(true)}
              >
                Cancel Subscription
              </Button>
            </div>
          </div>
        </Card>
      )}

      {/* Upgrade Modal */}
      <Modal
        open={showUpgradeModal}
        onClose={() => setShowUpgradeModal(false)}
        size="lg"
      >
        <ModalHeader>
          <ModalTitle>
            {subscription?.status === "trial"
              ? "Subscribe to Plan"
              : "Upgrade Plan"}
          </ModalTitle>
          <ModalDescription>
            {subscription?.status === "trial"
              ? `Subscribe to the ${
                  plans.find((p) => p.id === selectedPlan)?.name
                } plan to continue using our services after your trial ends.`
              : `Upgrade to the ${
                  plans.find((p) => p.id === selectedPlan)?.name
                } plan for more features and capabilities.`}
          </ModalDescription>
        </ModalHeader>
        <ModalBody>
          <div className="space-y-4">
            {selectedPlan && (
              <div className="p-4 bg-muted/50 rounded-lg">
                <h4 className="font-medium text-foreground mb-2">
                  {plans.find((p) => p.id === selectedPlan)?.name} Plan
                </h4>
                <p className="text-2xl font-bold text-foreground mb-3">
                  ₦
                  {getPrice(
                    plans.find((p) => p.id === selectedPlan)!,
                  ).price.toLocaleString()}
                  {getPrice(plans.find((p) => p.id === selectedPlan)!).period}
                </p>
                <ul className="space-y-2 text-sm">
                  {plans
                    .find((p) => p.id === selectedPlan)
                    ?.features.slice(0, 5)
                    .map((feature, idx) => (
                      <li key={idx} className="flex items-center gap-2">
                        <CheckIcon
                          size={16}
                          className="text-success shrink-0"
                        />
                        <span className="text-muted-foreground">{feature}</span>
                      </li>
                    ))}
                </ul>
              </div>
            )}
            <p className="text-sm text-muted-foreground">
              You will be redirected to complete the payment securely via
              Paystack.
            </p>
          </div>
        </ModalBody>
        <ModalFooter>
          <Button
            variant="outline"
            onClick={() => setShowUpgradeModal(false)}
            disabled={upgradeMutation.isPending}
          >
            Cancel
          </Button>
          <Button onClick={confirmUpgrade} disabled={upgradeMutation.isPending}>
            {upgradeMutation.isPending ? (
              <Spinner size="sm" />
            ) : (
              "Proceed to Payment"
            )}
          </Button>
        </ModalFooter>
      </Modal>

      {/* Cancel Modal */}
      <Modal
        open={showCancelModal}
        onClose={() => setShowCancelModal(false)}
        size="md"
      >
        <ModalHeader>
          <ModalTitle>Cancel Subscription</ModalTitle>
          <ModalDescription>
            Are you sure you want to cancel your subscription?
          </ModalDescription>
        </ModalHeader>
        <ModalBody>
          <div className="space-y-4">
            <div className="flex items-start gap-3 p-4 bg-error/10 rounded-lg border border-error/20">
              <AlertTriangleIcon size={20} className="text-error mt-0.5" />
              <div className="flex-1">
                <p className="text-sm font-medium text-foreground mb-1">
                  Important Notice
                </p>
                <p className="text-sm text-muted-foreground">
                  Your subscription will remain active until the end of the
                  current billing period. After that, you will lose access to
                  all features.
                </p>
              </div>
            </div>
            <p className="text-sm text-muted-foreground">
              Next billing date:{" "}
              <span className="font-medium text-foreground">
                {subscription?.current_period_end
                  ? new Date(
                      subscription.current_period_end,
                    ).toLocaleDateString()
                  : "N/A"}
              </span>
            </p>
          </div>
        </ModalBody>
        <ModalFooter>
          <Button
            variant="outline"
            onClick={() => setShowCancelModal(false)}
            disabled={cancelMutation.isPending}
          >
            Keep Subscription
          </Button>
          <Button
            onClick={handleCancelSubscription}
            disabled={cancelMutation.isPending}
            className="bg-error hover:bg-error/90"
          >
            {cancelMutation.isPending ? <Spinner size="sm" /> : "Cancel Plan"}
          </Button>
        </ModalFooter>
      </Modal>

      {/* Billing History Modal */}
      <Modal
        open={showHistoryModal}
        onClose={() => setShowHistoryModal(false)}
        size="xl"
      >
        <ModalHeader>
          <ModalTitle>Billing History</ModalTitle>
          <ModalDescription>
            View all your past transactions and invoices
          </ModalDescription>
        </ModalHeader>
        <ModalBody>
          {billingHistory && billingHistory.items.length > 0 ? (
            <div className="space-y-3">
              {billingHistory.items.map((item) => (
                <div
                  key={item.id}
                  className="flex justify-between items-center p-4 border border-border rounded-lg hover:bg-muted/50 transition-colors"
                >
                  <div className="flex-1">
                    <p className="font-medium text-foreground">
                      {item.description}
                    </p>
                    <p className="text-sm text-muted-foreground mt-1">
                      {new Date(item.created_at).toLocaleDateString("en-US", {
                        year: "numeric",
                        month: "long",
                        day: "numeric",
                      })}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-foreground text-lg">
                      ₦{item.amount.toLocaleString()}
                    </p>
                    <Badge
                      variant={
                        item.status === "completed" ? "success" : "error"
                      }
                      className="mt-1"
                    >
                      {item.status}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <CreditCardIcon
                size={48}
                className="mx-auto text-muted-foreground mb-4"
              />
              <p className="text-muted-foreground">No billing history yet</p>
              <p className="text-sm text-muted-foreground mt-1">
                Your transactions will appear here once you subscribe
              </p>
            </div>
          )}
        </ModalBody>
        <ModalFooter>
          <Button variant="outline" onClick={() => setShowHistoryModal(false)}>
            Close
          </Button>
        </ModalFooter>
      </Modal>
    </div>
  );
}
