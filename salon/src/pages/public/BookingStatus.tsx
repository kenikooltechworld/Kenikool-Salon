import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Card, Button, Spinner } from "@/components/ui";
import { apiClient } from "@/lib/utils/api";
import { formatDate } from "@/lib/utils/format";
import { CheckCircleIcon, AlertCircleIcon } from "@/components/icons";

interface BookingDetails {
  id: string;
  customer_name: string;
  customer_email: string;
  customer_phone: string;
  booking_date: string;
  booking_time: string;
  duration_minutes: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export default function BookingStatus() {
  const { bookingId } = useParams<{ bookingId: string }>();
  const navigate = useNavigate();

  const {
    data: booking,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["public-booking", bookingId],
    queryFn: async () => {
      const { data } = await apiClient.get<BookingDetails>(
        `/public/bookings/${bookingId}`,
      );
      return data;
    },
    enabled: !!bookingId,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Spinner />
      </div>
    );
  }

  if (error || !booking) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-8 px-4">
        <div className="max-w-2xl mx-auto">
          <Card className="p-8 text-center">
            <AlertCircleIcon size={48} className="text-red-600 mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-red-600 mb-4">
              Booking Not Found
            </h1>
            <p className="text-gray-600 mb-6">
              We couldn't find the booking you're looking for. Please check the
              booking ID and try again.
            </p>
            <Button onClick={() => navigate("/")} variant="primary">
              Back to Booking
            </Button>
          </Card>
        </div>
      </div>
    );
  }

  const bookingDate = new Date(booking.booking_date);
  const isCompleted = booking.status === "completed";
  const isCancelled = booking.status === "cancelled";

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-8 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2">Booking Status</h1>
          <p className="text-gray-600">
            Confirmation #{booking.id.substring(0, 8).toUpperCase()}
          </p>
        </div>

        {/* Status Card */}
        <Card className="p-8 mb-6">
          <div className="text-center mb-6">
            {isCompleted && (
              <CheckCircleIcon
                size={48}
                className="text-green-600 mx-auto mb-4"
              />
            )}
            {isCancelled && (
              <AlertCircleIcon
                size={48}
                className="text-red-600 mx-auto mb-4"
              />
            )}
            <h2 className="text-2xl font-bold capitalize mb-2">
              {booking.status}
            </h2>
            <p className="text-gray-600">
              {isCompleted && "Your appointment has been completed"}
              {isCancelled && "Your appointment has been cancelled"}
              {!isCompleted && !isCancelled && "Your appointment is confirmed"}
            </p>
          </div>

          {/* Booking Details */}
          <div className="space-y-4 border-t pt-6">
            <div className="flex justify-between">
              <span className="text-gray-600">Date:</span>
              <span className="font-semibold">
                {formatDate(bookingDate, "MMMM dd, yyyy")}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Time:</span>
              <span className="font-semibold">{booking.booking_time}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Duration:</span>
              <span className="font-semibold">
                {booking.duration_minutes} minutes
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Name:</span>
              <span className="font-semibold">{booking.customer_name}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Email:</span>
              <span className="font-semibold">{booking.customer_email}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Phone:</span>
              <span className="font-semibold">{booking.customer_phone}</span>
            </div>
          </div>
        </Card>

        {/* Actions */}
        {!isCancelled && (
          <div className="space-y-3 mb-6">
            <Button
              onClick={() => navigate(`/public/bookings/${bookingId}/cancel`)}
              variant="outline"
              className="w-full"
            >
              Cancel Booking
            </Button>
            <Button
              onClick={() =>
                navigate(`/public/bookings/${bookingId}/reschedule`)
              }
              variant="outline"
              className="w-full"
            >
              Reschedule Booking
            </Button>
          </div>
        )}

        {/* Back Button */}
        <Button
          onClick={() => navigate("/")}
          variant="ghost"
          className="w-full"
        >
          Back to Salon
        </Button>
      </div>
    </div>
  );
}
