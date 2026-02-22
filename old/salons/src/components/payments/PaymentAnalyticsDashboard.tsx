"use client";

import React, { useState } from "react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { usePaymentAnalytics } from "@/lib/api/hooks/usePaymentAnalytics";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertCircle, Download } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";

interface DateRange {
  from: string;
  to: string;
}

const COLORS = [
  "#3b82f6",
  "#ef4444",
  "#10b981",
  "#f59e0b",
  "#8b5cf6",
  "#ec4899",
  "#14b8a6",
  "#f97316",
];

export function PaymentAnalyticsDashboard() {
  const [dateRange, setDateRange] = useState<{
    period: "7days" | "30days" | "90days" | "custom";
    from?: string;
    to?: string;
  }>({
    period: "30days",
  });

  const { data: analytics, isLoading, error } = usePaymentAnalytics({
    period: dateRange.period,
    date_from: dateRange.from,
    date_to: dateRange.to,
  });

  const handleExport = () => {
    if (!analytics) return;

    const csvContent = generateCSV(analytics);
    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `payment-analytics-${new Date().toISOString().split("T")[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          Failed to load payment analytics. Please try again.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Date Range Selector */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Payment Analytics</h1>
        <div className="flex gap-2">
          {["7days", "30days", "90days"].map((period) => (
            <Button
              key={period}
              variant={dateRange.period === period ? "default" : "outline"}
              onClick={() =>
                setDateRange({
                  period: period as "7days" | "30days" | "90days",
                })
              }
            >
              {period === "7days"
                ? "Last 7 Days"
                : period === "30days"
                  ? "Last 30 Days"
                  : "Last 90 Days"}
            </Button>
          ))}
          <Button
            variant="outline"
            size="sm"
            onClick={handleExport}
            disabled={!analytics}
          >
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Key Metrics Cards */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <Card key={i}>
              <CardHeader className="pb-2">
                <Skeleton className="h-4 w-24" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-8 w-32" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : analytics ? (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Total Revenue
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                ${analytics.total_revenue.toFixed(2)}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Transactions
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {analytics.total_transactions}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Average Payment
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                ${analytics.average_payment.toFixed(2)}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Refund Rate
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {(analytics.refund_rate * 100).toFixed(1)}%
              </div>
            </CardContent>
          </Card>
        </div>
      ) : null}

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue Trends Chart */}
        {isLoading ? (
          <Card>
            <CardHeader>
              <Skeleton className="h-6 w-32" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-64 w-full" />
            </CardContent>
          </Card>
        ) : analytics && analytics.revenue_trends.length > 0 ? (
          <Card>
            <CardHeader>
              <CardTitle>Revenue Trends</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={analytics.revenue_trends}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip
                    formatter={(value) => `$${Number(value).toFixed(2)}`}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="amount"
                    stroke="#3b82f6"
                    name="Revenue"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        ) : null}

        {/* Payment Method Breakdown */}
        {isLoading ? (
          <Card>
            <CardHeader>
              <Skeleton className="h-6 w-32" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-64 w-full" />
            </CardContent>
          </Card>
        ) : analytics && analytics.payment_method_breakdown.length > 0 ? (
          <Card>
            <CardHeader>
              <CardTitle>Payment Methods</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={analytics.payment_method_breakdown}
                    dataKey="amount"
                    nameKey="method"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    label
                  >
                    {analytics.payment_method_breakdown.map((_, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={COLORS[index % COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(value) => `$${Number(value).toFixed(2)}`}
                  />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        ) : null}
      </div>

      {/* Gateway Performance Table */}
      {isLoading ? (
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-32" />
          </CardHeader>
          <CardContent>
            <Skeleton className="h-40 w-full" />
          </CardContent>
        </Card>
      ) : analytics && analytics.gateway_breakdown.length > 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>Gateway Performance</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2 px-4">Gateway</th>
                    <th className="text-right py-2 px-4">Amount</th>
                    <th className="text-right py-2 px-4">Transactions</th>
                    <th className="text-right py-2 px-4">Success Rate</th>
                  </tr>
                </thead>
                <tbody>
                  {analytics.gateway_breakdown.map((gateway) => (
                    <tr key={gateway.gateway} className="border-b">
                      <td className="py-2 px-4 font-medium">
                        {gateway.gateway}
                      </td>
                      <td className="text-right py-2 px-4">
                        ${gateway.amount.toFixed(2)}
                      </td>
                      <td className="text-right py-2 px-4">{gateway.count}</td>
                      <td className="text-right py-2 px-4">
                        {(gateway.success_rate * 100).toFixed(1)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      ) : null}

      {/* Failed Payments Analysis */}
      {isLoading ? (
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-32" />
          </CardHeader>
          <CardContent>
            <Skeleton className="h-40 w-full" />
          </CardContent>
        </Card>
      ) : analytics && analytics.failed_payment_count > 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>Failed Payments Analysis</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Failed Transactions</p>
                <p className="text-2xl font-bold">
                  {analytics.failed_payment_count}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Failed Amount</p>
                <p className="text-2xl font-bold">
                  ${analytics.failed_payment_amount.toFixed(2)}
                </p>
              </div>
            </div>

            {analytics.common_failure_reasons.length > 0 && (
              <div>
                <p className="text-sm font-medium mb-2">Common Reasons</p>
                <div className="space-y-2">
                  {analytics.common_failure_reasons.map((reason) => (
                    <div
                      key={reason.reason}
                      className="flex justify-between text-sm"
                    >
                      <span>{reason.reason}</span>
                      <span className="font-medium">{reason.count}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      ) : null}

      {/* Refund Statistics */}
      {isLoading ? (
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-32" />
          </CardHeader>
          <CardContent>
            <Skeleton className="h-24 w-full" />
          </CardContent>
        </Card>
      ) : analytics ? (
        <Card>
          <CardHeader>
            <CardTitle>Refund Statistics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-gray-600">Total Refunded</p>
                <p className="text-2xl font-bold">
                  ${analytics.total_refunded.toFixed(2)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Refund Count</p>
                <p className="text-2xl font-bold">{analytics.refund_count}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Refund Rate</p>
                <p className="text-2xl font-bold">
                  {(analytics.refund_rate * 100).toFixed(1)}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}
