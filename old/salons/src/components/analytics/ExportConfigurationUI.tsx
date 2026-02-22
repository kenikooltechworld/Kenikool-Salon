import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Modal } from "@/components/ui/modal";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import {
  DownloadIcon,
  CheckCircleIcon,
  AlertTriangleIcon,
  PlusIcon,
  TrashIcon,
} from "@/components/icons";

interface ExportFilter {
  id: string;
  field: string;
  operator: "equals" | "not_equals" | "greater_than" | "less_than" | "contains" | "between";
  value: string | number | [number, number];
}

interface ExportConfiguration {
  format: "csv" | "json" | "excel" | "pdf";
  metrics: string[];
  filters: ExportFilter[];
  dateRange: {
    start: string;
    end: string;
  };
  includeCharts: boolean;
  filename: string;
}

interface ExportConfigurationUIProps {
  open: boolean;
  onClose: () => void;
  onExport: (config: ExportConfiguration) => Promise<void>;
  availableMetrics?: string[];
  availableFields?: string[];
}

const DEFAULT_METRICS = [
  "revenue",
  "bookings",
  "clients",
  "avg_booking_value",
  "profit_margin",
  "staff_utilization",
];

const DEFAULT_FIELDS = [
  "location",
  "service",
  "staff",
  "date",
  "client_segment",
];

const OPERATORS = [
  { value: "equals", label: "Equals" },
  { value: "not_equals", label: "Not Equals" },
  { value: "greater_than", label: "Greater Than" },
  { value: "less_than", label: "Less Than" },
  { value: "contains", label: "Contains" },
  { value: "between", label: "Between" },
];

