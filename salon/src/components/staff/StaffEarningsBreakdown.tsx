import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { Button } from "@/components/ui/button";
import { RefreshCwIcon } from "@/components/icons";
import type { Commission } from "@/hooks/useMyEarnings";

interface StaffEarningsBreakdownProps {
  commissions: Commission[];
  isLoading?: boolean;
  error?: string;
  onRetry?: () => void;
  breakdownType?: "service" | "date";
}

interface BreakdownItem {
  label: string;
  amount: number;
  count: number;
  percentage: number;
}

/**
 * Earnings breakdown component showing commission details by service or date
 * Displays breakdown with percentages and transaction counts
 */
export function StaffEarningsBreakdown({
  commissions,
  isLoading = false,
  error,
  onRetry,
  breakdownType = "service",
}: StaffEarningsBreakdownProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>
            {breakdownType === "service"
              ? "Earnings by Service"
              : "Earnings by Date"}
          </CardTitle>
        </CardHeader>
        <CardContent className="flex justify-center py-8">
          <Spinner />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card
        variant="outlined"
        className="border-destructive/50 bg-destructive/5"
      >
        <CardHeader>
          <CardTitle>
            {breakdownType === "service"
              ? "Earnings by Service"
              : "Earnings by Date"}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <p className="text-sm text-destructive font-medium">
            Unable to load breakdown
          </p>
          <p className="text-xs text-muted-foreground">{error}</p>
          {onRetry && (
            <Button
              variant="outline"
              size="sm"
              onClick={onRetry}
              className="w-full"
            >
              <RefreshCwIcon size={14} className="mr-1" />
              Retry
            </Button>
          )}
        </CardContent>
      </Card>
    );
  }

  // Calculate breakdown based on type
  const breakdownMap: Record<string, { amount: number; count: number }> = {};

  commissions.forEach((commission) => {
    let key: string;

    if (breakdownType === "service") {
      // Group by commission type (percentage vs fixed)
      key =
        commission.commission_type === "percentage" ? "Percentage" : "Fixed";
    } else {
      // Group by date (week)
      const date = new Date(commission.calculated_at);
      const weekStart = new Date(date);
      weekStart.setDate(date.getDate() - date.getDay());
      key = weekStart.toLocaleDateString("en-NG", {
        month: "short",
        day: "numeric",
      });
    }

    if (!breakdownMap[key]) {
      breakdownMap[key] = { amount: 0, count: 0 };
    }
    breakdownMap[key].amount += commission.commission_amount;
    breakdownMap[key].count += 1;
  });

  const totalAmount = commissions.reduce(
    (sum, c) => sum + c.commission_amount,
    0,
  );

  const breakdownItems: BreakdownItem[] = Object.entries(breakdownMap)
    .map(([label, data]) => ({
      label,
      amount: data.amount,
      count: data.count,
      percentage: totalAmount > 0 ? (data.amount / totalAmount) * 100 : 0,
    }))
    .sort((a, b) => b.amount - a.amount);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>
            {breakdownType === "service"
              ? "Earnings by Type"
              : "Earnings by Week"}
          </CardTitle>
          {onRetry && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onRetry}
              title="Refresh breakdown"
              className="px-2"
            >
              <RefreshCwIcon size={14} />
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {commissions.length === 0 ? (
          <p className="text-muted-foreground text-center py-8">
            No earnings data available
          </p>
        ) : (
          <div className="space-y-3">
            {breakdownItems.map((item) => (
              <div key={item.label} className="space-y-1">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium">{item.label}</span>
                    <Badge variant="secondary" className="text-xs">
                      {item.count}
                    </Badge>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-bold">
                      ₦
                      {item.amount.toLocaleString("en-NG", {
                        maximumFractionDigits: 2,
                      })}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {item.percentage.toFixed(1)}%
                    </p>
                  </div>
                </div>
                <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-primary h-full transition-all"
                    style={{ width: `${item.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
