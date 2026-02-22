/**
 * BulkStatusUpdater Component
 * Allows bulk status update for multiple bookings
 * Validates: Requirements 9.2
 */
import React, { useState } from "react";
import { AlertCircle } from "lucide-react";

interface BulkStatusUpdaterProps {
  selectedCount: number;
  onSubmit: (status: string) => void;
  loading?: boolean;
}

/**
 * Component for bulk status updates
 */
export const BulkStatusUpdater: React.FC<BulkStatusUpdaterProps> = ({
  selectedCount,
  onSubmit,
  loading = false,
}) => {
  const [status, setStatus] = useState("confirmed");
  const [showConfirmation, setShowConfirmation] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setShowConfirmation(true);
  };

  const handleConfirm = () => {
    onSubmit(status);
    setShowConfirmation(false);
  };

  const statusOptions = [
    { value: "confirmed", label: "Confirmed" },
    { value: "completed", label: "Completed" },
    { value: "cancelled", label: "Cancelled" },
    { value: "no-show", label: "No-Show" },
  ];

  return (
    <>
      <form
        onSubmit={handleSubmit}
        className="space-y-4 rounded-lg border border-blue-200 bg-blue-50 p-4"
      >
        {/* Header */}
        <div className="flex items-center gap-2">
          <AlertCircle className="h-5 w-5 text-blue-600" />
          <h3 className="font-semibold text-blue-900">Update Status</h3>
        </div>

        {/* Selection Summary */}
        <div className="rounded-lg bg-white p-3 text-sm text-gray-600">
          Updating {selectedCount} booking{selectedCount !== 1 ? "s" : ""}
        </div>

        {/* Status Selection */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">
            New Status
          </label>
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
          >
            {statusOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-lg bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Updating..." : "Update Status"}
        </button>
      </form>

      {/* Confirmation Modal */}
      {showConfirmation && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-lg">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-6 w-6 flex-shrink-0 text-blue-600" />
              <div>
                <h3 className="font-semibold text-gray-900">
                  Confirm Status Update
                </h3>
                <p className="mt-2 text-sm text-gray-600">
                  This will update the status of {selectedCount} booking
                  {selectedCount !== 1 ? "s" : ""} to{" "}
                  <span className="font-medium">
                    {statusOptions.find((o) => o.value === status)?.label}
                  </span>
                  . This action cannot be undone.
                </p>
              </div>
            </div>
            <div className="mt-6 flex gap-3">
              <button
                type="button"
                onClick={() => setShowConfirmation(false)}
                className="flex-1 rounded-lg border border-gray-300 px-4 py-2 font-medium text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleConfirm}
                className="flex-1 rounded-lg bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700"
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default BulkStatusUpdater;
