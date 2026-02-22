/**
 * RecurrenceCancellation Component
 * Allows cancellation of series or individual occurrences
 * Validates: Requirements 8.3, 8.5
 */
import React, { useState } from "react";
import { Trash2, AlertCircle } from "lucide-react";

interface RecurrenceCancellationProps {
  bookingId: string;
  serviceName: string;
  onSubmit: (cancellation: CancellationRequest) => void;
  loading?: boolean;
}

export interface CancellationRequest {
  booking_id: string;
  scope: "this" | "all_future" | "entire_series";
  reason?: string;
}

/**
 * Component for cancelling recurring bookings
 */
export const RecurrenceCancellation: React.FC<RecurrenceCancellationProps> = ({
  bookingId,
  serviceName,
  onSubmit,
  loading = false,
}) => {
  const [scope, setScope] = useState<"this" | "all_future" | "entire_series">(
    "this",
  );
  const [reason, setReason] = useState("");
  const [showConfirmation, setShowConfirmation] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setShowConfirmation(true);
  };

  const handleConfirm = () => {
    onSubmit({
      booking_id: bookingId,
      scope,
      reason: reason || undefined,
    });
    setShowConfirmation(false);
  };

  const scopeDescriptions = {
    this: "Cancel only this occurrence",
    all_future: "Cancel this and all future occurrences",
    entire_series: "Cancel the entire recurring series",
  };

  return (
    <>
      <form
        onSubmit={handleSubmit}
        className="space-y-4 rounded-lg border border-red-200 bg-red-50 p-4"
      >
        {/* Header */}
        <div className="flex items-center gap-2">
          <Trash2 className="h-5 w-5 text-red-600" />
          <h3 className="font-semibold text-red-900">
            Cancel Recurring Booking
          </h3>
        </div>

        {/* Service Name */}
        <div className="rounded-lg bg-white p-3 text-sm text-gray-600">
          {serviceName}
        </div>

        {/* Scope Selection */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">
            Cancellation Scope
          </label>
          <div className="space-y-2">
            {(["this", "all_future", "entire_series"] as const).map((s) => (
              <label key={s} className="flex items-start gap-2">
                <input
                  type="radio"
                  checked={scope === s}
                  onChange={() => setScope(s)}
                  className="mt-1 h-4 w-4"
                />
                <div>
                  <div className="text-sm font-medium text-gray-900">
                    {s === "this" && "This Occurrence"}
                    {s === "all_future" && "This and Future"}
                    {s === "entire_series" && "Entire Series"}
                  </div>
                  <div className="text-xs text-gray-600">
                    {scopeDescriptions[s]}
                  </div>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Reason */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">
            Cancellation Reason (Optional)
          </label>
          <textarea
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="Why are you cancelling this booking?"
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            rows={3}
          />
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-lg bg-red-600 px-4 py-2 font-medium text-white hover:bg-red-700 disabled:opacity-50"
        >
          {loading ? "Cancelling..." : "Cancel Booking"}
        </button>
      </form>

      {/* Confirmation Modal */}
      {showConfirmation && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-lg">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-6 w-6 flex-shrink-0 text-red-600" />
              <div>
                <h3 className="font-semibold text-gray-900">
                  Confirm Cancellation
                </h3>
                <p className="mt-2 text-sm text-gray-600">
                  {scope === "this" &&
                    "This will cancel only this occurrence. Other bookings in the series will remain."}
                  {scope === "all_future" &&
                    "This will cancel this and all future occurrences. Previous bookings will remain."}
                  {scope === "entire_series" &&
                    "This will cancel the entire recurring series. This action cannot be undone."}
                </p>
              </div>
            </div>
            <div className="mt-6 flex gap-3">
              <button
                type="button"
                onClick={() => setShowConfirmation(false)}
                className="flex-1 rounded-lg border border-gray-300 px-4 py-2 font-medium text-gray-700 hover:bg-gray-50"
              >
                Keep Booking
              </button>
              <button
                type="button"
                onClick={handleConfirm}
                className="flex-1 rounded-lg bg-red-600 px-4 py-2 font-medium text-white hover:bg-red-700"
              >
                Cancel Booking
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default RecurrenceCancellation;
