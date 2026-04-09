import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { Button } from "@/components/ui/button";
import {
  RefreshCwIcon,
  TrendingUpIcon,
  DollarSignIcon,
  CalendarIcon,
  TargetIcon,
} from "@/components/icons";

interface PerformanceVsTarget {
  target: number;
  actual: number;
  percentage: number;
}

interface TargetProgressProps {
  salesVsTarget?: PerformanceVsTarget;
  commissionVsTarget?: PerformanceVsTarget;
  appointmentsVsTarget?: PerformanceVsTarget;
  isLoading?: boolean;
  error?: string;
  onRetry?: () => void;
}

/**
 * Target progress visualization component
 * Displays performance metrics relative to targets with visual indicators
 *
 * Features:
 * - Sales vs target comparison
 * - Commission vs target comparison
 * - Appointments vs target comparison
 * - Visual progress bars with color coding
 * - Percentage completion indicators
 * - Responsive grid layout
 *
 * Requirements: 17.3, 17.6
 */
export function TargetProgress({
  salesVsTarget,
  commissionVsTarget,
  appointmentsVsTarget,
  isLoading = false,
  error,
  onRetry,
}: TargetProgressProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUpIcon size={20} />
            Performance vs Targets
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
          <CardTitle className="flex items-center gap-2">
            <TrendingUpIcon size={20} />
            Performance vs Targets
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <p className="text-sm text-destructive font-medium">
            Unable to load performance data
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

  const renderProgressCard = (
    title: string,
    icon: React.ReactNode,
    data: PerformanceVsTarget | undefined,
    formatValue: (value: number) => string,
  ) => {
    if (!data) {
      return (
        <div className="p-4 border rounded-lg bg-muted/30">
          <div className="flex items-center gap-2 mb-3">
            {icon}
            <h4 className="font-medium text-foreground">{title}</h4>
          </div>
          <p className="text-sm text-muted-foreground">No target set</p>
        </div>
      );
    }

    const { target, actual, percentage } = data;
    const isOnTrack = percentage >= 75; // Consider on track if >= 75%
    const isCompleted = percentage >= 100;

    return (
      <div className="p-4 border rounded-lg space-y-3 hover:bg-muted/50 transition-colors">
        {/* Header */}
        <div className="flex items-center gap-2">
          {icon}
          <h4 className="font-medium text-foreground">{title}</h4>
        </div>

        {/* Progress Bar */}
        <div className="space-y-1">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Progress</span>
            <span className="font-bold">{percentage.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-muted rounded-full h-3 overflow-hidden">
            <div
              className={`h-full transition-all ${
                isCompleted
                  ? "bg-success"
                  : isOnTrack
                    ? "bg-primary"
                    : "bg-warning"
              }`}
              style={{ width: `${Math.min(percentage, 100)}%` }}
            />
          </div>
        </div>

        {/* Values */}
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="space-y-1">
            <p className="text-muted-foreground">Target</p>
            <p className="font-medium">{formatValue(target)}</p>
          </div>
          <div className="space-y-1">
            <p className="text-muted-foreground">Actual</p>
            <p className="font-medium">{formatValue(actual)}</p>
          </div>
        </div>

        {/* Status Message */}
        <div className="pt-2 border-t">
          {isCompleted ? (
            <p className="text-xs text-success font-medium">
              🎉 Target achieved! Great work!
            </p>
          ) : isOnTrack ? (
            <p className="text-xs text-primary font-medium">
              ✓ On track to meet target
            </p>
          ) : (
            <p className="text-xs text-warning font-medium">
              ⚠ Behind target - keep pushing!
            </p>
          )}
        </div>
      </div>
    );
  };

  const formatCurrency = (value: number) =>
    `₦${value.toLocaleString("en-NG", { maximumFractionDigits: 2 })}`;

  const formatNumber = (value: number) => value.toString();

  const hasAnyData =
    salesVsTarget || commissionVsTarget || appointmentsVsTarget;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <TrendingUpIcon size={20} />
            Performance vs Targets
          </CardTitle>
          {onRetry && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onRetry}
              title="Refresh performance data"
              className="px-2"
            >
              <RefreshCwIcon size={14} />
            </Button>
          )}
        </div>
        <p className="text-sm text-muted-foreground mt-1">
          Track your progress toward monthly targets
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        {!hasAnyData ? (
          <div className="text-center py-8">
            <TargetIcon
              size={48}
              className="mx-auto text-muted-foreground mb-3"
            />
            <p className="text-muted-foreground">
              No performance targets available. Targets will appear here once
              set by management.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Sales Target */}
            {renderProgressCard(
              "Sales Target",
              <DollarSignIcon size={16} className="text-primary" />,
              salesVsTarget,
              formatCurrency,
            )}

            {/* Commission Target */}
            {renderProgressCard(
              "Commission Target",
              <TrendingUpIcon size={16} className="text-primary" />,
              commissionVsTarget,
              formatCurrency,
            )}

            {/* Appointments Target */}
            {renderProgressCard(
              "Appointments Target",
              <CalendarIcon size={16} className="text-primary" />,
              appointmentsVsTarget,
              formatNumber,
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
