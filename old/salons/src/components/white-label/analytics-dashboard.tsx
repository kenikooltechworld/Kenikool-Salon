"use client";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useState } from "react";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
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
import { Download, TrendingUp, Users, Eye, Zap } from "lucide-react";

export interface WhiteLabelAnalytics {
  domain: string;
  period: string;
  traffic: {
    date: string;
    visits: number;
    uniqueVisitors: number;
  }[];
  performance: {
    metric: string;
    value: number;
    change: number;
  }[];
  conversions: {
    source: string;
    bookings: number;
    revenue: number;
  }[];
  emailMetrics: {
    sent: number;
    opened: number;
    clicked: number;
  };
}

interface AnalyticsDashboardProps {
  analytics?: WhiteLabelAnalytics;
  isLoading?: boolean;
  onExport?: () => Promise<void>;
  useHooks?: boolean;
}

const COLORS = ["#FF6B6B", "#4ECDC4", "#FFE66D", "#95E1D3", "#F38181"];

const SAMPLE_ANALYTICS: WhiteLabelAnalytics = {
  domain: "example.salon.com",
  period: "Last 30 days",
  traffic: [
    { date: "Day 1", visits: 120, uniqueVisitors: 95 },
    { date: "Day 5", visits: 180, uniqueVisitors: 140 },
    { date: "Day 10", visits: 220, uniqueVisitors: 170 },
    { date: "Day 15", visits: 280, uniqueVisitors: 210 },
    { date: "Day 20", visits: 320, uniqueVisitors: 240 },
    { date: "Day 25", visits: 380, uniqueVisitors: 290 },
    { date: "Day 30", visits: 420, uniqueVisitors: 320 },
  ],
  performance: [
    { metric: "Avg Page Load Time", value: 1.2, change: -15 },
    { metric: "Bounce Rate", value: 32, change: -8 },
    { metric: "Avg Session Duration", value: 3.5, change: 22 },
    { metric: "Conversion Rate", value: 4.2, change: 18 },
  ],
  conversions: [
    { source: "Direct", bookings: 45, revenue: 2250 },
    { source: "Organic Search", bookings: 38, revenue: 1900 },
    { source: "Social Media", bookings: 28, revenue: 1400 },
    { source: "Email", bookings: 22, revenue: 1100 },
    { source: "Referral", bookings: 15, revenue: 750 },
  ],
  emailMetrics: {
    sent: 1250,
    opened: 487,
    clicked: 156,
  },
};

