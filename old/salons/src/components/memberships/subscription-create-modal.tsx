"use client";

import { useState, useMemo, useEffect } from "react";
import {
  useGetPlans,
  useCreateSubscription,
} from "@/lib/api/hooks/useMemberships";
import { useClients } from "@/lib/api/hooks/useClients";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { showToast } from "@/lib/utils/toast";
import { CheckIcon, SearchIcon, LockIcon } from "@/components/icons";
import {
  loadPaystackScript,
  formatAmountForPaystack,
} from "@/lib/utils/paystack";

// Extend Window interface for Paystack
declare global {
  interface Window {
    PaystackPop: any;
  }
}

interface SubscriptionCreateModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export function SubscriptionCreateModal({
  isOpen,
  onClose,
  onSuccess,
}: SubscriptionCreateModalProps) {
  const { data: plansData, isLoading: plansLoading } = useGetPlans();
  const { data: clientsData, isLoading: clientsLoading } = useClients();
  const createMutation = useCreateSubscription();

  const [selectedClientId, setSelectedClientId] = useState<string>("");
  const [selectedPlanId, setSelectedPlanId] = useState<string>("");
  const [startTrial, setStartTrial] = useState(false);
  const [clientSearch, setClientSearch] = useState("");
  const [showClientDropdown, setShowClientDropdown] = useState(false);
  const [showPaymentForm, setShowPaymentForm] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  // Extract arrays from paginated responses
  const plans = Array.isArray(plansData) ? plansData : plansData?.data || [];
  const clients = Array.isArray(clientsData)
    ? clientsData
    : clientsData?.data || [];

  // Load Paystack script on component mount
  useEffect(() => {
    if (isOpen) {
      loadPaystackScript().catch((error: Error) => {
        console.error("Failed to load Paystack script:", error);
      });
    }
  }, [isOpen]);

  const filteredClients = useMemo(() => {
    if (!clientSearch) return clients;
    return clients.filter(
      (client: any) =>
        client.name?.toLowerCase().includes(clientSearch.toLowerCase()) ||
        client.email?.toLowerCase().includes(clientSearch.toLowerCase()),
    );
  }, [clients, clientSearch]);

  const selectedPlan = useMemo(
    () => plans.find((p: any) => p._id === selectedPlanId),
    [plans, selectedPlanId],
  );
  const selectedClient = useMemo(
    () => clients.find((c: any) => c._id === selectedClientId),
    [clients, selectedClientId],
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedClientId) {
      showToast("Please select a client", "error");
      return;
    }

    if (!selectedPlanId) {
      showToast("Please select a plan", "error");
      return;
    }

    // Show payment form instead of directly creating subscription
    if (!startTrial) {
      setShowPaymentForm(true);
    } else {
      // For trial subscriptions, create directly without payment
      await createSubscriptionDirect("trial_auth");
    }
  };

  const createSubscriptionDirect = async (authCode: string) => {
    try {
      setIsProcessing(true);
      await createMutation.mutateAsync({
        client_id: selectedClientId,
        plan_id: selectedPlanId,
        start_trial: startTrial,
        payment_method_id: authCode,
      } as any);

      showToast("Subscription created successfully", "success");
      setSelectedClientId("");
      setSelectedPlanId("");
      setStartTrial(false);
      setClientSearch("");
      setShowPaymentForm(false);
      onClose();
      onSuccess?.();
    } catch (error: any) {
      showToast(
        error.response?.data?.detail || "Failed to create subscription",
        "error",
      );
    } finally {
      setIsProcessing(false);
    }
  };

  const handlePaystackPayment = async () => {
    const selectedClientData = clients.find(
      (c: any) => c._id === selectedClientId,
    );
    const selectedPlanData = plans.find((p: any) => p._id === selectedPlanId);

    if (!selectedClientData || !selectedPlanData) {
      showToast("Invalid client or plan selection", "error");
      return;
    }

    if (!window.PaystackPop) {
      showToast(
        "Payment system not loaded. Please refresh and try again.",
        "error",
      );
      return;
    }

    setIsProcessing(true);

    try {
      // Initialize Paystack payment
      const handler = window.PaystackPop.setup({
        key: import.meta.env.VITE_PAYSTACK_PUBLIC_KEY,
        email: selectedClientData.email,
        amount: formatAmountForPaystack(selectedPlanData.price),
        ref: `sub_${selectedClientId}_${Date.now()}`,
        onClose: () => {
          setIsProcessing(false);
          showToast("Payment cancelled", "info");
        },
        onSuccess: async (response: any) => {
          // Payment successful, create subscription with authorization code
          await createSubscriptionDirect(response.reference);
        },
      });

      handler.openIframe();
    } catch (error: any) {
      setIsProcessing(false);
      showToast(
        "Payment initialization failed: " + (error?.message || "Unknown error"),
        "error",
      );
    }
  };

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

  const isLoading = plansLoading || clientsLoading || createMutation.isPending;

  return (
    <Modal open={isOpen} onClose={onClose} size="lg">
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold">Create Subscription</h2>
          <p className="text-muted-foreground mt-1">
            Subscribe a client to a membership plan
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Client Selection */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Select Client</label>
            <div className="relative">
              <div className="relative">
                <SearchIcon
                  size={18}
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
                />
                <Input
                  placeholder="Search by name or email..."
                  value={clientSearch}
                  onChange={(e) => {
                    setClientSearch(e.target.value);
                    setShowClientDropdown(true);
                  }}
                  onFocus={() => setShowClientDropdown(true)}
                  className="pl-10"
                  disabled={isLoading || showPaymentForm}
                />
              </div>

              {showClientDropdown && filteredClients.length > 0 && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-card border border-border rounded-md shadow-lg z-50 max-h-48 overflow-y-auto">
                  {filteredClients.map((client: any) => (
                    <button
                      key={client._id}
                      type="button"
                      onClick={() => {
                        setSelectedClientId(client._id);
                        setClientSearch(client.name);
                        setShowClientDropdown(false);
                      }}
                      className="w-full text-left px-4 py-2 hover:bg-accent transition-colors border-b border-border last:border-b-0"
                    >
                      <div className="font-medium">{client.name}</div>
                      <div className="text-sm text-muted-foreground">
                        {client.email}
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {selectedClient && (
              <div className="mt-2 p-3 bg-accent rounded-md">
                <p className="text-sm font-medium">{selectedClient.name}</p>
                <p className="text-xs text-muted-foreground">
                  {selectedClient.email}
                </p>
              </div>
            )}
          </div>

          {/* Plan Selection */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Select Plan</label>
            <Select
              value={selectedPlanId}
              onChange={(e) => setSelectedPlanId(e.target.value)}
              disabled={isLoading || showPaymentForm}
            >
              <option value="">Choose a plan...</option>
              {plans.map((plan: any) => (
                <option key={plan._id} value={plan._id}>
                  {plan.name} - ${plan.price}{" "}
                  {getBillingCycleLabel(plan.billing_cycle)}
                </option>
              ))}
            </Select>
          </div>

          {/* Plan Details Preview */}
          {selectedPlan && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">{selectedPlan.name}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold text-primary">
                    ${selectedPlan.price}
                  </span>
                  <span className="text-muted-foreground">
                    {getBillingCycleLabel(selectedPlan.billing_cycle)}
                  </span>
                </div>

                {selectedPlan.discount_percentage && (
                  <div className="p-2 bg-green-50 border border-green-200 rounded-md">
                    <p className="text-sm text-green-700">
                      {selectedPlan.discount_percentage}% discount on services
                    </p>
                  </div>
                )}

                {selectedPlan.description && (
                  <p className="text-sm text-muted-foreground">
                    {selectedPlan.description}
                  </p>
                )}

                {selectedPlan.benefits && selectedPlan.benefits.length > 0 && (
                  <div className="space-y-2">
                    <p className="text-sm font-medium">Benefits:</p>
                    <ul className="space-y-1">
                      {selectedPlan.benefits.map(
                        (benefit: any, index: number) => (
                          <li
                            key={index}
                            className="flex items-start gap-2 text-sm"
                          >
                            <CheckIcon
                              size={16}
                              className="text-green-500 mt-0.5 shrink-0"
                            />
                            <span>{benefit}</span>
                          </li>
                        ),
                      )}
                    </ul>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Trial Option */}
          {selectedPlan && !showPaymentForm && (
            <div className="flex items-center gap-3 p-3 bg-accent rounded-md">
              <Checkbox
                id="start-trial"
                checked={startTrial}
                onChange={(e) => setStartTrial(e.target.checked)}
                disabled={isLoading}
              />
              <label htmlFor="start-trial" className="text-sm cursor-pointer">
                Start with trial period ({selectedPlan.trial_period_days || 0}{" "}
                days)
              </label>
            </div>
          )}

          {/* Payment Form */}
          {showPaymentForm && selectedPlan && (
            <Card className="border-blue-200 bg-blue-50">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <LockIcon size={20} className="text-blue-600" />
                  Secure Payment
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="p-3 bg-white rounded-md border border-blue-200">
                  <p className="text-sm text-muted-foreground">
                    Amount to charge:
                  </p>
                  <p className="text-2xl font-bold text-primary">
                    ${selectedPlan.price}
                  </p>
                </div>
                <p className="text-sm text-muted-foreground">
                  Click "Process Payment" to proceed with Paystack secure
                  payment gateway.
                </p>
              </CardContent>
            </Card>
          )}

          {/* Actions */}
          <div className="flex gap-3 justify-end pt-4 border-t border-border">
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                setShowPaymentForm(false);
                onClose();
              }}
              disabled={isLoading}
            >
              Cancel
            </Button>
            {!showPaymentForm ? (
              <Button
                type="submit"
                disabled={!selectedClientId || !selectedPlanId || isLoading}
              >
                {isLoading ? "Creating..." : "Next"}
              </Button>
            ) : (
              <>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setShowPaymentForm(false)}
                  disabled={isLoading}
                >
                  Back
                </Button>
                <Button
                  type="button"
                  onClick={handlePaystackPayment}
                  disabled={isLoading}
                >
                  {isLoading ? "Processing..." : "Process Payment"}
                </Button>
              </>
            )}
          </div>
        </form>
      </div>
    </Modal>
  );
}
