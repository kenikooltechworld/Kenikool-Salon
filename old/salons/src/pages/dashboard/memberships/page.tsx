import { useState } from "react";
import {
  useGetPlans,
  useGetSubscriptions,
  useCancelSubscription,
} from "@/lib/api/hooks/useMemberships";
import {
  MembershipList,
  MembershipFormModal,
  SubscriptionList,
  SubscriptionCreateModal,
  SubscriptionDetailsModal,
  PlanDetailsModal,
  ChangePlanModal,
  MembershipAnalytics,
  PlanComparison,
} from "@/components/memberships";
import { CreditCardIcon, PlusIcon, StarIcon, BarChartIcon, CompareIcon } from "@/components/icons";
import { showToast } from "@/lib/utils/toast";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Spinner } from "@/components/ui/spinner";

export default function MembershipsPage() {
  const { data: plans = [], isLoading: plansLoading } = useGetPlans();
  const { data: subscriptions = [], isLoading: subscriptionsLoading } =
    useGetSubscriptions();
  const cancelMutation = useCancelSubscription();

  const [isFormOpen, setIsFormOpen] = useState(false);
  const [isCreateSubscriptionOpen, setIsCreateSubscriptionOpen] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [selectedSubscriptionId, setSelectedSubscriptionId] = useState<string | null>(null);
  const [selectedPlanId, setSelectedPlanId] = useState<string | null>(null);
  const [selectedSubscriptionForChange, setSelectedSubscriptionForChange] = useState<any>(null);
  const [activeTab, setActiveTab] = useState("plans");

  const handleEdit = (plan: any) => {
    setSelectedPlan(plan);
    setIsFormOpen(true);
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this membership plan?")) return;
    showToast("Membership plan deleted", "success");
  };

  const handleCancelSubscription = async (id: string) => {
    if (!confirm("Cancel this subscription?")) return;

    try {
      await cancelMutation.mutateAsync(id);
      showToast("Subscription cancelled successfully", "success");
    } catch (error: any) {
      showToast(
        error.response?.data?.detail || "Failed to cancel subscription",
        "error"
      );
    }
  };

  const handleViewSubscriptionDetails = (subscriptionId: string) => {
    setSelectedSubscriptionId(subscriptionId);
  };

  const handleViewPlanDetails = (planId: string) => {
    setSelectedPlanId(planId);
  };

  const handleChangePlan = (subscription: any) => {
    setSelectedSubscriptionForChange(subscription);
  };

  const isLoading = plansLoading || subscriptionsLoading;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <CreditCardIcon size={32} className="text-primary" />
            Membership Plans
          </h1>
          <p className="text-muted-foreground mt-1">
            Create and manage client membership plans and subscriptions
          </p>
        </div>
        {activeTab === "plans" && (
          <Button
            onClick={() => {
              setSelectedPlan(null);
              setIsFormOpen(true);
            }}
          >
            <PlusIcon size={20} />
            Create Plan
          </Button>
        )}
        {activeTab === "subscriptions" && (
          <Button
            onClick={() => setIsCreateSubscriptionOpen(true)}
          >
            <PlusIcon size={20} />
            Create Subscription
          </Button>
        )}
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="plans">
            <CreditCardIcon size={18} className="mr-2" />
            Plans
          </TabsTrigger>
          <TabsTrigger value="subscriptions">
            <StarIcon size={18} className="mr-2" />
            Subscriptions
          </TabsTrigger>
          <TabsTrigger value="comparison">
            <CompareIcon size={18} className="mr-2" />
            Compare Plans
          </TabsTrigger>
          <TabsTrigger value="analytics">
            <BarChartIcon size={18} className="mr-2" />
            Analytics
          </TabsTrigger>
        </TabsList>

        <TabsContent value="plans">
          <Card>
            <CardHeader>
              <CardTitle>Membership Plans</CardTitle>
            </CardHeader>
            <CardContent>
              <MembershipList
                plans={plans}
                onEdit={handleEdit}
                onDelete={handleDelete}
                onViewDetails={handleViewPlanDetails}
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="subscriptions">
          <Card>
            <CardHeader>
              <CardTitle>Active Subscriptions</CardTitle>
            </CardHeader>
            <CardContent>
              <SubscriptionList
                subscriptions={subscriptions}
                onCancel={handleCancelSubscription}
                onViewDetails={handleViewSubscriptionDetails}
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="comparison">
          <Card>
            <CardHeader>
              <CardTitle>Plan Comparison</CardTitle>
            </CardHeader>
            <CardContent>
              <PlanComparison
                onSelectPlan={(plan) => {
                  setSelectedPlan(plan);
                  setIsFormOpen(true);
                }}
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analytics">
          <Card>
            <CardHeader>
              <CardTitle>Membership Analytics</CardTitle>
            </CardHeader>
            <CardContent>
              <MembershipAnalytics />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <MembershipFormModal
        isOpen={isFormOpen}
        onClose={() => {
          setIsFormOpen(false);
          setSelectedPlan(null);
        }}
        plan={selectedPlan}
      />

      <SubscriptionCreateModal
        isOpen={isCreateSubscriptionOpen}
        onClose={() => setIsCreateSubscriptionOpen(false)}
        onSuccess={() => {
          setIsCreateSubscriptionOpen(false);
        }}
      />

      {selectedSubscriptionId && (
        <SubscriptionDetailsModal
          isOpen={!!selectedSubscriptionId}
          onClose={() => setSelectedSubscriptionId(null)}
          subscriptionId={selectedSubscriptionId}
          onChangePlan={(subId) => {
            const sub = subscriptions.find((s) => s._id === subId);
            if (sub) {
              setSelectedSubscriptionForChange(sub);
              setSelectedSubscriptionId(null);
            }
          }}
        />
      )}

      {selectedPlanId && (
        <PlanDetailsModal
          isOpen={!!selectedPlanId}
          onClose={() => setSelectedPlanId(null)}
          plan={plans.find((p) => p._id === selectedPlanId)!}
        />
      )}

      {selectedSubscriptionForChange && (
        <ChangePlanModal
          isOpen={!!selectedSubscriptionForChange}
          onClose={() => setSelectedSubscriptionForChange(null)}
          subscription={selectedSubscriptionForChange}
          currentPlan={plans.find((p) => p._id === selectedSubscriptionForChange.plan_id)!}
          onSuccess={() => {
            setSelectedSubscriptionForChange(null);
          }}
        />
      )}
    </div>
  );
}
