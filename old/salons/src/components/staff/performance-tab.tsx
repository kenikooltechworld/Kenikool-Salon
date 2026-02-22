import { Card } from "@/components/ui/card";

interface StylistStatistics {
  totalBookings: number;
  completedBookings: number;
  cancelledBookings: number;
  totalRevenue: number;
  averageRating?: number;
}

interface PerformanceTabProps {
  statistics: StylistStatistics | null;
}

export function PerformanceTab({ statistics }: PerformanceTabProps) {
  if (!statistics) {
    return (
      <Card className="p-4 sm:p-6">
        <p className="text-muted-foreground">No performance data available</p>
      </Card>
    );
  }

  return (
    <Card className="p-4 sm:p-6">
      <h2 className="text-lg sm:text-xl font-bold text-foreground mb-4">
        Performance Metrics
      </h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="p-4 border border-border rounded-lg">
          <p className="text-sm text-muted-foreground mb-2">Total Bookings</p>
          <p className="text-2xl font-bold">{statistics.totalBookings || 0}</p>
        </div>
        <div className="p-4 border border-border rounded-lg">
          <p className="text-sm text-muted-foreground mb-2">Completed</p>
          <p className="text-2xl font-bold">
            {statistics.completedBookings || 0}
          </p>
        </div>
        <div className="p-4 border border-border rounded-lg">
          <p className="text-sm text-muted-foreground mb-2">Cancelled</p>
          <p className="text-2xl font-bold">
            {statistics.cancelledBookings || 0}
          </p>
        </div>
        <div className="p-4 border border-border rounded-lg">
          <p className="text-sm text-muted-foreground mb-2">Average Rating</p>
          <p className="text-2xl font-bold">
            {statistics.averageRating
              ? statistics.averageRating.toFixed(1)
              : "N/A"}
          </p>
        </div>
      </div>
    </Card>
  );
}
