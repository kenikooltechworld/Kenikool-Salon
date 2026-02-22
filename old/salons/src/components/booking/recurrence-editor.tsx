/**
 * RecurrenceEditor Component
 * Allows editing of recurrence pattern with scope selection
 * Validates: Requirements 8.2, 8.4
 */
import React, { useState } from "react";
import { Edit2, AlertCircle } from "lucide-react";

interface RecurrenceEditorProps {
  currentFrequency: string;
  onSubmit: (changes: RecurrenceChanges) => void;
  loading?: boolean;
}

export interface RecurrenceChanges {
  frequency?: string;
  interval?: number;
  scope: "this" | "all_future";
}

/**
 * Component for editing recurrence patterns
 */
export const RecurrenceEditor: React.FC<RecurrenceEditorProps> = ({
  currentFrequency,
  onSubmit,
  loading = false,
}) => {
  const [frequency, setFrequency] = useState(currentFrequency);
  const [scope, setScope] = useState<"this" | "all_future">("all_future");
  const [showScopeWarning, setShowScopeWarning] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (scope === "all_future") {
      setShowScopeWarning(true);
    } else {
      onSubmit({
        frequency,
        scope,
      });
    }
  };

  const handleConfirmScope = () => {
    onSubmit({
      frequency,
      scope,
    });
    setShowScopeWarning(false);
  };

  const frequencyOptions = [
    { value: "daily", label: "Every Day" },
    { value: "weekly", label: "Every Week" },
    { value: "biweekly", label: "Every 2 Weeks" },
    { value: "monthly", label: "Every Month" },
  ];

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-4 rounded-lg border border-blue-200 bg-blue-50 p-4"
    >
      {/* Header */}
      <div className="flex items-center gap-2">
        <Edit2 className="h-5 w-5 text-blue-600" />
        <h3 className="font-semibold text-blue-900">Edit Recurrence</h3>
      </div>

      {/* Current Frequency */}
      <div className="space-y-2">
        <label className="text-sm font-medium text-gray-700">
          Current Frequency
        </label>
        <div className="rounded-lg bg-white p-3 text-sm text-gray-600">
          {currentFrequency}
        </div>
      </div>

      {/* New Frequency */}
      <div className="space-y-2">
        <label className="text-sm font-medium text-gray-700">
          New Frequency
        </label>
        <select
          value={frequency}
          onChange={(e) => setFrequency(e.target.value)}
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
        >
          {frequencyOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      {/* Scope Selection */}
      <div className="space-y-2">
        <label className="text-sm font-medium text-gray-700">
          Apply Changes To
        </label>
        <div className="space-y-2">
          <label className="flex items-center gap-2">
            <input
              type="radio"
              checked={scope === "this"}
              onChange={() => setScope("this")}
              className="h-4 w-4"
            />
            <span className="text-sm text-gray-700">This occurrence only</span>
          </label>
          <label className="flex items-center gap-2">
            <input
              type="radio"
              checked={scope === "all_future"}
              onChange={() => setScope("all_future")}
              className="h-4 w-4"
            />
            <span className="text-sm text-gray-700">
              This and all future occurrences
            </span>
          </label>
        </div>
      </div>

      {/* Submit */}
      <button
        type="submit"
        disabled={loading}
        className="w-full rounded-lg bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? "Updating..." : "Update Recurrence"}
      </button>

      {/* Scope Warning Modal */}
      {showScopeWarning && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-lg">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-6 w-6 flex-shrink-0 text-orange-600" />
              <div>
                <h3 className="font-semibold text-gray-900">
                  Update All Future Occurrences?
                </h3>
                <p className="mt-2 text-sm text-gray-600">
                  This will change the recurrence pattern for this and all
                  future occurrences. This action cannot be undone.
                </p>
              </div>
            </div>
            <div className="mt-6 flex gap-3">
              <button
                type="button"
                onClick={() => setShowScopeWarning(false)}
                className="flex-1 rounded-lg border border-gray-300 px-4 py-2 font-medium text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleConfirmScope}
                className="flex-1 rounded-lg bg-orange-600 px-4 py-2 font-medium text-white hover:bg-orange-700"
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </form>
  );
};

export default RecurrenceEditor;
