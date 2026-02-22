import React, { useState } from "react";
import { useFamilyAccounts } from "@/lib/api/hooks/useFamilyAccounts";
import { useBookings } from "@/lib/api/hooks/useBookings";
import { Button } from "@/components/ui/button";
import { AlertCircle } from "lucide-react";

interface FamilyBookingManagerProps {
  bookingId: string;
  memberId: string;
  memberName: string;
  onBookingUpdated?: () => void;
}

export const FamilyBookingManager: React.FC<FamilyBookingManagerProps> = ({
  bookingId,
  memberId,
  memberName,
  onBookingUpdated,
}) => {
  const { updateFamilyBooking, cancelFamilyBooking } = useFamilyAccounts();
  const { bookings } = useBookings();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showConfirm, setShowConfirm] = useState(false);

  const booking = bookings.find((b) => b.id === bookingId);

  const handleCancel = async () => {
    setLoading(true);
    setError(null);

    try {
      await cancelFamilyBooking(bookingId, memberId);
      onBookingUpdated?.();
      setShowConfirm(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to cancel booking");
    } finally {
      setLoading(false);
    }
  };

  if (!booking) {
    return null;
  }

  return (
    <div className="space-y-4 rounded-lg border border-gray-200 bg-white p-4">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="font-medium text-gray-900">{memberName}</h3>
          <p className="text-sm text-gray-600">{booking.service_name}</p>
        </div>
        <span
          className={`text-xs font-medium px-2 py-1 rounded ${
            booking.status === "confirmed"
              ? "bg-green-100 text-green-700"
              : "bg-gray-100 text-gray-700"
          }`}
        >
          {booking.status}
        </span>
      </div>

      {error && (
        <div className="flex items-start gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-900">
          <AlertCircle className="h-4 w-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {!showConfirm ? (
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowConfirm(true)}
            disabled={loading || booking.status === "cancelled"}
            className="flex-1"
          >
            Cancel Booking
          </Button>
        </div>
      ) : (
        <div className="space-y-3 rounded-lg bg-red-50 p-3">
          <p className="text-sm font-medium text-red-900">
            Cancel booking for {memberName}?
          </p>
          <p className="text-xs text-red-800">
            This action cannot be undone. A cancellation notification will be
            sent to {memberName}.
          </p>
          <div className="flex gap-2">
            <Button
              variant="destructive"
              size="sm"
              onClick={handleCancel}
              disabled={loading}
              className="flex-1"
            >
              {loading ? "Cancelling..." : "Confirm Cancel"}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowConfirm(false)}
              disabled={loading}
              className="flex-1"
            >
              Keep Booking
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};
