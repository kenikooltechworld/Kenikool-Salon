import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import {
  ClockIcon,
  UserIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  FilterIcon,
} from "@/components/icons";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";

interface AuditLogEntry {
  _id: string;
  entity_type: string;
  entity_id: string;
  action: string;
  tenant_id: string;
  user_id: string;
  user_email: string;
  changes: Record<string, { old: any; new: any }>;
  metadata: Record<string, any>;
  timestamp: string;
}

interface AuditLogViewerProps {
  serviceId: string;
}

export function AuditLogViewer({ serviceId }: AuditLogViewerProps) {
  const [page, setPage] = useState(1);
  const [filterAction, setFilterAction] = useState<string | null>(null);
  const limit = 20;

  const { data, isLoading, refetch } = useQuery({
    queryKey: ["service-audit-log", serviceId, page],
    queryFn: async () => {
      const skip = (page - 1) * limit;
      const response = await apiClient.get(
        `/api/services/${serviceId}/audit-log`,
        {
          params: { limit, skip },
        }
      );
      return response.data;
    },
  });

  const logs: AuditLogEntry[] = data?.logs || [];
  const totalPages = Math.ceil((data?.total || 0) / limit);

  // Filter logs by action if filter is set
  const filteredLogs = filterAction
    ? logs.filter((log) => log.action === filterAction)
    : logs;

  const getActionColor = (action: string) => {
    switch (action) {
      case "create":
        return "success";
      case "update":
        return "primary";
      case "delete":
        return "error";
      default:
        return "secondary";
    }
  };

  const formatTimestamp = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return timestamp;
    }
  };

  const formatValue = (value: any): string => {
    if (value === null || value === undefined) {
      return "N/A";
    }
    if (typeof value === "object") {
      return JSON.stringify(value);
    }
    return String(value);
  };

  const isPriceChange = (field: string): boolean => {
    return field.toLowerCase().includes("price");
  };

  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="flex justify-center py-8">
          <Spinner />
        </div>
      </Card>
    );
  }

  if (logs.length === 0) {
    return (
      <Card className="p-6">
        <h2 className="text-xl font-bold text-foreground mb-4">Audit Log</h2>
        <div className="text-center py-8">
          <ClockIcon size={48} className="mx-auto text-muted-foreground mb-4" />
          <p className="text-muted-foreground">No audit log entries yet</p>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-foreground">Audit Log</h2>

        {/* Filter buttons */}
        <div className="flex gap-2 items-center">
          <FilterIcon size={16} className="text-muted-foreground" />
          <button
            onClick={() => setFilterAction(null)}
            className={`px-3 py-1 text-sm rounded-lg transition-colors ${
              filterAction === null
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-muted-foreground hover:bg-muted/80"
            }`}
          >
            All
          </button>
          <button
            onClick={() => setFilterAction("create")}
            className={`px-3 py-1 text-sm rounded-lg transition-colors ${
              filterAction === "create"
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-muted-foreground hover:bg-muted/80"
            }`}
          >
            Created
          </button>
          <button
            onClick={() => setFilterAction("update")}
            className={`px-3 py-1 text-sm rounded-lg transition-colors ${
              filterAction === "update"
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-muted-foreground hover:bg-muted/80"
            }`}
          >
            Updated
          </button>
          <button
            onClick={() => setFilterAction("delete")}
            className={`px-3 py-1 text-sm rounded-lg transition-colors ${
              filterAction === "delete"
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-muted-foreground hover:bg-muted/80"
            }`}
          >
            Deleted
          </button>
        </div>
      </div>

      <div className="space-y-4">
        {filteredLogs.map((log) => (
          <div
            key={log._id}
            className="p-4 border border-border rounded-lg hover:bg-muted/30 transition-colors"
          >
            {/* Header */}
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-primary/10 rounded-lg">
                  <UserIcon size={16} className="text-primary" />
                </div>
                <div>
                  <p className="font-medium text-foreground">
                    {log.user_email}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {formatTimestamp(log.timestamp)}
                  </p>
                </div>
              </div>
              <Badge
                variant={
                  getActionColor(log.action) as
                    | "success"
                    | "primary"
                    | "error"
                    | "secondary"
                }
              >
                {log.action}
              </Badge>
            </div>

            {/* Changes */}
            {log.action === "update" && Object.keys(log.changes).length > 0 && (
              <div className="mt-3 space-y-2">
                <p className="text-sm font-medium text-foreground">Changes:</p>
                {Object.entries(log.changes).map(([field, change]) => (
                  <div
                    key={field}
                    className={`text-sm p-2 rounded ${
                      isPriceChange(field)
                        ? "bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800"
                        : "bg-muted/50"
                    }`}
                  >
                    <span className="font-medium capitalize">
                      {field.replace(/_/g, " ")}:
                    </span>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-red-600 dark:text-red-400 line-through">
                        {formatValue(change.old)}
                      </span>
                      <span className="text-muted-foreground">→</span>
                      <span className="text-green-600 dark:text-green-400 font-medium">
                        {formatValue(change.new)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Metadata for create/delete */}
            {(log.action === "create" || log.action === "delete") &&
              log.metadata && (
                <div className="mt-3">
                  <p className="text-sm text-muted-foreground">
                    {log.action === "create"
                      ? "Service created"
                      : "Service deleted"}
                  </p>
                </div>
              )}
          </div>
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-6 pt-4 border-t border-border">
          <p className="text-sm text-muted-foreground">
            Page {page} of {totalPages}
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
            >
              <ChevronLeftIcon size={16} />
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
            >
              Next
              <ChevronRightIcon size={16} />
            </Button>
          </div>
        </div>
      )}
    </Card>
  );
}
