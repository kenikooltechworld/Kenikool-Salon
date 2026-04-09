import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  RefreshCwIcon,
  TrendingUpIcon,
  TrendingDownIcon,
} from "@/components/icons";
import type { ReactNode } from "react";

interface MetricCardProps {
  title: string;
  value: string | number;
  unit?: string;
  trend?: "up" | "down" | "neutral";
  trendPercentage?: number;
  comparison?: string;
  icon?: ReactNode;
  onClick?: () => void;
  isLoading?: boolean;
  error?: string;
  onRetry?: () => void;
}

export function MetricCard({
  title,
  value,
  unit = "",
  trend,
  trendPercentage,
  comparison,
  icon,
  onClick,
  isLoading = false,
  error,
  onRetry,
}: MetricCardProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            {title}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <Skeleton className="h-8 w-24" />
          <Skeleton className="h-4 w-32" />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="border-destructive/50 bg-destructive/5">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            {title}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <p className="text-xs text-destructive font-medium">
            Unable to load metric
          </p>
          <p className="text-xs text-muted-foreground">
            {error || "Network error. Please try again."}
          </p>
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

  const getTrendColor = () => {
    if (trend === "up") return "var(--success, #22c55e)";
    if (trend === "down") return "var(--destructive)";
    return "var(--muted-foreground)";
  };

  const getTrendIcon = () => {
    if (trend === "up") return <TrendingUpIcon size={16} />;
    if (trend === "down") return <TrendingDownIcon size={16} />;
    return null;
  };

  return (
    <Card
      className={
        onClick ? "cursor-pointer hover:shadow-md transition-shadow" : ""
      }
      onClick={onClick}
    >
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            {title}
          </CardTitle>
          {icon && <div className="text-primary">{icon}</div>}
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-baseline gap-1">
          <p className="text-3xl font-bold text-foreground">{value}</p>
          {unit && (
            <span className="text-sm text-muted-foreground">{unit}</span>
          )}
        </div>

        {(trend || comparison) && (
          <div className="space-y-1">
            {trend && trendPercentage !== undefined && (
              <div
                className="flex items-center gap-1 text-sm font-medium"
                style={{ color: getTrendColor() }}
              >
                {getTrendIcon()}
                <span>{Math.abs(trendPercentage)}%</span>
              </div>
            )}
            {comparison && (
              <p className="text-xs text-muted-foreground">{comparison}</p>
            )}
          </div>
        )}

        {onRetry && (
          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              onRetry();
            }}
            title="Refresh this metric"
            className="px-2"
          >
            <RefreshCwIcon size={14} />
          </Button>
        )}
      </CardContent>
    </Card>
  );
}
