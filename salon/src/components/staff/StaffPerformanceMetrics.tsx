import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  RefreshCwIcon,
  StarIcon,
  UsersIcon,
  CalendarIcon,
  TrendingUpIcon,
} from "@/components/icons";

export interface PerformanceMetrics {
  averageRating: number;
  totalReviews: number;
  appointmentsCompleted: number;
  customerSatisfaction: number; // percentage
  totalEarnings?: number;
  topService?: string;
}

interface StaffPerformanceMetricsProps {
  metrics: PerformanceMetrics;
  isLoading?: boolean;
  error?: string;
  onRetry?: () => void;
  onViewDetails?: () => void;
}

export function StaffPerformanceMetrics({
  metrics,
  isLoading = false,
  error,
  onRetry,
  onViewDetails,
}: StaffPerformanceMetricsProps) {
  if (isLoading) {
    return <MetricsSkeleton />;
  }

  if (error) {
    return (
      <Card
        variant="outlined"
        className="border-destructive/50 bg-destructive/5"
      >
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            Performance Metrics
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <p className="text-xs text-destructive font-medium">
            Unable to load metrics
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

  const ratingColor = getRatingColor(metrics.averageRating);
  const satisfactionColor = getSatisfactionColor(metrics.customerSatisfaction);

  return (
    <Card hover>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-semibold">
            Performance Overview
          </CardTitle>
          <div className="flex gap-2">
            {onRetry && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onRetry}
                title="Refresh metrics"
                className="px-2"
              >
                <RefreshCwIcon size={14} />
              </Button>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Rating Section */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <StarIcon size={18} className="text-primary" />
              <h3 className="text-sm font-medium">Average Rating</h3>
            </div>
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1">
                {[1, 2, 3, 4, 5].map((star) => (
                  <StarIcon
                    key={star}
                    size={16}
                    className={
                      star <= Math.round(metrics.averageRating)
                        ? ratingColor
                        : "text-muted-foreground"
                    }
                    fill={
                      star <= Math.round(metrics.averageRating)
                        ? "currentColor"
                        : "none"
                    }
                  />
                ))}
              </div>
              <span className={`text-2xl font-bold ${ratingColor}`}>
                {metrics.averageRating.toFixed(1)}
              </span>
            </div>
          </div>
          <p className="text-sm text-muted-foreground">
            Based on {metrics.totalReviews} review
            {metrics.totalReviews !== 1 ? "s" : ""}
          </p>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-2 gap-4">
          <MetricCard
            icon={<CalendarIcon size={18} className="text-primary" />}
            title="Appointments Completed"
            value={metrics.appointmentsCompleted.toLocaleString()}
            description="Total completed appointments"
          />
          <MetricCard
            icon={<UsersIcon size={18} className="text-primary" />}
            title="Customer Satisfaction"
            value={`${metrics.customerSatisfaction}%`}
            description="Satisfied customers"
            valueColor={satisfactionColor}
          />
        </div>

        {/* Additional Metrics */}
        {(metrics.totalEarnings || metrics.topService) && (
          <div className="pt-4 border-t border-border space-y-3">
            <h3 className="text-sm font-medium">Additional Insights</h3>
            <div className="grid grid-cols-2 gap-4">
              {metrics.totalEarnings && (
                <div className="space-y-1">
                  <p className="text-xs text-muted-foreground">
                    Total Earnings
                  </p>
                  <p className="text-lg font-semibold">
                    $
                    {metrics.totalEarnings.toLocaleString(undefined, {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    })}
                  </p>
                </div>
              )}
              {metrics.topService && (
                <div className="space-y-1">
                  <p className="text-xs text-muted-foreground">Top Service</p>
                  <p className="text-lg font-semibold truncate">
                    {metrics.topService}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="pt-4 border-t border-border">
          <div className="flex gap-2">
            {onViewDetails && (
              <Button
                variant="outline"
                size="sm"
                onClick={onViewDetails}
                className="flex-1"
              >
                View Detailed Report
              </Button>
            )}
            <Button
              variant="ghost"
              size="sm"
              className="px-2"
              title="Performance trending up"
            >
              <TrendingUpIcon size={16} />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function MetricCard({
  icon,
  title,
  value,
  description,
  valueColor = "text-foreground",
}: {
  icon: React.ReactNode;
  title: string;
  value: string;
  description: string;
  valueColor?: string;
}) {
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        {icon}
        <h4 className="text-sm font-medium">{title}</h4>
      </div>
      <p className={`text-2xl font-bold ${valueColor}`}>{value}</p>
      <p className="text-xs text-muted-foreground">{description}</p>
    </div>
  );
}

function MetricsSkeleton() {
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-lg font-semibold">
          Performance Overview
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Rating Section Skeleton */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Skeleton className="h-5 w-32" />
            <Skeleton className="h-8 w-16" />
          </div>
          <Skeleton className="h-4 w-48" />
        </div>

        {/* Metrics Grid Skeleton */}
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Skeleton className="h-5 w-40" />
            <Skeleton className="h-8 w-20" />
            <Skeleton className="h-4 w-32" />
          </div>
          <div className="space-y-2">
            <Skeleton className="h-5 w-40" />
            <Skeleton className="h-8 w-20" />
            <Skeleton className="h-4 w-32" />
          </div>
        </div>

        {/* Action Buttons Skeleton */}
        <div className="pt-4 border-t border-border">
          <Skeleton className="h-9 w-full" />
        </div>
      </CardContent>
    </Card>
  );
}

function getRatingColor(rating: number): string {
  if (rating >= 4.5) return "text-success";
  if (rating >= 4.0) return "text-warning";
  if (rating >= 3.0) return "text-warning";
  if (rating >= 2.0) return "text-destructive/80";
  return "text-destructive";
}

function getSatisfactionColor(satisfaction: number): string {
  if (satisfaction >= 90) return "text-success";
  if (satisfaction >= 80) return "text-warning";
  if (satisfaction >= 70) return "text-warning";
  if (satisfaction >= 60) return "text-destructive/80";
  return "text-destructive";
}
