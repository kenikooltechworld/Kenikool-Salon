import { useState } from "react";
import {
  useOwnerMetrics,
  useUpcomingAppointments,
  usePendingActions,
  useRevenueAnalytics,
  useStaffPerformance,
} from "@/hooks/owner";
import { useTenantSettings } from "@/hooks/owner/useTenantSettings";
import { useWebSocket } from "@/hooks/useWebSocket";
import { DashboardHeader } from "@/components/owner/DashboardHeader";
import { MetricCard } from "@/components/owner/MetricCard";
import { UpcomingAppointments } from "@/components/owner/UpcomingAppointments";
import { PendingActions } from "@/components/owner/PendingActions";
import { RevenueChart } from "@/components/owner/RevenueChart";
import { StaffPerformance } from "@/components/owner/StaffPerformance";
import { formatCurrency } from "@/lib/utils/format";
import {
  DollarSignIcon,
  CalendarIcon,
  StarIcon,
  TrendingUpIcon,
  AlertCircleIcon,
  BoxIcon,
} from "@/components/icons";

export default function Dashboard() {
  const [revenuePeriod, setRevenuePeriod] = useState<
    "daily" | "weekly" | "monthly"
  >("daily");

  // Fetch tenant settings for currency
  const { data: tenantSettings } = useTenantSettings();
  const currency = tenantSettings?.currency || "USD";

  // Establish WebSocket connection for real-time updates
  useWebSocket({
    onConnect: () => {
      console.log("Dashboard WebSocket connected");
    },
    onDisconnect: () => {
      console.log("Dashboard WebSocket disconnected");
    },
    onError: (error) => {
      console.error("Dashboard WebSocket error:", error);
    },
  });

  // Fetch all dashboard data in parallel (React Query handles this automatically)
  const metricsQuery = useOwnerMetrics();
  const appointmentsQuery = useUpcomingAppointments(10);
  const actionsQuery = usePendingActions();
  const revenueQuery = useRevenueAnalytics(revenuePeriod, 30);
  const staffQuery = useStaffPerformance();

  // Handle metric card clicks for drill-down
  const handleMetricClick = (metricType: string) => {
    console.log(`Clicked metric: ${metricType}`);
    // Navigate to detailed view
  };

  return (
    <div className="space-y-6 pb-8">
      {/* Header - Always show */}
      <DashboardHeader />

      {/* Metric Cards Grid - Show loading state per card */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <MetricCard
          title="Total Revenue"
          value={formatCurrency(
            metricsQuery.data?.revenue.current || 0,
            currency,
          )}
          trend={metricsQuery.data?.revenue.trend}
          trendPercentage={metricsQuery.data?.revenue.trendPercentage}
          comparison={`vs ${formatCurrency(metricsQuery.data?.revenue.previous || 0, currency)} last month`}
          icon={<DollarSignIcon size={20} />}
          isLoading={metricsQuery.isLoading}
          error={metricsQuery.error?.message}
          onRetry={() => metricsQuery.refetch()}
          onClick={() => handleMetricClick("revenue")}
        />

        <MetricCard
          title="Total Appointments"
          value={metricsQuery.data?.appointments.thisMonth || 0}
          trend={metricsQuery.data?.appointments.trend}
          comparison={`${metricsQuery.data?.appointments.today || 0} today, ${metricsQuery.data?.appointments.thisWeek || 0} this week`}
          icon={<CalendarIcon size={20} />}
          isLoading={metricsQuery.isLoading}
          error={metricsQuery.error?.message}
          onRetry={() => metricsQuery.refetch()}
          onClick={() => handleMetricClick("appointments")}
        />

        <MetricCard
          title="Customer Satisfaction"
          value={metricsQuery.data?.satisfaction.score || 0}
          unit="/5"
          trend={metricsQuery.data?.satisfaction.trend}
          comparison={`Based on ${metricsQuery.data?.satisfaction.count || 0} reviews`}
          icon={<StarIcon size={20} />}
          isLoading={metricsQuery.isLoading}
          error={metricsQuery.error?.message}
          onRetry={() => metricsQuery.refetch()}
          onClick={() => handleMetricClick("satisfaction")}
        />

        <MetricCard
          title="Staff Utilization"
          value={metricsQuery.data?.staffUtilization.percentage || 0}
          unit="%"
          comparison={`${metricsQuery.data?.staffUtilization.bookedHours || 0} of ${metricsQuery.data?.staffUtilization.availableHours || 0} hours booked`}
          icon={<TrendingUpIcon size={20} />}
          isLoading={metricsQuery.isLoading}
          error={metricsQuery.error?.message}
          onRetry={() => metricsQuery.refetch()}
          onClick={() => handleMetricClick("utilization")}
        />

        <MetricCard
          title="Pending Payments"
          value={metricsQuery.data?.pendingPayments.count || 0}
          comparison={`${formatCurrency(metricsQuery.data?.pendingPayments.totalAmount || 0, currency)} total`}
          icon={<AlertCircleIcon size={20} />}
          isLoading={metricsQuery.isLoading}
          error={metricsQuery.error?.message}
          onRetry={() => metricsQuery.refetch()}
          onClick={() => handleMetricClick("payments")}
        />

        <MetricCard
          title="Low Stock Items"
          value={metricsQuery.data?.inventoryStatus.lowStockCount || 0}
          comparison={`${metricsQuery.data?.inventoryStatus.expiringCount || 0} expiring soon`}
          icon={<BoxIcon size={20} />}
          isLoading={metricsQuery.isLoading}
          error={metricsQuery.error?.message}
          onRetry={() => metricsQuery.refetch()}
          onClick={() => handleMetricClick("inventory")}
        />
      </div>

      {/* Upcoming Appointments */}
      <UpcomingAppointments
        appointments={appointmentsQuery.data || []}
        isLoading={appointmentsQuery.isLoading}
        error={appointmentsQuery.error?.message}
        onRetry={() => appointmentsQuery.refetch()}
      />

      {/* Pending Actions */}
      <PendingActions
        actions={Array.isArray(actionsQuery.data) ? actionsQuery.data : []}
        isLoading={actionsQuery.isLoading}
        error={actionsQuery.error?.message}
        onMarkComplete={actionsQuery.markComplete}
        onDismiss={actionsQuery.dismiss}
        isMarkingComplete={actionsQuery.isMarkingComplete}
        isDismissing={actionsQuery.isDismissing}
      />

      {/* Analytics Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RevenueChart
          data={revenueQuery.data}
          isLoading={revenueQuery.isLoading}
          error={revenueQuery.error?.message}
          onRetry={() => revenueQuery.refetch()}
          onPeriodChange={(period) => setRevenuePeriod(period)}
          currency={currency}
        />

        <StaffPerformance
          data={staffQuery.data}
          isLoading={staffQuery.isLoading}
          error={staffQuery.error?.message}
          onRetry={() => staffQuery.refetch()}
          currency={currency}
        />
      </div>
    </div>
  );
}
