import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { Card, Button, Spinner, Alert, Input } from "@/components/ui";
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

export default function BookingReschedule() {
  const { bookingId } = useParams<{ bookingId: string }>();
  const navigate = useNavigate();
  const [newDate, setNewDate] = useState("");
  const [newTime, setNewTime] = useState("");
  const [error, setError] = useState("");

  const {
    data: booking,
    isLoading,
    error: fetchError,
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

  const rescheduleMutation = useMutation({
    mutationFn: async () => {
      if (!newDate || !newTime) {
        throw new Error("Please select both date and time");
      }

      const { data } = await apiClient.post(
        `/public/bookings/${bookingId}/reschedule`,
        {
          new_date: newDate,
          new_time: newTime,
        },
      );
      return data;
    },
    onSuccess: () => {
      navigate(`/public/bookings/${bookingId}?rescheduled=true`);
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || "Failed to reschedule booking");
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Spinner />
      </div>
    );
  }

  if (fetchError || !booking) {
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
  const minDate = new Date();
  minDate.setDate(minDate.getDate() + 1);
  const minDateStr = minDate.toISOString().split("T")[0];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-8 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2">Reschedule Booking</h1>
          <p className="text-gray-600">
            Confirmation #{booking.id.substring(0, 8).toUpperCase()}
          </p>
        </div>

        {/* Current Booking Details */}
        <Card className="p-6 mb-6 bg-muted/50">
          <h3 className="font-semibold text-lg mb-4">Current Booking</h3>
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

        {/* Reschedule Form */}
        <Card className="p-6 mb-6">
          <h3 className="font-semibold text-lg mb-4">Select New Date & Time</h3>

          {error && (
            <Alert variant="error" className="mb-4">
              <p>{error}</p>
            </Alert>
          )}

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                New Date *
              </label>
              <Input
                type="date"
                value={newDate}
                onChange={(e) => {
                  setNewDate(e.target.value);
                  setError("");
                }}
                min={minDateStr}
              />
              <p className="text-xs text-gray-500 mt-1">
                Select a date at least 24 hours from now
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                New Time *
              </label>
              <Input
                type="time"
                value={newTime}
                onChange={(e) => {
                  setNewTime(e.target.value);
                  setError("");
                }}
              />
              <p className="text-xs text-gray-500 mt-1">
                Select your preferred time
              </p>
            </div>

            <Alert>
              <p className="text-sm">
                <strong>Note:</strong> Availability is subject to staff
                schedules. We'll confirm your new appointment via email.
              </p>
            </Alert>

            <div className="flex gap-3">
              <Button
                onClick={() => rescheduleMutation.mutate()}
                disabled={rescheduleMutation.isPending || !newDate || !newTime}
                variant="primary"
                className="flex-1"
              >
                {rescheduleMutation.isPending ? (
                  <>
                    <Spinner className="w-4 h-4 mr-2" />
                    Rescheduling...
                  </>
                ) : (
                  "Confirm New Date & Time"
                )}
              </Button>
              <Button
                onClick={() => navigate(`/public/bookings/${bookingId}`)}
                variant="outline"
                className="flex-1"
                disabled={rescheduleMutation.isPending}
              >
                Cancel
              </Button>
            </div>
          </div>
        </Card>

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
