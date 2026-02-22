import { Card } from "@/components/ui/card";
import { Table } from "@/components/ui/table";
import {
  TrendingUpIcon,
  TrendingDownIcon,
  CalendarIcon,
  DollarIcon,
} from "@/components/icons";
import type { Booking } from "@/lib/api/types";

interface BookingAnalyticsDashboardProps {
  bookings: Booking[];
}

export function BookingAnalyticsDashboard({
  bookings,
}: BookingAnalyticsDashboardProps) {
  const calculateMetrics = () => {
    const total = bookings.length;
    const totalRevenue = bookings.reduce(
      (sum, b) => sum + (b.service_price || 0),
      0,
    );
    const completed = bookings.filter((b) => b.status === "completed").length;
    const cancelled = bookings.filter((b) => b.status === "cancelled").length;
    const avgPrice = total > 0 ? totalRevenue / total : 0;

    const last7Days = bookings.filter((b) => {
      const bookingDate = new Date(b.booking_date);
      const sevenDaysAgo = new Date();
      sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
      return bookingDate >= sevenDaysAgo;
    }).length;

    const last30Days = bookings.filter((b) => {
      const bookingDate = new Date(b.booking_date);
      const thirtyDaysAgo = new Date();
      thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
      return bookingDate >= thirtyDaysAgo;
    }).length;

    const completionRate = total > 0 ? (completed / total) * 100 : 0;
    const cancellationRate = total > 0 ? (cancelled / total) * 100 : 0;

    return {
      total,
      totalRevenue,
      completed,
      cancelled,
      avgPrice,
      last7Days,
      last30Days,
      completionRate,
      cancellationRate,
    };
  };

  const metrics = calculateMetrics();

  const getServiceBreakdown = () => {
    const breakdown: Record<string, number> = {};
    bookings.forEach((b) => {
      breakdown[b.service_name] = (breakdown[b.service_name] || 0) + 1;
    });
    return Object.entries(breakdown)
      .map(([service, count]) => ({ service, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 5);
  };

  const getStylistPerformance = () => {
    const performance: Record<string, { count: number; revenue: number }> = {};
    bookings.forEach((b) => {
      if (!performance[b.stylist_name]) {
        performance[b.stylist_name] = { count: 0, revenue: 0 };
      }
      performance[b.stylist_name].count += 1;
      performance[b.stylist_name].revenue += b.service_price || 0;
    });
    return Object.entries(performance)
      .map(([stylist, data]) => ({ stylist, ...data }))
      .sort((a, b) => b.revenue - a.revenue)
      .slice(0, 5);
  };

  const serviceBreakdown = getServiceBreakdown();
  const stylistPerformance = getStylistPerformance();

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-2 sm:gap-3 md:gap-4">
        <Card className="p-3 sm:p-4">
          <div className="flex items-center justify-between gap-2">
            <div className="min-w-0">
              <p className="text-xs sm:text-sm text-muted-foreground truncate">
                Total
              </p>
              <p className="text-lg sm:text-2xl font-bold mt-1">
                {metrics.total}
              </p>
            </div>
            <CalendarIcon
              size={20}
              className="text-primary shrink-0 hidden sm:block"
            />
          </div>
          <p className="text-xs text-muted-foreground mt-2">
            {metrics.last7Days} in 7d
          </p>
        </Card>

        <Card className="p-3 sm:p-4">
          <div className="flex items-center justify-between gap-2">
            <div className="min-w-0">
              <p className="text-xs sm:text-sm text-muted-foreground truncate">
                Revenue
              </p>
              <p className="text-lg sm:text-2xl font-bold mt-1">
                ₦{(metrics.totalRevenue / 1000).toFixed(1)}K
              </p>
            </div>
            <DollarIcon
              size={20}
              className="text-success shrink-0 hidden sm:block"
            />
          </div>
          <p className="text-xs text-muted-foreground mt-2 truncate">
            Avg: ₦{(metrics.avgPrice / 1000).toFixed(1)}K
          </p>
        </Card>

        <Card className="p-3 sm:p-4">
          <div className="flex items-center justify-between gap-2">
            <div className="min-w-0">
              <p className="text-xs sm:text-sm text-muted-foreground truncate">
                Complete
              </p>
              <p className="text-lg sm:text-2xl font-bold mt-1">
                {metrics.completionRate.toFixed(0)}%
              </p>
            </div>
            <TrendingUpIcon
              size={20}
              className="text-success shrink-0 hidden sm:block"
            />
          </div>
          <p className="text-xs text-muted-foreground mt-2">
            {metrics.completed} done
          </p>
        </Card>

        <Card className="p-3 sm:p-4">
          <div className="flex items-center justify-between gap-2">
            <div className="min-w-0">
              <p className="text-xs sm:text-sm text-muted-foreground truncate">
                Cancel
              </p>
              <p className="text-lg sm:text-2xl font-bold mt-1">
                {metrics.cancellationRate.toFixed(0)}%
              </p>
            </div>
            <TrendingDownIcon
              size={20}
              className="text-destructive shrink-0 hidden sm:block"
            />
          </div>
          <p className="text-xs text-muted-foreground mt-2">
            {metrics.cancelled} cancelled
          </p>
        </Card>
      </div>

      {/* Service Breakdown */}
      <Card className="p-3 sm:p-4 md:p-6">
        <h3 className="text-sm sm:text-lg font-semibold mb-3 sm:mb-4">
          Top Services
        </h3>
        <div className="space-y-2 sm:space-y-3">
          {serviceBreakdown.map((item) => (
            <div
              key={item.service}
              className="flex items-center justify-between gap-2 text-xs sm:text-sm"
            >
              <span className="truncate flex-1">{item.service}</span>
              <div className="flex items-center gap-2 flex-shrink-0">
                <div className="w-16 sm:w-24 md:w-32 bg-muted rounded-full h-2">
                  <div
                    className="bg-primary h-2 rounded-full"
                    style={{
                      width: `${(item.count / metrics.total) * 100}%`,
                    }}
                  />
                </div>
                <span className="text-xs sm:text-sm font-medium w-8 text-right">
                  {item.count}
                </span>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Stylist Performance */}
      <Card className="p-3 sm:p-4 md:p-6 overflow-x-auto">
        <h3 className="text-sm sm:text-lg font-semibold mb-3 sm:mb-4">
          Top Stylists
        </h3>
        <div className="overflow-x-auto">
          <Table>
            <thead>
              <tr>
                <th className="text-xs sm:text-sm text-left">Stylist</th>
                <th className="text-xs sm:text-sm text-right">Bookings</th>
                <th className="text-xs sm:text-sm text-right">Revenue</th>
              </tr>
            </thead>
            <tbody>
              {stylistPerformance.map((item) => (
                <tr key={item.stylist} className="text-xs sm:text-sm">
                  <td className="truncate">{item.stylist}</td>
                  <td className="text-right">{item.count}</td>
                  <td className="text-right font-medium">
                    ₦{(item.revenue / 1000).toFixed(1)}K
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        </div>
      </Card>

      {/* Booking Trend */}
      <Card className="p-3 sm:p-4 md:p-6">
        <h3 className="text-sm sm:text-lg font-semibold mb-3 sm:mb-4">
          Booking Trend
        </h3>
        <div className="grid grid-cols-2 gap-2 sm:gap-3 md:gap-4">
          <div className="text-center p-3 sm:p-4 bg-muted rounded-lg">
            <p className="text-xs sm:text-sm text-muted-foreground">
              Last 7 Days
            </p>
            <p className="text-lg sm:text-2xl font-bold mt-1">
              {metrics.last7Days}
            </p>
          </div>
          <div className="text-center p-3 sm:p-4 bg-muted rounded-lg">
            <p className="text-xs sm:text-sm text-muted-foreground">
              Last 30 Days
            </p>
            <p className="text-lg sm:text-2xl font-bold mt-1">
              {metrics.last30Days}
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
