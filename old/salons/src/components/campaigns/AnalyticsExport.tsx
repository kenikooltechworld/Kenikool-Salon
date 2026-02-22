import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { DownloadIcon, DocumentIcon } from "@/components/icons";
import { useToast } from "@/hooks/use-toast";
import { apiClient } from "@/lib/api/client";

interface AnalyticsExportProps {
  campaignId: string;
  campaignName: string;
}

export function AnalyticsExport({
  campaignId,
  campaignName,
}: AnalyticsExportProps) {
  const { toast } = useToast();
  const [exporting, setExporting] = useState(false);
  const [exportFormat, setExportFormat] = useState<"csv" | "pdf">("csv");

  const handleExport = async () => {
    try {
      setExporting(true);

      // Fetch analytics data
      const response = await apiClient.get(
        `/api/campaigns/${campaignId}/analytics-detailed`,
      );
      const analytics = response.data;

      if (exportFormat === "csv") {
        exportToCSV(analytics);
      } else {
        exportToPDF(analytics);
      }

      toast({
        title: "Success",
        description: `Analytics exported as ${exportFormat.toUpperCase()}`,
      });
    } catch (error) {
      console.error("Failed to export analytics:", error);
      toast({
        title: "Error",
        description: "Failed to export analytics",
        variant: "destructive",
      });
    } finally {
      setExporting(false);
    }
  };

  const exportToCSV = (analytics: any) => {
    const rows: string[] = [];

    // Header
    rows.push("Campaign Analytics Report");
    rows.push(`Campaign: ${campaignName}`);
    rows.push(`Generated: ${new Date().toLocaleString()}`);
    rows.push("");

    // Summary Section
    rows.push("SUMMARY METRICS");
    rows.push("Metric,Value");
    rows.push(`Total Recipients,${analytics.total_recipients}`);
    rows.push(`Delivered,${analytics.delivered}`);
    rows.push(`Failed,${analytics.failed}`);
    rows.push(`Delivery Rate,${(analytics.delivery_rate * 100).toFixed(2)}%`);
    rows.push(`Opened,${analytics.opened}`);
    rows.push(`Open Rate,${(analytics.open_rate * 100).toFixed(2)}%`);
    rows.push(`Clicked,${analytics.clicked}`);
    rows.push(`Click Rate,${(analytics.click_rate * 100).toFixed(2)}%`);
    rows.push(`Conversions,${analytics.conversions}`);
    rows.push(
      `Conversion Rate,${(analytics.conversion_rate * 100).toFixed(2)}%`,
    );
    rows.push("");

    // Financial Section
    rows.push("FINANCIAL METRICS");
    rows.push("Metric,Value");
    rows.push(`Total Cost,₦${analytics.total_cost.toLocaleString()}`);
    rows.push(
      `Cost per Conversion,₦${analytics.cost_per_conversion.toLocaleString()}`,
    );
    rows.push(
      `Revenue Generated,₦${analytics.revenue_generated.toLocaleString()}`,
    );
    rows.push(`ROI,${analytics.roi.toFixed(2)}%`);
    rows.push("");

    // Channel Breakdown
    if (analytics.channel_stats && analytics.channel_stats.length > 0) {
      rows.push("CHANNEL BREAKDOWN");
      rows.push("Channel,Sent,Delivered,Opened,Clicked,Cost");
      analytics.channel_stats.forEach((channel: any) => {
        rows.push(
          `${channel.channel},${channel.sent},${channel.delivered},${channel.opened},${channel.clicked},₦${channel.cost.toLocaleString()}`,
        );
      });
      rows.push("");
    }

    // Daily Stats
    if (analytics.daily_stats && analytics.daily_stats.length > 0) {
      rows.push("DAILY STATISTICS");
      rows.push("Date,Delivered,Opened,Clicked,Conversions");
      analytics.daily_stats.forEach((day: any) => {
        rows.push(
          `${day.date},${day.delivered},${day.opened},${day.clicked},${day.conversions}`,
        );
      });
    }

    // Create and download CSV
    const csv = rows.join("\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute(
      "download",
      `campaign-analytics-${campaignId}-${new Date().getTime()}.csv`,
    );
    link.style.visibility = "hidden";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const exportToPDF = (analytics: any) => {
    // Create a simple HTML representation for PDF
    const htmlContent = `
      <!DOCTYPE html>
      <html>
      <head>
        <title>Campaign Analytics Report</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 20px; }
          h1 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
          h2 { color: #555; margin-top: 20px; }
          table { width: 100%; border-collapse: collapse; margin: 10px 0; }
          th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
          th { background-color: #f8f9fa; font-weight: bold; }
          .metric-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee; }
          .metric-label { font-weight: bold; }
          .metric-value { color: #007bff; }
          .positive { color: green; }
          .negative { color: red; }
          .summary { background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }
        </style>
      </head>
      <body>
        <h1>Campaign Analytics Report</h1>
        <div class="summary">
          <p><strong>Campaign:</strong> ${campaignName}</p>
          <p><strong>Generated:</strong> ${new Date().toLocaleString()}</p>
        </div>

        <h2>Summary Metrics</h2>
        <div class="metric-row">
          <span class="metric-label">Total Recipients:</span>
          <span class="metric-value">${analytics.total_recipients}</span>
        </div>
        <div class="metric-row">
          <span class="metric-label">Delivered:</span>
          <span class="metric-value">${analytics.delivered} (${(
            analytics.delivery_rate * 100
          ).toFixed(2)}%)</span>
        </div>
        <div class="metric-row">
          <span class="metric-label">Failed:</span>
          <span class="metric-value negative">${analytics.failed}</span>
        </div>
        <div class="metric-row">
          <span class="metric-label">Opened:</span>
          <span class="metric-value">${analytics.opened} (${(
            analytics.open_rate * 100
          ).toFixed(2)}%)</span>
        </div>
        <div class="metric-row">
          <span class="metric-label">Clicked:</span>
          <span class="metric-value">${analytics.clicked} (${(
            analytics.click_rate * 100
          ).toFixed(2)}%)</span>
        </div>
        <div class="metric-row">
          <span class="metric-label">Conversions:</span>
          <span class="metric-value">${analytics.conversions} (${(
            analytics.conversion_rate * 100
          ).toFixed(2)}%)</span>
        </div>

        <h2>Financial Metrics</h2>
        <div class="metric-row">
          <span class="metric-label">Total Cost:</span>
          <span class="metric-value">₦${analytics.total_cost.toLocaleString()}</span>
        </div>
        <div class="metric-row">
          <span class="metric-label">Cost per Conversion:</span>
          <span class="metric-value">₦${analytics.cost_per_conversion.toLocaleString()}</span>
        </div>
        <div class="metric-row">
          <span class="metric-label">Revenue Generated:</span>
          <span class="metric-value positive">₦${analytics.revenue_generated.toLocaleString()}</span>
        </div>
        <div class="metric-row">
          <span class="metric-label">ROI:</span>
          <span class="metric-value ${
            analytics.roi >= 0 ? "positive" : "negative"
          }">${analytics.roi.toFixed(2)}%</span>
        </div>

        ${
          analytics.channel_stats && analytics.channel_stats.length > 0
            ? `
          <h2>Channel Breakdown</h2>
          <table>
            <tr>
              <th>Channel</th>
              <th>Sent</th>
              <th>Delivered</th>
              <th>Opened</th>
              <th>Clicked</th>
              <th>Cost</th>
            </tr>
            ${analytics.channel_stats
              .map(
                (channel: any) => `
              <tr>
                <td>${channel.channel}</td>
                <td>${channel.sent}</td>
                <td>${channel.delivered}</td>
                <td>${channel.opened}</td>
                <td>${channel.clicked}</td>
                <td>₦${channel.cost.toLocaleString()}</td>
              </tr>
            `,
              )
              .join("")}
          </table>
        `
            : ""
        }
      </body>
      </html>
    `;

    // Open print dialog
    const printWindow = window.open("", "", "height=600,width=800");
    if (printWindow) {
      printWindow.document.write(htmlContent);
      printWindow.document.close();
      printWindow.print();
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <DownloadIcon size={20} />
          Export Analytics
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium text-foreground mb-2 block">
              Export Format
            </label>
            <div className="flex gap-3">
              <button
                onClick={() => setExportFormat("csv")}
                className={`flex-1 py-2 px-4 rounded-lg border transition-colors ${
                  exportFormat === "csv"
                    ? "bg-primary text-primary-foreground border-primary"
                    : "border-input hover:bg-muted"
                }`}
              >
                <FileTextIcon size={16} className="inline mr-2" />
                CSV
              </button>
              <button
                onClick={() => setExportFormat("pdf")}
                className={`flex-1 py-2 px-4 rounded-lg border transition-colors ${
                  exportFormat === "pdf"
                    ? "bg-primary text-primary-foreground border-primary"
                    : "border-input hover:bg-muted"
                }`}
              >
                <FileTextIcon size={16} className="inline mr-2" />
                PDF
              </button>
            </div>
          </div>

          <div className="bg-muted/50 rounded-lg p-3">
            <p className="text-sm text-muted-foreground">
              {exportFormat === "csv"
                ? "Export analytics as CSV for use in spreadsheets"
                : "Export analytics as PDF for printing and sharing"}
            </p>
          </div>

          <Button
            onClick={handleExport}
            disabled={exporting}
            className="w-full"
          >
            {exporting ? (
              <>
                <Spinner size="sm" className="mr-2" />
                Exporting...
              </>
            ) : (
              <>
                <DownloadIcon size={16} className="mr-2" />
                Export as {exportFormat.toUpperCase()}
              </>
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
