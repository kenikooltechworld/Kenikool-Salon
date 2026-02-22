import { useState } from "react";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import {
  DownloadIcon,
  CheckCircleIcon,
  AlertTriangleIcon,
} from "@/components/icons";
import {
  exportToCSV,
  exportToExcel,
  exportToPDF,
  generateTaxReport,
  type AnalyticsExportData,
  type TaxReportData,
} from "@/lib/utils/export";

interface ExportModalProps {
  open: boolean;
  onClose: () => void;
  data: AnalyticsExportData;
  dateRange?: {
    start: string;
    end: string;
  };
  salonName?: string;
}

type ExportFormat = "csv" | "excel" | "pdf" | "tax";

export function ExportModal({
  open,
  onClose,
  data,
  dateRange,
  salonName,
}: ExportModalProps) {
  const [selectedFormat, setSelectedFormat] = useState<ExportFormat>("pdf");
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleExport = async () => {
    setIsExporting(true);
    setError(null);
    setSuccess(false);

    try {
      const options = {
        filename: `analytics-report-${new Date().getTime()}`,
        dateRange,
        salonName,
      };

      switch (selectedFormat) {
        case "csv":
          exportToCSV(data, options);
          break;
        case "excel":
          await exportToExcel(data, options);
          break;
        case "pdf":
          await exportToPDF(data, options);
          break;
        case "tax":
          // Transform analytics data to tax report format
          const taxData: TaxReportData = {
            total_revenue: data.total_revenue,
            total_expenses: 0, // TODO: Fetch from expenses API
            taxable_income: data.total_revenue,
            revenue_by_category: data.top_services.map((s) => ({
              category: s.service_name,
              amount: s.total_revenue,
            })),
            monthly_breakdown: data.revenue_data.map((item) => ({
              month: item.date,
              revenue: item.revenue,
              expenses: 0,
            })),
          };
          await generateTaxReport(taxData, {
            ...options,
            filename: `tax-report-${new Date().getTime()}`,
          });
          break;
      }

      setSuccess(true);
      setTimeout(() => {
        onClose();
        setSuccess(false);
      }, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to export report");
    } finally {
      setIsExporting(false);
    }
  };

  const formats = [
    {
      id: "pdf" as ExportFormat,
      name: "PDF Report",
      description: "Professional formatted report with charts and tables",
      icon: DownloadIcon,
    },
    {
      id: "excel" as ExportFormat,
      name: "Excel Spreadsheet",
      description: "Detailed data in multiple sheets for analysis",
      icon: DownloadIcon,
    },
    {
      id: "csv" as ExportFormat,
      name: "CSV File",
      description: "Simple comma-separated values for easy import",
      icon: DownloadIcon,
    },
    {
      id: "tax" as ExportFormat,
      name: "Tax Report",
      description: "Formatted report for tax filing purposes",
      icon: DownloadIcon,
    },
  ];

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Export Analytics Report"
      description="Choose a format to export your analytics data"
      size="md"
    >
      <div className="space-y-4">
        {/* Format Selection */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-foreground">
            Export Format
          </label>
          <div className="grid grid-cols-1 gap-3">
            {formats.map((format) => {
              const Icon = format.icon;
              return (
                <button
                  key={format.id}
                  onClick={() => setSelectedFormat(format.id)}
                  className={`flex items-start gap-3 p-4 rounded-lg border-2 transition-all text-left ${
                    selectedFormat === format.id
                      ? "border-[var(--primary)] bg-[var(--primary)]/5"
                      : "border-[var(--border)] hover:border-[var(--primary)]/50"
                  }`}
                >
                  <Icon
                    size={24}
                    className={
                      selectedFormat === format.id
                        ? "text-[var(--primary)]"
                        : "text-muted-foreground"
                    }
                  />
                  <div className="flex-1">
                    <h3 className="font-medium text-foreground">
                      {format.name}
                    </h3>
                    <p className="text-sm text-muted-foreground mt-1">
                      {format.description}
                    </p>
                  </div>
                  {selectedFormat === format.id && (
                    <CheckCircleIcon
                      size={20}
                      className="text-[var(--primary)]"
                    />
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {/* Date Range Info */}
        {dateRange && (
          <div className="p-3 bg-muted rounded-lg">
            <p className="text-sm text-muted-foreground">
              <strong>Period:</strong> {dateRange.start} to {dateRange.end}
            </p>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <Alert variant="error">
            <AlertTriangleIcon size={20} />
            <div>
              <h3 className="font-semibold">Export Failed</h3>
              <p className="text-sm">{error}</p>
            </div>
          </Alert>
        )}

        {/* Success Message */}
        {success && (
          <Alert variant="success">
            <CheckCircleIcon size={20} />
            <div>
              <h3 className="font-semibold">Export Successful</h3>
              <p className="text-sm">Your report has been downloaded</p>
            </div>
          </Alert>
        )}

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-4">
          <Button variant="outline" onClick={onClose} disabled={isExporting}>
            Cancel
          </Button>
          <Button onClick={handleExport} disabled={isExporting}>
            {isExporting ? (
              <>
                <Spinner size="sm" />
                Exporting...
              </>
            ) : (
              <>
                <DownloadIcon size={20} />
                Export Report
              </>
            )}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