export function ExportConfigurationUI({
  open,
  onClose,
  onExport,
  availableMetrics = DEFAULT_METRICS,
  availableFields = DEFAULT_FIELDS,
}: ExportConfigurationUIProps) {
  const [config, setConfig] = useState<ExportConfiguration>({
    format: "csv",
    metrics: ["revenue", "bookings"],
    filters: [],
    dateRange: {
      start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
        .toISOString()
        .split("T")[0],
      end: new Date().toISOString().split("T")[0],
    },
    includeCharts: false,
    filename: `export-${new Date().toISOString().split("T")[0]}`,
  });

  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleFormatChange = (format: ExportConfiguration["format"]) => {
    setConfig({ ...config, format });
  };

  const handleMetricToggle = (metric: string) => {
    const metrics = config.metrics.includes(metric)
      ? config.metrics.filter((m) => m !== metric)
      : [...config.metrics, metric];
    setConfig({ ...config, metrics });
  };

  const handleAddFilter = () => {
    const newFilter: ExportFilter = {
      id: `filter_${Date.now()}`,
      field: DEFAULT_FIELDS[0],
      operator: "equals",
      value: "",
    };
    setConfig({
      ...config,
      filters: [...config.filters, newFilter],
    });
  };

  const handleUpdateFilter = (
    id: string,
    updates: Partial<ExportFilter>
  ) => {
    setConfig({
      ...config,
      filters: config.filters.map((f) =>
        f.id === id ? { ...f, ...updates } : f
      ),
    });
  };

  const handleRemoveFilter = (id: string) => {
    setConfig({
      ...config,
      filters: config.filters.filter((f) => f.id !== id),
    });
  };

  const handleDateRangeChange = (
    type: "start" | "end",
    value: string
  ) => {
    setConfig({
      ...config,
      dateRange: {
        ...config.dateRange,
        [type]: value,
      },
    });
  };

  const handleExport = async () => {
    setIsExporting(true);
    setError(null);
    setSuccess(false);

    try {
      if (config.metrics.length === 0) {
        throw new Error("Please select at least one metric to export");
      }

      await onExport(config);
      setSuccess(true);

      setTimeout(() => {
        onClose();
        setSuccess(false);
      }, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Export failed");
    } finally {
      setIsExporting(false);
    }
  };

  const formats = [
    {
      id: "csv" as const,
      name: "CSV",
      description: "Comma-separated values for spreadsheets",
    },
    {
      id: "json" as const,
      name: "JSON",
      description: "JSON format for API integration",
    },
    {
      id: "excel" as const,
      name: "Excel",
      description: "Excel workbook with multiple sheets",
    },
    {
      id: "pdf" as const,
      name: "PDF",
      description: "Professional PDF report",
    },
  ];

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Export Configuration"
      description="Configure your analytics data export"
      size="lg"
    >
      <div className="space-y-6 max-h-[80vh] overflow-y-auto">
        {/* Format Selection */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-3">
            Export Format
          </label>
          <div className="grid grid-cols-2 gap-3">
            {formats.map((format) => (
              <button
                key={format.id}
                onClick={() => handleFormatChange(format.id)}
                className={`p-3 rounded-lg border-2 transition-all text-left ${
                  config.format === format.id
                    ? "border-[var(--primary)] bg-[var(--primary)]/5"
                    : "border-[var(--border)] hover:border-[var(--primary)]/50"
                }`}
              >
                <h3 className="font-medium text-foreground">{format.name}</h3>
                <p className="text-xs text-muted-foreground mt-1">
                  {format.description}
                </p>
              </button>
            ))}
          </div>
        </div>

        {/* Metrics Selection */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-3">
            Metrics to Export
          </label>
          <div className="grid grid-cols-2 gap-2">
            {availableMetrics.map((metric) => (
              <label
                key={metric}
                className="flex items-center gap-2 p-2 rounded hover:bg-muted cursor-pointer"
              >
                <input
                  type="checkbox"
                  checked={config.metrics.includes(metric)}
                  onChange={() => handleMetricToggle(metric)}
                  className="rounded"
                />
                <span className="text-sm text-foreground capitalize">
                  {metric.replace(/_/g, " ")}
                </span>
              </label>
            ))}
          </div>
        </div>

        {/* Date Range */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-3">
            Date Range
          </label>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs text-muted-foreground mb-1">
                Start Date
              </label>
              <input
                type="date"
                value={config.dateRange.start}
                onChange={(e) =>
                  handleDateRangeChange("start", e.target.value)
                }
                className="w-full px-3 py-2 border border-[var(--border)] rounded-md text-sm"
              />
            </div>
            <div>
              <label className="block text-xs text-muted-foreground mb-1">
                End Date
              </label>
              <input
                type="date"
                value={config.dateRange.end}
                onChange={(e) => handleDateRangeChange("end", e.target.value)}
                className="w-full px-3 py-2 border border-[var(--border)] rounded-md text-sm"
              />
            </div>
          </div>
        </div>

        {/* Filters */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <label className="block text-sm font-medium text-foreground">
              Filters (Optional)
            </label>
            <Button
              onClick={handleAddFilter}
              variant="outline"
              size="sm"
              className="gap-1"
            >
              <PlusIcon size={16} />
              Add Filter
            </Button>
          </div>

          <div className="space-y-2">
            {config.filters.map((filter) => (
              <div
                key={filter.id}
                className="flex items-end gap-2 p-3 bg-muted rounded-lg"
              >
                <div className="flex-1">
                  <label className="block text-xs text-muted-foreground mb-1">
                    Field
                  </label>
                  <select
                    value={filter.field}
                    onChange={(e) =>
                      handleUpdateFilter(filter.id, { field: e.target.value })
                    }
                    className="w-full px-2 py-1 border border-[var(--border)] rounded text-sm"
                  >
                    {availableFields.map((field) => (
                      <option key={field} value={field}>
                        {field.replace(/_/g, " ")}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="flex-1">
                  <label className="block text-xs text-muted-foreground mb-1">
                    Operator
                  </label>
                  <select
                    value={filter.operator}
                    onChange={(e) =>
                      handleUpdateFilter(filter.id, {
                        operator: e.target.value as ExportFilter["operator"],
                      })
                    }
                    className="w-full px-2 py-1 border border-[var(--border)] rounded text-sm"
                  >
                    {OPERATORS.map((op) => (
                      <option key={op.value} value={op.value}>
                        {op.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="flex-1">
                  <label className="block text-xs text-muted-foreground mb-1">
                    Value
                  </label>
                  <input
                    type="text"
                    value={
                      Array.isArray(filter.value)
                        ? filter.value.join(" - ")
                        : filter.value
                    }
                    onChange={(e) =>
                      handleUpdateFilter(filter.id, { value: e.target.value })
                    }
                    placeholder="Enter value"
                    className="w-full px-2 py-1 border border-[var(--border)] rounded text-sm"
                  />
                </div>

                <button
                  onClick={() => handleRemoveFilter(filter.id)}
                  className="p-2 text-destructive hover:bg-destructive/10 rounded"
                >
                  <TrashIcon size={16} />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Additional Options */}
        <div>
          <label className="flex items-center gap-2 p-2 rounded hover:bg-muted cursor-pointer">
            <input
              type="checkbox"
              checked={config.includeCharts}
              onChange={(e) =>
                setConfig({ ...config, includeCharts: e.target.checked })
              }
              className="rounded"
            />
            <span className="text-sm text-foreground">
              Include charts in export (PDF only)
            </span>
          </label>
        </div>

        {/* Filename */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-2">
            Filename
          </label>
          <input
            type="text"
            value={config.filename}
            onChange={(e) =>
              setConfig({ ...config, filename: e.target.value })
            }
            className="w-full px-3 py-2 border border-[var(--border)] rounded-md text-sm"
          />
        </div>

        {/* Error Message */}
        {error && (
          <Alert variant="error">
            <AlertTriangleIcon size={20} />
            <div>
              <h3 className="font-semibold">Export Error</h3>
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
              <p className="text-sm">Your data has been exported</p>
            </div>
          </Alert>
        )}

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-4 border-t border-[var(--border)]">
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
                Export Data
              </>
            )}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
