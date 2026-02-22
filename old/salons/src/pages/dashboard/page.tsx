import { useCallback, lazy, Suspense, useState, useEffect } from "react";
import { Alert } from "@/components/ui/alert";
import { AlertTriangleIcon } from "@/components/icons";
import { DashboardMetrics } from "@/components/dashboard/dashboard-metrics";
import { QuickActions } from "@/components/dashboard/quick-actions";
import { useDashboardOverview } from "@/lib/api/hooks/useAnalytics-offline";
import { apiClient } from "@/lib/api/client";
import {
  useActivityFeed,
  useDashboardAlerts,
  useUpcomingEvents,
  useExpenseSummary,
  useWaitlistSummary,
  useQuickStats,
} from "@/lib/api/hooks/useAnalytics-offline";
import { Select } from "@/components/ui/select";
import { Card } from "@/components/ui/card";
import { ErrorBoundary } from "@/components/ui/error-boundary";

// Lazy load heavy components for better initial load performance
const RevenueChart = lazy(() =>
  import("@/components/dashboard/revenue-chart").then((mod) => ({
    default: mod.RevenueChart,
  })),
);
const TopServicesWidget = lazy(() =>
  import("@/components/dashboard/top-services-widget").then((mod) => ({
    default: mod.TopServicesWidget,
  })),
);
const StaffPerformanceWidget = lazy(() =>
  import("@/components/dashboard/staff-performance-widget").then((mod) => ({
    default: mod.StaffPerformanceWidget,
  })),
);
const ActivityFeed = lazy(() =>
  import("@/components/dashboard/activity-feed").then((mod) => ({
    default: mod.ActivityFeed,
  })),
);
const AlertsWidget = lazy(() =>
  import("@/components/dashboard/alerts-widget").then((mod) => ({
    default: mod.AlertsWidget,
  })),
);
const UpcomingEventsWidget = lazy(() =>
  import("@/components/dashboard/upcoming-events-widget").then((mod) => ({
    default: mod.UpcomingEventsWidget,
  })),
);
const ExpenseSummaryWidget = lazy(() =>
  import("@/components/dashboard/expense-summary-widget").then((mod) => ({
    default: mod.ExpenseSummaryWidget,
  })),
);
const WaitlistSummaryWidget = lazy(() =>
  import("@/components/dashboard/waitlist-summary-widget").then((mod) => ({
    default: mod.WaitlistSummaryWidget,
  })),
);
const QuickStatsWidget = lazy(() =>
  import("@/components/dashboard/quick-stats-widget").then((mod) => ({
    default: mod.QuickStatsWidget,
  })),
);

// Loading fallback component
function WidgetSkeleton() {
  return (
    <div className="animate-pulse">
      <div className="h-64 bg-muted rounded-lg"></div>
    </div>
  );
}

// Memoize navigation handlers
const useNavigationHandlers = () => {
  const handleServiceClick = useCallback((serviceId: string) => {
    window.location.href = `/dashboard/services?id=${serviceId}`;
  }, []);

  const handleStaffClick = useCallback((staffId: string) => {
    window.location.href = `/dashboard/staff?id=${staffId}`;
  }, []);

  const handleDateClick = useCallback((date: string) => {
    window.location.href = `/dashboard/bookings?date=${date}`;
  }, []);

  const handleAlertDismiss = useCallback((alertId: string) => {
    console.log("Alert dismissed:", alertId);
    // TODO: Implement alert dismissal API call
  }, []);

  return {
    handleServiceClick,
    handleStaffClick,
    handleDateClick,
    handleAlertDismiss,
  };
};

