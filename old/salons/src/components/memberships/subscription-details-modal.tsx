'use client';

import { useState } from 'react';
import {
  useGetSubscriptionDetails,
  useCancelSubscription,
  usePauseSubscription,
  useResumeSubscription,
} from '@/lib/api/hooks/useMemberships';
import { useGetPlans } from '@/lib/api/hooks/useMemberships';
import { Modal } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { showToast } from '@/lib/utils/toast';
import {
  CheckIcon,
  XIcon,
  CreditCardIcon,
  HistoryIcon,
} from '@/components/icons';
import { Spinner } from '@/components/ui/spinner';

interface SubscriptionDetailsModalProps {
  isOpen: boolean;
  onClose: () => void;
  subscriptionId: string;
  onChangePlan?: (subscriptionId: string) => void;
}

export function SubscriptionDetailsModal({
  isOpen,
  onClose,
  subscriptionId,
  onChangePlan,
}: SubscriptionDetailsModalProps) {
  const { data: subscription, isLoading } = useGetSubscriptionDetails(subscriptionId);
  const { data: plans = [] } = useGetPlans();
  const cancelMutation = useCancelSubscription();
  const pauseMutation = usePauseSubscription();
  const resumeMutation = useResumeSubscription();

  const [activeTab, setActiveTab] = useState('overview');
  const [showCancelConfirm, setShowCancelConfirm] = useState(false);

  if (!isOpen) return null;

  if (isLoading) {
    return (
      <Modal open={isOpen} onClose={onClose} size="lg">
        <div className="flex items-center justify-center h-64">
          <Spinner size="lg" />
        </div>
      </Modal>
    );
  }

  if (!subscription) {
    return (
      <Modal open={isOpen} onClose={onClose} size="lg">
        <div className="text-center py-12">
          <p className="text-muted-foreground">Subscription not found</p>
        </div>
      </Modal>
    );
  }

  const plan = plans.find((p) => p._id === subscription.plan_id);

  const getStatusVariant = (status: string) => {
    switch (status) {
      case 'active':
        return 'accent';
      case 'trial':
        return 'accent';
      case 'paused':
        return 'outline';
      case 'cancelled':
        return 'destructive';
      case 'expired':
        return 'outline';
      case 'grace_period':
        return 'destructive';
      default:
        return 'outline';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const calculateTotalPaid = () => {
    return (subscription.payment_history || [])
      .filter((p) => p.status === 'success')
      .reduce((sum, p) => sum + p.amount, 0);
  };

  const calculateTotalSavings = () => {
    if (!plan || !plan.discount_percentage) return 0;
    const totalPaid = calculateTotalPaid();
    return (totalPaid * plan.discount_percentage) / 100;
  };

  const handleCancel = async () => {
    try {
      await cancelMutation.mutateAsync(subscriptionId);
      showToast('Subscription cancelled successfully', 'success');
      setShowCancelConfirm(false);
      onClose();
    } catch (error: any) {
      showToast(
        error.response?.data?.detail || 'Failed to cancel subscription',
        'error'
      );
    }
  };

  const handlePause = async () => {
    try {
      await pauseMutation.mutateAsync(subscriptionId);
      showToast('Subscription paused successfully', 'success');
    } catch (error: any) {
      showToast(
        error.response?.data?.detail || 'Failed to pause subscription',
        'error'
      );
    }
  };

  const handleResume = async () => {
    try {
      await resumeMutation.mutateAsync(subscriptionId);
      showToast('Subscription resumed successfully', 'success');
    } catch (error: any) {
      showToast(
        error.response?.data?.detail || 'Failed to resume subscription',
        'error'
      );
    }
  };

  return (
    <Modal open={isOpen} onClose={onClose} size="lg">
      <div className="space-y-6">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-2xl font-bold">Subscription Details</h2>
            <p className="text-muted-foreground mt-1">
              {plan?.name || 'Unknown Plan'}
            </p>
          </div>
          <Badge variant={getStatusVariant(subscription.status)}>
            {subscription.status.charAt(0).toUpperCase() +
              subscription.status.slice(1)}
          </Badge>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="payments">Payments</TabsTrigger>
            <TabsTrigger value="history">History</TabsTrigger>
            <TabsTrigger value="benefits">Benefits</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-4">
            {/* Subscription Info */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Subscription Info</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Start Date</p>
                    <p className="font-medium">
                      {formatDate(subscription.start_date)}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">End Date</p>
                    <p className="font-medium">
                      {subscription.end_date
                        ? formatDate(subscription.end_date)
                        : 'N/A'}
                    </p>
                  </div>
                  {subscription.trial_end_date && (
                    <div>
                      <p className="text-sm text-muted-foreground">
                        Trial Ends
                      </p>
                      <p className="font-medium">
                        {formatDate(subscription.trial_end_date)}
                      </p>
                    </div>
                  )}
                  <div>
                    <p className="text-sm text-muted-foreground">Auto-Renew</p>
                    <p className="font-medium flex items-center gap-1">
                      {subscription.auto_renew ? (
                        <>
                          <CheckIcon
                            size={16}
                            className="text-green-500"
                          />
                          Enabled
                        </>
                      ) : (
                        <>
                          <XIcon size={16} className="text-red-500" />
                          Disabled
                        </>
                      )}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Plan Info */}
            {plan && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Plan Details</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-muted-foreground">Price</p>
                      <p className="text-2xl font-bold text-primary">
                        ${plan.price}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">
                        Billing Cycle
                      </p>
                      <p className="font-medium capitalize">
                        {plan.billing_cycle}
                      </p>
                    </div>
                    {plan.discount_percentage && (
                      <div>
                        <p className="text-sm text-muted-foreground">
                          Discount
                        </p>
                        <p className="font-medium text-green-600">
                          {plan.discount_percentage}% off services
                        </p>
                      </div>
                    )}
                  </div>

                  {plan.benefits && plan.benefits.length > 0 && (
                    <div className="pt-4 border-t border-border">
                      <p className="text-sm font-medium mb-2">Benefits:</p>
                      <ul className="space-y-1">
                        {plan.benefits.map((benefit: string, index: number) => (
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
                        ))}
                      </ul>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Summary */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Summary</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Total Paid</span>
                  <span className="font-medium">
                    {formatCurrency(calculateTotalPaid())}
                  </span>
                </div>
                {plan?.discount_percentage && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Total Savings</span>
                    <span className="font-medium text-green-600">
                      {formatCurrency(calculateTotalSavings())}
                    </span>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Payments Tab */}
          <TabsContent value="payments" className="space-y-4">
            {subscription.payment_history &&
            subscription.payment_history.length > 0 ? (
              <div className="space-y-2">
                {subscription.payment_history.map((payment: any, index: number) => (
                  <Card key={index}>
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex items-start gap-3">
                          <CreditCardIcon
                            size={20}
                            className="text-primary mt-1"
                          />
                          <div>
                            <p className="font-medium">
                              {formatCurrency(payment.amount)}
                            </p>
                            <p className="text-sm text-muted-foreground">
                              {formatDate(payment.date)}
                            </p>
                            {payment.transaction_id && (
                              <p className="text-xs text-muted-foreground mt-1">
                                ID: {payment.transaction_id}
                              </p>
                            )}
                          </div>
                        </div>
                        <Badge
                          variant={
                            payment.status === 'success' ? 'accent' : 'destructive'
                          }
                        >
                          {payment.status.charAt(0).toUpperCase() +
                            payment.status.slice(1)}
                        </Badge>
                      </div>
                      {payment.reason && (
                        <p className="text-sm text-muted-foreground mt-2">
                          {payment.reason}
                        </p>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <CreditCardIcon
                  size={32}
                  className="mx-auto text-muted-foreground mb-2"
                />
                <p className="text-muted-foreground">No payment history</p>
              </div>
            )}
          </TabsContent>

          {/* History Tab */}
          <TabsContent value="history" className="space-y-4">
            {subscription.renewal_history &&
            subscription.renewal_history.length > 0 ? (
              <div className="space-y-2">
                {subscription.renewal_history.map((renewal: any, index: number) => (
                  <Card key={index}>
                    <CardContent className="p-4">
                      <div className="flex items-start gap-3">
                        <HistoryIcon
                          size={20}
                          className="text-primary mt-1"
                        />
                        <div className="flex-1">
                          <p className="font-medium capitalize">
                            {renewal.type}
                          </p>
                          <p className="text-sm text-muted-foreground">
                            {formatDate(renewal.date)}
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <HistoryIcon
                  size={32}
                  className="mx-auto text-muted-foreground mb-2"
                />
                <p className="text-muted-foreground">No renewal history</p>
              </div>
            )}
          </TabsContent>

          {/* Benefits Tab */}
          <TabsContent value="benefits" className="space-y-4">
            {subscription.benefit_usage ? (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Benefit Usage</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <div className="flex justify-between mb-2">
                      <span className="text-sm font-medium">Usage</span>
                      <span className="text-sm text-muted-foreground">
                        {subscription.benefit_usage.usage_count} /{' '}
                        {subscription.benefit_usage.limit === -1
                          ? 'Unlimited'
                          : subscription.benefit_usage.limit}
                      </span>
                    </div>
                    {subscription.benefit_usage.limit !== -1 && (
                      <div className="w-full bg-muted rounded-full h-2">
                        <div
                          className="bg-primary h-2 rounded-full transition-all"
                          style={{
                            width: `${Math.min(
                              (subscription.benefit_usage.usage_count /
                                subscription.benefit_usage.limit) *
                                100,
                              100
                            )}%`,
                          }}
                        />
                      </div>
                    )}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Resets on{' '}
                    {formatDate(subscription.benefit_usage.cycle_start)}
                  </div>
                </CardContent>
              </Card>
            ) : (
              <div className="text-center py-8">
                <p className="text-muted-foreground">
                  No benefit usage tracking
                </p>
              </div>
            )}
          </TabsContent>
        </Tabs>

        {/* Actions */}
        <div className="flex gap-3 justify-end pt-4 border-t border-border">
          {subscription.status === 'active' && (
            <>
              <Button
                variant="outline"
                onClick={handlePause}
                disabled={pauseMutation.isPending}
              >
                Pause
              </Button>
              <Button
                variant="outline"
                onClick={() => onChangePlan?.(subscriptionId)}
              >
                Change Plan
              </Button>
            </>
          )}

          {subscription.status === 'paused' && (
            <Button
              variant="outline"
              onClick={handleResume}
              disabled={resumeMutation.isPending}
            >
              Resume
            </Button>
          )}

          {subscription.status !== 'cancelled' && (
            <>
              {!showCancelConfirm ? (
                <Button
                  variant="destructive"
                  onClick={() => setShowCancelConfirm(true)}
                >
                  Cancel Subscription
                </Button>
              ) : (
                <>
                  <Button
                    variant="outline"
                    onClick={() => setShowCancelConfirm(false)}
                  >
                    Keep Subscription
                  </Button>
                  <Button
                    variant="destructive"
                    onClick={handleCancel}
                    disabled={cancelMutation.isPending}
                  >
                    Confirm Cancel
                  </Button>
                </>
              )}
            </>
          )}

          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>
    </Modal>
  );
}
