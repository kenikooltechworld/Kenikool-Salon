import { useState } from "react";
import {
  useServiceCommissions,
  useCommissionSummary,
  usePendingCommissions,
  useMarkCommissionsAsPaidBatch,
} from "@/hooks/useServiceCommissions";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { useToast } from "@/components/ui/toast";

interface StaffCommissionDashboardProps {
  staffId: string;
  staffName?: string;
}

export function StaffCommissionDashboard({
  staffId,
  staffName,
}: StaffCommissionDashboardProps) {
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState<"pending" | "paid" | undefined>();
  const [startDate, setStartDate] = useState<string>("");
  const [endDate, setEndDate] = useState<string>("");
  const [selectedCommissions, setSelectedCommissions] = useState<Set<string>>(
    new Set(),
  );

  const { data: commissionsData, isLoading: commissionsLoading } =
    useServiceCommissions(staffId, {
      status,
      startDate: startDate || undefined,
      endDate: endDate || undefined,
      page,
      pageSize: 20,
    });

  const { data: summaryData } = useCommissionSummary(staffId, {
    startDate: startDate || undefined,
    endDate: endDate || undefined,
  });

  const { data: pendingData } = usePendingCommissions(staffId);
  const markAsPaidBatch = useMarkCommissionsAsPaidBatch();
  const { showToast } = useToast();

  const commissions = commissionsData?.commissions || [];
  const total = commissionsData?.total || 0;
  const summary = summaryData?.summary;
  const breakdown = summaryData?.breakdown || [];
  const pendingCommissions = pendingData?.commissions || [];

  const handleSelectCommission = (commissionId: string) => {
    const newSelected = new Set(selectedCommissions);
    if (newSelected.has(commissionId)) {
      newSelected.delete(commissionId);
    } else {
      newSelected.add(commissionId);
    }
    setSelectedCommissions(newSelected);
  };

  const handleSelectAll = () => {
    if (selectedCommissions.size === pendingCommissions.length) {
      setSelectedCommissions(new Set());
    } else {
      setSelectedCommissions(new Set(pendingCommissions.map((c) => c.id)));
    }
  };

  const handleMarkAsPaid = async () => {
    if (selectedCommissions.size === 0) {
      showToast({
        title: "Error",
        description: "Please select at least one commission",
        variant: "error",
      });
      return;
    }

    try {
      await markAsPaidBatch.mutateAsync({
        staffId,
        commissionIds: Array.from(selectedCommissions),
      });
      setSelectedCommissions(new Set());
      showToast({
        title: "Success",
        description: `Marked ${selectedCommissions.size} commission(s) as paid`,
        variant: "success",
      });
    } catch (error) {
      showToast({
        title: "Error",
        description: "Failed to mark commissions as paid",
        variant: "error",
      });
    }
  };

  return (
    <div className="space-y-4 md:space-y-6">
      {/* Header */}
      {staffName && (
        <div className="mb-4">
          <h2 className="text-2xl font-bold text-foreground">{staffName}</h2>
          <p className="text-sm text-muted-foreground">Commission Earnings</p>
        </div>
      )}

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 md:gap-4">
          <Card className="p-4 md:p-6">
            <p className="text-xs md:text-sm text-muted-foreground mb-2">
              Total Earned
            </p>
            <p className="text-2xl md:text-3xl font-bold text-foreground">
              ₦
              {summary.totalEarned.toLocaleString("en-NG", {
                maximumFractionDigits: 2,
              })}
            </p>
          </Card>
          <Card className="p-4 md:p-6">
            <p className="text-xs md:text-sm text-muted-foreground mb-2">
              Pending
            </p>
            <p className="text-2xl md:text-3xl font-bold text-yellow-600">
              ₦
              {summary.totalPending.toLocaleString("en-NG", {
                maximumFractionDigits: 2,
              })}
            </p>
          </Card>
          <Card className="p-4 md:p-6">
            <p className="text-xs md:text-sm text-muted-foreground mb-2">
              Paid
            </p>
            <p className="text-2xl md:text-3xl font-bold text-green-600">
              ₦
              {summary.totalPaid.toLocaleString("en-NG", {
                maximumFractionDigits: 2,
              })}
            </p>
          </Card>
          <Card className="p-4 md:p-6">
            <p className="text-xs md:text-sm text-muted-foreground mb-2">
              Services
            </p>
            <p className="text-2xl md:text-3xl font-bold text-foreground">
              {summary.totalServices}
            </p>
          </Card>
        </div>
      )}

      {/* Filters */}
      <Card className="p-4 md:p-6">
        <h3 className="text-base md:text-lg font-semibold text-foreground mb-4">
          Filters
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 md:gap-4">
          <div>
            <label className="block text-xs md:text-sm font-medium text-foreground mb-2">
              Status
            </label>
            <select
              value={status || ""}
              onChange={(e) => {
                setStatus((e.target.value as "pending" | "paid") || undefined);
                setPage(1);
              }}
              className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground text-sm"
            >
              <option value="">All</option>
              <option value="pending">Pending</option>
              <option value="paid">Paid</option>
            </select>
          </div>
          <div>
            <label className="block text-xs md:text-sm font-medium text-foreground mb-2">
              Start Date
            </label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => {
                setStartDate(e.target.value);
                setPage(1);
              }}
              className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground text-sm"
            />
          </div>
          <div>
            <label className="block text-xs md:text-sm font-medium text-foreground mb-2">
              End Date
            </label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => {
                setEndDate(e.target.value);
                setPage(1);
              }}
              className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground text-sm"
            />
          </div>
          <div className="flex items-end">
            <Button
              variant="outline"
              onClick={() => {
                setStatus(undefined);
                setStartDate("");
                setEndDate("");
                setPage(1);
              }}
              className="w-full text-sm"
            >
              Clear Filters
            </Button>
          </div>
        </div>
      </Card>

      {/* Service Breakdown */}
      {breakdown.length > 0 && (
        <Card className="p-4 md:p-6">
          <h3 className="text-base md:text-lg font-semibold text-foreground mb-4">
            Commission by Service
          </h3>
          <div className="space-y-2 md:space-y-3">
            {breakdown.map((item) => (
              <div
                key={item.serviceId}
                className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-2 p-3 md:p-4 bg-muted rounded-lg"
              >
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm md:text-base text-foreground truncate">
                    {item.serviceName || "Unknown Service"}
                  </p>
                  <p className="text-xs md:text-sm text-muted-foreground">
                    {item.count} service{item.count !== 1 ? "s" : ""}
                  </p>
                </div>
                <div className="text-right flex-shrink-0">
                  <p className="font-bold text-sm md:text-base text-foreground">
                    ₦
                    {item.totalCommission.toLocaleString("en-NG", {
                      maximumFractionDigits: 2,
                    })}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Commissions List */}
      <Card className="p-4 md:p-6">
        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3 mb-4">
          <h3 className="text-base md:text-lg font-semibold text-foreground">
            Commission Details
          </h3>
          {pendingCommissions.length > 0 && (
            <Button
              onClick={handleMarkAsPaid}
              disabled={
                selectedCommissions.size === 0 || markAsPaidBatch.isPending
              }
              className="text-sm"
            >
              {markAsPaidBatch.isPending
                ? "Processing..."
                : `Mark as Paid (${selectedCommissions.size})`}
            </Button>
          )}
        </div>

        {commissionsLoading ? (
          <div className="flex justify-center py-8">
            <Spinner />
          </div>
        ) : commissions.length === 0 ? (
          <p className="text-muted-foreground text-center py-8">
            No commissions found
          </p>
        ) : (
          <div className="space-y-2 md:space-y-3">
            {/* Select All for Pending */}
            {status === "pending" && pendingCommissions.length > 0 && (
              <div className="flex items-center gap-2 p-3 md:p-4 bg-muted rounded-lg">
                <input
                  type="checkbox"
                  checked={
                    selectedCommissions.size === pendingCommissions.length &&
                    pendingCommissions.length > 0
                  }
                  onChange={handleSelectAll}
                  className="w-4 h-4 rounded border-border"
                />
                <span className="text-sm text-muted-foreground">
                  Select All ({pendingCommissions.length})
                </span>
              </div>
            )}

            {commissions.map((commission) => (
              <div
                key={commission.id}
                className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-2 p-3 md:p-4 bg-muted rounded-lg"
              >
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  {commission.status === "pending" && (
                    <input
                      type="checkbox"
                      checked={selectedCommissions.has(commission.id)}
                      onChange={() => handleSelectCommission(commission.id)}
                      className="w-4 h-4 rounded border-border flex-shrink-0"
                    />
                  )}
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-sm md:text-base text-foreground truncate">
                      Service Commission
                    </p>
                    <p className="text-xs md:text-sm text-muted-foreground">
                      {new Date(commission.earnedDate).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <div className="text-right flex-shrink-0">
                  <p className="font-bold text-sm md:text-base text-foreground">
                    ₦
                    {commission.commissionAmount.toLocaleString("en-NG", {
                      maximumFractionDigits: 2,
                    })}
                  </p>
                  <div className="flex gap-2 justify-end mt-1">
                    <Badge variant="secondary" className="text-xs">
                      {commission.commissionPercentage}%
                    </Badge>
                    <Badge
                      variant={
                        commission.status === "paid" ? "default" : "secondary"
                      }
                      className="text-xs"
                    >
                      {commission.status}
                    </Badge>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Pagination */}
        {total > 20 && (
          <div className="flex justify-between items-center mt-6 pt-6 border-t border-border gap-2 flex-wrap">
            <Button
              variant="outline"
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page === 1}
              className="text-sm"
            >
              Previous
            </Button>
            <span className="text-xs md:text-sm text-muted-foreground">
              Page {page} of {Math.ceil(total / 20)}
            </span>
            <Button
              variant="outline"
              onClick={() => setPage(page + 1)}
              disabled={page >= Math.ceil(total / 20)}
              className="text-sm"
            >
              Next
            </Button>
          </div>
        )}
      </Card>
    </div>
  );
}
