"use client";

import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  ShoppingBagIcon,
  CheckCircleIcon,
  ArrowRightIcon,
  RefundIcon,
  CalendarIcon,
  UserIcon,
  AlertTriangleIcon,
} from "@/components/icons";
import { usePackageAuditTrail } from "@/lib/api/hooks/usePackageAuditTrail";
import type { PackageAuditLog } from "@/lib/api/hooks/usePackageAuditTrail";

export function PackageAuditTrailView() {
  const [actionType, setActionType] = useState<string>("");
  const [entityType, setEntityType] = useState<string>("");
  const [entityId, setEntityId] = useState<string>("");
  const [clientId, setClientId] = useState<string>("");
  const [startDate, setStartDate] = useState<string>("");
  const [endDate, setEndDate] = useState<string>("");
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);

  const { data, isLoading, error } = usePackageAuditTrail(
    actionType || undefined,
    entityType || undefined,
    entityId || undefined,
    clientId || undefined,
    undefined,
    startDate || undefined,
    endDate || undefined,
    page,
    pageSize
  );

  const getActionIcon = (actionType: string) => {
    switch (actionType) {
      case "create":
        return <ShoppingBagIcon size={16} />;
      case "purchase":
        return <ShoppingBagIcon size={16} />;
      case "redeem":
        return <CheckCircleIcon size={16} />;
      case "transfer":
        return <ArrowRightIcon size={16} />;
      case "refund":
        return <RefundIcon size={16} />;
      case "extend":
        return <CalendarIcon size={16} />;
      default:
        return <ShoppingBagIcon size={16} />;
    }
  };

  const getActionColor = (actionType: string) => {
    switch (actionType) {
      case "create":
        return "bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-100";
      case "purchase":
        return "bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-100";
      case "redeem":
        return "bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-100";
      case "transfer":
        return "bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-100";
      case "refund":
        return "bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-100";
      case "extend":
        return "bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-100";
      default:
        return "bg-gray-100 dark:bg-gray-900 text-gray-800 dark:text-gray-100";
    }
  };

  const formatActionType = (actionType: string) => {
    return actionType
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const handleReset = () => {
    setActionType("");
    setEntityType("");
    setEntityId("");
    setClientId("");
    setStartDate("");
    setEndDate("");
    setPage(1);
  };

  if (error) {
    return (
      <Card className="p-6">
        <div className="flex items-center gap-2 text-red-600 dark:text-red-400">
          <AlertTriangleIcon size={20} />
          <p>Failed to load audit trail. Please try again.</p>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Filters */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-foreground mb-4">Filters</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div>
            <label className="text-sm font-medium text-foreground mb-2 block">
              Action Type
            </label>
            <Select value={actionType} onValueChange={setActionType}>
              <SelectTrigger>
                <SelectValue placeholder="All actions" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All actions</SelectItem>
                <SelectItem value="create">Create</SelectItem>
                <SelectItem value="purchase">Purchase</SelectItem>
                <SelectItem value="redeem">Redeem</SelectItem>
                <SelectItem value="transfer">Transfer</SelectItem>
                <SelectItem value="refund">Refund</SelectItem>
                <SelectItem value="extend">Extend</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <label className="text-sm font-medium text-foreground mb-2 block">
              Entity Type
            </label>
            <Select value={entityType} onValueChange={setEntityType}>
              <SelectTrigger>
                <SelectValue placeholder="All entities" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All entities</SelectItem>
                <SelectItem value="definition">Definition</SelectItem>
                <SelectItem value="purchase">Purchase</SelectItem>
                <SelectItem value="credit">Credit</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <label className="text-sm font-medium text-foreground mb-2 block">
              Entity ID
            </label>
            <Input
              placeholder="Enter entity ID"
              value={entityId}
              onChange={(e) => {
                setEntityId(e.target.value);
                setPage(1);
              }}
            />
          </div>

          <div>
            <label className="text-sm font-medium text-foreground mb-2 block">
              Client ID
            </label>
            <Input
              placeholder="Enter client ID"
              value={clientId}
              onChange={(e) => {
                setClientId(e.target.value);
                setPage(1);
              }}
            />
          </div>

          <div>
            <label className="text-sm font-medium text-foreground mb-2 block">
              Start Date
            </label>
            <Input
              type="datetime-local"
              value={startDate}
              onChange={(e) => {
                setStartDate(e.target.value);
                setPage(1);
              }}
            />
          </div>

          <div>
            <label className="text-sm font-medium text-foreground mb-2 block">
              End Date
            </label>
            <Input
              type="datetime-local"
              value={endDate}
              onChange={(e) => {
                setEndDate(e.target.value);
                setPage(1);
              }}
            />
          </div>
        </div>

        <div className="flex gap-2 mt-4">
          <Button onClick={handleReset} variant="outline">
            Reset Filters
          </Button>
        </div>
      </Card>

      {/* Audit Trail */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-foreground mb-6">
          Audit Trail
        </h3>

        {isLoading ? (
          <div className="flex justify-center py-8">
            <Spinner />
          </div>
        ) : !data || data.logs.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-muted-foreground">No audit logs found.</p>
          </div>
        ) : (
          <>
            <div className="space-y-4">
              {data.logs.map((log: PackageAuditLog, index: number) => (
                <div key={log.id} className="flex gap-4 pb-4 border-b last:border-b-0">
                  {/* Timeline icon */}
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${getActionColor(
                      log.action_type
                    )}`}
                  >
                    {getActionIcon(log.action_type)}
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <p className="font-medium text-foreground">
                          {formatActionType(log.action_type)}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          {formatDate(log.timestamp)}
                        </p>
                      </div>
                    </div>

                    <div className="mt-2 text-sm text-muted-foreground space-y-1">
                      <p>
                        <span className="font-medium">Entity:</span> {log.entity_type} (
                        {log.entity_id.substring(0, 8)}...)
                      </p>
                      {log.client_id && (
                        <p>
                          <span className="font-medium">Client:</span> {log.client_id}
                        </p>
                      )}
                      <p>
                        <span className="font-medium">Performed by:</span>{" "}
                        {log.performed_by_user_id} ({log.performed_by_role})
                      </p>

                      {/* Details */}
                      {Object.keys(log.details).length > 0 && (
                        <div className="mt-2 p-2 bg-muted rounded text-xs">
                          {Object.entries(log.details).map(([key, value]) => (
                            <p key={key}>
                              <span className="font-medium">{key}:</span>{" "}
                              {typeof value === "object"
                                ? JSON.stringify(value)
                                : String(value)}
                            </p>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            {data.total_pages > 1 && (
              <div className="flex items-center justify-between mt-6 pt-4 border-t">
                <p className="text-sm text-muted-foreground">
                  Showing {(page - 1) * pageSize + 1} to{" "}
                  {Math.min(page * pageSize, data.total)} of {data.total} logs
                </p>

                <div className="flex gap-2">
                  <Button
                    onClick={() => setPage(Math.max(1, page - 1))}
                    disabled={page === 1}
                    variant="outline"
                  >
                    Previous
                  </Button>

                  <div className="flex items-center gap-2">
                    {Array.from({ length: data.total_pages }, (_, i) => i + 1).map(
                      (p) => (
                        <Button
                          key={p}
                          onClick={() => setPage(p)}
                          variant={p === page ? "default" : "outline"}
                          size="sm"
                        >
                          {p}
                        </Button>
                      )
                    )}
                  </div>

                  <Button
                    onClick={() => setPage(Math.min(data.total_pages, page + 1))}
                    disabled={page === data.total_pages}
                    variant="outline"
                  >
                    Next
                  </Button>
                </div>
              </div>
            )}
          </>
        )}
      </Card>
    </div>
  );
}
