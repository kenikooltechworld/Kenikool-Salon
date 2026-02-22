/**
 * BulkCanceller Component
 * Allows bulk cancellation with reason
 * Validates: Requirements 9.3
 */
import React, { useState } from "react";
import { Trash2, AlertCircle } from "lucide-react";

interface BulkCancellerProps {
  selectedCount: number;
  onSubmit: (reason?: string) => void;
  loading?: boolean;
}

/**
 * Component for bulk cancellation
 */
export const BulkCanceller: React.FC<BulkCancellerProps> = ({
  selectedCount,
  onSubmit,
  loading = false,
}) => {
  const [reason, setReason] = useState("");
  const [showConfirmation, setShowConfirmation] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setShowConfirmation(true);
  };

  const handleConfirm = () => {
    onSubmit(reason || undefined);
    setShowConfirmation(false);
  };

  const reasonOptions = [
    "Customer requested",
    "Stylist unavailable",
    "Scheduling conflict",
    "Other",
  ];

  return (
    <>
      <form
        onSubmit={handleSubmit}
        className="space-y-4 rounded-lg border border-red-200 bg-red-50 p-4"
      >
        {/* Header */}
        <div className="flex items-center gap-2">
          <Trash2 className="h-5 w-5 text-red-600" />
          <h3 className="font-semibold text-red-900">Cancel Bookings</h3>
        </div>

        {/* Selection Summary */}
        <div className="rounded-lg bg-white p-3 text-sm text-gray-600">
          Cancelling {selectedCount} booking{selectedCount !== 1 ? "s" : ""}
        </div>

        {/* Reason Selection */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">
            Cancellation Reason
          </label>
          <div className="space-y-2">
            {reasonOptions.map((option) => (
              <label key={option} className="flex items-center gap-2">
                <input
                  type="radio"
                  checked={reason === option}
                  onChange={() => setReason(option)}
                  className="h-4 w-4"
                />
                <span className="text-sm text-gray-700">{option}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Custom Reason */}
        {reason === "Other" && (
          <textarea
            placeholder="Please specify the reason..."
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            rows={3}
            onChange={(e) => setReason(e.target.value)}
          />
        )}

        {/* Submit */}
        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-lg bg-red-600 px-4 py-2 font-medium text-white hover:bg-red-700 disabled:opacity-50"
        >
          {loading ? "Cancelling..." : "Cancel Bookings"}
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
                  This will cancel {selectedCount} booking
                  {selectedCount !== 1 ? "s" : ""} and send notifications to
                  affected customers. This action cannot be undone.
                </p>
                {reason && (
                  <p className="mt-2 text-sm text-gray-600">
                    Reason: <span className="font-medium">{reason}</span>
                  </p>
                )}
              </div>
            </div>
            <div className="mt-6 flex gap-3">
              <button
                type="button"
                onClick={() => setShowConfirmation(false)}
                className="flex-1 rounded-lg border border-gray-300 px-4 py-2 font-medium text-gray-700 hover:bg-gray-50"
              >
                Keep Bookings
              </button>
              <button
                type="button"
                onClick={handleConfirm}
                className="flex-1 rounded-lg bg-red-600 px-4 py-2 font-medium text-white hover:bg-red-700"
              >
                Cancel Bookings
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default BulkCanceller;
