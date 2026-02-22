import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { BookingReschedule } from "./booking-reschedule";
import { BookingCancellation } from "./booking-cancellation";
import { ReviewSubmission } from "./review-submission";
import { CalendarIcon, ClockIcon, UserIcon } from "@/components/icons";

interface Booking {
  id: string;
  service_id: string;
  service_name: string;
  stylist_id: string;
  stylist_name: string;
  booking_date: string;
  booking_time: string;
  status: "confirmed" | "completed" | "cancelled" | "no_show";
  price: number;
  notes?: string;
}

interface BookingHistoryProps {
  email: string;
}

export function BookingHistory({ email }: BookingHistoryProps) {
  const [selectedBooking, setSelectedBooking] = useState<Booking | null>(null);
  const [showReschedule, setShowReschedule] = useState(false);
  const [showCancellation, setShowCancellation] = useState(false);
  const [showReview, setShowReview] = useState(false);

  const { data: bookings = [], isLoading } = useQuery({
    queryKey: ["booking-history", email],
    queryFn: async () => {
      const response = await apiClient.get("/api/bookings", {
        params: { email },
      });
      return response.data.bookings || [];
    },
    staleTime: 5 * 60 * 1000,
  });

  const upcomingBookings = bookings.filter(
    (b: Booking) =>
      b.status === "confirmed" &&
      new Date(b.booking_date) > new Date()
  );

  const pastBookings = bookings.filter(
    (b: Booking) =>
      (b.status === "completed" || b.status === "no_show") &&
      new Date(b.booking_date) <= new Date()
  );

  const getStatusColor = (status: string) => {
    switch (status) {
      case "confirmed":
        return "accent";
      case "completed":
        return "secondary";
      case "cancelled":
        return "destructive";
      case "no_show":
        return "destructive";
      default:
        return "secondary";
    }
  };

  const canReschedule = (booking: Booking) => {
    return (
      booking.status === "confirmed" &&
      new Date(booking.booking_date) > new Date()
    );
  };

  const canCancel = (booking: Booking) => {
    return (
      booking.status === "confirmed" &&
      new Date(booking.booking_date) > new Date()
    );
  };

  const canReview = (booking: Booking) => {
    return booking.status === "completed";
  };

  if (isLoading) {
    return <div className="text-[var(--muted-foreground)]">Loading bookings...</div>;
  }

  return (
    <div className="space-y-8">
      {/* Upcoming Bookings */}
      {upcomingBookings.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-[var(--foreground)]">
            Upcoming Appointments
          </h3>
          <div className="space-y-3">
            {upcomingBookings.map((booking: Booking) => (
              <Card key={booking.id}>
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h4 className="font-semibold text-[var(--foreground)]">
                        {booking.service_name}
                      </h4>
                      <p className="text-sm text-[var(--muted-foreground)]">
                        with {booking.stylist_name}
                      </p>
                    </div>
                    <Badge variant={getStatusColor(booking.status)}>
                      {booking.status}
                    </Badge>
                  </div>

                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div className="flex items-center gap-2 text-sm">
                      <CalendarIcon size={16} className="text-[var(--muted-foreground)]" />
                      <span className="text-[var(--foreground)]">
                        {new Date(booking.booking_date).toLocaleDateString(
                          "en-US",
                          {
                            weekday: "short",
                            year: "numeric",
                            month: "short",
                            day: "numeric",
                          }
                        )}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <ClockIcon size={16} className="text-[var(--muted-foreground)]" />
                      <span className="text-[var(--foreground)]">
                        {booking.booking_time}
                      </span>
                    </div>
                  </div>

                  <div className="flex gap-2 pt-4 border-t border-[var(--border)]">
                    {canReschedule(booking) && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => {
                          setSelectedBooking(booking);
                          setShowReschedule(true);
                        }}
                      >
                        Reschedule
                      </Button>
                    )}
                    {canCancel(booking) && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => {
                          setSelectedBooking(booking);
                          setShowCancellation(true);
                        }}
                      >
                        Cancel
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Past Bookings */}
      {pastBookings.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-[var(--foreground)]">
            Past Appointments
          </h3>
          <div className="space-y-3">
            {pastBookings.map((booking: Booking) => (
              <Card key={booking.id}>
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h4 className="font-semibold text-[var(--foreground)]">
                        {booking.service_name}
                      </h4>
                      <p className="text-sm text-[var(--muted-foreground)]">
                        with {booking.stylist_name}
                      </p>
                    </div>
                    <Badge variant={getStatusColor(booking.status)}>
                      {booking.status}
                    </Badge>
                  </div>

                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div className="flex items-center gap-2 text-sm">
                      <CalendarIcon size={16} className="text-[var(--muted-foreground)]" />
                      <span className="text-[var(--foreground)]">
                        {new Date(booking.booking_date).toLocaleDateString(
                          "en-US",
                          {
                            weekday: "short",
                            year: "numeric",
                            month: "short",
                            day: "numeric",
                          }
                        )}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <ClockIcon size={16} className="text-[var(--muted-foreground)]" />
                      <span className="text-[var(--foreground)]">
                        {booking.booking_time}
                      </span>
                    </div>
                  </div>

                  <div className="flex gap-2 pt-4 border-t border-[var(--border)]">
                    {canReview(booking) && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => {
                          setSelectedBooking(booking);
                          setShowReview(true);
                        }}
                      >
                        Leave Review
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {bookings.length === 0 && (
        <div className="text-center py-12">
          <p className="text-[var(--muted-foreground)]">
            No bookings yet. Book your first appointment!
          </p>
        </div>
      )}

      {/* Modals */}
      {selectedBooking && (
        <>
          <BookingReschedule
            isOpen={showReschedule}
            onClose={() => {
              setShowReschedule(false);
              setSelectedBooking(null);
            }}
            bookingId={selectedBooking.id}
            currentDate={selectedBooking.booking_date}
            currentTime={selectedBooking.booking_time}
            stylistId={selectedBooking.stylist_id}
            serviceId={selectedBooking.service_id}
          />

          <BookingCancellation
            isOpen={showCancellation}
            onClose={() => {
              setShowCancellation(false);
              setSelectedBooking(null);
            }}
            bookingId={selectedBooking.id}
            bookingDetails={{
              serviceName: selectedBooking.service_name,
              stylistName: selectedBooking.stylist_name,
              date: selectedBooking.booking_date,
              time: selectedBooking.booking_time,
              price: selectedBooking.price,
            }}
          />

          <ReviewSubmission
            isOpen={showReview}
            onClose={() => {
              setShowReview(false);
              setSelectedBooking(null);
            }}
            bookingId={selectedBooking.id}
            stylistId={selectedBooking.stylist_id}
            stylistName={selectedBooking.stylist_name}
            serviceName={selectedBooking.service_name}
          />
        </>
      )}
    </div>
  );
}
