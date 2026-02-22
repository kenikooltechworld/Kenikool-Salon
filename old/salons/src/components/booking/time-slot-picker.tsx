/**
 * TimeSlotPicker Component
 * Displays available time slots for a selected date
 * Validates: Requirements 1.2, 14.1, 14.3
 */
import React, { useMemo } from "react";
import { Clock, AlertCircle } from "lucide-react";
import type { TimeSlot } from "@/lib/api/types";

interface TimeSlotPickerProps {
  slots: TimeSlot[];
  selectedSlot?: string;
  onSlotSelect: (slot: TimeSlot) => void;
  loading?: boolean;
}

/**
 * Component for selecting a time slot from available options
 */
export const TimeSlotPicker: React.FC<TimeSlotPickerProps> = ({
  slots,
  selectedSlot,
  onSlotSelect,
  loading = false,
}) => {
  const availableSlots = useMemo(
    () => slots.filter((slot) => slot.available),
    [slots],
  );

  const groupedSlots = useMemo(() => {
    const groups: Record<string, TimeSlot[]> = {};
    availableSlots.forEach((slot) => {
      const hour = slot.start_time.split(":")[0];
      if (!groups[hour]) {
        groups[hour] = [];
      }
      groups[hour].push(slot);
    });
    return groups;
  }, [availableSlots]);

  if (availableSlots.length === 0) {
    return (
      <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-4">
        <div className="flex items-start gap-3">
          <AlertCircle className="h-5 w-5 flex-shrink-0 text-yellow-600" />
          <div>
            <h3 className="font-semibold text-yellow-900">No availability</h3>
            <p className="text-sm text-yellow-800">
              No time slots are available for the selected date. Please try
              another date or stylist.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Time Slots Grid */}
      <div className="space-y-3">
        {Object.entries(groupedSlots)
          .sort()
          .map(([hour, hourSlots]) => (
            <div key={hour}>
              <h4 className="mb-2 text-sm font-semibold text-gray-700">
                {hour}:00
              </h4>
              <div className="grid grid-cols-3 gap-2 sm:grid-cols-4 md:grid-cols-6">
                {hourSlots.map((slot) => (
                  <button
                    key={slot.start_time}
                    onClick={() => onSlotSelect(slot)}
                    disabled={loading}
                    className={`rounded border-2 px-3 py-2 text-sm font-medium transition-colors ${
                      selectedSlot === slot.start_time
                        ? "border-green-500 bg-green-50 text-green-900"
                        : "border-gray-200 bg-white text-gray-900 hover:border-green-300 hover:bg-green-50"
                    } disabled:opacity-50`}
                  >
                    <div className="flex items-center justify-center gap-1">
                      <Clock className="h-3 w-3" />
                      <span>{slot.start_time}</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          ))}
      </div>

      {/* Loading state */}
      {loading && (
        <div className="text-center text-sm text-gray-500">
          Loading time slots...
        </div>
      )}
    </div>
  );
};

export default TimeSlotPicker;
