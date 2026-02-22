import { Card } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import {
  CalendarIcon,
  CheckCircleIcon,
  XCircleIcon,
  AlertTriangleIcon,
  TrendingUpIcon,
} from "@/components/icons";
import { useBookings } from "@/lib/api/hooks/useBookings";

interface AppointmentMetricsProps {
  clientId: string;
}

export function AppointmentMetrics({ clientId }: AppointmentMetricsProps) {
  const {
    data: bookingsData,
    isLoading,
    error,
  } = useBookings({
    client_id: clientId,
    limit: 1000, // Get all bookings for metrics
  });

  const bookings = bookingsData?.items || [];

  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="flex justify-center py-4">
          <Spinner />
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="p-6">
        <Alert variant="error">
          <AlertTriangleIcon size={20} />
          <div>
            <h3 className="font-semibold">Error loading metrics</h3>
            <p className="text-sm">{error.message}</p>
          </div>
        </Alert>
      </Card>
    );
  }

  // Calculate metrics
  const totalBookings = bookings.length;
  const completedBookings = bookings.filter(
    (b) => b.status === "completed"
  ).length;
  const noShowCount = bookings.filter((b) => b.status === "no_show").length;
  const cancelledCount = bookings.filter(
    (b) => b.status === "cancelled"
  ).length;

  const attendanceRate =
    totalBookings > 0
      ? ((completedBookings / (totalBookings - cancelledCount)) * 100).toFixed(
          0
        )
      : 0;

  // Find patterns - most booked day of week
  const dayOfWeekCounts: { [key: string]: number } = {};
  bookings.forEach((booking) => {
    const date = new Date(booking.booking_date);
    const dayName = date.toLocaleDateString("en-US", { weekday: "long" });
    dayOfWeekCounts[dayName] = (dayOfWeekCounts[dayName] || 0) + 1;
  });

  const mostBookedDay = Object.entries(dayOfWeekCounts).sort(
    ([, a], [, b]) => b - a
  )[0]?.[0];

  // Find most booked time slot
  const timeSlotCounts: { [key: string]: number } = {};
  bookings.forEach((booking) => {
    const date = new Date(booking.booking_date);
    const hour = date.getHours();
    let timeSlot = "";
    if (hour < 12) timeSlot = "Morning (6am-12pm)";
    else if (hour < 17) timeSlot = "Afternoon (12pm-5pm)";
    else timeSlot = "Evening (5pm-9pm)";

    timeSlotCounts[timeSlot] = (timeSlotCounts[timeSlot] || 0) + 1;
  });

  const mostBookedTime = Object.entries(timeSlotCounts).sort(
    ([, a], [, b]) => b - a
  )[0]?.[0];

  return (
    <Card className="p-6">
      <h2 className="text-lg font-semibold text-foreground mb-4">
        Appointment History
      </h2>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        {/* Total Bookings */}
        <div className="p-3 bg-muted/50 rounded-lg">
          <div className="flex items-center gap-2 mb-1">
            <CalendarIcon size={16} className="text-primary" />
            <p className="text-xs text-muted-foreground">Total</p>
          </div>
          <p className="text-2xl font-bold text-foreground">{totalBookings}</p>
        </div>

        {/* Completed */}
        <div className="p-3 bg-muted/50 rounded-lg">
          <div className="flex items-center gap-2 mb-1">
            <CheckCircleIcon size={16} className="text-green-600" />
            <p className="text-xs text-muted-foreground">Completed</p>
          </div>
          <p className="text-2xl font-bold text-foreground">
            {completedBookings}
          </p>
        </div>

        {/* No-Shows */}
        <div className="p-3 bg-muted/50 rounded-lg">
          <div className="flex items-center gap-2 mb-1">
            <XCircleIcon size={16} className="text-red-600" />
            <p className="text-xs text-muted-foreground">No-Shows</p>
          </div>
          <p className="text-2xl font-bold text-foreground">{noShowCount}</p>
        </div>

        {/* Attendance Rate */}
        <div className="p-3 bg-muted/50 rounded-lg">
          <div className="flex items-center gap-2 mb-1">
            <TrendingUpIcon size={16} className="text-primary" />
            <p className="text-xs text-muted-foreground">Attendance</p>
          </div>
          <p className="text-2xl font-bold text-foreground">
            {attendanceRate}%
          </p>
        </div>
      </div>

      {/* Patterns & Highlights */}
      {(mostBookedDay || mostBookedTime) && (
        <div className="pt-4 border-t border-border">
          <h3 className="text-sm font-semibold text-foreground mb-3">
            Booking Patterns
          </h3>
          <div className="space-y-2">
            {mostBookedDay && (
              <div className="flex items-center justify-between p-2 bg-muted/30 rounded">
                <span className="text-sm text-muted-foreground">
                  Preferred Day:
                </span>
                <span className="text-sm font-medium text-foreground">
                  {mostBookedDay}
                </span>
              </div>
            )}
            {mostBookedTime && (
              <div className="flex items-center justify-between p-2 bg-muted/30 rounded">
                <span className="text-sm text-muted-foreground">
                  Preferred Time:
                </span>
                <span className="text-sm font-medium text-foreground">
                  {mostBookedTime}
                </span>
              </div>
            )}
          </div>
        </div>
      )}
    </Card>
  );
}