export default function DashboardPage() {
  const [selectedLocation, setSelectedLocation] = useState("all");
  const [locations, setLocations] = useState([]);
  const [locationsLoading, setLocationsLoading] = useState(true);

  // Fetch locations on mount
  useEffect(() => {
    fetchLocations();
  }, []);

  const fetchLocations = async () => {
    try {
      setLocationsLoading(true);
      const response = await apiClient.get("/api/locations");
      setLocations(response.data.locations || []);
    } catch (error) {
      console.error("Error fetching locations:", error);
    } finally {
      setLocationsLoading(false);
    }
  };

  const {
    data: overviewData,
    isLoading: overviewLoading,
    error: overviewError,
  } = useDashboardOverview({
    period: "month",
    location_id: selectedLocation !== "all" ? selectedLocation : undefined,
  });

  const {
    data: activityFeedData,
    isLoading: activityFeedLoading,
    refetch: refetchActivityFeed,
  } = useActivityFeed({
    limit: 10,
    location_id: selectedLocation !== "all" ? selectedLocation : undefined,
  });
  const { data: alertsData, isLoading: alertsLoading } = useDashboardAlerts();
  const { data: upcomingEventsData, isLoading: upcomingEventsLoading } =
    useUpcomingEvents({
      days: 7,
      location_id: selectedLocation !== "all" ? selectedLocation : undefined,
    });
  const { data: expenseSummaryData, isLoading: expenseSummaryLoading } =
    useExpenseSummary({
      period: "month",
      location_id: selectedLocation !== "all" ? selectedLocation : undefined,
    });
  const { data: waitlistSummaryData, isLoading: waitlistSummaryLoading } =
    useWaitlistSummary({
      location_id: selectedLocation !== "all" ? selectedLocation : undefined,
    });
  const { data: quickStatsData, isLoading: quickStatsLoading } = useQuickStats({
    period: "month",
    location_id: selectedLocation !== "all" ? selectedLocation : undefined,
  });

  const {
    handleServiceClick,
    handleStaffClick,
    handleDateClick,
    handleAlertDismiss,
  } = useNavigationHandlers();

  const showErrorAlert = overviewError && overviewData;

  if (overviewError && !overviewData) {
    return (
      <div className="space-y-6">
        <Alert variant="error">
          <AlertTriangleIcon size={20} />
          <div>
            <h3 className="font-semibold">Error loading dashboard</h3>
            <p className="text-sm">
              {overviewError?.message || "An error occurred"}
            </p>
          </div>
        </Alert>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Location Filter */}
      <Card className="p-4">
        <div className="flex items-center gap-4">
          <label htmlFor="location-select" className="text-sm font-medium">
            Filter by Location:
          </label>
          <Select
            id="location-select"
            value={selectedLocation}
            onValueChange={setSelectedLocation}
            className="w-64"
          >
            <option value="all">All Locations</option>
            {locations.map((location) => (
              <option key={location._id} value={location._id}>
                {location.name}
              </option>
            ))}
          </Select>
          {selectedLocation !== "all" && (
            <span className="text-sm text-muted-foreground">
              Showing metrics for selected location
            </span>
          )}
        </div>
      </Card>

      {showErrorAlert && (
        <Alert variant="warning">
          <AlertTriangleIcon size={20} />
          <div>
            <h3 className="font-semibold">Using cached data</h3>
            <p className="text-sm">
              Unable to fetch latest data. Showing cached information.
            </p>
          </div>
        </Alert>
      )}
      <DashboardMetrics />

      {/* Quick Actions - Now using extracted component */}
      <QuickActions />

      {/* Revenue Chart - Using data from overview endpoint */}
      <Suspense fallback={<WidgetSkeleton />}>
        <RevenueChart
          data={overviewData?.revenue_chart || []}
          loading={overviewLoading}
          period="month"
        />
      </Suspense>

      {/* Top Services and Staff Performance - Using data from overview endpoint */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Suspense fallback={<WidgetSkeleton />}>
          <TopServicesWidget
            services={overviewData?.top_services || []}
            loading={overviewLoading}
            onServiceClick={handleServiceClick}
          />
        </Suspense>
        <Suspense fallback={<WidgetSkeleton />}>
          <StaffPerformanceWidget
            staff={overviewData?.staff_performance || []}
            loading={overviewLoading}
            onStaffClick={handleStaffClick}
          />
        </Suspense>
      </div>

      {/* Activity Feed and Alerts - Lazy loaded */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Suspense fallback={<WidgetSkeleton />}>
          <ActivityFeed
            activities={activityFeedData?.activities || []}
            loading={activityFeedLoading}
            autoRefresh={true}
            onRefresh={refetchActivityFeed}
          />
        </Suspense>
        <Suspense fallback={<WidgetSkeleton />}>
          <AlertsWidget
            alerts={alertsData?.alerts || []}
            loading={alertsLoading}
            onDismiss={handleAlertDismiss}
          />
        </Suspense>
      </div>

      {/* Upcoming Events and Expense Summary - Lazy loaded */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Suspense fallback={<WidgetSkeleton />}>
          <UpcomingEventsWidget
            events={upcomingEventsData?.events || []}
            loading={upcomingEventsLoading}
            onDateClick={handleDateClick}
          />
        </Suspense>
        <Suspense fallback={<WidgetSkeleton />}>
          <ExpenseSummaryWidget
            totalExpenses={expenseSummaryData?.total_expenses || 0}
            expenseTrend={expenseSummaryData?.expense_trend || 0}
            breakdown={expenseSummaryData?.breakdown || []}
            profitMargin={expenseSummaryData?.profit_margin || 0}
            loading={expenseSummaryLoading}
          />
        </Suspense>
      </div>

      {/* Waitlist Summary and Quick Stats - Lazy loaded */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Suspense fallback={<WidgetSkeleton />}>
          <WaitlistSummaryWidget
            totalCount={waitlistSummaryData?.total_count || 0}
            byService={waitlistSummaryData?.by_service || []}
            urgentCount={waitlistSummaryData?.urgent_count || 0}
            loading={waitlistSummaryLoading}
          />
        </Suspense>
        <ErrorBoundary>
          <Suspense fallback={<WidgetSkeleton />}>
            <QuickStatsWidget
              stats={quickStatsData}
              loading={quickStatsLoading}
            />
          </Suspense>
        </ErrorBoundary>
      </div>
    </div>
  );
}
