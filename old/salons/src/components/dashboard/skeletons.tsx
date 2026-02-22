import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils/cn";

export function MetricCardSkeleton() {
  return (
    <Card className="p-6 animate-pulse">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center justify-between mb-1">
            <div className="h-4 w-24 bg-muted rounded" />
            <div className="flex gap-1">
              <div className="h-6 w-12 bg-muted rounded" />
              <div className="h-6 w-12 bg-muted rounded" />
              <div className="h-6 w-14 bg-muted rounded" />
            </div>
          </div>
          <div className="h-10 w-32 bg-muted rounded mb-2 mt-2" />
          <div className="flex items-center gap-1">
            <div className="h-4 w-4 bg-muted rounded" />
            <div className="h-4 w-16 bg-muted rounded" />
            <div className="h-3 w-20 bg-muted rounded ml-1" />
          </div>
        </div>
        <div className="p-3 bg-muted rounded-lg">
          <div className="h-6 w-6 bg-muted-foreground/20 rounded" />
        </div>
      </div>
    </Card>
  );
}

export function ChartSkeleton({ height = 300 }: { height?: number }) {
  return (
    <Card className="p-6 animate-pulse">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="h-6 w-32 bg-muted rounded" />
          <div className="flex gap-2">
            <div className="h-8 w-16 bg-muted rounded" />
            <div className="h-8 w-16 bg-muted rounded" />
            <div className="h-8 w-20 bg-muted rounded" />
          </div>
        </div>
        <div
          className="bg-muted rounded relative overflow-hidden"
          style={{ height: `${height}px` }}
        >
          {/* Animated shimmer effect */}
          <div className="absolute inset-0 -translate-x-full animate-[shimmer_2s_infinite] bg-gradient-to-r from-transparent via-white/10 to-transparent" />
        </div>
      </div>
    </Card>
  );
}

export function WidgetSkeleton({
  rows = 3,
  title = true,
}: {
  rows?: number;
  title?: boolean;
}) {
  return (
    <Card className="p-6 animate-pulse">
      <div className="space-y-4">
        {title && (
          <div className="flex items-center justify-between mb-4">
            <div className="h-6 w-32 bg-muted rounded" />
            <div className="h-8 w-20 bg-muted rounded" />
          </div>
        )}
        <div className="space-y-3">
          {Array.from({ length: rows }).map((_, i) => (
            <div
              key={i}
              className="flex items-center gap-3 p-3 bg-muted/50 rounded-lg"
            >
              <div className="p-2 bg-muted rounded-lg">
                <div className="h-5 w-5 bg-muted-foreground/20 rounded" />
              </div>
              <div className="flex-1 space-y-2">
                <div className="h-4 w-3/4 bg-muted rounded" />
                <div className="h-3 w-1/2 bg-muted rounded" />
              </div>
              <div className="h-6 w-16 bg-muted rounded" />
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
}

export function ActivityFeedSkeleton() {
  return (
    <Card className="p-6 animate-pulse">
      <div className="flex items-center justify-between mb-4">
        <div className="h-6 w-40 bg-muted rounded" />
        <div className="h-8 w-20 bg-muted rounded" />
      </div>
      <div className="space-y-3">
        {Array.from({ length: 5 }).map((_, i) => (
          <div
            key={i}
            className="flex items-start gap-3 p-3 bg-muted/50 rounded-lg"
          >
            <div className="p-2 bg-muted rounded-lg mt-1">
              <div className="h-4 w-4 bg-muted-foreground/20 rounded" />
            </div>
            <div className="flex-1 space-y-2">
              <div className="h-4 w-full bg-muted rounded" />
              <div className="h-3 w-2/3 bg-muted rounded" />
            </div>
            <div className="h-3 w-16 bg-muted rounded mt-1" />
          </div>
        ))}
      </div>
    </Card>
  );
}

export function QuickStatsCardSkeleton() {
  return (
    <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg animate-pulse">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-muted rounded-lg">
          <div className="h-5 w-5 bg-muted-foreground/20 rounded" />
        </div>
        <div className="space-y-2">
          <div className="h-3 w-24 bg-muted rounded" />
          <div className="h-5 w-16 bg-muted rounded" />
        </div>
      </div>
    </div>
  );
}

export function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      {/* Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MetricCardSkeleton />
        <MetricCardSkeleton />
        <MetricCardSkeleton />
      </div>

      {/* Quick Actions */}
      <Card className="p-6 animate-pulse">
        <div className="h-6 w-32 bg-muted rounded mb-4" />
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-24 bg-muted rounded" />
          ))}
        </div>
      </Card>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ActivityFeedSkeleton />
        <WidgetSkeleton rows={3} />
      </div>
    </div>
  );
}
