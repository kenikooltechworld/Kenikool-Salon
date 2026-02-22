import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import {
  UsersIcon,
  TrendingUpIcon,
  DollarIcon,
  AlertTriangleIcon,
  ArrowLeftIcon,
  DownloadIcon,
} from "@/components/icons";
import { useRetentionAnalytics } from "@/lib/api/hooks/useAnalytics-offline";
import { format, subDays } from "date-fns";
import { Link } from "react-router-dom";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  PointElement,
  LineElement,
  Filler,
  Title,
  Tooltip as ChartTooltip,
  Legend as ChartLegend,
} from "chart.js";
import { Bar, Pie, Line } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  PointElement,
  LineElement,
  Filler,
  Title,
  ChartTooltip,
  ChartLegend
);

const COLORS = [
  "hsl(var(--primary))",
  "hsl(var(--secondary))",
  "hsl(var(--accent))",
  "#8884d8",
];

export default function ClientAnalyticsPage() {
  const [dateRange, setDateRange] = useState({
    start_date: format(subDays(new Date(), 30), "yyyy-MM-dd"),
    end_date: format(new Date(), "yyyy-MM-dd"),
  });

  const {
    data: retentionData,
    isLoading,
    error,
  } = useRetentionAnalytics(dateRange);

  if (error) {
    return (
      <Alert variant="error">
        <AlertTriangleIcon size={20} />
        <div>
          <h3 className="font-semibold">Error loading client data</h3>
          <p className="text-sm">{error.message}</p>
        </div>
      </Alert>
    );
  }

  // Mock data for demonstration (replace with actual API data)
  const clientSegments = [
    { name: "New Clients", value: retentionData?.new_clients || 0 },
    { name: "Returning Clients", value: retentionData?.returning_clients || 0 },
    { name: "At Risk", value: retentionData?.at_risk_clients || 0 },
    { name: "Churned", value: retentionData?.churned_clients || 0 },
  ];

  const lifetimeValueData = [
    { range: "₦0-10k", count: 45 },
    { range: "₦10k-25k", count: 32 },
    { range: "₦25k-50k", count: 18 },
    { range: "₦50k-100k", count: 12 },
    { range: "₦100k+", count: 8 },
  ];

  const visitFrequencyData = [
    { visits: "1 visit", count: 35 },
    { visits: "2-3 visits", count: 28 },
    { visits: "4-6 visits", count: 22 },
    { visits: "7-10 visits", count: 10 },
    { visits: "10+ visits", count: 5 },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link to="/dashboard/analytics">
            <Button variant="ghost" size="sm">
              <ArrowLeftIcon size={20} />
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-foreground">
              Client Analytics
            </h1>
            <p className="text-muted-foreground">
              Client behavior, retention, and lifetime value analysis
            </p>
          </div>
        </div>
        <Button>
          <DownloadIcon size={20} />
          Export Report
        </Button>
      </div>

      {/* Date Range Filter */}
      <Card className="p-4">
        <div className="flex flex-col md:flex-row gap-4 items-end">
          <div className="flex-1">
            <label className="block text-sm font-medium text-foreground mb-1">
              Start Date
            </label>
            <input
              type="date"
              value={dateRange.start_date}
              onChange={(e) =>
                setDateRange({ ...dateRange, start_date: e.target.value })
              }
              className="w-full px-3 py-2 border border-[var(--border)] rounded-lg bg-background text-foreground"
            />
          </div>
          <div className="flex-1">
            <label className="block text-sm font-medium text-foreground mb-1">
              End Date
            </label>
            <input
              type="date"
              value={dateRange.end_date}
              onChange={(e) =>
                setDateRange({ ...dateRange, end_date: e.target.value })
              }
              className="w-full px-3 py-2 border border-[var(--border)] rounded-lg bg-background text-foreground"
            />
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() =>
                setDateRange({
                  start_date: format(subDays(new Date(), 7), "yyyy-MM-dd"),
                  end_date: format(new Date(), "yyyy-MM-dd"),
                })
              }
            >
              Last 7 Days
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() =>
                setDateRange({
                  start_date: format(subDays(new Date(), 30), "yyyy-MM-dd"),
                  end_date: format(new Date(), "yyyy-MM-dd"),
                })
              }
            >
              Last 30 Days
            </Button>
          </div>
        </div>
      </Card>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Spinner />
        </div>
      ) : (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card className="p-6">
              <div className="flex items-center gap-2 mb-2">
                <UsersIcon size={16} className="text-muted-foreground" />
                <span className="text-sm text-muted-foreground">
                  Total Clients
                </span>
              </div>
              <p className="text-3xl font-bold text-foreground">
                {(retentionData?.total_clients || 0).toLocaleString()}
              </p>
            </Card>

            <Card className="p-6">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUpIcon size={16} className="text-muted-foreground" />
                <span className="text-sm text-muted-foreground">
                  Retention Rate
                </span>
              </div>
              <p className="text-3xl font-bold text-foreground">
                {(retentionData?.retention_rate || 0).toFixed(1)}%
              </p>
            </Card>

            <Card className="p-6">
              <div className="flex items-center gap-2 mb-2">
                <DollarIcon size={16} className="text-muted-foreground" />
                <span className="text-sm text-muted-foreground">
                  Avg. Lifetime Value
                </span>
              </div>
              <p className="text-3xl font-bold text-foreground">
                ₦{(retentionData?.avg_lifetime_value || 0).toLocaleString()}
              </p>
            </Card>

            <Card className="p-6">
              <div className="flex items-center gap-2 mb-2">
                <UsersIcon size={16} className="text-muted-foreground" />
                <span className="text-sm text-muted-foreground">
                  New Clients
                </span>
              </div>
              <p className="text-3xl font-bold text-foreground">
                {retentionData?.new_clients || 0}
              </p>
            </Card>
          </div>

          {/* Client Segments */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="p-6">
              <h2 className="text-lg font-semibold text-foreground mb-4">
                Client Segments
              </h2>
              <div style={{ height: "300px" }}>
                <Pie
                  data={{
                    labels: clientSegments.map((s) => s.name),
                    datasets: [
                      {
                        data: clientSegments.map((s) => s.value),
                        backgroundColor: COLORS,
                      },
                    ],
                  }}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                  }}
                />
              </div>
            </Card>

            <Card className="p-6">
              <h2 className="text-lg font-semibold text-foreground mb-4">
                Client Lifetime Value Distribution
              </h2>
              <div style={{ height: "300px" }}>
                <Bar
                  data={{
                    labels: lifetimeValueData.map((d) => d.range),
                    datasets: [
                      {
                        label: "Clients",
                        data: lifetimeValueData.map((d) => d.count),
                        backgroundColor: "hsl(var(--primary))",
                      },
                    ],
                  }}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                      y: {
                        beginAtZero: true,
                      },
                    },
                  }}
                />
              </div>
            </Card>
          </div>

          {/* Visit Frequency */}
          <Card className="p-6">
            <h2 className="text-lg font-semibold text-foreground mb-4">
              Visit Frequency Distribution
            </h2>
            <div style={{ height: "300px" }}>
              <Bar
                data={{
                  labels: visitFrequencyData.map((d) => d.visits),
                  datasets: [
                    {
                      label: "Clients",
                      data: visitFrequencyData.map((d) => d.count),
                      backgroundColor: "hsl(var(--secondary))",
                    },
                  ],
                }}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  scales: {
                    y: {
                      beginAtZero: true,
                    },
                  },
                }}
              />
            </div>
          </Card>

          {/* Retention Trend */}
          <Card className="p-6">
            <h2 className="text-lg font-semibold text-foreground mb-4">
              Client Retention Trend
            </h2>
            <div style={{ height: "300px" }}>
              <Line
                data={{
                  labels: (retentionData?.retention_by_month || []).map(
                    (d) => d.month
                  ),
                  datasets: [
                    {
                      label: "Retention Rate (%)",
                      data: (retentionData?.retention_by_month || []).map(
                        (d) => d.retention_rate
                      ),
                      borderColor: "hsl(var(--primary))",
                      backgroundColor: "hsla(var(--primary), 0.6)",
                      fill: true,
                      tension: 0.4,
                    },
                  ],
                }}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  scales: {
                    y: {
                      beginAtZero: true,
                    },
                  },
                }}
              />
            </div>
          </Card>

          {/* Client Insights */}
          <Card className="p-6">
            <h2 className="text-lg font-semibold text-foreground mb-4">
              Key Client Insights
            </h2>
            <div className="space-y-4">
              <div className="p-4 bg-muted/50 rounded-lg">
                <h3 className="font-medium text-foreground mb-1">
                  Average Visit Frequency
                </h3>
                <p className="text-sm text-muted-foreground">
                  Clients visit an average of{" "}
                  {(retentionData?.avg_visits_per_client || 0).toFixed(1)} times
                  per period
                </p>
              </div>
              <div className="p-4 bg-muted/50 rounded-lg">
                <h3 className="font-medium text-foreground mb-1">
                  Client Acquisition Cost
                </h3>
                <p className="text-sm text-muted-foreground">
                  Estimated cost per new client: ₦
                  {(retentionData?.acquisition_cost || 0).toLocaleString()}
                </p>
              </div>
              <div className="p-4 bg-muted/50 rounded-lg">
                <h3 className="font-medium text-foreground mb-1">Churn Risk</h3>
                <p className="text-sm text-muted-foreground">
                  {retentionData?.at_risk_clients || 0} clients haven't visited
                  in 60+ days and may be at risk of churning
                </p>
              </div>
            </div>
          </Card>
        </>
      )}
    </div>
  );
}
