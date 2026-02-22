import { memo, useState, useCallback } from "react";
import { MetricCard } from "./metric-card";
import { DollarIcon, CalendarIcon, UsersIcon } from "@/components/icons";
import { useDashboardMetrics } from "@/lib/api/hooks/useAnalytics-offline";
import { useDashboardPrefetch } from "@/lib/api/hooks/useDashboardPrefetch";

type Period = "day" | "week" | "month";

/**
 * Dashboard Metrics Component
 *
 * Optimized to reduce API calls:
 * - Uses prefetching to load data before user interaction
 * - Shares data when periods are the same (React Query deduplication)
 * - Shows cached data instantly while fetching in background
 */
export const DashboardMetrics = memo(function DashboardMetrics() {
  const [revenuePeriod, setRevenuePeriod] = useState<Period>("month");
  const [bookingsPeriod, setBookingsPeriod] = useState<Period>("month");
  const [clientsPeriod, setClientsPeriod] = useState<Period>("month");

  // Get prefetch function for period changes
  const { prefetchMetrics } = useDashboardPrefetch({ immediate: false });

  // Fetch metrics for each card
  // React Query automatically deduplicates requests with the same query key
  // So if all periods are "month", only ONE API call is made
  const { data: revenueData, isLoading: revenueLoading } = useDashboardMetrics({
    period: revenuePeriod,
  });
  const { data: bookingsData, isLoading: bookingsLoading } =
    useDashboardMetrics({
      period: bookingsPeriod,
    });
  const { data: clientsData, isLoading: clientsLoading } = useDashboardMetrics({
    period: clientsPeriod,
  });

  // Period change handlers with prefetching
  const handleRevenuePeriodChange = useCallback(
    (period: Period) => {
      // Prefetch data for the new period before setting state
      prefetchMetrics(period);
      setRevenuePeriod(period);
    },
    [prefetchMetrics],
  );

  const handleBookingsPeriodChange = useCallback(
    (period: Period) => {
      prefetchMetrics(period);
      setBookingsPeriod(period);
    },
    [prefetchMetrics],
  );

  const handleClientsPeriodChange = useCallback(
    (period: Period) => {
      prefetchMetrics(period);
      setClientsPeriod(period);
    },
    [prefetchMetrics],
  );

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <MetricCard
        title="Revenue"
        value={
          revenueData?.total_revenue
            ? `₦${revenueData.total_revenue.toLocaleString()}`
            : "₦0"
        }
        change={revenueData?.revenue_trend ?? null}
        icon={DollarIcon}
        loading={revenueLoading}
        period={revenuePeriod}
        onPeriodChange={handleRevenuePeriodChange}
      />
      <MetricCard
        title="Bookings"
        value={bookingsData?.total_bookings?.toString() || "0"}
        change={bookingsData?.booking_trend ?? null}
        icon={CalendarIcon}
        loading={bookingsLoading}
        period={bookingsPeriod}
        onPeriodChange={handleBookingsPeriodChange}
      />
      <MetricCard
        title="Clients"
        value={clientsData?.total_clients?.toString() || "0"}
        change={clientsData?.client_trend ?? null}
        icon={UsersIcon}
        loading={clientsLoading}
        period={clientsPeriod}
        onPeriodChange={handleClientsPeriodChange}
      />
    </div>
  );
});
