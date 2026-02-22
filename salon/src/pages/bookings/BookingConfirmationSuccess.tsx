import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { CheckCircleIcon } from "@/components/icons";
import type { Booking } from "@/types";

export default function BookingConfirmationSuccess() {
  const navigate = useNavigate();
  const location = useLocation();
  const [booking, setBooking] = useState<Booking | null>(null);

  useEffect(() => {
    // Get booking data from location state
    const state = location.state as { booking?: Booking };
    if (state?.booking) {
      setBooking(state.booking);
    } else {
      // If no booking data, redirect to bookings list
      navigate("/bookings");
    }
  }, [location, navigate]);

  if (!booking) {
    return null;
  }

  const bookingDate = new Date(booking.startTime);
  const bookingRef = booking.id.slice(-8).toUpperCase();

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md shadow-lg">
        <div className="p-8 text-center space-y-6">
          {/* Success Icon */}
          <div className="flex justify-center">
            <div className="relative">
              <div className="absolute inset-0 bg-green-100 rounded-full animate-pulse" />
              <CheckCircleIcon
                size={64}
                className="text-green-600 relative z-10"
              />
            </div>
          </div>

          {/* Success Message */}
          <div>
            <h1 className="text-2xl font-bold text-foreground mb-2">
              Booking Confirmed!
            </h1>
            <p className="text-muted-foreground">
              Your appointment has been successfully scheduled.
            </p>
          </div>

          {/* Booking Reference */}
          <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
            <p className="text-xs text-muted-foreground mb-1">
              Booking Reference
            </p>
            <p className="text-lg font-mono font-bold text-foreground">
              {bookingRef}
            </p>
          </div>

          {/* Booking Details */}
          <div className="space-y-3 text-left bg-gray-50 rounded-lg p-4">
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Date</span>
              <span className="text-sm font-semibold text-foreground">
                {bookingDate.toLocaleDateString("en-US", {
                  weekday: "long",
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                })}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Time</span>
              <span className="text-sm font-semibold text-foreground">
                {bookingDate.toLocaleTimeString("en-US", {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Status</span>
              <span className="text-sm font-semibold text-green-600">
                {booking.status.charAt(0).toUpperCase() +
                  booking.status.slice(1)}
              </span>
            </div>
          </div>

          {/* Next Steps */}
          <div className="bg-amber-50 rounded-lg p-4 border border-amber-200">
            <p className="text-xs font-semibold text-amber-900 mb-2">
              Next Steps
            </p>
            <ul className="text-xs text-amber-800 space-y-1">
              <li>• Check your email for confirmation details</li>
              <li>• Arrive 5-10 minutes early</li>
              <li>• You can reschedule anytime from your bookings</li>
            </ul>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col gap-3 pt-4">
            <Button
              onClick={() => navigate("/bookings")}
              className="w-full cursor-pointer"
            >
              View All Bookings
            </Button>
            <Button
              variant="outline"
              onClick={() => navigate("/bookings/create")}
              className="w-full cursor-pointer"
            >
              Create Another Booking
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
