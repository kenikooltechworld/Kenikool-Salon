import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import {
  DollarIcon,
  CalendarIcon,
  UsersIcon,
  ChartIcon,
  TrendingUpIcon,
  TrendingDownIcon,
  AlertTriangleIcon,
  DownloadIcon,
} from "@/components/icons";
import { useAnalytics } from "@/lib/api/hooks/useAnalytics-offline";
import { RevenueChart } from "@/components/analytics/revenue-chart";
import { ServicePerformance } from "@/components/analytics/service-performance";
import { StaffLeaderboard } from "@/components/analytics/staff-leaderboard";
import { AIInsights } from "@/components/analytics/ai-insights";
import { ExportModal } from "@/components/analytics/export-modal";
import { format, subDays } from "date-fns";

export default function AnalyticsPage() {
  const [dateRange, setDateRange] = useState({
    start: format(subDays(new Date(), 30), "yyyy-MM-dd"),
    end: format(new Date(), "yyyy-MM-dd"),
  });
  const [showExportModal, setShowExportModal] = useState(false);

  const {
    data: analytics,
    isLoading,
    error,
  } = useAnalytics({
    date_from: dateRange.start,
    date_to: dateRange.end,
  });

  const handleExport = () => {
    setShowExportModal(true);
  };

  if (error) {
    return (
      <Alert variant="error">
        <AlertTriangleIcon size={20} />
        <div>
          <h3 className="font-semibold">Error loading analytics</h3>
          <p className="text-sm">{error.message}</p>
        </div>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Analytics</h1>
          <p className="text-muted-foreground">
            Track your business performance and insights
          </p>
        </div>
        <Button onClick={handleExport}>
          <DownloadIcon size={20} />
          Export Report
        </Button>
      </div>

      {/* Date Range Filter */}
      <Card className="p-4">
        <div className="flex flex-col md:flex-row gap-4 items-end">
          <div className="flex-1">
            <label className="block text-sm font-medium text-foreground mb-1">
              Start Date
            </label>
            <input
              type="date"
              value={dateRange.start}
              onChange={(e) =>
                setDateRange({ ...dateRange, start: e.target.value })
              }
              className="w-full px-3 py-2 border border-[var(--border)] rounded-lg bg-background text-foreground"
            />
          </div>
          <div className="flex-1">
            <label className="block text-sm font-medium text-foreground mb-1">
              End Date
            </label>
            <input
              type="date"
              value={dateRange.end}
              onChange={(e) =>
                setDateRange({ ...dateRange, end: e.target.value })
              }
              className="w-full px-3 py-2 border border-[var(--border)] rounded-lg bg-background text-foreground"
            />
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() =>
                setDateRange({
                  start: format(subDays(new Date(), 7), "yyyy-MM-dd"),
                  end: format(new Date(), "yyyy-MM-dd"),
                })
              }
            >
              Last 7 Days
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() =>
                setDateRange({
                  start: format(subDays(new Date(), 30), "yyyy-MM-dd"),
                  end: format(new Date(), "yyyy-MM-dd"),
                })
              }
            >
              Last 30 Days
            </Button>
          </div>
        </div>
      </Card>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Spinner />
        </div>
      ) : (
        <>
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card className="p-6">
              <div className="flex items-center gap-2 mb-2">
                <DollarIcon size={16} className="text-muted-foreground" />
                <span className="text-sm text-muted-foreground">
                  Total Revenue
                </span>
              </div>
              <p className="text-3xl font-bold text-foreground mb-2">
                ₦{(analytics?.total_revenue || 0).toLocaleString()}
              </p>
              <div className="flex items-center gap-1">
                {(analytics?.revenue_change || 0) >= 0 ? (
                  <TrendingUpIcon size={14} className="text-[var(--success)]" />
                ) : (
                  <TrendingDownIcon size={14} className="text-[var(--error)]" />
                )}
                <span
                  className={`text-sm ${
                    (analytics?.revenue_change || 0) >= 0
                      ? "text-[var(--success)]"
                      : "text-[var(--error)]"
                  }`}
                >
                  {analytics?.revenue_change || 0}%
                </span>
              </div>
            </Card>

            <Card className="p-6">
              <div className="flex items-center gap-2 mb-2">
                <CalendarIcon size={16} className="text-muted-foreground" />
                <span className="text-sm text-muted-foreground">
                  Total Bookings
                </span>
              </div>
              <p className="text-3xl font-bold text-foreground mb-2">
                {analytics?.total_bookings || 0}
              </p>
              <div className="flex items-center gap-1">
                {(analytics?.bookings_change || 0) >= 0 ? (
                  <TrendingUpIcon size={14} className="text-[var(--success)]" />
                ) : (
                  <TrendingDownIcon size={14} className="text-[var(--error)]" />
                )}
                <span
                  className={`text-sm ${
                    (analytics?.bookings_change || 0) >= 0
                      ? "text-[var(--success)]"
                      : "text-[var(--error)]"
                  }`}
                >
                  {analytics?.bookings_change || 0}%
                </span>
              </div>
            </Card>

            <Card className="p-6">
              <div className="flex items-center gap-2 mb-2">
                <UsersIcon size={16} className="text-muted-foreground" />
                <span className="text-sm text-muted-foreground">
                  New Clients
                </span>
              </div>
              <p className="text-3xl font-bold text-foreground mb-2">
                {analytics?.new_clients || 0}
              </p>
              <div className="flex items-center gap-1">
                {(analytics?.clients_change || 0) >= 0 ? (
                  <TrendingUpIcon size={14} className="text-[var(--success)]" />
                ) : (
                  <TrendingDownIcon size={14} className="text-[var(--error)]" />
                )}
                <span
                  className={`text-sm ${
                    (analytics?.clients_change || 0) >= 0
                      ? "text-[var(--success)]"
                      : "text-[var(--error)]"
                  }`}
                >
                  {analytics?.clients_change || 0}%
                </span>
              </div>
            </Card>

            <Card className="p-6">
              <div className="flex items-center gap-2 mb-2">
                <ChartIcon size={16} className="text-muted-foreground" />
                <span className="text-sm text-muted-foreground">
                  Avg. Booking Value
                </span>
              </div>
              <p className="text-3xl font-bold text-foreground mb-2">
                ₦{(analytics?.avg_booking_value || 0).toLocaleString()}
              </p>
              <div className="flex items-center gap-1">
                {(analytics?.avg_value_change || 0) >= 0 ? (
                  <TrendingUpIcon size={14} className="text-[var(--success)]" />
                ) : (
                  <TrendingDownIcon size={14} className="text-[var(--error)]" />
                )}
                <span
                  className={`text-sm ${
                    (analytics?.avg_value_change || 0) >= 0
                      ? "text-[var(--success)]"
                      : "text-[var(--error)]"
                  }`}
                >
                  {analytics?.avg_value_change || 0}%
                </span>
              </div>
            </Card>
          </div>

          {/* Revenue Chart */}
          <RevenueChart data={analytics?.revenue_data || []} />

          {/* AI Insights */}
          <AIInsights insights={analytics?.insights || []} />

          {/* Service Performance & Staff Leaderboard */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ServicePerformance services={analytics?.top_services || []} />
            <StaffLeaderboard staff={analytics?.staff_performance || []} />
          </div>
        </>
      )}

      {/* Export Modal */}
      {analytics && (
        <ExportModal
          open={showExportModal}
          onClose={() => setShowExportModal(false)}
          data={analytics}
          dateRange={dateRange}
          salonName="Kenikool Salon" // TODO: Get from tenant context
        />
      )}
    </div>
  );
}
