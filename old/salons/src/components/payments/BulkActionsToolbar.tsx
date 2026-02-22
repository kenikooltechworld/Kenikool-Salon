"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Progress } from "@/components/ui/progress";
import { AlertCircle, Download, X } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  useBulkExportPayments,
  useBulkStatusUpdate,
} from "@/lib/api/hooks/useBulkPaymentOperations";
import type { Payment } from "@/lib/api/types";

interface BulkActionsToolbarProps {
  selectedPayments: Payment[];
  onClearSelection: () => void;
}

export function BulkActionsToolbar({
  selectedPayments,
  onClearSelection,
}: BulkActionsToolbarProps) {
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [exportProgress, setExportProgress] = useState(0);
  const [showProgress, setShowProgress] = useState(false);

  const exportMutation = useBulkExportPayments({
    onSuccess: (blob) => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `payments-export-${new Date().toISOString().split("T")[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      setShowProgress(false);
      setExportProgress(0);
    },
    onError: () => {
      setShowProgress(false);
      setExportProgress(0);
    },
  });

  const statusUpdateMutation = useBulkStatusUpdate({
    onSuccess: () => {
      setShowProgress(false);
      setExportProgress(0);
      setStatusFilter("");
      onClearSelection();
    },
  });

  const handleExport = () => {
    if (selectedPayments.length === 0) return;

    setShowProgress(true);
    setExportProgress(30);

    setTimeout(() => {
      setExportProgress(60);
      exportMutation.mutate({
        payment_ids: selectedPayments.map((p) => p.id),
        format: "csv",
      });
      setExportProgress(100);
    }, 500);
  };

  const handleStatusUpdate = () => {
    if (!statusFilter || selectedPayments.length === 0) return;

    setShowProgress(true);
    setExportProgress(30);

    setTimeout(() => {
      setExportProgress(60);
      statusUpdateMutation.mutate({
        payment_ids: selectedPayments.map((p) => p.id),
        status: statusFilter,
      });
      setExportProgress(100);
    }, 500);
  };

  if (selectedPayments.length === 0) {
    return null;
  }

  return (
    <div className="space-y-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <span className="font-medium">
            {selectedPayments.length} payment{selectedPayments.length !== 1 ? "s" : ""} selected
          </span>

          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Update status..." />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="pending">Pending</SelectItem>
              <SelectItem value="completed">Completed</SelectItem>
              <SelectItem value="failed">Failed</SelectItem>
              <SelectItem value="refunded">Refunded</SelectItem>
            </SelectContent>
          </Select>

          <Button
            size="sm"
            onClick={handleStatusUpdate}
            disabled={!statusFilter || statusUpdateMutation.isPending}
          >
            Update Status
          </Button>

          <Button
            size="sm"
            variant="outline"
            onClick={handleExport}
            disabled={exportMutation.isPending}
          >
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>

          <Button
            size="sm"
            variant="ghost"
            onClick={onClearSelection}
            disabled={showProgress}
          >
            <X className="h-4 w-4 mr-2" />
            Clear
          </Button>
        </div>
      </div>

      {showProgress && (
        <div className="space-y-2">
          <Progress value={exportProgress} className="h-2" />
          <p className="text-sm text-gray-600">
            {exportProgress < 100 ? "Processing..." : "Complete"}
          </p>
        </div>
      )}

      {exportMutation.isError && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Failed to export payments. Please try again.
          </AlertDescription>
        </Alert>
      )}

      {statusUpdateMutation.isError && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Failed to update payment status. Please try again.
          </AlertDescription>
        </Alert>
      )}

      {statusUpdateMutation.isSuccess && (
        <Alert>
          <AlertDescription className="text-green-700">
            Successfully updated {statusUpdateMutation.data?.processed_count} payment(s).
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
}
