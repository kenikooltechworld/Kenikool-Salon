import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { Alert } from "@/components/ui/alert";
import {
  CalendarIcon,
  ClockIcon,
  UserIcon,
  AlertTriangleIcon,
  XIcon,
  EditIcon,
} from "@/components/icons";
import {
  useBookings,
  useUpdateBookingStatus,
} from "@/lib/api/hooks/useBookings";
import { Booking } from "@/lib/api/types";
import { format } from "date-fns";

interface UpcomingAppointmentsProps {
  clientId: string;
  onReschedule?: (booking: Booking) => void;
}

export function UpcomingAppointments({
  clientId,
  onReschedule,
}: UpcomingAppointmentsProps) {
  const {
    data: bookingsData,
    isLoading,
    error,
    refetch,
  } = useBookings({
    client_id: clientId,
    status: "confirmed,pending",
    limit: 5,
  });

  const updateStatusMutation = useUpdateBookingStatus();

  const bookings = bookingsData?.items || [];

  // Filter for upcoming appointments only
  const upcomingBookings = bookings.filter((booking) => {
    const bookingDate = new Date(booking.booking_date);
    return bookingDate >= new Date();
  });

  const handleCancel = async (bookingId: string) => {
    if (!confirm("Are you sure you want to cancel this appointment?")) {
      return;
    }

    try {
      await updateStatusMutation.mutateAsync({
        id: bookingId,
        data: { status: "cancelled" },
      });
      refetch();
    } catch (error) {
      console.error("Error cancelling booking:", error);
    }
  };

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
            <h3 className="font-semibold">Error loading appointments</h3>
            <p className="text-sm">{error.message}</p>
          </div>
        </Alert>
      </Card>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "confirmed":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200";
      case "pending":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200";
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200";
    }
  };

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-foreground">
          Upcoming Appointments
        </h2>
        {upcomingBookings.length > 0 && (
          <Badge variant="secondary">{upcomingBookings.length}</Badge>
        )}
      </div>

      {upcomingBookings.length === 0 ? (
        <div className="text-center py-8">
          <CalendarIcon
            size={48}
            className="mx-auto text-muted-foreground mb-3"
          />
          <p className="text-muted-foreground">No upcoming appointments</p>
        </div>
      ) : (
        <div className="space-y-3">
          {upcomingBookings.map((booking) => (
            <div
              key={booking.id}
              className="p-4 border border-border rounded-lg hover:bg-muted/50 transition-colors"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="font-semibold text-foreground">
                      {booking.service_name}
                    </h3>
                    <Badge className={getStatusColor(booking.status)}>
                      {booking.status}
                    </Badge>
                  </div>
                  {booking.variant_name && (
                    <p className="text-sm text-muted-foreground mb-2">
                      Variant: {booking.variant_name}
                    </p>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 mb-3">
                <div className="flex items-center gap-2">
                  <CalendarIcon size={16} className="text-muted-foreground" />
                  <span className="text-sm text-foreground">
                    {format(new Date(booking.booking_date), "MMM dd, yyyy")}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <ClockIcon size={16} className="text-muted-foreground" />
                  <span className="text-sm text-foreground">
                    {format(new Date(booking.booking_date), "hh:mm a")}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <UserIcon size={16} className="text-muted-foreground" />
                  <span className="text-sm text-foreground">
                    {booking.stylist_name}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <ClockIcon size={16} className="text-muted-foreground" />
                  <span className="text-sm text-foreground">
                    {booking.duration_minutes} mins
                  </span>
                </div>
              </div>

              {booking.notes && (
                <p className="text-sm text-muted-foreground mb-3 p-2 bg-muted/50 rounded">
                  {booking.notes}
                </p>
              )}

              <div className="flex items-center gap-2">
                {onReschedule && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onReschedule(booking)}
                    className="flex-1"
                  >
                    <EditIcon size={16} />
                    Reschedule
                  </Button>
                )}
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleCancel(booking.id)}
                  disabled={updateStatusMutation.isPending}
                  className="flex-1 text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20"
                >
                  <XIcon size={16} />
                  Cancel
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
