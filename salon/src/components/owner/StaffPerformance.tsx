import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { UsersIcon } from "@/components/icons";
import { formatCurrency } from "@/lib/utils/format";
import type { StaffPerformanceData } from "@/hooks/owner";

interface StaffPerformanceProps {
  data?: StaffPerformanceData;
  isLoading?: boolean;
  error?: string;
  onRetry?: () => void;
  onStaffClick?: (staffId: string) => void;
  currency?: string;
}

export function StaffPerformance({
  data,
  isLoading = false,
  error,
  onRetry,
  onStaffClick,
  currency = "USD",
}: StaffPerformanceProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <UsersIcon size={20} />
            Staff Performance
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <Skeleton key={i} className="h-12 w-full" />
          ))}
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="border-destructive/50 bg-destructive/5">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <UsersIcon size={20} />
            Staff Performance
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <p className="text-sm text-destructive font-medium">
            Unable to load staff performance
          </p>
          <p className="text-sm text-muted-foreground">{error}</p>
          {onRetry && (
            <Button
              variant="outline"
              size="sm"
              onClick={onRetry}
              className="w-full"
            >
              Retry
            </Button>
          )}
        </CardContent>
      </Card>
    );
  }

  if (!data || data.topStaff.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <UsersIcon size={20} />
            Staff Performance
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground text-center py-8">
            No staff performance data available
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <UsersIcon size={20} />
          Staff Performance
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Average metrics */}
        <div
          className="grid grid-cols-3 gap-3 p-3 rounded-lg"
          style={{ backgroundColor: "var(--muted)" }}
        >
          <div className="space-y-1">
            <p className="text-xs" style={{ color: "var(--muted-foreground)" }}>
              Avg Utilization
            </p>
            <p
              className="text-lg font-bold"
              style={{ color: "var(--foreground)" }}
            >
              {data.averageUtilization.toFixed(1)}%
            </p>
          </div>
          <div className="space-y-1">
            <p className="text-xs" style={{ color: "var(--muted-foreground)" }}>
              Avg Satisfaction
            </p>
            <p
              className="text-lg font-bold"
              style={{ color: "var(--foreground)" }}
            >
              {data.averageSatisfaction.toFixed(1)}/5
            </p>
          </div>
          <div className="space-y-1">
            <p className="text-xs" style={{ color: "var(--muted-foreground)" }}>
              Avg Attendance
            </p>
            <p
              className="text-lg font-bold"
              style={{ color: "var(--foreground)" }}
            >
              {data.averageAttendance.toFixed(1)}%
            </p>
          </div>
        </div>

        {/* Top staff list */}
        <div className="space-y-2">
          <h4
            className="font-medium text-sm"
            style={{ color: "var(--foreground)" }}
          >
            Top 5 Staff by Revenue
          </h4>
          <div className="space-y-2">
            {data.topStaff.map((staff) => (
              <div
                key={staff.staffId}
                className="p-3 border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer"
                onClick={() => onStaffClick?.(staff.staffId)}
              >
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <p className="font-medium text-sm">{staff.staffName}</p>
                    <p className="text-xs text-muted-foreground">
                      Rank #{staff.revenueRank}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-sm">
                      {formatCurrency(staff.revenue, currency)}
                    </p>
                    <p
                      className="text-xs"
                      style={{
                        color:
                          staff.revenueGrowth >= 0
                            ? "var(--success, #22c55e)"
                            : "var(--destructive)",
                      }}
                    >
                      {staff.revenueGrowth >= 0 ? "+" : ""}
                      {staff.revenueGrowth.toFixed(1)}%
                    </p>
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-2 text-xs">
                  <div>
                    <p style={{ color: "var(--muted-foreground)" }}>
                      Utilization
                    </p>
                    <div
                      className="w-full rounded-full h-1.5 mt-1"
                      style={{ backgroundColor: "var(--muted)" }}
                    >
                      <div
                        className="h-1.5 rounded-full"
                        style={{
                          width: `${staff.utilizationRate}%`,
                          backgroundColor: "var(--primary)",
                        }}
                      />
                    </div>
                    <p
                      className="mt-1"
                      style={{ color: "var(--muted-foreground)" }}
                    >
                      {staff.utilizationRate.toFixed(0)}%
                    </p>
                  </div>
                  <div>
                    <p style={{ color: "var(--muted-foreground)" }}>
                      Satisfaction
                    </p>
                    <p
                      className="font-bold mt-1"
                      style={{ color: "var(--foreground)" }}
                    >
                      {staff.satisfactionScore.toFixed(1)}/5
                    </p>
                  </div>
                  <div>
                    <p style={{ color: "var(--muted-foreground)" }}>
                      Attendance
                    </p>
                    <p
                      className="font-bold mt-1"
                      style={{ color: "var(--foreground)" }}
                    >
                      {staff.attendanceRate.toFixed(0)}%
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <Button variant="outline" className="w-full" size="sm">
          View All Staff
        </Button>
      </CardContent>
    </Card>
  );
}
