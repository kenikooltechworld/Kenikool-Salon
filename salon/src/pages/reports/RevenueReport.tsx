import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useRevenueReport } from "@/hooks/useFinancialReport";
import { Button } from "@/components/ui/button";
import { formatCurrency, formatDate } from "@/lib/utils/format";
import { DownloadIcon } from "@/components/icons";

export default function RevenueReport() {
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

  const { data: report, isLoading } = useRevenueReport(
    dateRange.start,
    dateRange.end,
  );

  const reportData = report as any;

  const handleExportCSV = () => {
    if (!reportData) return;

    const headers = ["Date", "Revenue", "Transactions"];
    const rows = (reportData.breakdown || []).map((item: any) => [
      item.date,
      item.revenue,
      item.transactions,
    ]);

    const csv = [
      headers.join(","),
      ...rows.map((row: any) => row.join(",")),
    ].join("\n");

    const blob = new Blob([csv], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `revenue-report-${dateRange.start}-to-${dateRange.end}.csv`;
    a.click();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Revenue Report</h1>
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
        <div className="text-center py-8">Loading revenue data...</div>
      ) : reportData ? (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-card border border-border rounded-lg p-6">
              <p className="text-sm text-muted-foreground">Total Revenue</p>
              <p className="text-3xl font-bold mt-2">
                {formatCurrency(reportData.total_revenue || 0)}
              </p>
            </div>
            <div className="bg-card border border-border rounded-lg p-6">
              <p className="text-sm text-muted-foreground">
                Total Transactions
              </p>
              <p className="text-3xl font-bold mt-2">
                {reportData.payment_count || 0}
              </p>
            </div>
            <div className="bg-card border border-border rounded-lg p-6">
              <p className="text-sm text-muted-foreground">
                Average Transaction
              </p>
              <p className="text-3xl font-bold mt-2">
                {formatCurrency(
                  (reportData.total_revenue || 0) /
                    (reportData.payment_count || 1),
                )}
              </p>
            </div>
          </div>

          {/* Revenue Breakdown */}
          <div className="bg-card border border-border rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold">Revenue Breakdown</h3>
              <Button
                variant="outline"
                size="sm"
                onClick={handleExportCSV}
                className="gap-2"
              >
                <DownloadIcon size={16} />
                Export CSV
              </Button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-muted border-b border-border">
                  <tr>
                    <th className="px-4 py-3 text-left text-sm font-semibold">
                      Date
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-semibold">
                      Revenue
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-semibold">
                      Transactions
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-semibold">
                      Average
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {(reportData.breakdown || []).map(
                    (item: any, index: number) => (
                      <tr key={index} className="hover:bg-muted/50">
                        <td className="px-4 py-3 text-sm">
                          {formatDate(item.date)}
                        </td>
                        <td className="px-4 py-3 text-sm font-medium">
                          {formatCurrency(item.revenue)}
                        </td>
                        <td className="px-4 py-3 text-sm">
                          {item.transactions}
                        </td>
                        <td className="px-4 py-3 text-sm">
                          {formatCurrency(item.revenue / item.transactions)}
                        </td>
                      </tr>
                    ),
                  )}
                </tbody>
              </table>
            </div>

            {(!reportData.breakdown || reportData.breakdown.length === 0) && (
              <p className="text-center py-8 text-muted-foreground">
                No data available for the selected date range
              </p>
            )}
          </div>

          {/* Revenue by Service */}
          {reportData.byService && reportData.byService.length > 0 && (
            <div className="bg-card border border-border rounded-lg p-6">
              <h3 className="font-semibold mb-4">Revenue by Service</h3>
              <div className="space-y-3">
                {reportData.byService.map((service: any, index: number) => (
                  <div
                    key={index}
                    className="flex items-center justify-between"
                  >
                    <span className="text-sm">{service.name}</span>
                    <div className="flex items-center gap-4">
                      <div className="w-32 bg-muted rounded-full h-2">
                        <div
                          className="bg-primary h-2 rounded-full"
                          style={{
                            width: `${
                              (service.revenue /
                                (reportData.total_revenue || 1)) *
                              100
                            }%`,
                          }}
                        />
                      </div>
                      <span className="font-medium w-24 text-right">
                        {formatCurrency(service.revenue)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Revenue by Staff */}
          {reportData.byStaff && reportData.byStaff.length > 0 && (
            <div className="bg-card border border-border rounded-lg p-6">
              <h3 className="font-semibold mb-4">Revenue by Staff Member</h3>
              <div className="space-y-3">
                {reportData.byStaff.map((staff: any, index: number) => (
                  <div
                    key={index}
                    className="flex items-center justify-between"
                  >
                    <span className="text-sm">{staff.name}</span>
                    <div className="flex items-center gap-4">
                      <div className="w-32 bg-muted rounded-full h-2">
                        <div
                          className="bg-green-600 h-2 rounded-full"
                          style={{
                            width: `${
                              (staff.revenue /
                                (reportData.total_revenue || 1)) *
                              100
                            }%`,
                          }}
                        />
                      </div>
                      <span className="font-medium w-24 text-right">
                        {formatCurrency(staff.revenue)}
                      </span>
                    </div>
                  </div>
                ))}
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
