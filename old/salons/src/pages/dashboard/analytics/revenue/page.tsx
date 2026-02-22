import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import {
  DollarIcon,
  TrendingUpIcon,
  AlertTriangleIcon,
  ArrowLeftIcon,
} from "@/components/icons";
import { useRevenueAnalytics } from "@/lib/api/hooks/useAnalytics-offline";
import { format, subDays } from "date-fns";
import { Link } from "react-router-dom";
import { ExportDropdown } from "@/components/analytics/export-dropdown";
import {
  exportRevenueToCSV,
  exportRevenueToExcel,
  exportRevenueToPDF,
} from "@/lib/utils/export-revenue";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip as ChartTooltip,
  Legend as ChartLegend,
} from "chart.js";
import { Line, Bar, Pie } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  ChartTooltip,
  ChartLegend,
);

const COLORS = [
  "hsl(var(--primary))",
  "hsl(var(--secondary))",
  "hsl(var(--accent))",
  "#8884d8",
  "#82ca9d",
  "#ffc658",
  "#ff7c7c",
  "#a78bfa",
];

export default function RevenueBreakdownPage() {
  const [dateRange, setDateRange] = useState({
    start_date: format(subDays(new Date(), 30), "yyyy-MM-dd"),
    end_date: format(new Date(), "yyyy-MM-dd"),
  });

  const {
    data: revenueData,
    isLoading,
    error,
  } = useRevenueAnalytics(dateRange);

  if (error) {
    return (
      <Alert variant="error">
        <AlertTriangleIcon size={20} />
        <div>
          <h3 className="font-semibold">Error loading revenue data</h3>
          <p className="text-sm">{error.message}</p>
        </div>
      </Alert>
    );
  }

  const revenueByMonth = (revenueData?.revenue_by_month || []) as Array<{
    date: string;
    revenue: number;
    total?: number;
  }>;
  const revenueByService = (revenueData?.revenue_by_service || []) as Array<{
    service_name: string;
    revenue: number;
  }>;

  const handleExport = async (format: "csv" | "excel" | "pdf") => {
    if (!revenueData) return;

    const options = {
      filename: `revenue-report-${new Date().getTime()}`,
      dateRange,
      salonName: "Kenikool Salon", // TODO: Get from tenant context
    };

    try {
      switch (format) {
        case "csv":
          exportRevenueToCSV(revenueData, options);
          break;
        case "excel":
          await exportRevenueToExcel(revenueData, options);
          break;
        case "pdf":
          await exportRevenueToPDF(revenueData, options);
          break;
      }
    } catch (error) {
      console.error("Export failed:", error);
      showToast("Export failed. Please try again.", "error");
    }
  };

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
              Revenue Breakdown
            </h1>
            <p className="text-muted-foreground">
              Detailed revenue analysis and trends
            </p>
          </div>
        </div>
        <ExportDropdown
          options={[
            { label: "Export as PDF", onClick: () => handleExport("pdf") },
            { label: "Export as Excel", onClick: () => handleExport("excel") },
            { label: "Export as CSV", onClick: () => handleExport("csv") },
          ]}
        />
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
            <Button
              variant="outline"
              size="sm"
              onClick={() =>
                setDateRange({
                  start_date: format(subDays(new Date(), 90), "yyyy-MM-dd"),
                  end_date: format(new Date(), "yyyy-MM-dd"),
                })
              }
            >
              Last 90 Days
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
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="p-6">
              <div className="flex items-center gap-2 mb-2">
                <DollarIcon size={16} className="text-muted-foreground" />
                <span className="text-sm text-muted-foreground">
                  Total Revenue
                </span>
              </div>
              <p className="text-3xl font-bold text-foreground">
                ₦{(revenueData?.total_revenue || 0).toLocaleString()}
              </p>
            </Card>

            <Card className="p-6">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUpIcon size={16} className="text-muted-foreground" />
                <span className="text-sm text-muted-foreground">
                  Average Daily Revenue
                </span>
              </div>
              <p className="text-3xl font-bold text-foreground">
                ₦
                {revenueByMonth.length > 0
                  ? Math.round(
                      (revenueData?.total_revenue || 0) / revenueByMonth.length,
                    ).toLocaleString()
                  : 0}
              </p>
            </Card>

            <Card className="p-6">
              <div className="flex items-center gap-2 mb-2">
                <DollarIcon size={16} className="text-muted-foreground" />
                <span className="text-sm text-muted-foreground">
                  Highest Revenue Day
                </span>
              </div>
              <p className="text-3xl font-bold text-foreground">
                ₦
                {revenueByMonth.length > 0
                  ? Math.max(
                      ...revenueByMonth.map(
                        (d: { revenue?: number; total?: number }) =>
                          d.revenue || d.total || 0,
                      ),
                    ).toLocaleString()
                  : 0}
              </p>
            </Card>
          </div>

          {/* Revenue Trend Chart */}
          <Card className="p-6">
            <h2 className="text-lg font-semibold text-foreground mb-4">
              Revenue Trend
            </h2>
            <div style={{ height: "400px" }}>
              <Line
                data={{
                  labels: revenueByMonth.map((d: { date: string }) => {
                    try {
                      return format(new Date(d.date), "MMM dd");
                    } catch {
                      return d.date;
                    }
                  }),
                  datasets: [
                    {
                      label: "Revenue",
                      data: revenueByMonth.map(
                        (d: { revenue: number }) => d.revenue,
                      ),
                      borderColor: "hsl(var(--primary))",
                      backgroundColor: "hsl(var(--primary))",
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
                      ticks: {
                        callback: (value) => `₦${value.toLocaleString()}`,
                      },
                    },
                  },
                  plugins: {
                    tooltip: {
                      callbacks: {
                        label: (context) =>
                          `Revenue: ₦${(
                            context.parsed.y ?? 0
                          ).toLocaleString()}`,
                      },
                    },
                  },
                }}
              />
            </div>
          </Card>

          {/* Revenue by Service */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="p-6">
              <h2 className="text-lg font-semibold text-foreground mb-4">
                Revenue by Service (Bar Chart)
              </h2>
              <div style={{ height: "300px" }}>
                <Bar
                  data={{
                    labels: revenueByService.map(
                      (d: { service_name: string }) => d.service_name,
                    ),
                    datasets: [
                      {
                        label: "Revenue",
                        data: revenueByService.map(
                          (d: { revenue: number }) => d.revenue,
                        ),
                        backgroundColor: "hsl(var(--primary))",
                      },
                    ],
                  }}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    indexAxis: "x",
                    scales: {
                      y: {
                        beginAtZero: true,
                        ticks: {
                          callback: (value) => `₦${value.toLocaleString()}`,
                        },
                      },
                    },
                    plugins: {
                      tooltip: {
                        callbacks: {
                          label: (context) =>
                            `Revenue: ₦${(
                              context.parsed.y ?? 0
                            ).toLocaleString()}`,
                        },
                      },
                    },
                  }}
                />
              </div>
            </Card>

            <Card className="p-6">
              <h2 className="text-lg font-semibold text-foreground mb-4">
                Revenue Distribution (Pie Chart)
              </h2>
              <div style={{ height: "300px" }}>
                <Pie
                  data={{
                    labels: revenueByService.map(
                      (d: { service_name: string }) => d.service_name,
                    ),
                    datasets: [
                      {
                        data: revenueByService.map(
                          (d: { revenue: number }) => d.revenue,
                        ),
                        backgroundColor: COLORS,
                      },
                    ],
                  }}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      tooltip: {
                        callbacks: {
                          label: (context) => {
                            const label = context.label || "";
                            const value = context.parsed || 0;
                            return `${label}: ₦${value.toLocaleString()}`;
                          },
                        },
                      },
                    },
                  }}
                />
              </div>
            </Card>
          </div>

          {/* Service Revenue Table */}
          <Card className="p-6">
            <h2 className="text-lg font-semibold text-foreground mb-4">
              Service Revenue Details
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-[var(--border)]">
                    <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">
                      Service
                    </th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">
                      Revenue
                    </th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">
                      % of Total
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {revenueByService.map(
                    (
                      service: { service_name: string; revenue: number },
                      index: number,
                    ) => (
                      <tr
                        key={index}
                        className="border-b border-[var(--border)] hover:bg-muted/50"
                      >
                        <td className="py-3 px-4 text-foreground">
                          {service.service_name}
                        </td>
                        <td className="py-3 px-4 text-right text-foreground font-medium">
                          ₦{service.revenue.toLocaleString()}
                        </td>
                        <td className="py-3 px-4 text-right text-muted-foreground">
                          {revenueData?.total_revenue
                            ? (
                                (service.revenue / revenueData.total_revenue) *
                                100
                              ).toFixed(1)
                            : 0}
                          %
                        </td>
                      </tr>
                    ),
                  )}
                </tbody>
              </table>
            </div>
          </Card>
        </>
      )}
    </div>
  );
}
