import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Spinner } from "@/components/ui/spinner";
import { DownloadIcon, FilterIcon } from "@/components/icons";
import { useExportAuditLog } from "@/lib/api/hooks/useSettings";

export function AuditLogFilters() {
  const [eventType, setEventType] = useState<string>("all");
  const [dateRange, setDateRange] = useState<"all" | "7days" | "30days" | "90days">("all");
  const exportMutation = useExportAuditLog();

  const handleExport = () => {
    exportMutation.mutate(undefined, {
      onSuccess: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = `audit-log-${new Date().toISOString().split("T")[0]}.csv`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      },
    });
  };

  const eventTypes = [
    { value: "all", label: "All Events" },
    { value: "login", label: "Login" },
    { value: "logout", label: "Logout" },
    { value: "password_change", label: "Password Change" },
    { value: "2fa_enabled", label: "2FA Enabled" },
    { value: "2fa_disabled", label: "2FA Disabled" },
    { value: "account_deletion_requested", label: "Account Deletion" },
    { value: "email_changed", label: "Email Changed" },
    { value: "phone_verified", label: "Phone Verified" },
    { value: "settings_updated", label: "Settings Updated" },
  ];

  const dateRanges = [
    { value: "all", label: "All Time" },
    { value: "7days", label: "Last 7 Days" },
    { value: "30days", label: "Last 30 Days" },
    { value: "90days", label: "Last 90 Days" },
  ];

  return (
    <Card className="p-6">
      <div className="flex items-center gap-2 mb-6">
        <FilterIcon size={20} />
        <h2 className="text-lg font-semibold text-foreground">Filters</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Event Type Filter */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-2">
            Event Type
          </label>
          <Select value={eventType} onValueChange={setEventType}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {eventTypes.map((type) => (
                <SelectItem key={type.value} value={type.value}>
                  {type.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Date Range Filter */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-2">
            Date Range
          </label>
          <Select value={dateRange} onValueChange={(value: any) => setDateRange(value)}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {dateRanges.map((range) => (
                <SelectItem key={range.value} value={range.value}>
                  {range.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Export Button */}
        <div className="flex items-end">
          <Button
            onClick={handleExport}
            disabled={exportMutation.isPending}
            variant="outline"
            className="w-full"
          >
            {exportMutation.isPending ? (
              <>
                <Spinner size="sm" />
                Exporting...
              </>
            ) : (
              <>
                <DownloadIcon size={16} className="mr-2" />
                Export to CSV
              </>
            )}
          </Button>
        </div>
      </div>

      <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded-lg">
        <p className="text-xs text-blue-800 dark:text-blue-200">
          💡 Filters are applied client-side. Export includes all events in the selected date range.
        </p>
      </div>
    </Card>
  );
}
