import React from "react";
import { AlertCircle } from "lucide-react";

interface TimeSlot {
  time: string;
  available: boolean;
  reason?: string;
}

interface BufferTimeDisplayProps {
  timeSlots: TimeSlot[];
  bufferTime: number; // minutes
  existingBookings?: Array<{
    startTime: string;
    endTime: string;
  }>;
}

export const BufferTimeDisplay: React.FC<BufferTimeDisplayProps> = ({
  timeSlots,
  bufferTime,
  existingBookings = [],
}) => {
  const unavailableSlots = timeSlots.filter((slot) => !slot.available);
  const bufferSlots = unavailableSlots.filter(
    (slot) =>
      slot.reason?.includes("buffer") || slot.reason?.includes("Buffer"),
  );

  if (bufferSlots.length === 0) {
    return null;
  }

  return (
    <div className="space-y-3 rounded-lg border border-yellow-200 bg-yellow-50 p-4">
      <div className="flex items-start gap-2">
        <AlertCircle className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <h3 className="font-medium text-yellow-900">Buffer Time</h3>
          <p className="text-sm text-yellow-800 mt-1">
            {bufferTime} minutes buffer is maintained between appointments
          </p>
        </div>
      </div>

      {bufferSlots.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm font-medium text-yellow-900">
            Unavailable due to buffer time:
          </p>
          <div className="grid grid-cols-2 gap-2">
            {bufferSlots.map((slot, idx) => (
              <div
                key={idx}
                className="text-xs bg-white rounded p-2 text-yellow-900"
              >
                {slot.time}
              </div>
            ))}
          </div>
        </div>
      )}

      {existingBookings.length > 0 && (
        <div className="space-y-2 border-t border-yellow-200 pt-2">
          <p className="text-sm font-medium text-yellow-900">
            Existing appointments:
          </p>
          <div className="space-y-1">
            {existingBookings.map((booking, idx) => (
              <div key={idx} className="text-xs text-yellow-800">
                {booking.startTime} - {booking.endTime}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
