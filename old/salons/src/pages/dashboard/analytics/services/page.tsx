import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import {
  CalendarIcon,
  DollarIcon,
  StarIcon,
  AlertTriangleIcon,
  ArrowLeftIcon,
  DownloadIcon,
} from "@/components/icons";
import { useServicePerformance } from "@/lib/api/hooks/useAnalytics-offline";
import { format, subDays } from "date-fns";
import { Link } from "react-router-dom";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Title,
  Tooltip as ChartTooltip,
  Legend as ChartLegend,
} from "chart.js";
import { Bar, Radar } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Title,
  ChartTooltip,
  ChartLegend
);

export default function ServiceAnalyticsPage() {
  const [dateRange, setDateRange] = useState({
    start_date: format(subDays(new Date(), 30), "yyyy-MM-dd"),
    end_date: format(new Date(), "yyyy-MM-dd"),
  });

  const { data: services, isLoading, error } = useServicePerformance(dateRange);

  if (error) {
    return (
      <Alert variant="error">
        <AlertTriangleIcon size={20} />
        <div>
          <h3 className="font-semibold">Error loading service data</h3>
          <p className="text-sm">{error.message}</p>
        </div>
      </Alert>
    );
  }

  const totalBookings =
    services?.reduce((sum, s) => sum + s.total_bookings, 0) || 0;
  const totalRevenue =
    services?.reduce((sum, s) => sum + s.total_revenue, 0) || 0;
  const avgRating =
    services && services.length > 0
      ? services.reduce((sum, s) => sum + (s.average_rating || 0), 0) /
        services.length
      : 0;

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
              Service Analytics
            </h1>
            <p className="text-muted-foreground">
              Detailed service performance and insights
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
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="p-6">
              <div className="flex items-center gap-2 mb-2">
                <CalendarIcon size={16} className="text-muted-foreground" />
                <span className="text-sm text-muted-foreground">
                  Total Bookings
                </span>
              </div>
              <p className="text-3xl font-bold text-foreground">
                {totalBookings.toLocaleString()}
              </p>
            </Card>

            <Card className="p-6">
              <div className="flex items-center gap-2 mb-2">
                <DollarIcon size={16} className="text-muted-foreground" />
                <span className="text-sm text-muted-foreground">
                  Total Revenue
                </span>
              </div>
              <p className="text-3xl font-bold text-foreground">
                ₦{totalRevenue.toLocaleString()}
              </p>
            </Card>

            <Card className="p-6">
              <div className="flex items-center gap-2 mb-2">
                <StarIcon size={16} className="text-muted-foreground" />
                <span className="text-sm text-muted-foreground">
                  Average Rating
                </span>
              </div>
              <p className="text-3xl font-bold text-foreground">
                {avgRating.toFixed(1)}
              </p>
            </Card>
          </div>

          {/* Bookings by Service */}
          <Card className="p-6">
            <h2 className="text-lg font-semibold text-foreground mb-4">
              Bookings by Service
            </h2>
            <div style={{ height: "400px" }}>
              <Bar
                data={{
                  labels: services?.map((s) => s.service_name) || [],
                  datasets: [
                    {
                      label: "Bookings",
                      data: services?.map((s) => s.total_bookings) || [],
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

          {/* Revenue by Service */}
          <Card className="p-6">
            <h2 className="text-lg font-semibold text-foreground mb-4">
              Revenue by Service
            </h2>
            <div style={{ height: "400px" }}>
              <Bar
                data={{
                  labels: services?.map((s) => s.service_name) || [],
                  datasets: [
                    {
                      label: "Revenue",
                      data: services?.map((s) => s.total_revenue) || [],
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

          {/* Service Performance Radar */}
          <Card className="p-6">
            <h2 className="text-lg font-semibold text-foreground mb-4">
              Service Performance Overview
            </h2>
            <div style={{ height: "400px" }}>
              <Radar
                data={{
                  labels:
                    services?.slice(0, 6).map((s) => s.service_name) || [],
                  datasets: [
                    {
                      label: "Bookings",
                      data:
                        services?.slice(0, 6).map((s) => s.total_bookings) ||
                        [],
                      backgroundColor: "hsla(var(--primary), 0.6)",
                      borderColor: "hsl(var(--primary))",
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

          {/* Service Details Table */}
          <Card className="p-6">
            <h2 className="text-lg font-semibold text-foreground mb-4">
              Service Performance Details
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-[var(--border)]">
                    <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">
                      Service
                    </th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">
                      Bookings
                    </th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">
                      Revenue
                    </th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">
                      Avg. Revenue
                    </th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">
                      Rating
                    </th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">
                      % of Total
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {services?.map((service, index) => (
                    <tr
                      key={index}
                      className="border-b border-[var(--border)] hover:bg-muted/50"
                    >
                      <td className="py-3 px-4 text-foreground">
                        {service.service_name}
                      </td>
                      <td className="py-3 px-4 text-right text-foreground">
                        {service.total_bookings}
                      </td>
                      <td className="py-3 px-4 text-right text-foreground font-medium">
                        ₦{service.total_revenue.toLocaleString()}
                      </td>
                      <td className="py-3 px-4 text-right text-muted-foreground">
                        ₦
                        {service.total_bookings > 0
                          ? Math.round(
                              service.total_revenue / service.total_bookings
                            ).toLocaleString()
                          : 0}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end gap-1">
                          <StarIcon size={14} className="text-yellow-500" />
                          <span className="text-foreground">
                            {(service.average_rating || 0).toFixed(1)}
                          </span>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-right text-muted-foreground">
                        {totalBookings > 0
                          ? (
                              (service.total_bookings / totalBookings) *
                              100
                            ).toFixed(1)
                          : 0}
                        %
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </>
      )}
    </div>
  );
}
