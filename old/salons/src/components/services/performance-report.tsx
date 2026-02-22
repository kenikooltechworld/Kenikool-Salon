import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import {
  ChartIcon,
  AlertTriangleIcon,
  DownloadIcon,
  TrendingUpIcon,
  TrendingDownIcon,
  DollarIcon,
  CalendarIcon,
  StarIcon,
} from "@/components/icons";
import { apiClient } from "@/lib/api/client";
import { showToast } from "@/lib/utils/toast";

interface PerformanceReport {
  service_id: string;
  service_name: string;
  period: {
    start_date: string;
    end_date: string;
    days: number;
  };
  summary: {
    total_bookings: number;
    completed_bookings: number;
    cancelled_bookings: number;
    cancellation_rate: number;
    total_revenue: number;
    estimated_costs: number;
    profit: number;
    profit_margin: number;
  };
  performance: {
    utilization_rate: number;
    profit_per_booking: number;
    average_rating: number;
    total_reviews: number;
  };
  growth: {
    revenue_growth: number;
    booking_growth: number;
  };
  top_stylists: Array<{
    stylist_id: string;
    bookings: number;
    revenue: number;
  }>;
  revenue_trend: Array<{
    date: string;
    revenue: number;
  }>;
}

interface PerformanceReportProps {
  serviceId: string;
}

