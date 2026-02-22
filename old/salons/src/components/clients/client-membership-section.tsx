import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import {
  CheckIcon,
  AlertTriangleIcon,
  CreditCardIcon,
  CalendarIcon,
  PercentIcon,
} from "@/components/icons";
import {
  useGetClientSubscriptions,
  useGetPlans,
} from "@/lib/api/hooks/useMemberships";
import { SubscriptionDetailsModal } from "@/components/memberships/subscription-details-modal";
import { ChangePlanModal } from "@/components/memberships/change-plan-modal";

interface ClientMembershipSectionProps {
  clientId: string;
}

export function ClientMembershipSection({
  clientId,
}: ClientMembershipSectionProps) {
  const subscriptionsQuery = useGetClientSubscriptions(clientId);
  const plansQuery = useGetPlans();
  const [selectedSubscriptionId, setSelectedSubscriptionId] = useState<
    string | null
  >(null);
  const [showChangePlanModal, setShowChangePlanModal] = useState(false);

  // Ensure data is always an array
  const subscriptions: any[] = Array.isArray(subscriptionsQuery.data)
    ? subscriptionsQuery.data
    : [];
  const plans: any[] = Array.isArray(plansQuery.data) ? plansQuery.data : [];
  const isLoading = subscriptionsQuery.isLoading;

  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="flex justify-center py-8">
          <Spinner />
        </div>
      </Card>
    );
  }

  const activeSubscription = subscriptions.find(
    (sub) => sub.status === "active" || sub.status === "trial"
  );
  const subscriptionHistory = subscriptions.filter(
    (sub) => sub.status !== "active" && sub.status !== "trial"
  );

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200";
      case "trial":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200";
      case "paused":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200";
      case "cancelled":
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200";
      case "expired":
        return "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200";
      case "grace_period":
        return "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200";
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200";
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  if (subscriptions.length === 0) {
    return (
      <Card className="p-6">
        <h2 className="text-lg font-semibold text-foreground mb-4">
          Membership
        </h2>
        <Alert variant="info">
          <AlertTriangleIcon size={20} />
          <div>
            <p className="text-sm">No active membership</p>
          </div>
        </Alert>
      </Card>
    );
  }

  return (
    <>
      <Card className="p-6">
        <h2 className="text-lg font-semibold text-foreground mb-4">
          Membership
        </h2>

        {/* Active Subscription */}
        {activeSubscription && (
          <div className="mb-6">
            <h3 className="text-sm font-medium text-muted-foreground mb-3">
              Active Subscription
            </h3>
            <div className="border border-border rounded-lg p-4 bg-muted/30">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <h4 className="font-semibold text-foreground">
                      {plans.find((p) => p._id === activeSubscription.plan_id)
                        ?.name || "Unknown Plan"}
                    </h4>
                    <Badge className={getStatusColor(activeSubscription.status)}>
                      {activeSubscription.status.charAt(0).toUpperCase() +
                        activeSubscription.status.slice(1)}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {plans.find((p) => p._id === activeSubscription.plan_id)
                      ?.description}
                  </p>
                </div>
              </div>

              {/* Subscription Details Grid */}
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="flex items-start gap-2">
                  <CalendarIcon size={16} className="text-primary mt-1" />
                  <div>
                    <p className="text-xs text-muted-foreground">Start Date</p>
                    <p className="text-sm font-medium">
                      {formatDate(activeSubscription.start_date)}
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <CalendarIcon size={16} className="text-primary mt-1" />
                  <div>
                    <p className="text-xs text-muted-foreground">Next Renewal</p>
                    <p className="text-sm font-medium">
                      {activeSubscription.end_date
                        ? formatDate(activeSubscription.end_date)
                        : "N/A"}
                    </p>
                  </div>
                </div>
                {plans.find((p) => p._id === activeSubscription.plan_id)
                  ?.discount_percentage && (
                  <div className="flex items-start gap-2">
                    <PercentIcon size={16} className="text-primary mt-1" />
                    <div>
                      <p className="text-xs text-muted-foreground">Discount</p>
                      <p className="text-sm font-medium text-green-600">
                        {
                          plans.find((p) => p._id === activeSubscription.plan_id)
                            ?.discount_percentage
                        }
                        % off
                      </p>
                    </div>
                  </div>
                )}
                <div className="flex items-start gap-2">
                  <CreditCardIcon size={16} className="text-primary mt-1" />
                  <div>
                    <p className="text-xs text-muted-foreground">Auto-Renew</p>
                    <p className="text-sm font-medium flex items-center gap-1">
                      {activeSubscription.auto_renew ? (
                        <>
                          <CheckIcon size={14} className="text-green-500" />
                          Enabled
                        </>
                      ) : (
                        <>
                          <span className="text-red-500">✕</span>
                          Disabled
                        </>
                      )}
                    </p>
                  </div>
                </div>
              </div>

              {/* Benefits */}
              {plans.find((p) => p._id === activeSubscription.plan_id)
                ?.benefits && (
                <div className="mb-4 pb-4 border-b border-border">
                  <p className="text-xs font-medium text-muted-foreground mb-2">
                    Benefits:
                  </p>
                  <ul className="space-y-1">
                    {plans
                      .find((p) => p._id === activeSubscription.plan_id)
                      ?.benefits.slice(0, 3)
                      .map((benefit: string, index: number) => (
                        <li
                          key={index}
                          className="flex items-start gap-2 text-xs"
                        >
                          <CheckIcon
                            size={12}
                            className="text-green-500 mt-0.5 shrink-0"
                          />
                          <span>{benefit}</span>
                        </li>
                      ))}
                  </ul>
                  {(plans.find((p) => p._id === activeSubscription.plan_id)
                    ?.benefits.length || 0) > 3 && (
                    <p className="text-xs text-muted-foreground mt-1">
                      +
                      {(plans.find((p) => p._id === activeSubscription.plan_id)
                        ?.benefits.length || 0) - 3}{" "}
                      more benefits
                    </p>
                  )}
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => setSelectedSubscriptionId(activeSubscription._id)}
                >
                  View Details
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => setShowChangePlanModal(true)}
                >
                  Change Plan
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* Subscription History */}
        {subscriptionHistory.length > 0 && (
          <div>
            <h3 className="text-sm font-medium text-muted-foreground mb-3">
              Subscription History
            </h3>
            <div className="space-y-2">
              {subscriptionHistory.map((subscription) => (
                <div
                  key={subscription._id}
                  className="border border-border rounded-lg p-3 bg-muted/20 hover:bg-muted/40 transition-colors cursor-pointer"
                  onClick={() => setSelectedSubscriptionId(subscription._id)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <p className="text-sm font-medium">
                          {plans.find((p) => p._id === subscription.plan_id)
                            ?.name || "Unknown Plan"}
                        </p>
                        <Badge className={getStatusColor(subscription.status)}>
                          {subscription.status.charAt(0).toUpperCase() +
                            subscription.status.slice(1)}
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        {formatDate(subscription.start_date)} -{" "}
                        {subscription.end_date
                          ? formatDate(subscription.end_date)
                          : "N/A"}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </Card>

      {/* Subscription Details Modal */}
      {selectedSubscriptionId && (
        <SubscriptionDetailsModal
          isOpen={!!selectedSubscriptionId}
          onClose={() => setSelectedSubscriptionId(null)}
          subscriptionId={selectedSubscriptionId}
          onChangePlan={() => setShowChangePlanModal(true)}
        />
      )}

      {/* Change Plan Modal */}
      {showChangePlanModal && activeSubscription && plans.length > 0 && (
        <ChangePlanModal
          isOpen={showChangePlanModal}
          onClose={() => setShowChangePlanModal(false)}
          subscription={activeSubscription}
          currentPlan={
            plans.find((p) => p._id === activeSubscription.plan_id) || plans[0]
          }
          onSuccess={() => {
            setShowChangePlanModal(false);
          }}
        />
      )}
    </>
  );
}
