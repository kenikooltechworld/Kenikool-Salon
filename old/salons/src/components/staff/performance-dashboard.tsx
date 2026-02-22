"use client";

import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

interface PerformanceMetrics {
  revenue?: {
    total: number;
    average_per_booking: number;
    booking_count: number;
  };
  bookings?: { total: number; by_service: Record<string, number> };
  rating?: {
    average: number;
    review_count: number;
    distribution: Record<number, number>;
  };
  rebooking_rate?: {
    rate: number;
    rebooking_count: number;
    total_unique_clients: number;
  };
  avg_service_time?: { minutes: number; booking_count: number };
  utilization?: {
    percentage: number;
    booked_hours: number;
    available_hours: number;
  };
}

interface PerformanceDashboardProps {
  staffId: string;
  staffName: string;
  startDate?: Date;
  endDate?: Date;
}

export function PerformanceDashboard({
  staffId,
  staffName,
  startDate,
  endDate,
}: PerformanceDashboardProps) {
  const { data: performance, isLoading } = useQuery({
    queryKey: ["staff-performance", staffId, startDate, endDate],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (startDate) params.append("start_date", startDate.toISOString());
      if (endDate) params.append("end_date", endDate.toISOString());

      const res = await fetch(`/api/staff/performance/${staffId}?${params}`);
      if (!res.ok) throw new Error("Failed to fetch performance");
      return res.json();
    },
  });

  const metrics: PerformanceMetrics = performance?.data?.metrics || {};

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[...Array(6)].map((_, i) => (
          <Skeleton key={i} className="h-32" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">{staffName}</h2>
        <p className="text-sm text-muted-foreground">Performance Overview</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Revenue Card */}
        {metrics.revenue && (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">
                Total Revenue
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                ${metrics.revenue.total.toFixed(2)}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                {metrics.revenue.booking_count} bookings
              </p>
              <p className="text-xs text-muted-foreground">
                Avg: ${metrics.revenue.average_per_booking.toFixed(2)}/booking
              </p>
            </CardContent>
          </Card>
        )}

        {/* Bookings Card */}
        {metrics.bookings && (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">
                Total Bookings
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.bookings.total}</div>
              <p className="text-xs text-muted-foreground mt-1">
                {Object.keys(metrics.bookings.by_service).length} service types
              </p>
            </CardContent>
          </Card>
        )}

        {/* Rating Card */}
        {metrics.rating && (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">
                Average Rating
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {metrics.rating.average.toFixed(1)}/5
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                {metrics.rating.review_count} reviews
              </p>
              <div className="flex gap-1 mt-2">
                {[1, 2, 3, 4, 5].map((star) => (
                  <div
                    key={star}
                    className="text-xs"
                    title={`${metrics.rating?.distribution?.[star] || 0} ${star}-star reviews`}
                  >
                    {metrics.rating?.distribution?.[star] || 0}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Rebooking Rate Card */}
        {metrics.rebooking_rate && (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">
                Rebooking Rate
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {metrics.rebooking_rate.rate.toFixed(1)}%
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                {metrics.rebooking_rate.rebooking_count} returning clients
              </p>
              <p className="text-xs text-muted-foreground">
                {metrics.rebooking_rate.total_unique_clients} total clients
              </p>
            </CardContent>
          </Card>
        )}

        {/* Avg Service Time Card */}
        {metrics.avg_service_time && (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">
                Avg Service Time
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {metrics.avg_service_time.minutes.toFixed(0)} min
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                {metrics.avg_service_time.booking_count} bookings
              </p>
            </CardContent>
          </Card>
        )}

        {/* Utilization Card */}
        {metrics.utilization && (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Utilization</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {metrics.utilization.percentage.toFixed(1)}%
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                {metrics.utilization.booked_hours.toFixed(1)} /{" "}
                {metrics.utilization.available_hours.toFixed(1)} hours
              </p>
              <div className="w-full bg-muted rounded-full h-2 mt-2">
                <div
                  className="bg-primary h-2 rounded-full"
                  style={{
                    width: `${Math.min(metrics.utilization.percentage, 100)}%`,
                  }}
                />
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
