/**
 * Booking Confirmation Component - Display booking confirmation details
 */

import { Button, Card, Badge, Alert } from "@/components/ui";
import { formatDate } from "@/lib/utils/format";
import { CheckCircleIcon } from "@/components/icons";

interface BookingConfirmationProps {
  booking: {
    id: string;
    customer_name: string;
    customer_email: string;
    customer_phone: string;
    booking_date: string;
    booking_time: string;
    duration_minutes: number;
    status: string;
    created_at: string;
  };
}

export default function BookingConfirmation({
  booking,
}: BookingConfirmationProps) {
  const bookingDate = new Date(booking.booking_date);

  return (
    <div className="space-y-6">
      {/* Success Message */}
      <div className="text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-success/10 rounded-full mb-4">
          <CheckCircleIcon size={32} className="text-success" />
        </div>
        <h2 className="text-2xl font-bold mb-2">Booking Confirmed!</h2>
        <p className="text-muted-foreground">
          A confirmation email has been sent to{" "}
          <strong>{booking.customer_email}</strong>
        </p>
      </div>

      {/* Booking Details */}
      <Card className="p-6 bg-muted/50">
        <h3 className="font-semibold text-lg mb-4">Booking Details</h3>

        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Confirmation Number:</span>
            <span className="font-mono font-semibold text-sm">
              {booking.id}
            </span>
          </div>

          <div className="flex justify-between">
            <span className="text-muted-foreground">Date:</span>
            <span className="font-semibold">
              {formatDate(bookingDate, "MMMM dd, yyyy")}
            </span>
          </div>

          <div className="flex justify-between">
            <span className="text-muted-foreground">Time:</span>
            <span className="font-semibold">{booking.booking_time}</span>
          </div>

          <div className="flex justify-between">
            <span className="text-muted-foreground">Duration:</span>
            <span className="font-semibold">
              {booking.duration_minutes} minutes
            </span>
          </div>

          <div className="flex justify-between">
            <span className="text-muted-foreground">Status:</span>
            <Badge variant="secondary">{booking.status}</Badge>
          </div>
        </div>
      </Card>

      {/* Customer Information */}
      <Card className="p-6 bg-primary/5">
        <h3 className="font-semibold text-lg mb-4">Your Information</h3>

        <div className="space-y-2 text-sm">
          <p>
            <span className="text-muted-foreground">Name:</span>{" "}
            <strong>{booking.customer_name}</strong>
          </p>
          <p>
            <span className="text-muted-foreground">Email:</span>{" "}
            <strong>{booking.customer_email}</strong>
          </p>
          <p>
            <span className="text-muted-foreground">Phone:</span>{" "}
            <strong>{booking.customer_phone}</strong>
          </p>
        </div>
      </Card>

      {/* Important Information */}
      <Alert>
        <div className="space-y-2">
          <h4 className="font-semibold">Important Information</h4>
          <ul className="text-sm space-y-1 list-disc list-inside">
            <li>Please arrive 5-10 minutes early</li>
            <li>
              You can cancel or reschedule up to 24 hours before your
              appointment
            </li>
            <li>Check your email for cancellation and rescheduling links</li>
            <li>If you have questions, contact the salon directly</li>
          </ul>
        </div>
      </Alert>

      {/* Actions */}
      <div className="flex flex-col gap-3">
        <Button
          variant="primary"
          className="w-full"
          onClick={() => window.print()}
        >
          Print Confirmation
        </Button>
        <Button
          variant="outline"
          className="w-full"
          onClick={() => (window.location.href = "/")}
        >
          Back to Salon
        </Button>
      </div>

      {/* Footer Message */}
      <div className="text-center text-sm text-muted-foreground pt-4 border-t">
        <p>
          Thank you for booking with us! We look forward to seeing you on{" "}
          <strong>{formatDate(bookingDate, "MMMM dd")}</strong>.
        </p>
      </div>
    </div>
  );
}
