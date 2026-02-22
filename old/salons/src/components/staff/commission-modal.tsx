import { Modal } from "@/components/ui/modal";
import { Card } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DollarIcon,
  CalendarIcon,
  AlertTriangleIcon,
  DownloadIcon,
} from "@/components/icons";
import { useStylistCommissions } from "@/lib/api/hooks/useStylists";
import { Stylist } from "@/lib/api/types";
import { useState } from "react";

interface CommissionModalProps {
  isOpen: boolean;
  onClose: () => void;
  stylist: Stylist;
}

export function CommissionModal({
  isOpen,
  onClose,
  stylist,
}: CommissionModalProps) {
  const [dateRange, setDateRange] = useState({
    start: new Date(new Date().setDate(1)).toISOString().split("T")[0], // First day of month
    end: new Date().toISOString().split("T")[0], // Today
  });

  const {
    data: commissions,
    isLoading,
    error,
  } = useStylistCommissions(stylist.id, dateRange);

  const totalCommission =
    commissions?.reduce(
      (sum: number, c: any) => sum + (c.commission_amount || 0),
      0
    ) || 0;

  const handleExport = () => {
    // Export commission data as CSV
    const csvContent = [
      ["Date", "Service", "Client", "Service Price", "Commission Amount"],
      ...(commissions || []).map((c: any) => [
        new Date(c.booking_date).toLocaleDateString(),
        c.service_name,
        c.client_name,
        `₦${c.service_price}`,
        `₦${c.commission_amount}`,
      ]),
    ]
      .map((row) => row.join(","))
      .join("\n");

    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${stylist.name}-commissions-${dateRange.start}-to-${dateRange.end}.csv`;
    a.click();
  };

  return (
    <Modal open={isOpen} onClose={onClose} size="xl">
      <div className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-foreground">
            Commission Breakdown - {stylist.name}
          </h2>
          <Button variant="outline" size="sm" onClick={handleExport}>
            <DownloadIcon size={16} />
            Export CSV
          </Button>
        </div>

        {/* Date Range Filter */}
        <Card className="p-4 mb-6">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-1">
                Start Date
              </label>
              <input
                type="date"
                value={dateRange.start}
                onChange={(e) =>
                  setDateRange({ ...dateRange, start: e.target.value })
                }
                className="w-full px-3 py-2 border border-[var(--border)] rounded-lg bg-background text-foreground"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-foreground mb-1">
                End Date
              </label>
              <input
                type="date"
                value={dateRange.end}
                onChange={(e) =>
                  setDateRange({ ...dateRange, end: e.target.value })
                }
                className="w-full px-3 py-2 border border-[var(--border)] rounded-lg bg-background text-foreground"
              />
            </div>
          </div>
        </Card>

        {isLoading ? (
          <div className="flex justify-center py-12">
            <Spinner />
          </div>
        ) : error ? (
          <Alert variant="error">
            <AlertTriangleIcon size={20} />
            <div>
              <h3 className="font-semibold">Error loading commission data</h3>
              <p className="text-sm">{error.message}</p>
            </div>
          </Alert>
        ) : (
          <>
            {/* Summary */}
            <Card className="p-4 mb-6 bg-[var(--primary)]/10 border-[var(--primary)]">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <DollarIcon size={24} className="text-[var(--primary)]" />
                  <div>
                    <p className="text-sm text-muted-foreground">
                      Total Commission
                    </p>
                    <p className="text-2xl font-bold text-foreground">
                      ₦{totalCommission.toLocaleString()}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm text-muted-foreground">
                    {commissions?.length || 0} Services
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {dateRange.start} to {dateRange.end}
                  </p>
                </div>
              </div>
            </Card>

            {/* Commission List */}
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {commissions && commissions.length > 0 ? (
                commissions.map((commission: any) => (
                  <Card key={commission.id} className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h3 className="font-semibold text-foreground">
                            {commission.service_name}
                          </h3>
                          <Badge variant="secondary" size="sm">
                            {commission.booking_status}
                          </Badge>
                        </div>
                        <div className="grid grid-cols-2 gap-2 text-sm">
                          <div>
                            <span className="text-muted-foreground">
                              Client:
                            </span>{" "}
                            <span className="text-foreground">
                              {commission.client_name}
                            </span>
                          </div>
                          <div>
                            <span className="text-muted-foreground">Date:</span>{" "}
                            <span className="text-foreground">
                              {new Date(
                                commission.booking_date
                              ).toLocaleDateString()}
                            </span>
                          </div>
                          <div>
                            <span className="text-muted-foreground">
                              Service Price:
                            </span>{" "}
                            <span className="text-foreground">
                              ₦{commission.service_price?.toLocaleString()}
                            </span>
                          </div>
                          <div>
                            <span className="text-muted-foreground">
                              Commission Rate:
                            </span>{" "}
                            <span className="text-foreground">
                              {commission.commission_rate
                                ? `${(commission.commission_rate * 100).toFixed(
                                    0
                                  )}%`
                                : "N/A"}
                            </span>
                          </div>
                        </div>
                      </div>
                      <div className="text-right ml-4">
                        <p className="text-xs text-muted-foreground mb-1">
                          Commission
                        </p>
                        <p className="text-xl font-bold text-[var(--success)]">
                          ₦{commission.commission_amount?.toLocaleString()}
                        </p>
                      </div>
                    </div>
                  </Card>
                ))
              ) : (
                <div className="text-center py-12">
                  <DollarIcon
                    size={48}
                    className="mx-auto text-muted-foreground mb-3"
                  />
                  <p className="text-muted-foreground">
                    No commissions found for this period
                  </p>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </Modal>
  );
}
