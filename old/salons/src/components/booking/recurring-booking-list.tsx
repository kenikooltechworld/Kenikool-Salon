/**
 * RecurringBookingList Component
 * Displays recurring bookings with frequency information
 * Validates: Requirements 8.1
 */
import React from "react";
import { Repeat2, Calendar, Clock } from "lucide-react";

interface RecurringBooking {
  id: string;
  service_name: string;
  stylist_name: string;
  frequency: string;
  next_occurrence: string;
  series_end_date: string;
  occurrences_remaining: number;
}

interface RecurringBookingListProps {
  bookings: RecurringBooking[];
  onEdit?: (bookingId: string) => void;
  onCancel?: (bookingId: string) => void;
  loading?: boolean;
}

/**
 * Component for displaying recurring bookings
 */
export const RecurringBookingList: React.FC<RecurringBookingListProps> = ({
  bookings,
  onEdit,
  onCancel,
  loading = false,
}) => {
  const formatDate = (dateStr: string) => {
    try {
      return new Date(dateStr).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
      });
    } catch {
      return dateStr;
    }
  };

  const formatTime = (dateStr: string) => {
    try {
      return new Date(dateStr).toLocaleTimeString("en-US", {
        hour: "numeric",
        minute: "2-digit",
        hour12: true,
      });
    } catch {
      return "";
    }
  };

  if (bookings.length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-4">
        <div className="text-center text-sm text-gray-500">
          No recurring bookings
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {bookings.map((booking) => (
        <div
          key={booking.id}
          className="rounded-lg border border-gray-200 bg-white p-4"
        >
          {/* Header */}
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <Repeat2 className="h-5 w-5 text-blue-600" />
                <h3 className="font-semibold text-gray-900">
                  {booking.service_name}
                </h3>
              </div>
              <div className="mt-1 text-sm text-gray-600">
                with {booking.stylist_name}
              </div>
            </div>
            <div className="flex gap-2">
              {onEdit && (
                <button
                  onClick={() => onEdit(booking.id)}
                  disabled={loading}
                  className="rounded-lg border border-gray-300 px-3 py-1 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
                >
                  Edit
                </button>
              )}
              {onCancel && (
                <button
                  onClick={() => onCancel(booking.id)}
                  disabled={loading}
                  className="rounded-lg border border-red-300 px-3 py-1 text-sm font-medium text-red-700 hover:bg-red-50 disabled:opacity-50"
                >
                  Cancel
                </button>
              )}
            </div>
          </div>

          {/* Details */}
          <div className="mt-3 space-y-2 border-t border-gray-200 pt-3">
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Repeat2 className="h-4 w-4" />
              <span>{booking.frequency}</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Clock className="h-4 w-4" />
              <span>
                Next: {formatDate(booking.next_occurrence)}{" "}
                {formatTime(booking.next_occurrence)}
              </span>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Calendar className="h-4 w-4" />
              <span>
                Ends: {formatDate(booking.series_end_date)} (
                {booking.occurrences_remaining} remaining)
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default RecurringBookingList;
