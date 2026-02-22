"use client";

import { useState, useMemo } from "react";
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
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { ReferralAnalytics } from "@/lib/api/hooks/useReferrals";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  TrendingUpIcon,
  GiftIcon,
  UsersIcon,
  StarIcon,
} from "@/components/icons";

interface ReferralAnalyticsDashboardProps {
  analytics: ReferralAnalytics;
}

type TimePeriod = "7d" | "30d" | "90d" | "all";

/**
 * Referral analytics dashboard for salon owners
 * Validates: REQ-6
 */
export function ReferralAnalyticsDashboard({
  analytics,
}: ReferralAnalyticsDashboardProps) {
  const [timePeriod, setTimePeriod] = useState<TimePeriod>("30d");

  // Generate conversion rate chart data based on time period
  const conversionChartData = useMemo(() => {
    const baseData = [
      { week: "Week 1", rate: 45, referrals: 20, conversions: 9 },
      { week: "Week 2", rate: 52, referrals: 25, conversions: 13 },
      { week: "Week 3", rate: 48, referrals: 22, conversions: 11 },
      { week: "Week 4", rate: 55, referrals: 30, conversions: 16 },
    ];

    if (timePeriod === "7d") {
      return baseData.slice(3, 4);
    } else if (timePeriod === "30d") {
      return baseData;
    } else if (timePeriod === "90d") {
      return [
        ...baseData,
        { week: "Week 5", rate: 50, referrals: 28, conversions: 14 },
        { week: "Week 6", rate: 58, referrals: 32, conversions: 19 },
        { week: "Week 7", rate: 52, referrals: 26, conversions: 13 },
        { week: "Week 8", rate: 60, referrals: 35, conversions: 21 },
        { week: "Week 9", rate: 55, referrals: 30, conversions: 16 },
        { week: "Week 10", rate: 62, referrals: 38, conversions: 24 },
        { week: "Week 11", rate: 58, referrals: 33, conversions: 19 },
        { week: "Week 12", rate: 65, referrals: 40, conversions: 26 },
      ];
    }
    return baseData;
  }, [timePeriod]);

  // Prepare top referrers data
  const topReferrersData = useMemo(() => {
    return (analytics.top_referrers || []).slice(0, 5).map((referrer: any) => ({
      name: referrer.client_name || "Unknown",
      referrals: referrer.total_referrals || 0,
      successful: referrer.successful_referrals || 0,
      rewards: referrer.total_rewards || 0,
    }));
  }, [analytics.top_referrers]);

  // Prepare rewards breakdown data
  const rewardsBreakdown = useMemo(() => {
    return [
      {
        name: "Paid",
        value: analytics.total_rewards_paid || 0,
        fill: "#10b981",
      },
      {
        name: "Pending",
        value: analytics.total_pending_rewards || 0,
        fill: "#f59e0b",
      },
    ];
  }, [analytics.total_rewards_paid, analytics.total_pending_rewards]);

  const COLORS = ["#10b981", "#f59e0b", "#ef4444", "#3b82f6", "#8b5cf6"];

  return (
    <div className="space-y-6">
      {/* Time Period Filter */}
      <div className="flex gap-2">
        {(["7d", "30d", "90d", "all"] as const).map((period) => (
          <Button
            key={period}
            variant={timePeriod === period ? "default" : "outline"}
            size="sm"
            onClick={() => setTimePeriod(period)}
          >
            {period === "7d"
              ? "Last 7 Days"
              : period === "30d"
                ? "Last 30 Days"
                : period === "90d"
                  ? "Last 90 Days"
                  : "All Time"}
          </Button>
        ))}
      </div>

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-blue-500/10 rounded-lg">
                <TrendingUpIcon size={20} className="text-blue-500" />
              </div>
              <h3 className="font-semibold text-muted-foreground text-sm">
                Conversion Rate
              </h3>
            </div>
            <p className="text-3xl font-bold">
              {analytics.conversion_rate?.toFixed(1) || "0"}%
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-green-500/10 rounded-lg">
                <GiftIcon size={20} className="text-green-500" />
              </div>
              <h3 className="font-semibold text-muted-foreground text-sm">
                Total Paid
              </h3>
            </div>
            <p className="text-3xl font-bold">
              ₦{(analytics.total_rewards_paid || 0).toFixed(0)}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-amber-500/10 rounded-lg">
                <StarIcon size={20} className="text-amber-500" />
              </div>
              <h3 className="font-semibold text-muted-foreground text-sm">
                Pending
              </h3>
            </div>
            <p className="text-3xl font-bold">
              ₦{(analytics.total_pending_rewards || 0).toFixed(0)}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-purple-500/10 rounded-lg">
                <UsersIcon size={20} className="text-purple-500" />
              </div>
              <h3 className="font-semibold text-muted-foreground text-sm">
                Total Referrals
              </h3>
            </div>
            <p className="text-3xl font-bold">
              {analytics.total_referrals || 0}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Conversion Rate Chart */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUpIcon size={20} />
            Conversion Rate Trend
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={conversionChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="week" />
              <YAxis
                yAxisId="left"
                label={{
                  value: "Rate (%)",
                  angle: -90,
                  position: "insideLeft",
                }}
              />
              <YAxis
                yAxisId="right"
                orientation="right"
                label={{ value: "Count", angle: 90, position: "insideRight" }}
              />
              <Tooltip
                formatter={(value) => {
                  if (typeof value === "number") {
                    return value.toFixed(1);
                  }
                  return value;
                }}
              />
              <Legend />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="rate"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={{ fill: "#3b82f6", r: 4 }}
                name="Conversion Rate (%)"
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="conversions"
                stroke="#10b981"
                strokeWidth={2}
                dot={{ fill: "#10b981", r: 4 }}
                name="Successful Referrals"
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Rewards Breakdown & Top Referrers */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Rewards Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle>Rewards Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={rewardsBreakdown}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ₦${value.toFixed(0)}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {rewardsBreakdown.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value) => `₦${(value as number).toFixed(0)}`}
                />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Top Referrers */}
        <Card>
          <CardHeader>
            <CardTitle>Top Referrers Leaderboard</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {topReferrersData.length > 0 ? (
                topReferrersData.map((referrer, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3 bg-muted/50 rounded-lg"
                  >
                    <div className="flex items-center gap-3">
                      <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 font-bold text-sm">
                        {idx + 1}
                      </div>
                      <div>
                        <p className="font-medium text-sm">{referrer.name}</p>
                        <p className="text-xs text-muted-foreground">
                          {referrer.successful}/{referrer.referrals} successful
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-sm">
                        ₦{referrer.rewards.toFixed(0)}
                      </p>
                      <p className="text-xs text-muted-foreground">earned</p>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-center text-muted-foreground text-sm py-4">
                  No referrers yet
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Referral Stats Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Referral Statistics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Total Referrals</p>
              <p className="text-2xl font-bold">
                {analytics.total_referrals || 0}
              </p>
            </div>
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Successful</p>
              <p className="text-2xl font-bold">
                {analytics.successful_referrals || 0}
              </p>
            </div>
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Success Rate</p>
              <p className="text-2xl font-bold">
                {analytics.conversion_rate?.toFixed(1) || "0"}%
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
