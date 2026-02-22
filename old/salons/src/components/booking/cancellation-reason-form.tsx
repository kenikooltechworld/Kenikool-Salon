/**
 * CancellationReasonForm Component
 * Captures cancellation reason from user
 * Validates: Requirements 11.1, 11.2
 */
import React, { useState } from "react";
import { AlertCircle } from "lucide-react";

interface CancellationReasonFormProps {
  onSubmit: (reason: string) => Promise<void>;
  onCancel?: () => void;
  loading?: boolean;
}

const PREDEFINED_REASONS = [
  "Schedule conflict",
  "Found another stylist",
  "Not feeling well",
  "Transportation issue",
  "Changed my mind",
  "Other",
];

/**
 * Component for capturing cancellation reason
 */
export const CancellationReasonForm: React.FC<CancellationReasonFormProps> = ({
  onSubmit,
  onCancel,
  loading = false,
}) => {
  const [selectedReason, setSelectedReason] = useState<string | null>(null);
  const [customReason, setCustomReason] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    const reason =
      selectedReason === "Other" ? customReason : selectedReason || "";

    if (!reason.trim()) {
      setError("Please select or enter a reason");
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      await onSubmit(reason);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to cancel booking");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-4 rounded-lg border border-gray-200 bg-white p-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-900">
          Why are you cancelling?
        </h2>
        <p className="mt-1 text-sm text-gray-600">
          Your feedback helps us improve our service
        </p>
      </div>

      {/* Predefined Reasons */}
      <div className="space-y-2">
        {PREDEFINED_REASONS.map((reason) => (
          <label key={reason} className="flex items-center gap-3">
            <input
              type="radio"
              name="cancellation-reason"
              value={reason}
              checked={selectedReason === reason}
              onChange={(e) => {
                setSelectedReason(e.target.value);
                setError(null);
              }}
              disabled={loading || submitting}
              className="h-4 w-4 border-gray-300"
            />
            <span className="text-gray-700">{reason}</span>
          </label>
        ))}
      </div>

      {/* Custom Reason Input */}
      {selectedReason === "Other" && (
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-900">
            Please tell us more
          </label>
          <textarea
            value={customReason}
            onChange={(e) => {
              setCustomReason(e.target.value);
              setError(null);
            }}
            disabled={loading || submitting}
            placeholder="Enter your reason here..."
            className="w-full rounded border border-gray-300 px-3 py-2 text-gray-900 placeholder-gray-500 focus:border-blue-500 focus:outline-none disabled:bg-gray-50"
            rows={3}
          />
          <div className="text-xs text-gray-500">
            {customReason.length}/500 characters
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="flex items-start gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-900">
          <AlertCircle className="h-4 w-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-3 border-t border-gray-200 pt-4">
        <button
          onClick={handleSubmit}
          disabled={loading || submitting || !selectedReason}
          className="flex-1 rounded bg-red-600 px-4 py-2 font-medium text-white hover:bg-red-700 disabled:opacity-50"
        >
          {submitting ? "Cancelling..." : "Confirm Cancellation"}
        </button>
        <button
          onClick={onCancel}
          disabled={loading || submitting}
          className="flex-1 rounded border border-gray-300 bg-white px-4 py-2 font-medium text-gray-900 hover:bg-gray-50 disabled:opacity-50"
        >
          Keep Booking
        </button>
      </div>
    </div>
  );
};

export default CancellationReasonForm;
