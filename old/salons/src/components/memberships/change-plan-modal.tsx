'use client';

import { useState, useMemo } from 'react';
import {
  useGetPlans,
  useChangePlan,
  MembershipSubscription,
  MembershipPlan,
} from '@/lib/api/hooks/useMemberships';
import { Modal } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { showToast } from '@/lib/utils/toast';
import { CheckIcon, ArrowRightIcon } from '@/components/icons';
import { Spinner } from '@/components/ui/spinner';

interface ChangePlanModalProps {
  isOpen: boolean;
  onClose: () => void;
  subscription: MembershipSubscription;
  currentPlan: MembershipPlan;
  onSuccess?: () => void;
}

export function ChangePlanModal({
  isOpen,
  onClose,
  subscription,
  currentPlan,
  onSuccess,
}: ChangePlanModalProps) {
  const { data: plans = [], isLoading: plansLoading } = useGetPlans();
  const changePlanMutation = useChangePlan();

  const [selectedPlanId, setSelectedPlanId] = useState<string>('');
  const [applyImmediately, setApplyImmediately] = useState(true);
  const [showConfirm, setShowConfirm] = useState(false);

  const availablePlans = useMemo(() => {
    return plans.filter((p) => p._id !== currentPlan._id);
  }, [plans, currentPlan._id]);

  const selectedPlan = plans.find((p) => p._id === selectedPlanId);

  const calculateProration = () => {
    if (!selectedPlan || !currentPlan.price) return 0;

    const startDate = new Date(subscription.start_date);
    const endDate = subscription.end_date
      ? new Date(subscription.end_date)
      : new Date();

    const totalDays = Math.ceil(
      (endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24)
    );
    const daysRemaining = Math.max(
      0,
      Math.ceil(
        (endDate.getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24)
      )
    );

    const priceDifference = selectedPlan.price - currentPlan.price;
    const prorationAmount =
      (priceDifference * daysRemaining) / Math.max(totalDays, 1);

    return prorationAmount;
  };

  const prorationAmount = calculateProration();

  const getPlanChangeType = () => {
    if (!selectedPlan) return null;
    if (selectedPlan.price > currentPlan.price) return 'upgrade';
    if (selectedPlan.price < currentPlan.price) return 'downgrade';
    return 'change';
  };

  const changeType = getPlanChangeType();

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const getBillingCycleLabel = (cycle: string) => {
    switch (cycle) {
      case 'monthly':
        return 'per month';
      case 'quarterly':
        return 'per quarter';
      case 'yearly':
        return 'per year';
      default:
        return '';
    }
  };

  const handleConfirm = async () => {
    if (!selectedPlanId) {
      showToast('Please select a plan', 'error');
      return;
    }

    try {
      await changePlanMutation.mutateAsync({
        subscriptionId: subscription._id,
        newPlanId: selectedPlanId,
        applyImmediately,
      });

      showToast('Plan changed successfully', 'success');
      setSelectedPlanId('');
      setApplyImmediately(true);
      setShowConfirm(false);
      onClose();
      onSuccess?.();
    } catch (error: any) {
      showToast(
        error.response?.data?.detail || 'Failed to change plan',
        'error'
      );
    }
  };

  if (!isOpen) return null;

  return (
    <Modal open={isOpen} onClose={onClose} size="lg">
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold">Change Plan</h2>
          <p className="text-muted-foreground mt-1">
            Upgrade or downgrade to a different membership plan
          </p>
        </div>

        {/* Current Plan */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Current Plan</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-semibold text-lg">{currentPlan.name}</p>
                <p className="text-sm text-muted-foreground">
                  ${currentPlan.price} {getBillingCycleLabel(currentPlan.billing_cycle)}
                </p>
              </div>
              <Badge variant="info">Current</Badge>
            </div>
          </CardContent>
        </Card>

        {/* Available Plans */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Select New Plan</label>
          {plansLoading ? (
            <div className="flex items-center justify-center h-32">
              <Spinner size="lg" />
            </div>
          ) : availablePlans.length > 0 ? (
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {availablePlans.map((plan) => (
                <button
                  key={plan._id}
                  onClick={() => setSelectedPlanId(plan._id)}
                  className={`w-full p-4 border rounded-lg transition-all text-left ${
                    selectedPlanId === plan._id
                      ? 'border-primary bg-primary/5'
                      : 'border-border hover:border-primary/50'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="font-semibold">{plan.name}</p>
                      <p className="text-sm text-muted-foreground">
                        ${plan.price} {getBillingCycleLabel(plan.billing_cycle)}
                      </p>
                      {plan.discount_percentage && (
                        <p className="text-sm text-green-600 mt-1">
                          {plan.discount_percentage}% discount on services
                        </p>
                      )}
                    </div>
                    {selectedPlanId === plan._id && (
                      <CheckIcon size={20} className="text-primary" />
                    )}
                  </div>
                </button>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-muted-foreground">No other plans available</p>
            </div>
          )}
        </div>

        {/* Proration Preview */}
        {selectedPlan && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">
                {changeType === 'upgrade'
                  ? 'Upgrade Details'
                  : changeType === 'downgrade'
                    ? 'Downgrade Details'
                    : 'Plan Change Details'}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Current Price</p>
                  <p className="font-semibold">${currentPlan.price}</p>
                </div>
                <ArrowRightIcon size={20} className="text-muted-foreground" />
                <div>
                  <p className="text-sm text-muted-foreground">New Price</p>
                  <p className="font-semibold">${selectedPlan.price}</p>
                </div>
              </div>

              <div className="pt-4 border-t border-border space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">
                    Price Difference
                  </span>
                  <span className="font-medium">
                    {formatCurrency(selectedPlan.price - currentPlan.price)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">
                    Prorated Amount
                  </span>
                  <span
                    className={`font-medium ${
                      prorationAmount > 0 ? 'text-red-600' : 'text-green-600'
                    }`}
                  >
                    {prorationAmount > 0 ? '+' : ''}
                    {formatCurrency(prorationAmount)}
                  </span>
                </div>
              </div>

              {prorationAmount > 0 && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                  <p className="text-sm text-red-700">
                    You will be charged {formatCurrency(prorationAmount)} for
                    this upgrade
                  </p>
                </div>
              )}

              {prorationAmount < 0 && (
                <div className="p-3 bg-green-50 border border-green-200 rounded-md">
                  <p className="text-sm text-green-700">
                    You will receive a credit of{' '}
                    {formatCurrency(Math.abs(prorationAmount))} for this
                    downgrade
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Apply Immediately Option */}
        {selectedPlan && (
          <div className="flex items-center gap-3 p-3 bg-accent rounded-md">
            <Checkbox
              id="apply-immediately"
              checked={applyImmediately}
              onChange={(e) => setApplyImmediately(e.target.checked)}
              disabled={changePlanMutation.isPending}
            />
            <label htmlFor="apply-immediately" className="text-sm cursor-pointer">
              Apply immediately (otherwise applies at next billing cycle)
            </label>
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-3 justify-end pt-4 border-t border-border">
          <Button
            variant="outline"
            onClick={onClose}
            disabled={changePlanMutation.isPending}
          >
            Cancel
          </Button>
          {!showConfirm ? (
            <Button
              onClick={() => setShowConfirm(true)}
              disabled={!selectedPlanId || changePlanMutation.isPending}
            >
              Continue
            </Button>
          ) : (
            <>
              <Button
                variant="outline"
                onClick={() => setShowConfirm(false)}
                disabled={changePlanMutation.isPending}
              >
                Back
              </Button>
              <Button
                onClick={handleConfirm}
                disabled={changePlanMutation.isPending}
              >
                {changePlanMutation.isPending ? 'Changing...' : 'Confirm Change'}
              </Button>
            </>
          )}
        </div>
      </div>
    </Modal>
  );
}
