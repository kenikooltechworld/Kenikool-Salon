import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { usePaymentReport } from "@/hooks/useFinancialReport";
import { Button } from "@/components/ui/button";
import { formatCurrency } from "@/lib/utils/format";

export default function PaymentStats() {
  const navigate = useNavigate();

  // Convert local date to YYYY-MM-DD format (not UTC)
  const getLocalDateString = (date: Date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
  };

  const [dateRange, setDateRange] = useState({
    start: getLocalDateString(new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)),
    end: getLocalDateString(new Date()),
  });

  const { data: report, isLoading } = usePaymentReport(
    dateRange.start,
    dateRange.end,
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Payment Statistics</h1>
        <Button variant="outline" onClick={() => navigate("/reports")}>
          Back
        </Button>
      </div>

      {/* Date Range Filter */}
      <div className="bg-card border border-border rounded-lg p-6">
        <h3 className="font-semibold mb-4">Filter by Date Range</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Start Date</label>
            <input
              type="date"
              value={dateRange.start}
              onChange={(e) =>
                setDateRange({ ...dateRange, start: e.target.value })
              }
              className="w-full px-3 py-2 border border-border rounded-lg"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">End Date</label>
            <input
              type="date"
              value={dateRange.end}
              onChange={(e) =>
                setDateRange({ ...dateRange, end: e.target.value })
              }
              className="w-full px-3 py-2 border border-border rounded-lg"
            />
          </div>
        </div>
      </div>

      {isLoading ? (
        <div className="text-center py-8">Loading payment statistics...</div>
      ) : report ? (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-card border border-border rounded-lg p-6">
              <p className="text-sm text-muted-foreground">Total Payments</p>
              <p className="text-3xl font-bold mt-2">
                {report.totalPayments || 0}
              </p>
            </div>
            <div className="bg-card border border-border rounded-lg p-6">
              <p className="text-sm text-muted-foreground">Successful</p>
              <p className="text-3xl font-bold text-green-600 mt-2">
                {report.successfulPayments || 0}
              </p>
            </div>
            <div className="bg-card border border-border rounded-lg p-6">
              <p className="text-sm text-muted-foreground">Failed</p>
              <p className="text-3xl font-bold text-destructive mt-2">
                {report.failedPayments || 0}
              </p>
            </div>
            <div className="bg-card border border-border rounded-lg p-6">
              <p className="text-sm text-muted-foreground">Success Rate</p>
              <p className="text-3xl font-bold text-blue-600 mt-2">
                {report.successRate
                  ? `${report.successRate.toFixed(1)}%`
                  : "0%"}
              </p>
            </div>
          </div>

          {/* Amount Statistics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-card border border-border rounded-lg p-6">
              <p className="text-sm text-muted-foreground">Total Amount</p>
              <p className="text-2xl font-bold mt-2">
                {formatCurrency(report.totalAmount || 0)}
              </p>
            </div>
            <div className="bg-card border border-border rounded-lg p-6">
              <p className="text-sm text-muted-foreground">Average Payment</p>
              <p className="text-2xl font-bold mt-2">
                {formatCurrency(
                  (report.totalAmount || 0) / (report.totalPayments || 1),
                )}
              </p>
            </div>
            <div className="bg-card border border-border rounded-lg p-6">
              <p className="text-sm text-muted-foreground">Highest Payment</p>
              <p className="text-2xl font-bold mt-2">
                {formatCurrency(report.highestPayment || 0)}
              </p>
            </div>
          </div>

          {/* Payment Methods Breakdown */}
          {report.byMethod && report.byMethod.length > 0 && (
            <div className="bg-card border border-border rounded-lg p-6">
              <h3 className="font-semibold mb-4">Payment Methods</h3>
              <div className="space-y-3">
                {report.byMethod.map((method: any, index: number) => (
                  <div
                    key={index}
                    className="flex items-center justify-between"
                  >
                    <span className="text-sm capitalize">{method.method}</span>
                    <div className="flex items-center gap-4">
                      <div className="w-32 bg-muted rounded-full h-2">
                        <div
                          className="bg-primary h-2 rounded-full"
                          style={{
                            width: `${
                              (method.count / (report.totalPayments || 1)) * 100
                            }%`,
                          }}
                        />
                      </div>
                      <span className="font-medium w-16 text-right">
                        {method.count}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Status Distribution */}
          {report.byStatus && report.byStatus.length > 0 && (
            <div className="bg-card border border-border rounded-lg p-6">
              <h3 className="font-semibold mb-4">Status Distribution</h3>
              <div className="space-y-3">
                {report.byStatus.map((status: any, index: number) => {
                  const statusColors: Record<string, string> = {
                    completed: "bg-green-600",
                    pending: "bg-yellow-600",
                    failed: "bg-destructive",
                    refunded: "bg-blue-600",
                  };
                  return (
                    <div
                      key={index}
                      className="flex items-center justify-between"
                    >
                      <span className="text-sm capitalize">
                        {status.status}
                      </span>
                      <div className="flex items-center gap-4">
                        <div className="w-32 bg-muted rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${
                              statusColors[status.status] || "bg-gray-600"
                            }`}
                            style={{
                              width: `${
                                (status.count / (report.totalPayments || 1)) *
                                100
                              }%`,
                            }}
                          />
                        </div>
                        <span className="font-medium w-16 text-right">
                          {status.count}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Top Customers */}
          {report.topCustomers && report.topCustomers.length > 0 && (
            <div className="bg-card border border-border rounded-lg p-6">
              <h3 className="font-semibold mb-4">
                Top Customers by Payment Amount
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-muted border-b border-border">
                    <tr>
                      <th className="px-4 py-3 text-left text-sm font-semibold">
                        Customer
                      </th>
                      <th className="px-4 py-3 text-left text-sm font-semibold">
                        Payments
                      </th>
                      <th className="px-4 py-3 text-left text-sm font-semibold">
                        Total Amount
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {report.topCustomers.map((customer: any, index: number) => (
                      <tr key={index} className="hover:bg-muted/50">
                        <td className="px-4 py-3 text-sm">{customer.name}</td>
                        <td className="px-4 py-3 text-sm">
                          {customer.paymentCount}
                        </td>
                        <td className="px-4 py-3 text-sm font-medium">
                          {formatCurrency(customer.totalAmount)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-8 text-muted-foreground">
          No data available
        </div>
      )}
    </div>
  );
}
