import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { Badge } from "@/components/ui/badge";
import {
  DollarIcon,
  TrendingUpIcon,
  TrendingDownIcon,
  AlertTriangleIcon,
} from "@/components/icons";
import { cn } from "@/lib/utils/cn";

interface ExpenseBreakdown {
  category: string;
  amount: number;
}

interface ExpenseSummaryWidgetProps {
  totalExpenses: number;
  expenseTrend: number;
  breakdown: ExpenseBreakdown[];
  profitMargin: number;
  loading?: boolean;
}

export function ExpenseSummaryWidget({
  totalExpenses,
  expenseTrend,
  breakdown,
  profitMargin,
  loading = false,
}: ExpenseSummaryWidgetProps) {
  const isPositiveTrend = expenseTrend >= 0;
  const isProfitable = profitMargin > 0;

  return (
    <Card
      className="p-6 animate-in fade-in-0 slide-in-from-right-4 duration-500"
      role="region"
      aria-label="Expense Summary Widget"
    >
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-foreground">
          Expense Summary
        </h2>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => (window.location.href = "/dashboard/expenses")}
          className="transition-all duration-200 ease-out hover:scale-105"
          aria-label="View detailed expenses"
        >
          View Details
        </Button>
      </div>

      {loading ? (
        <div className="flex justify-center py-8">
          <Spinner />
        </div>
      ) : (
        <div className="space-y-4">
          {/* Total Expenses */}
          <div
            className="p-4 bg-[var(--muted)]/50 rounded-lg"
            role="group"
            aria-label="Total expenses"
          >
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-muted-foreground">Total Expenses</p>
              <div className="flex items-center gap-1">
                {isPositiveTrend ? (
                  <TrendingUpIcon
                    size={14}
                    className="text-[var(--error)]"
                    aria-hidden="true"
                  />
                ) : (
                  <TrendingDownIcon
                    size={14}
                    className="text-[var(--success)]"
                    aria-hidden="true"
                  />
                )}
                <span
                  className={cn(
                    "text-xs font-medium",
                    isPositiveTrend
                      ? "text-[var(--error)]"
                      : "text-[var(--success)]"
                  )}
                  aria-label={`Expense trend: ${
                    isPositiveTrend ? "increased" : "decreased"
                  } by ${Math.abs(expenseTrend).toFixed(1)} percent`}
                >
                  {isPositiveTrend ? "+" : ""}
                  {expenseTrend.toFixed(1)}%
                </span>
              </div>
            </div>
            <p className="text-2xl font-bold text-foreground">
              ₦{totalExpenses.toLocaleString()}
            </p>
          </div>

          {/* Profit Margin */}
          <div
            className="p-4 bg-[var(--muted)]/50 rounded-lg"
            role="group"
            aria-label="Profit margin"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground mb-1">
                  Profit Margin
                </p>
                <p className="text-xl font-bold text-foreground">
                  {profitMargin.toFixed(1)}%
                </p>
              </div>
              {!isProfitable && (
                <Badge
                  variant="error"
                  aria-label="Negative profit margin warning"
                >
                  <AlertTriangleIcon
                    size={12}
                    className="mr-1"
                    aria-hidden="true"
                  />
                  Negative
                </Badge>
              )}
            </div>
          </div>

          {/* Breakdown */}
          {breakdown.length > 0 && (
            <div
              className="space-y-2"
              role="group"
              aria-label="Top expense categories"
            >
              <p className="text-sm font-medium text-foreground">
                Top Categories
              </p>
              {breakdown.slice(0, 3).map((item, index) => {
                const percentage = (item.amount / totalExpenses) * 100;

                return (
                  <div
                    key={item.category}
                    className="animate-in fade-in-0 slide-in-from-right-2"
                    style={{ animationDelay: `${index * 50}ms` }}
                    role="group"
                    aria-label={`${
                      item.category
                    }: ₦${item.amount.toLocaleString()}, ${percentage.toFixed(
                      1
                    )}% of total`}
                  >
                    <div className="flex items-center justify-between text-sm mb-1">
                      <span className="text-muted-foreground">
                        {item.category}
                      </span>
                      <span className="font-medium text-foreground">
                        ₦{item.amount.toLocaleString()}
                      </span>
                    </div>
                    <div
                      className="h-2 bg-[var(--muted)] rounded-full overflow-hidden"
                      role="progressbar"
                      aria-valuenow={percentage}
                      aria-valuemin={0}
                      aria-valuemax={100}
                      aria-label={`${percentage.toFixed(1)}% of total expenses`}
                    >
                      <div
                        className="h-full bg-[var(--primary)] transition-all duration-500 ease-out"
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </Card>
  );
}
