/**
 * BulkActionSelector Component
 * Allows selection of multiple bookings for bulk operations
 * Validates: Requirements 9.1
 */
import React from "react";
import { CheckSquare, Square } from "lucide-react";

interface Booking {
  id: string;
  service_name: string;
  stylist_name: string;
  booking_date: string;
  status: string;
}

interface BulkActionSelectorProps {
  bookings: Booking[];
  selectedIds: string[];
  onSelectionChange: (selectedIds: string[]) => void;
  onSelectAll?: () => void;
  onClearAll?: () => void;
}

/**
 * Component for selecting multiple bookings
 */
export const BulkActionSelector: React.FC<BulkActionSelectorProps> = ({
  bookings,
  selectedIds,
  onSelectionChange,
  onSelectAll,
  onClearAll,
}) => {
  const handleToggle = (id: string) => {
    if (selectedIds.includes(id)) {
      onSelectionChange(selectedIds.filter((sid) => sid !== id));
    } else {
      onSelectionChange([...selectedIds, id]);
    }
  };

  const handleSelectAll = () => {
    if (selectedIds.length === bookings.length) {
      onClearAll?.();
    } else {
      onSelectAll?.();
    }
  };

  const allSelected =
    selectedIds.length === bookings.length && bookings.length > 0;

  return (
    <div className="space-y-3">
      {/* Header with Select All */}
      <div className="flex items-center justify-between rounded-lg border border-gray-200 bg-gray-50 p-3">
        <button
          onClick={handleSelectAll}
          className="flex items-center gap-2 text-sm font-medium text-gray-700 hover:text-gray-900"
        >
          {allSelected ? (
            <CheckSquare className="h-5 w-5 text-blue-600" />
          ) : (
            <Square className="h-5 w-5 text-gray-400" />
          )}
          {allSelected ? "Deselect All" : "Select All"}
        </button>
        <span className="text-sm text-gray-600">
          {selectedIds.length} of {bookings.length} selected
        </span>
      </div>

      {/* Bookings List */}
      <div className="space-y-2">
        {bookings.map((booking) => {
          const isSelected = selectedIds.includes(booking.id);

          return (
            <div
              key={booking.id}
              onClick={() => handleToggle(booking.id)}
              className={`flex cursor-pointer items-center gap-3 rounded-lg border p-3 transition-colors ${
                isSelected
                  ? "border-blue-300 bg-blue-50"
                  : "border-gray-200 bg-white hover:bg-gray-50"
              }`}
            >
              {isSelected ? (
                <CheckSquare className="h-5 w-5 text-blue-600" />
              ) : (
                <Square className="h-5 w-5 text-gray-400" />
              )}
              <div className="flex-1">
                <div className="font-medium text-gray-900">
                  {booking.service_name}
                </div>
                <div className="text-sm text-gray-600">
                  {booking.stylist_name} • {booking.booking_date}
                </div>
              </div>
              <div className="text-xs font-medium text-gray-600">
                {booking.status}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default BulkActionSelector;
