'use client';

import { useState, useMemo } from 'react';
import { useGetAnalytics, useGetSubscriptions, useGetPlans } from '@/lib/api/hooks/useMemberships';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  TrendingUpIcon,
  UsersIcon,
  DollarSignIcon,
  PercentIcon,
  DownloadIcon,
} from '@/components/icons';
import { Spinner } from '@/components/ui/spinner';

interface MembershipAnalyticsProps {
  className?: string;
}

export function MembershipAnalytics({ className }: MembershipAnalyticsProps) {
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const { data: analytics, isLoading: analyticsLoading } = useGetAnalytics(
    startDate,
    endDate
  );
  const { data: subscriptions = [] } = useGetSubscriptions();
  const { data: plans = [] } = useGetPlans();

  const statusDistribution = useMemo(() => {
    const distribution: Record<string, number> = {
      active: 0,
      paused: 0,
      cancelled: 0,
      expired: 0,
      trial: 0,
      grace_period: 0,
    };

    subscriptions.forEach((sub) => {
      if (sub.status in distribution) {
        distribution[sub.status]++;
      }
    });

    return distribution;
  }, [subscriptions]);

  const revenueByPlan = useMemo(() => {
    const revenue: Record<string, { name: string; revenue: number; count: number }> = {};

    subscriptions.forEach((sub) => {
      const plan = plans.find((p) => p._id === sub.plan_id);
      if (plan) {
        if (!revenue[sub.plan_id]) {
          revenue[sub.plan_id] = { name: plan.name, revenue: 0, count: 0 };
        }
        const paymentSum = (sub.payment_history || [])
          .filter((p) => p.status === 'success')
          .reduce((sum, p) => sum + p.amount, 0);
        revenue[sub.plan_id].revenue += paymentSum;
        revenue[sub.plan_id].count++;
      }
    });

    return Object.values(revenue).sort((a, b) => b.revenue - a.revenue);
  }, [subscriptions, plans]);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const handleExport = () => {
    const data = {
      mrr: analytics?.mrr || 0,
      arr: analytics?.arr || 0,
      activeSubscribers: analytics?.active_subscribers || 0,
      churnRate: analytics?.churn_rate || 0,
      revenueByPlan,
      statusDistribution,
      exportedAt: new Date().toISOString(),
    };

    const csv = [
      ['Membership Analytics Report'],
      ['Exported at', new Date().toLocaleString()],
      [],
      ['Metric', 'Value'],
      ['MRR', formatCurrency(data.mrr)],
      ['ARR', formatCurrency(data.arr)],
      ['Active Subscribers', data.activeSubscribers],
      ['Churn Rate', `${data.churnRate}%`],
      [],
      ['Revenue by Plan'],
      ['Plan Name', 'Revenue', 'Subscribers'],
      ...data.revenueByPlan.map((p) => [p.name, formatCurrency(p.revenue), p.count]),
      [],
      ['Status Distribution'],
      ['Status', 'Count'],
      ...Object.entries(data.statusDistribution).map(([status, count]) => [
        status,
        count,
      ]),
    ]
      .map((row) => row.map((cell) => `"${cell}"`).join(','))
      .join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `membership-analytics-${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  if (analyticsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Date Range Filter */}
      <div className="flex gap-4 items-end">
        <div className="flex-1">
          <label className="text-sm font-medium">Start Date</label>
          <Input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
          />
        </div>
        <div className="flex-1">
          <label className="text-sm font-medium">End Date</label>
          <Input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
          />
        </div>
        <Button
          variant="outline"
          onClick={() => {
            setStartDate('');
            setEndDate('');
          }}
        >
          Clear
        </Button>
        <Button onClick={handleExport} className="gap-2">
          <DownloadIcon size={18} />
          Export
        </Button>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-muted-foreground">MRR</p>
                <p className="text-3xl font-bold text-primary mt-2">
                  {formatCurrency(analytics?.mrr || 0)}
                </p>
              </div>
              <DollarSignIcon
                size={24}
                className="text-primary/50"
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-muted-foreground">ARR</p>
                <p className="text-3xl font-bold text-green-600 mt-2">
                  {formatCurrency(analytics?.arr || 0)}
                </p>
              </div>
              <TrendingUpIcon
                size={24}
                className="text-green-600/50"
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Active Subscribers</p>
                <p className="text-3xl font-bold mt-2">
                  {analytics?.active_subscribers || 0}
                </p>
              </div>
              <UsersIcon
                size={24}
                className="text-blue-600/50"
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Churn Rate</p>
                <p className="text-3xl font-bold text-red-600 mt-2">
                  {(analytics?.churn_rate || 0).toFixed(1)}%
                </p>
              </div>
              <PercentIcon
                size={24}
                className="text-red-600/50"
              />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Growth Metrics */}
      {analytics?.subscriber_growth && (
        <Card>
          <CardHeader>
            <CardTitle>Subscriber Growth</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Current Month</p>
                <p className="text-2xl font-bold">
                  {analytics.subscriber_growth.current_month}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Last Month</p>
                <p className="text-2xl font-bold">
                  {analytics.subscriber_growth.last_month}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Growth Rate</p>
                <p className="text-2xl font-bold text-green-600">
                  +{(analytics.subscriber_growth.growth_rate || 0).toFixed(1)}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Revenue by Plan */}
      {revenueByPlan.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Revenue by Plan</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {revenueByPlan.map((plan) => (
                <div key={plan.name} className="flex items-center justify-between">
                  <div className="flex-1">
                    <p className="font-medium">{plan.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {plan.count} subscriber{plan.count !== 1 ? 's' : ''}
                    </p>
                  </div>
                  <p className="font-bold text-lg">
                    {formatCurrency(plan.revenue)}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Status Distribution */}
      <Card>
        <CardHeader>
          <CardTitle>Subscription Status Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {Object.entries(statusDistribution).map(([status, count]) => (
              <div key={status} className="p-4 bg-accent rounded-lg">
                <p className="text-sm text-muted-foreground capitalize">
                  {status}
                </p>
                <p className="text-2xl font-bold mt-2">{count}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Additional Metrics */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Average Subscription Lifetime</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">
                {analytics.average_lifetime_days || 0} days
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Trial Conversion Rate</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold text-green-600">
                {(analytics.trial_conversion_rate || 0).toFixed(1)}%
              </p>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
