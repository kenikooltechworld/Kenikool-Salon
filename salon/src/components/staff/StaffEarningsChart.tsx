import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { Button } from "@/components/ui/button";
import { RefreshCwIcon } from "@/components/icons";
import type { Commission } from "@/hooks/useMyEarnings";

interface StaffEarningsChartProps {
  commissions: Commission[];
  isLoading?: boolean;
  error?: string;
  onRetry?: () => void;
  period?: {
    startDate: string;
    endDate: string;
  };
}

/**
 * Visual earnings data component showing commission trends
 * Displays earnings over time with breakdown by period
 */
export function StaffEarningsChart({
  commissions,
  isLoading = false,
  error,
  onRetry,
  period,
}: StaffEarningsChartProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Earnings Trend</CardTitle>
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
          <CardTitle>Earnings Trend</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <p className="text-sm text-destructive font-medium">
            Unable to load earnings chart
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

  // Group commissions by date for trend visualization
  const earningsByDate = commissions.reduce(
    (acc, commission) => {
      const date = new Date(commission.calculated_at).toLocaleDateString();
      if (!acc[date]) {
        acc[date] = 0;
      }
      acc[date] += commission.commission_amount;
      return acc;
    },
    {} as Record<string, number>,
  );

  const sortedDates = Object.keys(earningsByDate).sort(
    (a, b) => new Date(a).getTime() - new Date(b).getTime(),
  );

  const totalEarnings = commissions.reduce(
    (sum, c) => sum + c.commission_amount,
    0,
  );
  const averageEarnings =
    commissions.length > 0 ? totalEarnings / commissions.length : 0;
  const maxEarning = Math.max(...Object.values(earningsByDate), 1);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Earnings Trend</CardTitle>
          {onRetry && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onRetry}
              title="Refresh chart"
              className="px-2"
            >
              <RefreshCwIcon size={14} />
            </Button>
          )}
        </div>
        {period && (
          <p className="text-xs text-muted-foreground mt-2">
            {new Date(period.startDate).toLocaleDateString()} -{" "}
            {new Date(period.endDate).toLocaleDateString()}
          </p>
        )}
      </CardHeader>
      <CardContent className="space-y-4">
        {commissions.length === 0 ? (
          <p className="text-muted-foreground text-center py-8">
            No earnings data available
          </p>
        ) : (
          <>
            {/* Summary Stats */}
            <div className="grid grid-cols-3 gap-2">
              <div className="p-2 bg-muted rounded">
                <p className="text-xs text-muted-foreground">Total</p>
                <p className="text-sm font-bold">
                  ₦
                  {totalEarnings.toLocaleString("en-NG", {
                    maximumFractionDigits: 2,
                  })}
                </p>
              </div>
              <div className="p-2 bg-muted rounded">
                <p className="text-xs text-muted-foreground">Average</p>
                <p className="text-sm font-bold">
                  ₦
                  {averageEarnings.toLocaleString("en-NG", {
                    maximumFractionDigits: 2,
                  })}
                </p>
              </div>
              <div className="p-2 bg-muted rounded">
                <p className="text-xs text-muted-foreground">Transactions</p>
                <p className="text-sm font-bold">{commissions.length}</p>
              </div>
            </div>

            {/* Simple Bar Chart */}
            <div className="space-y-2">
              <p className="text-xs font-medium text-muted-foreground">
                Daily Earnings
              </p>
              <div className="space-y-1">
                {sortedDates.slice(-7).map((date) => {
                  const amount = earningsByDate[date];
                  const percentage = (amount / maxEarning) * 100;
                  return (
                    <div key={date} className="flex items-center gap-2">
                      <span className="text-xs text-muted-foreground w-16 truncate">
                        {new Date(date).toLocaleDateString("en-NG", {
                          month: "short",
                          day: "numeric",
                        })}
                      </span>
                      <div className="flex-1 bg-muted rounded h-6 overflow-hidden">
                        <div
                          className="bg-primary h-full transition-all"
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                      <span className="text-xs font-medium w-20 text-right">
                        ₦
                        {amount.toLocaleString("en-NG", {
                          maximumFractionDigits: 0,
                        })}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
