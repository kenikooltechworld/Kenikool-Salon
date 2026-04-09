import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { RefreshCwIcon } from "@/components/icons";
import { formatDate, formatTime } from "@/lib/utils/format";
import type { ActivityEvent } from "@/hooks/useActivityFeed";
import type { BadgeProps } from "@/components/ui/badge";

interface ActivityFeedProps {
  events: ActivityEvent[];
  isLoading?: boolean;
  error?: string;
  onRetry?: () => void;
}

const typeVariants: Record<
  ActivityEvent["type"],
  NonNullable<BadgeProps["variant"]>
> = {
  appointment: "default",
  shift: "secondary",
  timeoff: "accent",
  earnings: "default",
  review: "secondary",
};

const typeLabels: Record<ActivityEvent["type"], string> = {
  appointment: "Appointment",
  shift: "Shift",
  timeoff: "Time Off",
  earnings: "Earnings",
  review: "Review",
};

export function ActivityFeed({
  events,
  isLoading = false,
  error,
  onRetry,
}: ActivityFeedProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="space-y-2">
              <Skeleton className="h-4 w-32" />
              <Skeleton className="h-3 w-48" />
            </div>
          ))}
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
        <CardHeader className="flex flex-row items-center justify-between space-y-0">
          <CardTitle>Recent Activity</CardTitle>
          {onRetry && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onRetry}
              title="Refresh activity feed"
            >
              <RefreshCwIcon size={16} />
            </Button>
          )}
        </CardHeader>
        <CardContent className="space-y-2">
          <p className="text-sm text-destructive font-medium">
            Unable to load activity
          </p>
          <p className="text-sm text-muted-foreground">
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

  if (events.length === 0) {
    return (
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0">
          <CardTitle>Recent Activity</CardTitle>
          {onRetry && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onRetry}
              title="Refresh activity feed"
            >
              <RefreshCwIcon size={16} />
            </Button>
          )}
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">No recent activity</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0">
        <CardTitle>Recent Activity</CardTitle>
        {onRetry && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onRetry}
            title="Refresh activity feed"
          >
            <RefreshCwIcon size={16} />
          </Button>
        )}
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {events.map((event) => (
            <div
              key={event.id}
              className="flex items-start gap-3 pb-3 border-b border-border last:border-0 last:pb-0"
            >
              <Badge variant={typeVariants[event.type]} className="shrink-0">
                {typeLabels[event.type]}
              </Badge>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-sm text-foreground">
                  {event.title}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  {event.description}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  {formatDate(new Date(event.timestamp))}{" "}
                  {formatTime(new Date(event.timestamp))}
                </p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