export function AnalyticsDashboard({
  analytics = SAMPLE_ANALYTICS,
  isLoading = false,
  onExport,
  useHooks = false,
}: AnalyticsDashboardProps) {
  const [exporting, setExporting] = useState(false);

  const handleExport = async () => {
    if (!onExport) return;
    try {
      setExporting(true);
      await onExport();
      showToast("Report exported successfully", "success");
    } catch (error) {
      console.error("Export failed:", error);
      showToast("Failed to export report", "error");
    } finally {
      setExporting(false);
    }
  };

  const emailOpenRate = (
    (analytics.emailMetrics.opened / analytics.emailMetrics.sent) *
    100
  ).toFixed(1);
  const emailClickRate = (
    (analytics.emailMetrics.clicked / analytics.emailMetrics.sent) *
    100
  ).toFixed(1);

  const totalVisits = analytics.traffic.reduce((sum, d) => sum + d.visits, 0);
  const totalBookings = analytics.conversions.reduce(
    (sum, c) => sum + c.bookings,
    0,
  );
  const totalRevenue = analytics.conversions.reduce(
    (sum, c) => sum + c.revenue,
    0,
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">White Label Analytics</h2>
          <p className="text-gray-600 mt-1">
            Domain: <span className="font-semibold">{analytics.domain}</span> •{" "}
            {analytics.period}
          </p>
        </div>
        {onExport && (
          <Button onClick={handleExport} disabled={exporting} className="gap-2">
            <Download className="h-4 w-4" />
            {exporting ? "Exporting..." : "Export Report"}
          </Button>
        )}
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Visits</p>
              <p className="text-2xl font-bold mt-1">{totalVisits}</p>
            </div>
            <Eye className="h-8 w-8 text-blue-500 opacity-20" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Bookings</p>
              <p className="text-2xl font-bold mt-1">{totalBookings}</p>
            </div>
            <Zap className="h-8 w-8 text-yellow-500 opacity-20" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Revenue</p>
              <p className="text-2xl font-bold mt-1">${totalRevenue}</p>
            </div>
            <TrendingUp className="h-8 w-8 text-green-500 opacity-20" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Conversion Rate</p>
              <p className="text-2xl font-bold mt-1">
                {((totalBookings / totalVisits) * 100).toFixed(1)}%
              </p>
            </div>
            <Users className="h-8 w-8 text-purple-500 opacity-20" />
          </div>
        </Card>
      </div>

      {/* Charts */}
      <Tabs defaultValue="traffic" className="space-y-4">
        <TabsList>
          <TabsTrigger value="traffic">Traffic</TabsTrigger>
          <TabsTrigger value="conversions">Conversions</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="email">Email Metrics</TabsTrigger>
        </TabsList>

        {/* Traffic Chart */}
        <TabsContent value="traffic">
          <Card className="p-4">
            <h3 className="font-semibold mb-4">Traffic Over Time</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={analytics.traffic}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="visits"
                  stroke="#FF6B6B"
                  name="Total Visits"
                />
                <Line
                  type="monotone"
                  dataKey="uniqueVisitors"
                  stroke="#4ECDC4"
                  name="Unique Visitors"
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </TabsContent>

        {/* Conversions Chart */}
        <TabsContent value="conversions">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Bookings by Source */}
            <Card className="p-4">
              <h3 className="font-semibold mb-4">Bookings by Source</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={analytics.conversions}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="source" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="bookings" fill="#FF6B6B" />
                </BarChart>
              </ResponsiveContainer>
            </Card>

            {/* Revenue by Source */}
            <Card className="p-4">
              <h3 className="font-semibold mb-4">Revenue by Source</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={analytics.conversions}
                    dataKey="revenue"
                    nameKey="source"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    label
                  >
                    {analytics.conversions.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={COLORS[index % COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </Card>
          </div>

          {/* Conversion Details Table */}
          <Card className="p-4 mt-4">
            <h3 className="font-semibold mb-4">Conversion Details</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="border-b">
                  <tr>
                    <th className="text-left py-2 px-2">Source</th>
                    <th className="text-right py-2 px-2">Bookings</th>
                    <th className="text-right py-2 px-2">Revenue</th>
                    <th className="text-right py-2 px-2">Avg Value</th>
                  </tr>
                </thead>
                <tbody>
                  {analytics.conversions.map((conversion) => (
                    <tr
                      key={conversion.source}
                      className="border-b hover:bg-gray-50"
                    >
                      <td className="py-2 px-2">{conversion.source}</td>
                      <td className="text-right py-2 px-2">
                        {conversion.bookings}
                      </td>
                      <td className="text-right py-2 px-2">
                        ${conversion.revenue}
                      </td>
                      <td className="text-right py-2 px-2">
                        ${(conversion.revenue / conversion.bookings).toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </TabsContent>

        {/* Performance Chart */}
        <TabsContent value="performance">
          <Card className="p-4">
            <h3 className="font-semibold mb-4">Performance Metrics</h3>
            <div className="space-y-4">
              {analytics.performance.map((perf) => (
                <div
                  key={perf.metric}
                  className="flex items-center justify-between"
                >
                  <div>
                    <p className="font-medium">{perf.metric}</p>
                    <p className="text-2xl font-bold mt-1">
                      {perf.metric.includes("Rate") ||
                      perf.metric.includes("Duration")
                        ? perf.value.toFixed(1)
                        : perf.value}
                      {perf.metric.includes("Rate") ? "%" : "s"}
                    </p>
                  </div>
                  <div
                    className={`text-lg font-semibold ${
                      perf.change > 0 ? "text-green-600" : "text-red-600"
                    }`}
                  >
                    {perf.change > 0 ? "+" : ""}
                    {perf.change}%
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </TabsContent>

        {/* Email Metrics */}
        <TabsContent value="email">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="p-4">
              <p className="text-sm text-gray-600">Emails Sent</p>
              <p className="text-3xl font-bold mt-2">
                {analytics.emailMetrics.sent}
              </p>
            </Card>

            <Card className="p-4">
              <p className="text-sm text-gray-600">Open Rate</p>
              <p className="text-3xl font-bold mt-2">{emailOpenRate}%</p>
              <p className="text-xs text-gray-500 mt-1">
                {analytics.emailMetrics.opened} opens
              </p>
            </Card>

            <Card className="p-4">
              <p className="text-sm text-gray-600">Click Rate</p>
              <p className="text-3xl font-bold mt-2">{emailClickRate}%</p>
              <p className="text-xs text-gray-500 mt-1">
                {analytics.emailMetrics.clicked} clicks
              </p>
            </Card>
          </div>

          {/* Email Funnel */}
          <Card className="p-4 mt-4">
            <h3 className="font-semibold mb-4">Email Funnel</h3>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between mb-1">
                  <span>Sent</span>
                  <span className="font-semibold">
                    {analytics.emailMetrics.sent}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full"
                    style={{ width: "100%" }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between mb-1">
                  <span>Opened</span>
                  <span className="font-semibold">
                    {analytics.emailMetrics.opened}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-green-500 h-2 rounded-full"
                    style={{
                      width: `${(analytics.emailMetrics.opened / analytics.emailMetrics.sent) * 100}%`,
                    }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between mb-1">
                  <span>Clicked</span>
                  <span className="font-semibold">
                    {analytics.emailMetrics.clicked}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-purple-500 h-2 rounded-full"
                    style={{
                      width: `${(analytics.emailMetrics.clicked / analytics.emailMetrics.sent) * 100}%`,
                    }}
                  />
                </div>
              </div>
            </div>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Monthly Reports */}
      <Card className="p-4">
        <h3 className="font-semibold mb-4">Monthly Reports</h3>
        <div className="space-y-2">
          {["January", "February", "March", "April", "May", "June"].map(
            (month) => (
              <div
                key={month}
                className="flex items-center justify-between p-2 hover:bg-gray-50 rounded"
              >
                <span>{month} 2024</span>
                <Button size="sm" variant="ghost">
                  Download
                </Button>
              </div>
            ),
          )}
        </div>
      </Card>
    </div>
  );
}
