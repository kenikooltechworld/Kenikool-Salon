import { useAuthStore } from "@/stores/auth";
import { useStaffMetrics } from "@/hooks/useStaffMetrics";
import { useActivityFeed } from "@/hooks/useActivityFeed";
import { MetricCard } from "@/components/staff/MetricCard";
import { ActivityFeed } from "@/components/staff/ActivityFeed";
import { NetworkStatus } from "@/components/staff/NetworkStatus";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/toast";
import { useNavigate } from "react-router-dom";
import { useEffect } from "react";
import {
  CalendarIcon,
  ClockIcon,
  DollarIcon,
  BriefcaseIcon,
} from "@/components/icons";

export default function StaffDashboard() {
  const user = useAuthStore((state) => state.user);
  const navigate = useNavigate();
  const { showToast } = useToast();

  const {
    data: metrics,
    isLoading: metricsLoading,
    error: metricsError,
    refetch: refetchMetrics,
  } = useStaffMetrics();

  const {
    data: activities = [],
    isLoading: activitiesLoading,
    error: activitiesError,
    refetch: refetchActivities,
  } = useActivityFeed(10);

  // Show error toast when metrics fail to load
  useEffect(() => {
    if (metricsError) {
      showToast({
        variant: "error",
        title: "Failed to load metrics",
        description:
          "Unable to fetch dashboard metrics. Please check your connection and try again.",
      });
    }
  }, [metricsError, showToast]);

  // Show error toast when activities fail to load
  useEffect(() => {
    if (activitiesError) {
      showToast({
        variant: "error",
        title: "Failed to load activity",
        description:
          "Unable to fetch recent activity. Please check your connection and try again.",
      });
    }
  }, [activitiesError, showToast]);

  const handleRefreshAll = () => {
    refetchMetrics();
    refetchActivities();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">
            Welcome, {user?.firstName}!
          </h1>
          <p className="text-muted-foreground mt-2">
            Here's your staff dashboard overview
          </p>
        </div>
        <div className="flex items-center gap-3">
          <NetworkStatus />
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefreshAll}
            disabled={metricsLoading || activitiesLoading}
          >
            Refresh
          </Button>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Today's Appointments"
          value={metrics?.todayAppointments ?? 0}
          icon={<CalendarIcon size={20} />}
          actionLabel="View"
          onAction={() => navigate("/staff/appointments")}
          isLoading={metricsLoading}
          error={metricsError ? "Failed to load" : undefined}
          onRetry={refetchMetrics}
        />
        <MetricCard
          title="Upcoming Shifts"
          value={metrics?.upcomingShifts ?? 0}
          icon={<ClockIcon size={20} />}
          actionLabel="View"
          onAction={() => navigate("/staff/shifts")}
          isLoading={metricsLoading}
          error={metricsError ? "Failed to load" : undefined}
          onRetry={refetchMetrics}
        />
        <MetricCard
          title="Pending Time Off"
          value={metrics?.pendingTimeOff ?? 0}
          icon={<BriefcaseIcon size={20} />}
          actionLabel="Request"
          onAction={() => navigate("/staff/time-off")}
          isLoading={metricsLoading}
          error={metricsError ? "Failed to load" : undefined}
          onRetry={refetchMetrics}
        />
        <MetricCard
          title="Earnings Summary"
          value={`$${(metrics?.earningsSummary?.total ?? 0).toFixed(2)}`}
          icon={<DollarIcon size={20} />}
          actionLabel="Details"
          onAction={() => navigate("/staff/earnings")}
          isLoading={metricsLoading}
          error={metricsError ? "Failed to load" : undefined}
          onRetry={refetchMetrics}
        />
      </div>

      {/* Activity Feed */}
      <ActivityFeed
        events={activities}
        isLoading={activitiesLoading}
        error={activitiesError ? "Failed to load activity" : undefined}
        onRetry={refetchActivities}
      />
    </div>
  );
}
