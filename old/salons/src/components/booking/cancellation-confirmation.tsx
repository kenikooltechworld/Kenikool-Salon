import React from "react";
import { CheckCircle, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

interface CancellationConfirmationProps {
  bookingId: string;
  bookingDate: string;
  bookingTime: string;
  serviceName: string;
  stylistName: string;
  cancellationReason: string;
  refundAmount?: number;
  onClose: () => void;
  onViewBookings?: () => void;
}

export const CancellationConfirmation: React.FC<
  CancellationConfirmationProps
> = ({
  bookingId,
  bookingDate,
  bookingTime,
  serviceName,
  stylistName,
  cancellationReason,
  refundAmount,
  onClose,
  onViewBookings,
}) => {
  return (
    <div className="space-y-6 rounded-lg border border-gray-200 bg-white p-6">
      {/* Success Header */}
      <div className="flex items-center gap-3">
        <CheckCircle className="h-6 w-6 text-green-600" />
        <div>
          <h2 className="text-lg font-semibold text-gray-900">
            Booking Cancelled
          </h2>
          <p className="text-sm text-gray-600">
            Your booking has been successfully cancelled
          </p>
        </div>
      </div>

      {/* Cancellation Details */}
      <div className="space-y-3 rounded-lg bg-gray-50 p-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs font-medium text-gray-600">Booking ID</p>
            <p className="text-sm font-mono text-gray-900">{bookingId}</p>
          </div>
          <div>
            <p className="text-xs font-medium text-gray-600">Service</p>
            <p className="text-sm text-gray-900">{serviceName}</p>
          </div>
          <div>
            <p className="text-xs font-medium text-gray-600">Date & Time</p>
            <p className="text-sm text-gray-900">
              {bookingDate} at {bookingTime}
            </p>
          </div>
          <div>
            <p className="text-xs font-medium text-gray-600">Stylist</p>
            <p className="text-sm text-gray-900">{stylistName}</p>
          </div>
        </div>
      </div>

      {/* Cancellation Reason */}
      <div className="space-y-2">
        <p className="text-sm font-medium text-gray-900">Cancellation Reason</p>
        <p className="text-sm text-gray-700">{cancellationReason}</p>
      </div>

      {/* Refund Information */}
      {refundAmount !== undefined && refundAmount > 0 && (
        <div className="flex items-start gap-3 rounded-lg bg-blue-50 p-3">
          <AlertCircle className="h-5 w-5 flex-shrink-0 text-blue-600" />
          <div className="text-sm">
            <p className="font-medium text-blue-900">Refund Processed</p>
            <p className="text-blue-800">
              ${refundAmount.toFixed(2)} will be refunded to your original
              payment method within 3-5 business days
            </p>
          </div>
        </div>
      )}

      {/* Notification Info */}
      <div className="rounded-lg bg-gray-50 p-3 text-sm text-gray-700">
        <p className="font-medium text-gray-900">What happens next?</p>
        <ul className="mt-2 space-y-1 list-disc list-inside">
          <li>A cancellation confirmation has been sent to your email</li>
          <li>Your stylist has been notified of the cancellation</li>
          <li>The time slot is now available for other customers</li>
        </ul>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3 border-t border-gray-200 pt-4">
        <Button onClick={onViewBookings} variant="outline" className="flex-1">
          View My Bookings
        </Button>
        <Button onClick={onClose} className="flex-1">
          Done
        </Button>
      </div>
    </div>
  );
};
