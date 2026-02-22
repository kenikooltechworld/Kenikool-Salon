import { useState } from "react";
import {
  useExpenseSummary,
  useProfitLoss,
  useFinancialReport,
} from "@/lib/api/hooks/useExpenses";
import { MetricCard } from "./metric-card";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { DownloadIcon, DollarSignIcon } from "@/components/icons";
import { showToast } from "@/lib/utils/toast";

export function FinancialReports() {
  const [startDate, setStartDate] = useState<string>("");
  const [endDate, setEndDate] = useState<string>("");

  const { data: summary, isLoading: summaryLoading } = useExpenseSummary(
    startDate,
    endDate,
  );
  const { data: profitLoss, isLoading: profitLossLoading } = useProfitLoss(
    startDate,
    endDate,
  );
  const reportMutation = useFinancialReport();

  const handleDownloadReport = async () => {
    try {
      await reportMutation.mutateAsync({
        startDate,
        endDate,
      });
      showToast("Report downloaded successfully", "success");
    } catch (error: any) {
      showToast(
        error.response?.data?.detail || "Failed to download report",
        "error",
      );
    }
  };

  const isLoading = summaryLoading || profitLossLoading;

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Report Period</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <Label htmlFor="report_start_date">Start Date</Label>
            <Input
              id="report_start_date"
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
          </div>

          <div>
            <Label htmlFor="report_end_date">End Date</Label>
            <Input
              id="report_end_date"
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
            />
          </div>

          <div className="flex items-end">
            <Button
              onClick={handleDownloadReport}
              disabled={reportMutation.isPending}
              className="w-full gap-2"
            >
              <DownloadIcon size={20} />
              {reportMutation.isPending ? "Generating..." : "Download PDF"}
            </Button>
          </div>
        </div>
      </Card>

      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <Spinner size="lg" />
        </div>
      ) : (
        <>
          {profitLoss && (
            <div>
              <h3 className="text-lg font-semibold mb-4">Profit & Loss</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <MetricCard
                  label="Total Revenue"
                  value={profitLoss.total_revenue}
                  format="currency"
                  isPositive={true}
                  icon={
                    <DollarSignIcon
                      size={24}
                      className="text-[var(--success)]"
                    />
                  }
                />
                <MetricCard
                  label="Total Expenses"
                  value={profitLoss.total_expenses}
                  format="currency"
                  isPositive={false}
                  icon={
                    <DollarSignIcon
                      size={24}
                      className="text-[var(--destructive)]"
                    />
                  }
                />
                <MetricCard
                  label="Profit/Loss"
                  value={profitLoss.profit_loss}
                  format="currency"
                  isPositive={profitLoss.is_profitable}
                />
                <MetricCard
                  label="Profit Margin"
                  value={profitLoss.profit_margin}
                  format="percentage"
                  isPositive={profitLoss.is_profitable}
                />
              </div>
            </div>
          )}

          {summary && summary.category_breakdown.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold mb-4">
                Expense Breakdown by Category
              </h3>
              <Card className="p-6">
                <div className="space-y-4">
                  {summary.category_breakdown.map((category) => (
                    <div key={category.category}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium">{category.category}</span>
                        <span className="text-sm text-[var(--muted-foreground)]">
                          ₦{category.total_amount.toFixed(2)} ({category.count}{" "}
                          items)
                        </span>
                      </div>
                      <div className="w-full bg-[var(--muted)] rounded-full h-2 overflow-hidden">
                        <div
                          className="bg-[var(--primary)] h-full rounded-full transition-all duration-300"
                          style={{
                            width: `${
                              (category.total_amount / summary.total_expenses) *
                              100
                            }%`,
                          }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          )}
        </>
      )}
    </div>
  );
}
