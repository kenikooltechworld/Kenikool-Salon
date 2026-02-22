"use client";

import { useGetUsageStats } from "@/lib/api/hooks/useUsage";
import { ChartIcon, AlertTriangleIcon } from "@/components/icons";
import { Card } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { Badge } from "@/components/ui/badge";

export function UsageDashboard() {
  const { data: usage, isLoading } = useGetUsageStats();

  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center py-8">
          <Spinner size="lg" />
        </div>
      </Card>
    );
  }

  if (!usage) {
    return (
      <Card className="p-6">
        <div className="text-center py-8">
          <ChartIcon
            size={48}
            className="mx-auto text-[var(--muted-foreground)] mb-4"
          />
          <p className="text-[var(--muted-foreground)]">
            No usage data available
          </p>
        </div>
      </Card>
    );
  }

  const resources = [
    {
      name: "Bookings",
      ...usage.bookings,
      color: "var(--primary)",
      warningThreshold: 80,
    },
    {
      name: "Staff Members",
      ...usage.staff,
      color: "var(--info)",
      warningThreshold: 80,
    },
    {
      name: "SMS Messages",
      ...usage.sms,
      color: "var(--success)",
      warningThreshold: 80,
    },
    {
      name: "API Calls",
      ...usage.api_calls,
      color: "var(--warning)",
      warningThreshold: 80,
    },
  ];

  return (
    <Card className="p-6">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold">Usage This Month</h3>
            <p className="text-sm text-[var(--muted-foreground)]">
              {usage.month}
            </p>
          </div>
          <ChartIcon size={24} className="text-[var(--primary)]" />
        </div>

        <div className="space-y-4">
          {resources.map((resource) => {
            const isNearLimit =
              !resource.unlimited &&
              resource.limit &&
              resource.percentage >= resource.warningThreshold;
            const isOverLimit =
              !resource.unlimited &&
              resource.limit &&
              resource.used >= resource.limit;

            return (
              <div key={resource.name} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{resource.name}</span>
                    {resource.unlimited ? (
                      <Badge variant="success">Unlimited</Badge>
                    ) : isOverLimit ? (
                      <Badge variant="error">
                        <AlertTriangleIcon size={12} className="mr-1" />
                        Limit Reached
                      </Badge>
                    ) : isNearLimit ? (
                      <Badge variant="warning">
                        <AlertTriangleIcon size={12} className="mr-1" />
                        Near Limit
                      </Badge>
                    ) : null}
                  </div>
                  <span className="text-sm text-[var(--muted-foreground)]">
                    {resource.used}
                    {resource.limit !== null && ` / ${resource.limit}`}
                    {resource.unlimited && " (Unlimited)"}
                  </span>
                </div>

                {!resource.unlimited && resource.limit && (
                  <div className="w-full bg-[var(--muted)] rounded-full h-2 overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-300"
                      style={{
                        width: `${Math.min(resource.percentage, 100)}%`,
                        backgroundColor: isOverLimit
                          ? "var(--error)"
                          : isNearLimit
                          ? "var(--warning)"
                          : resource.color,
                      }}
                    />
                  </div>
                )}

                {isOverLimit && (
                  <p className="text-xs text-[var(--error)]">
                    You've reached your {resource.name.toLowerCase()} limit.
                    Upgrade your plan to continue.
                  </p>
                )}
                {isNearLimit && !isOverLimit && (
                  <p className="text-xs text-[var(--warning)]">
                    You're approaching your {resource.name.toLowerCase()} limit
                    ({resource.percentage.toFixed(0)}% used).
                  </p>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </Card>
  );
}
