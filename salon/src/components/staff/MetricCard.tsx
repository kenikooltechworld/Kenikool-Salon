import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { RefreshCwIcon } from "@/components/icons";
import type { ReactNode } from "react";

interface MetricCardProps {
  title: string;
  value: string | number;
  icon?: ReactNode;
  actionLabel?: string;
  onAction?: () => void;
  isLoading?: boolean;
  error?: string;
  onRetry?: () => void;
}

export function MetricCard({
  title,
  value,
  icon,
  actionLabel,
  onAction,
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
        <CardContent>
          <Skeleton className="h-8 w-16" />
          <Skeleton className="h-8 w-full mt-3" />
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

  return (
    <Card hover>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            {title}
          </CardTitle>
          {icon && <div className="text-primary">{icon}</div>}
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <p className="text-3xl font-bold text-foreground">{value}</p>
        <div className="flex gap-2">
          {actionLabel && onAction && (
            <Button
              variant="outline"
              size="sm"
              onClick={onAction}
              className="flex-1"
            >
              {actionLabel}
            </Button>
          )}
          {onRetry && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onRetry}
              title="Refresh this metric"
              className="px-2"
            >
              <RefreshCwIcon size={14} />
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
