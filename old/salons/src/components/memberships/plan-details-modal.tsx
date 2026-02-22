import { useMemo } from "react";
import {
  useGetSubscriptions,
  MembershipPlan,
} from "@/lib/api/hooks/useMemberships";
// TODO: useGetClients needs to be implemented in useClients
// import { useGetClients } from '@/lib/api/hooks/useClients';
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs } from "@/components/ui/tabs";
import { CheckIcon, UserIcon, TrendingUpIcon } from "@/components/icons";
import { Spinner } from "@/components/ui/spinner";
import { useState } from "react";

interface PlanDetailsModalProps {
  isOpen: boolean;
  onClose: () => void;
  plan: MembershipPlan;
}

export function PlanDetailsModal({
  isOpen,
  onClose,
  plan,
}: PlanDetailsModalProps) {
  const { data: subscriptions = [], isLoading: subscriptionsLoading } =
    useGetSubscriptions();
  const { data: clients = [], isLoading: clientsLoading } = useGetClients();
  const [activeTab, setActiveTab] = useState("overview");

  const planSubscriptions = useMemo(() => {
    return subscriptions.filter((sub) => sub.plan_id === plan._id);
  }, [subscriptions, plan._id]);

  const activeSubscribers = useMemo(() => {
    return planSubscriptions.filter((sub) => sub.status === "active");
  }, [planSubscriptions]);

  const subscribersWithDetails = useMemo(() => {
    return activeSubscribers.map((sub) => {
      const client = clients.find((c: any) => c._id === sub.client_id);
      return {
        ...sub,
        client,
      };
    });
  }, [activeSubscribers, clients]);

  const totalRevenue = useMemo(() => {
    return planSubscriptions.reduce((sum, sub) => {
      const paymentSum = (sub.payment_history || [])
        .filter((p) => p.status === "success")
        .reduce((s, p) => s + p.amount, 0);
      return sum + paymentSum;
    }, 0);
  }, [planSubscriptions]);

  const averageSubscriptionDays = useMemo(() => {
    if (planSubscriptions.length === 0) return 0;
    const totalDays = planSubscriptions.reduce((sum, sub) => {
      const startDate = new Date(sub.start_date);
      const endDate = sub.end_date ? new Date(sub.end_date) : new Date();
      const days = Math.floor(
        (endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24),
      );
      return sum + days;
    }, 0);
    return Math.round(totalDays / planSubscriptions.length);
  }, [planSubscriptions]);

  const getBillingCycleLabel = (cycle: string) => {
    switch (cycle) {
      case "monthly":
        return "per month";
      case "quarterly":
        return "per quarter";
      case "yearly":
        return "per year";
      default:
        return "";
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(amount);
  };

  const isLoading = subscriptionsLoading || clientsLoading;

  return (
    <Modal open={isOpen} onClose={onClose} size="lg">
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold">{plan.name}</h2>
          <p className="text-muted-foreground mt-1">{plan.description}</p>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-3 gap-4">
          <Card>
            <CardContent className="p-4">
              <p className="text-sm text-muted-foreground">
                Active Subscribers
              </p>
              <p className="text-3xl font-bold text-primary">
                {activeSubscribers.length}
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <p className="text-sm text-muted-foreground">Total Revenue</p>
              <p className="text-2xl font-bold text-green-600">
                {formatCurrency(totalRevenue)}
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <p className="text-sm text-muted-foreground">Avg. Duration</p>
              <p className="text-2xl font-bold">{averageSubscriptionDays}d</p>
            </CardContent>
          </Card>
        </div>

        <Tabs
          value={activeTab}
          onValueChange={setActiveTab}
          tabs={[
            { value: "overview", label: "Overview" },
            { value: "subscribers", label: "Subscribers" },
          ]}
        >
          {/* Overview Tab */}
          {activeTab === "overview" && (
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Plan Details</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-muted-foreground">Price</p>
                      <p className="text-3xl font-bold text-primary">
                        ${plan.price}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">
                        Billing Cycle
                      </p>
                      <p className="text-lg font-medium capitalize">
                        {plan.billing_cycle}
                      </p>
                    </div>
                    {plan.discount_percentage && (
                      <div>
                        <p className="text-sm text-muted-foreground">
                          Discount
                        </p>
                        <p className="text-lg font-medium text-green-600">
                          {plan.discount_percentage}% off services
                        </p>
                      </div>
                    )}
                    <div>
                      <p className="text-sm text-muted-foreground">Created</p>
                      <p className="text-lg font-medium">
                        {formatDate(plan.created_at)}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {plan.benefits && plan.benefits.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Benefits</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {plan.benefits.map((benefit, index) => (
                        <li key={index} className="flex items-start gap-2">
                          <CheckIcon
                            size={20}
                            className="text-green-500 mt-0.5 flex-shrink-0"
                          />
                          <span>{benefit}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}
            </div>
          )}

          {/* Subscribers Tab */}
          {activeTab === "subscribers" && (
            <div className="space-y-4">
              {isLoading ? (
                <div className="flex items-center justify-center h-64">
                  <Spinner size="lg" />
                </div>
              ) : subscribersWithDetails.length > 0 ? (
                <div className="space-y-2">
                  {subscribersWithDetails.map((subscription) => (
                    <Card key={subscription._id}>
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between">
                          <div className="flex items-start gap-3">
                            <UserIcon size={20} className="text-primary mt-1" />
                            <div>
                              <p className="font-medium">
                                {subscription.client?.name || "Unknown Client"}
                              </p>
                              <p className="text-sm text-muted-foreground">
                                {subscription.client?.email}
                              </p>
                              <p className="text-xs text-muted-foreground mt-1">
                                Joined {formatDate(subscription.start_date)}
                              </p>
                            </div>
                          </div>
                          <Badge variant="success">Active</Badge>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <UserIcon
                    size={48}
                    className="mx-auto text-muted-foreground mb-4"
                  />
                  <h3 className="text-lg font-semibold mb-2">
                    No active subscribers
                  </h3>
                  <p className="text-muted-foreground">
                    This plan has no active subscriptions yet
                  </p>
                </div>
              )}
            </div>
          )}
        </Tabs>

        {/* Actions */}
        <div className="flex gap-3 justify-end pt-4 border-t border-border">
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>
    </Modal>
  );
}
