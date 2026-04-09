import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { BarChart3Icon, DownloadIcon } from "@/components/icons";
import { formatCurrency } from "@/lib/utils/format";
import type { RevenueAnalytics } from "@/hooks/owner";
import { useState } from "react";
import { D3BarChart } from "./D3BarChart";
import jsPDF from "jspdf";

interface RevenueChartProps {
  data?: RevenueAnalytics;
  isLoading?: boolean;
  error?: string;
  onRetry?: () => void;
  onPeriodChange?: (period: "daily" | "weekly" | "monthly") => void;
  currency?: string;
}

export function RevenueChart({
  data,
  isLoading = false,
  error,
  onRetry,
  onPeriodChange,
  currency = "USD",
}: RevenueChartProps) {
  const [period, setPeriod] = useState<"daily" | "weekly" | "monthly">("daily");

  const handlePeriodChange = (newPeriod: "daily" | "weekly" | "monthly") => {
    setPeriod(newPeriod);
    onPeriodChange?.(newPeriod);
  };

  const handleExportCSV = () => {
    if (!data) return;

    // Get the appropriate data based on period
    let chartData: { date: string; revenue: number }[] = [];
    if (period === "daily") {
      chartData = data.dailyRevenue;
    } else if (period === "weekly") {
      chartData = data.weeklyRevenue;
    } else {
      chartData = data.monthlyRevenue;
    }

    // Create CSV content
    const headers = ["Date", "Revenue"];
    const rows = chartData.map((item) => [item.date, item.revenue.toFixed(2)]);

    const csvContent = [
      headers.join(","),
      ...rows.map((row) => row.join(",")),
    ].join("\n");

    // Create and download file
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute(
      "download",
      `revenue-${period}-${new Date().toISOString().split("T")[0]}.csv`,
    );
    link.style.visibility = "hidden";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleExportPDF = () => {
    if (!data) return;

    const doc = new jsPDF();
    const pageWidth = doc.internal.pageSize.getWidth();

    // Title
    doc.setFontSize(18);
    doc.text("Revenue Analytics Report", pageWidth / 2, 20, {
      align: "center",
    });

    // Period and date
    doc.setFontSize(12);
    doc.text(
      `Period: ${period.charAt(0).toUpperCase() + period.slice(1)}`,
      20,
      35,
    );
    doc.text(`Generated: ${new Date().toLocaleDateString()}`, 20, 42);

    // Summary metrics
    doc.setFontSize(14);
    doc.text("Summary", 20, 55);
    doc.setFontSize(11);
    doc.text(
      `Total Revenue: ${formatCurrency(data.totalRevenue, currency)}`,
      20,
      65,
    );
    doc.text(
      `Average Daily Revenue: ${formatCurrency(data.averageDailyRevenue, currency)}`,
      20,
      72,
    );
    doc.text(`Growth: ${data.growthPercentage.toFixed(1)}%`, 20, 79);

    // Revenue by Service
    doc.setFontSize(14);
    doc.text("Revenue by Service", 20, 95);
    doc.setFontSize(10);
    let yPos = 105;
    data.byService.slice(0, 5).forEach((service) => {
      doc.text(
        `${service.serviceName}: ${formatCurrency(service.revenue, currency)} (${service.percentage.toFixed(1)}%)`,
        25,
        yPos,
      );
      yPos += 7;
    });

    // Top Staff
    doc.setFontSize(14);
    doc.text("Top Staff by Revenue", 20, yPos + 10);
    doc.setFontSize(10);
    yPos += 20;
    data.byStaff.slice(0, 5).forEach((staff) => {
      doc.text(
        `${staff.staffName}: ${formatCurrency(staff.revenue, currency)} (${staff.percentage.toFixed(1)}%)`,
        25,
        yPos,
      );
      yPos += 7;
    });

    // Save PDF
    doc.save(`revenue-${period}-${new Date().toISOString().split("T")[0]}.pdf`);
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3Icon size={20} />
            Revenue Analytics
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Skeleton className="h-64 w-full" />
          <Skeleton className="h-10 w-full" />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="border-destructive/50 bg-destructive/5">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3Icon size={20} />
            Revenue Analytics
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <p className="text-sm text-destructive font-medium">
            Unable to load revenue data
          </p>
          <p className="text-sm text-muted-foreground">{error}</p>
          {onRetry && (
            <Button
              variant="outline"
              size="sm"
              onClick={onRetry}
              className="w-full"
            >
              Retry
            </Button>
          )}
        </CardContent>
      </Card>
    );
  }

  if (!data) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3Icon size={20} />
            Revenue Analytics
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground text-center py-8">
            No revenue data available
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <CardTitle className="flex items-center gap-2">
            <BarChart3Icon size={20} />
            Revenue Analytics
          </CardTitle>
          <div className="flex gap-2">
            <Button
              variant={period === "daily" ? "primary" : "outline"}
              size="sm"
              onClick={() => handlePeriodChange("daily")}
            >
              Daily
            </Button>
            <Button
              variant={period === "weekly" ? "primary" : "outline"}
              size="sm"
              onClick={() => handlePeriodChange("weekly")}
            >
              Weekly
            </Button>
            <Button
              variant={period === "monthly" ? "primary" : "outline"}
              size="sm"
              onClick={() => handlePeriodChange("monthly")}
            >
              Monthly
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* D3.js Bar Chart */}
        <D3BarChart
          data={
            period === "daily"
              ? data.dailyRevenue
              : period === "weekly"
                ? data.weeklyRevenue
                : data.monthlyRevenue
          }
          height={380}
          currency={currency}
        />

        {/* Metrics */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="space-y-1">
            <p className="text-xs" style={{ color: "var(--muted-foreground)" }}>
              Total Revenue
            </p>
            <p
              className="text-2xl font-bold"
              style={{ color: "var(--foreground)" }}
            >
              {formatCurrency(data.totalRevenue, currency)}
            </p>
          </div>
          <div className="space-y-1">
            <p className="text-xs" style={{ color: "var(--muted-foreground)" }}>
              Average Daily
            </p>
            <p
              className="text-2xl font-bold"
              style={{ color: "var(--foreground)" }}
            >
              {formatCurrency(data.averageDailyRevenue, currency)}
            </p>
          </div>
          <div className="space-y-1">
            <p className="text-xs" style={{ color: "var(--muted-foreground)" }}>
              Growth
            </p>
            <p
              className="text-2xl font-bold"
              style={{
                color:
                  data.growthPercentage >= 0
                    ? "var(--success, #22c55e)"
                    : "var(--destructive)",
              }}
            >
              {data.growthPercentage >= 0 ? "+" : ""}
              {data.growthPercentage.toFixed(1)}%
            </p>
          </div>
        </div>

        {/* Revenue by Service */}
        <div className="space-y-2">
          <h4
            className="font-medium text-sm"
            style={{ color: "var(--foreground)" }}
          >
            Revenue by Service
          </h4>
          <div className="space-y-2">
            {data.byService.slice(0, 5).map((service) => (
              <div
                key={service.serviceName}
                className="flex items-center justify-between text-sm"
              >
                <span style={{ color: "var(--muted-foreground)" }}>
                  {service.serviceName}
                </span>
                <div className="flex items-center gap-2">
                  <div
                    className="w-24 rounded-full h-2"
                    style={{ backgroundColor: "var(--muted)" }}
                  >
                    <div
                      className="h-2 rounded-full"
                      style={{
                        width: `${service.percentage}%`,
                        backgroundColor: "var(--primary)",
                      }}
                    />
                  </div>
                  <span
                    className="font-medium w-16 text-right"
                    style={{ color: "var(--foreground)" }}
                  >
                    {formatCurrency(service.revenue, currency)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Revenue by Staff */}
        <div className="space-y-2">
          <h4
            className="font-medium text-sm"
            style={{ color: "var(--foreground)" }}
          >
            Top Staff by Revenue
          </h4>
          <div className="space-y-2">
            {data.byStaff.slice(0, 5).map((staff) => (
              <div
                key={staff.staffName}
                className="flex items-center justify-between text-sm"
              >
                <span style={{ color: "var(--muted-foreground)" }}>
                  {staff.staffName}
                </span>
                <div className="flex items-center gap-2">
                  <div
                    className="w-24 rounded-full h-2"
                    style={{ backgroundColor: "var(--muted)" }}
                  >
                    <div
                      className="h-2 rounded-full"
                      style={{
                        width: `${staff.percentage}%`,
                        backgroundColor: "var(--primary)",
                      }}
                    />
                  </div>
                  <span
                    className="font-medium w-16 text-right"
                    style={{ color: "var(--foreground)" }}
                  >
                    {formatCurrency(staff.revenue, currency)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Export buttons */}
        <div className="flex flex-col sm:flex-row gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleExportPDF}
            className="flex-1"
          >
            <DownloadIcon size={14} className="mr-1" />
            Export PDF
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleExportCSV}
            className="flex-1"
          >
            <DownloadIcon size={14} className="mr-1" />
            Export CSV
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