export function PerformanceReport({ serviceId }: PerformanceReportProps) {
  const [report, setReport] = useState<PerformanceReport | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dateRange, setDateRange] = useState<"7d" | "30d" | "90d" | "custom">(
    "30d",
  );
  const [customStart, setCustomStart] = useState("");
  const [customEnd, setCustomEnd] = useState("");

  useEffect(() => {
    loadReport();
  }, [serviceId, dateRange]);

  const loadReport = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const params: any = {};

      // Calculate date range
      const end = new Date();
      let start = new Date();

      if (dateRange === "7d") {
        start.setDate(end.getDate() - 7);
      } else if (dateRange === "30d") {
        start.setDate(end.getDate() - 30);
      } else if (dateRange === "90d") {
        start.setDate(end.getDate() - 90);
      } else if (dateRange === "custom" && customStart && customEnd) {
        start = new Date(customStart);
        end.setTime(new Date(customEnd).getTime());
      }

      params.start_date = start.toISOString();
      params.end_date = end.toISOString();

      const response = await apiClient.get(
        `/api/services/${serviceId}/reports/performance`,
        { params },
      );
      setReport(response.data);
    } catch (err) {
      console.error("Error loading report:", err);
      setError("Failed to load performance report");
    } finally {
      setIsLoading(false);
    }
  };

  const handleExport = (format: "csv" | "pdf") => {
    try {
      if (format === "csv") {
        exportToCSV();
      } else if (format === "pdf") {
        exportToPDF();
      }
    } catch (error) {
      console.error(`Error exporting ${format.toUpperCase()}:`, error);
      showToast({
        type: "error",
        title: "Export Failed",
        message: `Failed to export as ${format.toUpperCase()}`,
      });
    }
  };

  const exportToCSV = () => {
    if (!report) return;

    // Prepare CSV data
    const rows: string[] = [];

    // Header
    rows.push("Performance Report");
    rows.push(`Service: ${report.service_name}`);
    rows.push(
      `Period: ${new Date(report.period.start_date).toLocaleDateString()} - ${new Date(report.period.end_date).toLocaleDateString()}`,
    );
    rows.push("");

    // Summary
    rows.push("SUMMARY");
    rows.push("Metric,Value");
    rows.push(`Total Bookings,${report.summary.total_bookings}`);
    rows.push(`Completed Bookings,${report.summary.completed_bookings}`);
    rows.push(`Cancelled Bookings,${report.summary.cancelled_bookings}`);
    rows.push(
      `Cancellation Rate,${report.summary.cancellation_rate.toFixed(1)}%`,
    );
    rows.push(
      `Total Revenue,₦${report.summary.total_revenue.toLocaleString()}`,
    );
    rows.push(
      `Estimated Costs,₦${report.summary.estimated_costs.toLocaleString()}`,
    );
    rows.push(`Net Profit,₦${report.summary.profit.toLocaleString()}`);
    rows.push(`Profit Margin,${report.summary.profit_margin.toFixed(1)}%`);
    rows.push("");

    // Performance
    rows.push("PERFORMANCE");
    rows.push("Metric,Value");
    rows.push(
      `Utilization Rate,${report.performance.utilization_rate.toFixed(1)}%`,
    );
    rows.push(
      `Profit per Booking,₦${report.performance.profit_per_booking.toLocaleString()}`,
    );
    rows.push(`Average Rating,${report.performance.average_rating.toFixed(1)}`);
    rows.push(`Total Reviews,${report.performance.total_reviews}`);
    rows.push("");

    // Growth
    rows.push("GROWTH");
    rows.push("Metric,Value");
    rows.push(`Revenue Growth,${report.growth.revenue_growth.toFixed(1)}%`);
    rows.push(`Booking Growth,${report.growth.booking_growth.toFixed(1)}%`);
    rows.push("");

    // Top Stylists
    if (report.top_stylists.length > 0) {
      rows.push("TOP STYLISTS");
      rows.push("Stylist ID,Bookings,Revenue");
      report.top_stylists.forEach((stylist) => {
        rows.push(
          `${stylist.stylist_id},${stylist.bookings},₦${stylist.revenue.toLocaleString()}`,
        );
      });
    }

    // Create CSV content
    const csvContent = rows.join("\n");

    // Create blob and download
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);

    link.setAttribute("href", url);
    link.setAttribute(
      "download",
      `performance-report-${report.service_name}-${new Date().toISOString().split("T")[0]}.csv`,
    );
    link.style.visibility = "hidden";

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    showToast({
      type: "success",
      title: "Export Successful",
      message: "Performance report exported as CSV",
    });
  };

  const exportToPDF = () => {
    if (!report) return;

    try {
      // Create a new window for printing
      const printWindow = window.open("", "", "height=600,width=800");
      if (!printWindow) {
        showToast({
          type: "error",
          title: "Export Failed",
          message: "Unable to open print window. Please check popup settings.",
        });
        return;
      }

      const htmlContent = `
        <!DOCTYPE html>
        <html>
          <head>
            <title>Performance Report</title>
            <style>
              body { font-family: Arial, sans-serif; margin: 20px; }
              h1 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
              h2 { color: #555; margin-top: 20px; }
              table { width: 100%; border-collapse: collapse; margin: 10px 0; }
              th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
              th { background-color: #f2f2f2; font-weight: bold; }
              .metric-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee; }
              .metric-label { font-weight: 500; }
              .metric-value { text-align: right; }
              .positive { color: green; }
              .negative { color: red; }
              @media print { body { margin: 0; } }
            </style>
          </head>
          <body>
            <h1>Performance Report</h1>
            <p><strong>Service:</strong> ${report.service_name}</p>
            <p><strong>Period:</strong> ${new Date(report.period.start_date).toLocaleDateString()} - ${new Date(report.period.end_date).toLocaleDateString()}</p>
            
            <h2>Summary</h2>
            <div class="metric-row">
              <span class="metric-label">Total Bookings:</span>
              <span class="metric-value">${report.summary.total_bookings}</span>
            </div>
            <div class="metric-row">
              <span class="metric-label">Completed Bookings:</span>
              <span class="metric-value">${report.summary.completed_bookings}</span>
            </div>
            <div class="metric-row">
              <span class="metric-label">Cancelled Bookings:</span>
              <span class="metric-value">${report.summary.cancelled_bookings}</span>
            </div>
            <div class="metric-row">
              <span class="metric-label">Total Revenue:</span>
              <span class="metric-value">₦${report.summary.total_revenue.toLocaleString()}</span>
            </div>
            <div class="metric-row">
              <span class="metric-label">Estimated Costs:</span>
              <span class="metric-value">₦${report.summary.estimated_costs.toLocaleString()}</span>
            </div>
            <div class="metric-row">
              <span class="metric-label">Net Profit:</span>
              <span class="metric-value positive">₦${report.summary.profit.toLocaleString()}</span>
            </div>
            <div class="metric-row">
              <span class="metric-label">Profit Margin:</span>
              <span class="metric-value">${report.summary.profit_margin.toFixed(1)}%</span>
            </div>

            <h2>Performance Metrics</h2>
            <div class="metric-row">
              <span class="metric-label">Utilization Rate:</span>
              <span class="metric-value">${report.performance.utilization_rate.toFixed(1)}%</span>
            </div>
            <div class="metric-row">
              <span class="metric-label">Profit per Booking:</span>
              <span class="metric-value">₦${report.performance.profit_per_booking.toLocaleString()}</span>
            </div>
            <div class="metric-row">
              <span class="metric-label">Average Rating:</span>
              <span class="metric-value">${report.performance.average_rating.toFixed(1)} ★</span>
            </div>
            <div class="metric-row">
              <span class="metric-label">Total Reviews:</span>
              <span class="metric-value">${report.performance.total_reviews}</span>
            </div>

            <h2>Growth</h2>
            <div class="metric-row">
              <span class="metric-label">Revenue Growth:</span>
              <span class="metric-value ${report.growth.revenue_growth >= 0 ? "positive" : "negative"}">
                ${report.growth.revenue_growth >= 0 ? "+" : ""}${report.growth.revenue_growth.toFixed(1)}%
              </span>
            </div>
            <div class="metric-row">
              <span class="metric-label">Booking Growth:</span>
              <span class="metric-value ${report.growth.booking_growth >= 0 ? "positive" : "negative"}">
                ${report.growth.booking_growth >= 0 ? "+" : ""}${report.growth.booking_growth.toFixed(1)}%
              </span>
            </div>

            ${
              report.top_stylists.length > 0
                ? `
              <h2>Top Stylists</h2>
              <table>
                <tr>
                  <th>Stylist ID</th>
                  <th>Bookings</th>
                  <th>Revenue</th>
                </tr>
                ${report.top_stylists
                  .map(
                    (stylist) => `
                  <tr>
                    <td>${stylist.stylist_id}</td>
                    <td>${stylist.bookings}</td>
                    <td>₦${stylist.revenue.toLocaleString()}</td>
                  </tr>
                `,
                  )
                  .join("")}
              </table>
            `
                : ""
            }

            <p style="margin-top: 30px; color: #999; font-size: 12px;">
              Generated on ${new Date().toLocaleString()}
            </p>
          </body>
        </html>
      `;

      printWindow.document.write(htmlContent);
      printWindow.document.close();

      // Trigger print dialog
      setTimeout(() => {
        printWindow.print();
        showToast({
          type: "success",
          title: "Export Ready",
          message: "PDF export ready. Use your browser's print dialog to save.",
        });
      }, 250);
    } catch (error) {
      console.error("Error exporting PDF:", error);
      showToast({
        type: "error",
        title: "Export Failed",
        message: "Failed to export as PDF",
      });
    }
  };

  const formatCurrency = (amount: number) => {
    return `₦${amount.toLocaleString(undefined, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`;
  };

  const formatPercentage = (value: number) => {
    return `${value >= 0 ? "+" : ""}${value.toFixed(1)}%`;
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error || !report) {
    return (
      <Alert variant="error">
        <AlertTriangleIcon size={20} />
        <div>
          <h3 className="font-semibold">Error</h3>
          <p className="text-sm">{error || "Failed to load report"}</p>
        </div>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-foreground flex items-center gap-2">
            <ChartIcon size={20} className="text-primary" />
            Performance Report
          </h3>
          <p className="text-sm text-muted-foreground mt-1">
            {report.service_name} • {report.period.days} days
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => handleExport("csv")}
            className="cursor-pointer transition-all duration-200"
          >
            <DownloadIcon size={16} />
            Export CSV
          </Button>
          <Button
            variant="outline"
            onClick={() => handleExport("pdf")}
            className="cursor-pointer transition-all duration-200"
          >
            <DownloadIcon size={16} />
            Export PDF
          </Button>
        </div>
      </div>

      {/* Date Range Selector */}
      <Card className="p-4">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-sm font-medium text-foreground">
            Time Period:
          </span>
          {["7d", "30d", "90d", "custom"].map((range) => (
            <Button
              key={range}
              variant={dateRange === range ? "default" : "outline"}
              size="sm"
              onClick={() => setDateRange(range as any)}
              className="cursor-pointer transition-all duration-200"
            >
              {range === "7d" && "Last 7 Days"}
              {range === "30d" && "Last 30 Days"}
              {range === "90d" && "Last 90 Days"}
              {range === "custom" && "Custom Range"}
            </Button>
          ))}
          {dateRange === "custom" && (
            <div className="flex gap-2 ml-4">
              <input
                type="date"
                value={customStart}
                onChange={(e) => setCustomStart(e.target.value)}
                className="px-2 py-1 text-sm border border-border rounded bg-background text-foreground"
              />
              <span className="text-sm text-muted-foreground">to</span>
              <input
                type="date"
                value={customEnd}
                onChange={(e) => setCustomEnd(e.target.value)}
                className="px-2 py-1 text-sm border border-border rounded bg-background text-foreground"
              />
              <Button
                size="sm"
                onClick={loadReport}
                className="cursor-pointer transition-all duration-200"
              >
                Apply
              </Button>
            </div>
          )}
        </div>
      </Card>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-6">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-muted-foreground mb-1">
                Total Revenue
              </p>
              <p className="text-2xl font-bold text-foreground">
                {formatCurrency(report.summary.total_revenue)}
              </p>
              <div className="flex items-center gap-1 mt-2">
                {report.growth.revenue_growth >= 0 ? (
                  <TrendingUpIcon size={14} className="text-green-500" />
                ) : (
                  <TrendingDownIcon size={14} className="text-red-500" />
                )}
                <span
                  className={`text-xs font-medium ${
                    report.growth.revenue_growth >= 0
                      ? "text-green-500"
                      : "text-red-500"
                  }`}
                >
                  {formatPercentage(report.growth.revenue_growth)}
                </span>
              </div>
            </div>
            <div className="p-3 bg-green-100 dark:bg-green-900 rounded-lg">
              <DollarIcon
                size={20}
                className="text-green-600 dark:text-green-400"
              />
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-muted-foreground mb-1">
                Total Bookings
              </p>
              <p className="text-2xl font-bold text-foreground">
                {report.summary.total_bookings}
              </p>
              <div className="flex items-center gap-1 mt-2">
                {report.growth.booking_growth >= 0 ? (
                  <TrendingUpIcon size={14} className="text-green-500" />
                ) : (
                  <TrendingDownIcon size={14} className="text-red-500" />
                )}
                <span
                  className={`text-xs font-medium ${
                    report.growth.booking_growth >= 0
                      ? "text-green-500"
                      : "text-red-500"
                  }`}
                >
                  {formatPercentage(report.growth.booking_growth)}
                </span>
              </div>
            </div>
            <div className="p-3 bg-blue-100 dark:bg-blue-900 rounded-lg">
              <CalendarIcon
                size={20}
                className="text-blue-600 dark:text-blue-400"
              />
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-muted-foreground mb-1">Profit</p>
              <p className="text-2xl font-bold text-foreground">
                {formatCurrency(report.summary.profit)}
              </p>
              <p className="text-xs text-muted-foreground mt-2">
                {report.summary.profit_margin.toFixed(1)}% margin
              </p>
            </div>
            <div className="p-3 bg-purple-100 dark:bg-purple-900 rounded-lg">
              <TrendingUpIcon
                size={20}
                className="text-purple-600 dark:text-purple-400"
              />
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-muted-foreground mb-1">Utilization</p>
              <p className="text-2xl font-bold text-foreground">
                {report.performance.utilization_rate.toFixed(1)}%
              </p>
              <p className="text-xs text-muted-foreground mt-2">
                {report.performance.average_rating.toFixed(1)} ★ rating
              </p>
            </div>
            <div className="p-3 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
              <StarIcon
                size={20}
                className="text-yellow-600 dark:text-yellow-400"
              />
            </div>
          </div>
        </Card>
      </div>

      {/* Detailed Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Performance Metrics */}
        <Card className="p-6">
          <h4 className="font-semibold text-foreground mb-4">
            Performance Metrics
          </h4>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">
                Completed Bookings
              </span>
              <span className="text-sm font-medium text-foreground">
                {report.summary.completed_bookings}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">
                Cancelled Bookings
              </span>
              <span className="text-sm font-medium text-foreground">
                {report.summary.cancelled_bookings} (
                {report.summary.cancellation_rate.toFixed(1)}%)
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">
                Profit per Booking
              </span>
              <span className="text-sm font-medium text-foreground">
                {formatCurrency(report.performance.profit_per_booking)}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">
                Total Reviews
              </span>
              <span className="text-sm font-medium text-foreground">
                {report.performance.total_reviews}
              </span>
            </div>
          </div>
        </Card>

        {/* Cost Breakdown */}
        <Card className="p-6">
          <h4 className="font-semibold text-foreground mb-4">
            Financial Breakdown
          </h4>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">
                Total Revenue
              </span>
              <span className="text-sm font-medium text-green-600">
                {formatCurrency(report.summary.total_revenue)}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">
                Estimated Costs
              </span>
              <span className="text-sm font-medium text-red-600">
                -{formatCurrency(report.summary.estimated_costs)}
              </span>
            </div>
            <div className="h-px bg-border" />
            <div className="flex justify-between items-center">
              <span className="text-sm font-semibold text-foreground">
                Net Profit
              </span>
              <span className="text-sm font-bold text-foreground">
                {formatCurrency(report.summary.profit)}
              </span>
            </div>
          </div>
        </Card>
      </div>

      {/* Top Stylists */}
      {report.top_stylists.length > 0 && (
        <Card className="p-6">
          <h4 className="font-semibold text-foreground mb-4">
            Top Performing Stylists
          </h4>
          <div className="space-y-3">
            {report.top_stylists.map((stylist, index) => (
              <div
                key={stylist.stylist_id}
                className="flex items-center justify-between p-3 bg-muted rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                    <span className="text-sm font-bold text-primary">
                      #{index + 1}
                    </span>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-foreground">
                      Stylist {stylist.stylist_id.slice(-6)}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {stylist.bookings} bookings
                    </p>
                  </div>
                </div>
                <span className="text-sm font-semibold text-foreground">
                  {formatCurrency(stylist.revenue)}
                </span>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Info Card */}
      <Card className="p-4 bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800">
        <div className="flex gap-3">
          <ChartIcon size={20} className="text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-1">
              About This Report
            </h4>
            <p className="text-sm text-blue-800 dark:text-blue-200">
              This report provides comprehensive performance metrics for the
              selected time period. Profit calculations assume 30% overhead
              costs. Use the export buttons to download detailed reports for
              further analysis.
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
