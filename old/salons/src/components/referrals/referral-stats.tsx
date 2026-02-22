'use client';

import { useMemo } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { ReferralStats, ReferralDashboard } from "@/lib/api/hooks/useReferrals";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  UsersIcon,
  CheckCircleIcon,
  ClockIcon,
  GiftIcon,
  TrendingUpIcon,
} from "@/components/icons";

interface ReferralStatsProps {
  stats: ReferralStats;
  dashboard?: ReferralDashboard;
}

/**
 * Enhanced referral stats component with charts and analytics
 * Validates: REQ-6, REQ-11
 */
export function ReferralStatsComponent({ stats, dashboard }: ReferralStatsProps) {
  // Calculate conversion rate
  const conversionRate = useMemo(() => {
    if (stats.total_referrals === 0) return 0;
    return ((stats.successful_referrals / stats.total_referrals) * 100).toFixed(1);
  }, [stats]);

  // Generate earnings trend data (mock data - would come from backend in production)
  const earningsTrendData = useMemo(() => {
    return [
      { month: 'Jan', earnings: 0 },
      { month: 'Feb', earnings: 0 },
      { month: 'Mar', earnings: 0 },
      { month: 'Apr', earnings: 0 },
      { month: 'May', earnings: 0 },
      { month: 'Jun', earnings: stats.total_rewards },
    ];
  }, [stats.total_rewards]);

  // Prepare pending vs earned breakdown
  const breakdownData = useMemo(() => {
    return [
      {
        name: 'Earned',
        value: stats.total_rewards,
        fill: '#10b981',
      },
      {
        name: 'Pending',
        value: stats.total_rewards * 0.3, // Mock calculation
        fill: '#f59e0b',
      },
    ];
  }, [stats.total_rewards]);

  return (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-4">
        <div className="bg-card border border-border rounded-[var(--radius-lg)] p-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-primary/10 rounded-[var(--radius-md)]">
              <UsersIcon size={20} className="text-primary" />
            </div>
            <h3 className="font-semibold text-muted-foreground">
              Total Referrals
            </h3>
          </div>
          <p className="text-3xl font-bold">{stats.total_referrals}</p>
        </div>

        <div className="bg-card border border-border rounded-[var(--radius-lg)] p-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-green-500/10 rounded-[var(--radius-md)]">
              <CheckCircleIcon size={20} className="text-green-500" />
            </div>
            <h3 className="font-semibold text-muted-foreground">Successful</h3>
          </div>
          <p className="text-3xl font-bold">{stats.successful_referrals}</p>
        </div>

        <div className="bg-card border border-border rounded-[var(--radius-lg)] p-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-blue-500/10 rounded-[var(--radius-md)]">
              <TrendingUpIcon size={20} className="text-blue-500" />
            </div>
            <h3 className="font-semibold text-muted-foreground">
              Conversion Rate
            </h3>
          </div>
          <p className="text-3xl font-bold">{conversionRate}%</p>
        </div>

        <div className="bg-card border border-border rounded-[var(--radius-lg)] p-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-blue-500/10 rounded-[var(--radius-md)]">
              <GiftIcon size={20} className="text-blue-500" />
            </div>
            <h3 className="font-semibold text-muted-foreground">Total Rewards</h3>
          </div>
          <p className="text-3xl font-bold">₦{stats.total_rewards.toFixed(2)}</p>
        </div>
      </div>

      {/* Earnings Trend Chart */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUpIcon size={20} />
            Earnings Trend
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={earningsTrendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip formatter={(value) => `₦${value.toFixed(2)}`} />
              <Line
                type="monotone"
                dataKey="earnings"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={{ fill: '#3b82f6', r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Pending vs Earned Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle>Rewards Breakdown</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            {breakdownData.map((item) => (
              <div
                key={item.name}
                className="bg-muted/50 rounded-lg p-4 border border-border"
              >
                <div className="flex items-center gap-2 mb-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: item.fill }}
                  />
                  <p className="font-medium">{item.name}</p>
                </div>
                <p className="text-2xl font-bold">₦{item.value.toFixed(2)}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Recent Activity Feed */}
      {dashboard && dashboard.referral_history.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {dashboard.referral_history.slice(0, 5).map((item, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 bg-muted/50 rounded-lg"
                >
                  <div>
                    <p className="font-medium text-sm">
                      {item.referred_client_name}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {new Date(item.referred_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-sm">
                      ₦{item.reward_amount.toFixed(2)}
                    </p>
                    <p
                      className={`text-xs font-medium ${
                        item.status === 'completed'
                          ? 'text-green-600'
                          : item.status === 'pending'
                          ? 'text-yellow-600'
                          : 'text-red-600'
                      }`}
                    >
                      {item.status.charAt(0).toUpperCase() + item.status.slice(1)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
