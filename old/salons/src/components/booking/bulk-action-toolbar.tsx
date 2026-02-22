/**
 * BulkActionToolbar Component
 * Displays available bulk actions when bookings are selected
 * Validates: Requirements 9.1
 */
import React from "react";
import { CheckSquare, Trash2, Calendar, AlertCircle } from "lucide-react";

interface BulkActionToolbarProps {
  selectedCount: number;
  onStatusUpdate?: () => void;
  onCancel?: () => void;
  onReschedule?: () => void;
  onClearSelection?: () => void;
  disabled?: boolean;
}

/**
 * Component for displaying bulk action options
 */
export const BulkActionToolbar: React.FC<BulkActionToolbarProps> = ({
  selectedCount,
  onStatusUpdate,
  onCancel,
  onReschedule,
  onClearSelection,
  disabled = false,
}) => {
  if (selectedCount === 0) {
    return null;
  }

  return (
    <div className="sticky bottom-0 z-40 space-y-3 rounded-lg border border-blue-200 bg-blue-50 p-4 shadow-lg">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <CheckSquare className="h-5 w-5 text-blue-600" />
          <span className="font-semibold text-blue-900">
            {selectedCount} booking{selectedCount !== 1 ? "s" : ""} selected
          </span>
        </div>
        {onClearSelection && (
          <button
            onClick={onClearSelection}
            className="text-sm text-blue-600 hover:text-blue-700"
          >
            Clear
          </button>
        )}
      </div>

      {/* Actions */}
      <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
        {onStatusUpdate && (
          <button
            onClick={onStatusUpdate}
            disabled={disabled}
            className="flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 disabled:opacity-50"
          >
            <AlertCircle className="h-4 w-4" />
            Update Status
          </button>
        )}

        {onReschedule && (
          <button
            onClick={onReschedule}
            disabled={disabled}
            className="flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 disabled:opacity-50"
          >
            <Calendar className="h-4 w-4" />
            Reschedule
          </button>
        )}

        {onCancel && (
          <button
            onClick={onCancel}
            disabled={disabled}
            className="flex items-center justify-center gap-2 rounded-lg bg-red-600 px-4 py-2 font-medium text-white hover:bg-red-700 disabled:opacity-50"
          >
            <Trash2 className="h-4 w-4" />
            Cancel
          </button>
        )}
      </div>

      {/* Info */}
      <div className="text-xs text-blue-700">
        Select bookings above to perform bulk actions
      </div>
    </div>
  );
};

export default BulkActionToolbar;
