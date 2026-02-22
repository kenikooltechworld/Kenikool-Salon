import { memo, useMemo } from "react";
import { Card } from "@/components/ui/card";
import { Tooltip } from "@/components/ui/tooltip";
import { Spinner } from "@/components/ui/spinner";
import { TrendingUpIcon, TrendingDownIcon } from "@/components/icons";
import { cn } from "@/lib/utils/cn";

interface MetricCardProps {
  title: string;
  value: string;
  change: number | null;
  icon: React.ComponentType<{ size?: number; className?: string }>;
  loading?: boolean;
  period: "day" | "week" | "month";
  onPeriodChange: (period: "day" | "week" | "month") => void;
}

/**
 * MetricCard component displays a single metric with trend comparison
 * Memoized to prevent unnecessary re-renders
 */
export const MetricCard = memo(function MetricCard({
  title,
  value,
  change,
  icon: Icon,
  loading,
  period,
  onPeriodChange,
}: MetricCardProps) {
  const isPositive = change !== null && change >= 0;
  const hasValidTrend = change !== null;

  const periodLabels = useMemo(
    () => ({
      day: "vs yesterday",
      week: "vs last week",
      month: "vs last month",
    }),
    []
  );

  // Memoize tooltip content generation
  const tooltipContent = useMemo(() => {
    if (loading) return "Loading...";
    if (!hasValidTrend) return "No previous data available for comparison";

    const direction = isPositive ? "increase" : "decrease";
    const periodText =
      period === "day"
        ? "yesterday"
        : period === "week"
        ? "last week"
        : "last month";
    return `${Math.abs(change!).toFixed(
      1
    )}% ${direction} compared to ${periodText}`;
  }, [loading, hasValidTrend, isPositive, change, period]);

  return (
    <Card
      className="p-6 transition-all duration-300 ease-in-out hover:shadow-lg hover:scale-[1.02] animate-in fade-in-0 slide-in-from-bottom-4 will-change-transform"
      role="region"
      aria-label={`${title} metric card`}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center justify-between mb-1">
            <Tooltip
              content={`View ${title.toLowerCase()} trends over different time periods`}
            >
              <p className="text-sm text-muted-foreground cursor-help transition-colors duration-200 hover:text-foreground">
                {title}
              </p>
            </Tooltip>
            <div
              className="flex gap-1"
              role="group"
              aria-label="Period selector"
            >
              <button
                onClick={() => onPeriodChange("day")}
                className={cn(
                  "px-2 py-1 text-xs rounded transition-all duration-300 ease-out cursor-pointer transform will-change-transform",
                  period === "day"
                    ? "bg-primary text-primary-foreground scale-105 shadow-sm"
                    : "bg-muted text-muted-foreground hover:bg-muted/80 hover:scale-105 hover:shadow-sm"
                )}
                aria-label="View daily comparison"
                aria-pressed={period === "day"}
              >
                Day
              </button>
              <button
                onClick={() => onPeriodChange("week")}
                className={cn(
                  "px-2 py-1 text-xs rounded transition-all duration-300 ease-out cursor-pointer transform will-change-transform",
                  period === "week"
                    ? "bg-primary text-primary-foreground scale-105 shadow-sm"
                    : "bg-muted text-muted-foreground hover:bg-muted/80 hover:scale-105 hover:shadow-sm"
                )}
                aria-label="View weekly comparison"
                aria-pressed={period === "week"}
              >
                Week
              </button>
              <button
                onClick={() => onPeriodChange("month")}
                className={cn(
                  "px-2 py-1 text-xs rounded transition-all duration-300 ease-out cursor-pointer transform will-change-transform",
                  period === "month"
                    ? "bg-primary text-primary-foreground scale-105 shadow-sm"
                    : "bg-muted text-muted-foreground hover:bg-muted/80 hover:scale-105 hover:shadow-sm"
                )}
                aria-label="View monthly comparison"
                aria-pressed={period === "month"}
              >
                Month
              </button>
            </div>
          </div>
          {loading ? (
            <div className="h-10 flex items-center">
              <Spinner size="sm" />
            </div>
          ) : (
            <>
              <p className="text-3xl font-bold text-foreground mb-2 transition-all duration-500 ease-out animate-in fade-in-0 zoom-in-95 will-change-transform">
                {value}
              </p>
              <Tooltip content={tooltipContent}>
                <div className="flex items-center gap-1 cursor-help">
                  {hasValidTrend ? (
                    <>
                      {isPositive ? (
                        <TrendingUpIcon
                          size={16}
                          className="text-[var(--success)] animate-in slide-in-from-bottom-2 duration-300 ease-out"
                        />
                      ) : (
                        <TrendingDownIcon
                          size={16}
                          className="text-[var(--error)] animate-in slide-in-from-top-2 duration-300 ease-out"
                        />
                      )}
                      <span
                        className={cn(
                          "text-sm font-medium transition-all duration-300 ease-out",
                          isPositive
                            ? "text-[var(--success)]"
                            : "text-[var(--error)]"
                        )}
                      >
                        {isPositive ? "+" : ""}
                        {change.toFixed(2)}%
                      </span>
                      <span className="text-xs text-muted-foreground ml-1 transition-opacity duration-300 ease-out">
                        {periodLabels[period]}
                      </span>
                    </>
                  ) : (
                    <span className="text-sm text-muted-foreground transition-opacity duration-300 ease-out">
                      N/A
                    </span>
                  )}
                </div>
              </Tooltip>
            </>
          )}
        </div>
        <div
          className="p-3 bg-[var(--primary)]/10 rounded-lg transition-all duration-300 ease-out hover:bg-[var(--primary)]/20 hover:scale-110 hover:rotate-3 transform will-change-transform"
          aria-hidden="true"
        >
          <Icon
            size={24}
            className="text-[var(--primary)] transition-transform duration-300 ease-out"
          />
        </div>
      </div>
    </Card>
  );
});
