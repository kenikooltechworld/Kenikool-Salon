/**
 * BulkRescheduler Component
 * Allows bulk rescheduling to new date/time
 * Validates: Requirements 9.4
 */
import React, { useState } from "react";
import { Calendar, AlertCircle } from "lucide-react";

interface BulkRescheduleProps {
  selectedCount: number;
  onSubmit: (newDate: string, newTime: string) => void;
  loading?: boolean;
}

/**
 * Component for bulk rescheduling
 */
export const BulkRescheduler: React.FC<BulkRescheduleProps> = ({
  selectedCount,
  onSubmit,
  loading = false,
}) => {
  const [newDate, setNewDate] = useState("");
  const [newTime, setNewTime] = useState("09:00");
  const [showConfirmation, setShowConfirmation] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newDate) {
      alert("Please select a date");
      return;
    }
    setShowConfirmation(true);
  };

  const handleConfirm = () => {
    onSubmit(newDate, newTime);
    setShowConfirmation(false);
  };

  const formatDate = (dateStr: string) => {
    try {
      return new Date(dateStr).toLocaleDateString("en-US", {
        weekday: "long",
        month: "long",
        day: "numeric",
        year: "numeric",
      });
    } catch {
      return dateStr;
    }
  };

  return (
    <>
      <form
        onSubmit={handleSubmit}
        className="space-y-4 rounded-lg border border-blue-200 bg-blue-50 p-4"
      >
        {/* Header */}
        <div className="flex items-center gap-2">
          <Calendar className="h-5 w-5 text-blue-600" />
          <h3 className="font-semibold text-blue-900">Reschedule Bookings</h3>
        </div>

        {/* Selection Summary */}
        <div className="rounded-lg bg-white p-3 text-sm text-gray-600">
          Rescheduling {selectedCount} booking{selectedCount !== 1 ? "s" : ""}
        </div>

        {/* New Date */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">New Date</label>
          <input
            type="date"
            value={newDate}
            onChange={(e) => setNewDate(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
            required
          />
        </div>

        {/* New Time */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">New Time</label>
          <input
            type="time"
            value={newTime}
            onChange={(e) => setNewTime(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
          />
        </div>

        {/* Summary */}
        {newDate && (
          <div className="rounded-lg bg-white p-3">
            <div className="text-sm text-gray-600">
              New Date & Time:{" "}
              <span className="font-medium">
                {formatDate(newDate)} at {newTime}
              </span>
            </div>
          </div>
        )}

        {/* Submit */}
        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-lg bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Rescheduling..." : "Reschedule Bookings"}
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
                  Confirm Rescheduling
                </h3>
                <p className="mt-2 text-sm text-gray-600">
                  This will reschedule {selectedCount} booking
                  {selectedCount !== 1 ? "s" : ""} to{" "}
                  <span className="font-medium">
                    {formatDate(newDate)} at {newTime}
                  </span>{" "}
                  and send notifications to affected customers. This action
                  cannot be undone.
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

export default BulkRescheduler;
