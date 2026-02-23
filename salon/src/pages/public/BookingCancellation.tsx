import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { Card, Button, Spinner, Alert, Textarea } from "@/components/ui";
import { apiClient } from "@/lib/utils/api";
import { formatDate } from "@/lib/utils/format";
import { AlertCircleIcon } from "@/components/icons";

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

export default function BookingCancellation() {
  const { bookingId } = useParams<{ bookingId: string }>();
  const navigate = useNavigate();
  const [cancellationReason, setCancellationReason] = useState("");
  const [showConfirm, setShowConfirm] = useState(false);

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

  const cancelMutation = useMutation({
    mutationFn: async () => {
      const { data } = await apiClient.post(
        `/public/bookings/${bookingId}/cancel`,
        {
          cancellation_reason: cancellationReason || null,
        },
      );
      return data;
    },
    onSuccess: () => {
      navigate(`/public/bookings/${bookingId}?cancelled=true`);
    },
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
            <Button onClick={() => navigate("/")} variant="primary">
              Back to Booking
            </Button>
          </Card>
        </div>
      </div>
    );
  }

  const bookingDate = new Date(booking.booking_date);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-8 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2">Cancel Booking</h1>
          <p className="text-gray-600">
            Confirmation #{booking.id.substring(0, 8).toUpperCase()}
          </p>
        </div>

        {/* Booking Details */}
        <Card className="p-6 mb-6 bg-muted/50">
          <h3 className="font-semibold text-lg mb-4">Booking Details</h3>
          <div className="space-y-3">
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
          </div>
        </Card>

        {/* Warning */}
        <Alert variant="warning" className="mb-6">
          <AlertCircleIcon size={20} className="inline mr-2" />
          <p>
            <strong>Warning:</strong> Cancelling this booking cannot be undone.
            You will receive a cancellation confirmation email.
          </p>
        </Alert>

        {/* Cancellation Form */}
        {!showConfirm ? (
          <Card className="p-6 mb-6">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Reason for Cancellation (Optional)
                </label>
                <Textarea
                  value={cancellationReason}
                  onChange={(e) => setCancellationReason(e.target.value)}
                  placeholder="Please let us know why you're cancelling..."
                  rows={4}
                />
              </div>

              <div className="flex gap-3">
                <Button
                  onClick={() => setShowConfirm(true)}
                  variant="destructive"
                  className="flex-1"
                >
                  Continue to Cancel
                </Button>
                <Button
                  onClick={() => navigate(`/public/bookings/${bookingId}`)}
                  variant="outline"
                  className="flex-1"
                >
                  Keep Booking
                </Button>
              </div>
            </div>
          </Card>
        ) : (
          <Card className="p-6 mb-6 border-red-200 bg-red-50">
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold text-lg mb-2">
                  Confirm Cancellation
                </h3>
                <p className="text-gray-600 mb-4">
                  Are you sure you want to cancel this booking? This action
                  cannot be undone.
                </p>
              </div>

              <div className="flex gap-3">
                <Button
                  onClick={() => cancelMutation.mutate()}
                  disabled={cancelMutation.isPending}
                  variant="destructive"
                  className="flex-1"
                >
                  {cancelMutation.isPending ? (
                    <>
                      <Spinner className="w-4 h-4 mr-2" />
                      Cancelling...
                    </>
                  ) : (
                    "Yes, Cancel Booking"
                  )}
                </Button>
                <Button
                  onClick={() => setShowConfirm(false)}
                  variant="outline"
                  className="flex-1"
                  disabled={cancelMutation.isPending}
                >
                  No, Go Back
                </Button>
              </div>
            </div>
          </Card>
        )}

        {/* Back Button */}
        <Button
          onClick={() => navigate(`/public/bookings/${bookingId}`)}
          variant="ghost"
          className="w-full"
        >
          Back to Booking
        </Button>
      </div>
    </div>
  );
}
